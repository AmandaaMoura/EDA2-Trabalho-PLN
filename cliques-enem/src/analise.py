# cliques-enem/src/analysis.py

import os
import matplotlib.pyplot as plt
import pandas as pd

# Importando os módulos que você já escreveu
from graph import carregar_corpus, construir_grafo_de_coocorrencia, aplicar_podas, estatisticas_grafo
from cliques import encontrar_cliques, estatisticas_cliques
from bfs import componentes_conexos

# Configurações de caminhos baseadas no seu projeto
# Modifique essas 3 linhas no topo do seu analise.py:
CORPUS_A = os.path.join("data", "processed", "corpus_nota1000.json")
CORPUS_B = os.path.join("data", "processed", "corpus_abaixo1000.json")
PASTA_OUTPUT = os.path.join("presentation")

def gerar_graficos_comparativos(stats_a, stats_b, cliques_a, cliques_b):
    """Gera e salva gráficos comparativos exigidos pelo R5."""
    os.makedirs(PASTA_OUTPUT, exist_ok=True)
    
    # --- GRÁFICO 1: Comparativo de Métricas do Grafo ---
    categorias = ['Vértices (Palavras)', 'Arestas (Conexões)', 'Total de Cliques']
    valores_a = [stats_a['grafo']['vertices'], stats_a['grafo']['arestas'], stats_a['cliques']['total']]
    valores_b = [stats_b['grafo']['vertices'], stats_b['grafo']['arestas'], stats_b['cliques']['total']]
    
    df_comp = pd.DataFrame({'Nota 1000': valores_a, 'Abaixo de 1000': valores_b}, index=categorias)
    
    ax = df_comp.plot(kind='bar', figsize=(10, 6), color=['#2ca02c', '#d62728'], zorder=2)
    plt.title('Comparativo Estrutural: Redações Nota 1000 vs Abaixo de 1000')
    plt.ylabel('Quantidade')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    caminho_grafico_1 = os.path.join(PASTA_OUTPUT, 'comparativo_estrutural.png')
    plt.savefig(caminho_grafico_1)
    plt.close()
    print(f"[OK] Gráfico salvo em: {caminho_grafico_1}")

    # --- GRÁFICO 2: Distribuição de Tamanho de Cliques ---
    dist_a = stats_a['cliques']['distribuicao']
    dist_b = stats_b['cliques']['distribuicao']
    faixas = list(dist_a.keys())
    
    df_dist = pd.DataFrame({
        'Nota 1000': [dist_a[f] for f in faixas],
        'Abaixo de 1000': [dist_b[f] for f in faixas]
    }, index=faixas)
    
    df_dist.plot(kind='line', marker='o', figsize=(8, 5), color=['#2ca02c', '#d62728'], linewidth=2)
    plt.title('Distribuição do Tamanho dos Cliques de Palavras')
    plt.xlabel('Tamanho do Clique (Qtd. de Palavras)')
    plt.ylabel('Número de Cliques Encontrados')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    
    caminho_grafico_2 = os.path.join(PASTA_OUTPUT, 'distribuicao_cliques.png')
    plt.savefig(caminho_grafico_2)
    plt.close()
    print(f"[OK] Gráfico salvo em: {caminho_grafico_2}")

def analisar_grupo(caminho_corpus, label):
    """Executa todo o pipeline para um grupo específico."""
    print(f"\n" + "="*50)
    print(f" PROCESSANDO: {label}")
    print("="*50)
    
    if not os.path.exists(caminho_corpus):
        print(f"[ERRO] Arquivo {caminho_corpus} não encontrado. Certifique-se de rodar o preprocessing.py primeiro.")
        return None

    # 1. Carrega o Corpus
    corpus = carregar_corpus(caminho_corpus)
    
    # 2. Constrói Grafo Bruto
    g_bruto = construir_grafo_de_coocorrencia(corpus)
    
    # 3. Aplica as 3 Podas (Absoluta, Relativa e Pontes)
    print("\n--> Aplicando Pipeline de Podas:")
    g_podado, _ = aplicar_podas(g_bruto, min_peso=2, usar_pontes=True)
    
    # 4. Análise BFS: Componentes Conexos
    # Convertemos o grafo do módulo graph para o formato aceito pela BFS se necessário,
    # mas suas implementações de obter_todos_vertices já são compatíveis.
    comp = componentes_conexos(g_podado)
    
    # 5. Extração de Cliques Maximais
    print("\n--> Enumerando Cliques Maximais via DFS...")
    cliques_encontrados = encontrar_cliques(g_podado, min_peso=2, tamanho_minimo=4)
    
    # Coleta de Métricas
    stats_g = estatisticas_grafo(g_podado)
    stats_c = estatisticas_cliques(cliques_encontrados)
    
    print(f"\n[Resultados {label}]")
    print(f" - Componentes Conexos: {len(comp)}")
    print(f" - Cliques Encontrados: {stats_c['total']}")
    print(f" - Maior Clique: {stats_c['tamanho_maximo']} palavras")
    
    return {
        "grafo": stats_g,
        "cliques": stats_c,
        "componentes": comp,
        "lista_cliques": cliques_encontrados
    }

def main():
    print("Iniciando Pipeline de Análise Comparativa do ENEM (R5)...")
    
    # Executa a análise para os dois grupos
    dados_a = analisar_grupo(CORPUS_A, "Grupo A (Nota 1000)")
    dados_b = analisar_grupo(CORPUS_B, "Grupo B (Abaixo de 1000)")
    
    if dados_a and dados_b:
        # Gera os gráficos na pasta presentation/
        print("\n" + "-"*50)
        print(" GERANDO ARTEFATOS VISUAIS PARA A APRESENTAÇÃO ")
        print("-"*50)
        gerar_graficos_comparativos(dados_a, dados_b, dados_a['lista_cliques'], dados_b['lista_cliques'])
        print("\n[SUCESSO] Pipeline completo finalizado.")
        print(f"Confira os gráficos gerados na pasta: '{PASTA_OUTPUT}'")

if __name__ == "__main__":
    main()