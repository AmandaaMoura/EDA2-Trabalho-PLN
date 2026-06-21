# Relatório de Progresso — Análise de Cliques ENEM

**Data:** 21/06/2026  
**Referência:** [planejamento_estrategico.md](../../../planejamento_estrategico.md) (Seções 2, 5, 6, 14)  
**Repositório:** `EDA2-Trabalho-PLN/cliques-enem/`

---

## 1. Resumo

Este relatório cobre **meu desenvolvimento a partir de R3** (grafo, podas, BFS parcial, scripts de apoio). As etapas **R1 (coleta de dados) e R2 (pré-processamento NLP)** já estavam **concluídas antes** — usei os artefatos que o grupo deixou prontos (`data/redacoes.csv`, JSONs em `data/processed/`).

**O que implementei nesta fase:** construção do grafo ponderado, poda em camadas, BFS para pontes, Fila própria e script de relatório de podas. Meu pipeline parte dos JSONs processados até `aplicar_podas()`, sem `networkx` nem `collections.deque`.

**Próximo bloco crítico:** completar o BFS analítico (níveis + componentes), implementar Pilha + DFS guloso de cliques, a análise comparativa e a integração em `main.py`.

**Decisão algorítmica que registrei:** substituí Bron–Kerbosch por **DFS guloso com poda** + ranking, alinhado à disciplina (BFS/DFS, Fila/Pilha).

---

## 2. O que foi feito

### 2.1 Coleta e dados (R1) — *anteriormente desenvolvido*

| Item | Status | Detalhe |
|---|---|---|
| CSV unificado | ✅ | `data/redacoes.csv` (~128 redações carregadas pelo pré-processamento) |
| Grupo A (nota 1000) | ✅ | 64 redações |
| Grupo B (nota < 1000) | ✅ | 64 redações |
| JSONs processados | ✅ | `data/processed/corpus_nota1000.json`, `corpus_abaixo1000.json` |

Não participei desta etapa; **herdei** o CSV e os JSONs como ponto de partida.

**Observação de balanceamento (relevante para minha análise):** o corpus tem o mesmo número de redações (64 vs 64), mas o Grupo A tem **~2× mais lemas por redação** (196 vs 102 em média). Preciso documentar ou normalizar isso na análise final.

---

### 2.2 Pré-processamento NLP (R2) — *anteriormente desenvolvido*

| Item | Status | Arquivo |
|---|---|---|
| Pipeline spaCy (`pt_core_news_sm`) | ✅ | `src/preprocessing.py` |
| Lematização + POS (NOUN, VERB, ADJ) | ✅ | |
| Stopwords + filtro de lemas (≥ 3 chars) | ✅ | |
| Coocorrência por sentença (`doc.sents`) | ✅ | |
| Separação A/B | ✅ | `NOTA_CORTE = 1000` |


**Comando usado pelo grupo (referência):**

```bash
cd cliques-enem
python src/preprocessing.py --input data/redacoes.csv --output data/processed/
```

---

### 2.3 Grafo ponderado (R3) — *desenvolvido nesta etapa*

| Item | Status | Arquivo |
|---|---|---|
| Classe `Graph` (lista de adjacência esparso) | ✅ | `src/graph.py` |
| `adj[u][v] = peso` (coocorrência por sentença) | ✅ | |
| `construir_grafo_de_coocorrencia(corpus)` | ✅ | |
| `carregar_corpus`, `estatisticas_grafo` | ✅ | |
| `definir_aresta` (cópia na poda, sem somar) | ✅ | |

**Modelo que adotei:** vértice = lema; peso = número de sentenças em que o par coocorre.

---

### 2.4 Poda do grafo (R3) — *desenvolvido nesta etapa*

| Etapa | Função | Status |
|---|---|---|
| 1 — Peso absoluto | `poda_peso_absoluto(min_peso=2)` | ✅ |
| 2 — Peso relativo | `poda_peso_relativo(fator_media=0.5, fator_max=0.25)` | ✅ |
| 3 — Arestas ponte | `poda_pontes()` + BFS | ✅ |
| Orquestração + log | `aplicar_podas()` | ✅ |

**Parâmetros que foram usados:** `MIN_PESO_ARESTA=2`, `FATOR_MEDIA=0.5`, `FATOR_MAX=0.25`.

---

### 2.5 BFS parcial (R3) — *desenvolvido nesta etapa*

| Função | Status | Uso |
|---|---|---|
| `bfs(grafo, origem, destino, aresta_bloqueada)` | ✅ | Detecção de pontes em `poda_pontes` |
| `bfs_niveis` | ❌ | Raio semântico (planejamento Seção 6.2) |
| `componentes_conexos` | ❌ | Fragmentação lexical (planejamento Seção 6.2) |
**Fila:** implementei em `src/queue_structure.py` (`Queue`).

---

### 2.6 Material — *desenvolvido nesta etapa*

| Item | Status | Local |
|---|---|---|
| Exemplo DFS + Pilha (5 palavras) | ✅ | `exemplos/slide-dfs-cliques/` |
| Script de estatísticas de poda | ✅ | `scripts/run_podas_report.py` → `results/tables/podas_report.md` |

---

## 3. Resultados empíricos da poda (21/06/2026)

Executei com `aplicar_podas(construir_grafo_de_coocorrencia(corpus))` e os parâmetros padrão.

### Grupo A — Nota 1000

| Etapa | Vértices | Arestas | Peso médio | Peso máx. |
|---|---:|---:|---:|---:|
| bruto | 2.886 | 72.138 | 1,24 | 69 |
| poda_absoluta | 1.391 | 10.221 | 2,71 | 69 |
| poda_relativa | 20 | 25 | 28,44 | 69 |
| poda_pontes | 13 | 19 | 30,16 | 69 |

