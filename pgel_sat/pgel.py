import numpy as np
import scipy.sparse as sp
import random
from . import owl, gel


class ProbabilisticKnowledgeBase(gel.KnowledgeBase):
    def __init__(self, empty_concept_iri, general_concept_iri, A=None, b=None, signs=[]):
        super().__init__(empty_concept_iri, general_concept_iri)
        self.A = A
        self.b = b
        self.signs = signs

    @property
    def n(self) -> int:
        return self.A.shape[1]

    @property
    def k(self) -> int:
        return self.A.shape[0]

    def add_probabilistic_restrictions(self, A, b, signs):
        self.A = A
        self.b = b
        self.signs = signs

    @classmethod
    def from_file(cls, file):
        kb, pbox_restrictions = owl.parser.parse(file)

        signs = []
        values = []
        rows, cols, data = [], [], []
        for row, pbox_restriction in enumerate(pbox_restrictions):
            axiom_restrictions, sign, value = pbox_restriction
            for axiom_restriction in axiom_restrictions:
                col, coefficient = axiom_restriction
                rows += [row]
                cols += [col]
                data += [coefficient]
            signs += [sign]
            values += [value]

        A = sp.coo_matrix((data, (rows, cols))).todense()
        b = np.array(values)

        kb.add_probabilistic_restrictions(A, b, signs)

        return kb

    @classmethod
    def random(cls,
               concepts_count,
               axioms_count,
               prob_axioms_count,
               axioms_per_restriction,
               prob_restrictions_count,
               coef_lo,
               coef_hi,
               b_lo,
               b_hi,
               sign_type,
               roles_count):

        kb = super(ProbabilisticKnowledgeBase, cls).random(concepts_count, axioms_count, prob_axioms_count)

        A = np.zeros((prob_restrictions_count, prob_axioms_count))

        get_sign = {
            'lo': lambda: '<=',
            'eq': lambda: '==',
            'hi': lambda: '>=',
            'all': lambda: random.choice(['<=', '==', '>='])
        }[sign_type]

        b = np.zeros(prob_restrictions_count)
        signs = []
        for i in range(prob_restrictions_count):
            A[i, i] = 1
            signs += [get_sign()]
            b[i] = np.random.uniform(b_lo, b_hi)

        kb.add_probabilistic_restrictions(A, b, signs)
        return kb
