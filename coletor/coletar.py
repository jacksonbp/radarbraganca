# -*- coding: utf-8 -*-
"""
Robô do Radar Bragança.

Vai ao sistema oficial da Câmara Municipal de Bragança Paulista (SISCAM,
braganca.siscam.com.br) e ao site da Câmara (camarabp.sp.gov.br), baixa:
  - a lista de vereadores em exercício (nome, apelido, partido, cargo, foto, e-mail oficial);
  - todas as proposituras e projetos de cada vereador desde a posse (01/01/2025);
  - todas as votações nominais do plenário (quem votou sim, não, se absteve ou estava ausente);
e grava tudo em site/dados.js, que a página lê.

Só usa a biblioteca padrão do Python. Coleta devagar (pausa entre pedidos)
e se identifica, para não pesar no servidor da Câmara.

Uso:  python coletor/coletar.py
Se a coleta vier incompleta ou estranha, o robô para com erro e NÃO
sobrescreve os dados antigos: o site continua com a última versão boa.
"""
import csv, html, io, json, os, re, sys, time, unicodedata, urllib.parse, urllib.request
from collections import Counter, defaultdict
from datetime import datetime, date, timezone, timedelta

BASE = "https://braganca.siscam.com.br"
SITE_CAMARA = "https://camarabp.sp.gov.br"
POSSE = "2025-01-01"
UA = "Mozilla/5.0 (compatible; RadarBraganca/1.0; projeto civico de transparencia; coleta lenta 1 pedido a cada 1,5s)"
PAUSA = 1.5
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "site", "dados.js")
FOTOS = os.path.join(RAIZ, "site", "fotos")

# Salário: Resolução nº 2/2024 (altera a Resolução nº 3/2023), publicada na Imprensa Oficial em 25/04/2024, pág. 10.
# O valor abaixo foi divulgado pela imprensa local sobre essa resolução. CONFIRA no texto oficial e ajuste se preciso.
SALARIO = {"v": 15147.29, "lei": "Resolução nº 2/2024",
           "u": BASE + "/Documentos/Details?id=221758&grupoId=2", "confirmado": False}

BRT = timezone(timedelta(hours=-3))
_ultimo = [0.0]


def baixar(url, tentativas=4):
    for t in range(tentativas):
        espera = PAUSA - (time.time() - _ultimo[0])
        if espera > 0:
            time.sleep(espera)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR"})
            with urllib.request.urlopen(req, timeout=180) as r:
                dado = r.read()
            _ultimo[0] = time.time()
            texto = dado.decode("utf-8-sig", "replace")
            if "System.InvalidOperationException" in texto[:300]:
                raise IOError("erro interno do servidor da Câmara")
            return texto
        except Exception as e:  # noqa
            _ultimo[0] = time.time()
            print(f"  ! falhou ({e}); tentando de novo em {5 * (t + 1)}s", file=sys.stderr)
            time.sleep(5 * (t + 1))
    raise SystemExit(f"Não consegui baixar: {url}")


def baixar_bin(url):
    time.sleep(PAUSA)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def reduzir_foto(dado, lado=240):
    """Corta as bordas vazias, pega um quadrado na parte de cima (rosto) e salva um JPEG pequeno.
    Precisa da biblioteca Pillow; sem ela, guarda a foto original."""
    try:
        from PIL import Image
    except ImportError:
        return dado
    im = Image.open(io.BytesIO(dado))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        caixa = im.getchannel("A").getbbox()
        if caixa:
            im = im.crop(caixa)
        fundo = Image.new("RGB", im.size, (255, 255, 255))
        fundo.paste(im, mask=im.getchannel("A"))
        im = fundo
    else:
        im = im.convert("RGB")
    w, h = im.size
    q = min(w, h)
    topo = 0 if h > w else 0
    esq = (w - q) // 2
    im = im.crop((esq, topo, esq + q, topo + q)).resize((lado, lado), Image.LANCZOS)
    saida = io.BytesIO()
    im.save(saida, "JPEG", quality=82, optimize=True)
    return saida.getvalue()


