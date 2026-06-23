import json

class Grafo:
    """
    Utiliza um dicionário (Tabela Hash) para mapear cada vértice aos seus vizinhos.
    Estrutura: {vertice_u: {vizinho_v: peso, vizinho_w: peso}}
    """
    def __init__(self, vertices=None):
        self.adjacencia = {}
        self.num_vertices = 0
        self.num_arestas = 0
        
        if vertices:
            for v in vertices:
                self.adicionar_vertice(v)

    @property
    def adj(self):
        """
        Truque de Compatibilidade: Permite que arquivos como cliques.py 
        acessem grafo.adj sem quebrar o seu código original.
        """
        return self.adjacencia

    def adicionar_vertice(self, vertice):
        if vertice not in self.adjacencia:
            self.adjacencia[vertice] = {}
            self.num_vertices += 1

    def adicionar_aresta(self, u, v, peso=1):
        if u == v: # Evita auto-arestas na mesma frase
            return
            
        self.adicionar_vertice(u)
        self.adicionar_vertice(v) 
        
        if v in self.adjacencia[u]:
            self.adjacencia[u][v] += peso
            self.adjacencia[v][u] += peso
        else:
            self.adjacencia[u][v] = peso
            self.adjacencia[v][u] = peso
            self.num_arestas += 1

    def definir_aresta_peso_exato(self, u, v, peso):
        self.adicionar_vertice(u)
        self.adicionar_vertice(v)
        if v not in self.adjacencia[u]:
            self.num_arestas += 1
        self.adjacencia[u][v] = peso
        self.adjacencia[v][u] = peso

    def obter_vizinhos(self, vertice):
        if vertice in self.adjacencia:
            return list(self.adjacencia[vertice].keys())
        return []
    
    def obter_peso_aresta(self, u, v):
        if u in self.adjacencia and v in self.adjacencia[u]:
            return self.adjacencia[u][v]
        return 0
    
    def obter_todos_vertices(self):
        return list(self.adjacencia.keys())

    def imprimir_resumo(self):
        print(f"O grafo foi criado com {self.num_vertices} vértices e {self.num_arestas} arestas.")

    def add_coocorrencia(self, u, v, peso=1):
        self.adicionar_aresta(u, v, peso)

    def peso(self, u, v):
        return self.obter_peso_aresta(u, v)
    
    def adjacentes(self, u):
        return dict(self.adjacencia.get(u, {}))
    
    def grau(self, u):
        return len(self.adjacencia.get(u, {}))
    
    def nomes_vizinhos(self, u):
        return set(self.adjacencia.get(u, {}))
    
    def tem_aresta(self, u, v):
        return v in self.adjacencia.get(u, {})
    
    def listar_vertices(self):
        return set(self.adjacencia.keys())

    def listar_arestas(self):
        arestas = []
        for u in self.adjacencia:
            for v, peso in self.adjacencia[u].items():
                if u < v: # Evita duplicatas (u-v e v-u)
                    arestas.append((u, v, peso))
        return arestas

# para que arquivos antigos não quebrem ao procurar pela classe Graph
Graph = Grafo

def construir_grafo_de_coocorrencia(corpus):
    grafo = Grafo()
    for redacao in corpus:
        for sentenca in redacao["sentencas"]:
            for i in range(len(sentenca)):
                for j in range(i+1, len(sentenca)):
                    grafo.adicionar_aresta(sentenca[i], sentenca[j], 1)
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
    return [p for _, _, p in grafo.listar_arestas()]

def definir_aresta(grafo, u, v, peso):
    grafo.definir_aresta_peso_exato(u, v, peso)

def poda_peso_absoluto(grafo, min_peso=2):
    novo_grafo = Grafo()
    for u, v, peso in grafo.listar_arestas():
        if peso >= min_peso:
            novo_grafo.definir_aresta_peso_exato(u, v, peso)
    return novo_grafo

def poda_peso_relativo(grafo, fator_media=0.4, fator_max=0.12):
    pesos = estatisticas_pesos(grafo)
    if not pesos:
        return Grafo()
    
    media = sum(pesos) / len(pesos)
    max_peso = max(pesos)
    limiar = max(fator_media * media, fator_max * max_peso)

    novo = Grafo()
    for u, v, peso in grafo.listar_arestas():
        if peso >= limiar:
            novo.definir_aresta_peso_exato(u, v, peso)
    return novo

def poda_pontes(grafo):
    from bfs import bfs
    
    remover = set()
    for u, v, _ in grafo.listar_arestas():
        if not bfs(grafo, u, v, aresta_bloqueada=(u, v)):
            remover.add((u, v))

    novo = Grafo()
    for u, v, peso in grafo.listar_arestas():
        if (u, v) not in remover:
            novo.definir_aresta_peso_exato(u, v, peso)
    return novo

def aplicar_podas(grafo, min_peso=2, fator_media=0.4, fator_max=0.12, usar_pontes=True):
    log = []

    def registrar(etapa, g):
        stats = estatisticas_grafo(g)
        log.append({"etapa": etapa, **stats})
        print(f"[{etapa}] vértices={stats['vertices']} arestas={stats['arestas']}")
        return g

    g = registrar("bruto", grafo)
    g = registrar("poda_absoluta", poda_peso_absoluto(g, min_peso))
    g = registrar("poda_relativa", poda_peso_relativo(g, fator_media, fator_max))
    if usar_pontes:
        g = registrar("poda_pontes", poda_pontes(g))
    return g, log