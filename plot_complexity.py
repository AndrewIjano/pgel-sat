import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import argparse
from sklearn import linear_model
import math

SMOOTHING_FACTOR = 5

COLOR_1 = 'navy'
COLOR_2 = 'firebrick'
COLOR_3 = 'tab:green'

TITLE = 'PGEL-SAT'
X_LABEL = 'number of uncertain axioms'
Y_LABEL_RIGHT = 'number of iterations'

Y_LABEL_LEFT = 'PGEL-SAT time (s)'

DF_TIME_MEAN_LABEL = 'time_mean'
DF_TIME_STD_LABEL = 'time_std'

DF_ITERS_MEAN_LABEL = 'iters_mean'
DF_ITERS_TIME_MEAN_LABEL = 'iters_time_mean'

# NEED LATEX FONT PACKAGES TO WORK PROPERLY
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
    data = get_data_from_experiment(experiment_path)

    if not args.complexity_2:
        complexity_1_plot(data, args, experiment_path)
    else:
        complexity_2_plot(data, args, experiment_path)


def complexity_1_plot(data, args, experiment_path):
    for idx, values in enumerate(data):
        (key, counts, times_mean, iters_mean, iters_time_mean) = values
        key = [
            'number of axioms',
            'number of concepts',
            'number of uncertain axioms'
        ][idx]
        axes = init_subplots(args, idx, key)
        plot_curve(counts, times_mean*1000, args, axes[0, 0], COLOR_1)
        plot_curve(counts, iters_time_mean*1000, args, axes[0, 1], COLOR_3)
        plot_curve(counts, iters_mean, args, axes[1, 0], COLOR_2)

        filename = extract_filename(experiment_path)
        plt.savefig(f'data/plots/complexity-1/{filename}-({idx}).png',
                    bbox_inches='tight', dpi=300)

        if args.show:
            plt.show()

        plt.close()


def complexity_2_plot(data, args, experiment_path):
    ax1 = init_plot(args)
    (key, counts, times_mean, iters_mean, iters_time_mean) = data[2]

    plot_curve(counts, times_mean, args, plt, COLOR_3)
    plot_polynomial_fit(counts, times_mean, ax1, COLOR_2)
    plot_exponential_fit(counts, times_mean, ax1, COLOR_1)
    # -----

    ax1.legend([
        'PGEL-SAT time',
        'polynomial approximation',
        'exponential approximation'],
        loc='upper left')

    filename = extract_filename(experiment_path)
    plt.savefig(
        f'data/plots/complexity-2/{filename}.png',
        bbox_inches='tight',
        dpi=300)

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

    parser.add_argument('--complexity-2', action='store_true',
                        help='run the complexity 2 plot')

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

    param_groups = df.groupby(['moving_param'])
    param_dfs = ((gp, param_groups.get_group(gp))
                 for gp in param_groups.groups)

    data = []
    for param_key, param_df in param_dfs:
        gp = param_df.groupby([param_key])
        param_counts = [j for j in gp.groups.keys()]
        means = gp.mean()

        def get_vals(label): return means.get(label).values

        vals = map(get_vals, [DF_TIME_MEAN_LABEL,
                              DF_ITERS_MEAN_LABEL, DF_ITERS_TIME_MEAN_LABEL])

        data += [(param_key, np.array(param_counts), *vals)]

    return data


def init_subplots(args, idx, key):
    plt.rcParams.update({'font.size': args.font_size})

    fig, axes = plt.subplots(2, 2)

    axes[0, 0].set_xlabel(key)
    axes[0, 0].set_ylabel('PGEL-SAT time (ms)')

    axes[0, 1].set_xlabel(key)
    axes[0, 1].set_ylabel('avg. iteration time (ms)')

    axes[1, 0].set_xlabel(key)
    axes[1, 0].set_ylabel('avg. number of iterations')

    axes[-1, -1].axis('off')
    fig.tight_layout()

    return axes


def init_plot(args):
    plt.rcParams.update({'font.size': args.font_size})

    fig, ax1 = plt.subplots()

    ax1.set_xlabel(X_LABEL)
    ax1.set_ylabel(Y_LABEL_LEFT)
    fig.tight_layout()

    return ax1


