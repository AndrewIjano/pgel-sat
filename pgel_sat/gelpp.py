from collections import namedtuple
import owlready2 as owl


class Graph():
    Concept = namedtuple(
        'Concept',
        ['iri',
         'name',
         'index',
         'is_artificial',
         'is_individual',
         'artificial_node_data'])

    Role = namedtuple(
        'Role',
        ['iri',
         'name',
         'index'])

    Arrow = namedtuple(
        'Arrow',
        ['concept',
         'role',
         'pbox_id',
         'is_derivated'])

    def __init__(self, **kwargs):
        self.INIT = Graph.Concept('init', 'init', 0, False, False, [])
        self.ISA = Graph.Role('isa', 'isa', 0)

        self.PBOX_ID_HEADER = '#!pbox-id'
        self.PBOX_RESTRICTION_HEADER = '#!pbox-restriction'
        self.concepts = [self.INIT]
        self.axioms = [[]]

        self.axioms_rev = [[]]
        self.artificials = []
        self.individuals = []
        self.axioms_isa = []
        self.axioms_by_role = [[]]
        self.is_a_bot = [False]

        self.roles = [self.ISA]
        self.role_inclusions = []

        self.role_inc_duo = [[]]
        self.role_inc_tri = {}

        self.concept_idxs = {self.INIT.name: 0}
        self.role_idxs = {self.ISA.name: 0}

        self.get_concept = lambda c: self.concept_idxs[str(
            c)] if str(c) in self.concept_idxs else -1
        self.get_role = lambda c: self.role_idxs[str(type(c.property()))]
        self.get_role_idx = lambda r: self.role_idxs[str(r)]
        self.get_value = lambda c: self.concept_idxs[str(type(c.value()))]

        self.is_existencial = lambda c: isinstance(
            c, owl.class_construct.Restriction)
        self.owl_isa = owl.rdfs_subclassof

    def is_there_path_init_bot(self):
        return self.is_a_bot[0]

    def add_concept(self, owl_concept, is_artificial=False,
                    is_individual=False):
        artificial_node_data = []

        index = len(self.concepts)
        self.concept_idxs[str(owl_concept)] = index

        iri = str(owl_concept)
        name = str(owl_concept)
        if not is_artificial:
            iri = owl_concept.iri
            name = owl_concept.name

        if is_artificial:
            role = self.get_role(owl_concept)
            conc = self.get_value(owl_concept)
            artificial_node_data = [role, conc]
            self.artificials += [index]

        if is_individual:
            self.individuals += [index]

        self.is_a_bot += [index == 1]

        concept = Graph.Concept(
            iri=iri,
            name=name,
            index=index,
            artificial_node_data=artificial_node_data,
            is_artificial=is_artificial,
            is_individual=is_individual,
        )
        self.concepts += [concept]
        self.axioms += [[]]
        self.axioms_rev += [[]]

    def add_concepts(self, owl_concepts, is_artificial=False,
                     is_individual=False):
        for owl_concept in owl_concepts:
            self.add_concept(owl_concept, is_artificial, is_individual)

    def add_role(self, owl_role):
        index = len(self.roles)
        role = Graph.Role(
            iri=owl_role.iri,
            name=owl_role.name,
            index=index
        )
        self.role_idxs[str(owl_role)] = index
        self.roles += [role]
        self.role_inc_duo += [[]]
        self.axioms_by_role += [[]]

    def add_roles(self, owl_roles):
        for owl_role in owl_roles:
            self.add_role(owl_role)

    def add_axioms_from_concepts(self, owl_concepts):
        for sub_concept in owl_concepts:
            if sub_concept == owl.Nothing:
                continue
            for sup_concept in sub_concept.is_a:
                self.add_axiom(sub_concept, sup_concept)
            for sup_concept in sub_concept.equivalent_to:
                self.add_axiom(sub_concept, sup_concept)
                self.add_axiom(sup_concept, sub_concept)

    def add_axiom(self, owl_sub_concept, owl_sup_concept):
        sub_concept = self.get_concept(owl_sub_concept)
        sup_concept = self.get_concept(owl_sup_concept)
        role = 0

        if self.is_existencial(owl_sub_concept):
            self.add_concept(owl_sub_concept, is_artificial=True)
            sub_concept = self.concept_idxs[str(owl_sub_concept)]

        if self.is_existencial(owl_sup_concept):
            role = self.get_role(owl_sup_concept)
            sup_concept = self.get_value(owl_sup_concept)

        pbox_id = self.get_pbox_id(owl_sub_concept, owl_sup_concept)
        self.__add_axiom(sub_concept, sup_concept, role, pbox_id)

    def __add_axiom(self, sub_concept, sup_concept, role=0,
                    pbox_id=-1, is_derivated=False):
        new_arrow = Graph.Arrow(sup_concept, role, pbox_id, is_derivated)
        rev_arrow = Graph.Arrow(sub_concept, role, pbox_id, is_derivated)
        if new_arrow in self.axioms[sub_concept]:
            return False

        # GC4
        if role == 0:
            for c, i in self.sup_concepts_role(sup_concept):
                self.__add_axiom(sup_concept, c, i, is_derivated=True)
        else:
            for c in self.sub_concepts(sub_concept):
                self.__add_axiom(c, sub_concept, role, is_derivated=True)

        # GC6
        if self.is_there_path_to_bot(sup_concept) and role != 0:
            self.is_a_bot[sub_concept] = True
            self.__add_axiom(sub_concept, sup_concept, is_derivated=True)

        # GC8
        for sup_role in self.role_inc_duo[role]:
            self.__add_axiom(
                sub_concept,
                sup_concept,
                sup_role,
                is_derivated=True)

        # GC9
        for d, j in self.sup_concepts_role(sup_concept):
            for k in self.role_inc_tri.get((role, j), []):
                self.__add_axiom(sub_concept, d, k, is_derivated=True)

        self.axioms_by_role[role] += [(sub_concept, sup_concept)]

        self.axioms[sub_concept] += [new_arrow]
        self.axioms_rev[sup_concept] += [rev_arrow]
        return True

    def add_role_inclusions_from_roles(self, owl_roles):
        for owl_sup_role in owl_roles:
            for owl_sub_role in owl_sup_role.get_property_chain():
                self.add_role_inclusion(owl_sub_role, owl_sup_role)
            for owl_sub_role in owl_sup_role.subclasses():
                self.add_role_inclusion(owl_sub_role, owl_sup_role)

    def add_role_inclusion(self, owl_sub_role, owl_sup_role):
        sup_role = self.get_role_idx(owl_sup_role)
        if isinstance(owl_sub_role, owl.PropertyChain):
            sub_role1, sub_role2 = map(
                self.get_role_idx, owl_sub_role.properties)

            sup_roles = self.role_inc_tri.get((sub_role1, sub_role2), [])
            sup_roles += [sup_role]
            self.role_inc_tri[sub_role1, sub_role2] = sup_roles

            for c, d_prime in self.axioms_by_role[sub_role1]:
                for d, j in self.sub_concepts_role(d_prime):
                    if j == sub_role2:
                        self.__add_axiom(c, d, sup_role, is_derivaated=True)
        else:
            sub_role = self.get_role_idx(owl_sub_role)

            self.role_inc_duo[sub_role] += [sup_role]
            for c, d in self.axioms_by_role[sub_role]:
                self.__add_axiom(c, d, sup_role, is_derivated=True)

    def link_to_init(self):
        self.__add_axiom(0, 2)
        for i in self.individuals:
            self.__add_axiom(0, i)

    def get_pbox_id(self, owl_sub_concept, owl_sup_concept):
        if self.is_existencial(owl_sub_concept):
            return -1
        comments = owl.comment[owl_sub_concept, self.owl_isa, owl_sup_concept]
        for comment in comments:
            c = comment.split()
            if len(c) > 1 and c[0] == self.PBOX_ID_HEADER:
                return int(c[1])
        return -1

    def sup_concepts(self, c):
        return self.sup_concepts_role_i(c, 0)

    def sup_concepts_role(self, c):
        return ((a.concept, a.role) for a in self.axioms[c] if a.role != 0)

    def sup_concepts_role_i(self, c, i):
        return (a.concept for a in self.axioms[c] if a.role == i)

    def sub_concepts(self, d):
        return (a.concept for a in self.axioms_rev[d] if a.role == 0)

    def sub_concepts_role(self, d):
        return ((a.concept, a.role)
                for a in self.axioms_rev[d] if a.role != 0)

    def is_there_path_to_bot(self, c):
        def _is_there_path_to_bot(v, visited):
            if self.is_a_bot[v]:
                return True
            visited[v] = True
            reached = False
            for a in self.axioms[v]:
                c = a.concept
                i = a.role
                if not visited[c] and i == 0 and a.pbox_id < 0:
                    reached = reached or _is_there_path_to_bot(c, visited)

            self.is_a_bot[v] = reached
            return reached
        visited = [False] * len(self.concepts)
        return _is_there_path_to_bot(0, visited)

    def complete(self):
        def sup_concepts_any_role(c):
            return (a.concept for a in self.axioms[c])

        def reaches_by_is_a(c):
            def _reaches_by_is_a(d, v):
                v[d] = True
                yield d
                for dd in self.sup_concepts(d):
                    if not v[dd]:
                        yield from _reaches_by_is_a(dd, v)

            v = [False] * len(self.concepts)
            yield from _reaches_by_is_a(c, v)

        def reaches_by_is_a_rev(d):
            def _reaches_by_is_a_rev(c, v):
                v[c] = True
                yield c
                for cc in self.sub_concepts(c):
                    if not v[cc]:
                        yield from _reaches_by_is_a_rev(cc, v)

            v = [False] * len(self.concepts)
            yield from _reaches_by_is_a_rev(d, v)

        def reaches(d):
            def _reaches(c, v):
                v[c] = True
                yield c
                for cc in sup_concepts_any_role(c):
                    if not v[cc]:
                        yield from _reaches(cc, v)

            v = [False] * len(self.concepts)
            yield from _reaches(d, v)

        def sub_concepts_with_role(i, e):
            for concept in self.concepts:
                c = concept.index
                for e_prime in self.sup_concepts_role_i(c, i):
                    if e in reaches_by_is_a(e_prime):
                        yield c

        def concepts_connected_by_artificial(ri_e):
            i, e = self.concepts[ri_e].artificial_node_data
            for c in sub_concepts_with_role(i, e):
                for d in self.sup_concepts(ri_e):
                    yield c, d

        def complete_rule_5():
            ok = False
            for ri_e in self.artificials:
                for c, d in concepts_connected_by_artificial(ri_e):
                    ok = ok or self.__add_axiom(c, d, is_derivated=True)
            return ok

        def is_reached_by_init(c, d):
            reached_by_init = reaches(self.INIT.index)
            return c in reached_by_init and d in reached_by_init

        def complete_rule_7():
            ok = False
            for a in self.individuals:
                for c in reaches_by_is_a_rev(a):
                    for d in reaches_by_is_a_rev(a):
                        if is_reached_by_init(c, d):
                            ok = ok or self.__add_axiom(
                                c, d, is_derivated=True)
            return ok

        ok = False

        while not ok:
            ok = True
            ok = ok and not complete_rule_5()
            ok = ok and not complete_rule_7()
