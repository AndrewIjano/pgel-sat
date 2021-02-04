from math import isclose
import numpy as np
from . import gel_max_sat
from . import linprog
import time

EPSILON = 1e-7
TRACE = False


def is_satisfiable(kb):
    return solve(kb)['satisfiable']


def solve(kb):
    C = initialize_C(kb)
    c = initialize_c(kb)
    d = initialize_d(kb)

    signs = initialize_signs(kb)
    trace(f'C:\n {C}')
    trace(f'c: {c}')
    trace(f'd: {d}')
    trace(f'signs: {signs}')
    lp = linprog.solve(c, C, d, signs)

    trace(str_lp(lp))

    i = 0
    iteration_times = []
    while not is_min_cost_zero(lp):
        start = time.time()
        trace(f'\n\niteration: {i}')
        result = generate_column(kb, lp)
        if not result['success']:
            return {'satisfiable': False, 'iterations': i,
                    'iteration_times': iteration_times}
        trace(f'column {result["column"]}')

        column = result['column']
        C = np.column_stack((C, column))
        c = np.append(c, 0)

        lp = linprog.solve(c, C, d, signs)
        trace(str_lp(lp))
        i += 1
        end = time.time()
        iteration_times += [end - start]

    assert_result(C @ lp.x, signs, d)
    return {'satisfiable': True, 'lp': lp, 'iterations': i,
            'iteration_times': iteration_times}


def initialize_C(kb):
    C_left = np.identity(kb.n + kb.k + 1)

    C_right = np.vstack((
        - np.identity(kb.n),
        kb.A,
        np.zeros(kb.n)
    ))

    return np.hstack((C_left, C_right))


def initialize_c(kb):
    c_left = np.ones(kb.n + kb.k + 1)
    c_right = np.zeros(kb.n)
    return np.hstack((c_left, c_right))


def initialize_d(kb):
    return np.hstack((np.zeros(kb.n), kb.b, 1))


def initialize_signs(kb):
    return ['==']*kb.n + kb.signs + ['==']


def is_min_cost_zero(lp):
    return isclose(lp.cost, 0, abs_tol=EPSILON)


def get_weights(lp):
    return np.array(lp.y)


def generate_column(kb, lp):
    weights = get_weights(lp)
    trace(f'weights {weights}')

    result = gel_max_sat.solve(kb, weights[:kb.n])

    if not result['success']:
        return {'success': False}

    column = extract_column(kb, result)
    if weights @ column < 0:
        return {'success': False}

    return {'success': True, 'column': column}


def extract_column(kb, result):
    m_column = np.ones(kb.n)
    for prob_axiom_index in result['prob_axiom_indexes']:
        m_column[prob_axiom_index] = 0

    column = np.hstack((m_column, np.zeros(kb.k), 1))
    return column


def assert_result(product, signs, d):
    for i, value in enumerate(product.T):
        if signs[i] in ['==', '<=']:
            assert value < d[i] + EPSILON/2
        if signs[i] in ['==', '=>']:
            assert value > d[i] - EPSILON/2


def str_lp(lp):
    return f'''lp solution:
    x: {lp.x}
    y: {lp.y}
    cost: {lp.cost}'''


def trace(string):
    if TRACE:
        print(string)
