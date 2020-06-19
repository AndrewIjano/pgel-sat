import time
import numpy as np
import pandas as pd
import pgel_sat
import argparse


def test_pgel_satisfatibility(axioms_count, concepts_count, prob_axioms_count, test_count=100, axioms_per_prob_restriction=2, prob_restrictions_count=10):
    def random_knowledge_bases():
        for _ in range(test_count):
            yield pgel_sat.ProbabilisticKnowledgeBase.random(
                concepts_count, axioms_count, prob_axioms_count, axioms_per_prob_restriction, prob_restrictions_count)

    sat_and_time_results = np.empty((test_count, 2))
    for idx, kb in enumerate(random_knowledge_bases()):
        sat, time = pgel_sat_is_satisfiable(kb)
        sat_and_time_results[idx, 0] = sat
        sat_and_time_results[idx, 1] = time

    return np.mean(sat_and_time_results, axis=0)


def track_time(function):
    def wrap(*args, **kwargs):
        start = time.time()
        result = function(*args, **kwargs)
        end = time.time()
        return result, end - start
    return wrap


@track_time
def pgel_sat_is_satisfiable(knowledge_base):
    return pgel_sat.is_satisfiable(knowledge_base)


def get_datas_by_cols(datas):
    datas_by_cols = [[] for _ in datas[0]]
    for data in datas:
        for idx, item in enumerate(data):
            datas_by_cols[idx] += [item]
    return datas_by_cols


@track_time
def run_experiment(*args, **kwargs):
    sat_mean, time_mean = test_pgel_satisfatibility(*args, **kwargs)
    concepts_count, axioms_count, prob_axioms_count = args

    return (concepts_count,
            axioms_count / concepts_count,
            prob_axioms_count,
            sat_mean,
            time_mean)


def run_experiments(axioms_range, *args, **kwargs):
    data_set = []
    for axioms_count in axioms_range:
        print('axioms:', axioms_count, end=' ')
        experiment = (axioms_count, *args)
        data, exec_time = run_experiment(*experiment, **kwargs)
        data_set += [data]
        print(exec_time)
    return data_set


def create_data_frame(data_set):
    return pd.DataFrame(
        data=data_set,
        columns=[
            'Concepts count',
            'Axioms count',
            'Probability axioms count',
            'SAT proportion',
            'Time'])


def init_argparse():
    parser = argparse.ArgumentParser(
        usage='%(prog)s [OPTION]',
        description='Run experiments for PGEL-SAT algorithm.'
    )

    parser.add_argument('-m', '--axioms-range-min', nargs='?',
                        default=1, type=int, help='minimum number of axioms tested')

    parser.add_argument('-M', '--axioms-range-max', nargs='?',
                        default=200, type=int, help='maximum number of axioms tested')

    parser.add_argument('-s', '--axioms-range-step', nargs='?',
                        default=1, type=int, help='step between each number of axioms tested in the range')

    parser.add_argument('-n', '--concepts-count', nargs='?',
                        default=60, type=int, help='number of concepts tested')

    parser.add_argument('-p', '--prob-axioms-count', nargs='?', default=10,
                        type=int, help='number of probabilistic axioms tested')

    parser.add_argument('-r', '--axioms-per-prob-restriction', nargs='?',
                        default=2, type=int, help='number of axioms per restriction in pbox')

    parser.add_argument('-k', '--prob-restrictions-count', nargs='?',
                        default=10, type=int, help='number of linear restrictions in pbox')

    parser.add_argument('-t', '--test-count', nargs='?', default=100,
                        type=int, help='number of tests for each axiom number')
    return parser


if __name__ == '__main__':
    parser = init_argparse()
    args = parser.parse_args()

    axioms_range = range(args.axioms_range_min,
                         args.axioms_range_max, args.axioms_range_step)

    data_set = run_experiments(
        axioms_range,
        args.concepts_count,
        args.prob_axioms_count,
        test_count=args.test_count,
        axioms_per_prob_restriction=args.axioms_per_prob_restriction,
        prob_restrictions_count=args.prob_restrictions_count
    )

    df = create_data_frame(data_set)
    df.to_csv('data/experiments/m{}-M{}-s{}-n{}-p{}-r{}-k{}-t{}.csv'.format(*
                                                                            (vars(args).values())), index=False)
