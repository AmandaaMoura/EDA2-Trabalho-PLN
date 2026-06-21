from fila import Fila
from grafo import Grafo

def componentes_conexos(grafo: Grafo):
    visitados = set()  #conjunto para rastrear os vértices visitados
    componentes = []  #lista para armazenar os componentes conexos

    #pegar todas as palavras do grafo
    todos_vertices = grafo.obter_todos_vertices()

    for vertice_inicial in todos_vertices:
        #se a palavra ainda não foi visitada, inicia uma nova busca
        if vertice_inicial not in visitados:
            componente_atual = []  #lista para armazenar o componente conexo atual
            fila = Fila()

            #marca como visitado e adiciona à fila
            visitados.add(vertice_inicial)
            fila.enfileirar(vertice_inicial)

            #enquanto houver vértices na fila, continua a busca
            while not fila.esta_vazia():
                #o primeiro da fila sai
                vertice_atual = fila.desenfileirar()
                componente_atual.append(vertice_atual)

                #busca os vizinhos do vértice atual
                vizinhos = grafo.obter_vizinhos(vertice_atual)

                for vizinho in vizinhos:
                    #se o vizinho ainda não foi visitado, marca como visitado e adiciona à fila
                    if vizinho not in visitados:
                        visitados.add(vizinho)
                        fila.enfileirar(vizinho)

            #fila esvaziada, terminou de mapear essa janela de palavras
            componentes.append(componente_atual)  

    return componentes

def bfs_niveis(grafo: Grafo, origem):
    #retorna a profundidade

    #busca as palavras que existem no grafo
    todos_vertices = grafo.obter_todos_vertices()
    #se a palavra não estiver no grafo, nterrompe a funcao e retorna vazio
    if origem not in todos_vertices:
        return {}
    
    visitados = set()
    niveis = {}
    fila = Fila()

    #coloca a palavra de origem na fia de processamento
    fila.enfileirar(origem)
    #marca a origem como visitado
    visitados.add(origem)
    niveis[origem] = 0

    #loop roda enquanto houver palavras na fila 
    while not fila.esta_vazia():
        #tira o primeiro da fila e deixa como atual
        atual = fila.desenfileirar()
        #consulta em qual camada ou profundidade esta esse vertice atual
        nivel_atual = niveis[atual]

        #busca todas as palavras conectadas diretamente a "atual"
        vizinhos = grafo.obter_vizinhos(atual)

        #expansao em camada
        #processa vizinhos que nao foram buscados
        for vizinho in vizinhos:
            if vizinho not in visitados:
                #marca como visitado
                visitados.add(vizinho)
                #distancia do vizinho e a distancia da palavra atual +1 salto (aresta)
                niveis[vizinho] = nivel_atual +1
                #verificar quem são os vizinhos dele, proxima camada
                fila.enfileirar(vizinho)

    #retorna com as distancias calculadas
    return niveis
 

from queue_structure import Queue



def imprimir_analise_bfs(componentes):
   #imprimir os resultados da análise BFS    
   print(f"Total de componentes conexos: {len(componentes)}")

   #ordena os componentes do maior para o menor
   componentes_ordenados = sorted(componentes, key=len, reverse=True)
   print(f"Tamanho do maior componente (Núcleo Principal): {len(componentes_ordenados[0])} palavras")

   #se houver mais de um componente, mostra como estão fragmentados
   if len(componentes_ordenados) > 1:
        print(f"Tamanho do segundo maior componente: {len(componentes_ordenados[1])} palavras")
       
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