def limpa(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def norm(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s.lower()).strip()


def campo(bloco, rotulo):
    m = re.search(r"<strong>\s*" + rotulo + r"\s*:?\s*</strong>(.*?)</(?:p|div)>", bloco, re.S)
    return limpa(m.group(1)) if m else ""


def data_br(s):  # "22/09/2026" -> "2026-09-22"
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", s or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""


def data_csv(s):  # o CSV do SISCAM usa mês/dia/ano: "01/07/2025 00:00:00" = 7 de janeiro
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", s or "")
    return f"{m.group(3)}{m.group(1)}{m.group(2)}" if m else ""


# ---------------------------------------------------------------- vereadores
def bonito(s):
    s = re.sub(r"\s+", " ", s).strip().title()
    return re.sub(r"\b(Da|De|Do|Dos|Das|E)\b", lambda m: m.group(1).lower(), s)


def coletar_vereadores():
    print("1/5 Vereadores em exercício…")
    s = baixar(BASE + "/Autores?ShowSearch=True&TipoId=1&Ativo=True&ItemsPerPage=50")
    V = []
    for m in re.finditer(r'<a href="/Autores/Details\?id=(\d+)">(.*?)</a>(.*?)(?=<a href="/Autores/Details|<nav|<footer)', s, re.S):
        sid, nome, resto = m.group(1), limpa(m.group(2)), m.group(3)
        V.append({"sid": int(sid), "nome": bonito(nome),
                  "NOME": nome, "part": campo(resto, "Partido"), "mesa": campo(resto, "Cargo")})
    for v in V:
        t = limpa(re.search(r"<title>(.*?)</title>", baixar(f"{BASE}/Autores/Details?id={v['sid']}"), re.S).group(1))
        m = re.search(r"\(([^)]+)\)\s*-", t)
        v["ap"] = bonito((m.group(1) if m else v["NOME"]).strip())
        v["url"] = f"{BASE}/Autores/Details?id={v['sid']}"
    # site da Câmara: foto e e-mail oficial
    lista = baixar(SITE_CAMARA + "/vereadores")
    paginas = sorted(set(re.findall(r'href="(https://camarabp\.sp\.gov\.br/vereador/\d+/[\w-]+)"', lista)))
    os.makedirs(FOTOS, exist_ok=True)
    for p in paginas:
        s = baixar(p)
        t = limpa(re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S))
        mn = re.search(r"Perfil Nome (.+?) Partido", t)
        if not mn:
            continue
        alvo = norm(mn.group(1))
        v = next((x for x in V if norm(x["NOME"]) == alvo), None) or \
            next((x for x in V if norm(x["NOME"]).split()[0] == alvo.split()[0] and norm(x["NOME"]).split()[-1] == alvo.split()[-1]), None)
        if not v:
            print("  (sem correspondência no SISCAM:", mn.group(1), ")")
            continue
        v["ficha"] = p
        me = re.search(r"[\w.+-]+@camarabp\.sp\.gov\.br", t)
        if me:
            v["email"] = me.group(0)
        mf = re.search(r'src="(https://camarabp\.sp\.gov\.br/files/vereador/[^"]+)"', s)
        if mf:
            try:
                open(os.path.join(FOTOS, f"{v['sid']}.jpg"), "wb").write(reduzir_foto(baixar_bin(mf.group(1))))
                v["foto"] = 1
            except Exception as e:  # noqa
                print("  foto falhou:", e)
    V.sort(key=lambda v: norm(v["ap"]))
    for i, v in enumerate(V):
        v["id"] = v["sid"]
    print(f"   {len(V)} vereadores")
    return V


# ---------------------------------------------------------------- proposituras e projetos
GRUPOS = {1: "Proposituras", 3: "Projetos"}


