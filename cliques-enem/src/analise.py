# analise.py
import os
import matplotlib.pyplot as plt
import pandas as pd

# Importo os módulos dos outros arquivos
from graph import carregar_corpus, construir_grafo_de_coocorrencia, aplicar_podas, estatisticas_grafo
from cliques import encontrar_cliques, estatisticas_cliques
from bfs import componentes_conexos, bfs_niveis

# JSONs salvos
CORPUS_A = os.path.join("data", "processed", "corpus_nota1000.json")
CORPUS_B = os.path.join("data", "processed", "corpus_abaixo1000.json")

# Pasta onde guardo os gráficos
PASTA_FIGURAS = os.path.join("cliques-enem", "results", "figures")

# Palavra-semente comum para a análise do Raio Semântico
PALAVRA_SEMENTE = "sociedade" 

def gerar_graficos_comparativos(stats_a, stats_b):
    """Gera gráficos lado a lado em barras simples[cite: 157]."""
    os.makedirs(PASTA_FIGURAS, exist_ok=True)
    
    # 1. Gero o Gráfico de Métricas Gerais
    categorias = ['Total de Cliques', 'Tamanho Máx. Clique', 'Componentes Conexos', 'Raio Semântico']
    valores_a = [stats_a['cliques']['total'], stats_a['cliques']['tamanho_maximo'], len(stats_a['componentes']), stats_a['profundidade_bfs']]
    valores_b = [stats_b['cliques']['total'], stats_b['cliques']['tamanho_maximo'], len(stats_b['componentes']), stats_b['profundidade_bfs']]
    
    df = pd.DataFrame({'Grupo A (Nota 1000)': valores_a, 'Grupo B (< 1000)': valores_b}, index=categorias)
    df.plot(kind='bar', figsize=(10, 6), color=['#2ca02c', '#d62728'], edgecolor='black')
    plt.title('Análise Comparativa de Métricas — Grupo A vs Grupo B')
    plt.ylabel('Valores Obtidos')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(PASTA_FIGURAS, 'analise_comparativa_metricas.png'))
    plt.close()

    # 2. Gero o Gráfico de Palavras por Nível da BFS
    niveis_a = stats_a['palavras_por_nivel']
    niveis_b = stats_b['palavras_por_nivel']
    max_nivel = max(max(niveis_a.keys() if niveis_a else [0]), max(niveis_b.keys() if niveis_b else [0]))
    
    niveis_eixo = list(range(max_nivel + 1))
    contagem_a = [niveis_a.get(n, 0) for n in niveis_eixo]
    contagem_b = [niveis_b.get(n, 0) for n in niveis_eixo]
    
    df_niveis = pd.DataFrame({'Grupo A': contagem_a, 'Grupo B': contagem_b}, index=[f'Nível {n}' for n in niveis_eixo])
    df_niveis.plot(kind='bar', figsize=(10, 5), color=['#2ca02c', '#d62728'], edgecolor='black')
    plt.title(f'Concentração Vocabular: Nº de Palavras por Nível a partir de "{PALAVRA_SEMENTE}"')
    plt.xlabel('Camada / Nível da BFS')
    plt.ylabel('Quantidade de Palavras')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(PASTA_FIGURAS, 'concentracao_por_nivel_bfs.png'))
    plt.close()

def analisar_grupo(caminho_corpus, label):
    print(f"\n" + "="*60)
    print(f" EXECUÇÃO DE MÉTRICAS: {label}")
    print("="*60)
    
    if not os.path.exists(caminho_corpus):
        print(f"[ERRO] Arquivo {caminho_corpus} não encontrado. Verifique a execução do preprocessing.")
        return None

    corpus = carregar_corpus(caminho_corpus)
    g_bruto = construir_grafo_de_coocorrencia(corpus)
    
    print("\n--> Aplicando Pipeline de Podas:")
    g_podado, _ = aplicar_podas(g_bruto, min_peso=2, usar_pontes=True)
    
    # Métrica: Componentes Conexos (BFS) 
    comp = componentes_conexos(g_podado)
    
    # Métrica: Cliques 
    cliques_encontrados = encontrar_cliques(g_podado, min_peso=2, tamanho_minimo=4)
    stats_c = estatisticas_cliques(cliques_encontrados)
    
    # Métrica: BFS por Níveis
    semente_real = PALAVRA_SEMENTE
    if semente_real not in g_podado.obter_todos_vertices():
        vertices_disponiveis = g_podado.obter_todos_vertices()
        semente_real = vertices_disponiveis[0] if vertices_disponiveis else None
    
    niveis_calculados = bfs_niveis(g_podado, semente_real) if semente_real else {}
    
    profundidade_bfs = max(niveis_calculados.values()) if niveis_calculados else 0
    palavras_por_nivel = {}
    for nv in niveis_calculados.values():
        palavras_por_nivel[nv] = palavras_por_nivel.get(nv, 0) + 1

    return {
        "grafo": estatisticas_grafo(g_podado),
        "cliques": stats_c,
        "componentes": comp,
        "lista_cliques": cliques_encontrados,
        "profundidade_bfs": profundidade_bfs,
        "palavras_por_nivel": palavras_por_nivel,
        "semente_utilizada": semente_real
    }

def main():
    dados_a = analisar_grupo(CORPUS_A, "Grupo A (Nota 1000)")
    dados_b = analisar_grupo(CORPUS_B, "Grupo B (Abaixo de 1000)")
    
    if dados_a and dados_b:
        # Exibo a Tabela Comparativa de Resultados no terminal
        linha = "-" * 75
        print(f"\n{linha}\nTABELA COMPARATIVA DE RESULTADOS (LADO A LADO)\n{linha}")
        print(f"{'Métrica Medida':<35} | {'Grupo A':<15} | {'Grupo B':<15}")
        print(linha)
        print(f"{'Nº Total de Cliques (>= 4)':<35} | {dados_a['cliques']['total']:<15} | {dados_b['cliques']['total']:<15}")
        print(f"{'Tamanho Médio dos Cliques':<35} | {dados_a['cliques']['tamanho_medio']:<15} | {dados_b['cliques']['tamanho_medio']:<15}")
        print(f"{'Tamanho do Maior Clique':<35} | {dados_a['cliques']['tamanho_maximo']:<15} | {dados_b['cliques']['tamanho_maximo']:<15}")
        print(f"{'Nº de Componentes Conexos':<35} | {len(dados_a['componentes']):<15} | {len(dados_b['componentes']):<15}")
        print(f"{'Profundidade BFS (Raio Semântico)':<35} | {dados_a['profundidade_bfs']:<15} | {dados_b['profundidade_bfs']:<15}")
        print(linha)
        
        print("\n--> Conteúdo qualitativo do maior clique[cite: 156]:")
        print(f"  [Grupo A]: {dados_a['cliques']['maior_clique']}")
        print(f"  [Grupo B]: {dados_b['cliques']['maior_clique']}")
        print(f"  (Sementes BFS usadas: Grupo A='{dados_a['semente_utilizada']}', Grupo B='{dados_b['semente_utilizada']}')")
        
        # Gero os gráficos diretamente na pasta
        gerar_graficos_comparativos(dados_a, dados_b)
        print(f"\n[SUCESSO] Medições realizadas! Imagens salvas em '{PASTA_FIGURAS}'")

if __name__ == "__main__":
    main()