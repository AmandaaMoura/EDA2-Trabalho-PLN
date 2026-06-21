"""
Relatório do pipeline de podas nos grafos de coocorrência (saída no terminal).

Uso (a partir da pasta cliques-enem):
    python scripts/run_podas_report.py
    python scripts/run_podas_report.py --min-peso 2 --fator-media 0.3 --fator-max 0.15
    python scripts/run_podas_report.py --sem-pontes
"""

from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from graph import (  # noqa: E402
    FATOR_MAX,
    FATOR_MEDIA,
    MIN_PESO_ARESTA,
    aplicar_podas,
    carregar_corpus,
    construir_grafo_de_coocorrencia,
    estatisticas_pesos,
    poda_peso_absoluto,
)

CORPUS_A = os.path.join(ROOT, "data", "processed", "corpus_nota1000.json")
CORPUS_B = os.path.join(ROOT, "data", "processed", "corpus_abaixo1000.json")


def estatisticas_corpus(corpus):
    total_sent = sum(r.get("total_sentencas", 0) for r in corpus)
    total_lemas = sum(r.get("total_lemas", 0) for r in corpus)
    n = len(corpus)
    return {
        "redacoes": n,
        "sentencas": total_sent,
        "lemas": total_lemas,
        "media_sent_por_redacao": total_sent / n if n else 0,
        "media_lemas_por_redacao": total_lemas / n if n else 0,
    }


def distribuicao_pesos(grafo, top_n=5):
    pesos = estatisticas_pesos(grafo)
    if not pesos:
        return {"total": 0, "peso_1": 0, "pct_peso_1": 0.0, "top_pesos": []}

    freq: dict[int, int] = {}
    for p in pesos:
        freq[p] = freq.get(p, 0) + 1

    top = sorted(freq.items(), key=lambda x: (-x[1], -x[0]))[:top_n]
    n = len(pesos)
    p1 = freq.get(1, 0)
    return {
        "total": n,
        "peso_1": p1,
        "pct_peso_1": 100.0 * p1 / n,
        "top_pesos": top,
    }


def limiar_poda_relativa(grafo, fator_media, fator_max):
    pesos = estatisticas_pesos(grafo)
    if not pesos:
        return 0.0, 0.0, 0.0
    media = sum(pesos) / len(pesos)
    max_peso = max(pesos)
    limiar = max(fator_media * media, fator_max * max_peso)
    return limiar, media, max_peso


def top_grau(grafo, k=5):
    vertices = grafo.listar_vertices()
    ordenados = sorted(vertices, key=lambda v: grafo.grau(v), reverse=True)
    return [(v, grafo.grau(v)) for v in ordenados[:k]]


def delta_etapa(log, etapa_atual, etapa_anterior="bruto"):
    atual = next(e for e in log if e["etapa"] == etapa_atual)
    base = next(e for e in log if e["etapa"] == etapa_anterior)
    dv = base["vertices"] - atual["vertices"]
    da = base["arestas"] - atual["arestas"]
    pv = 100.0 * dv / base["vertices"] if base["vertices"] else 0
    pa = 100.0 * da / base["arestas"] if base["arestas"] else 0
    return {"vertices_removidos": dv, "arestas_removidas": da, "pct_vertices": pv, "pct_arestas": pa}


def processar_grupo(nome, caminho_json, args):
    corpus = carregar_corpus(caminho_json)
    info_corpus = estatisticas_corpus(corpus)

    grafo_bruto = construir_grafo_de_coocorrencia(corpus)
    dist = distribuicao_pesos(grafo_bruto)

    g_pos_abs = poda_peso_absoluto(grafo_bruto, args.min_peso)
    limiar, media_pos_abs, max_pos_abs = limiar_poda_relativa(
        g_pos_abs, args.fator_media, args.fator_max
    )

    grafo_final, log = aplicar_podas(
        grafo_bruto,
        min_peso=args.min_peso,
        fator_media=args.fator_media,
        fator_max=args.fator_max,
        usar_pontes=not args.sem_pontes,
        verbose=False,
    )

    reducao_final = delta_etapa(log, log[-1]["etapa"], "bruto")
    deltas = {}
    for i in range(1, len(log)):
        deltas[log[i]["etapa"]] = delta_etapa(log, log[i]["etapa"], log[i - 1]["etapa"])

    return {
        "nome": nome,
        "caminho": caminho_json,
        "corpus": info_corpus,
        "distribuicao_bruto": dist,
        "limiar_relativo": limiar,
        "media_pos_absoluta": media_pos_abs,
        "max_pos_absoluta": max_pos_abs,
        "log": log,
        "deltas_sequenciais": deltas,
        "reducao_final": reducao_final,
        "top_grau_final": top_grau(grafo_final, k=5),
    }


def fmt_int(n):
    return f"{n:,}".replace(",", ".")


def fmt_float(x, casas=2):
    return f"{x:.{casas}f}".replace(".", ",")


def imprimir_parametros(args):
    print("Parâmetros:")
    print(f"  MIN_PESO_ARESTA = {args.min_peso}")
    print(f"  FATOR_MEDIA     = {args.fator_media}")
    print(f"  FATOR_MAX       = {args.fator_max}")
    print(f"  Poda de pontes  = {'não' if args.sem_pontes else 'sim'}")


