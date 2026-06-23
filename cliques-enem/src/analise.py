import os
import matplotlib.pyplot as plt
import pandas as pd

# importo módulos de outros arquivos
from grafo import carregar_corpus, construir_grafo_de_coocorrencia, aplicar_podas, estatisticas_grafo
from cliques import encontrar_cliques, estatisticas_cliques
from bfs import componentes_conexos

# JSONs oficiais 
CORPUS_A = os.path.join("data", "processed", "corpus_nota1000.json")
CORPUS_B = os.path.join("data", "processed", "corpus_abaixo1000.json")

# pasta onde guardo os gráficos de resultados
PASTA_FIGURAS = os.path.join("cliques-enem", "results", "figures")

def gerar_graficos_comparativos_globais(stats_a, stats_b):
    os.makedirs(PASTA_FIGURAS, exist_ok=True)
    
    #métricas gerais
    categorias = [
        'Total de Cliques',
        'Tamanho Médio dos Cliques',
        'Tamanho Máx. Clique',
        'Componentes Conexos',
        'Vértices Pós-Poda',
        'Arestas Pós-Poda'
    ]
    valores_a = [
        stats_a['cliques']['total'],
        stats_a['cliques']['tamanho_medio'],
        stats_a['cliques']['tamanho_maximo'],
        len(stats_a['componentes']),
        stats_a['grafo']['vertices'],
        stats_a['grafo']['arestas']
    ]
    valores_b = [
        stats_b['cliques']['total'],
        stats_b['cliques']['tamanho_medio'],
        stats_b['cliques']['tamanho_maximo'],
        len(stats_b['componentes']),
        stats_b['grafo']['vertices'],
        stats_b['grafo']['arestas']
    ]

    df = pd.DataFrame({'Grupo A (Nota 1000)': valores_a, 'Grupo B (< 1000)': valores_b}, index=categorias)
    df.plot(kind='bar', figsize=(12, 7), color=['#2ca02c', '#d62728'], edgecolor='black')
    plt.title('Métricas Globais Comparativas — Mesmas Métricas da Tabela')
    plt.ylabel('Valores Obtidos')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(PASTA_FIGURAS, 'analise_comparativa_metricas.png'))
    plt.close()

    # gráfico de distribuição de tamanhos de cliques
    dist_a = stats_a['cliques']['distribuicao']
    dist_b = stats_b['cliques']['distribuicao']
    
    faixas = sorted(dist_a.keys())
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
    
    g_podado, _ = aplicar_podas(
        g_bruto, 
        min_peso=2, 
        fator_media=0.4,   # valor de equilíbrio estatístico
        fator_max=0.12,   # valor ideal para coexistência de anos/temas
        usar_pontes=True
    )

    comp = componentes_conexos(g_podado)
    
    # enumeração completa de cliques
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
        # exibição da tabela completa
        linha = "-" * 85
        print(f"\n{linha}\nTABELA COMPARATIVA DE RESULTADOS GLOBAIS (R5)\n{linha}")
        print(f"{'Métrica Medida':<40} | {'Grupo A':<18} | {'Grupo B':<18}")
        print(linha)
        print(f"{'Nº Total de Cliques (>= 4)':<40} | {dados_a['cliques']['total']:<18} | {dados_b['cliques']['total']:<18}")
        print(f"{'Tamanho Médio dos Cliques':<40} | {dados_a['cliques']['tamanho_medio']:<18} | {dados_b['cliques']['tamanho_medio']:<18}")
        print(f"{'Tamanho do Maior Clique':<40} | {dados_a['cliques']['tamanho_maximo']:<18} | {dados_b['cliques']['tamanho_maximo']:<18}")
        print(f"{'Nº de Componentes Conexos':<40} | {len(dados_a['componentes']):<18} | {len(dados_b['componentes']):<18}")
        print(f"{'Vértices Restantes (Pós-Poda)':<40} | {dados_a['grafo']['vertices']:<18} | {dados_b['grafo']['vertices']:<18}")
        print(f"{'Arestas Restantes (Pós-Poda)':<40} | {dados_a['grafo']['arestas']:<18} | {dados_b['grafo']['arestas']:<18}")
        print(linha)
        
        # mapeamento quantitativo
        print("\n--> Mapeamento dos Cliques:")
        
        print(f"\n  [Grupo A - Nota 1000] - 30/30 Cliques:")
        cliques_ordenados_a = sorted(dados_a['lista_cliques'], key=len, reverse=True)
        if cliques_ordenados_a:
            for i, clq in enumerate(cliques_ordenados_a[:30], 1):
                print(f"    {i}. Tamanho {len(clq)}: {sorted(list(clq))}")
        else:
            print("    Nenhum clique detectado com os parâmetros atuais.")
            
        print(f"\n  [Grupo B - Nota < 1000] - 30/96 Cliques:")
        cliques_ordenados_b = sorted(dados_b['lista_cliques'], key=len, reverse=True)
        if cliques_ordenados_b:
            for i, clq in enumerate(cliques_ordenados_b[:30], 1):
                print(f"    {i}. Tamanho {len(clq)}: {sorted(list(clq))}")
        else:
            print("    Nenhum clique detectado com os parâmetros atuais.")
        
        # gera os novos gráficos
        gerar_graficos_comparativos_globais(dados_a, dados_b)
        print(f"\n[SUCESSO]")

if __name__ == "__main__":
    main()