def csv_docs(params):
    url = BASE + "/Documentos?" + urllib.parse.urlencode(params, doseq=True) + "&Export=Csv"
    texto = baixar(url)
    if not texto.lstrip().startswith("Id,"):
        raise SystemExit("Resposta inesperada do CSV: " + url)
    return list(csv.DictReader(io.StringIO(texto)))


def coletar_documentos(V):
    print("2/5 Proposituras e projetos de cada vereador (isso demora alguns minutos)…")
    anos = list(range(2025, date.today().year + 1))
    docs = {}
    for i, v in enumerate(V):
        for g in GRUPOS:
            for ano in anos:
                linhas = csv_docs({"Pesquisa": "Avancada", "ShowSearch": "False", "GrupoId": g, "Numeracao": "Documento",
                                   "Ano": ano, "TipoAutorId": 1, "AutorId": v["sid"], "Ordenacao": 2})
                for r in linhas:
                    d = data_csv(r["Data"])
                    if d < POSSE.replace("-", ""):
                        continue
                    doc = docs.setdefault(int(r["Id"]), {"id": int(r["Id"]), "tipo": r["Tipo"].strip(), "cod": r["DescricaoCompleta"].strip(),
                                                         "num": r["Numero"], "ano": r["Ano"], "data": d,
                                                         "txt": re.sub(r"\s+", " ", r["Ementa"]).strip(), "aut": [], "g": g})
                    if i not in doc["aut"]:
                        doc["aut"].append(i)
        print(f"   {v['ap']}: ok ({len(docs)} documentos até aqui)")
    # situação dos projetos (aprovado, rejeitado…)
    situ = {9: "Aprovado", 78: "Rejeitado", 96: "Vetado", 15: "Arquivado", 66: "Prejudicado"}
    for sid_, nome in situ.items():
        for ano in anos:
            for r in csv_docs({"Pesquisa": "Avancada", "ShowSearch": "False", "GrupoId": 3, "Numeracao": "Documento",
                               "Ano": ano, "SituacaoId": sid_, "Ordenacao": 2}):
                if int(r["Id"]) in docs:
                    docs[int(r["Id"])]["res"] = nome
    return docs


# ---------------------------------------------------------------- classificação
def classificar(doc):
    """Mesma regra para todos. Devolve o grupo: b pedido no bairro, c pergunta/cobrança, h homenagem, l lei, o outros."""
    t, tipo = norm(doc["txt"]), norm(doc["tipo"])
    homen = re.search(r"congratula|aplauso|parabeniz|parabens|louvor|homenag|pesar|falecimento|condolenc|titulo de cidadao|cidadao bragantino|cidada bragantina|cidadania bragantina|"
                      r"medalha|diploma|honra ao merito|denomina|da nome|da denominacao|institui o dia|institui a semana|institui o mes|dia municipal|semana municipal|calendario oficial|data comemorativa|reconhecimento", t)
    if tipo.startswith("indicac"):
        return "b"
    if tipo.startswith("pedido de informac"):
        return "c"
    if tipo.startswith("requerimento"):
        return "h" if homen else "c"
    if tipo.startswith("moc"):
        if re.search(r"\bapelo\b", t):
            return "c"
        return "h" if homen else "o"
    if tipo.startswith("projeto de resoluc"):
        return "h" if homen else "o"
    if tipo.startswith("projeto"):
        return "h" if homen else "l"
    return "o"


