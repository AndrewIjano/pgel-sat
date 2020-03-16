import numpy as np
import math
from copy import deepcopy


def solve(kb, weights):
    weighted_graph = WeightedGraph(kb, weights)
    cut_set = min_cut(weighted_graph)
    if cut_set['is_weight_infinity']:
        return {'success': False}

    return {'success': True, 'prob_axiom_indexes': cut_set['prob_axiom_indexes']}


def min_cut(weighted_graph):
    s = weighted_graph.init
    t = weighted_graph.bottom

    residual_graph = deepcopy(weighted_graph)

    is_there_augment_path, parent = bfs(residual_graph, s, t)
    while is_there_augment_path:
        augment_flow = get_augment_flow(t, s, parent, residual_graph)
        update_path_weights(t, s, parent, residual_graph, augment_flow)

        is_there_augment_path, parent = bfs(residual_graph, s, t)

    visited = dfs(residual_graph, s)
    cut_set = get_cut_set(weighted_graph, visited)
    return cut_set


def bfs(residual_graph, s, t):
    parent = [0] * residual_graph.order
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
                parent[v] = u
                visited[v] = True

    return visited[t], parent


def get_augment_flow(t, s, parent, residual_graph):
    augment_flow = math.inf

    for v in get_path(t, s, parent):
        u = parent[v]
        augment_flow = min(augment_flow, residual_graph.get_weight(u, v))

    return augment_flow


def update_path_weights(t, s, parent, residual_graph, augment_flow):
    for v in get_path(t, s, parent):
        u = parent[v]
        residual_graph.add_arrow(
            u, v, residual_graph.get_weight(u, v) - augment_flow)
        residual_graph.add_arrow(
            v, u, residual_graph.get_weight(v, u) + augment_flow)


def get_path(t, s, parent):
    v = t
    while v != s:
        yield v
        v = parent[v]


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
        self.adj = []
        self.order = len(kb.concepts)
        self.infinity = math.inf

        self.init = kb.init
        self.bottom = kb.bottom
        self.negative_arrows = []

        for _ in range(self.order):
            self.adj += [[]]

        for ci in kb.concept_inclusions:
            if ci.prob_axiom_index >= 0 and weights[ci.prob_axiom_index] >= 0:
                weight = weights[ci.prob_axiom_index]
                prob_axiom_index = ci.prob_axiom_index
            elif weights[ci.prob_axiom_index] < 0:
                self.negative_arrows += [ci.prob_axiom_index]
                continue
            else:
                weight = self.infinity
                prob_axiom_index = -1

            arrow = self.Arrow(ci.super_concept, weight, prob_axiom_index)
            self.adj[ci.sub_concept] += [arrow]

    def add_arrow(self, vertex_1, vertex_2, weight):
        for arrow in self.adj[vertex_1]:
            if arrow.vertex == vertex_2:
                arrow.weight = weight

        arrow = self.Arrow(vertex_2, weight, -1)
        self.adj[vertex_1] += [arrow]

    def get_weight(self, vertex_1, vertex_2):
        for arrow in self.adj[vertex_1]:
            if arrow.vertex == vertex_2:
                return arrow.weight
        return 0
