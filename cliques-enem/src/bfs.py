from fila import Fila

def bfs(grafo):
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

def imprimir_analise_bfs(componentes):
   #imprimir os resultados da análise BFS    
   print(f"Total de componentes conexos: {len(componentes)}")

   #ordena os componentes do maior para o menor
   componentes_ordenados = sorted(componentes, key=len, reverse=True)
   print(f"Tamanho do maior componente (Núcleo Principal): {len(componentes_ordenados[0])} palavras")

   #se houver mais de um componente, mostra como estão fragmentados
   if len(componentes_ordenados) > 1:
        print(f"Tamanho do segundo maior componente: {len(componentes_ordenados[1])} palavras")
       