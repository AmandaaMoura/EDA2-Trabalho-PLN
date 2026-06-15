"""Estrutura do grafo em lista de adjacência."""


class Graph:
    """Representação simples de um grafo não direcionado."""

    def __init__(self, vertices=None):
        self.vertices = set(vertices or [])
        self.adj = {vertex: set() for vertex in self.vertices}

    def add_edge(self, u, v):
        self.vertices.add(u)
        self.vertices.add(v)
        self.adj.setdefault(u, set()).add(v)
        self.adj.setdefault(v, set()).add(u)
