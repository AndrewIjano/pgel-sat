from probabilistic_knowledge_base import ProbabilisticKnowledgeBase
import pgel_sat
import matplotlib.pyplot as plt
import time
import matplotlib.colors as mc
import colorsys
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


def adjust_lightness(color, amount=0.5):
    c = color if color not in mc.cnames.keys() else mc.cnames[color]
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])


def plot_subgraph(ax, data, label, color, light=1):
    ax.set_ylabel(label, color=color)
    ax.plot(data, color=adjust_lightness(color, light))
    # ax.tick_params(axis='y', labelcolor=color)


def multiplot_subgraph(ax, datas, label, color):
    light = 0.2
    light_factor = 2 / len(datas)
    for data in datas:
        plot_subgraph(ax, data, label, color, light=light)
        light += light_factor


def multiplot_graph(datas, label, color='tab:red'):
    fig, ax = plt.subplots()
    plot_subgraph(ax, datas, label, color)
    fig.tight_layout()
    plt.show()


def multiplot_graphs(satisfatibility_proportions, mean_elapsed_times):
    fig, ax1 = plt.subplots()

    ax1.set_xlabel('number of axioms')
    multiplot_subgraph(
        ax1,
        satisfatibility_proportions,
        'satisfatibility proportion',
        'tab:red')

    ax2 = ax1.twinx()
    multiplot_subgraph(
        ax2,
        mean_elapsed_times,
        'time (s)',
        'tab:blue')

    fig.tight_layout()
    plt.show()


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

    fig, ax1 = plt.subplots()
    ax1.set_xlabel('number of axioms')
    ax1.set_title('PGEL-SAT: SAT proportion and time')

    axioms_counts = np.array(axioms_counts)
    sats_mean = sats_and_times_mean_prob[:, 0]
    sats_stdev = sats_and_times_stdev_prob[:, 0]

    ax1.set_ylabel('SAT proportion', color='b')
    ax1.plot(axioms_counts, sats_mean, color='b')
    ax1.fill_between(axioms_counts,
                     sats_mean - sats_stdev / 2,
                     sats_mean + sats_stdev / 2,
                     alpha=0.2, color='b')

    ax2 = ax1.twinx()

    times_mean = sats_and_times_mean_prob[:, 1]
    times_stdev = sats_and_times_stdev_prob[:, 1]

    ax2.set_ylabel('time (s)', color='r')
    ax2.plot(axioms_counts, times_mean, color='r')
    ax2.fill_between(axioms_counts,
                     times_mean - times_stdev / 2,
                     times_mean + times_stdev / 2,
                     alpha=0.2, color='r')

    fig.tight_layout()
    plt.show()

    plt.xlabel('number of axioms')
    plt.title('PGEL-SAT: time * (1 - SAT proportion)')
    sat_time_mean = sats_and_times_mean_prob[:, 2]
    sat_time_stdev = sats_and_times_stdev_prob[:, 2]

    plt.ylabel('time * (1 - SAT proportion)', color='b')
    plt.plot(axioms_counts, sat_time_mean, color='b')
    plt.fill_between(axioms_counts,
                     sat_time_mean - sat_time_stdev / 2,
                     sat_time_mean + sat_time_stdev / 2,
                     alpha=0.2, color='b')
    plt.show()

    df = pd.DataFrame(
        data=data_set,
        columns=[
            'Concepts count',
            'Axioms count',
            'Probability axioms count',
            'SAT proportion',
            'Time'])

    df.to_csv('data.csv', index=False)
