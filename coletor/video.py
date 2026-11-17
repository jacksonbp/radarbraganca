# -*- coding: utf-8 -*-
"""
Gera o vídeo vertical (Reels/Stories, 1080x1920, 30 fps) do Radar Bragança a partir de site/dados.js.
Todos os números vêm dos dados do site. Ordem dos vereadores: alfabética (mesma régua para todos).

Uso: python coletor/video.py <ffmpeg.exe>
Saída: video/radar_braganca.mp4
"""
import glob, json, math, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = sys.argv[1]
D = json.loads(open(os.path.join(RAIZ, "site", "dados.js"), encoding="utf-8").read()[len("window.RB="):].rstrip().rstrip(";"))
V = sorted(D["v"], key=lambda v: v["ap"])
W, H, FPS = 1080, 1920, 30
FT = "C:/Windows/Fonts/"
_fc = {}
def F(n, s):
    k = (n, s)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FT + n, s)
    return _fc[k]
BLACK, BOLD, REG = "ariblk.ttf", "segoeuib.ttf", "segoeui.ttf"
INK, RED, MUTE, SOFT, WHITE = (17, 26, 36), (229, 50, 45), (93, 105, 118), (244, 246, 248), (255, 255, 255)
BLUE, ORANGE, PINK, GREEN, BAD = (31, 95, 214), (210, 87, 15), (196, 42, 110), (11, 135, 88), (207, 58, 46)
nf = lambda n: f"{int(round(n)):,}".replace(",", ".")
brl = lambda x: "R$ " + f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
ease = lambda t: 1 - (1 - max(0, min(1, t))) ** 3


def texto(d, xy, s, fonte, cor, anchor="la"):
    d.text(xy, s, font=fonte, fill=cor, anchor=anchor)


def quebra(d, s, fonte, largura):
    linhas, atual = [], ""
    for p in s.split():
        t = (atual + " " + p).strip()
        if d.textlength(t, font=fonte) <= largura:
            atual = t
        else:
            linhas.append(atual); atual = p
    return linhas + [atual]


def radar(d, cx, cy, r, cor_arco=INK):
    d.ellipse([cx - r * .28, cy - r * .28, cx + r * .28, cy + r * .28], fill=RED)
    for k in (.62, 1.0):
        b = [cx - r * k, cy - r * k, cx + r * k, cy + r * k]
        d.arc(b, 128, 232, fill=cor_arco, width=int(r * .16))
        d.arc(b, -52, 52, fill=cor_arco, width=int(r * .16))


def faixa(d):
    x = 0
    for col, w in [(BLUE, .62), (ORANGE, .2), (PINK, .08), (GREEN, .05), (MUTE, .05)]:
        d.rectangle([x, 0, x + int(W * w), 14], fill=col); x += int(W * w)


