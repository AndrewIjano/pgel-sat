import json
import numpy as np
import scipy.sparse as sp
from random import randrange


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
        with open(file) as onto_file:
            onto = json.load(onto_file)

            kb.concepts = onto['vertices']
            kb.roles = onto['roles']

            for sub_concept_index, arrows in enumerate(onto['arrows']):
                for arrow in arrows:
                    kb.add_concept_inclusion(
                        sub_concept=sub_concept_index,
                        super_concept=arrow['vertex'],
                        role=arrow['role'],
                        prob_axiom_index=arrow['probabilityID']
                    )

            b = []

            rows = []
            cols = []
            data = []
            for row, prob_restriction in enumerate(
                    onto['probabilityRestrictions']):
                for axiom_restriction in prob_restriction['axiomRestrictions']:
                    col, value = axiom_restriction
                    rows += [row]
                    cols += [col]
                    data += [value]
                b += [prob_restriction['probabilityValue']]

            kb.A = sp.coo_matrix((data, (rows, cols))).todense()
            kb.b = np.array(b)
        return kb

    @classmethod
    def random(cls, concepts_count, axioms_count):
        kb = cls()
        kb.concepts = [str(i) for i in range(concepts_count)]
        kb.roles = ['ISA', 'A']

        for _ in range(axioms_count):
            kb.add_concept_inclusion(
                sub_concept=randrange(concepts_count),
                super_concept=randrange(concepts_count),
                role=randrange(2)
            )

        return kb