TEMAS = [  # assunto do pedido, pelas palavras do texto oficial (ordem importa)
    ("luz", r"iluminac|lampada|luminaria|poste|\bled\b"),
    ("asf", r"tapa[- ]buraco|buraco|asfalt|recape|pavimenta|cascalh|patrolamento|nivelamento"),
    ("tra", r"sinalizac|lombada|transito|semaforo|faixa de pedestre|redutor de velocidade|rotatoria|estacionamento|placa|radar"),
    ("agu", r"esgoto|vazamento|drenagem|alagamento|enchente|\bagua\b|bueiro|boca de lobo|galeria|sabesp|erosao"),
    ("lim", r"rocag|limpeza|capina|poda|\bmato\b|entulho|cata[- ]treco|arvore|descarte|lixo|coleta"),
    ("cal", r"calcada|passeio publico|sarjet|meio[- ]fio|guia"),
    ("laz", r"praca|playground|academia ao ar livre|parque|quadra|campo de futebol|area de lazer|ciles"),
    ("sau", r"\bubs\b|saude|medic|hospital|\bupa\b|dengue|vacina|santa casa|caps\b"),
    ("edu", r"escola|emef|emeb|creche|aluno|educac"),
    ("seg", r"seguranca|guarda civil|guarda municipal|ronda|camera|policia|monitoramento"),
    ("bus", r"onibus|transporte publico|transporte coletivo|ponto de parada|abrigo"),
]
TEMAS_H = [
    ("pes", r"pesar|falecimento|condolenc"),
    ("tit", r"titulo|medalha|diploma|honra ao merito|cidadao bragantino|cidada bragantina"),
    ("nom", r"denomina|da nome"),
    ("dat", r"institui o dia|institui a semana|institui o mes|dia municipal|semana municipal|calendario|data comemorativa"),
    ("par", r"."),
]


def tema(doc, g):
    t = norm(doc["txt"])
    for k, rx in (TEMAS_H if g == "h" else TEMAS):
        if re.search(rx, t):
            return k
    return ""


LOGR = r"(?:Rua|Avenida|Av\.|Alameda|Travessa|Estrada Municipal|Estrada|Rodovia|Pra[cç]a|Viela|Largo|Via|Vicinal)"


def endereco(txt):
    """Tenta achar 'Rua X - Bairro Y' na ementa. Devolve (rua, bairro) ou (None, None)."""
    m = re.search(r"(" + LOGR + r"\s+[^,;\-–(]+?)(?:,?\s*(?:n[º°o.]?\s*)?\d+[^\-–]*?)?\s*[-–]\s*([A-ZÁÉÍÓÚÂÊÔÃÕÇ][^.;,()]{2,60})", txt)
    if not m:
        return None, None
    rua = re.sub(r"\s+", " ", m.group(1)).strip().rstrip(".")
    rua = re.sub(r"^Av\.\s*", "Avenida ", rua)
    rua = re.sub(r"\s*\)+\s*$", "", rua).strip(" .,")  # tira parêntese solto no fim ("Rua 2)")
    if rua.count("(") > rua.count(")"):
        rua = rua.split("(")[0].strip()
    bairro = re.sub(r"\s+", " ", m.group(2)).strip().rstrip(".")
    bairro = re.split(r"\s+(?:e|em|no|na|para|com|entre)\s+", bairro)[0]
    if len(bairro) < 3 or re.match(r"(?i)(rua|avenida|altura|esquina|pr[oó]ximo)", bairro):
        bairro = None
    return rua, bairro


# ---------------------------------------------------------------- votações e presença
def chave_nome(s):
    s = re.sub(r"\s*\(.*?\)\s*", " ", s)
    return norm(s)