def rodape(d, txt="Fonte: Câmara Municipal de Bragança Paulista · dados oficiais"):
    texto(d, (W // 2, H - 70), txt, F(REG, 30), MUTE, "mm")


def foto_redonda(path, lado):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bb = im.getchannel("A").getbbox()
        if bb: im = im.crop(bb)
        bg = Image.new("RGB", im.size, WHITE); bg.paste(im, mask=im.getchannel("A")); im = bg
    im = im.convert("RGB")
    w, h = im.size; q = min(w, h)
    im = im.crop(((w - q) // 2, 0, (w - q) // 2 + q, q)).resize((lado, lado), Image.LANCZOS)
    m = Image.new("L", (lado * 3, lado * 3), 0); ImageDraw.Draw(m).ellipse([0, 0, lado * 3, lado * 3], fill=255)
    im.putalpha(m.resize((lado, lado), Image.LANCZOS))
    return im


# ------------------------------------------------------------------ cenas (cada uma devolve uma função quadro(t) e a duração)
def cena_abertura():
    def q(t):
        im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im); faixa(d)
        a = ease(t / .6)
        radar(d, W // 2, 560, 150 * (0.6 + .4 * a))
        texto(d, (W // 2, 860), "RADAR", F(BLACK, 170), INK, "mm")
        texto(d, (W // 2, 1040), "BRAGANÇA", F(BLACK, 150), RED, "mm")
        if t > .8:
            for k, l in enumerate(["O que cada vereador de", "Bragança Paulista fez", "desde a posse."]):
                texto(d, (W // 2, 1260 + k * 78), l, F(BOLD, 62), INK, "mm")
        if t > 1.6:
            d.rounded_rectangle([200, 1560, 880, 1650], 45, fill=SOFT)
            texto(d, (W // 2, 1605), "Só dados oficiais da Câmara", F(BOLD, 42), INK, "mm")
        rodape(d, "bragancaterraquerida.com.br")
        return im
    return q, 3.5


def cena_numero(eyebrow, grande, cor, linhas, nota=None, dur=4.5, de=None):
    def q(t):
        im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im); faixa(d)
        texto(d, (W // 2, 470), eyebrow.upper(), F(BOLD, 40), MUTE, "mm")
        val = grande
        if de is not None:
            val = nf(de + (int(grande.replace(".", "")) - de) * ease(t / 1.2))
        texto(d, (W // 2, 720), val, F(BLACK, 230 if len(val) <= 6 else 190), cor, "mm")
        for k, l in enumerate(linhas):
            texto(d, (W // 2, 940 + k * 84), l, F(BOLD, 66), INK, "mm")
        if nota and t > 1.0:
            ys = 940 + len(linhas) * 84 + 80
            for k, l in enumerate(quebra(d, nota, F(REG, 44), 900)):
                texto(d, (W // 2, ys + k * 60), l, F(REG, 44), MUTE, "mm")
        rodape(d)
        return im
    return q, dur


def cena_cidade():
    c = D["catot"]
    def q(t):
        im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im); faixa(d)
        texto(d, (W // 2, 360), "DESDE A POSSE, A CÂMARA RECEBEU", F(BOLD, 40), MUTE, "mm")
        tot = len(D["items"])
        texto(d, (W // 2, 520), nf(tot * ease(t / 1.2)), F(BLACK, 200), INK, "mm")
        texto(d, (W // 2, 680), "propostas dos 19 vereadores", F(BOLD, 60), INK, "mm")
        rows = [("Pedidos nos bairros", c.get("b", 0), BLUE), ("Perguntas e cobranças", c.get("c", 0), ORANGE),
                ("Homenagens", c.get("h", 0), PINK), ("Propostas de lei", c.get("l", 0), GREEN), ("Outros", c.get("o", 0), MUTE)]
        for k, (nome, n, cor) in enumerate(rows):
            a = ease((t - .6 - k * .25) / .5)
            if a <= 0: continue
            y = 840 + k * 150
            d.rounded_rectangle([90, y, 990, y + 120], 30, fill=SOFT)
            d.ellipse([130, y + 46, 158, y + 74], fill=cor)
            texto(d, (190, y + 60), nome, F(BOLD, 46), INK, "lm")
            texto(d, (950, y + 60), nf(n), F(BLACK, 58), cor, "rm")
        if t > 2.2:
            texto(d, (W // 2, 1660), f"Para cada proposta de lei, {nf(c.get('b', 0) / max(1, c.get('l', 1)))} pedidos de bairro.", F(BOLD, 44), INK, "mm")
        rodape(d)
        return im
    return q, 6.0


def cena_rua():
    g = D["rep"][0]
    MES = "jan fev mar abr mai jun jul ago set out nov dez".split()
    ma = lambda s: f"{MES[int(s[4:6]) - 1]}/{s[:4]}"
    tema = {"asf": "asfalto e buracos", "lim": "limpeza e poda", "luz": "iluminação", "tra": "trânsito", "agu": "água e esgoto"}.get(g["th"], "melhoria")
    def q(t):
        im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im); faixa(d)
        texto(d, (W // 2, 380), "O PROBLEMA QUE NÃO SOME", F(BOLD, 42), MUTE, "mm")
        texto(d, (W // 2, 600), nf(g["n"] * ease(t / 1.0)), F(BLACK, 300), RED, "mm")
        texto(d, (W // 2, 790), f"pedidos de {tema}", F(BOLD, 64), INK, "mm")
        for k, l in enumerate(quebra(d, g["r"], F(BLACK, 70), 940)):
            texto(d, (W // 2, 930 + k * 90), l, F(BLACK, 70), INK, "mm")
        y = 930 + len(quebra(d, g["r"], F(BLACK, 70), 940)) * 90 + 10
        texto(d, (W // 2, y), g["b"] or "Bragança Paulista", F(BOLD, 50), MUTE, "mm")
        texto(d, (W // 2, y + 110), f"{g['a']} vereadores pediram · de {ma(g['d0'])} a {ma(g['d1'])}", F(BOLD, 46), INK, "mm")
        if t > 1.5:
            for k, l in enumerate(["Pedido repetido não prova que a Prefeitura", "ignorou, mas mostra onde o problema volta."]):
                texto(d, (W // 2, y + 260 + k * 60), l, F(REG, 42), MUTE, "mm")
        rodape(d, "Fonte: Indicações oficiais da Câmara (SISCAM)")
        return im
    return q, 5.5


def cena_transicao():
    def q(t):
        im = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(im)
        texto(d, (W // 2, 820), "E cada um", F(BLACK, 110), WHITE, "mm")
        texto(d, (W // 2, 960), "dos 19 vereadores?", F(BLACK, 84), (255, 143, 139), "mm")
        texto(d, (W // 2, 1140), "Em ordem alfabética, com a mesma régua.", F(BOLD, 46), (184, 194, 204), "mm")
        for k, (s, cor) in enumerate([("Presença nas sessões", WHITE), ("Propostas que fez", (109, 156, 255)), ("Bairro com mais pedidos", (255, 143, 139))]):
            if t > .8 + k * .5:
                y = 1320 + k * 110
                d.rounded_rectangle([170, y - 44, W - 170, y + 44], 44, fill=(40, 48, 58))
                texto(d, (W // 2, y), s, F(BOLD, 48), cor, "mm")
        return im
    return q, 6.0


FOTOS = {}
def cena_vereador(v, idx):
    p = (glob.glob(os.path.join(RAIZ, "video", "fotos", f"{v['id']}.*")) or glob.glob(os.path.join(RAIZ, "site", "fotos", f"{v['id']}.jpg")))
    foto = foto_redonda(p[0], 440) if p else None
    tP = v["P"] + v["A"] + v["F"]
    cm = v.get("cm") or {"P": 0, "A": 0, "F": 0}
    tC = cm["P"] + cm["A"] + cm["F"]
    tot = sum(v["cat"].values())
    vg = v.get("vg") or []
    hue = (idx * 47 + 200) % 360
    import colorsys
    tint = tuple(int(c * 255) for c in colorsys.hls_to_rgb(hue / 360, .94, .85))
    deep = tuple(int(c * 255) for c in colorsys.hls_to_rgb(hue / 360, .26, .55))
    tiles = [
        ("Presença no plenário", f"{round(v['P'] / tP * 100)}%" if tP else "—", f"{v['P']} de {tP} sessões · {v['F']} falta{'s' if v['F'] != 1 else ''}", INK),
        ("Presença nas comissões", f"{round(cm['P'] / tC * 100)}%" if tC else "—", f"{cm['P']} de {tC} sessões · {cm['F']} falta{'s' if cm['F'] != 1 else ''}" if tC else "sem lista de presença registrada", INK),
        ("Propostas desde a posse", nf(tot), f"{nf(v['cat']['b'])} pedidos · {nf(v['cat']['l'])} de lei · {nf(v['cat']['h'])} homenagens", BLUE),
        ("Viagens oficiais", nf(len(vg)), brl(v.get("vgt") or 0) + " em despesas" if vg else "nenhuma registrada", ORANGE),
    ]
    def q(t):
        im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im); faixa(d)
        d.rectangle([0, 14, W, 760], fill=tint)
        texto(d, (60, 70), f"{idx + 1}/19", F(BOLD, 36), deep)
        radar(d, W - 110, 95, 38)
        a = ease(t / .45)
        if foto:
            lado = 440
            x, y = (W - lado) // 2, 110 + int(40 * (1 - a))
            d.ellipse([x - 12, y - 12, x + lado + 12, y + lado + 12], fill=WHITE)
            im.paste(foto, (x, y), foto)
        nm = v["ap"]
        fs = 92 if d.textlength(nm, font=F(BLACK, 92)) < 960 else 72
        texto(d, (W // 2, 640), nm, F(BLACK, fs), deep, "mm")
        pt = v["part"] + (f"  ·  {v['mesa']} da Câmara" if v.get("mesa") else "")
        pw = d.textlength(pt, font=F(BOLD, 40))
        d.rounded_rectangle([W // 2 - pw / 2 - 26, 700, W // 2 + pw / 2 + 26, 756], 14, fill=INK)
        texto(d, (W // 2, 728), pt, F(BOLD, 40), WHITE, "mm")
        for k, (lab, big, sub, cor) in enumerate(tiles):
            b = ease((t - .25 - k * .18) / .4)
            if b <= 0: continue
            y = 810 + k * 235 + int(30 * (1 - b))
            d.rounded_rectangle([60, y, W - 60, y + 210], 32, fill=SOFT)
            texto(d, (100, y + 48), lab.upper(), F(BOLD, 34), MUTE, "lm")
            texto(d, (100, y + 128), big, F(BLACK, 92), cor, "lm")
            bw = d.textlength(big, font=F(BLACK, 92))
            ls = quebra(d, sub, F(BOLD, 38), W - 60 - (100 + bw + 40) - 40)[:2]
            for j, l in enumerate(ls):
                texto(d, (100 + bw + 40, y + 128 + (j - (len(ls) - 1) / 2) * 46), l, F(BOLD, 38), INK, "lm")
        txt = f"Votos em 2024: {nf(v['vot'])} (TSE)" if v.get("vot") else ""
        texto(d, (W // 2, 1790), txt, F(BOLD, 36), MUTE, "mm")
        rodape(d, "Fontes: Câmara (SISCAM), Portal da Transparência e TSE")
        return im
    return q, 3.4


TEMAS = {"luz": "Iluminação", "asf": "Asfalto e buracos", "tra": "Trânsito", "agu": "Água e esgoto", "lim": "Limpeza e poda",
         "cal": "Calçadas", "laz": "Praças e lazer", "sau": "Saúde", "edu": "Escolas", "seg": "Segurança", "bus": "Ônibus"}


def limpa_rua(s):
    s = re.sub(r"\s*\)+\s*$", "", s or "").strip(" .,-")
    return s if s.count("(") <= s.count(")") else s.split("(")[0].strip()


def cena_pedidos(v, idx):
    from collections import Counter
    i = D["v"].index(v)
    its = [it for it in D["items"] if i in it[6]]
    b = [it for it in its if it[4] == "b"]
    cnt = Counter(it[4] for it in its)
    bai = [(k, n) for k, n in Counter(it[10] for it in b if it[10]).most_common(3) if n >= 2]
    tem = [(TEMAS.get(k, k), n) for k, n in Counter(it[8] for it in b if it[8]).most_common(3)]
    rua = [(r, ba, n) for (r, ba), n in Counter((limpa_rua(it[9]), it[10]) for it in b if it[9]).most_common(1) if n >= 3]
    p = (glob.glob(os.path.join(RAIZ, "video", "fotos", f"{v['id']}.*")) or [None])[0]
    foto = foto_redonda(p, 170) if p else None
    import colorsys
    hue = (idx * 47 + 200) % 360
    tint = tuple(int(c * 255) for c in colorsys.hls_to_rgb(hue / 360, .94, .85))
    deep = tuple(int(c * 255) for c in colorsys.hls_to_rgb(hue / 360, .26, .55))
    def q(t):
        im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im); faixa(d)
        d.rectangle([0, 14, W, 250], fill=tint)
        if foto:
            im.paste(foto, (60, 48), foto)
        nm = v["ap"]; fs = 64 if d.textlength(nm, font=F(BLACK, 64)) < 760 else 50
        texto(d, (260, 105), nm, F(BLACK, fs), deep, "lm")
        texto(d, (260, 180), "O que pediu e propôs", F(BOLD, 44), INK, "lm")
        y = 300
        a = ease(t / .4)
        texto(d, (70, y + 30), "PEDIDOS DE MELHORIA NOS BAIRROS", F(BOLD, 36), MUTE, "lm")
        texto(d, (70, y + 120), nf(len(b) * a), F(BLACK, 120), BLUE, "lm")
        y += 210
        if bai:
            texto(d, (70, y + 20), "Bairros com mais pedidos", F(BOLD, 40), INK, "lm")
            mx = bai[0][1]
            for k, (nome, n) in enumerate(bai):
                bb = ease((t - .3 - k * .15) / .4)
                yy = y + 70 + k * 105
                nome_c = nome if d.textlength(nome, font=F(BOLD, 38)) < 760 else nome[:34] + "…"
                texto(d, (70, yy + 18), nome_c, F(BOLD, 38), INK, "lm")
                texto(d, (W - 70, yy + 18), nf(n), F(BLACK, 44), BLUE, "rm")
                d.rounded_rectangle([70, yy + 48, W - 70, yy + 66], 9, fill=SOFT)
                d.rounded_rectangle([70, yy + 48, 70 + int((W - 140) * n / mx * bb) + 1, yy + 66], 9, fill=BLUE)
            y += 70 + len(bai) * 105 + 20
        elif b:
            texto(d, (70, y + 20), "Poucos pedidos com bairro identificado.", F(REG, 40), MUTE, "lm"); y += 80
        if tem:
            texto(d, (70, y + 20), "Assuntos mais pedidos", F(BOLD, 40), INK, "lm")
            x, yy = 70, y + 70
            for k, (nome, n) in enumerate(tem):
                if ease((t - .8 - k * .15) / .3) <= 0: continue
                s = f"{nome}  {nf(n)}"
                w = d.textlength(s, font=F(BOLD, 38)) + 50
                if x + w > W - 60: x, yy = 70, yy + 82
                d.rounded_rectangle([x, yy, x + w, yy + 64], 32, fill=SOFT)
                texto(d, (x + 25, yy + 32), s, F(BOLD, 38), INK, "lm")
                x += w + 18
            y = yy + 100
        if rua and t > 1.4:
            r, ba, n = rua[0]
            d.rounded_rectangle([60, y, W - 60, y + 190], 30, fill=(255, 241, 230))
            texto(d, (95, y + 42), f"RUA QUE MAIS PEDIU · {n} VEZES", F(BOLD, 34), ORANGE, "lm")
            ls = quebra(d, r, F(BLACK, 46), W - 190)
            for k, l in enumerate(ls[:2]):
                texto(d, (95, y + 98 + k * 52), l, F(BLACK, 46), INK, "lm")
            if len(ls) == 1 and ba:
                texto(d, (95, y + 152), ba[:44], F(BOLD, 36), MUTE, "lm")
            y += 215
        # outros números, mesma régua para todos
        yb = max(y + 10, 1520)
        caixas = [("Cobranças", cnt.get("c", 0), ORANGE), ("De lei", cnt.get("l", 0), GREEN), ("Homenagens", cnt.get("h", 0), PINK)]
        cw = (W - 120 - 40) // 3
        for k, (lab, n, cor) in enumerate(caixas):
            x0 = 60 + k * (cw + 20)
            d.rounded_rectangle([x0, yb, x0 + cw, yb + 170], 28, fill=SOFT)
            texto(d, (x0 + cw // 2, yb + 70), nf(n), F(BLACK, 72), cor, "mm")
            texto(d, (x0 + cw // 2, yb + 135), lab, F(BOLD, 34), INK, "mm")
        texto(d, (W // 2, H - 125), "Bairros e ruas lidos do texto oficial de cada pedido.", F(REG, 30), MUTE, "mm")
        rodape(d, "Fonte: proposituras oficiais da Câmara (SISCAM)")
        return im
    return q, 4.2


def cena_propaganda():
    shot = Image.open(os.path.join(RAIZ, "video", "site_topo.png")).convert("RGB")
    pw = 600; ph = int(shot.height * pw / shot.width)
    shot = shot.resize((pw, ph), Image.LANCZOS)
    def q(t):
        im = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(im)
        texto(d, (W // 2, 150), "Quer ver o que pediram", F(BLACK, 72), WHITE, "mm")
        texto(d, (W // 2, 245), "para a SUA rua?", F(BLACK, 72), (255, 143, 139), "mm")
        # celular com o site rolando
        a = ease(t / .6)
        cx, top = W // 2, 360 + int(80 * (1 - a))
        fw, fh = pw + 40, 900
        d.rounded_rectangle([cx - fw // 2, top, cx + fw // 2, top + fh], 70, fill=(40, 48, 58))
        tela = Image.new("RGB", (pw, fh - 60), WHITE)
        rol = int(max(0, min(ph - (fh - 60), (ph - (fh - 60)) * ease((t - 1.2) / 3.5))))
        tela.paste(shot.crop((0, rol, pw, rol + fh - 60)), (0, 0))
        m = Image.new("L", tela.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, tela.width, tela.height], 50, fill=255)
        im.paste(tela, (cx - pw // 2, top + 30), m)
        y = top + fh + 70
        itens = ["Busque o seu bairro ou a sua rua", "Presença, votos e viagens de cada um", "Cobre o vereador pelo WhatsApp"]
        for k, s in enumerate(itens):
            b = ease((t - .8 - k * .35) / .4)
            if b <= 0: continue
            d.ellipse([150, y + k * 78 - 14, 178, y + k * 78 + 14], fill=RED)
            texto(d, (205, y + k * 78), s, F(BOLD, 46), WHITE, "lm")
        if t > 2.4:
            p = .5 + .5 * math.sin(t * 5)
            d.rounded_rectangle([60, 1610, W - 60, 1760], 40, fill=RED)
            texto(d, (W // 2, 1685), "bragancaterraquerida.com.br", F(BLACK, 58), WHITE, "mm")
            texto(d, (W // 2, 1830), "Link na bio  ·  só dados oficiais  ·  atualizado todo dia", F(BOLD, 36), (184, 194, 204), "mm")
        return im
    return q, 6.5


def cena_final():
    def q(t):
        im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im); faixa(d)
        radar(d, W // 2, 600, 140)
        texto(d, (W // 2, 860), "RADAR", F(BLACK, 160), INK, "mm")
        texto(d, (W // 2, 1030), "BRAGANÇA", F(BLACK, 140), RED, "mm")
        texto(d, (W // 2, 1230), "www.bragancaterraquerida.com.br", F(BOLD, 54), INK, "mm")
        for k, l in enumerate(["Achou um erro? Escreva para", "contato@bragancaterraquerida.com.br"]):
            texto(d, (W // 2, 1420 + k * 60), l, F(REG, 42), MUTE, "mm")
        texto(d, (W // 2, 1640), "Compartilhe com quem mora em Bragança", F(BOLD, 46), RED, "mm")
        rodape(d, "Fontes: Câmara Municipal (SISCAM), Portal da Transparência e TSE")
        return im
    return q, 3.5


cenas = [cena_abertura(), cena_cidade(),
         cena_numero("Votações com voto de cada um", f"{round(D['unan'] / D['nvot'] * 100)}%", INK,
                     ["das votações:", "todos votaram igual"], nota=f"{D['unan']} de {D['nvot']} votações nominais desde {D['pri'][8:10]}/{D['pri'][5:7]}/{D['pri'][:4]}."),
         cena_rua(), cena_transicao()] + [c for i, v in enumerate(V) for c in (cena_vereador(v, i), cena_pedidos(v, i))] + [cena_propaganda(), cena_final()]

if os.environ.get("DURS"):  # tempos de cada cena ajustados à narração gravada
    _d = json.load(open(os.environ["DURS"]))["durs"]
    assert len(_d) == len(cenas), (len(_d), len(cenas))
    cenas = [(q, d) for (q, _), d in zip(cenas, _d)]

if os.environ.get("PREVIA"):  # só tira fotos de algumas cenas, para conferir o visual
    pasta = os.path.join(RAIZ, "video", "previa"); os.makedirs(pasta, exist_ok=True)
    for k in [int(x) for x in os.environ["PREVIA"].split(",")]:
        q, dur = cenas[k]
        q(dur - 0.05).save(os.path.join(pasta, f"cena{k:02d}.png"))
    sys.exit(0)

total = sum(d for _, d in cenas)
print(f"{len(cenas)} cenas, {total:.1f} s")
out = os.path.join(RAIZ, "video", "radar_braganca.mp4")
cmd = [FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
FADE = 0.25
anterior = None
for k, (q, dur) in enumerate(cenas):
    n = int(round(dur * FPS))
    for f in range(n):
        t = f / FPS
        im = q(t)
        if anterior is not None and t < FADE:  # transição suave entre cenas
            im = Image.blend(anterior, im, t / FADE)
        pr.stdin.write(im.tobytes())
        if f == n - 1:
            anterior = im
    print(f"  cena {k + 1}/{len(cenas)}")
pr.stdin.close(); pr.wait()
print("Pronto:", out)
