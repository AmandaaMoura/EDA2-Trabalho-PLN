# Relatório de Uso de LLM — Requisito R5

Este documento descreve como as ferramentas de Inteligência Artificial e Modelos de Linguagem (LLMs) foram integradas no desenvolvimento e depuração deste projeto.

## 1. Ferramentas Utilizadas
* **Modelo:** Gemini (Google) 
* **Interface:** Chat / Assistente Editorial de Código

## 2. Escopo da Assistência
A IA foi utilizada estritamente como um par de programação (*Pair Programming*) focado em engenharia de software e integração de sistemas:

* **Mapeamento de Arquiteturas:** Auxílio na criação inicial de um script central de pipeline (`analysis.py`) capaz de unificar os módulos pré-existentes de PLN (`preprocessing.py`), Grafos (`graph.py`), BFS (`bfs.py`) e DFS (`cliques.py`).

* **Depuração de Interfaces (Refatoração):** Resolução de incompatibilidades de nomenclaturas entre assinaturas de métodos das classes `Grafo` e `Graph` (ex: mapeamento de `obter_todos_vertices` para `listar_vertices`).

* **Visualização de Dados:** Estruturação de scripts automatizados utilizando as bibliotecas `matplotlib` e `pandas` para salvar gráficos comparativos diretamente na pasta `presentation/`.

## 3. Raciocínio Humano e Supervisão
A IA atuou unicamente na amarração dos componentes de software e automação visual da entrega R5.