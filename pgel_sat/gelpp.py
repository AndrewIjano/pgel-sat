class Concept:
    def __init__(self, iri):
        self.iri = iri
        self.sup_arrows = []
        self.sub_arrows = []
        self._is_empty = False
        self.reaches = {self}

    def has_arrow(self, arrow):
        return arrow in self.sup_arrows

    def add_arrow(self, sup_arrow):
        sup_concept = sup_arrow.concept
        sub_arrow = sup_arrow.copy_from(self)
        if not self.has_arrow(sup_arrow):
            self.sup_arrows += [sup_arrow]
            sup_concept.sub_arrows += [sub_arrow]

    def is_a(self):
        return (a.concept for a in self.sup_arrows
                if isinstance(a.role, IsA) and a.pbox_id < 0)

    def sup_concepts(self, role=None):
        return (a.concept for a in self.sup_arrows
                if role is not None and a.role == role)

    def sup_concepts_with_roles(self, without=None):
        return ((a.concept, a.role) for a in self.sup_arrows
                if a.role != without)

    def sub_concepts(self, role=None):
        return (a.concept for a in self.sub_arrows
                if role is not None and a.role == role)

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
        return _is_empty(self)

    def sup_concepts_reached(self, role=None):
        visited = set()

        def _sup_concepts_reached(concept):
            visited.add(concept)
            yield concept
            for sup_concept in concept.sup_concepts(role=role):
                if sup_concept not in visited:
                    yield from _sup_concepts_reached(sup_concept)

        yield from _sup_concepts_reached(self)

    def sub_concepts_reach(self, role=None):
        visited = set()

        def _sub_concepts_reached(concept):
            visited.add(concept)
            yield concept
            for sub_concept in concept.sub_concepts(role=role):
                if sub_concept not in visited:
                    yield from _sub_concepts_reached(sub_concept)

        yield from _sub_concepts_reached(self)


class EmptyConcept(Concept):
    def __init__(self, iri):
        super().__init__(iri)
        self._is_empty = True


class IndividualConcept(Concept):
    def __init__(self, iri):
        super().__init__(iri)


class ExistentialConcept(Concept):
    def __init__(self, role_iri, concept_iri):
        self.concept_iri = concept_iri
        self.role_iri = role_iri
        super().__init__(f'{role_iri}.{concept_iri}')


class Arrow():
    def __init__(self, concept, role, pbox_id=-1, is_derivated=False):
        self.concept = concept
        self.role = role
        self.pbox_id = pbox_id
        self.is_derivated = is_derivated

    def copy_from(self, concept):
        return Arrow(concept, self.role, self.pbox_id, self.is_derivated)

    def __eq__(self, other):
        if not isinstance(other, Arrow):
            return NotImplemented

        return (self.concept == other.concept and
                self.role == other.role and
                self.pbox_id == other.pbox_id and
                self.is_derivated == other.is_derivated)


class Role():
    def __init__(self, iri):
        self.iri = iri
        self.axioms = []

    def add_axiom(self, sub_concept, sup_concept):
        self.axioms += [(sub_concept, sup_concept)]


class IsA(Role):
    def __init__(self):
        super().__init__('is a')


