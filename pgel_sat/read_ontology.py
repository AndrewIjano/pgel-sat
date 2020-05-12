import owlready2 as owl
from . import gelpp

INIT = 'INIT'
ISA = 'ISA'

PBOX_ID_HEADER = '#!pbox-id'
PBOX_RESTRICTION_HEADER = '#!pbox-restriction'


def parse(file):
    onto = owl.get_ontology(file)
    onto.load()
    classes = list(onto.classes())
    individuals = list(onto.individuals())

    graph = gelpp.Graph()

    graph.add_roles(onto.object_properties())
    graph.add_role_inclusions_from_roles(onto.object_properties())

    graph.add_concepts([owl.Nothing, owl.Thing])
    graph.add_concepts(classes)
    graph.add_concepts(individuals, is_individual=True)

    graph.link_to_init()

    graph.add_axioms_from_concepts([owl.Thing])
    graph.add_axioms_from_concepts(classes)
    graph.add_axioms_from_concepts(individuals)

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
    return {
        'graph': graph,
        'pbox_restrictions': pbox_restrictions
    }


if __name__ == '__main__':
    parse('../data/example8.owl')
