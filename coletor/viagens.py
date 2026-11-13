# -*- coding: utf-8 -*-
"""
Viagens oficiais dos vereadores (Portal da Transparência da Câmara, "Despesas de Viagens").

A página lista quem viajou em cada ano. O detalhe de cada pessoa traz destino e motivo de
cada viagem, e um PDF de prestação de contas com o valor. O valor é lido do PDF (biblioteca
pypdf). Cada PDF já lido fica guardado em coletor/cache_viagens.json, para o robô não
baixar tudo de novo toda madrugada.

Atenção ao que o valor significa (está escrito em cada PDF): é o adiantamento gasto na viagem
(alimentação, hospedagem etc.) de todos os participantes, inclusive motorista e servidores,
e NÃO inclui combustível e pedágio.
"""
import html, io, json, os, re, unicodedata
from datetime import date

SITE = "https://camarabp.sp.gov.br"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache_viagens.json")
DINHEIRO = re.compile(r"\d{1,3}(?:\.\d{3})*,\d{2}")


def _norm(s):
    s = unicodedata.normalize("NFD", s or "")
    return re.sub(r"\s+", " ", "".join(c for c in s if unicodedata.category(c) != "Mn").upper()).strip()


def _limpa(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def _casa(nome_viagem, V):
    """Liga o nome usado na página de viagens ao vereador (ex.: 'CLAUDIO CHAGAS' -> Claudio Manoel das Chagas)."""
    t = [p for p in _norm(nome_viagem).split() if p not in ("DA", "DE", "DO", "DOS", "DAS", "E")]
    for i, v in enumerate(V):
        vt = [p for p in _norm(v["NOME"]).split() if p not in ("DA", "DE", "DO", "DOS", "DAS", "E")]
        if t and t[0] == vt[0] and set(t) <= set(vt):
            return i
    return None


def _valor_pdf(dado):
    try:
        from pypdf import PdfReader
    except ImportError:
        return None, ""
    try:
        txt = "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(dado)).pages)
    except Exception:
        return None, ""
    vals = DINHEIRO.findall(txt)
    total = float(vals[-1].replace(".", "").replace(",", ".")) if vals else None
    m = re.search(r"\d{2}/\d{2}/\d{4}", txt)
    return total, (m.group(0) if m else "")


def coletar_viagens(V, baixar, baixar_bin):
    print("Viagens oficiais (Portal da Transparência)…")
    try:
        cache = json.load(open(CACHE, encoding="utf-8"))
    except Exception:
        cache = {}
    por_ver = {i: [] for i in range(len(V))}
    for ano in range(2025, date.today().year + 1):
        lista = baixar(f"{SITE}/transparencia/despesas-viagens?ano={ano}")
        pessoas = re.findall(r'<td class="force-full-width">([^<]+)</td>\s*<td[^>]*>\s*<a href="(https://camarabp\.sp\.gov\.br/transparencia/despesa-viagem/[\d-]+)"', lista)
        for nome, url in pessoas:
            i = _casa(nome, V)
            if i is None:
                continue
            s = baixar(url)
            if "VEREADOR" not in _norm(_limpa(s[:s.find("Despesa:")] if "Despesa:" in s else s)):
                continue
            for bloco in s.split('<div class="each">')[1:]:
                mnum = re.search(r"Despesa:\s*(\d+)/(\d{4})", bloco)
                if not mnum:
                    continue
                chave = f"{mnum.group(2)}-{mnum.group(1)}"
                destino = _limpa((re.search(r'<div class="destino">(.*?)</div>', bloco, re.S) or [None, ""])[1])
                motivo = _limpa((re.search(r'<div class="motivo">(.*?)</div>', bloco, re.S) or [None, ""])[1])
                doc = (re.search(r'href="(https://camarabp\.sp\.gov\.br/download/[^"]+)"', bloco) or [None, ""])[1]
                if chave not in cache or cache[chave].get("v") is None:
                    valor, data = (None, "")
                    if doc:
                        try:
                            valor, data = _valor_pdf(baixar_bin(doc))
                        except Exception as e:  # noqa
                            print("   PDF falhou:", chave, e)
                    cache[chave] = {"v": valor, "dt": data}
                c = cache[chave]
                if any(t["k"] == chave for t in por_ver[i]):
                    continue
                por_ver[i].append({"k": chave, "de": destino, "mo": motivo, "v": c["v"], "dt": c["dt"], "u": doc})
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=0, sort_keys=True)
    for i, lst in por_ver.items():
        lst.sort(key=lambda t: (t["dt"][6:] + t["dt"][3:5] + t["dt"][:2]) if t["dt"] else t["k"], reverse=True)
        V[i]["vg"] = lst
        V[i]["vgt"] = round(sum(t["v"] or 0 for t in lst), 2)
    tot = sum(len(l) for l in por_ver.values())
    print(f"   {tot} viagens de vereadores")
    return tot