### Grupo B — Nota < 1000

| Etapa | Vértices | Arestas | Peso médio | Peso máx. |
|---|---:|---:|---:|---:|
| bruto | 2.373 | 34.940 | 1,16 | 21 |
| poda_absoluta | 1.226 | 3.994 | 2,38 | 21 |
| poda_relativa | 71 | 82 | 7,32 | 21 |
| poda_pontes | 25 | 42 | 7,81 | 21 |

### O que interpreto

- A **poda absoluta** remove a maior massa de arestas fracas (peso 1).
- A **poda relativa** ficou **muito agressiva no Grupo A** (20 vértices finais) — provavelmente preciso **calibrar para menores** `FATOR_MEDIA` / `FATOR_MAX, tentei para 0,3 / 0,15, mas não mudou muita coisa, buscando equilibrar A vs B antes dos cliques.
- A **poda de pontes** reduz mais no A (25→19 arestas) do que no B (82→42).
- O Grupo B retém **mais vértices** após a poda

---

## 4. O que ainda falta (vs. planejamento estratégico)

### 4.1 Algoritmos e estruturas

| Item | Responsável | Prioridade | Arquivo |
|---|---|---|---|
| `bfs_niveis(grafo, origem)` | R3 | Alta | `src/bfs.py` |
| `componentes_conexos(grafo)` | R3 | Alta | `src/bfs.py` |
| `stack_structure.py` (Pilha) | R4 | Alta | criar |
| `clique_guloso` + `buscar_cliques` | R4 | Alta | `src/cliques.py` |
| `rankear_cliques` | R4 | Alta | `src/cliques.py` |
| Calibrar poda (fatores relativos) | R3/R4 | Alta | `src/graph.py` |
| `main.py` — pipeline completo | R5 | Média | `src/main.py` |
| `analysis.py` — métricas A vs B | R5 | Média | `src/analysis.py` |

**O que decidimos não implementar:** Bron–Kerbosch, por nao estar dentro dos conteudos aprendidos em aula.

---

### 4.2 Análise comparativa (Seção 7)

| Métrica | Status |
|---|---|
| Top-N cliques rankeados (DFS guloso) | ❌ |
| Maior clique / média top-3 | ❌ |
| Peso total/médio/mínimo por clique | ❌ |
| Componentes conexos (BFS) | ❌ |
| Profundidade BFS / palavras por nível | ❌ |

---

### 4.3 Entregáveis finais (Seções 8–11)

| Item | Status | Prazo planejado |
|---|---|---|
| README completo | ⚠️ esqueleto | 21–22/06 |
| `docs/llm_usage.md` | ❌ | 21/06 |
| Slides apresentação | ❌ | 21/06 |
| Teste end-to-end ambiente limpo | ❌ | 21/06 |
| Push final GitHub | ❌ | 22/06 |

---

## 5. Ordem para os próximos passos

```
[1] Calibrar poda relativa (Grupo A muito esparso após fatores 0,5/0,25)
         ↓
[2] bfs_niveis + componentes_conexos (bfs.py)
         ↓
[3] stack_structure.py + cliques.py (DFS guloso, TOP_K=10, min clique=4)
         ↓
[4] Rodar cliques nos grafos podados A e B; comparar ranking
         ↓
[5] analysis.py + main.py
         ↓
[6] README, llm_usage.md, slides, push
```

---

## 6. Mapa de arquivos do repositório

```
cliques-enem/
├── data/                               ← R1 (anterior)
│   ├── redacoes.csv                    ✅ herdado
│   └── processed/
│       ├── corpus_nota1000.json        ✅ herdado
│       └── corpus_abaixo1000.json      ✅ herdado
├── src/
│   ├── preprocessing.py                ✅ R2 (anterior)
│   ├── graph.py                        ✅ R3 — feito nesta etapa
│   ├── queue_structure.py              ✅ R3 — feito nesta etapa
│   ├── bfs.py                          ⚠️ R3 — feito parcialmente nesta etapa, parcial
│   ├── cliques.py                      ❌ R4 — pendente
│   ├── analysis.py                     ❌ R5 — pendente
│   └── main.py                         ❌ R5 — pendente
├── docs/
│   └── relatorio_progresso.md          ← este arquivo
├── scripts/
│   └── run_podas_report.py             ✅ R3 — feito nesta etapa
```

---

## 7. Conformidade com a disciplina

| Requisito | Situação |
|---|---|
| Grafo (lista de adjacência) | ✅ |
| Fila implementada do zero | ✅ |
| Pilha implementada do zero | ❌ pendente |
| BFS implementado pelo grupo | ⚠️ parcial |
| DFS para cliques | ❌ pendente |
| Sem libs de grafo para algoritmos | ✅ |
| spaCy só no pré-processamento | ✅ |

---

## 8. Riscos ativos

| Risco | Mitigação sugerida |
|---|---|
| Poda relativa deixa Grupo A com 13 vértices | Reduzir `FATOR_MEDIA`/`FATOR_MAX`; testar 0,3 e 0,15 |
| Cliques vazios após poda agressiva | Relaxar poda só no grupo afetado **ou** unificar parâmetros e re-calibrar |
---

## 9. Conclusão

A base **R1 + R2** (dados e pré-processamento) já estava pronta quando comecei. Nesta fase, implementei e testei **R3** (grafo → poda → BFS parcial). Estou pronto para entrar na **fase de cliques e análise comparativa**, precedida de uma **calibração rápida da poda relativa** no Grupo A.

**Minha estimativa de progresso:** R1/R2 ✅ (herdados); R3 ~70% (falta calibrar poda e completar BFS analítico); R4/R5 ainda por fazer.
