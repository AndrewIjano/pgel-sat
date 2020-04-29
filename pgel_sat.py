import sys
from pgel_sat import ProbabilisticKnowledgeBase, solve


def str_lp(lp):
    return f'''lp solution:
    x: {lp['x']}
    y: {lp['y']}
    cost: {lp['cost']}'''


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python3 pgel_sat.py <inputfile> [--trace]')
    else:
        filename = sys.argv[1]
        kb = ProbabilisticKnowledgeBase.from_file(filename)

        result = solve(kb)
        print('is satisfiable:', result['satisfiable'])
        print(str_lp(result['lp']))
