import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import argparse

SMOOTHING_FACTOR = 5

COLOR_1 = 'navy'
COLOR_2 = 'firebrick'

TITLE = 'PGEL-SAT: SAT proportion and time'
X_LABEL = '$m$/$n$'
Y_LABEL_LEFT = '\%PGEL-SAT'
Y_LABEL_RIGHT = 'time (s)'

DF_SAT_MEAN_LABEL = 'SAT proportion mean'
DF_SAT_STD_LABEL = 'SAT proportion std'

DF_TIME_MEAN_LABEL = 'Time mean'
DF_TIME_STD_LABEL = 'Time std'

plt.rcParams.update({
    'text.usetex': True,
    'text.latex.preamble': '''  \\usepackage{libertine} 
                                \\usepackage[libertine]{newtxmath} 
                                \\usepackage[T1]{fontenc}
                            '''
})


def main():
    parser = init_argparse()
    args = parser.parse_args()

    experiment_path = args.experiment[0]

    axioms_counts, sats, times = get_data_from_experiment(experiment_path)
    ax1, ax2 = init_plot(args)

    sats_mean, _ = sats
    plot_curve(axioms_counts, sats_mean, args, ax1, COLOR_1, '-')

    times_mean, _ = times
    plot_curve(axioms_counts, times_mean, args, ax2, COLOR_2, '--')

    if not args.no_objective_curves:
        plot_logit_fit(axioms_counts, sats_mean, ax1)

    filename = extract_filename(experiment_path)
    plt.savefig(f'data/plots/{filename}.png', bbox_inches='tight', dpi=300)

    if args.show:
        plt.show()

    plt.close()


def init_argparse():
    parser = argparse.ArgumentParser(
        usage='%(prog)s [options] experiment',
        description='Plot experiment for PGEL-SAT algorithm.'
    )

    parser.add_argument('experiment', nargs=1, type=str,
                        help='path of the CSV file of the experiment')

    parser.add_argument('-w', '--moving-average-size', nargs='?',
                        default=5, type=int, help='size of the moving average smoothing')

    parser.add_argument('-p', '--prob-axioms-count', nargs='?', default=10,
                        type=int, help='number of probabilistic axioms tested')

    parser.add_argument('-f', '--font-size', nargs='?',
                        default=12, type=int, help='font size for labels')

    parser.add_argument('--no-title', action='store_true',
                        help='remove the title')

    parser.add_argument('--no-objective-curves', action='store_true',
                        help='remove the objecive curves from the plot')

    parser.add_argument('--show', action='store_true', help='show the plot')
    return parser


def get_data_from_experiment(experiment_path):
    df = pd.read_csv(experiment_path)
    gp = df.groupby(['Concepts count', 'Axioms count'])
    axioms_counts = [j for i, j in gp.groups.keys()]
    means = gp.mean()

    def get_vals(label): return means.get(label).values

    sats = map(get_vals, [DF_SAT_MEAN_LABEL, DF_SAT_STD_LABEL])
    times = map(get_vals, [DF_TIME_MEAN_LABEL, DF_TIME_STD_LABEL])

    return axioms_counts, sats, times


def init_plot(args):
    plt.rcParams.update({'font.size': args.font_size})

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.set_xlabel(X_LABEL)
    if not args.no_title:
        ax1.set_title(f'{TITLE}')
    ax1.set_ylabel(Y_LABEL_LEFT, color=COLOR_1)
    ax2.set_ylabel(Y_LABEL_RIGHT, color=COLOR_2)

    fig.tight_layout()
    return ax1, ax2


def running_average(data_list, size):
    window = np.ones(size)/size

    def smooth_data(data):
        return np.convolve(data, window, mode='valid')

    return list(map(smooth_data, data_list))


def plot_curve(axioms_counts, values_mean, args, ax, color, ls):
    axioms_counts, values_mean = running_average(
        [axioms_counts, values_mean], args.moving_average_size)
    ax.plot(axioms_counts, values_mean, color=color, ls=ls)


def plot_logit_fit(axioms_counts, sats_mean, ax1):
    def logit_fn(x, k, x0, A, off):
        return A / (1 + np.exp(k * (x - x0))) + off

    popt, _ = curve_fit(logit_fn, axioms_counts, sats_mean)
    logit_vals = logit_fn(axioms_counts, *popt)
    ax1.plot(axioms_counts, logit_vals, color=COLOR_1, ls=':')


def plot_linear_fit(axioms_counts, times_mean, ax2):
    coef = np.polyfit(axioms_counts, times_mean, 1)
    poly1d_fn = np.poly1d(coef)
    ax2.plot(axioms_counts, poly1d_fn(axioms_counts), color=COLOR_2, ls=':')


def extract_filename(path):
    return path.split('/')[-1].split('.')[0]


if __name__ == '__main__':
    main()
