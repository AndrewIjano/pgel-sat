import matplotlib.pyplot as plt
import pandas as pd
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python3 plot.py <filename.csv>')
    else:
        dataset = sys.argv[1]
        df = pd.read_csv(dataset)
        print(df)
        gp = df.groupby(['Concepts count', 'Axioms count'])
        axioms_counts = [j for i, j in gp.groups.keys()]

        means = gp.mean()
        stdevs = gp.std()

        # plt.rcParams.update({'font.size': 16})
        fig, ax1 = plt.subplots()
        ax1.set_xlabel('m/n')
        ax1.set_title('PGEL-SAT: SAT proportion and time')

        sats_mean = means.get('SAT proportion').values
        sats_stdev = stdevs.get('SAT proportion').values

        ax1.set_ylabel('%PGEL-SAT', color='b')
        ax1.plot(axioms_counts, sats_mean, color='b')
        ax1.fill_between(axioms_counts,
                         sats_mean - sats_stdev / 2,
                         sats_mean + sats_stdev / 2,
                         alpha=0.2, color='b')

        ax2 = ax1.twinx()

        times_mean = means.get('Time').values
        times_stdev = stdevs.get('Time').values

        ax2.set_ylabel('time (s)', color='r')
        ax2.plot(axioms_counts, times_mean, color='r', ls='--')
        ax2.fill_between(axioms_counts,
                         times_mean - times_stdev / 2,
                         times_mean + times_stdev / 2,
                         alpha=0.2, color='r')

        fig.tight_layout()
        plt.show()
