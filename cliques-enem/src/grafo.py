class Grafo:
    """
        Inicializa o grafo vazio.
        Utiliza um dicionário (Tabela Hash) para mapear cada vértice aos seus vizinhos.
        Estrutura: {vertice_u: {vizinho_v: peso, vizinho_w: peso}}
        """
    def __init__(self):
        self.adjacencia = {}
        self.num_vertices = 0
        self.num_arestas = 0

    def adicionar_vertice(self, vertice):
        #adiciona um novo vértice ao grafo, se ele ainda não existir.
        if vertice not in self.adjacencia:
            self.adjacencia[vertice] = {}
            self.num_vertices += 1

    def adicionar_aresta(self, u, v, peso=1):
        #adiciona um novo vértice ao grafo, se ele ainda não existir.
        self.adicionar_vertice(u)
        self.adicionar_vertice(v) # Garante que ambos os vértices existem no grafo
        #como é um grafo não-direcionado, a conexão vai para os dois lados.
        #se a conexão já existe, apenas incrementamos o peso.
        if v in self.adjacencia[u]:
            self.adjacencia[u][v] += peso
            self.adjacencia[v][u] += peso
        else:
            #se não existe, criamos a conexão com o peso inicial.
            self.adjacencia[u][v] = peso
            self.adjacencia[v][u] = peso
            self.num_arestas += 1

    def obter_vizinhos(self, vertice):
        #retorna uma lista com os vizinhos de um vértice.
        if vertice in self.adjacencia:
            return list(self.adjacencia[vertice].keys())
        return []
    
    def obter_peso_aresta(self, u, v):
        #retorna o peso da aresta entre u e v. Se não existir, retorna 0.
        if u in self.adjacencia and v in self.adjacencia[u]:
            return self.adjacencia[u][v]
        return 0
    
    def imprimir_resumo(self):
        print(f"O grafo foi criado com {self.num_vertices} vértices e {self.num_arestas} arestas.")

    def obter_todos_vertices(self):
        #retorna uma lista com todos os vértices (chaves) do grafo.
        return list(self.adjacencia.keys())