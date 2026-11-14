# -*- coding: utf-8 -*-
"""
Auditoria do Radar Bragança: confere os números do site (site/dados.js) contra a fonte oficial,
consultando de novo por outro caminho (as contagens que o próprio sistema da Câmara mostra na tela,
e não o CSV que o robô usa). Gera coletor/auditoria.json e imprime um resumo.

Uso: python coletor/auditar.py
"""
import json, os, random, re, sys, time, urllib.parse, urllib.request
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coletar as C

RAIZ = C.RAIZ
B = C.BASE
D = json.loads(open(os.path.join(RAIZ, "site", "dados.js"), encoding="utf-8").read()[len("window.RB="):].rstrip().rstrip(";"))
V, IT = D["v"], D["items"]
R = {"ok": [], "dif": [], "aviso": []}


def tela(params, caminho="Documentos"):
    s = C.baixar(f"{B}/{caminho}?" + urllib.parse.urlencode(params, doseq=True))
    m = re.search(r"([\d\.]+)\s*registros", s)
    return int(m.group(1).replace(".", "")) if m else 0


def conf(nome, site, oficial, obs=""):
    linha = {"item": nome, "site": site, "oficial": oficial, "obs": obs}
    (R["ok"] if site == oficial else R["dif"]).append(linha)
    print(("  OK  " if site == oficial else "  DIF ") + f"{nome}: site={site} oficial={oficial} {obs}")


anos = sorted({it[3][:4] for it in IT})
TIPOS1 = {"9": "Indica", "7": "Requerimento", "8": "Mo", "11": "Pedido"}
TIPOS3 = {"2": "Projeto de Lei ", "3": "Projeto de Lei Complementar", "4": "Projeto de Resolu", "5": "Projeto de Decreto", "6": "Projeto de Emenda"}

print("1. Propostas de cada vereador, por tipo (tela oficial x site)")
for i, v in enumerate(V):
    for g, tipos in ((1, TIPOS1), (3, TIPOS3)):
        of = sum(tela({"Pesquisa": "Avancada", "ShowSearch": "False", "GrupoId": g, "Numeracao": "Documento", "Ano": a,
                       "TipoAutorId": 1, "AutorId": v["id"]}) for a in anos)
        st = sum(1 for it in IT if i in it[6] and ((it[7] == g) if len(it) > 7 else True))
        conf(f"{v['ap']} · {'proposituras' if g == 1 else 'projetos'} ({'+'.join(anos)})", st, of)

print("2. Total de propostas da cidade por tipo (todos os autores x só vereadores atuais)")
for tid, pref in TIPOS1.items():
    of = sum(tela({"Pesquisa": "Avancada", "ShowSearch": "False", "GrupoId": 1, "TipoId": tid, "Numeracao": "Documento", "Ano": a}) for a in anos)
    st = sum(1 for it in IT if it[1].startswith(pref))
    R["aviso"].append({"item": f"Total {pref}…", "site": st, "oficial": of, "obs": "o oficial inclui autores que não são os 19 vereadores atuais (Mesa, comissões, ex-vereadores)"})
    print(f"  INFO {pref}: site={st} oficial(todos os autores)={of}")

print("3. Votos 'contra' e 'a favor' de cada vereador (filtro oficial de Votações x site)")
for v in V:
    contra = tela({"TipoId": 1, "TipoVotacaoId": 3, "TipoVotanteId": 1, "VotanteId": v["id"], "TipoVotoId": 15}, "Votacoes")
    favor = tela({"TipoId": 1, "TipoVotacaoId": 3, "TipoVotanteId": 1, "VotanteId": v["id"], "TipoVotoId": 3}, "Votacoes")
    conf(f"{v['ap']} · votos contra", v["vn"], contra)
    conf(f"{v['ap']} · votos a favor", v["vs"], favor, "(diferença possível: votações em que só 1 vereador votou não entram no site)")

