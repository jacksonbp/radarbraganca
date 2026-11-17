# -*- coding: utf-8 -*-
"""
Gera o vídeo vertical (Reels, 1080x1920, 30 fps) que apresenta a página "Voz do Bairro".
Não mostra endereço de site: termina pedindo para comentar EU QUERO.

Uso: python coletor/video_voz.py <ffmpeg.exe> <pasta com vazio.png, cheio.png e ok.png>
     (as três imagens são capturas da página em formato de celular, com 800 px de largura)
Saída: video/voz_do_bairro.mp4
PREVIA=1 no ambiente: só salva uma foto de cada cena em video/previa_voz/.
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF, SHOTS = sys.argv[1], sys.argv[2]
W, H, FPS = 1080, 1920, 30
FT = "C:/Windows/Fonts/"
_fc = {}
def F(n, s):
    if (n, s) not in _fc:
        _fc[(n, s)] = ImageFont.truetype(FT + n, s)
    return _fc[(n, s)]
BLACK, BOLD, REG = "ariblk.ttf", "segoeuib.ttf", "segoeui.ttf"
INK, RED, MUTE, SOFT, WHITE, GREEN = (17, 26, 36), (229, 50, 45), (93, 105, 118), (244, 246, 248), (255, 255, 255), (11, 135, 88)
ease = lambda t: 1 - (1 - max(0, min(1, t))) ** 3
io = lambda t: (lambda x: x * x * (3 - 2 * x))(max(0, min(1, t)))  # começa e termina devagar

# Celular: tela de 760 px de largura.
SX, SY, SW, SH = 160, 470, 760, 1300
def carrega(nome):
    im = Image.open(os.path.join(SHOTS, nome + ".png")).convert("RGB")
    return im.resize((SW, round(im.height * SW / im.width)), Image.LANCZOS)
TELAS = {n: carrega(n) for n in ("vazio", "cheio", "ok")}
K = SW / 800  # fator entre a captura (800 px) e a tela do celular
_mask = Image.new("L", (SW, SH), 0); ImageDraw.Draw(_mask).rounded_rectangle([0, 0, SW, SH], 48, fill=255)


def base(titulo_num=None):
    im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 14], fill=RED)
    return im, d


def radar(d, cx, cy, r):
    d.ellipse([cx - r * .28, cy - r * .28, cx + r * .28, cy + r * .28], fill=RED)
    for k in (.62, 1.0):
        b = [cx - r * k, cy - r * k, cx + r * k, cy + r * k]
        d.arc(b, 128, 232, fill=INK, width=int(r * .16)); d.arc(b, -52, 52, fill=INK, width=int(r * .16))


def rodape(d):
    d.text((W // 2, H - 60), "Bragança Terra Querida · projeto independente", font=F(REG, 34), fill=MUTE, anchor="mm")


def etiqueta(d, cx, cy, s="VOZ DO BAIRRO", tam=40):
    f = F(BOLD, tam); w = d.textlength(s, font=f) + tam * 1.6
    d.rounded_rectangle([cx - w / 2, cy - tam * .95, cx + w / 2, cy + tam * .95], tam, fill=INK)
    d.text((cx, cy - 2), s, font=f, fill=WHITE, anchor="mm")


def celular(im, d, tela, y):
    d.rounded_rectangle([SX - 18, SY - 18, SX + SW + 18, SY + SH + 18], 64, fill=INK)
    src = TELAS[tela]
    y = int(max(0, min(src.height - SH, y)))
    im.paste(src.crop((0, y, SW, y + SH)), (SX, SY), _mask)


def legenda(d, num, linhas, a=1.0):
    """Título de cada passo, acima do celular."""
    dy = int((1 - a) * 30)
    if num:
        d.ellipse([70, 150 + dy, 190, 270 + dy], fill=RED)
        d.text((130, 206 + dy), num, font=F(BLACK, 76), fill=WHITE, anchor="mm")
    x = 220 if num else 70
    for k, l in enumerate(linhas):
        d.text((x, 172 + k * 84 + dy), l, font=F(BLACK, 64), fill=INK, anchor="lm")


def cena_gancho():
    frases = [("Buraco na rua?", 0.0), ("Poste apagado?", 1.45), ("Mato alto?", 2.7)]
    def q(t):
        im, d = base()
        for k, (s, t0) in enumerate(frases):
            if t >= t0:
                a = ease((t - t0) / .35)
                d.text((W // 2, 620 + k * 230 + int((1 - a) * 40)), s, font=F(BLACK, 118), fill=RED if k == 2 else INK, anchor="mm")
        rodape(d)
        return im
    return q, 3.6


def cena_titulo():
    def q(t):
        im, d = base()
        a = ease(t / .5)
        radar(d, W // 2, 520, 130 * (.7 + .3 * a))
        etiqueta(d, W // 2, 770, tam=54)
        for k, l in enumerate(["Agora o problema", "do seu bairro", "chega aos vereadores."]):
            if t > .5 + k * .35:
                d.text((W // 2, 960 + k * 120), l, font=F(BLACK, 86), fill=INK, anchor="mm")
        if t > 3.6:
            d.rounded_rectangle([190, 1390, 890, 1490], 50, fill=SOFT)
            d.text((W // 2, 1438), "É simples e leva 1 minuto", font=F(BOLD, 46), fill=INK, anchor="mm")
        rodape(d)
        return im
    return q, 5.0


def cena_tela(tela, y0, y1, num, linhas, dur, espera=.9, destaque=None):
    def q(t):
        im, d = base()
        legenda(d, num, linhas, ease(t / .4))
        y = y0 + (y1 - y0) * io((t - espera) / max(.1, dur - espera - .8))
        celular(im, d, tela, y * K)
        if destaque and t > 0.6:  # contorno vermelho em volta de um trecho da tela
            x0, ya, x1, yb = [v * K for v in destaque]
            p = 6 + 4 * abs(((t * 1.5) % 2) - 1)
            topo, fundo = SY + ya - y * K - p, SY + yb - y * K + p
            if topo >= SY and fundo <= SY + SH:  # só quando o trecho está visível na tela
                d.rounded_rectangle([SX + x0 - p, topo, SX + x1 + p, fundo], 22, outline=RED, width=8)
        rodape(d)
        return im
    return q, dur


def cena_encaminha():
    def q(t):
        im, d = base()
        etiqueta(d, W // 2, 330, tam=44)
        for k, l in enumerate(["Nós recebemos", "e encaminhamos"]):
            d.text((W // 2, 560 + k * 130), l, font=F(BLACK, 100), fill=INK, anchor="mm")
        itens = [("aos vereadores", 1.7), ("à Câmara Municipal", 2.7)]
        for k, (s, t0) in enumerate(itens):
            if t >= t0:
                a = ease((t - t0) / .35); y = 930 + k * 190
                d.rounded_rectangle([130, y - 70, 950, y + 70], 40, fill=SOFT)
                d.ellipse([170, y - 34, 238, y + 34], fill=GREEN)
                d.line([186, y + 2, 200, y + 16, 224, y - 14], fill=WHITE, width=9, joint="curve")
                d.text((270 + int((1 - a) * 30), y - 4), s, font=F(BOLD, 62), fill=INK, anchor="lm")
        if t > 4.3:
            for k, l in enumerate(["Mesmo tratamento para todos.", "Sem partido e sem opinião."]):
                d.text((W // 2, 1400 + k * 70), l, font=F(REG, 48), fill=MUTE, anchor="mm")
        rodape(d)
        return im
    return q, 5.2


def cena_final():
    def q(t):
        im, d = base()
        radar(d, W // 2, 330, 100)
        for k, l in enumerate(["Quer mandar o problema", "do seu bairro?"]):
            d.text((W // 2, 560 + k * 100), l, font=F(BLACK, 74), fill=INK, anchor="mm")
        if t > 2.0:
            a = ease((t - 2.0) / .4)
            d.text((W // 2, 850), "Comente", font=F(BOLD, 70), fill=INK, anchor="mm")
            p = 1 + .03 * abs(((t * 1.2) % 2) - 1)
            w, h = 760 * p * (.85 + .15 * a), 220 * p
            d.rounded_rectangle([W / 2 - w / 2, 1030 - h / 2, W / 2 + w / 2, 1030 + h / 2], 110, fill=RED)
            d.text((W // 2, 1022), "EU QUERO", font=F(BLACK, 128), fill=WHITE, anchor="mm")
        if t > 3.5:
            for k, l in enumerate(["que a gente te envia", "tudo no direct"]):
                d.text((W // 2, 1250 + k * 84), l, font=F(BOLD, 62), fill=INK, anchor="mm")
        if t > 4.3:  # balão de comentário
            d.rounded_rectangle([230, 1470, 850, 1610], 70, fill=SOFT)
            d.ellipse([260, 1500, 340, 1580], fill=MUTE)
            d.text((370, 1516), "você", font=F(REG, 34), fill=MUTE, anchor="lm")
            d.text((370, 1562), "eu quero", font=F(BOLD, 50), fill=INK, anchor="lm")
        rodape(d)
        return im
    return q, 6.5


def cena_pagina():
    """Fecha o vídeo divulgando a página Bragança Terra Querida no Instagram."""
    ROSA, CINZA = (255, 143, 139), (184, 194, 204)
    def q(t):
        im = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, W, 14], fill=RED)
        a = ease(t / .5)
        d.text((W // 2, 300), "Siga a página", font=F(BOLD, 64), fill=CINZA, anchor="mm")
        d.text((W // 2, 480 + int((1 - a) * 30)), "BRAGANÇA", font=F(BLACK, 128), fill=WHITE, anchor="mm")
        d.text((W // 2, 630 + int((1 - a) * 30)), "TERRA QUERIDA", font=F(BLACK, 98), fill=ROSA, anchor="mm")
        if t > .7:
            d.rounded_rectangle([150, 760, 930, 870], 55, fill=(40, 48, 58))
            d.text((W // 2, 812), "@bragancaterraqueridaoficial", font=F(BOLD, 48), fill=WHITE, anchor="mm")
        itens = ["Notícias e histórias de Bragança Paulista", "Política explicada sem enrolação", "+66 mil bragantinos acompanham"]
        for k, s in enumerate(itens):
            if t > 1.2 + k * .4:
                y = 1030 + k * 100
                d.ellipse([110, y - 16, 142, y + 16], fill=RED)
                d.text((175, y - 2), s, font=F(BOLD, 44), fill=WHITE, anchor="lm")
        if t > 2.8:
            p = 1 + .03 * abs(((t * 1.2) % 2) - 1)
            w, h = 640 * p, 150 * p
            d.rounded_rectangle([W / 2 - w / 2, 1480 - h / 2, W / 2 + w / 2, 1480 + h / 2], 75, fill=RED)
            d.text((W // 2, 1474), "SEGUIR", font=F(BLACK, 88), fill=WHITE, anchor="mm")
            d.text((W // 2, 1650), "Curta e compartilhe com quem mora em Bragança", font=F(BOLD, 40), fill=CINZA, anchor="mm")
        return im
    return q, 5.5


cenas = [
    cena_gancho(),
    cena_titulo(),
    cena_tela("vazio", 0, 760, "1", ["Conte o que", "está acontecendo"], 6.0),
    cena_tela("cheio", 900, 1700, "2", ["Escolha para", "quem encaminhar"], 6.0, destaque=(20, 2422, 780, 2500)),
    cena_tela("cheio", 1700, 2330, None, ["Não precisa", "se identificar"], 4.8),
    cena_tela("ok", 0, 0, "3", ["Você recebe", "um protocolo"], 4.6, destaque=(52, 925, 210, 1000)),
    cena_encaminha(),
    cena_final(),
    cena_pagina(),
]

if os.environ.get("DURS"):  # duração de cada cena ajustada à narração gravada (segundos, separados por vírgula)
    _d = [float(x) for x in os.environ["DURS"].split(",")]
    assert len(_d) == len(cenas), (len(_d), len(cenas))
    cenas = [(q, d) for (q, _), d in zip(cenas, _d)]

if os.environ.get("PREVIA"):
    pasta = os.path.join(RAIZ, "video", "previa_voz"); os.makedirs(pasta, exist_ok=True)
    for k, (q, dur) in enumerate(cenas):
        q(dur - 0.05).save(os.path.join(pasta, f"cena{k + 1}.jpg"), quality=80)
    print("prévias em", pasta); sys.exit(0)

total = sum(d for _, d in cenas)
print(f"{len(cenas)} cenas, {total:.1f} s")
out = os.path.join(RAIZ, "video", "voz_do_bairro.mp4")
cmd = [FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
FADE, anterior = 0.25, None
for k, (q, dur) in enumerate(cenas):
    n = int(round(dur * FPS))
    for f in range(n):
        t = f / FPS
        im = q(t)
        if anterior is not None and t < FADE:
            im = Image.blend(anterior, im, t / FADE)
        pr.stdin.write(im.tobytes())
        if f == n - 1:
            anterior = im
    print(f"  cena {k + 1}/{len(cenas)}")
pr.stdin.close(); pr.wait()
print("Pronto:", out)
