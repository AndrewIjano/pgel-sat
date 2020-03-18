from probabilistic_knowledge_base import ProbabilisticKnowledgeBase
import pgel_sat
import matplotlib.pyplot as plt
import statistics as stat
import time


def test_pgel_satisfatibility(concepts_count, axioms_count, test_count=1000):
    def random_knowledge_bases():
        for _ in range(test_count):
            yield ProbabilisticKnowledgeBase.random(
                concepts_count, axioms_count)

    satisfatibility_results, elapsed_times = zip(*[
        pgel_sat_is_satisfatible(kb) for kb in random_knowledge_bases()
    ])

    return stat.mean(satisfatibility_results), stat.mean(elapsed_times)


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


def plot_graph(satisfatibility_proportions, mean_elapsed_times):
    def plot_subgraph(ax, data, label, color):
        ax.set_ylabel(label, color=color)
        ax.plot(data, color=color)
        ax.tick_params(axis='y', labelcolor=color)

    fig, ax1 = plt.subplots()

    ax1.set_xlabel('number of axioms')

    plot_subgraph(
        ax1,
        satisfatibility_proportions,
        'satisfatibility proportion',
        'tab:red')

    plot_subgraph(ax1.twinx(), mean_elapsed_times, 'time (s)', 'tab:blue')

    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    concepts_count = 10
    max_axioms_count = 50

    satisfatibility_proportions, mean_elapsed_times = zip(*[
        test_pgel_satisfatibility(concepts_count, axioms_count)
        for axioms_count in range(max_axioms_count)
    ])

    plot_graph(satisfatibility_proportions, mean_elapsed_times)
