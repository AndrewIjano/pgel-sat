from probabilistic_knowledge_base import ProbabilisticKnowledgeBase
import numpy as np
import gelpp_max_sat
import linprog


def pgel_sat(kb):
    C = initialize_C(kb)
    c = initialize_c(kb)
    d = initialize_d(kb)

    lp = linprog.solve(c, C, d)

    while lp['cost'] != 0:
        weights = get_weights(lp)
        result = generate_column(kb, weights)
        if not result['success']:
            return False
        
        column = result['column']
        C = np.column_stack((C, column))
        c = np.append(c, 0)

        lp = linprog.solve(c, C, d)

    return lp


def initialize_C(kb):
    C_left = np.identity(kb.n() + kb.k() + 1)

    C_right = np.vstack((
        - np.identity(kb.n()),
        kb.A,
        np.zeros(kb.n())
    ))

    return np.hstack((C_left, C_right))


def initialize_c(kb):
    c_left = np.ones(kb.n() + kb.k() + 1)
    c_right = np.zeros(kb.n())
    return np.hstack((c_left, c_right))


def initialize_d(kb):
    return np.hstack((np.zeros(kb.n()), kb.b, 1))


def get_total_cost(c, x):
    return c @ x


def get_weights(lp):
    return np.array(lp['y'])


def generate_column(kb, weights):
    result = gelpp_max_sat.solve(kb, weights)
    if not result['success']:
        return {'success': False}

    column = extract_column(kb, result)
    if weights @ column < 0:
        return {'success': False}

    return {'success': True, 'column': column}


def extract_column(kb, result):
    m_column = np.ones(kb.n())
    for prob_axiom_index in result['prob_axiom_indexes']:
        m_column[prob_axiom_index] = 0

    column = np.hstack((m_column, np.zeros(kb.k()), 1))
    return column


def print_lp(lp):
    print('x:', lp['x'])
    print('y:', lp['y'])
    print('cost:', lp['cost'])


if __name__ == "__main__":
    filename = 'test.json'
    kb = ProbabilisticKnowledgeBase.from_file(filename)
    pgel_sat(kb)
