import matplotlib.pyplot as plt
import matplotlib.colors as mc
import colorsys


def adjust_lightness(color, amount=0.5):
    c = color if color not in mc.cnames.keys() else mc.cnames[color]
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])


def plot_subgraph(ax, data, label, color, light=1):
    ax.set_ylabel(label, color=color)
    ax.plot(data, color=adjust_lightness(color, light))


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