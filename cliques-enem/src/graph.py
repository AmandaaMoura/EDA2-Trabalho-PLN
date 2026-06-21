"""Estrutura do grafo em lista de adjacência."""

import json

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

def carregar_corpus(caminho_json):
    with open(caminho_json, "r", encoding="utf-8") as f:
        return json.load(f)

def estatisticas_grafo(grafo):
    arestas = grafo.listar_arestas()
    pesos = [peso for _, _, peso in arestas]
    return {
        "vertices": len(grafo.listar_vertices()),
        "arestas": len(arestas),
        "peso_medio": sum(pesos) / len(pesos) if pesos else 0,
        "peso_max": max(pesos) if pesos else 0,
    }

def estatisticas_pesos(grafo):
    #somente para pesos menores ao do vertice de referencia (usar na pode relativa dos vertices mais fracos)
    return [p for _, _, p in grafo.listar_arestas()]

MIN_PESO_ARESTA = 2

def poda_peso_absoluto(grafo, min_peso=MIN_PESO_ARESTA): #vai selecionar as arestas com peso >=2 em um novo grafo
    novo_grafo = Graph()
    for u, v, peso in grafo.listar_arestas():
        if peso >= min_peso:
            definir_aresta(novo_grafo, u, v, peso)
    return novo_grafo

def definir_aresta(grafo, u, v, peso):  #nao soma os pesos igual ao add_coocorrencia, apenas define o peso, apos selecao anterior(poda)
    grafo.vertices.add(u)
    grafo.vertices.add(v)
    grafo.adj.setdefault(u, {})
    grafo.adj.setdefault(v, {})
    grafo.adj[u][v] = peso
    grafo.adj[v][u] = peso

#podando em relacao ao peso medio e maximo do corpus

FATOR_MEDIA = 0.5
FATOR_MAX = 0.25

def poda_peso_relativo(grafo, fator_media=FATOR_MEDIA, fator_max=FATOR_MAX):
    
    #vai selecionar as arestas com peso >= ao peso medio ou maximo do corpus em um novo grafo
    
    pesos = estatisticas_pesos(grafo)

    if not pesos:
        return Graph()
    media = sum(pesos) / len(pesos)
    max_peso = max(pesos)
    limiar = max(fator_media * media, fator_max * max_peso)

    novo = Graph()
    for u, v, peso in grafo.listar_arestas():
        if peso >= limiar:
            definir_aresta(novo, u, v, peso)
    return novo


corpus = carregar_corpus("data/processed/corpus_nota1000.json")
g = construir_grafo_de_coocorrencia(corpus)

print("ANTES:", estatisticas_grafo(g))
g_podado = poda_peso_absoluto(g, min_peso=2)
print("DEPOIS:", estatisticas_grafo(g_podado))

pesos = estatisticas_pesos(g)
peso_1 = sum(1 for p in pesos if p == 1)
print(f"Arestas com peso 1: {peso_1} de {len(pesos)}")
print("DEPOIS:", estatisticas_grafo(g_podado))
print("RELATIVO:", estatisticas_grafo(poda_peso_relativo(g, fator_media=0.5, fator_max=0.25)))