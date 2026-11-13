# -*- coding: utf-8 -*-
"""
Dados que não mudam mais, gerados uma vez e guardados em coletor/estatico.json:

1. Votos de cada vereador na eleição de 2024 — resultado oficial do TSE
   (resultados.tse.jus.br, município 62510 = Bragança Paulista, cargo 13 = vereador).
2. Propostas apresentadas na legislatura anterior (2021–2024), com a mesma regra de grupos
   usada no site, para comparar com o mandato atual. Presença e votos da legislatura anterior
   não existem no sistema da Câmara (o voto por nome só começou a ser registrado em 2026).

Uso: python coletor/estatico.py   (o robô diário só lê o arquivo gerado)
"""
import json, os, re, sys, unicodedata, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coletar as C

SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "estatico.json")
TSE = "https://resultados.tse.jus.br/oficial/ele2024/619/dados/sp/sp62510-c0013-e000619-u.json"


def n(s):
    s = unicodedata.normalize("NFD", s or "")
    return re.sub(r"\s+", " ", "".join(c for c in s if unicodedata.category(c) != "Mn").upper()).strip()


def main():
    V = C.coletar_vereadores()
    out = {"fonte_tse": TSE, "v": {}}

    print("TSE 2024…")
    d = json.loads(C.baixar(TSE))
    cands = []
    def walk(o):
        if isinstance(o, dict):
            if "nm" in o and "vap" in o:
                cands.append(o)
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(d)
    por_nome = {n(c["nm"]): c for c in cands}
    for v in V:
        c = por_nome.get(n(v["NOME"]))
        out["v"][str(v["sid"])] = {"votos": int(c["vap"]) if c else None, "sit": c["st"] if c else None}
        print(f"   {v['ap']}: {c['vap'] if c else '?'} votos")

    print("Legislatura 2021–2024…")
    for v in V:
        cat = {k: 0 for k in "bchlo"}
        tot = 0
        for g in (1, 3):
            for ano in range(2021, 2025):
                for r in C.csv_docs({"Pesquisa": "Avancada", "ShowSearch": "False", "GrupoId": g, "Numeracao": "Documento",
                                     "Ano": ano, "TipoAutorId": 1, "AutorId": v["sid"], "Ordenacao": 2}):
                    cat[C.classificar({"txt": re.sub(r"\s+", " ", r["Ementa"]), "tipo": r["Tipo"]})] += 1
                    tot += 1
        out["v"][str(v["sid"])]["ant"] = {"cat": cat, "tot": tot}
        print(f"   {v['ap']}: {tot} propostas em 2021–2024")

    json.dump(out, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Pronto:", SAIDA)


if __name__ == "__main__":
    main()
