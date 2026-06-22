import os
from graph import Graph, construir_grafo_de_coocorrencia, carregar_corpus, aplicar_podas

MIN_PESO_ARESTA = 2
# mínimo de coocorrência definido para uma aresta ser usada.
# arestas com peso < 2 ocorreram em apenas 1 sentença — evitar.

TAMANHO_MINIMO_CLIQUE = 4
# tamanho mínimo para um clique ser conisderado na nossa analise.
# pares (2) e triângulos (3) são bem comuns.

# filtragem do grafo por peso de aresta

def filtrar_adjacencia(grafo: Graph, min_peso: int = MIN_PESO_ARESTA) -> dict:
# constrói dicionário de adjacência filtrado por peso mínimo.
# estrutura: { palavra: set(vizinhos com peso >= min_peso) }
# Usar sets permite verificar adjacência em O(1) e fazer interseções eficientes durante a DFS.

    adj = {}
    for vertice in grafo.listar_vertices():
        adj[vertice] = {
            viz
            for viz, peso in grafo.adj.get(vertice, {}).items()
            if peso >= min_peso
        }
    return adj


# verificação de clique

def eh_clique(conjunto, adj):
# verifica se um subconjunto S de vértices forma um clique.
# implementação direta do pseudocódigo do slide de aula

    membros = list(conjunto)
    for u in membros:
        for v in membros:
            if u != v:
                if v not in adj.get(u, set()):
                    return False
    return True


# DFS recursivo para expansão de cliques

def _dfs(clique_atual, candidatos, adj, resultado):
    """
    DFS recursivo: tenta expandir clique_atual adicionando vértices de candidatos.

    Para cada vértice v em candidatos (em ordem lexicográfica):
        - Testa se clique_atual U {v} ainda é clique (via eh_clique).
        - Se sim: recursão com o novo clique e candidatos restritos a vizinhos de v
          com índice lexicográfico maior que v (evita reexplorar o mesmo clique).

    Quando nenhum candidato pode expandir o clique, ele é localmente maximal:
    registra na lista resultado.
    """
    algum_extendido = False

    for v in sorted(candidatos):
        novo_clique = clique_atual | {v}

        # verificação pelo algoritmo do slide
        if eh_clique(novo_clique, adj):
            algum_extendido = True
            # restringe candidatos: apenas vértices com índice lex. > v E vizinhos de v
            novos_cands = {c for c in candidatos if c > v} & adj.get(v, set())
            _dfs(novo_clique, novos_cands, adj, resultado)

    # nenhum candidato pôde estender: clique localmente maximal neste ramo
    if not algum_extendido:
        resultado.append(frozenset(clique_atual))


# pós-processamento: remover cliques não-maximais

def filtrar_maximais(cliques):
# remove cliques que são subconjuntos próprios de outro clique na lista.

    resultado = []
    for c in cliques:
        if not any(c < outro for outro in cliques):
            resultado.append(c)
    return resultado


# interface pública

def encontrar_cliques(grafo: Graph,
                      min_peso: int = MIN_PESO_ARESTA,
                      tamanho_minimo: int = TAMANHO_MINIMO_CLIQUE) -> list:
    """
    Ponto de entrada principal do módulo.

    Etapas:
        1. Filtra arestas com peso < min_peso.
        2. Para cada vértice v (em ordem lexicográfica):
               DFS com candidatos = vizinhos de v com índice lexicográfico > v.
        3. Deduplica (frozensets são hashables).
        4. Remove cliques não-maximais.
        5. Filtra por tamanho_minimo.

    Parâmetros:
        grafo          — instância de Graph (src/graph.py)
        min_peso       — limiar mínimo de peso das arestas
        tamanho_minimo — tamanho mínimo dos cliques retornados

    Retorna:
        list[frozenset[str]] — cada frozenset é um clique maximal de palavras.
    """
    adj = filtrar_adjacencia(grafo, min_peso)
    vertices_ordenados = sorted(adj.keys())

    resultado_bruto = []
    for v in vertices_ordenados:
        candidatos = {u for u in adj.get(v, set()) if u > v}
        _dfs({v}, candidatos, adj, resultado_bruto)

    todos = list({c for c in resultado_bruto})
    maximais = filtrar_maximais(todos)
    return [c for c in maximais if len(c) >= tamanho_minimo]


