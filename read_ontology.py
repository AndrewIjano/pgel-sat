import owlready2 as owl

INIT = 'INIT'
ISA = 'ISA'

PBOX_ID_HEADER = '#! pbox-id'
PBOX_RESTRICTION_HEADER = '#! pbox-restriction'


def parse(file):
    onto = owl.get_ontology(file)
    onto.load()

    classes = list(onto.classes())
    individuals = list(onto.individuals())

    basic_concepts = [INIT, owl.Nothing, owl.Thing] + classes + individuals
    roles = [ISA] + list(onto.object_properties())

    c_indexes = {concept: index for index,
                 concept in enumerate(basic_concepts)}
    r_indexes = {role: index for index, role in enumerate(roles)}

    concept_inclusions = []

    # create arrows from init to individuals and Thing
    init_idx = c_indexes[INIT]
    isa_idx = r_indexes[ISA]
    for i in individuals:
        concept_inclusions += [(init_idx, c_indexes[i], isa_idx, -1)]
    concept_inclusions += [(init_idx, c_indexes[owl.Thing], isa_idx, -1)]

    def get_prob_id(sub_concept, super_concept):
        if isinstance(sub_concept, owl.class_construct.Restriction):
            return -1

        comments = owl.comment[sub_concept, owl.rdfs_subclassof, super_concept]
        for comment in comments:
            lines = comment.split('\n')
            if len(lines) < 2:
                continue
            if lines[0] == PBOX_ID_HEADER:
                return int(lines[1])
        return -1

    def get_concept_inclusion(sub_concept, super_concept, basic_concepts):
        role_idx = 0
        super_basic_concept = super_concept

        if isinstance(sub_concept, owl.class_construct.Restriction):
            c_indexes[sub_concept] = len(basic_concepts)
            basic_concepts += [sub_concept]

        if isinstance(super_concept, owl.class_construct.Restriction):
            role_idx = r_indexes[type(super_concept.property())]
            super_basic_concept = type(super_concept.value())

        return (c_indexes[sub_concept],
                c_indexes[super_basic_concept],
                role_idx,
                get_prob_id(sub_concept,
                            super_concept))

    for sub_concept in basic_concepts[1:]:
        if sub_concept == owl.Nothing:
            continue

        for super_concept in sub_concept.is_a:
            concept_inclusions += [
                get_concept_inclusion(
                    sub_concept,
                    super_concept,
                    basic_concepts)]

        for super_concept in sub_concept.equivalent_to:
            concept_inclusions += [
                get_concept_inclusion(
                    sub_concept,
                    super_concept,
                    basic_concepts)]
            concept_inclusions += [
                get_concept_inclusion(
                    super_concept,
                    sub_concept,
                    basic_concepts)]

    def is_thing_comment(triple):
        return triple[0] == owl.Thing.storid and triple[1] == owl.comment.storid

    thing_comments = [triple for triple in onto.get_triples()
                      if is_thing_comment(triple)]

    pbox_restrictions = []
    for comment in thing_comments:
        comment_raw = comment[2]
        comment_lines = comment_raw.replace('\"', '').split('\n')
        if len(comment_lines) < 1:
            continue

        if comment_lines[0] != PBOX_RESTRICTION_HEADER:
            continue

        restriction_raw_lines = comment_lines[1:]
        axiom_restrictions = []
        for raw_line in restriction_raw_lines[:-2]:
            raw_line = raw_line.strip()
            pbox_id, pbox_coef = raw_line.split()
            pbox_id = int(pbox_id)
            pbox_coef = float(pbox_coef)
            axiom_restrictions += [(pbox_id, pbox_coef)]

        restriction_sign = restriction_raw_lines[-2].strip()
        restriction_value = float(restriction_raw_lines[-1])

        pbox_restrictions += [(axiom_restrictions,
                               restriction_sign,
                               restriction_value)]

    return {
        'concepts': basic_concepts,
        'roles': roles,
        'concept_inclusions': concept_inclusions,
        'pbox_restrictions': pbox_restrictions
    }
