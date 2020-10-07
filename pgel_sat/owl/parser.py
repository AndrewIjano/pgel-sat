import owlready2 as owl
from .. import gel, pgel
from . import pbox_parser


def parse(file: str):
    onto = owl.get_ontology(file)
    onto.load()

    kb = get_kb(onto)
    pbox_restrictions = pbox_parser.get_restrictions(onto)
    return kb, pbox_restrictions


def get_kb(onto):
    owl_concepts = list(onto.classes())
    owl_individuals = list(onto.individuals())
    owl_roles = onto.object_properties()

    kb = pgel.ProbabilisticKnowledgeBase(owl.Nothing.iri, owl.Thing.iri)

    add_concepts(kb, owl_concepts, gel.Concept)
    add_concepts(kb, owl_individuals, gel.IndividualConcept)
    add_roles(kb, owl_roles)

    add_role_inclusions_from_roles(kb, owl_roles)
    owl_basic_concepts = [owl.Thing] + owl_concepts + owl_individuals
    add_axioms_from_concepts(kb, owl_basic_concepts)
    return kb


def add_concepts(kb, owl_concepts, concept_class: type):
    for owl_concept in owl_concepts:
        kb.add_concept(concept_class(owl_concept.iri))


def add_roles(kb, owl_roles):
    for owl_role in owl_roles:
        kb.add_role(gel.Role(owl_role.iri))


def add_role_inclusions_from_roles(kb, owl_roles):
    for owl_sup_role in owl_roles:
        for owl_sub_role in owl_sup_role.get_property_chain():
            add_chained_role_inclusion(kb, owl_sub_role, owl_sup_role)

        for owl_sub_role in owl_sup_role.subclasses():
            add_role_inclusion(kb, owl_sub_role, owl_sup_role)


def add_chained_role_inclusion(kb, owl_sub_role_chain, owl_sup_role):
    owl_sub_role1, owl_sub_role2 = owl_sub_role_chain.properties
    kb.add_chained_role_inclusion(
        (owl_sub_role1.iri, owl_sub_role2.iri),
        owl_sup_role.iri)


def add_role_inclusion(kb, owl_sub_role, owl_sup_role):
    kb.add_role_inclusion(owl_sub_role.iri, owl_sup_role.iri)


def add_axioms_from_concepts(kb, owl_concepts):
    for sub_concept in owl_concepts:
        if sub_concept == owl.Nothing:
            continue

        for sup_concept in sub_concept.is_a:
            # ignore trivial axioms
            if sup_concept == owl.Thing:
                continue
            add_axiom(kb, sub_concept, sup_concept)

        for sup_concept in sub_concept.equivalent_to:
            add_axiom(kb, sub_concept, sup_concept)
            add_axiom(kb, sup_concept, sub_concept)

        if not is_concept(sub_concept):
            for sup_concept, role in get_individual_sup_and_role(sub_concept):
                pbox_id = pbox_parser.get_id(sub_concept, sup_concept)
                kb.add_axiom(
                    sub_concept.iri,
                    sup_concept.iri,
                    role.iri,
                    pbox_id)


def add_axiom(kb, owl_sub_concept, owl_sup_concept):
    sub_concept_iri = get_sub_concept_iri(kb, owl_sub_concept)
    sup_concept_iri = get_sup_concept_iri(owl_sup_concept)
    role_iri = get_role_iri(kb, owl_sup_concept)
    pbox_id = pbox_parser.get_id(owl_sub_concept, owl_sup_concept)

    kb.add_axiom(sub_concept_iri, sup_concept_iri, role_iri, pbox_id)


def get_sub_concept_iri(kb, owl_sub_concept):
    sub_concept = owl_sub_concept
    if is_existential(owl_sub_concept):
        sub_concept = create_existential_concept(owl_sub_concept)
        if sub_concept not in kb.concepts:
            kb.add_concept(sub_concept)
    return sub_concept.iri


def get_role_iri(kb, owl_sup_concept):
    return extract_role_iri(owl_sup_concept) if is_existential(
        owl_sup_concept) else kb.is_a.iri


def get_sup_concept_iri(owl_sup_concept):
    return extract_concept_iri(owl_sup_concept) if is_existential(
        owl_sup_concept) else owl_sup_concept.iri


def create_existential_concept(owl_concept):
    role_iri = extract_role_iri(owl_concept)
    concept_iri = extract_concept_iri(owl_concept)
    existential_concept = gel.ExistentialConcept(role_iri, concept_iri)
    return existential_concept


def is_existential(owl_concept):
    return isinstance(owl_concept, owl.class_construct.Restriction)


def is_concept(owl_concept):
    return isinstance(owl_concept, owl.entity.ThingClass)


def extract_role_iri(owl_existential_concept):
    return type(owl_existential_concept.property()).iri


def extract_concept_iri(owl_existential_concept):
    return type(owl_existential_concept.value()).iri


def get_individual_sup_and_role(owl_individual_concept):
    for role in owl_individual_concept.get_properties():
        sup_concepts = owl_individual_concept.__getattr__(role.name)
        for sup_concept in sup_concepts:
            yield sup_concept, role


if __name__ == '__main__':
    parse('../data/example.owl')
