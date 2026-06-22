# analise.py
import os
import matplotlib.pyplot as plt
import pandas as pd

# importo os módulos dos outros arquivos
from graph import carregar_corpus, construir_grafo_de_coocorrencia, aplicar_podas, estatisticas_grafo
from cliques import encontrar_cliques, estatisticas_cliques
from bfs import componentes_conexos

# JSONs que foram salvos
CORPUS_A = os.path.join("data", "processed", "corpus_nota1000.json")
CORPUS_B = os.path.join("data", "processed", "corpus_abaixo1000.json")

# pasta onde guardo os gráficos
PASTA_FIGURAS = os.path.join("cliques-enem", "results", "figures")

def gerar_graficos_comparativos_globais(stats_a, stats_b):
    """Gera gráficos estruturais globais, sem depender de sementes."""
    os.makedirs(PASTA_FIGURAS, exist_ok=True)
    
    # 1. gráfico de métricas gerais de cliques e conectividade
    categorias = ['Total de Cliques', 'Tamanho Máx. Clique', 'Componentes Conexos']
    valores_a = [stats_a['cliques']['total'], stats_a['cliques']['tamanho_maximo'], len(stats_a['componentes'])]
    valores_b = [stats_b['cliques']['total'], stats_b['cliques']['tamanho_maximo'], len(stats_b['componentes'])]
    
    df = pd.DataFrame({'Grupo A (Nota 1000)': valores_a, 'Grupo B (< 1000)': valores_b}, index=categorias)
    df.plot(kind='bar', figsize=(10, 6), color=['#2ca02c', '#d62728'], edgecolor='black')
    plt.title('Análise Comparativa Global — Grupo A vs Grupo B')
    plt.ylabel('Valores Obtidos')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(PASTA_FIGURAS, 'analise_comparativa_metricas.png'))
    plt.close()

    # 2. gráfico de distribuição de tamanhos de cliques
    dist_a = stats_a['cliques']['distribuicao']
    dist_b = stats_b['cliques']['distribuicao']
    
    faixas = list(dist_a.keys())
    contagem_a = [dist_a[f] for f in faixas]
    contagem_b = [dist_b[f] for f in faixas]
    
    df_dist = pd.DataFrame({'Grupo A': contagem_a, 'Grupo B': contagem_b}, index=faixas)
    df_dist.plot(kind='bar', figsize=(10, 5), color=['#2ca02c', '#d62728'], edgecolor='black')
    plt.title('Densidade Argumentativa: Distribuição por Tamanho de Cliques')
    plt.xlabel('Faixas de Tamanho do Clique (Nº de Palavras)')
    plt.ylabel('Quantidade de Cliques Encontrados')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(PASTA_FIGURAS, 'distribuicao_tamanhos_cliques.png'))
    plt.close()

def analisar_grupo_global(caminho_corpus, label):
    print(f"\n" + "="*60)
    print(f" EXECUÇÃO DE MÉTRICAS GLOBAIS: {label}")
    print("="*60)
    
    if not os.path.exists(caminho_corpus):
        print(f"[ERRO] Arquivo {caminho_corpus} não encontrado. Verifique a execução do preprocessing.")
        return None

    corpus = carregar_corpus(caminho_corpus)
    g_bruto = construir_grafo_de_coocorrencia(corpus)
    
    print("\n--> Aplicando Pipeline de Podas:")
    
    # fatores corrigidos
    g_podado, _ = aplicar_podas(
        g_bruto, 
        min_peso=2, 
        fator_media=0.4,   # valor de equilíbrio para não travar
        fator_max=0.12,   # valor ideal para resgatar outros temas
        usar_pontes=True
    )
    
    # métrica global 1: componentes conexos via BFS
    comp = componentes_conexos(g_podado)
    
    # métrica global 2: enumeração completa de cliques maximais
    cliques_encontrados = encontrar_cliques(g_podado, min_peso=2, tamanho_minimo=4)
    stats_c = estatisticas_cliques(cliques_encontrados)
    
    return {
        "grafo": estatisticas_grafo(g_podado),
        "cliques": stats_c,
        "componentes": comp,
        "lista_cliques": cliques_encontrados
    }
def main():
    dados_a = analisar_grupo_global(CORPUS_A, "Grupo A (Nota 1000)")
    dados_b = analisar_grupo_global(CORPUS_B, "Grupo B (Abaixo de 1000)")
    
    if dados_a and dados_b:
        # exibição da Tabela Comparativa de Resultados Globais no terminal
        linha = "-" * 75
        print(f"\n{linha}\nTABELA COMPARATIVA DE RESULTADOS GLOBAIS\n{linha}")
        print(f"{'Métrica Medida':<35} | {'Grupo A':<15} | {'Grupo B':<15}")
        print(linha)
        print(f"{'Nº Total de Cliques (>= 4)':<35} | {dados_a['cliques']['total']:<15} | {dados_b['cliques']['total']:<15}")
        print(f"{'Tamanho Médio dos Cliques':<35} | {dados_a['cliques']['tamanho_medio']:<15} | {dados_b['cliques']['tamanho_medio']:<15}")
        print(f"{'Tamanho do Maior Clique':<35} | {dados_a['cliques']['tamanho_maximo']:<15} | {dados_b['cliques']['tamanho_maximo']:<15}")
        print(f"{'Nº de Componentes Conexos':<35} | {len(dados_a['componentes']):<15} | {len(dados_b['componentes']):<15}")
        print(f"{'Vértices Restantes (Pós-Poda)':<35} | {dados_a['grafo']['vertices']:<15} | {dados_b['grafo']['vertices']:<15}")
        print(f"{'Arestas Restantes (Pós-Poda)':<35} | {dados_a['grafo']['arestas']:<15} | {dados_b['grafo']['arestas']:<15}")
        print(linha)
        
        # mapeamento qualitativo de relevância dos subgrafos completos
        print("\n--> Mapeamento e Relevância dos Principais Cliques Maximais:")
        
        print(f"\n  [Grupo A - Nota 1000] Núcleos Temáticos Consolidados:")
        cliques_ordenados_a = sorted(dados_a['lista_cliques'], key=len, reverse=True)
        if cliques_ordenados_a:
            for i, clq in enumerate(cliques_ordenados_a[:3], 1):
                print(f"    {i}. Tamanho {len(clq)}: {sorted(list(clq))}")
        else:
            print("    Nenhum clique detectado com os parâmetros atuais.")
            
        print(f"\n  [Grupo B - Nota < 1000] Núcleos Temáticos Fragmentados:")
        cliques_ordenados_b = sorted(dados_b['lista_cliques'], key=len, reverse=True)
        if cliques_ordenados_b:
            for i, clq in enumerate(cliques_ordenados_b[:5], 1):
                print(f"    {i}. Tamanho {len(clq)}: {sorted(list(clq))}")
        else:
            print("    Nenhum clique detectado com os parâmetros atuais.")
        
        # geração automática dos novos gráficos globais
        gerar_graficos_comparativos_globais(dados_a, dados_b)
        print(f"\n[SUCESSO] Medições estruturais concluídas! Imagens salvas em '{PASTA_FIGURAS}'")

if __name__ == "__main__":
    main()