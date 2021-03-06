from pgel_sat import ProbabilisticKnowledgeBase, solve
from pgel_sat import gel
import pytest


@pytest.fixture()
def empty_kb():
    return ProbabilisticKnowledgeBase('bot', 'top')


def test_kb_far_existential_concept_is_unsatisfiable(empty_kb):
    kb = empty_kb

    kb.add_concept(gel.IndividualConcept('a'))
    kb.add_concept(gel.IndividualConcept('b'))
    kb.add_concept(gel.Concept('B'))
    kb.add_role(gel.Role('r'))

    kb.add_axiom('a', 'b', 'r')
    kb.add_axiom('b', 'B', kb.is_a)

    rB = gel.ExistentialConcept('r', 'B')
    kb.add_concept(rB)
    kb.add_axiom(rB, kb.bot, kb.is_a)

    result = solve(kb)
    assert not result['satisfiable']


def test_example8_is_correct():
    goal_is_satisfiable = True
    goal_lp_solution_x = [
        2.971849718984097e-10,
        2.611870272454962e-10,
        2.7347816755261047e-10,
        4.2675808097907373e-10,
        5.715521528916973e-10,
        9.996262660145507e-10,
        0.2500000002875222,
        0.2999999999836768,
        0.6999999996742742,
        0.2500000001132499,
        0.6999999995237088,
        0.04999999985506553]
    goal_lp_solution_y = [7.143976405699169e-09, -5.589433348852922e-09,
                          2.0697207378104556e-09, -5.9652571468327445e-09,
                          2.0424164559293503e-09, -2.148781755390826e-09]
    goal_lp_solution_cost = 2.829786666581838e-09

    kb = ProbabilisticKnowledgeBase.from_file('./data/example.owl')
    result = solve(kb)
    assert result['satisfiable'] == goal_is_satisfiable
    assert result['lp'].x == goal_lp_solution_x
    assert result['lp'].y == goal_lp_solution_y
    assert result['lp'].cost == goal_lp_solution_cost
