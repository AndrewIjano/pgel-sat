from probabilistic_knowledge_base import ProbabilisticKnowledgeBase
import pgel_sat
import matplotlib.pyplot as plt
import statistics as stat
import time
import matplotlib.colors as mc
import colorsys


def test_pgel_satisfatibility(
        concepts_count, axioms_count, test_count=100, prob_axioms_count=0):
    def random_knowledge_bases():
        for _ in range(test_count):
            yield ProbabilisticKnowledgeBase.random(
                concepts_count, axioms_count, prob_axioms_count)

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
    def adjust_lightness(color, amount=0.5):
        c = color if color not in mc.cnames.keys() else mc.cnames[color]
        c = colorsys.rgb_to_hls(*mc.to_rgb(c))
        return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])

    def plot_subgraph(ax, data, label, color, light=1):
        ax.set_ylabel(label, color=color)
        ax.plot(data, color=adjust_lightness(color, light))
        ax.tick_params(axis='y', labelcolor=color)

    fig, ax1 = plt.subplots()

    ax1.set_xlabel('number of axioms')

    light = 0.2
    light_factor = 2 / len(satisfatibility_proportions)
    for props in satisfatibility_proportions:
        plot_subgraph(
            ax1,
            props,
            'satisfatibility proportion',
            'tab:red', light=light)
        light += light_factor

    ax2 = ax1.twinx()

    light = 0.2
    for times in mean_elapsed_times:
        plot_subgraph(ax2, times, 'time (s)', 'tab:blue', light=light)
        light += light_factor

    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    concepts_count = 10
    # axioms_counts = [10, 20, 30, 40, 50]
    axioms_counts = range(1, 50, 2)
    prob_axioms_counts = range(0, 21, 2)

    all_satisfatibility_proportions = []
    all_mean_elapsed_times = []
    for prob_axioms_count in prob_axioms_counts:
        satisfatibility_proportions, mean_elapsed_times = zip(
            *
            [
                test_pgel_satisfatibility(
                    concepts_count, axioms_count,
                    prob_axioms_count=prob_axioms_count)
                for axioms_count in axioms_counts])
        all_satisfatibility_proportions += [satisfatibility_proportions]
        all_mean_elapsed_times += [mean_elapsed_times]
    plot_graph(all_satisfatibility_proportions, all_mean_elapsed_times)
