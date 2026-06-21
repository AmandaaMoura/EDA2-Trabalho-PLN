"""Estrutura do grafo em lista de adjacência."""


class Graph:
    """Grafo não direcionado."""

    def __init__(self, vertices=None):
        self.vertices = set(vertices or [])
        self.adj = {vertex: {} for vertex in self.vertices}

    #adiciona os pesos das arestas entre cada um dos vertices u e v
    def add_coocorrencia(self, u, v, peso=1):
        if u == v:  #se os vertices sao iguais nao tem porque somar peso + 1
            return
        
        self.vertices.add(u)
        self.vertices.add(v)
        self.adj.setdefault(u, {})
        self.adj.setdefault(v, {})

        self.adj[u][v] = self.adj[u].get(v, 0) + peso
        self.adj[v][u] = self.adj[v].get(u, 0) + peso

    def peso(self, u, v):
        return self.adj.get(u, {}).get(v, 0)  #retorna o peso da aresta entre u e v
    
    def adjacentes(self, u):
        return dict(self.adj.get(u, {}))  #retorna o conjunto de adjacentes a u com seus pesos
    
    def grau(self, u):
        return len(self.adj.get(u, {}))  #retorna o grau de u (vertice especifico)
    
    def nomes_vizinhos(self, u):
        return set(self.adj.get(u, {})) #retorna o conjunto de nomes dos vizinhos de u
    
    def tem_aresta(self, u, v):
        return v in self.adj.get(u, {})  #retorna se existe aresta entre u e v  

    def listar_vertices(self):
        return set(self.vertices) #retorna o conjunto de vertices do grafo

    def listar_arestas(self): #retorna a lista de arestas do grafo (para o final da analise)
        arestas = []
        for u in self.adj:
            for v, peso in self.adj[u].items():
                if u < v:
                    arestas.append((u, v, peso))
        return arestas


def construir_grafo_de_coocorrencia(corpus):
    grafo = Graph()
    for redacao in corpus:
        for sentenca in redacao["sentencas"]:
            for i in range(len(sentenca)):
                for j in range(i+1, len(sentenca)):
                    grafo.add_coocorrencia(sentenca[i], sentenca[j], 1)
    return grafo