def coletar_votacoes(V):
    print("3/5 Votações nominais do plenário…")
    por_nome = {chave_nome(v["NOME"]): i for i, v in enumerate(V)}
    votos, pagina = [], 1
    while True:
        s = baixar(f"{BASE}/Votacoes?TipoId=1&TipoVotacaoId=3&ItemsPerPage=100&CurrentPage={pagina}")
        itens = s.split('<div class="data-list-item">')[1:]
        if not itens:
            break
        velho = False
        for it in itens:
            mid = re.search(r'/Votacoes/Details\?id=(\d+)">(.*?)</a>', it, re.S)
            mr = re.search(r'/Reunioes/Details\?id=(\d+)">(.*?)</a>', it, re.S)
            datas = re.findall(r"<strong>Data:</strong>\s*([\d/]+)", it)
            d = data_br(datas[-1]) if datas else ""
            if d and d < POSSE:
                velho = True
                continue
            grupos = {}
            for rot, nomes in re.findall(r"<strong>([^<]+?)\s*\(\d+\):</strong>(.*?)</p>", it, re.S):
                rot = norm(limpa(rot))
                for nm in re.split(r",\s*(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])", limpa(nomes)):
                    k = chave_nome(nm)
                    if k in por_nome:
                        grupos[por_nome[k]] = rot
            votos.append({"id": int(mid.group(1)), "t": limpa(mid.group(2)), "sess": int(mr.group(1)) if mr else 0,
                          "sn": limpa(mr.group(2)) if mr else "", "d": d, "e": campo(it, "Ementa"),
                          "a": campo(it, "Autor"), "r": campo(it, "Resultado"), "v": grupos})
        print(f"   página {pagina}: {len(votos)} votações desde a posse")
        if velho:
            break
        pagina += 1
    return votos


def coletar_justificadas(V):
    """Ausências justificadas / licenças registradas em Frequências das sessões plenárias."""
    print("4/5 Ausências justificadas…")
    por_nome = {chave_nome(v["NOME"]): i for i, v in enumerate(V)}
    just = defaultdict(set)  # sessao -> {vereador}
    for tipo in (6, 12):
        pagina = 1
        while True:
            s = baixar(f"{BASE}/Frequencias?TipoId=1&TipoPresencaId={tipo}&ItemsPerPage=100&CurrentPage={pagina}")
            itens = s.split('<div class="data-list-item">')[1:]
            if not itens:
                break
            for it in itens:
                mr = re.search(r'/Reunioes/Details\?id=(\d+)', it)
                for rot, nomes in re.findall(r"<strong>([^<]+?)\s*\(\d+\):</strong>(.*?)</p>", it, re.S):
                    if re.search(r"justificad|licen", norm(rot)) and mr:
                        for nm in re.split(r",\s*(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])", limpa(nomes)):
                            if chave_nome(nm) in por_nome:
                                just[int(mr.group(1))].add(por_nome[chave_nome(nm)])
            if len(itens) < 100:
                break
            pagina += 1
    return just


COMISSOES = {"CFO": "Finanças e Orçamento", "CJR": "Justiça e Redação", "CEC": "Educação e Cultura", "CAS": "Socioeconômica"}


def coletar_comissoes(V):
    """Presença nas sessões das comissões (Frequências, tipo 'Sessões das Comissões').
    Por sessão: presente se aparece como presente em algum momento; ausência justificada/licença
    conta à parte; falta se só aparece como ausente. Só conta quem é membro (aparece na lista)."""
    print("Presença nas comissões…")
    por_nome = {chave_nome(v["NOME"]): i for i, v in enumerate(V)}
    sess = defaultdict(lambda: defaultdict(set))  # reuniao -> vereador -> {estados}
    info = {}
    pagina = 1
    while True:
        s = baixar(f"{BASE}/Frequencias?TipoId=3&ItemsPerPage=100&CurrentPage={pagina}")
        itens = s.split('<div class="data-list-item">')[1:]
        if not itens:
            break
        for it in itens:
            mr = re.search(r'/Reunioes/Details\?id=(\d+)">(.*?)</a>', it, re.S)
            datas = re.findall(r"<strong>Data:</strong>\s*([\d/]+)", it)
            if not mr or not datas or data_br(datas[-1]) < POSSE:
                continue
            rid = int(mr.group(1))
            ms = re.search(r"Comiss[ãa]o\s+([A-Z]{2,5})", limpa(mr.group(2)))
            info[rid] = (ms.group(1) if ms else "?", data_br(datas[-1]))
            for rot, nomes in re.findall(r"<strong>([^<]+?)\s*\(\d+\):</strong>(.*?)</p>", it, re.S):
                r = norm(limpa(rot))
                est = "A" if re.search(r"justificad|licen", r) else ("P" if r.startswith("presen") else "F")
                for nm in re.split(r",\s*(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])", limpa(nomes)):
                    k = chave_nome(nm)
                    if k in por_nome:
                        sess[rid][por_nome[k]].add(est)
        if len(itens) < 100:
            break
        pagina += 1
    for v in V:
        v["cm"] = {"P": 0, "A": 0, "F": 0, "por": {}}
    for rid, regs in sess.items():
        sig = info[rid][0]
        for i, ests in regs.items():
            e = "P" if "P" in ests else ("A" if "A" in ests else "F")
            V[i]["cm"][e] += 1
            V[i]["cm"]["por"].setdefault(sig, {"P": 0, "A": 0, "F": 0})[e] += 1
    print(f"   {len(sess)} sessões de comissão com lista de presença")
    return len(sess), min((d for _, d in info.values()), default="")


