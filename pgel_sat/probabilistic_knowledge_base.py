import numpy as np
import scipy.sparse as sp
import random
from . import owl
from . import gelpp


class ProbabilisticKnowledgeBase:
    def __init__(self, graph, A, b, signs=[]):
        self.graph = graph
        self.A = A
        self.b = b
        self.signs = signs

    def init(self):
        return self.graph.init.iri

    def bottom(self):
        return self.graph.bot.iri

    def add_concept_inclusion(self, **kwargs):
        concept_inclusion = self.ConceptInclusion(**kwargs)
        self.concept_inclusions += [concept_inclusion]

    def n(self):
        return self.A.shape[1]

    def k(self):
        return self.A.shape[0]

    def concepts(self):
        return self.graph.concepts.values()

    def is_existential(self, concept):
        return isinstance(concept, gelpp.ExistentialConcept)

    def is_individual(self, concept):
        return isinstance(concept, gelpp.IndividualConcept)

    @classmethod
    def from_file(cls, file):
        graph, pbox_restrictions = owl.parser.parse(file)
        graph.complete()

        b = []
        rows, cols, data = [], [], []
        for row, pbox_restriction in enumerate(pbox_restrictions):
            axiom_restrictions, sign, value = pbox_restriction
            for axiom_restriction in axiom_restrictions:
                col, coefficient = axiom_restriction
                rows += [row]
                cols += [col]
                data += [coefficient]
            b += [value]

        A = sp.coo_matrix((data, (rows, cols))).todense()
        b = np.array(b)
        return cls(graph, A, b)

    @classmethod
    def random(cls, concepts_count, axioms_count, prob_axioms_count=0):
        roles_count = 3
        graph = gelpp.Graph('bot', 'top')

        for i in range(concepts_count):
            concept = gelpp.Concept(str(i))
            if random.random() < axioms_count / (concepts_count**2):
                concept = gelpp.IndividualConcept(str(i))
            graph.add_concept(concept)

        for i in range(roles_count):
            graph.add_role(gelpp.Role(chr(ord('r') + i)))

        roles = [role for role in graph.get_roles() if role != graph.infinity]
        concepts = [c for c in graph.get_concepts() if c != graph.init]

        axioms = 0
        while axioms < axioms_count:
            axioms += graph.add_axiom(
                random.choice(concepts).iri,
                random.choice(concepts).iri,
                random.choice(roles).iri
            )

        A = np.zeros((prob_axioms_count, prob_axioms_count))

        p_axioms = 0
        while p_axioms < prob_axioms_count:
            if graph.add_axiom(
                random.choice(concepts).iri,
                random.choice(concepts).iri,
                random.choice(roles).iri,
                pbox_id=p_axioms
            ):
                p_axioms += 1
        graph.complete()

        b = np.zeros(prob_axioms_count)
        axioms_per_restriction = 3
        for i in range(prob_axioms_count):
            for j in range(axioms_per_restriction):
                axiom_index = np.random.randint(
                    prob_axioms_count)
                coefficient = np.random.rand()
                A[i, axiom_index] = coefficient
            b[i] = np.random.rand()

        return cls(graph, A, b)
