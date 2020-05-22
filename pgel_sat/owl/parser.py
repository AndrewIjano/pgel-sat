import owlready2 as owl
from .. import gelpp
from . import pbox_parser


def parse(file):
    onto = owl.get_ontology(file)
    onto.load()

    graph = get_graph(onto)
    pbox_restrictions = pbox_parser.get_restrictions(onto)
    return graph, pbox_restrictions


def get_graph(onto):
    owl_concepts = list(onto.classes())
    owl_individuals = list(onto.individuals())
    owl_roles = onto.object_properties()

    graph = gelpp.Graph(owl.Nothing.iri, owl.Thing.iri)

    add_concepts(graph, owl_concepts, gelpp.Concept)
    add_concepts(graph, owl_individuals, gelpp.IndividualConcept)
    add_roles(graph, owl_roles)

    add_role_inclusions_from_roles(graph, owl_roles)
    owl_basic_concepts = [owl.Thing] + owl_concepts + owl_individuals
    add_axioms_from_concepts(graph, owl_basic_concepts)
    return graph


def add_concepts(graph, owl_concepts, ConceptClass):
    for owl_concept in owl_concepts:
        graph.add_concept(ConceptClass(owl_concept.iri))


def add_roles(graph, owl_roles):
    for owl_role in owl_roles:
        graph.add_role(gelpp.Role(owl_role.iri))


def add_role_inclusions_from_roles(graph, owl_roles):
    for owl_sup_role in owl_roles:
        for owl_sub_role in owl_sup_role.get_property_chain():
            add_role_inclusion_chain(graph, owl_sub_role, owl_sup_role)

        for owl_sub_role in owl_sup_role.subclasses():
            add_role_inclusion(graph, owl_sub_role, owl_sup_role)


def add_role_inclusion_chain(graph, owl_sub_role_chain, owl_sup_role):
    owl_sub_role1, owl_sub_role2 = owl_sub_role_chain.properties
    graph.add_role_inclusion_chain(
        (owl_sub_role1.iri, owl_sub_role2.iri),
        owl_sup_role.iri)


def add_role_inclusion(graph, owl_sub_role, owl_sup_role):
    graph.add_role_inclusion(owl_sub_role.iri, owl_sup_role.iri)


def add_axioms_from_concepts(graph, owl_concepts):
    for sub_concept in owl_concepts:
        if sub_concept == owl.Nothing:
            continue

        for sup_concept in sub_concept.is_a:
            add_axiom(graph, sub_concept, sup_concept)

        for sup_concept in sub_concept.equivalent_to:
            add_axiom(graph, sub_concept, sup_concept)
            add_axiom(graph, sup_concept, sub_concept)


def add_axiom(graph, owl_sub_concept, owl_sup_concept):
    sub_concept_iri = get_sub_concept_iri(graph, owl_sub_concept)
    sup_concept_iri = get_sup_concept_iri(owl_sup_concept)
    role_iri = get_role_iri(graph, owl_sup_concept)
    pbox_id = pbox_parser.get_id(owl_sub_concept, owl_sup_concept)

    graph.add_axiom(sub_concept_iri, sup_concept_iri, role_iri, pbox_id)


def get_sub_concept_iri(graph, owl_sub_concept):
    sub_concept = owl_sub_concept
    if is_existential(owl_sub_concept):
        sub_concept = create_existential_concept(owl_sub_concept)
        graph.add_concept(sub_concept)
    return sub_concept.iri


def get_role_iri(graph, owl_sup_concept):
    return extract_role_iri(owl_sup_concept) if is_existential(
        owl_sup_concept) else graph.is_a.iri


def get_sup_concept_iri(owl_sup_concept):
    return extract_concept_iri(owl_sup_concept) if is_existential(
        owl_sup_concept) else owl_sup_concept.iri


def create_existential_concept(owl_concept):
    role_iri = extract_role_iri(owl_concept)
    concept_iri = extract_concept_iri(owl_concept)
    existential_concept = gelpp.ExistentialConcept(role_iri, concept_iri)
    return existential_concept


def is_existential(owl_concept):
    return isinstance(owl_concept, owl.class_construct.Restriction)


def extract_role_iri(owl_existential_concept):
    return type(owl_existential_concept.property()).iri


def extract_concept_iri(owl_existential_concept):
    return type(owl_existential_concept.value()).iri


if __name__ == '__main__':
    parse('../data/example8.owl')