def imprimir_grupo(rel, args):
    c = rel["corpus"]
    d = rel["distribuicao_bruto"]

    print(f"\n{'=' * 60}")
    print(f"  {rel['nome']}")
    print(f"{'=' * 60}")
    print(f"  Arquivo: {os.path.relpath(rel['caminho'], ROOT)}")

    print("\n  Corpus:")
    print(f"    Redações:            {c['redacoes']}")
    print(f"    Sentenças:           {fmt_int(c['sentencas'])}")
    print(f"    Lema total:          {fmt_int(c['lemas'])}")
    print(f"    Média sent./redação: {fmt_float(c['media_sent_por_redacao'])}")
    print(f"    Média lemas/redação: {fmt_float(c['media_lemas_por_redacao'])}")

    print("\n  Grafo bruto — distribuição de pesos:")
    print(f"    Arestas totais:      {fmt_int(d['total'])}")
    print(f"    Arestas peso 1:      {fmt_int(d['peso_1'])} ({fmt_float(d['pct_peso_1'])}%)")
    print("    Pesos mais frequentes:")
    for peso, qtd in d["top_pesos"]:
        print(f"      peso {peso} → {fmt_int(qtd)} arestas")

    print(f"\n  Limiar poda relativa (após absoluta, min_peso={args.min_peso}):")
    print(f"    Média de pesos:      {fmt_float(rel['media_pos_absoluta'])}")
    print(f"    Peso máximo:         {rel['max_pos_absoluta']}")
    print(
        f"    Limiar:              {fmt_float(rel['limiar_relativo'])} "
        f"(max({args.fator_media}×média, {args.fator_max}×max))"
    )

    print("\n  Pipeline de podas:")
    print(f"    {'Etapa':<16} {'Vértices':>8} {'Arestas':>10} {'Peso méd.':>10} {'Peso máx.':>10}")
    print(f"    {'-' * 16} {'-' * 8} {'-' * 10} {'-' * 10} {'-' * 10}")
    for entry in rel["log"]:
        print(
            f"    {entry['etapa']:<16} "
            f"{entry['vertices']:>8} "
            f"{entry['arestas']:>10} "
            f"{fmt_float(entry['peso_medio']):>10} "
            f"{entry['peso_max']:>10}"
        )
        if entry["etapa"] == "poda_pontes" and "pontes_removidas" in entry:
            print(f"      → pontes removidas: {entry['pontes_removidas']}")

    print("\n  Redução por etapa (vs. etapa anterior):")
    for etapa, delta in rel["deltas_sequenciais"].items():
        print(
            f"    {etapa}: "
            f"-{delta['vertices_removidos']} vértices ({fmt_float(delta['pct_vertices'])}%), "
            f"-{fmt_int(delta['arestas_removidas'])} arestas ({fmt_float(delta['pct_arestas'])}%)"
        )

    rf = rel["reducao_final"]
    print("\n  Redução total (bruto → final):")
    print(
        f"    {fmt_int(rf['arestas_removidas'])} arestas ({fmt_float(rf['pct_arestas'])}%), "
        f"{fmt_int(rf['vertices_removidos'])} vértices ({fmt_float(rf['pct_vertices'])}%)"
    )

    print("\n  Top 5 lemas por grau (grafo final):")
    for lema, grau in rel["top_grau_final"]:
        print(f"    {lema:<20} grau {grau}")


def imprimir_comparativo(relatorios):
    if len(relatorios) != 2:
        return

    a, b = relatorios[0]["log"][-1], relatorios[1]["log"][-1]
    ca, cb = relatorios[0]["corpus"], relatorios[1]["corpus"]

    print(f"\n{'=' * 60}")
    print("  Comparativo A vs B (grafo final)")
    print(f"{'=' * 60}")
    print(f"    {'Métrica':<20} {'Grupo A':>12} {'Grupo B':>12}")
    print(f"    {'-' * 20} {'-' * 12} {'-' * 12}")
    print(f"    {'Vértices':<20} {a['vertices']:>12} {b['vertices']:>12}")
    print(f"    {'Arestas':<20} {a['arestas']:>12} {b['arestas']:>12}")
    print(f"    {'Peso médio':<20} {fmt_float(a['peso_medio']):>12} {fmt_float(b['peso_medio']):>12}")
    print(f"    {'Peso máx.':<20} {a['peso_max']:>12} {b['peso_max']:>12}")
    print(
        f"    {'Lema/redação':<20} "
        f"{fmt_float(ca['media_lemas_por_redacao']):>12} "
        f"{fmt_float(cb['media_lemas_por_redacao']):>12}"
    )


def imprimir_relatorio(relatorios, args):
    print("=" * 60)
    print("  RELATÓRIO DE PODAS — Grafos de Coocorrência")
    print("=" * 60)
    print()
    imprimir_parametros(args)
    for rel in relatorios:
        imprimir_grupo(rel, args)
    imprimir_comparativo(relatorios)
    print()


def main():
    parser = argparse.ArgumentParser(description="Relatório do pipeline de podas (terminal)")
    parser.add_argument("--min-peso", type=int, default=MIN_PESO_ARESTA)
    parser.add_argument("--fator-media", type=float, default=FATOR_MEDIA)
    parser.add_argument("--fator-max", type=float, default=FATOR_MAX)
    parser.add_argument("--sem-pontes", action="store_true", help="Não aplicar poda de pontes")
    args = parser.parse_args()

    for path in (CORPUS_A, CORPUS_B):
        if not os.path.isfile(path):
            print(f"[ERRO] Arquivo não encontrado: {path}")
            print("       Rode o pré-processamento antes ou execute de cliques-enem/")
            sys.exit(1)

    relatorios = [
        processar_grupo("Grupo A — Nota 1000", CORPUS_A, args),
        processar_grupo("Grupo B — Nota < 1000", CORPUS_B, args),
    ]

    imprimir_relatorio(relatorios, args)


if __name__ == "__main__":
    main()
