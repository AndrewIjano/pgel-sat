import numpy as np
import swiglpk as glpk


def solve(c, C, d, signs=None):
    lp = create_minimization_problem()

    rows_count = set_rows(lp, d, signs)
    cols_count = set_objective(lp, c)
    set_coefficients(lp, C)

    optimize(lp)

    x = get_primal_solution(lp, cols_count)
    y = get_dual_solution(lp, rows_count)
    cost = get_cost(lp)

    delete_problem(lp)
    return {'x': x, 'y': y, 'cost': cost}


def create_minimization_problem():
    glpk.glp_term_out(glpk.GLP_OFF)

    lp = glpk.glp_create_prob()
    glpk.glp_set_obj_dir(lp, glpk.GLP_MIN)
    return lp


def set_rows(lp, d, signs):
    rows_count = len(d)
    bnd_types = get_bnd_types(signs, rows_count)
    glpk.glp_add_rows(lp, rows_count)
    for idx, (bnd_type, bnd) in enumerate(zip(bnd_types, d)):
        glpk.glp_set_row_bnds(lp, idx + 1, bnd_type, bnd, bnd)

    return rows_count


def get_bnd_types(signs, rows_count):
    if signs is None:
        [glpk.GLP_FX]*rows_count

    sign_to_type = {
        '==': glpk.GLP_FX,
        '<=': glpk.GLP_UP,
        '>=': glpk.GLP_LO
    }

    return [sign_to_type[sign] for sign in signs]


def set_objective(lp, c):
    cols_count = len(c)
    glpk.glp_add_cols(lp, cols_count)
    for idx, coef in enumerate(c):
        glpk.glp_set_col_bnds(lp, idx + 1, glpk.GLP_LO, 0.0, 0.0)
        glpk.glp_set_obj_coef(lp, idx + 1, coef)

    return cols_count


def set_coefficients(lp, C):
    elements_count = np.count_nonzero(C)
    i_C = glpk.intArray(1 + elements_count)
    j_C = glpk.intArray(1 + elements_count)
    a_C = glpk.doubleArray(1 + elements_count)

    for idx, (i, j) in enumerate(zip(*C.nonzero()), 1):
        i_C[idx] = int(i + 1)
        j_C[idx] = int(j + 1)
        a_C[idx] = float(C[i, j])

    glpk.glp_load_matrix(lp, elements_count, i_C, j_C, a_C)


def optimize(lp):
    glpk.glp_interior(lp, None)


def get_primal_solution(lp, cols_count):
    return [glpk.glp_ipt_col_prim(lp, i + 1) for i in range(cols_count)]


def get_dual_solution(lp, rows_count):
    return [glpk.glp_ipt_row_dual(lp, j + 1) for j in range(rows_count)]


def get_cost(lp):
    return glpk.glp_ipt_obj_val(lp)


def delete_problem(lp):
    glpk.glp_delete_prob(lp)
