from . import roles


class Arrow:
    def __init__(self, concept, role, pbox_id=-1, is_derived=False):
        self.concept = concept
        self.role = role
        self.pbox_id = pbox_id
        self.is_derived = is_derived

    def copy_from(self, concept):
        return Arrow(concept, self.role, self.pbox_id, self.is_derived)

    def __eq__(self, other):
        if not isinstance(other, Arrow):
            return NotImplemented

        return (self.concept == other.concept and
                self.role == other.role)

    def __hash__(self):
        return hash((self.concept.iri, self.role.iri))

    def __repr__(self):
        return f'Arrow({repr(self.concept)},' \
               + f' {repr(self.role)},' \
               + f' {self.pbox_id},' \
               + f' {self.is_derived})'

    @property
    def name(self):
        is_isa = isinstance(self.role, roles.IsA)
        return '⊑ {}{}'.format(
            '' if is_isa else f'∃{self.role.name}.',
            self.concept.name
        )
