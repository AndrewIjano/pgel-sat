import numpy as np
from swiglpk import *


def solve(c, C, d):
    lp = create_minimization_problem()

    rows_count = set_rows(lp, d)
    cols_count = set_objective(lp, c)
    set_coefficients(lp, C)

    glp_interior(lp, None)

    x = get_primal_solution(lp, cols_count)
    y = get_dual_solution(lp, rows_count)
    cost = get_cost(lp)

    delete_problem(lp)
    return {'x': x, 'y': y, 'cost': cost}


def create_minimization_problem():
    glp_term_out(GLP_OFF)

    lp = glp_create_prob()
    glp_set_obj_dir(lp, GLP_MIN)
    return lp


def set_rows(lp, d):
    rows_count = len(d)
    glp_add_rows(lp, rows_count)
    for idx, bnd in enumerate(d):
        glp_set_row_bnds(lp, idx + 1, GLP_FX, bnd, bnd)

    return rows_count


def set_objective(lp, c):
    cols_count = len(c)
    glp_add_cols(lp, cols_count)
    for idx, coef in enumerate(c):
        glp_set_col_bnds(lp, idx + 1, GLP_LO, 0.0, 0.0)
        glp_set_obj_coef(lp, idx + 1, coef)

    return cols_count


def set_coefficients(lp, C):
    elements_count = np.count_nonzero(C)
    i_C = intArray(1 + elements_count)
    j_C = intArray(1 + elements_count)
    a_C = doubleArray(1 + elements_count)

    for idx, (i, j) in enumerate(zip(*C.nonzero()), 1):
        i_C[idx] = int(i + 1)
        j_C[idx] = int(j + 1)
        a_C[idx] = float(C[i, j])

    glp_load_matrix(lp, elements_count, i_C, j_C, a_C)


def get_primal_solution(lp, cols_count):
    return [glp_ipt_col_prim(lp, i + 1) for i in range(cols_count)]


def get_dual_solution(lp, rows_count):
    return [glp_ipt_row_dual(lp, j + 1) for j in range(rows_count)]

def get_cost(lp):
    return glp_ipt_obj_val(lp)

def delete_problem(lp):
    glp_delete_prob(lp)