class Graph():
    def __init__(self, empty_concept_iri, general_concept_iri):
        self.init = Concept('init')
        self.bot = EmptyConcept(empty_concept_iri)
        self.top = Concept(general_concept_iri)

        self.is_a = IsA()
        self.infinity = Role('∞')

        self.concepts = {c.iri: c for c in [self.init, self.bot, self.top]}
        self.roles = {r.iri: r for r in [self.is_a, self.infinity]}
        self.role_inclusions = {}

        self.init.add_arrow(Arrow(self.top, self.is_a))

    def has_path_init_to_bot(self):
        return self.init.is_empty()

    def add_concept(self, concept):
        self.concepts[concept.iri] = concept

        if isinstance(concept, IndividualConcept):
            self.init.add_arrow(Arrow(concept, self.is_a))

    def get_concept(self, concept_iri):
        return self.concepts[concept_iri]
    
    def get_concepts(self):
        return list(self.concepts.values())

    def add_role(self, role):
        self.roles[role.iri] = role

    def get_role(self, role_iri):
        return self.roles[role_iri]

    def get_roles(self):
        return list(self.roles.values())

    def add_chained_role_inclusion(self, sub_roles_iri, sup_role_iri):
        sub_role1 = self.get_role(sub_roles_iri[0])
        sub_role2 = self.get_role(sub_roles_iri[1])
        sup_role = self.get_role(sup_role_iri)

        sup_roles = self.role_inclusions.get(sub_roles_iri, [])
        sup_roles += [sup_role]
        self.role_inclusions[sub_roles_iri] = sup_roles
        self.check_new_derivations_from_chained_role_inclusions(
            sub_role1, sub_role2, sup_role)

    def check_new_derivations_from_chained_role_inclusions(
            self, sub_role1, sub_role2, sup_role):
        for c, d_prime in sub_role1.axioms():
            for d in d_prime.sup_concepts(sub_role2):
                self.add_axiom(c.iri, d.iri, sup_role.iri, is_derivated=True)

    def add_role_inclusion(self, sub_role_iri, sup_role_iri):
        sub_role = self.get_role(sub_role_iri)
        sup_role = self.get_role(sup_role_iri)

        sup_roles = self.role_inclusions.get(sub_role_iri, [])
        sup_roles += [sup_role]
        self.role_inclusions[sub_role_iri] = sup_roles
        self.check_new_derivations_from_role_inclusions(sub_role, sup_role)

    def check_new_derivations_from_role_inclusions(self, sub_role, sup_role):
        for c, d in sub_role.axioms():
            self.add_axiom(c, d, sup_role, is_derivated=True)

    def add_axiom(self, sub_concept, sup_concept, role,
                  pbox_id=-1, is_derivated=False):
        if not isinstance(sub_concept, Concept):
            sub_concept = self.get_concept(sub_concept)
        if not isinstance(sup_concept, Concept):
            sup_concept = self.get_concept(sup_concept)
        if not isinstance(role, Role):
            role = self.get_role(role)

        arrow = Arrow(sup_concept, role, pbox_id, is_derivated)
        if not sub_concept.has_arrow(arrow):
            sub_concept.add_arrow(arrow)

            axiom = (sub_concept, sup_concept, role)
            self.check_new_derivations_from_axioms(axiom)
            self.check_new_paths_to_bot(axiom)
            self.check_new_derivations_from_axioms_and_roles(axiom)
            return True
        return False

    def check_new_derivations_from_axioms(self, axiom):
        sub_concept, sup_concept, role = axiom
        if role == self.is_a:
            for c, i in sup_concept.sup_concepts_with_roles(without=self.is_a):
                self.add_axiom(sup_concept, c, i, is_derivated=True)
            return
        for c in sub_concept.sub_concepts(role=self.is_a):
            self.add_axiom(c, sub_concept, role, is_derivated=True)

    def check_new_paths_to_bot(self, axiom):
        sub_concept, sup_concept, role = axiom
        if sup_concept.is_empty() and role != self.is_a:
            sub_concept._is_empty = True
            is_a = self.is_a
            self.add_axiom(sub_concept, sup_concept, is_a, is_derivated=True)

    def check_new_derivations_from_axioms_and_roles(self, axiom):
        sub_concept, sup_concept, role = axiom
        for sup_role in self.role_inclusions.get(role.iri, []):
            self.add_axiom(sub_concept, sup_concept, role, is_derivated=True)

        for d, j in sup_concept.sub_concepts_with_roles(without=self.is_a):
            for k in self.role_inclusions.get((role.iri, j.iri), []):
                self.add_axiom(sub_concept, d, k, is_derivated=True)

    def existential_concepts(self):
        return (concept for concept in self.concepts.values()
                if isinstance(concept, ExistentialConcept))

    def inidividuals(self):
        return (concept for concept in self.concepts.values()
                if isinstance(concept, IndividualConcept))

    def complete(self):
        def concepts_connected_by_existential(ri_e):
            i = self.get_role(ri_e.role_iri)
            e = self.get_concept(ri_e.concept_iri)
            for c in e.sub_concepts(role=i):
                for d in ri_e.sup_concepts(role=self.is_a):
                    self.add_axiom(e, ri_e, self.infinity)
                    yield c, d

        def complete_rule_5():
            ok = False
            for ri_e in self.existential_concepts():
                for c, d in concepts_connected_by_existential(ri_e):
                    ok = ok or self.add_axiom(
                        c, d, self.is_a, is_derivated=True)
            return ok

        def is_reached_by_init(c, d):
            reached_by_init = self.init.sup_concepts_reached()
            return c in reached_by_init and d in reached_by_init

        def complete_rule_7():
            ok = False
            for a in self.inidividuals():
                for c in a.sub_concepts_reach():
                    for d in a.sub_concepts_reach():
                        if is_reached_by_init(c, d):
                            ok = ok or self.add_axiom(
                                c, d, self.is_a, is_derivated=True)
            return ok

        ok = False
        while not ok:
            ok = True
            ok = ok and not complete_rule_5()
            ok = ok and not complete_rule_7()
