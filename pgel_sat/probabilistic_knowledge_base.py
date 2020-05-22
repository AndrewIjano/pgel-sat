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
        graph = gelpp.Graph('bot', 'top')

        for i in range(concepts_count):
            graph.add_concept(gelpp.Concept(i))

        graph.add_role(gelpp.Role('i'))

        for _ in range(axioms_count):
            graph.add_axiom(
                random.choice(graph.get_concepts().iri),
                random.choice(graph.get_concepts().iri),
                random.choice(graph.get_roles().iri)
            )

        A = np.zeros((prob_axioms_count, prob_axioms_count))
        for i in range(prob_axioms_count):
            graph.add_axiom(
                random.choice(graph.get_concepts()).iri,
                random.choice(graph.get_concepts()).iri,
                random.choice(graph.get_roles()).iri,
                pbox_id=i
            )
            A[i, i] = 1

        b = np.random.random_sample(prob_axioms_count)

        return cls(graph, A, b)
