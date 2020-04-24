import numpy as np
import scipy.sparse as sp
from random import randrange
import read_ontology


class ProbabilisticKnowledgeBase:
    class ConceptInclusion():
        def __init__(self, **kwargs):
            self.sub_concept = kwargs.setdefault('sub_concept', 0)
            self.super_concept = kwargs.setdefault('super_concept', 0)
            self.role = kwargs.setdefault('role', 0)
            self.prob_axiom_index = kwargs.setdefault('prob_axiom_index', -1)

    def __init__(self):
        self.init = 0
        self.bottom = 1

        self.concepts = []
        self.concept_inclusions = []

        self.roles = []
        self.role_inclusions = []

        self.A = np.empty((0, 0))
        self.signs = []
        self.b = np.empty(0)

    def add_concept_inclusion(self, **kwargs):
        concept_inclusion = self.ConceptInclusion(**kwargs)
        self.concept_inclusions += [concept_inclusion]

    def n(self):
        return self.A.shape[1]

    def k(self):
        return self.A.shape[0]

    @classmethod
    def from_file(cls, file):
        kb = cls()
        onto = read_ontology.parse(file)
        kb.concepts = onto['concepts']
        kb.roles = onto['roles']

        for ci in onto['concept_inclusions']:
            kb.add_concept_inclusion(
                sub_concept=ci[0],
                super_concept=ci[1],
                role=ci[2],
                prob_axiom_index=ci[3]
            )

        b = []

        rows = []
        cols = []
        data = []
        for row, pbox_restriction in enumerate(onto['pbox_restrictions']):
            axiom_restrictions, sign, value = pbox_restriction
            for axiom_restriction in axiom_restrictions:
                col, value = axiom_restriction
                rows += [row]
                cols += [col]
                data += [value]
            b += [value]

        kb.A = sp.coo_matrix((data, (rows, cols))).todense()
        kb.b = np.array(b)
        return kb

    @classmethod
    def random(cls, concepts_count, axioms_count, prob_axioms_count=0):
        kb = cls()
        kb.concepts = [str(i) for i in range(concepts_count)]
        kb.roles = ['ISA', 'A']

        for _ in range(axioms_count):
            kb.add_concept_inclusion(
                sub_concept=randrange(concepts_count),
                super_concept=randrange(concepts_count),
                role=randrange(2)
            )

        kb.A = np.zeros((prob_axioms_count, prob_axioms_count))
        for i in range(prob_axioms_count):
            kb.add_concept_inclusion(
                sub_concept=randrange(concepts_count),
                super_concept=randrange(concepts_count),
                role=randrange(2),
                prob_axiom_index=i
            )
            kb.A[i, i] = 1

        kb.b = np.random.random_sample(prob_axioms_count)

        return kb
