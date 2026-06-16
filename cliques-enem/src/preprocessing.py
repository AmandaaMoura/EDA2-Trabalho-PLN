"""
Lê a planilha de redações (CSV exportado do Google Sheets),
aplica o pipeline spaCy e salva as sentenças processadas em JSON.

Uso:
    python preprocessing.py --input redacoes.csv --output data/processed/
"""

import csv
import json
import argparse
import os
import spacy


# Classes gramaticais que serão MANTIDAS (palavras de conteúdo)
POS_PERMITIDOS = {"NOUN", "VERB", "ADJ"}

# Comprimento mínimo de um lema para ser considerado (evita lemas de 1-2 letras)
TAMANHO_MINIMO_LEMA = 3

# Nota de corte: abaixo dessa nota = Grupo B
NOTA_CORTE = 1000  # apenas nota exatamente 1000 vai para o Grupo A

def carregar_modelo_spacy():
    """Carrega o modelo português do spaCy."""
    try:
        nlp = spacy.load("pt_core_news_sm")
        print("[OK] Modelo pt_core_news_sm carregado.")
        return nlp
    except OSError:
        print("[ERRO] Modelo não encontrado. Execute:")
        print("       python -m spacy download pt_core_news_sm")
        raise


def processar_sentenca(sentenca, nlp_stopwords):
    """
    Recebe um objeto sentença do spaCy e retorna lista de lemas filtrados.

    Filtros aplicados:
    - Classe gramatical (POS): apenas NOUN, VERB, ADJ
    - Stopwords do spaCy + lista customizada
    - Comprimento mínimo do lema
    - Remove tokens que não sejam alfabéticos
    """
    lemas = []
    for token in sentenca:
        # Ignorar pontuação, espaços, números
        if not token.is_alpha:
            continue
        # Filtrar por classe gramatical
        if token.pos_ not in POS_PERMITIDOS:
            continue
        lema = token.lemma_.lower().strip()
        # Filtrar stopwords do spaCy
        if token.is_stop:
            continue
        # Filtrar lemas muito curtos
        if len(lema) < TAMANHO_MINIMO_LEMA:
            continue
        lemas.append(lema)
    return lemas


def processar_redacao(texto, nlp):
    """
    Recebe o texto completo de uma redação e retorna lista de sentenças processadas.
    Cada sentença é uma lista de lemas filtrados.
    Descarta sentenças com menos de 2 lemas (sem informação útil).
    """
    doc = nlp(texto)
    sentencas = []
    for sent in doc.sents:
        lemas = processar_sentenca(sent, nlp)
        if len(lemas) >= 2:  # descarta sentenças vazias ou triviais
            sentencas.append(lemas)
    return sentencas


