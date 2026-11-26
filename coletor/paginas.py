# -*- coding: utf-8 -*-
"""
Gera as páginas do site Radar Bragança a partir de um modelo único (mesmo topo, menu e rodapé).

Páginas: / (Início), /vereadores/, /vereador/<nome>/ (uma por vereador), /bairros/, /propostas/, /sobre/.
A página /demandas/ (Voz do Bairro) é mantida como está.
Para cada vereador também é criada a imagem de prévia do WhatsApp (card.jpg), se a biblioteca Pillow estiver instalada.

Uso: python coletor/paginas.py     (o robô diário roda depois de coletar.py)
"""
import html, json, os, re, unicodedata
from datetime import datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(RAIZ, "site")
DOMINIO = "https://www.bragancaterraquerida.com.br"
D = json.loads(open(os.path.join(SITE, "dados.js"), encoding="utf-8").read()[len("window.RB="):].rstrip().rstrip(";"))
V = D["v"]
e = lambda s: html.escape(str(s), quote=True)
nf = lambda n: f"{int(n):,}".replace(",", ".")
VER = lambda arq: str(int(os.path.getmtime(os.path.join(SITE, "assets", arq))))


def slug(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


LOGO = ('<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="8" fill="#e5322d"/>'
        '<path d="M19 17a21 21 0 000 30M45 17a21 21 0 010 30M10 9a33 33 0 000 46M54 9a33 33 0 010 46" '
        'stroke="currentColor" stroke-width="5" fill="none" stroke-linecap="round"/></svg>')
MENU = [("inicio", "/", "Início"), ("vereadores", "/vereadores/", "Vereadores"), ("bairros", "/bairros/", "Seu bairro"),
        ("propostas", "/propostas/", "Propostas"), ("prefeitura", "/prefeitura/", "Prefeitura"), ("sobre", "/sobre/", "Sobre"), ("voz", "/demandas/", "Voz do Bairro")]


def menu_mobile(ativa):
    links = [(h, f'<a href="{h}"{" aria-current=page" if k == ativa else ""}>{n}</a>')
             for k, h, n in MENU]
    diretos = ("/bairros/", "/demandas/")
    main = "".join(link for h, link in links if h in diretos)
    more = "".join(link for h, link in links if h not in diretos)
    return ('<div class="mobile-nav">' + main + '<details><summary>Menu</summary>'
            + '<div class="mobile-nav-links">' + more + '</div></details></div>')


def dados_inicio(dados):
    campos = ("gerh", "posse", "sal", "catot", "nvot", "unan", "pri", "bairros")
    resumo = {campo: dados[campo] for campo in campos}
    resumo["totalPropostas"] = len(dados["items"])
    resumo["v"] = [{campo: v[campo] for campo in ("id", "ap", "foto", "email", "cat") if campo in v}
                   for v in dados["v"]]
    indices = {}
    resumo["items"] = []
    resumo["rep"] = []
    for grupo in dados["rep"][:6]:
        ids = []
        for antigo in grupo["ids"]:
            if antigo not in indices:
                indices[antigo] = len(resumo["items"])
                resumo["items"].append(dados["items"][antigo])
            ids.append(indices[antigo])
        resumo["rep"].append({**grupo, "ids": ids})
    return "window.RB=" + json.dumps(resumo, ensure_ascii=False, separators=(",", ":")) + ";\n"


def pagina(ativa, titulo, descricao, url, corpo, init, imagem="/capa.jpg", titulo_og=None, extra_head=""):
    menu = "".join(
        f'<li{" class=cta" if k == "voz" else ""}><a href="{h}"{" aria-current=page" if k == ativa else ""}>{n}</a></li>'
        for k, h, n in MENU)
    img = imagem if imagem.startswith("http") else DOMINIO + imagem
    noscript = '<noscript><p class="wrap warn" style="margin-top:20px">Este site precisa do JavaScript ligado no navegador para mostrar os dados.</p></noscript>' if init else ""
    arquivo_dados = 'dados-inicio.js' if ativa == 'inicio' else 'dados.js'
    scripts = f'''<script src="/{arquivo_dados}?v={D['gerh']}"></script>
<script src="/assets/radar.js?v={VER('radar.js')}"></script>
<script>{init}</script>''' if init else ""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Radar Bragança">
<meta property="og:title" content="{e(titulo_og or titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:url" content="{DOMINIO}{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#e5322d">
<link rel="canonical" href="{DOMINIO}{url}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='5' fill='%23e5322d'/%3E%3Cpath d='M8 8a11 11 0 000 16M24 8a11 11 0 010 16' stroke='%230f1720' stroke-width='3' fill='none' stroke-linecap='round'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/radar.css?v={VER('radar.css')}">
<link rel="stylesheet" href="/assets/mobile-nav.css?v=4">
{extra_head}</head>
<body>
<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<header class="nav"><div class="wrap">
  <a class="brand" href="/" aria-label="Radar Bragança, página inicial">{LOGO}<span><b>RADAR</b><b>BRAGANÇA</b></span></a>
  <nav aria-label="Menu principal"><ul class="menu">{menu}</ul>{menu_mobile(ativa)}</nav>
</div></header>
<main id="conteudo">
{noscript}
{corpo}
</main>
<footer class="foot2"><div class="wrap">
  <div><a class="brand" href="/">{LOGO}<span><b>RADAR</b><b>BRAGANÇA</b></span></a>
    <p>O que cada vereador de Bragança Paulista fez desde a posse, com os dados oficiais da Câmara, do TSE e do Portal da Transparência. Mesma régua para todos, sem nota nem opinião.</p></div>
  <div><h4>Páginas</h4><ul>{"".join(f'<li><a href="{h}">{n}</a></li>' for k, h, n in MENU)}</ul></div>
  <div><h4>Contato</h4><ul><li>Achou um erro? Escreva para<br><a href="mailto:contato@bragancaterraquerida.com.br"><b>contato@bragancaterraquerida.com.br</b></a><br>Conferimos e corrigimos o mais rápido possível, e a correção fica registrada.</li><li><a href="/sobre/">Como contamos os números</a></li></ul></div>
  <p class="fine"><span data-atualizado></span> Este não é um site oficial. Projeto independente, sem ligação com a Câmara, a Prefeitura, candidatos ou partidos. Todos os dados vêm de fontes públicas, citadas em cada página.</p>
</div></footer>
{scripts}
<!-- Contador de visitas (GoatCounter): sem cookies, não identifica ninguém. -->
<script data-goatcounter="https://radarbraganca.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</body>
</html>
"""


def escreve(caminho, conteudo):
    p = os.path.join(SITE, caminho)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(conteudo)


SEARCH_ICON = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>'


def tile(k, href, titulo, texto, icone):
    return (f'<a class="tile k-{k}" href="{href}"><span class="ci">{icone}</span><b>{titulo}</b>'
            f'<span>{texto}</span><span class="go">Abrir →</span></a>')


I = lambda p: f'<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{p}</svg>'
IC_USERS = I('<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0113 0M16 4.5a3.5 3.5 0 010 7M18 14a6 6 0 013.5 6"/>')
IC_PIN = I('<path d="M12 21s7-6.2 7-11a7 7 0 10-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>')
IC_LAW = I('<path d="M7 3h8l4 4v14H7z"/><path d="M15 3v4h4M10 12h6M10 16h6"/>')
IC_CHECK = I('<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>')
IC_MEGA = I('<path d="M3 11v3a1 1 0 001 1h2l5 4V6L6 10H4a1 1 0 00-1 1z"/><path d="M15 9a4 4 0 010 6M18 6a8 8 0 010 12"/>')

LD = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "WebSite", "name": "Radar Bragança", "url": DOMINIO + "/", "inLanguage": "pt-BR", "description": "O que cada vereador de Bragança Paulista fez desde a posse, com dados oficiais."}, ensure_ascii=False) + "</script>\n"

# ------------------------------------------------------------------ Início
def data_prefeitura():
    caminho = os.path.join(SITE, "prefeitura.js")
    if not os.path.exists(caminho):
        return "Data de atualização indisponível"
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.loads(arquivo.read().removeprefix("window.PF=").strip().removesuffix(";"))
    data = datetime.fromisoformat(dados["ger"])
    ano, mes = dados["ult"].split("-")
    return f"Atualizada em {data:%d/%m/%Y}, às {data:%Hh%M} · dados até {mes}/{ano}"


inicio = f"""
<section class="wrap radar-home">
  <div>
    <span class="live"><i></i><span id="livet">Dados da Câmara</span></span>
    <h1 class="logo" aria-label="Radar Bragança">{LOGO}<span><b>RADAR</b><b>BRAGANÇA</b></span></h1>
    <p class="intro">Veja o que os vereadores propuseram, como votaram e o que pediram para o seu bairro.</p>
    <form class="search" id="fbq" action="/bairros/#busca" role="search"><label for="hq" class="eyebrow">Bairro ou rua</label>
      <div class="radar-search-row"><div class="radar-search-field">{SEARCH_ICON}<input id="hq" name="q" type="search" list="hq-bairros" placeholder="Digite seu bairro ou sua rua" autocomplete="off"><datalist id="hq-bairros"></datalist></div><button class="btn" type="submit">Consultar pedidos para minha rua</button></div></form>
    <ul class="chips" id="bairros-chips"></ul>
    <p><a href="/demandas/">Relatar um problema na Voz do Bairro →</a></p>
  </div>
  <div>
    <div class="meter radar-salary"><p class="t">Estimativa acumulada de subsídios desde a posse</p><p class="v num" id="tick">—</p><small id="msal"></small><a href="/sobre/">Como calculamos</a></div>
    <div class="stats" id="stats"></div>
    <p class="upd" data-atualizado></p>
    <p class="upd"><a href="/prefeitura/">Prefeitura (TCE-SP)</a> · {data_prefeitura()}</p>
  </div>
</section>

<section class="wrap">
  <h2>Explore o Radar</h2>
  <div class="tiles">
    {tile("o", "/vereadores/", "Os 19 vereadores", "Presença, propostas, votos e viagens de cada um, com a mesma régua.", IC_USERS)}
    {tile("b", "/bairros/", "Pedidos por bairro", "Veja os pedidos registrados e quem os apresentou.", IC_PIN)}
    {tile("l", "/propostas/", "Propostas", "Consulte pedidos, homenagens e projetos de lei.", IC_LAW)}
    {tile("h", "/demandas/", "Relatar um problema", "Envie sua demanda pela Voz do Bairro.", IC_MEGA)}
  </div>
</section>

<section class="wrap" style="padding-top:26px">
  <ul class="trust">
    <li>{IC_CHECK}<b>Só dados oficiais</b><span>Câmara, TSE e Portal da Transparência</span></li>
    <li>{IC_CHECK}<b>Atualizado todo dia</b><span>Consulta diária às fontes oficiais</span></li>
    <li>{IC_CHECK}<b>Mesma régua</b><span>Os 19 vereadores medidos do mesmo jeito, sem nota nem opinião</span></li>
    <li>{IC_CHECK}<b>Fonte em cada número</b><span>Cada proposta abre na página da Câmara</span></li>
  </ul>
</section>

<section class="wrap">
  <p class="eyebrow">Um por um</p>
  <h2>Os vereadores</h2>
  <p class="lead">Toque em um rosto para ver tudo o que ele fez desde a posse.</p>
  <ul class="faces" id="faces"></ul>
</section>

<section class="wrap">
  <p class="eyebrow">Em números</p>
  <h2>O retrato da Câmara</h2>
  <div class="cols">
    <div class="box rt"><p class="eyebrow">Como a Câmara vota</p><p class="bign num" id="pct">–</p><p class="rt-t">das votações terminaram com <b>todos votando igual</b></p><div class="sbar" id="pctb"></div><p class="rt-l num" id="pctl"></p><p class="mute rt-d" id="pctd"></p></div>
    <div class="box rt"><p class="eyebrow">Pedidos ou leis?</p><p class="bign num" id="rz" style="color:var(--b)">–</p><p class="rt-t">pedidos de melhoria para cada <b>projeto de lei</b></p><div class="sbar" id="rzb"></div><p class="rt-l num" id="rzl"></p><p class="mute rt-d" id="rzd"></p></div>
  </div>
</section>

<section class="wrap" id="repetidos">
  <p class="eyebrow">Só aqui</p>
  <h2>Pedidos que voltaram à Câmara</h2>
  <p class="lead">Veja pedidos sobre a mesma rua e o mesmo tema registrados mais de uma vez. <a href="/bairros/#repetidos">Ver todas as ruas →</a></p>
  <div class="reps" id="reps"></div>
</section>
"""
escreve("dados-inicio.js", dados_inicio(D))
escreve("index.html", pagina("inicio", "Radar Bragança",
        "O que cada vereador de Bragança Paulista fez desde a posse: presença, propostas e votos. Só dados oficiais da Câmara, atualizados todo dia.",
        "/", inicio, "Radar.inicio()", titulo_og="Radar Bragança: o que cada vereador fez desde a posse", extra_head=LD))

# ------------------------------------------------------------------ Vereadores
vereadores = """
<section class="wrap phead">
  <p class="eyebrow">Um por um</p>
  <h1>Os vereadores de Bragança Paulista</h1>
  <p class="lead" id="vsub"></p>
  <a class="cmp-cta" href="/comparar/"><span class="cmp-ic" aria-hidden="true">⇄</span><span><b>Comparar dois vereadores</b><small>Escolha dois nomes e veja os números lado a lado</small></span><span aria-hidden="true">→</span></a>
  <div class="filters">
    <label class="field">Buscar por nome<input id="q" type="search" placeholder="Ex.: Fabiana, Coxinha" autocomplete="off"></label>
    <label class="field">Partido<select id="partido"><option value="">Todos</option></select></label>
    <label class="field">Ordenar por<select id="ordem">
      <option value="nome">Nome (A–Z)</option><option value="tot">Mais propostas</option><option value="faltas">Mais faltas</option><option value="b">Mais pedidos no bairro</option>
      <option value="l">Mais propostas de lei</option><option value="h">Mais homenagens</option><option value="nao">Mais votos “não”</option><option value="vot">Mais votos em 2024</option><option value="vg">Mais gasto em viagens</option><option value="cf">Mais faltas em comissões</option></select></label>
  </div>
  <p class="mute" id="conta" style="font-size:14px;margin:4px 0 0"></p>
  <ul class="legend" aria-label="Legenda das barras coloridas"><li class="k-b"><i></i>Pedidos nos bairros</li><li class="k-c"><i></i>Cobranças</li><li class="k-h"><i></i>Homenagens</li><li class="k-l"><i></i>Propostas de lei</li><li class="k-o"><i></i>Outros</li></ul>
  <div class="vgrid" id="grid"></div>
</section>
<section class="wrap" id="planilha">
  <div class="dl"><button class="btn gh" id="csv" type="button">Baixar planilha com os 19 vereadores</button>
    <span class="mute">Arquivo CSV, abre no Excel ou no Google Planilhas. Use à vontade, citando a fonte.</span></div>
</section>
"""
escreve("vereadores/index.html", pagina("vereadores", "Vereadores · Radar Bragança",
        "Os 19 vereadores de Bragança Paulista: presença, propostas, votos e viagens de cada um, com dados oficiais.",
        "/vereadores/", vereadores, "Radar.vereadores()"))

# ------------------------------------------------------------------ Página de cada vereador
def card_img(v, destino):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False
    import colorsys
    W, H = 1200, 630
    i = V.index(v)
    hue = (i * 47 + 200) % 360
    tint = tuple(int(c * 255) for c in colorsys.hls_to_rgb(hue / 360, .94, .85))
    deep = tuple(int(c * 255) for c in colorsys.hls_to_rgb(hue / 360, .26, .55))
    im = Image.new("RGB", (W, H), tint); d = ImageDraw.Draw(im)
    def fonte(nomes, s):
        for n in nomes:
            for base in ("C:/Windows/Fonts/", "/usr/share/fonts/truetype/dejavu/", "/usr/share/fonts/truetype/liberation/"):
                try: return ImageFont.truetype(base + n, s)
                except Exception: pass
        return ImageFont.load_default()
    BLACK = lambda s: fonte(["ariblk.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"], s)
    BOLD = lambda s: fonte(["segoeuib.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"], s)
    REG = lambda s: fonte(["segoeui.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"], s)
    fp = os.path.join(SITE, "fotos", f"{v['id']}.jpg")
    if os.path.exists(fp):
        ph = Image.open(fp).convert("RGB").resize((300, 300), Image.LANCZOS)
        m = Image.new("L", (900, 900), 0); ImageDraw.Draw(m).ellipse([0, 0, 900, 900], fill=255)
        d.ellipse([62, 112, 378, 428], fill=(255, 255, 255))
        im.paste(ph, (70, 120), m.resize((300, 300), Image.LANCZOS))
    nome = v["ap"]; s = 72
    while d.textlength(nome, font=BLACK(s)) > 720 and s > 40: s -= 4
    d.text((430, 150), nome, font=BLACK(s), fill=deep)
    d.text((432, 150 + s + 18), v["part"], font=BOLD(34), fill=(17, 26, 36))
    t = v["P"] + v["A"] + v["F"]; tot = sum(v["cat"].values())
    kp = [(f"{round(v['P'] / t * 100)}%" if t else "–", "presença"), (nf(tot), "propostas"), (nf(len(v.get('vg') or [])), "viagens")]
    for k, (a, b) in enumerate(kp):
        x = 432 + k * 240
        d.rounded_rectangle([x, 330, x + 220, 450], 24, fill=(255, 255, 255))
        d.text((x + 110, 375), a, font=BLACK(50), fill=(17, 26, 36), anchor="mm")
        d.text((x + 110, 425), b, font=BOLD(26), fill=(93, 105, 118), anchor="mm")
    d.rectangle([0, 520, W, H], fill=(17, 26, 36))
    d.text((70, 575), "RADAR BRAGANÇA", font=BLACK(36), fill=(255, 255, 255), anchor="lm")
    d.text((W - 70, 575), "bragancaterraquerida.com.br", font=BOLD(30), fill=(255, 143, 139), anchor="rm")
    im.save(destino, "JPEG", quality=86, optimize=True)
    return True


for v in V:
    s = slug(v["ap"])
    t = v["P"] + v["A"] + v["F"]; tot = sum(v["cat"].values())
    pres = f"{round(v['P'] / t * 100)}% de presença, " if t else ""
    desc = f"{v['ap']} ({v['part']}) desde a posse: {pres}{nf(tot)} propostas, votos e viagens oficiais. Dados oficiais da Câmara de Bragança Paulista."
    foto = f'<img class="big-ph" src="/fotos/{v["id"]}.jpg" alt="Foto de {e(v["ap"])}">' if v.get("foto") else ""
    tags = f'<span class="pill">{e(v["part"])}</span>' + (f'<span class="pill r">{e(v["mesa"])} da Câmara</span>' if v.get("mesa") else "") \
        + (f'<span class="pill r">{nf(v["vot"])} votos em 2024</span>' if v.get("vot") else "")
    contato = (f'<a class="btn ficha-compare" href="/comparar/?a={v["id"]}">Comparar vereadores</a>'
               + f'<a class="btn lt" href="{e(v.get("ficha") or v["url"])}" target="_blank" rel="noopener">Ficha oficial na Câmara ↗</a>'
               + (f'<a class="btn lt" href="mailto:{e(v["email"])}">{e(v["email"])}</a>' if v.get("email") else "")
               + '<a class="btn wa" id="wa" href="#" target="_blank" rel="noopener">Compartilhar no WhatsApp</a><button class="btn gh" type="button" id="cp">Copiar link</button>')
    corpo = f"""
<section class="wrap phead" style="padding-top:20px">
  <p class="crumbs"><a href="/">Início</a> › <a href="/vereadores/">Vereadores</a> › {e(v['ap'])}</p>
  <div class="prof">{foto}<div><h1>{e(v['ap'])}</h1><p class="civil">{e(v['nome'])}</p><div class="tags">{tags}</div><div class="contato">{contato}</div></div></div>
  <nav class="subnav ficha-nav" aria-label="Nesta página"><a href="#s-propostas">Propostas</a><a href="#kpis">Presença</a><a href="#s-votos">Votos e comissões</a><a href="#s-viagens">Viagens</a><a href="#s-voto24">Bairros que votaram</a><a href="#s-ruas">Ruas que voltam</a><a href="#s-blocos">Com quem vota</a></nav>
  <div class="kpis" id="kpis"></div>
</section>
<section class="wrap">
  <div class="cols">
    <div class="box"><h3>O que propôs</h3><div id="picks"></div></div>
    <div class="box"><h3>Onde pediu</h3><div id="onde"></div></div>
  </div>
</section>
<section class="wrap" id="s-voto24">
  <p class="eyebrow">Eleição de 2024</p><h2>Os bairros que deram mais votos</h2>
  <p class="lead" id="locc"></p>
  <div class="lcards" id="loc"></div>
  <p class="mute small">O local de votação é onde o eleitor vota, que nem sempre é onde mora. Os nomes de bairro da Justiça Eleitoral e da Câmara às vezes não batem; por isso alguns aparecem como “sem pedidos com esse nome”.</p>
</section>
<section class="wrap" id="s-propostas">
  <p class="eyebrow">Proposta por proposta</p><h2>Tudo o que apresentou desde a posse</h2>
  <ul class="tabs chips" id="tabs"></ul><div id="lista"></div>
</section>
<section class="wrap" id="s-ruas">
  <p class="eyebrow">Ruas que voltam</p><h2>Problemas que não somem</h2>
  <p class="lead" id="reps-n"></p><div class="reps" id="reps-v"></div>
</section>
<section class="wrap" id="s-votos">
  <div class="cols">
    <div class="box"><h3>Como votou</h3><div id="votos"></div></div>
    <div class="box"><h3>Comissões</h3><div id="com"></div><h3 style="margin-top:22px">Comparado com 2021–2024</h3><div id="ant"></div></div>
  </div>
</section>
<section class="wrap" id="s-blocos">
  <p class="eyebrow">Votações divididas</p><h2>Com quem vota e quanto apoia a Prefeitura</h2>
  <div class="cols">
    <div class="box"><h3>Com quem vota</h3><div id="jt"></div></div>
    <div class="box"><h3>Projetos da Prefeitura</h3><div id="gov"></div></div>
  </div>
</section>
<section class="wrap" id="s-viagens">
  <p class="eyebrow">Portal da Transparência</p><h2>Viagens oficiais</h2><div id="vgs"></div>
  <nav class="pn" id="pn" aria-label="Outros vereadores"></nav>
</section>
"""
    img = f"/vereador/{s}/card.jpg"
    os.makedirs(os.path.join(SITE, "vereador", s), exist_ok=True)
    if not card_img(v, os.path.join(SITE, "vereador", s, "card.jpg")):
        img = "/capa.jpg"
    escreve(f"vereador/{s}/index.html", pagina("vereadores", f"{v['ap']} · Radar Bragança", desc, f"/vereador/{s}/", corpo,
            f"Radar.vereador({v['id']})", imagem=img, titulo_og=f"{v['ap']}: o que fez desde a posse"))

# ------------------------------------------------------------------ Seu bairro
with open(os.path.join(SITE, "demandas", "index.html"), encoding="utf-8") as arquivo:
    receptor_bairros = re.search(r'''const ENDERECO\s*=\s*['"]([^'"]+)['"]''', arquivo.read())[1]

bairros = f"""
<section class="wrap phead" id="busca">
  <p class="eyebrow">Na sua rua</p>
  <h1>O que pediram pelo seu bairro?</h1>
  <p class="lead">Digite o bairro ou a rua. Sem nada digitado, você vê a cidade inteira.</p>
  <div class="search">{SEARCH_ICON}<input id="bq" type="search" list="bl" placeholder="Digite seu bairro ou sua rua" autocomplete="off" aria-label="Bairro ou rua"><datalist id="bl"></datalist></div>
  <ul class="chips" id="chips"></ul>
  <p><a class="btn gh" href="#problemas-bairro">Ver problemas relatados</a></p>
  <div id="bres"></div>
</section>
<section class="wrap bairro-painel" id="problemas-bairro" data-receptor="{e(receptor_bairros)}" aria-labelledby="problemas-titulo">
  <header class="bairro-painel-topo">
    <h2 id="problemas-titulo">Problemas dos bairros</h2>
    <p class="mute">Acompanhe a situação das demandas deste bairro enviadas pelo <a href="/demandas/">Voz do Bairro</a>. Os relatos aparecem aqui após revisão da equipe do Radar Bragança.</p>
    <p class="mute" id="problemas-nota" role="status"></p>
  </header>
  <div id="problemas-lista"></div>
</section>
<section class="wrap" id="repetidos">
  <p class="eyebrow">Só aqui</p>
  <h2>Pedidos que voltaram à Câmara</h2>
  <p class="lead">Veja pedidos sobre a mesma rua e o mesmo tema registrados mais de uma vez. O site da Câmara mostra os pedidos um por um; aqui eles são cruzados.</p>
  <p class="warn"><b>Atenção:</b> pedido repetido não prova que a Prefeitura ignorou. Às vezes o serviço foi feito e o problema voltou, ou o pedido é sobre um trecho diferente da mesma rua.</p>
  <div class="reps" id="reps"></div>
</section>
"""
comparar = """
<section class="wrap phead">
  <p class="eyebrow">Lado a lado</p>
  <h1>Comparar vereadores</h1>
  <p class="lead">Escolha dois vereadores. Os números são os mesmos para todos e vêm dos dados oficiais. Nas barras, quem tem o número maior fica com a barra cheia, e as porcentagens vão de 0 a 100%.</p>
  <div class="vs" id="vs"></div>
  <div class="contato"><button class="btn gh" type="button" id="cmp-copy">Copiar link desta comparação</button><span role="status" id="cmp-copy-status"></span></div>
  <div id="cmp"></div>
  <p class="mute" style="font-size:14px;margin-top:18px">Desde a posse, em 1º de janeiro de 2025. Como cada número é contado: <a href="/sobre/">Sobre</a>.</p>
</section>
"""
escreve("comparar/index.html", pagina("vereadores", "Comparar vereadores · Radar Bragança",
        "Compare dois vereadores de Bragança Paulista lado a lado: presença, propostas, votos e viagens, com dados oficiais.",
        "/comparar/", comparar, "Radar.comparar()"))

prefeitura = """
<section class="wrap phead">
  <p class="eyebrow">Radar da Prefeitura</p>
  <h1>O dinheiro da Prefeitura</h1>
  <p class="lead" id="pf-lead">Quanto a Prefeitura de Bragança Paulista recebe, quanto paga e para quem. Os números são os que a própria Prefeitura envia ao Tribunal de Contas do Estado (TCE-SP).</p>
  <ul class="chips" id="pf-anos" aria-label="Escolha o ano"></ul>
  <div class="kpis" id="pf-kpis"></div>
</section>
<section class="wrap">
  <p class="eyebrow">Mês a mês</p>
  <h2>Quanto entrou e quanto foi pago</h2>
  <p class="mute" id="pf-mes-sub" style="margin:0 0 6px"></p>
  <div class="box"><ul class="pf-leg"><li><i class="e"></i>Entrou (receita)</li><li><i class="s"></i>Pago pela Prefeitura</li></ul><div class="pf-meses" id="pf-meses"></div></div>
</section>
<section class="wrap">
  <div class="cols">
    <div class="box"><h3>De onde vem o dinheiro</h3><p class="mute" style="margin:-4px 0 14px;font-size:14px">Impostos da cidade e repasses do Estado e do governo federal.</p><ol class="rank" id="pf-grp"></ol></div>
    <div class="box"><h3>Quanto custa a Câmara</h3><div id="pf-cam"></div></div>
  </div>
</section>
<section class="wrap">
  <p class="eyebrow">Fornecedores</p>
  <h2>Para quem a Prefeitura mais pagou</h2>
  <p class="mute" id="pf-forn-sub" style="margin:0 0 12px"></p>
  <div class="box"><ol class="pf-forn" id="pf-forn"></ol><button class="btn gh" type="button" id="pf-mais" hidden>Ver mais empresas</button>
  <p class="mute" id="pf-pf" style="font-size:14px;margin:16px 0 0"></p></div>
</section>
<section class="wrap">
  <p class="eyebrow">Como ler</p>
  <h2>De onde vêm esses números</h2>
  <div class="method">
    <details open><summary>Fonte</summary><p>Portal da Transparência Municipal do Tribunal de Contas do Estado de São Paulo (TCE-SP), com os dados que a Prefeitura envia todo mês. O Radar consulta esses dados diariamente. Os números de um mês costumam aparecer no TCE uns 30 a 60 dias depois. Veja a fonte em <a href="https://transparencia.tce.sp.gov.br/municipio/braganca-paulista" target="_blank" rel="noopener">transparencia.tce.sp.gov.br</a>.</p></details>
    <details open><summary>“Pago” e “entrou”</summary><p><b>Pago</b> é o dinheiro que de fato saiu do caixa da Prefeitura naquele mês. Pode incluir contas de meses ou anos anteriores. <b>Entrou</b> é o que a Prefeitura arrecadou: impostos, taxas e repasses do Estado e do governo federal. Os dois não se comparam como um “lucro” ou “prejuízo”: a Prefeitura também guarda dinheiro para pagar depois, e parte das receitas tem destino obrigatório, como saúde e educação.</p></details>
    <details open><summary>Fornecedores</summary><p>A lista soma os pagamentos feitos a cada empresa (CNPJ) no ano. Aparecer na lista não indica nenhum problema: mostra só para onde o dinheiro foi. Pagamentos a pessoas físicas aparecem só como total, sem nomes, para proteger a privacidade de servidores, aposentados e prestadores.</p></details>
    <details open><summary>Câmara</summary><p>O custo da Câmara é o que a própria Câmara pagou no período, com o dinheiro que recebe da Prefeitura: salários, funcionários, contas e serviços.</p></details>
  </div>
</section>
"""
escreve("prefeitura/index.html", pagina("prefeitura", "Prefeitura · Radar Bragança",
        "Quanto a Prefeitura de Bragança Paulista recebe, quanto paga e para quem, com os dados oficiais do TCE-SP.",
        "/prefeitura/", prefeitura, "Radar.prefeitura()",
        extra_head=f'<script src="/prefeitura.js?v={int(os.path.getmtime(os.path.join(SITE, "prefeitura.js")))}"></script>\n'))

escreve("bairros/index.html", pagina("bairros", "Seu bairro · Radar Bragança",
        "Busque seu bairro ou sua rua e veja tudo o que os vereadores de Bragança Paulista pediram para lá, e por quem.",
        "/bairros/", bairros, "Radar.bairros()", extra_head='<link rel="stylesheet" href="/assets/problemas-bairro.css?v=6">\n<script defer src="/assets/problemas-bairro.js?v=5"></script>\n'))

# ------------------------------------------------------------------ Propostas
propostas = f"""
<section class="wrap phead">
  <p class="eyebrow">Tudo o que entrou na Câmara</p>
  <h1>O que os vereadores propuseram</h1>
  <p class="lead" id="hsub"></p>
  <div class="split" id="split" aria-hidden="true"></div>
  <div class="cats" id="cats"></div>
</section>
<section class="wrap" id="lista-propostas">
  <p class="eyebrow">Proposta por proposta</p>
  <h2>Procure qualquer proposta</h2>
  <div class="search" style="max-width:640px">{SEARCH_ICON}<input id="pq" type="search" placeholder="Ex.: creche, iluminação, Rua Santa Clara" autocomplete="off" aria-label="Procurar proposta"></div>
  <ul class="chips" id="ptabs"></ul>
  <p class="mute" id="pcount" style="font-size:14px;margin:6px 0 10px"></p>
  <div id="plista"></div>
</section>
"""
escreve("propostas/index.html", pagina("propostas", "Propostas · Radar Bragança",
        "Todas as propostas dos vereadores de Bragança Paulista desde a posse: pedidos, cobranças, homenagens e projetos de lei.",
        "/propostas/", propostas, "Radar.propostas()"))

# ------------------------------------------------------------------ Sobre
sobre = """
<section class="wrap phead">
  <p class="eyebrow">Transparência</p>
  <h1>Sobre o Radar Bragança</h1>
  <p class="lead">Um site independente que reúne, num só lugar, o trabalho dos vereadores de Bragança Paulista desde a posse, em 1º de janeiro de 2025. Só com dados oficiais, a mesma régua para todos e nenhuma nota ou opinião.</p>
  <div class="cols" style="margin-top:10px">
    <div class="box"><h3>De onde vêm os dados</h3><ul class="themes" style="gap:10px">
      <li><span class="ti">1</span><span>Sistema legislativo da Câmara Municipal (braganca.siscam.com.br): propostas, votações e presença</span><b></b></li>
      <li><span class="ti">2</span><span>Portal da Transparência da Câmara: viagens oficiais e prestações de contas</span><b></b></li>
      <li><span class="ti">3</span><span>TSE: votos de cada vereador na eleição de 2024</span><b></b></li>
      <li><span class="ti">4</span><span>Site camarabp.sp.gov.br: foto e e-mail oficial de cada gabinete</span><b></b></li>
      <li><span class="ti">5</span><span>Tribunal de Contas do Estado (TCE-SP): receitas, pagamentos e fornecedores da Prefeitura e gastos da Câmara</span><b></b></li></ul>
      <p class="mute" style="margin:12px 0 0;font-size:14px">Consultamos as fontes diariamente. Quando a coleta retorna dados incompletos ou inconsistentes, o site exibe a última versão validada.</p></div>
    <div class="box"><h3>Achou um erro?</h3><p id="m-erro" style="margin:0 0 10px"></p><p class="mute" style="margin:0;font-size:14px">Todos os números foram conferidos contra a fonte oficial antes da publicação: propostas, votos, presença no plenário e nas comissões, viagens e votos de 2024.</p></div>
  </div>
</section>
<section class="wrap">
  <p class="eyebrow">Metodologia</p>
  <h2>Como contamos</h2>
  <div class="method">
    <details open><summary>Presença nas reuniões da Câmara</summary><p id="m-pres"></p></details>
    <details open><summary>Presença nas comissões</summary><p id="m-com"></p></details>
    <details open><summary>Os grupos de propostas</summary><p>A mesma regra vale para todos.<br>• <b>Pedido de melhoria no bairro</b> (na Câmara se chama “indicação”): o vereador pede à Prefeitura uma melhoria na rua ou no bairro.<br>• <b>Cobrança</b>: pedido de informação, requerimento ou moção de apelo, quando o vereador pergunta ou cobra algo da Prefeitura ou de outro órgão.<br>• <b>Homenagem</b>: parabéns, voto de pesar, título, medalha, nome de rua ou data comemorativa.<br>• <b>Projeto de lei</b>: cria ou muda uma regra da cidade.<br>• <b>Outros</b>: moções de apoio ou repúdio e regras internas da Câmara.</p></details>
    <details open><summary>Votos</summary><p id="m-vot"></p></details>
    <details open><summary>Com quem vota e apoio à Prefeitura</summary><p id="m-blo"></p></details>
    <details open><summary>Onde foi votado e onde pede</summary><p id="m-loc"></p></details>
    <details open><summary>Salário</summary><p id="m-sal"></p></details>
    <details open><summary>Bairros e ruas</summary><p>O bairro e a rua são lidos do texto oficial de cada pedido (o trecho “Rua tal – Bairro tal”). Quando o texto não segue esse formato, o pedido não entra no cruzamento por rua, mas continua aparecendo na busca por palavra.</p></details>
    <details open><summary>Viagens oficiais</summary><p>Vêm do Portal da Transparência da Câmara. O valor de cada viagem é o da prestação de contas oficial. Ele soma alimentação e hospedagem de todos que foram, inclusive motorista e funcionários. Não inclui combustível nem pedágio. Se mais de um vereador foi, a viagem aparece na página de cada um.</p></details>
    <details open><summary>Votos em 2024 e comparação com o mandato anterior</summary><p>Os votos são o resultado oficial do TSE na eleição de 2024. A comparação mostra quantas propostas por ano o vereador fazia no mandato anterior (2021–2024) e quantas faz agora, com a mesma regra de grupos. Presença e votos do mandato anterior não podem ser comparados, porque a Câmara só começou a registrar o voto de cada vereador em 2026.</p></details>
    <details open><summary>O que não é falta</summary><p>Ausência justificada e licença médica aparecem separadas e não contam como falta. Reunião em que o sistema não registrou ninguém também não conta.</p></details>
    <details open><summary>Leis aprovadas</summary><p>O site mostra quantos projetos de lei cada vereador apresentou, mas ainda não quantos viraram lei. O sistema da Câmara não informa a situação de cada projeto de forma confiável.</p></details>
  </div>
</section>
"""
# Registro público de correções: acrescente uma linha a cada erro corrigido.
# Formato: ("dd/mm/aaaa", "o que estava errado e o que foi feito")
CORRECOES = [
]
lista_corr = "".join(f"<li><b>{e(d)}</b> · {e(t)}</li>" for d, t in CORRECOES) or     "<li>Nenhuma correção registrada até agora. O registro começou em 17/11/2026.</li>"
sobre += f"""
<section class="wrap" id="correcoes">
  <p class="eyebrow">Transparência do próprio site</p>
  <h2>Quem somos, correções e aviso legal</h2>
  <div class="method">
    <details open><summary>Quem faz e como é financiado</summary><p>O Radar Bragança é feito pela equipe do Bragança Terra Querida, moradores de Bragança Paulista que querem facilitar o acompanhamento da Câmara e da Prefeitura. O site é mantido pelos próprios organizadores.<br><b>Regra de financiamento:</b> não aceitamos dinheiro, patrocínio ou anúncio de vereadores, políticos, candidatos, partidos, da Prefeitura ou da Câmara. Se um dia o site tiver apoio de leitores ou patrocínio de comércio local, isso será informado aqui, e quem apoia não tem nenhuma influência sobre os números.</p></details>
    <details open><summary>Correções</summary><p>Quando alguém aponta um erro, conferimos na fonte oficial. Se o erro for nosso, corrigimos e anotamos aqui a data e o que mudou.</p><ul>{lista_corr}</ul></details>
    <details open><summary>Direito de resposta</summary><p>Qualquer vereador, a Prefeitura ou a Câmara pode mandar uma nota sobre os dados publicados para <a href="mailto:contato@bragancaterraquerida.com.br">contato@bragancaterraquerida.com.br</a>. A nota é publicada sem cortes ao lado dos dados de quem a enviou, desde que trate dos números mostrados aqui.</p></details>
    <details open><summary>Aviso legal</summary><p>Este não é um site oficial. É um projeto independente, sem ligação com a Câmara, a Prefeitura, candidatos ou partidos, e não faz propaganda a favor ou contra ninguém. Todas as informações vêm de dados que os próprios órgãos públicos publicam, como manda a Lei de Acesso à Informação (Lei 12.527/2011). Cada número tem a fonte indicada. O site mostra fatos e contagens, não dá notas nem acusa ninguém. Se um dado oficial estiver errado na origem, o erro aparece aqui também até que o órgão o corrija.</p></details>
    <details open><summary>Privacidade</summary><p>O site não usa cookies e não identifica quem o visita. As visitas são contadas de forma anônima, sem guardar quem é a pessoa. As fontes de letra são carregadas do Google Fonts. As mensagens enviadas pela página Voz do Bairro ficam guardadas com a equipe, não são publicadas e só são repassadas com autorização de quem escreveu. Para apagar uma mensagem, escreva para o e-mail acima.</p></details>
  </div>
</section>
"""
escreve("sobre/index.html", pagina("sobre", "Sobre · Radar Bragança",
        "Como o Radar Bragança conta os números: fontes oficiais, regras e como pedir correção.",
        "/sobre/", sobre, "Radar.sobre()"))

# ------------------------------------------------------------------ 404, robots, sitemap
escreve("404.html", pagina("", "Página não encontrada · Radar Bragança", "Página não encontrada.", "/404.html", """
<section class="wrap e404">
  <p class="bign">404</p>
  <h1 style="font-family:var(--display);font-weight:900;font-size:clamp(26px,6vw,40px);margin:0 0 10px">Esta página não existe</h1>
  <p class="lead" style="margin:0 auto 20px">O endereço pode ter mudado. Comece por uma destas páginas:</p>
  <p style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap"><a class="btn" href="/">Página inicial</a><a class="btn gh" href="/vereadores/">Vereadores</a><a class="btn gh" href="/bairros/">Seu bairro</a></p>
</section>""", ""))
urls = ["/", "/vereadores/", "/comparar/", "/prefeitura/", "/bairros/", "/propostas/", "/sobre/", "/demandas/"] + [f"/vereador/{slug(v['ap'])}/" for v in V]
escreve("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{DOMINIO}{u}</loc><lastmod>{D['ger']}</lastmod></url>\n" for u in urls) + "</urlset>\n")
escreve("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /v/\nSitemap: {DOMINIO}/sitemap.xml\n")


def dados_formulario(pagina, dados):
    vereadores = [{"ap": v["ap"], "part": v.get("part", "")} for v in dados["v"]]
    conteudo = json.dumps({"v": vereadores, "bairros": dados["bairros"]},
                          ensure_ascii=False, separators=(",", ":")).replace("<", r"<")
    bloco = f'<script type="application/json" id="dados-formulario">{conteudo}</script>'
    padrao = r'<script src="\.\./dados\.js"></script>|<script type="application/json" id="dados-formulario">.*?</script>'
    resultado, total = re.subn(padrao, lambda _: bloco, pagina, flags=re.S)
    if total != 1:
        raise ValueError("Bloco de dados do formulario ausente ou duplicado")
    return resultado


# ------------------------------------------------------------------ Voz do Bairro: mesmo menu do resto do site
pd = os.path.join(SITE, "demandas", "index.html")
if os.path.exists(pd):
    h = open(pd, encoding="utf-8").read()
    h = re.sub(r"<!-- menu:ini -->.*?<!-- menu:fim -->\n?", "", h, flags=re.S)
    itens = "".join(f'<li{" class=cta" if k == "voz" else ""}><a href="{hh}"{" aria-current=page" if k == "voz" else ""}>{n}</a></li>' for k, hh, n in MENU)
    css = (
        '.rb-nav{position:sticky;top:0;z-index:15;background:rgba(236,242,236,.94);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid #d3ded3;font-family:"Inter",system-ui,sans-serif}'
        '.rb-nav>div{max-width:1120px;margin:0 auto;padding:0 16px;display:flex;align-items:center;gap:18px;min-height:62px;flex-wrap:wrap}'
        '.rb-nav .brand{display:flex;align-items:center;gap:9px;text-decoration:none;color:#111a24;font-family:"Archivo","Inter",sans-serif;font-weight:900;letter-spacing:-.02em;line-height:.9;font-size:15px}'
        '.rb-nav .brand svg{width:34px;height:34px}.rb-nav .brand b{display:block}.rb-nav .brand b+b{color:#e5322d}'
        '.rb-nav ul{display:flex;gap:4px;list-style:none;margin:0 0 0 auto;padding:0}'
        '.rb-nav li a{display:block;padding:9px 12px;border-radius:10px;text-decoration:none;color:#111a24;font-weight:600;font-size:15px;white-space:nowrap}'
        '.rb-nav li a:hover{background:#e1e9e1}.rb-nav .cta a,.rb-nav .cta a:hover{background:#e5322d;color:#fff}'
        '@media(prefers-color-scheme:dark){.rb-nav{background:rgba(14,20,27,.92);border-bottom-color:#26333f}.rb-nav .brand,.rb-nav li a{color:#e9eef3}.rb-nav li a:hover{background:#1b2530}.rb-nav .cta a,.rb-nav .cta a:hover{background:#d8332e}}'
        '@media(max-width:899px){.rb-nav>div{gap:0;padding-top:8px}.rb-nav ul{margin:0 -16px;padding:6px 16px 8px;width:calc(100% + 32px);overflow-x:auto;scrollbar-width:none}.rb-nav li a{padding:7px 11px;font-size:14px;background:var(--soft,#e1e9e1)}.rb-nav .cta a{background:#e5322d}}'
        '.top .back{display:none}')
    bloco = ('<!-- menu:ini --><style>' + css + '</style><nav class="rb-nav" aria-label="Menu principal"><div><a class="brand" href="/">'
             + LOGO + '<span><b>RADAR</b><b>BRAGANÇA</b></span></a><ul class="desktop-nav">' + itens + '</ul>' + menu_mobile("voz") + '</div></nav><!-- menu:fim -->\n')
    if "/assets/mobile-nav.css?" not in h:
        h = h.replace("</head>", '<link rel="stylesheet" href="/assets/mobile-nav.css?v=4">\n' + "</head>", 1)
    h = h.replace("<body>\n", "<body>\n" + bloco, 1)
    open(pd, "w", encoding="utf-8").write(dados_formulario(h, D))

print(f"Páginas geradas: início, vereadores, {len(V)} vereadores, bairros, propostas, sobre.")