def running_average(data_list, size):
    window = np.ones(size)/size

    def smooth_data(data):
        return np.convolve(data, window, mode='valid')

    return list(map(smooth_data, data_list))


def plot_curve(axioms_counts, values_mean, args, ax, color):
    axioms_counts, values_mean = running_average(
        [axioms_counts, values_mean], args.moving_average_size)
    ax.plot(axioms_counts, values_mean, color=color)


def plot_logit_fit(axioms_counts, sats_mean, ax1):
    def logit_fn(x, k, x0, A, off):
        return A / (1 + np.exp(k * (x - x0))) + off

    popt, _ = curve_fit(logit_fn, axioms_counts, sats_mean)
    logit_vals = logit_fn(axioms_counts, *popt)
    ax1.plot(axioms_counts, logit_vals, color=COLOR_1, ls='--')


def plot_linear_fit(axioms_counts, times_mean, ax2):
    coef = np.polyfit(axioms_counts, times_mean, 1)
    poly1d_fn = np.poly1d(coef)
    ax2.plot(axioms_counts, poly1d_fn(axioms_counts), color=COLOR_2, ls='--')


def plot_polynomial_fit(axioms_counts, times_mean, ax1, color):
    def polynomial_fn(x, a, b, c, d, e, f, g, h):
        return np.polyval([a, b, c, d, e, f, g, h], x)

    popt, _ = curve_fit(polynomial_fn, axioms_counts, times_mean)
    poly_vals = polynomial_fn(axioms_counts, *popt)

    print('POLYNOMIAL FIT')
    print(' + '.join((f'{a}*x^{len(popt) - i - 1}'
                      for i, a in enumerate(popt))))
    print()
    print(' + '.join((f'{a:.10f}*x^{len(popt) - i - 1}'
                      for i, a in enumerate(popt))))
    print()

    ax1.plot(axioms_counts, poly_vals, color=color, ls='--')


def plot_exponential_fit(axioms_counts, times_mean, ax1, color):
    def exponential_fn(x, a, b, d):
        return a*2**(b*x) + d

    popt, _ = curve_fit(exponential_fn, axioms_counts,
                        times_mean, [1, 1/100, -1])
    print('EXPONENTIAL FIT')
    print('{}*2**({}*x) + {}'.format(*popt))
    exp_vals = exponential_fn(axioms_counts, *popt)
    ax1.plot(axioms_counts, exp_vals, color=color, ls=':')


def plot_fit_linear_regression(counts, times_mean, plt):
    logx = np.log(counts)
    logy = np.log(times_mean)

    # log-log fit
    loglogmod = linear_model.LinearRegression()
    x = np.reshape(logx, (len(counts), 1))
    y = logy
    loglogmod.fit(x, y)
    loglogmod_r2 = loglogmod.score(x, y)
    # log fit
    logmod = linear_model.LinearRegression()
    x = np.reshape(counts, (len(counts), 1))
    logmod.fit(x, y)
    logmod_r2 = logmod.score(x, y)

    # polynomial plot
    m = loglogmod.coef_[0]
    c = loglogmod.intercept_
    polynomial = math.exp(c)*np.power(counts, m)
    plt.plot(counts, polynomial,
             label='$y = {:.3f} \\cdot x^{{{:.3f}}}$ ($r^2={:.2f}$)'.format(
                 math.exp(c), m, loglogmod_r2),
             ls='--', color=COLOR_2)
    print(m)
    # exponential plot
    m = logmod.coef_[0]
    c = logmod.intercept_
    print(m)
    exponential = np.exp(counts * m) * math.exp(c)
    plt.plot(counts, exponential,
             label='$y = {:.3f} \\cdot e^{{{:.3f}x}}$ ($r^2={:.2f}$)'.format(
                 math.exp(c), m, logmod_r2),
             ls=':', color=COLOR_3)

    plt.legend(loc='upper left')


def extract_filename(path):
    return path.split('/')[-1].split('.')[0]


if __name__ == '__main__':
    main()
