import json
import numpy as np
import scipy.sparse as sp
from random import randrange, sample, random


class ProbabilisticKnowledgeBase:
    class ConceptInclusion():
        def __init__(self, sub_concept, super_concept, role, prob_axiom_index):
            self.sub_concept = sub_concept
            self.super_concept = super_concept
            self.role = role
            self.prob_axiom_index = prob_axiom_index

    def __init__(self):
        self.init = 0
        self.bottom = 1

        self.concepts = []
        self.concept_inclusions = []

        self.roles = []
        self.role_inclusions = []

        self.A = np.empty((0, 0))
        self.signs = []
        self.b = []

    def add_concept_inclusion(self, sub_concept, super_concept, role, prob_axiom_index):
        concept_inclusion = self.ConceptInclusion(
            sub_concept, super_concept, role, prob_axiom_index)

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
                    role_index = arrow['role']
                    super_concept_index = arrow['vertex']
                    prob_axiom_index = arrow['probabilityID']
                    kb.add_concept_inclusion(
                        sub_concept_index, super_concept_index, role_index, prob_axiom_index)

            kb.b = []

            rows = []
            cols = []
            data = []
            for row, prob_restriction in enumerate(onto['probabilityRestrictions']):
                for axiom_restriction in prob_restriction['axiomRestrictions']:
                    col, value = axiom_restriction
                    rows += [row]
                    cols += [col]
                    data += [value]
                kb.b += [prob_restriction['probabilityValue']]

            kb.A = sp.coo_matrix((data, (rows, cols))).todense()
            kb.b = np.array(kb.b)
        return kb

    @classmethod
    def random(cls, axioms_count, concepts_count):

        kb = cls()

        kb.concepts = [str(i) for i in range(concepts_count)]
        kb.roles = ['ISA', 'A']

        prob_index = 0
        min_probs = 3
        for _ in range(axioms_count):
            sub_concept_index = randrange(concepts_count)
            super_concept_index = randrange(concepts_count)
            role_index = randrange(2)

            if min_probs > 0:
                prob_axiom_index = prob_index
                prob_index += 1
                min_probs -= 1
            else:
                prob_axiom_index = -1

            kb.add_concept_inclusion(
                sub_concept_index, super_concept_index, role_index, prob_axiom_index)

        rows = []
        cols = []
        data = []
        pbox_axioms_count = prob_index
        print(pbox_axioms_count)
        for row in range(pbox_axioms_count):
            for col in sample(list(range(pbox_axioms_count)), randrange(pbox_axioms_count)):
                rows += [row]
                cols += [col]
                data += [random()]
            kb.b += [random()]

        print(rows, cols, data)
        kb.A = sp.coo_matrix((data, (rows, cols))).todense()
        kb.b = np.array(kb.b)

        return kb