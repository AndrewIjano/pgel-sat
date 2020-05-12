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
        self.axioms_role = []

        self.roles = [self.ISA]
        self.role_inclusions = []

        self.role_inc_duo = [[]]

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
        def _is_there_path_init_bot(v, visited):
            if v == 1:
                return True
            visited[v] = True
            reached = False
            for a in self.axioms[v]:
                c = a.concept
                i = a.role
                if not visited[c] and i == 0 and a.pbox_id < 0:
                    reached = reached or _is_there_path_init_bot(c, visited)
            return reached
        visited = [False] * len(self.concepts)
        return _is_there_path_init_bot(0, visited)

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
        self._add_axiom(sub_concept, sup_concept, role, pbox_id)

    def _add_axiom(self, sub_concept, sup_concept, role=0,
                   pbox_id=-1, is_derivated=False):
        new_arrow = Graph.Arrow(sup_concept, role, pbox_id, is_derivated)
        rev_arrow = Graph.Arrow(sub_concept, role, pbox_id, is_derivated)
        for arrow in self.axioms[sub_concept]:
            if arrow == new_arrow:
                return False

        if role == 0:
            self.axioms_isa += [(sub_concept, sup_concept)]
        else:
            self.axioms_role += [(sub_concept, sup_concept, role)]

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
            sub_role = (sub_role1, sub_role2)
        else:
            sub_role = self.get_role_idx(owl_sub_role)
            self.role_inc_duo[sub_role] += [sup_role]
        self.role_inclusions += [(sub_role, sup_role)]

    def link_to_init(self):
        self._add_axiom(0, 2)
        for i in self.individuals:
            self._add_axiom(0, i)

    def get_pbox_id(self, owl_sub_concept, owl_sup_concept):
        if self.is_existencial(owl_sub_concept):
            return -1
        comments = owl.comment[owl_sub_concept, self.owl_isa, owl_sup_concept]
        for comment in comments:
            c = comment.split()
            if len(c) > 1 and c[0] == self.PBOX_ID_HEADER:
                return int(c[1])
        return -1

    def complete(self):
        def all_c(c):
            return (a.concept for a in self.axioms[c])

        def isas(c):
            return (a.concept for a in self.axioms[c] if a.role == 0)

        def not_isas(c):
            return ((a.concept, a.role) for a in self.axioms[c] if a.role != 0)

        def isas_rev(d):
            return (a.concept for a in self.axioms_rev[d] if a.role == 0)

        def not_isas_rev(d):
            return ((a.concept, a.role)
                    for a in self.axioms_rev[d] if a.role != 0)

        def isa_reaches(c):
            def _isa_reaches(d, v):
                v[d] = True
                yield d
                for dd in isas(d):
                    if not v[dd]:
                        yield from _isa_reaches(dd, v)

            v = [False] * len(self.concepts)
            yield from _isa_reaches(c, v)

        def isa_reaches_rev(d):
            def _isa_reaches_rev(c, v):
                v[c] = True
                yield c
                for cc in isas_rev(c):
                    if not v[cc]:
                        yield from _isa_reaches_rev(cc, v)

            v = [False] * len(self.concepts)
            yield from _isa_reaches_rev(d, v)

        def reaches(d):
            def _reaches(c, v):
                v[c] = True
                yield c
                for cc in all_c(c):
                    if not v[cc]:
                        yield from _reaches(cc, v)

            v = [False] * len(self.concepts)
            yield from _reaches(d, v)

        def complete_rule_4():
            ok = False
            for concept in self.concepts:
                c = concept.index
                for c_dash in isas(c):
                    for d, i in not_isas(c_dash):
                        ok = ok or self._add_axiom(c, d, i, is_derivated=True)
            return ok

        def complete_rule_5():
            ok = False
            for ri_e in self.artificials:
                for d in isas(ri_e):
                    for concept in self.concepts:
                        c = concept.index
                        for e_dash, i in not_isas(c):
                            for e in isa_reaches(e_dash):
                                ok = ok or self._add_axiom(
                                    c, d, is_derivated=True)
            return ok

        def complete_rule_6():
            ok = False
            for d in isa_reaches_rev(1):
                for c, i in not_isas_rev(d):
                    ok = ok or self._add_axiom(c, d, is_derivated=True)
            return ok

        def complete_rule_7():
            ok = False
            for a in self.individuals:
                for c in isa_reaches_rev(a):
                    for d in isa_reaches_rev(a):
                        r = reaches(0)
                        if c in r and d in r:
                            ok = ok or self._add_axiom(c, d, is_derivated=True)
            return ok

        def complete_rule_8():
            ok = False
            for conc in self.concepts:
                c = conc.index
                for d, i in not_isas(c):
                    for j in self.role_inc_duo[i]:
                        ok = ok or self._add_axiom(c, d, j)
            return ok

        def complete_rule_9():
            ok = False
            for conc in self.concepts:
                c = conc.index
                for d_dash, i in not_isas(c):
                    for d, j in not_isas(d_dash):
                        for k in (
                                ri[1] for ri in self.role_inclusions
                                if(i, j) == ri[0]):
                            ok = ok or self._add_axiom(c, d, k)
            return ok

        ok = False

        while not ok:
            ok = True
            ok = ok and not complete_rule_4()
            ok = ok and not complete_rule_5()
            ok = ok and not complete_rule_6()
            ok = ok and not complete_rule_7()
            ok = ok and not complete_rule_8()
            ok = ok and not complete_rule_9()
