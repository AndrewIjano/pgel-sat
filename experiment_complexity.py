import time
import numpy as np
import pandas as pd
import pgel_sat
import argparse

IS_VERBOSE = False


def main():
    parser = init_argparse()
    args = parser.parse_args()

    global IS_VERBOSE
    IS_VERBOSE = args.verbose

    step = args.step

    concepts_range = range(args.concepts_range_min,
                           args.concepts_range_max, step)

    axioms_range = range(args.axioms_range_min,
                         args.axioms_range_max, step)

    prob_axioms_range = range(args.prob_axioms_range_min,
                              args.prob_axioms_range_max, step)

    ranges = {
        'concepts_count': concepts_range,
        'axioms_count': axioms_range,
        'prob_axioms_count': prob_axioms_range
    }

    kb_params = {
        'concepts_count': 10,
        'axioms_count': 10,
        'prob_axioms_count': 10,
        'axioms_per_restriction': 1,
        'prob_restrictions_count': 10,
        'coef_lo': args.coef_lo,
        'coef_hi': args.coef_hi,
        'b_lo': args.b_lo,
        'b_hi': args.b_hi,
        'sign_type': args.sign_type,
        'roles_count': args.roles_count
    }

    data_set = run_experiments(
        kb_params,
        ranges,
        args.test_count
    )

    data_frame = create_data_frame(data_set)
    export_data_frame(data_frame, vars(args).values())


def init_argparse():
    parser = argparse.ArgumentParser(
        usage='%(prog)s [options]',
        description='Run experiments for PGEL-SAT algorithm.'
    )

    parser.add_argument('-m', '--axioms-range-min', nargs='?',
                        default=10, type=int, help='minimum number of axioms tested')

    parser.add_argument('-M', '--axioms-range-max', nargs='?',
                        default=200, type=int, help='maximum number of axioms tested')

    parser.add_argument('-s', '--step', nargs='?',
                        default=1, type=int, help='step between each number of parameters tested in the range')

    parser.add_argument('-n', '--concepts-range-min', nargs='?',
                        default=10, type=int, help='minimum number of concepts tested')

    parser.add_argument('-N', '--concepts-range-max', nargs='?',
                        default=200, type=int, help='maximum number of concepts tested')

    parser.add_argument('-p', '--prob-axioms-range-min', nargs='?', default=10,
                        type=int, help='minimum number of probabilistic axioms tested')

    parser.add_argument('-P', '--prob-axioms-range-max', nargs='?', default=200,
                        type=int, help='maximum number of probabilistic axioms tested')

    parser.add_argument('-a', '--axioms-per-prob-restriction', nargs='?',
                        default=2, type=int, help='number of axioms per restriction in pbox')

    parser.add_argument('-k', '--prob-restrictions-range-min', nargs='?',
                        default=1, type=int, help='minimum number of linear restrictions in pbox')

    parser.add_argument('-K', '--prob-restrictions-range-max', nargs='?',
                        default=100, type=int, help='maximum number of linear restrictions in pbox')

    parser.add_argument('-t', '--test-count', nargs='?', default=100,
                        type=int, help='number of tests for each axiom number')

    parser.add_argument('--coef-lo', nargs='?', default=-1,
                        type=int, help='minimum value of coefficients in pbox')

    parser.add_argument('--coef-hi', nargs='?', default=1,
                        type=int, help='maximum value of coefficients in pbox')

    parser.add_argument('--b-lo', nargs='?', default=0,
                        type=int, help='minimum value of the right-hand-side scalar in pbox (b)')

    parser.add_argument('--b-hi', nargs='?', default=2,
                        type=int, help='maximum value of the right-hand-side scalar in pbox (b)')

    parser.add_argument('--sign-type', nargs='?', default='lo', choices=['lo', 'eq', 'hi', 'all'],
                        type=str, help='type of signs used in pbox restrictions')

    parser.add_argument('-r', '--roles-count', nargs='?', default=3,
                        type=int, help='number of roles tested')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='print the progress of the experiments')

    return parser


def print_verbose(*args, **kwargs):
    if IS_VERBOSE:
        print(*args, **kwargs)


def run_experiments(kb_params, ranges, test_count):
    data_set = []

    for param_key, param_range in ranges.items():
        print_verbose(f'|- {param_key:10} -|')

        experiment_params = {**kb_params}
        for param in param_range:
            experiment_params[param_key] = param
            data, exec_time = run_experiment(
                experiment_params, test_count, param_key)
            data_set += [data]
            print_verbose(f'|   {param:3}  {exec_time:.5f}   |')

        print_verbose('-------------\n')

    return data_set


def track_time(function):
    def wrap(*args, **kwargs):
        start = time.time()
        result = function(*args, **kwargs)
        end = time.time()
        return result, end - start

    return wrap


@track_time
def run_experiment(params, test_count, moving_param):
    means, stds = test_pgel_satisfiability(params, test_count)
    (sat_mean, time_mean, iters_mean, iters_time_mean) = means
    (sat_std, time_std, iters_std, iters_time_std) = stds

    return (moving_param,
            params['concepts_count'],
            params['axioms_count'],
            params['prob_axioms_count'],
            time_mean,
            time_std,
            iters_mean,
            iters_time_mean)


def test_pgel_satisfiability(params, test_count):
    def random_knowledge_bases():
        for _ in range(test_count):
            yield pgel_sat.ProbabilisticKnowledgeBase.random(**params)

    results = np.empty((test_count, 4))
    for idx, kb in enumerate(random_knowledge_bases()):
        (sat, iters, iter_times), time = pgel_sat_is_satisfiable(kb)
        results[idx, 0] = sat
        results[idx, 1] = time
        results[idx, 2] = iters
        results[idx, 3] = 0 if iter_times == [] else np.mean(iter_times)

    return np.mean(results, axis=0), np.std(results, axis=0)


@track_time
def pgel_sat_is_satisfiable(knowledge_base):
    result = pgel_sat.solve(knowledge_base)
    return result['satisfiable'], result['iterations'], result['iteration_times']

def create_data_frame(data_set):
    return pd.DataFrame(
        data=data_set,
        columns=[
            'moving_param',
            'concepts_count',
            'axioms_count',
            'prob_axioms_count',
            'time_mean',
            'time_std',
            'iters_mean',
            'iters_time_mean'
        ])


def export_data_frame(data_frame, arg_values):
    filename = 'data/experiments/complexity/'
    filename += 'm{}-M{}-s{}-n{}-N{}-p{}-P{}-a{}-k{}-K{}-t{}-'
    filename += 'cl{}-ch{}-bl{}-bh{}-st{}-r{}'
    filename += '.csv'
    filename = filename.format(*arg_values)
    data_frame.to_csv(filename, index=False)


if __name__ == '__main__':
    main()