def ler_csv(caminho_csv):
    """
    Lê o CSV exportado do Google Sheets e retorna lista de dicionários.
    Colunas esperadas: source, year, title, grade, content
    """
    redacoes = []
    with open(caminho_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, linha in enumerate(reader):
            try:
                grade = int(linha["grade"])
            except (ValueError, KeyError):
                print(f"[AVISO] Linha {i+2}: nota inválida, pulando.")
                continue

            conteudo = linha.get("content", "").strip()
            if not conteudo:
                print(f"[AVISO] Linha {i+2}: texto vazio, pulando.")
                continue

            redacoes.append({
                "id": i,
                "source": linha.get("source", ""),
                "year": linha.get("year", ""),
                "title": linha.get("title", ""),
                "grade": grade,
                "content": conteudo,
            })

    print(f"[OK] {len(redacoes)} redações carregadas do CSV.")
    return redacoes


def separar_grupos(redacoes):
    """
    Separa as redações em dois grupos:
    - Grupo A: nota == 1000
    - Grupo B: nota < 1000
    """
    grupo_a = [r for r in redacoes if r["grade"] == NOTA_CORTE]
    grupo_b = [r for r in redacoes if r["grade"] < NOTA_CORTE]
    print(f"[OK] Grupo A (nota 1000): {len(grupo_a)} redações")
    print(f"[OK] Grupo B (nota < 1000): {len(grupo_b)} redações")
    return grupo_a, grupo_b


def processar_grupo(grupo, nlp, nome_grupo):
    """
    Aplica o pipeline spaCy em todas as redações de um grupo.
    Retorna lista de dicionários com metadados + sentenças processadas.
    """
    resultado = []
    for i, redacao in enumerate(grupo):
        print(f"  [{nome_grupo}] Processando {i+1}/{len(grupo)}: {redacao['title'][:50]}...")
        sentencas = processar_redacao(redacao["content"], nlp)
        resultado.append({
            "id": redacao["id"],
            "source": redacao["source"],
            "year": redacao["year"],
            "title": redacao["title"],
            "grade": redacao["grade"],
            "sentencas": sentencas,           # lista de listas de lemas
            "total_sentencas": len(sentencas),
            "total_lemas": sum(len(s) for s in sentencas),
        })
    return resultado


def salvar_json(dados, caminho):
    """Salva os dados processados em JSON formatado."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"[OK] Salvo em: {caminho}")


def imprimir_estatisticas(grupo_processado, nome):
    """Imprime estatísticas básicas após processamento."""
    total_sent = sum(r["total_sentencas"] for r in grupo_processado)
    total_lemas = sum(r["total_lemas"] for r in grupo_processado)
    media_sent = total_sent / len(grupo_processado) if grupo_processado else 0
    media_lemas = total_lemas / len(grupo_processado) if grupo_processado else 0

    # Vocabulário único do grupo
    todos_lemas = set()
    for r in grupo_processado:
        for sent in r["sentencas"]:
            todos_lemas.update(sent)

    print(f"\n── Estatísticas {nome} ──────────────────────────")
    print(f"  Redações:             {len(grupo_processado)}")
    print(f"  Total de sentenças:   {total_sent}")
    print(f"  Média sent./redação:  {media_sent:.1f}")
    print(f"  Total de lemas:       {total_lemas}")
    print(f"  Média lemas/redação:  {media_lemas:.1f}")
    print(f"  Vocabulário único:    {len(todos_lemas)} palavras")

def main():
    parser = argparse.ArgumentParser(description="Pré-processamento das redações do ENEM")
    parser.add_argument("--input",  default="redacoes.csv",       help="Caminho para o CSV de entrada")
    parser.add_argument("--output", default="data/processed/",    help="Pasta para salvar os JSONs")
    args = parser.parse_args()

    print("=" * 55)
    print("  PRÉ-PROCESSAMENTO — Redações ENEM")
    print("=" * 55)

    #Carregar modelo spaCy
    nlp = carregar_modelo_spacy()

    #Ler CSV
    redacoes = ler_csv(args.input)

    #Separar grupos
    grupo_a, grupo_b = separar_grupos(redacoes)

    #Processar com spaCy
    print("\nProcessando Grupo A (nota 1000)...")
    grupo_a_processado = processar_grupo(grupo_a, nlp, "A")

    print("\nProcessando Grupo B (nota < 1000)...")
    grupo_b_processado = processar_grupo(grupo_b, nlp, "B")

    #Salvar JSONs
    print("\nSalvando resultados...")
    salvar_json(grupo_a_processado, os.path.join(args.output, "corpus_nota1000.json"))
    salvar_json(grupo_b_processado, os.path.join(args.output, "corpus_abaixo1000.json"))

    #Estatísticas
    imprimir_estatisticas(grupo_a_processado, "Grupo A — Nota 1000")
    imprimir_estatisticas(grupo_b_processado, "Grupo B — Nota < 1000")

    print("\n[CONCLUÍDO] Pré-processamento finalizado com sucesso.")
    print(f"  Arquivos gerados em: {args.output}")


if __name__ == "__main__":
    main()