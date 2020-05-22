import owlready2 as owl

PBOX_ID_HEADER = '#!pbox-id'
PBOX_RESTRICTION_HEADER = '#!pbox-restriction'


def get_id(owl_sub_concept, owl_sup_concept):
    if is_existential(owl_sub_concept):
        return -1

    comments = get_comments(owl_sub_concept, owl_sup_concept)
    for comment in comments:
        tokens = comment.split()
        if len(tokens) > 1 and tokens[0] == PBOX_ID_HEADER:
            return int(tokens[1])
    return -1


def is_existential(owl_concept):
    return isinstance(owl_concept, owl.class_construct.Restriction)


def get_comments(owl_sub_concept, owl_sup_concept):
    owl_is_a = owl.rdfs_subclassof
    return owl.comment[owl_sub_concept, owl_is_a, owl_sup_concept]


def get_restrictions(onto):
    def is_thing_comment(triple):
        return triple[0] == owl.Thing.storid \
            and triple[1] == owl.comment.storid

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
    return pbox_restrictions