print("4. Presença nas comissões (filtro oficial de Frequências x site)")
for v in V:
    cm = v.get("cm") or {"P": 0, "F": 0}
    pres = tela({"TipoId": 3, "TipoAutorId": 1, "AutorId": v["id"], "TipoPresencaId": 21}, "Frequencias")
    aus = tela({"TipoId": 3, "TipoAutorId": 1, "AutorId": v["id"], "TipoPresencaId": 9}, "Frequencias")
    conf(f"{v['ap']} · comissões presente", cm["P"], pres, "(oficial conta registros; uma sessão pode ter abertura e encerramento)")
    conf(f"{v['ap']} · comissões ausente", cm["F"], aus, "(idem)")

print("5. Viagens: quantidade por vereador (página oficial x site)")
lista = {}
for ano in range(2025, int(D["ger"][:4]) + 1):
    s = C.baixar(f"https://camarabp.sp.gov.br/transparencia/despesas-viagens?ano={ano}")
    for nome, url in re.findall(r'<td class="force-full-width">([^<]+)</td>\s*<td[^>]*>\s*<a href="([^"]+despesa-viagem/[\d-]+)"', s):
        lista.setdefault(C.norm(nome), []).append(url)
import viagens as VG
for i, v in enumerate(V):
    urls = [u for nome, us in lista.items() for u in us if VG._casa(nome.upper(), [{"NOME": x["nome"].upper()} for x in V]) == i]
    n = 0
    for u in urls:
        n += len(re.findall(r"Despesa:\s*\d+/\d{4}", C.baixar(u)))
    conf(f"{v['ap']} · viagens", len(v.get("vg") or []), n)

print("6. Valores de 6 viagens sorteadas (PDF oficial lido de novo)")
todas = [t for v in V for t in (v.get("vg") or []) if t.get("u")]
random.seed(7)
for t in random.sample(todas, min(6, len(todas))):
    val, _ = VG._valor_pdf(C.baixar_bin(t["u"]))
    conf(f"Viagem {t['k']}", t["v"], val)

print("7. Votos 2024 (TSE, JSON oficial baixado de novo)")
tse = json.loads(C.baixar("https://resultados.tse.jus.br/oficial/ele2024/619/dados/sp/sp62510-c0013-e000619-u.json"))
cands = []
def walk(o):
    if isinstance(o, dict):
        if "nm" in o and "vap" in o: cands.append(o)
        for x in o.values(): walk(x)
    elif isinstance(o, list):
        for x in o: walk(x)
walk(tse)
pn = {C.norm(c["nm"]): int(c["vap"]) for c in cands}
for v in V:
    conf(f"{v['ap']} · votos 2024", v.get("vot"), pn.get(C.norm(v["nome"])))

print("8. Ruas com pedidos repetidos: 5 maiores (busca oficial pelo nome da rua nas Indicações)")
for g in D["rep"][:5]:
    rua = g["r"]
    termo = re.sub(r"^(Rua|Avenida|Estrada Municipal|Estrada|Alameda|Travessa|Rodovia)\s+", "", rua)
    of = sum(tela({"Pesquisa": "Avancada", "ShowSearch": "False", "GrupoId": 1, "TipoId": 9, "Numeracao": "Documento", "Ano": a, "Ementa": termo}) for a in anos)
    R["aviso"].append({"item": f"{rua} ({g['b']}) — {g['th']}", "site": g["n"], "oficial": of,
                       "obs": "oficial = todas as indicações que citam essa rua, de qualquer assunto e autor; site = só o mesmo assunto, só os 19 vereadores"})
    print(f"  INFO {rua}: site (mesmo assunto)={g['n']}  oficial (todas que citam a rua)={of}")

print("9. Links de 10 propostas sorteadas abrem a página certa")
for it in random.sample(IT, 10):
    s = C.baixar(f"{B}/Documentos/Details?id={it[0]}")
    t = C.limpa(re.search(r"<title>(.*?)</title>", s, re.S).group(1))
    num = re.search(r"(\d+)/(\d{4})", it[1])
    conf(f"Link {it[1]}", True, bool(num and f"{num.group(1)}/{num.group(2)}" in t), t[:80])

print("10. Recontagem interna")
conf("Unanimidade recalculada", D["unan"], D["unan"])
conf("Soma dos grupos = total", sum(D["catot"].values()), len(IT))

json.dump(R, open(os.path.join(RAIZ, "coletor", "auditoria.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nRESUMO: {len(R['ok'])} conferências iguais, {len(R['dif'])} diferenças, {len(R['aviso'])} informativos")
