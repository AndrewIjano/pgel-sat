import pytest
from pgel_sat import gelpp


@pytest.fixture
def concept_with_arrows():
    concept_a = gelpp.Concept('a')
    concept_b = gelpp.Concept('b')
    role = gelpp.Role('r')
    arrow1 = gelpp.Arrow(concept_b, role)
    concept_a.add_arrow(arrow1)

    concept_c = gelpp.Concept('c')
    arrow2 = gelpp.Arrow(concept_c, role)
    concept_a.add_arrow(arrow2)

    return concept_a, [arrow1, arrow2]


def test_concept_arrow_addition(concept_with_arrows):
    concept, arrows = concept_with_arrows
    assert concept.sup_arrows[0] == arrows[0]
    assert concept.sup_arrows[1] == arrows[1]


def test_concept_same_arrow_addition(concept_with_arrows):
    concept, arrows = concept_with_arrows
    concept.add_arrow(arrows[0])
    assert len(concept.sup_arrows) == len(arrows)


def test_concept_has_arrow(concept_with_arrows):
    concept, arrows = concept_with_arrows
    assert concept.has_arrow(arrows[0])


def test_same_values_arrow_equal(concept_with_arrows):
    concept, arrows = concept_with_arrows
    arrow = arrows[0]
    arrow2 = gelpp.Arrow(arrow.concept, arrow.role)
    assert concept.has_arrow(arrow2)
