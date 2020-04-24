from math import isclose
import numpy as np
from probabilistic_knowledge_base import ProbabilisticKnowledgeBase
import gelpp_max_sat
import linprog

EPSILON = 1e-7


def is_satisfatible(kb):
    return solve(kb)['satisfatible']


def solve(kb):
    C = initialize_C(kb)
    c = initialize_c(kb)
    d = initialize_d(kb)

    print('C:\n', C)
    print('c:', c)
    print('d:', d)
    lp = linprog.solve(c, C, d)

    print_lp(lp)

    i = 0
    while not is_min_cost_zero(lp):
        print('\n\niteration:', i)
        weights = get_weights(lp)
        print('weights', weights)
        result = generate_column(kb, weights)
        if not result['success']:
            return {'satisfatible': False}
        print('column', result['column'])

        column = result['column']
        C = np.column_stack((C, column))
        c = np.append(c, 0)

        lp = linprog.solve(c, C, d)
        print_lp(lp)
        i += 1

    assert (C @ lp['x'] < d + EPSILON / 2).all()
    assert (C @ lp['x'] > d - EPSILON / 2).all()

    return {'satisfatible': True, 'lp': lp}


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


def is_min_cost_zero(lp):
    return isclose(lp['cost'], 0, abs_tol=EPSILON)


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
    print('lp solution:')
    print('\tx:', lp['x'])
    print('\ty:', lp['y'])
    print('\tcost:', lp['cost'])


if __name__ == '__main__':
    filename = 'example8.owl'
    kb = ProbabilisticKnowledgeBase.from_file(filename)

    print('\nSOLVER STARTED')
    result = solve(kb)
    print('\nSOLVER FINISHED')
    print('is satisfatible:', result['satisfatible'])
