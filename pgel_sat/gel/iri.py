def clear(iri):
    if '#' not in str(iri):
        return str(iri)
    return ''.join(iri.split('#')[1:])