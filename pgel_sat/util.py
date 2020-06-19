def print_gelpp_max_sat_problem(function):
    def name(kb, obj):
        iri = obj

        if obj == kb.graph.top:
            return '⊤'

        if obj == kb.graph.bot:
            return '⊥'

        if not isinstance(obj, str):
            iri = obj.iri

        if kb.is_existential(obj):
            return f'∃{name(kb, obj.role_iri)}.{name(kb, obj.concept_iri)}'

        if kb.is_individual(obj):
            return '{' + name(kb, obj.iri) + '}'

        if '#' not in str(iri):
            return str(iri)

        return ''.join(iri.split('#')[1:])

    def str_axiom(kb, sub_concept, role, sup_concept):
        s = f'{name(kb, sub_concept)} ⊑ '
        if role != kb.graph.is_a:
            s += f'∃{name(kb, role)}.'
        s += name(kb, sup_concept)
        return s

    def is_real_axiom(kb, sub_concept, sup_arrow):
        is_init = kb.graph.init in [sub_concept, sup_arrow.concept]
        return not(is_init or sup_arrow.is_derivated)

    def str_weight(pbox_id, weights):
        return '     ∞' if pbox_id < 0 else '{:+5.3f}'.format(weights[pbox_id])

    def get_ids_weights_axioms(kb, weights):
        for concept in kb.concepts():
            for sup_arrow in concept.sup_arrows:
                sup_concept = sup_arrow.concept
                role = sup_arrow.role
                pbox_id = sup_arrow.pbox_id
                if is_real_axiom(kb, concept, sup_arrow):
                    a = str_axiom(kb, concept, role, sup_concept)
                    w = str_weight(pbox_id, weights)
                    yield pbox_id, w, a

    def wrapper(kb, weights):
        print()
        print('-' * 18, 'GEL++ MAX-SAT PROBLEM', '-' * 19)
        print('  i \t\t w(Ax_i) \t\t Ax_i')
        print('-' * 60)
        i = 0
        real_id = {}
        for pbox_id, weight, axiom in get_ids_weights_axioms(kb, weights):
            print('{:3}\t\t{}\t\t{}'.format(i, weight, axiom))
            real_id[pbox_id] = i
            i += 1
        result = function(kb, weights)

        print('-' * 60)
        print('HAS SOLUTION:', result['success'])
        if result['success']:
            print('SOLUTION:', [real_id[i]
                                for i in result['prob_axiom_indexes']])

        print('-' * 60)
        print('\n')
        return result
    return wrapper
