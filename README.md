# Cliques nas redações do ENEM: Análise Textual com Grafos

Neste projeto, transformamos redações do ENEM em redes para medir a qualidade da argumentação sem precisar ler uma única linha. Usando **Processamento de Linguagem Natural (PLN)** e **Algoritmos de Grafos**, mapeamos como as palavras se conectam nas frases. O nosso objetivo foi provar numericamente a diferença de coesão textual  a qualidade das palavras entre as redações perfeitas (Nota 1000 - Grupo A) e redações com falhas estruturais (Notas menores - Grupo B).

---

## Estruturas e Algoritmos Implementados

* **Grafo via Lista de Adjacência (`grafo.py`):** Mapeamento implementado com Tabelas Hash (dicionários) para inserção e busca de vizinhos.
* **Fila Encadeada / Linked Queue (`fila.py`):** Estrutura auxiliar baseada em nós para gerenciar filas de execução.
* **Busca em Largura / BFS (`bfs.py`):** Algoritmo clássico utilizado para encontrar Componentes Conexos e mapear a conectividade global do texto.
* **Busca de Cliques Maximais via DFS (`cliques.py`):** Algoritmo de Busca em Profundidade (DFS) recursivo  para encontrar cliques maximais e filtrar os agrupamentos ("panelinhas") de palavras mais densos do texto.

---

## 🚀 Como Executar o Projeto

Siga o passo a passo abaixo para rodar o projeto:

### 1. Preparação do Ambiente
Certifique-se de ter o Python 3 instalado. É recomendado criar e ativar um ambiente virtual:

Para Linux/macOS:
```bash
python -m venv venv
source venv/bin/activate
``` 
Para Windows:
```bash
python -m venv venv
venv\Scripts\activate
``` 
### 2. Instalação de Dependências
Com o ambiente ativado, instale as bibliotecas necessárias e o modelo de linguagem em português do spaCy:
```bash
pip install spacy pandas matplotlib
python -m spacy download pt_core_news_sm
``` 
### 3. Pré Processamento dos Dados
O sistema precisa ler a base de dados bruta (redacoes.csv), remover as stopwords, aplicar a lematização e separar os textos nos grupos A (Nota 1000) e B (Abaixo de 1000). Execute:
```bash
python src/preprocessing.py --input data/redacoes.csv --output data/processed/
``` 
Isso gerará os arquivos corpus_nota1000.json e corpus_abaixo1000.json na pasta data/processed/

### 4. Análise de Grafos e Geração de Resultados
Com os JSONs gerados, execute o orquestrador principal. Ele construirá os grafos, aplicará o pipeline de podas (removendo arestas fracas e pontes) e varrerá a rede com os algoritmos de Cliques e BFS.
```bash
python src/analise.py
``` 