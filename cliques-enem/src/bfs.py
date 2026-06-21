"""Algoritmo BFS para níveis e componentes conexos."""

from queue_structure import Queue

def bfs(grafo, origem, destino, aresta_bloqueada=None):
    if origem == destino:
        return True
    
    visitados = {origem}
    fila = Queue()
    fila.enqueue(origem)

    while not fila.is_empty():
        atual = fila.dequeue()
        for vizinho in grafo.nomes_vizinhos(atual):
            if vizinho in visitados:
                continue
            if aresta_bloqueada:
                u, v = aresta_bloqueada
                if (atual, vizinho) in {(u, v), (v, u)}:
                    continue
            if vizinho == destino:
                return True
            visitados.add(vizinho)
            fila.enqueue(vizinho)
    return False

if __name__ == "__main__":
    from graph import Graph, definir_aresta
    g = Graph()
    definir_aresta(g, "a", "b", 1)
    definir_aresta(g, "b", "c", 1)
    definir_aresta(g, "a", "c", 1)
    print(bfs(g, "a", "b", ("a", "b")))  # ?
    print(bfs(g, "a", "c", ("a", "b")))  # ?