# ---------------------------------------------------------------- montagem
def montar():
    V = coletar_vereadores()
    docs = coletar_documentos(V)
    votos = coletar_votacoes(V)
    just = coletar_justificadas(V)
    try:
        ncom, pricom = coletar_comissoes(V)
    except Exception as e:  # extra: se falhar, o resto continua
        print("   ! comissões não coletadas:", e, file=sys.stderr)
        ncom, pricom = 0, ""
    try:
        from viagens import coletar_viagens
        coletar_viagens(V, baixar, baixar_bin)
    except Exception as e:  # viagens são um extra: se falhar, o resto do site continua
        print("   ! viagens não coletadas:", e, file=sys.stderr)
    try:
        est = json.load(open(os.path.join(RAIZ, "coletor", "estatico.json"), encoding="utf-8"))["v"]
        for v in V:
            e = est.get(str(v["sid"]), {})
            v["vot"] = e.get("votos")
            v["ant"] = e.get("ant")
    except Exception as e:
        print("   ! estatico.json não lido:", e, file=sys.stderr)

    print("5/5 Cruzando os dados…")
    # itens: [id, codigo, texto, aaaammdd, grupo, resultado, autores, temGrupo(1=proposituras,3=projetos), tema, rua, bairro]
    IT = []
    for d in sorted(docs.values(), key=lambda d: (d["data"], d["id"]), reverse=True):
        g = classificar(d)
        rua, bairro = endereco(d["txt"]) if g in "bc" else (None, None)
        IT.append([d["id"], d["cod"].replace(" Nº ", " ").replace("Nº ", ""), d["txt"], d["data"], g, d.get("res", ""), d["aut"], d["g"], tema(d, g), rua or "", bairro or ""])

    catot = Counter(it[4] for it in IT)
    for i, v in enumerate(V):
        v["cat"] = {c: sum(1 for it in IT if it[4] == c and i in it[6]) for c in "bchlo"}

    # bairros mais citados
    cont_b = Counter()
    nome_b = {}
    for it in IT:
        if it[10]:
            k = norm(it[10])
            cont_b[k] += 1
            nome_b.setdefault(k, it[10])
    bairros = [(nome_b[k], n) for k, n in cont_b.most_common() if n >= 3]

    # problemas que não somem: mesmo assunto, mesma rua, várias vezes
    grp = defaultdict(list)
    for n, it in enumerate(IT):
        if it[4] == "b" and it[9] and it[8]:
            grp[(norm(it[9]), norm(it[10]), it[8])].append(n)
    rep = []
    for (r, b, th), ids in grp.items():
        if len(ids) < 3:
            continue
        its = [IT[n] for n in ids]
        rep.append({"r": its[0][9], "b": its[0][10], "th": th, "n": len(ids), "ids": ids,
                    "a": len({a for it in its for a in it[6]}),
                    "d0": min(it[3] for it in its), "d1": max(it[3] for it in its)})
    rep.sort(key=lambda g: (-g["n"], -g["a"]))

    # votos e presença
    sess_votos = defaultdict(list)
    for vt in votos:
        sess_votos[vt["sess"]].append(vt)
    nvot = unan = 0
    for i, v in enumerate(V):
        v.update({"vs": 0, "vn": 0, "va": 0, "P": 0, "A": 0, "F": 0, "naos": []})
    for vt in votos:
        ativos = {i: r for i, r in vt["v"].items() if r in ("a favor", "contra", "abstencao")}
        if len(ativos) < 2:
            continue
        nvot += 1
        if len(set(ativos.values())) == 1:
            unan += 1
        for i, r in ativos.items():
            v = V[i]
            if r == "a favor":
                v["vs"] += 1
            else:
                v["vn" if r == "contra" else "va"] += 1
                v["naos"].append({"e": vt["t"] + (": " + vt["e"] if vt["e"] else ""), "v": "nao" if r == "contra" else "abs",
                                  "d": vt["d"], "t": vt["sn"], "a": vt["a"].title(), "u": f"{BASE}/Votacoes/Details?id={vt['id']}"})
    sess_ok, semreg = [], []
    for sid, lst in sess_votos.items():
        regs = defaultdict(set)
        for vt in lst:
            for i, r in vt["v"].items():
                regs[i].add(r)
        if not regs:
            semreg.append(sid)
            continue
        sess_ok.append((sid, max(vt["d"] for vt in lst)))
        for i, rs in regs.items():
            if rs - {"ausente", "nao votou"}:
                V[i]["P"] += 1
            elif i in just.get(sid, set()):
                V[i]["A"] += 1
            else:
                V[i]["F"] += 1

    agora = datetime.now(BRT)
    dados = {
        "gerh": agora.isoformat(timespec="seconds"), "ger": agora.strftime("%Y-%m-%d"), "posse": POSSE,
        "sal": SALARIO, "catot": catot, "nvot": nvot, "unan": unan,
        "sess": len(sess_ok), "ult": max((d for _, d in sess_ok), default=""), "pri": min((d for _, d in sess_ok), default=""), "semreg": len(semreg),
        "ncom": ncom, "pricom": pricom, "comissoes": COMISSOES,
        "bairros": [b for b, _ in bairros], "bairrosn": [n for _, n in bairros],
        "rep": rep,
        "v": [{k: v.get(k) for k in ("id", "ap", "nome", "part", "mesa", "foto", "email", "url", "ficha", "cat", "vs", "vn", "va", "P", "A", "F", "naos", "vot", "ant", "vg", "vgt", "cm")} for v in V],
        "items": IT,
    }
    conferir(dados)
    return dados


