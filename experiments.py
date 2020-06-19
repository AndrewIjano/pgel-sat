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

    axioms_range = range(args.axioms_range_min,
                         args.axioms_range_max, args.axioms_range_step)

    data_set = run_experiments(
        axioms_range,
        args.concepts_count,
        args.prob_axioms_count,
        test_count=args.test_count,
        axioms_per_prob_restriction=args.axioms_per_prob_restriction,
        prob_restrictions_count=args.prob_restrictions_count,
        coef_lo=args.coef_lo,
        coef_hi=args.coef_hi,
        b_lo=args.b_lo,
        b_hi=args.b_hi,
        sign_type=args.sign_type,
        roles_count=args.roles_count
    )

    data_frame = create_data_frame(data_set)
    export_data_frame(data_frame, vars(args).values())


def init_argparse():
    parser = argparse.ArgumentParser(
        usage='%(prog)s [options]',
        description='Run experiments for PGEL-SAT algorithm.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-m', '--axioms-range-min', nargs='?',
                        default=11, type=int, help='minimum number of axioms tested')
    
    parser.add_argument('-M', '--axioms-range-max', nargs='?',
                        default=200, type=int, help='maximum number of axioms tested')
    
    parser.add_argument('-s', '--axioms-range-step', nargs='?',
                        default=1, type=int, help='step between each number of axioms tested in the range')
    
    parser.add_argument('-n', '--concepts-count', nargs='?',
                        default=60, type=int, help='number of concepts tested')
    
    parser.add_argument('-p', '--prob-axioms-count', nargs='?', default=10,
                        type=int, help='number of probabilistic axioms tested')
    
    parser.add_argument('-a', '--axioms-per-prob-restriction', nargs='?',
                        default=2, type=int, help='number of axioms per restriction in pbox')
    
    parser.add_argument('-k', '--prob-restrictions-count', nargs='?',
                        default=10, type=int, help='number of linear restrictions in pbox')
    
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


def run_experiments(axioms_range, *args, **kwargs):
    data_set = []
    print_verbose('axioms |  time ')
    print_verbose('----------------')
    for axioms_count in axioms_range:
        print_verbose(end='  {:3}  | '.format(axioms_count))
        experiment = (axioms_count, *args)
        # print('>>>', experiment)
        data, exec_time = run_experiment(*experiment, **kwargs)
        data_set += [data]
        print_verbose('{:.5f}'.format(exec_time))
        print(data)
    return data_set


def track_time(function):
    def wrap(*args, **kwargs):
        start = time.time()
        result = function(*args, **kwargs)
        end = time.time()
        return result, end - start
    return wrap


@track_time
def run_experiment(*args, **kwargs):
    sat_mean, time_mean = test_pgel_satisfatibility(*args, **kwargs)
    axioms_count, concepts_count, prob_axioms_count = args
    return (concepts_count,
            axioms_count / concepts_count,
            prob_axioms_count,
            sat_mean,
            time_mean)


def test_pgel_satisfatibility(axioms_count,
                              concepts_count,
                              prob_axioms_count,
                              *args,
                              test_count,
                              **kwargs):

    def random_knowledge_bases():
        for _ in range(test_count):
            yield pgel_sat.ProbabilisticKnowledgeBase.random(
                concepts_count,
                axioms_count,
                prob_axioms_count,
                *(kwargs.values()))

    sat_and_time_results = np.empty((test_count, 2))
    for idx, kb in enumerate(random_knowledge_bases()):
        sat, time = pgel_sat_is_satisfiable(kb)
        sat_and_time_results[idx, 0] = sat
        sat_and_time_results[idx, 1] = time

    return np.mean(sat_and_time_results, axis=0)


@track_time
def pgel_sat_is_satisfiable(knowledge_base):
    return pgel_sat.is_satisfiable(knowledge_base)


def create_data_frame(data_set):
    return pd.DataFrame(
        data=data_set,
        columns=[
            'Concepts count',
            'Axioms count',
            'Probability axioms count',
            'SAT proportion',
            'Time'])


def export_data_frame(data_frame, arg_values):
    filename = 'data/experiments/'
    filename += 'm{}-M{}-s{}-n{}-p{}-a{}-k{}-t{}-'
    filename += 'cl{}-ch{}-bl{}-bh{}-st{}-r{}'
    filename += '.csv'
    filename = filename.format(*arg_values)
    data_frame.to_csv(filename, index=False)


if __name__ == '__main__':
    main()
