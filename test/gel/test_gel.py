import pytest
from pgel_sat import gel


@pytest.fixture
def simple_graph():
    graph = gel.KnowledgeBase('bot', 'top')
    graph.add_concept(gel.Concept('C'))
    graph.add_concept(gel.IndividualConcept('a'))
    graph.add_role(gel.Role('r'))

    graph.add_concept(gel.ExistentialConcept('r', 'C'))
    graph.add_axiom('a', 'C', graph.is_a.iri)
    return graph


@pytest.fixture
def init_bot_graph():
    graph = gel.KnowledgeBase('bot', 'top')
    graph.add_concept(gel.Concept('C'))
    graph.add_concept(gel.IndividualConcept('a'))
    graph.add_role(gel.Role('r'))
    graph.add_axiom('a', 'C', graph.is_a.iri)
    graph.add_axiom('C', 'bot', graph.is_a.iri)
    return graph


@pytest.fixture
def three_concept_graph():
    graph = gel.KnowledgeBase('bot', 'top')
    graph.add_concept(gel.Concept('C'))
    graph.add_concept(gel.Concept('C_prime'))
    graph.add_concept(gel.Concept('D'))
    graph.add_role(gel.Role('i'))
    return graph


@pytest.fixture
def graph_pre_role_inclusion():
    graph = gel.KnowledgeBase('bot', 'top')
    graph.add_concept(gel.Concept('C'))
    graph.add_concept(gel.Concept('D'))

    graph.add_role(gel.Role('i'))
    graph.add_role(gel.Role('j'))
    return graph


@pytest.fixture
def graph_pre_chained_role_inclusion():
    graph = gel.KnowledgeBase('bot', 'top')
    graph.add_concept(gel.Concept('C'))
    graph.add_concept(gel.Concept('D_prime'))
    graph.add_concept(gel.Concept('D'))

    graph.add_role(gel.Role('i'))
    graph.add_role(gel.Role('j'))
    graph.add_role(gel.Role('k'))
    return graph


@pytest.fixture
def graph_complete_rule_5():
    graph = gel.KnowledgeBase('bot', 'top')
    graph.add_concept(gel.Concept('C'))
    graph.add_concept(gel.Concept('D'))
    graph.add_concept(gel.Concept('C1'))
    graph.add_concept(gel.Concept('C2'))
    graph.add_axiom('C', 'C1', graph.is_a)
    graph.add_axiom('C1', 'C2', graph.is_a)

    graph.add_concept(gel.Concept('D1'))
    graph.add_axiom('D', 'D1', graph.is_a)

    graph.add_role(gel.Role('i'))
    graph.add_concept(gel.Concept('D-1'))
    graph.add_axiom('D-1', 'D', 'i')

    graph.add_concept(gel.IndividualConcept('a'))

    graph.add_axiom('C2', 'a', graph.is_a)
    graph.add_axiom('D1', 'a', graph.is_a)
    graph.add_axiom('a', 'C', graph.is_a)
    graph.add_axiom('a', 'D-1', graph.is_a)
    return graph

@pytest.mark.timeout(1)
def test_graph_concepts(simple_graph):
    expected_iris = [
        'init',
        'bot',
        'top',
        'C',
        'a',
        'r.C'
    ]

    expected_concepts = [
        simple_graph.get_concept(iri)
        for iri in expected_iris
    ]

    assert isinstance(simple_graph.concepts, list)
    assert simple_graph.concepts == expected_concepts


@pytest.mark.timeout(1)
def test_graph_individuals(simple_graph):
    expected_iris = [
        'a'
    ]

    expected_individuals = [
        simple_graph.get_concept(iri)
        for iri in expected_iris
    ]

    assert isinstance(simple_graph.individuals, list)
    assert simple_graph.individuals == expected_individuals


@pytest.mark.timeout(1)
def test_graph_roles(simple_graph):
    expected_iris = [
        'is a',
        'r'
    ]

    expected_roles = [
        simple_graph.get_role(iri)
        for iri in expected_iris
    ]

    assert isinstance(simple_graph.roles, list)
    assert simple_graph.roles == expected_roles


@pytest.mark.timeout(1)
def test_graph_link_init(simple_graph):
    init = simple_graph.init
    concept_iris = ['top', 'a', 'C']
    concepts = [
        simple_graph.get_concept(iri)
        for iri in concept_iris
    ]

    assert concepts[0] in init.is_a()
    assert concepts[1] in init.is_a()
    assert concepts[2] not in init.is_a()


@pytest.mark.timeout(1)
def test_graph_link_existential_concept(simple_graph):
    is_axiom_added = simple_graph.add_axiom('r.C', 'C', 'r',
                                            is_immutable=True)
    assert not is_axiom_added


@pytest.mark.timeout(1)
def test_graph_add_axiom():
    graph = gel.KnowledgeBase('bot', 'top')
    graph.add_concept(gel.Concept('C'))
    graph.add_concept(gel.Concept('D'))
    assert graph.add_axiom('C', 'D', graph.is_a)
    assert not graph.add_axiom('C', 'D', graph.is_a)


@pytest.mark.timeout(1)
def test_graph_fix_existential_head_axiom(simple_graph):
    concept_d = gel.Concept('D')
    simple_graph.add_concept(concept_d)
    existential_concept = simple_graph.get_concept('r.C')

    assert existential_concept not in concept_d.is_a()
    simple_graph.add_axiom('D', 'C', 'r')
    assert existential_concept in concept_d.is_a()


@pytest.mark.timeout(1)
def test_graph_add_pbox_axiom():
    graph = gel.KnowledgeBase('bot', 'top')
    assert graph.pbox_axioms == {}

    graph.add_concept(gel.Concept('C'))
    graph.add_concept(gel.Concept('D'))
    graph.add_axiom('C', 'D', graph.is_a, pbox_id=0)

    expected_axiom = (
        graph.get_concept('C'),
        graph.get_concept('D'),
        graph.is_a
    )

    assert graph.pbox_axioms == {0: expected_axiom}


@pytest.mark.timeout(1)
def test_graph_can_handle_multiple_completions():
    graph = gel.KnowledgeBase.random(concepts_count=100,
                                     axioms_count=1000,
                                     uncertain_axioms_count=40,
                                     roles_count=10)