# análise e métricas

def estatisticas_cliques(cliques: list) -> dict:
    if not cliques:
        return {
            "total": 0,
            "tamanho_medio": 0.0,
            "tamanho_maximo": 0,
            "maior_clique": [],
            "distribuicao": {"4-5": 0, "6-7": 0, "8+": 0},
        }

    tamanhos = [len(c) for c in cliques]
    maior = max(cliques, key=len)

    dist = {"4-5": 0, "6-7": 0, "8+": 0}
    for t in tamanhos:
        if t <= 5:
            dist["4-5"] += 1
        elif t <= 7:
            dist["6-7"] += 1
        else:
            dist["8+"] += 1

    return {
        "total": len(cliques),
        "tamanho_medio": round(sum(tamanhos) / len(tamanhos), 2),
        "tamanho_maximo": max(tamanhos),
        "maior_clique": sorted(maior),
        "distribuicao": dist,
    }


def imprimir_relatorio(cliques: list, label: str = "Grupo", top_n: int = 5):
    stats = estatisticas_cliques(cliques)
    linha = "=" * 58

    print(f"\n{linha}")
    print(f"  RELATORIO DE CLIQUES — {label}")
    print(linha)

    if stats["total"] == 0:
        print("  Nenhum clique encontrado com os parametros atuais.")
        print(linha + "\n")
        return

    print(f"  Cliques maximais encontrados (tamanho >= {TAMANHO_MINIMO_CLIQUE}): {stats['total']}")
    print(f"  Tamanho medio dos cliques : {stats['tamanho_medio']} palavras")
    print(f"  Maior clique encontrado   : {stats['tamanho_maximo']} palavras")
    print(f"\n  Distribuicao por numero de palavras no clique:")
    for faixa, qtd in stats["distribuicao"].items():
        barra = "#" * min(qtd, 40)
        print(f"    {faixa} palavras: {qtd:>4} clique(s)  {barra}")

    ordenados = sorted(cliques, key=len, reverse=True)
    n = min(top_n, len(ordenados))
    print(f"\n  Top {n} cliques (grupos de palavras mais densamente conectadas):")
    for i, c in enumerate(ordenados[:n], 1):
        palavras = ", ".join(sorted(c))
        print(f"    {i}. [{len(c)} palavras] {palavras}")
    print(linha + "\n")
    

if __name__ == "__main__":
    CORPUS_A = os.path.join("..", "data", "processed", "corpus_nota1000.json")
    CORPUS_B = os.path.join("..", "data", "processed", "corpus_abaixo1000.json")

    sep = "-" * 58

    print(sep)
    print("  GRUPO A — Redacoes nota 1000")
    print(sep)
    print("  Carregando corpus e construindo grafo de coocorrencia...")
    corpus_a = carregar_corpus(CORPUS_A)
    grafo_a_bruto = construir_grafo_de_coocorrencia(corpus_a)
    print("  Aplicando podas (remove arestas fracas e pontes)...")
    grafo_a, log_a = aplicar_podas(grafo_a_bruto, min_peso=MIN_PESO_ARESTA)
    print("  Enumerando cliques maximais...")
    cliques_a = encontrar_cliques(grafo_a, min_peso=MIN_PESO_ARESTA,
                                  tamanho_minimo=TAMANHO_MINIMO_CLIQUE)
    imprimir_relatorio(cliques_a, label="Grupo A — Nota 1000")

    print(sep)
    print("  GRUPO B — Redacoes abaixo de nota 1000")
    print(sep)
    print("  Carregando corpus e construindo grafo de coocorrencia...")
    corpus_b = carregar_corpus(CORPUS_B)
    grafo_b_bruto = construir_grafo_de_coocorrencia(corpus_b)
    print("  Aplicando podas (remove arestas fracas e pontes)...")
    grafo_b, log_b = aplicar_podas(grafo_b_bruto, min_peso=MIN_PESO_ARESTA)
    print("  Enumerando cliques maximais...")
    cliques_b = encontrar_cliques(grafo_b, min_peso=MIN_PESO_ARESTA,
                                  tamanho_minimo=TAMANHO_MINIMO_CLIQUE)
    imprimir_relatorio(cliques_b, label="Grupo B — Abaixo de 1000")
    
