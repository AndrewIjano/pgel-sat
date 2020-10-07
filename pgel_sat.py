import sys
from pgel_sat import ProbabilisticKnowledgeBase, solve
import argparse


def str_lp(lp):
    return f'''lp solution:
    x: {lp.x}
    y: {lp.y}
    cost: {lp.cost}'''


def main():
    parser = init_argparse()
    args = parser.parse_args()

    filename = args.file[0]
    kb = ProbabilisticKnowledgeBase.from_file(filename)

    result = solve(kb)
    print('is satisfiable:', result['satisfiable'])
    print(str_lp(result['lp']))


def init_argparse():
    parser = argparse.ArgumentParser(
        description='Computes the Probabilistic SAT algorithm' \
                    'in a Probabilistic Graphic EL knowledge base.'
    )

    parser.add_argument(
        'file', nargs=1, type=str,
        help='path of the OWL file with the Probabilistic Graphic EL ontology')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='prints the problem and solution')
    return parser


if __name__ == '__main__':
    main()
