from pgel_sat import ProbabilisticKnowledgeBase, gel, is_satisfiable, solve
import argparse
import math
import numpy as np

EPSILON = 1e-7


def main():
    parser = init_argparse()
    args = parser.parse_args()

    filename = args.file[0]
    axiom = args.axiom[0].split()
    assert len(axiom) == 3

    kb = ProbabilisticKnowledgeBase.from_file(filename)
    kb = extend_knowledge_base(kb, axiom)

    min_bound = get_min_bound(kb)
    max_bound = get_max_bound(kb)

    show_bounds(axiom, kb, min_bound, max_bound)


def init_argparse():
    parser = argparse.ArgumentParser(
        description='Computes the probability bounds for a given axiom' \
                    'in a Probabilistic Graphic EL knowledge base.'
    )

    parser.add_argument(
        'file', nargs=1, type=str,
        help='path of the OWL file with the Probabilistic Graphic EL ontology')

    parser.add_argument(
        'axiom', nargs=1, type=str,
        help='the axiom in ntriples format'
    )
    return parser


def extend_knowledge_base(kb, axiom):
    sub_concept, role, sup_concept = axiom
    new_pbox_id = max(pbox_id for pbox_id in kb.pbox_axioms) + 1
    kb.add_axiom(sub_concept, sup_concept, role, pbox_id=new_pbox_id)
    extend_pbox(kb)
    return kb


def extend_pbox(kb):
    kb.A = np.hstack((kb.A, np.zeros((kb.k, 1))))
    kb.A = np.vstack((
        kb.A,
        np.hstack((np.zeros(kb.n - 1), 1))
    ))
    kb.b = np.hstack((kb.b, 1))
    kb.signs += ['>=']


def get_min_bound(kb):
    if is_extended_kb_satisfiable(kb, '==', 0):
        return 0

    k = math.ceil(abs(math.log2(EPSILON)))
    v_max = 1
    for j in range(1, k + 1):
        v_min = v_max - 1 / (2 ** j)
        if is_extended_kb_satisfiable(kb, '<=', v_min):
            v_max = v_min
    return v_max


def get_max_bound(kb):
    if is_extended_kb_satisfiable(kb, '==', 1):
        return 1

    k = math.ceil(abs(math.log2(EPSILON)))
    v_min = 0
    for j in range(1, k + 1):
        v_max = v_min + 1 / (2 ** j)
        if is_extended_kb_satisfiable(kb, '>=', v_max):
            v_min = v_max
    return v_min


def is_extended_kb_satisfiable(kb, sign: str, probability: float):
    kb.signs[-1] = sign
    kb.b[-1] = probability
    return is_satisfiable(kb)


def show_bounds(axiom, kb, min_bound, max_bound):
    sub_concept_iri, role_iri, sup_concept_iri = axiom
    sub_concept = kb.get_concept(sub_concept_iri)
    sup_concept = kb.get_concept(sup_concept_iri)
    role = kb.get_role(role_iri)
    arrow = gel.Arrow(sup_concept, role)
    print(f'{min_bound} <= P({sub_concept.name} {arrow.name}) <= {max_bound}')


if __name__ == '__main__':
    main()
