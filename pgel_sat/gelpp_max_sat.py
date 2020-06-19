from copy import deepcopy
from . import util


# @util.print_gelpp_max_sat_problem
def solve(kb, weights):
    weighted_graph = WeightedGraph(kb, weights)
    cut_set = min_cut(weighted_graph)
    if cut_set['is_weight_infinity']:
        return {'success': False}

    return {'success': True,
            'prob_axiom_indexes': cut_set['prob_axiom_indexes']}


def min_cut(weighted_graph):
    s = weighted_graph.init
    t = weighted_graph.bottom

    residual_graph = deepcopy(weighted_graph)

    is_there_augment_path, path = get_augment_path(residual_graph, s, t)
    while is_there_augment_path:
        augment_flow = get_augment_flow(path, residual_graph)
        update_path_weights(path, residual_graph, augment_flow)

        is_there_augment_path, path = get_augment_path(residual_graph, s, t)

    visited = dfs(residual_graph, s)
    cut_set = get_cut_set(weighted_graph, visited)
    return cut_set


def get_augment_path(residual_graph, s, t):
    def get_path(parent, s, t):
        v = t
        while v != s:
            yield (parent[v], v)
            v = parent[v]

    visited = [False] * residual_graph.order
    parent = [0] * residual_graph.order

    queue = [s]
    visited[s] = True
    parent[s] = -1

    while len(queue) > 0:
        u = queue.pop(0)
        for arrow in residual_graph.adj[u]:
            v = arrow.vertex
            if not visited[v] and arrow.weight > 0:
                queue += [v]
                visited[v] = True
                parent[v] = u

    return visited[t], list(get_path(parent, s, t))


def get_augment_flow(path, residual_graph):
    return min(
        (residual_graph.get_weight(u, v) for u, v in path),
        default=residual_graph.infinity
    )


def update_path_weights(path, residual_graph, augment_flow):
    for u, v in path:
        residual_graph.increment_weight(u, v, -augment_flow)
        residual_graph.increment_weight(v, u, +augment_flow)


def dfs(residual_graph, s):
    def _dfs(residual_graph, v, visited):
        visited[v] = True
        for a in residual_graph.adj[v]:
            u = a.vertex
            if not visited[u] and residual_graph.get_weight(v, u) > 0:
                _dfs(residual_graph, u, visited)

    visited = [False] * residual_graph.order
    _dfs(residual_graph, s, visited)
    return visited


def get_cut_set(weighted_graph, visited):
    is_weight_infinity = False
    prob_axiom_indexes = weighted_graph.negative_arrows

    for v, arrows in enumerate(weighted_graph.adj):
        for arrow in arrows:
            if visited[v] and not visited[arrow.vertex]:
                if arrow.prob_axiom_index < 0:
                    is_weight_infinity = True
                prob_axiom_indexes += [arrow.prob_axiom_index]

    return {'is_weight_infinity': is_weight_infinity,
            'prob_axiom_indexes': prob_axiom_indexes}


class WeightedGraph:
    class Arrow():
        def __init__(self, vertex, weight, prob_axiom_index):
            self.vertex = vertex
            self.weight = weight
            self.prob_axiom_index = prob_axiom_index

        def __repr__(self):
            return f'({self.vertex}, {self.weight}, {self.prob_axiom_index})'

    def __init__(self, kb, weights):
        indexes = {j.iri: i for i, j in enumerate(kb.concepts())}

        self.order = len(kb.concepts())
        self.infinity = max(weights) + 1

        self.init = indexes[kb.init()]
        self.bottom = indexes[kb.bottom()]
        self.negative_arrows = []

        self.adj = [[] for _ in range(self.order)]

        for concept in kb.concepts():
            for a in concept.sup_arrows:
                if a.is_derivated:
                    continue

                if a.pbox_id < 0:
                    weight = self.infinity
                else:
                    weight = weights[a.pbox_id]

                if weight < 0:
                    self.negative_arrows += [a.pbox_id]
                    continue

                vertex_1 = indexes[concept.iri]
                vertex_2 = indexes[a.concept.iri]
                self.increment_weight(vertex_1, vertex_2, weight)
                self.add_pbox_id(vertex_1, vertex_2, a.pbox_id)

    def add_arrow(self, vertex_1, vertex_2, weight, pbox_id=-1):
        for arrow in self.adj[vertex_1]:
            if arrow.vertex == vertex_2:
                arrow.weight = weight
                return

        arrow = self.Arrow(vertex_2, weight, pbox_id)
        self.adj[vertex_1] += [arrow]

    def get_weight(self, vertex_1, vertex_2):
        for arrow in self.adj[vertex_1]:
            if arrow.vertex == vertex_2:
                return arrow.weight
        return 0

    def increment_weight(self, vertex_1, vertex_2, increment):
        current_weight = self.get_weight(vertex_1, vertex_2)
        self.add_arrow(vertex_1, vertex_2, current_weight + increment)

    def add_pbox_id(self, vertex_1, vertex_2, pbox_id):
        for arrow in self.adj[vertex_1]:
            if arrow.vertex == vertex_2 and pbox_id != -1:
                arrow.prob_axiom_index = pbox_id
                return
