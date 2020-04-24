from probabilistic_knowledge_base import ProbabilisticKnowledgeBase
import pgel_sat
import time
import numpy as np
import pandas as pd


def test_pgel_satisfatibility(
        concepts_count, axioms_count, prob_axioms_count=0, test_count=50):
    def random_knowledge_bases():
        for _ in range(test_count):
            yield ProbabilisticKnowledgeBase.random(
                concepts_count, axioms_count, prob_axioms_count)

    sat_and_time_results = np.empty((test_count, 2))
    for idx, kb in enumerate(random_knowledge_bases()):
        sat, time = pgel_sat_is_satisfatible(kb)
        sat_and_time_results[idx, 0] = sat
        sat_and_time_results[idx, 1] = time

    return np.mean(sat_and_time_results, axis=0)


def track_time(function):
    def wrap(*args):
        start = time.time()
        result = function(*args)
        end = time.time()
        return result, end - start
    return wrap


@track_time
def pgel_sat_is_satisfatible(knowledge_base):
    return pgel_sat.is_satisfatible(knowledge_base)


def get_datas_by_cols(datas):
    datas_by_cols = [[] for _ in datas[0]]
    for data in datas:
        for idx, item in enumerate(data):
            datas_by_cols[idx] += [item]
    return datas_by_cols


if __name__ == '__main__':
    concepts_count = 20
    axioms_counts = range(1, 80, 5)
    prob_axioms_counts = range(0, 21, 2)

    sats_and_times_mean_prob = np.empty((len(axioms_counts), 3))
    sats_and_times_stdev_prob = np.empty((len(axioms_counts), 3))

    data_set = []
    for i, axioms_count in enumerate(axioms_counts):
        print('axioms:', i)
        sats_and_times_mean = np.empty((len(prob_axioms_counts), 3))
        for j, prob_axioms_count in enumerate(prob_axioms_counts):
            sat_mean, time_mean = test_pgel_satisfatibility(
                concepts_count, axioms_count, prob_axioms_count)
            sats_and_times_mean[j, :] = (
                sat_mean,
                time_mean,
                time_mean * (1 - sat_mean))

            data_set += [(concepts_count, axioms_count,
                          prob_axioms_count, sat_mean, time_mean)]

        sats_and_times_mean_prob[i, :] = np.mean(sats_and_times_mean, axis=0)
        sats_and_times_stdev_prob[i, :] = np.std(sats_and_times_mean, axis=0)

    df = pd.DataFrame(
        data=data_set,
        columns=[
            'Concepts count',
            'Axioms count',
            'Probability axioms count',
            'SAT proportion',
            'Time'])

    df.to_csv('data.csv', index=False)
