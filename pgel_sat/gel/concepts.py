from . import roles
from . import iri


class Concept:
    def __init__(self, iri):
        self.iri = str(iri)
        self.sup_arrows = set()
        self.sub_arrows = set()
        self._is_empty = False
        self.reaches = {self}
        self.is_individual = False
        self.is_existential = False

    @property
    def name(self):
        return iri.clear(self.iri)

    def __repr__(self):
        return f'Concept({self.iri})'

    def has_arrow(self, arrow):
        return arrow in self.sup_arrows

    def add_arrow(self, sup_arrow):
        sup_concept = sup_arrow.concept
        sub_arrow = sup_arrow.copy_from(self)
        if not self.has_arrow(sup_arrow):
            self.sup_arrows.add(sup_arrow)
            sup_concept.sub_arrows.add(sub_arrow)

    def remove_arrow(self, sup_arrow):
        sup_concept = sup_arrow.concept
        sub_arrow = sup_arrow.copy_from(self)
        if self.has_arrow(sup_arrow):
            self.sup_arrows.remove(sup_arrow)
            sup_concept.sub_arrows.remove(sub_arrow)

    def is_a(self):
        return (a.concept for a in self.sup_arrows
                if isinstance(a.role, roles.IsA) and a.pbox_id < 0)

    def sup_concepts(self, role='all'):
        return (a.concept for a in self.sup_arrows
                if role == 'all' or a.role == role)

    def sup_concepts_with_roles(self, without=None):
        return ((a.concept, a.role) for a in self.sup_arrows
                if a.role != without)

    def sub_concepts(self, role='all'):
        return (a.concept for a in self.sub_arrows
                if role == 'all' or a.role == role)

    def sub_concepts_with_roles(self, without=None):
        return ((a.concept, a.role) for a in self.sub_arrows
                if a.role != without)

    def is_empty(self):
        visited = set()

        def _is_empty(concept):
            if concept._is_empty:
                return True
            visited.add(concept)
            reached = False
            for sup_concept in concept.is_a():
                if sup_concept not in visited:
                    reached = reached or _is_empty(sup_concept)
            concept._is_empty = reached
            return concept._is_empty
        return _is_empty(self)

    def sup_concepts_reached(self, role='all'):
        visited = set()

        def _sup_concepts_reached(concept):
            visited.add(concept)
            yield concept
            for sup_concept in concept.sup_concepts(role=role):
                if sup_concept not in visited:
                    yield from _sup_concepts_reached(sup_concept)

        yield from _sup_concepts_reached(self)

    def sub_concepts_reach(self, role='all'):
        visited = set()

        def _sub_concepts_reach(concept):
            visited.add(concept)
            yield concept
            for sub_concept in concept.sub_concepts(role=role):
                if sub_concept not in visited:
                    yield from _sub_concepts_reach(sub_concept)

        yield from _sub_concepts_reach(self)


class EmptyConcept(Concept):
    def __init__(self, iri):
        super().__init__(iri)
        self._is_empty = True

    @property
    def name(self):
        return '⊥'


class GeneralConcept(Concept):
    def __init__(self, iri):
        super().__init__(iri)

    @property
    def name(self):
        return '⊤'


class InitialConcept(Concept):
    def __init__(self, iri):
        super().__init__(iri)


class IndividualConcept(Concept):
    def __init__(self, iri):
        super().__init__(iri)
        self.is_individual = True

    @property
    def name(self):
        return '{' + iri.clear(self.iri) + '}'


class ExistentialConcept(Concept):
    def __init__(self, role_iri, concept_iri):
        self.concept_iri = concept_iri
        self.role_iri = role_iri
        super().__init__(f'{role_iri}.{iri.clear(concept_iri)}')
        self.is_existential = True

    @property
    def name(self):
        return '"∃{}.{}"'.format(
            iri.clear(self.role_iri),
            iri.clear(self.concept_iri)
        )
