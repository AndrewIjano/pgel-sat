from . import iri


class Role:
    def __init__(self, iri):
        self.iri = iri
        self.axioms = []
        self.is_isa = False

    def add_axiom(self, sub_concept, sup_concept):
        self.axioms += [(sub_concept, sup_concept)]

    @property
    def name(self):
        return iri.clear(self.iri)

    def __repr__(self):
        return f'Role({self.iri})'


class IsA(Role):
    def __init__(self):
        super().__init__('is a')
        self.is_isa = True
