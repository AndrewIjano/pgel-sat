from pgel_sat.gel import iri


def test_clear_in_real_iri():
    real_iri = 'urn:absolute:example#Disease'
    assert iri.clear(real_iri) == 'Disease'


def test_clear_in_simple_string():
    simple_string = 'Disease'
    assert iri.clear(simple_string) == 'Disease'


def test_clear_in_empty_string():
    empty_string = ''
    assert iri.clear(empty_string) == ''


def test_clear_in_iri_with_duplicated_hashtag():
    double_hashtag = 'urn:absolute:example#Disease#Song'
    assert iri.clear(double_hashtag) == 'DiseaseSong'
