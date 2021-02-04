import random
from .concepts import (
    Concept,
    EmptyConcept,
    GeneralConcept,
    ExistentialConcept,
    IndividualConcept,
)
from .roles import Role, IsA, ArtificialRole
from .arrows import Arrow

from collections import defaultdict


class Axiom:
    def __init__(self, graph, sub_concept, sup_concept, role, pbox_id=-1):
        self.graph = graph
        self.sub_concept = graph.get_concept(sub_concept)
        self.sup_concept = graph.get_concept(sup_concept)
        self.role = graph.get_role(role)
        self.pbox_id = pbox_id

    @property
    def arrow(self):
        return Arrow(self.sup_concept, self.role, self.pbox_id)

    @property
    def is_new(self):
        return not self.sub_concept.has_arrow(self.arrow)

    @property
    def is_uncertain(self):
        return self.pbox_id >= 0

    def fix_existential_head(self):
        existential_concept = ExistentialConcept(self.role.iri, self.sup_concept.iri)
        if self.graph.has_concept(existential_concept):
            self.sup_concept = self.graph.get_concept(existential_concept.iri)
            self.role = self.graph.is_a

    def add(self):
        self.sub_concept.add_arrow(self.arrow)
        self.role.add_axiom(self.sub_concept, self.sup_concept)

    def __hash__(self):
        return hash((self.sub_concept.iri, self.sup_concept.iri, self.role.iri, self.pbox_id))

    def __repr__(self):
        return f'Axiom({self.sub_concept}, {self.sup_concept}, {self.role}, {self.pbox_id})'


class KnowledgeBase:
    def __init__(self, empty_concept_iri, general_concept_iri):
        self.init = Concept('init')
        self.bot = EmptyConcept(empty_concept_iri)
        self.top = GeneralConcept(general_concept_iri)

        self.is_a = IsA()

        self._concepts = {c.iri: c for c in [self.init, self.bot, self.top]}
        self._roles = {r.iri: r for r in [self.is_a]}

        self.role_inclusions = defaultdict(list)
        self.pbox_axioms = {}

        self.init.add_arrow(Arrow(self.top, self.is_a))

    @property
    def has_path_init_to_bot(self):
        return self.init.is_empty()

    @property
    def concepts(self):
        return list(self._concepts.values())

    @property
    def existential_concepts(self):
        return [concept for concept in self.concepts
                if isinstance(concept, ExistentialConcept)]

    @property
    def individuals(self):
        return [concept for concept in self.concepts
                if isinstance(concept, IndividualConcept)]

    @property
    def roles(self):
        return list(self._roles.values())

    def add_concept(self, concept):
        self._concepts[concept.iri] = concept

        if isinstance(concept, IndividualConcept):
            self.link_individual_concept(concept)

        if isinstance(concept, ExistentialConcept):
            self.fix_previous_existential_head_axioms(concept)
            self.link_existential_concept(concept)

    def link_individual_concept(self, concept):
        self.init.add_arrow(Arrow(concept, self.is_a))

    def has_concept(self, concept):
        return concept.iri in self._concepts

    def get_concept(self, concept):
        if isinstance(concept, Concept):
            return concept
        if concept not in self._concepts:
            raise ValueError(f'Concept missing: {concept}')
        return self._concepts[concept]

    def fix_previous_existential_head_axioms(self, existential_concept):
        role = self.get_role(existential_concept.role_iri)
        origin_concept = self.get_concept(existential_concept.concept_iri)

        def outdated_sub_concepts():
            for sub_concept, sup_concept in role.axioms:
                if sup_concept == origin_concept:
                    yield sub_concept

        def new_role_axioms():
            axioms = []
            for sub_concept, sup_concept in role.axioms:
                if sup_concept != origin_concept:
                    axioms += [(sub_concept, sup_concept)]
            return axioms

        for sub_concept in outdated_sub_concepts():
            arrow = Arrow(origin_concept, role)
            sub_concept.remove_arrow(arrow)
            self.add_axiom(sub_concept, existential_concept, self.is_a)

        role.axioms = new_role_axioms()

    def link_existential_concept(self, existential_concept):
        # get ri
        role_iri = existential_concept.role_iri
        # get Cj
        concept_iri = existential_concept.concept_iri

        # create u_{ri.Cj}
        artificial_role = ArtificialRole(role_iri, concept_iri)
        self.add_role(artificial_role)
        # link concept and existential concept
        self.add_axiom(
            concept_iri,
            existential_concept,
            artificial_role,
            is_immutable=True
        )

        # add '∃ri.Cj' ⊑ ∃ri.Cj
        self.add_axiom(
            existential_concept,
            concept_iri,
            role_iri,
            is_immutable=True)

    def add_role(self, role):
        self._roles[role.iri] = role

    def get_role(self, role):
        if isinstance(role, Role):
            return role
        if role not in self._roles:
            raise ValueError(f'Role missing: {role}')
        return self._roles[role]

    def add_chained_role_inclusion(self, sub_roles_iri, sup_role_iri):
        sup_role = self.get_role(sup_role_iri)
        self.role_inclusions[sub_roles_iri] += [sup_role]

    def add_role_inclusion(self, sub_role_iri, sup_role_iri):
        sup_role = self.get_role(sup_role_iri)
        self.role_inclusions[sub_role_iri] += [sup_role]

    def add_random_axioms(self, axioms_count, is_uncertain=False):
        axioms = 0
        while axioms < axioms_count:
            pbox_id = axioms if is_uncertain else -1
            axioms += self.add_random_axiom(pbox_id=pbox_id)

    def add_random_axiom(self, pbox_id=-1):
        sub_concept = random.choice(self.concepts).iri
        valid_sup_concepts = [c for c in self.concepts if c not in (sub_concept, self.init)]
        sup_concept = random.choice(valid_sup_concepts).iri
        return self.add_axiom(
            sub_concept,
            sup_concept,
            random.choice(self.roles).iri,
            pbox_id=pbox_id
        )

    def add_axiom(self, sub_concept, sup_concept, role,
                  pbox_id=-1, is_immutable=False):

        axiom = Axiom(self, sub_concept, sup_concept, role, pbox_id)
        if not is_immutable:
            axiom.fix_existential_head()

        if not axiom.is_new:
            return False

        axiom.add()
        if axiom.is_uncertain:
            self.add_pbox_axiom(axiom)

        return True

    def add_pbox_axiom(self, axiom):
        self.pbox_axioms[axiom.pbox_id] = (axiom.sub_concept, axiom.sup_concept, axiom.role)

    @classmethod
    def random(cls,
               concepts_count=20,
               axioms_count=80,
               uncertain_axioms_count=10,
               roles_count=2):

        graph = cls('bot', 'top')
        # add concepts
        for i in range(concepts_count):
            concept = Concept(i)
            graph.add_concept(concept)

        # add roles
        for i in range(roles_count):
            graph.add_role(Role(chr(ord('r') + i)))

        # add certain axioms randomly
        graph.add_random_axioms(axioms_count)

        # add uncertain axioms randomly
        graph.add_random_axioms(uncertain_axioms_count, is_uncertain=True)
        return graph