def conferir(D):
    """Trava de segurança: se algo vier estranho, não publica."""
    erros = []
    if not 15 <= len(D["v"]) <= 25:
        erros.append(f"número de vereadores estranho: {len(D['v'])}")
    if len(D["items"]) < 1000:
        erros.append(f"poucas propostas: {len(D['items'])}")
    if D["nvot"] < 50:
        erros.append(f"poucas votações: {D['nvot']}")
    if sum(1 for v in D["v"] if sum(v["cat"].values()) == 0) > 3:
        erros.append("muitos vereadores sem nenhuma proposta")
    if os.path.exists(SAIDA):
        try:
            velho = json.loads(open(SAIDA, encoding="utf-8").read().split("=", 1)[1].rstrip().rstrip(";"))
            if len(D["items"]) < 0.9 * len(velho["items"]):
                erros.append(f"propostas caíram de {len(velho['items'])} para {len(D['items'])}")
        except Exception:
            pass
    if erros:
        raise SystemExit("COLETA RECUSADA, site mantido como estava:\n - " + "\n - ".join(erros))


if __name__ == "__main__":
    D = montar()
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    tmp = SAIDA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("window.RB=" + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + ";\n")
    os.replace(tmp, SAIDA)
    print(f"Pronto: {len(D['items'])} propostas, {len(D['v'])} vereadores, {D['nvot']} votações, {len(D['rep'])} problemas repetidos.")
