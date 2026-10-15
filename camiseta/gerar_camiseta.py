"""Estampas da camiseta preta NEXT LEVEL 2026 (frente e costas), 100% vetoriais.

Tudo é pixel art: as fontes Press Start 2P e Silkscreen são convertidas na grade de
pixels delas (8 px por em) e cada pixel vira um retângulo vetorial. Assim o glitch
e as scanlines são exatos e o arquivo não depende de fontes instaladas.

Saídas por estampa: PDF e SVG em tamanho real (mm) e PNG 300 dpi com fundo transparente.
Uso: python3 gerar_camiseta.py [pasta_saida]
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.join(HERE, "fontes")
LION = open(os.path.join(HERE, "..", "paineis", "leao_64.txt")).read().split()

# paleta da identidade visual
VERDE = "#00E87A"     # Neon Green — cor primária
V_ESC = "#009650"     # verde escuro (sombras)
ROSA = "#FF0066"      # Hot Pink
R_ESC = "#99003D"     # rosa escuro (extrusão do LEVEL)
OURO = "#FFD700"      # Gold — estrelas e moedas
BRANCO = "#FFFFFF"

MM_PT = 72 / 25.4
DPI = 300


# ---------------------------------------------------------------- fontes pixel
def text_bitmap(text, font="PressStart2P-Regular.ttf"):
    """Bitmap (lista de listas bool) do texto na grade nativa da fonte (8 px por em)."""
    s = 16  # px de render por pixel da fonte
    f = ImageFont.truetype(os.path.join(FONTES, font), 8 * s)
    w = int(f.getlength(text)) + 4 * s
    im = Image.new("L", (w, 12 * s), 0)
    ImageDraw.Draw(im).text((2 * s, 9 * s), text, font=f, fill=255, anchor="ls")
    a = np.array(im)[s // 2::s, s // 2::s] > 127
    rows = np.flatnonzero(a.any(1))
    cols = np.flatnonzero(a.any(0))
    return a[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]


def heart():
    return np.array([[c == "#" for c in r] for r in
                     [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."]])


ICONS = {
    "heart": [".##.##.", "#o#####", "#######", ".#####.", "..###..", "...#..."],
    "coin": ["..####..", ".######.", "###oo###", "###oo###", "###oo###", "###oo###", ".######.", "..####.."],
    "star": ["....#....", "....#....", "...###...", "#########", ".#######.", "..#####..", "..##.##..",
             ".##...##.", ".#.....#."],
}


# ---------------------------------------------------------------- cena
class Cena:
    """Acumula retângulos coloridos (em mm, origem no topo-esquerdo)."""

    def __init__(self, w_mm, h_mm):
        self.w, self.h = w_mm, h_mm
        self.items = []  # (cor, [(x, y, w, h)])

    def grid(self, grid, x, y, cell):
        """grid: matriz 2D de cores (None = vazio). Mescla em retângulos por cor."""
        g = [list(r) for r in grid]
        gh = len(g)
        gw = len(g[0]) if gh else 0
        out = {}
        open_runs = {}
        for r in range(gh + 1):
            runs = {}
            if r < gh:
                k = 0
                while k < gw:
                    col = g[r][k]
                    j = k
                    while j < gw and g[r][j] == col:
                        j += 1
                    if col:
                        runs[(k, j, col)] = open_runs.get((k, j, col), r)
                    k = j
            for key, start in open_runs.items():
                if key not in runs:
                    a, b, col = key
                    out.setdefault(col, []).append((x + a * cell, y + start * cell, (b - a) * cell, (r - start) * cell))
            open_runs = runs
        for col, rects in out.items():
            self.items.append((col, rects))

    def mask(self, m, x, y, cell, color):
        self.grid([[color if v else None for v in row] for row in m], x, y, cell)

    def rows(self, rows, x, y, cell, colors):
        self.grid([[colors.get(ch) for ch in row] for row in rows], x, y, cell)

    def text(self, s, x, y, cell, color, font="Silkscreen-Regular.ttf", align="left"):
        m = text_bitmap(s, font)
        w = m.shape[1] * cell
        x = x - w / 2 if align == "center" else x - w if align == "right" else x
        self.mask(m, x, y, cell, color)
        return w, m.shape[0] * cell

    def box(self, x, y, w, h, color):
        self.items.append((color, [(x, y, w, h)]))

    # ---- saídas
    def pdf(self, path, title):
        # fonte inicial incorporada: o ReportLab sempre declara uma fonte; sem isso seria uma
        # Helvetica não incorporada (alerta na pré-impressão). Nenhum texto é escrito.
        if "PressStart2P" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("PressStart2P", os.path.join(FONTES, "PressStart2P-Regular.ttf")))
        c = canvas.Canvas(path, pagesize=(self.w * MM_PT, self.h * MM_PT), initialFontName="PressStart2P")
        c.setTitle(title)
        c.setAuthor("INTEENSOS · Next Level 2026")
        for col, rects in self.items:
            p = c.beginPath()
            for x, y, w, h in rects:
                p.rect(x * MM_PT, (self.h - y - h) * MM_PT, w * MM_PT, h * MM_PT)
            c.setFillColor(col)
            c.drawPath(p, stroke=0, fill=1)
        c.showPage()
        c.save()

    def svg(self, path):
        f = lambda v: f"{v:.3f}".rstrip("0").rstrip(".")
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{f(self.w)}mm" height="{f(self.h)}mm" '
               f'viewBox="0 0 {f(self.w)} {f(self.h)}" shape-rendering="crispEdges">']
        for col, rects in self.items:
            d = "".join(f"M{f(x)} {f(y)}h{f(w)}v{f(h)}h{f(-w)}z" for x, y, w, h in rects)
            out.append(f'<path fill="{col}" d="{d}"/>')
        out.append("</svg>")
        open(path, "w").write("\n".join(out))

    def png(self, path, bg=None):
        k = DPI / 25.4
        im = Image.new("RGBA", (round(self.w * k), round(self.h * k)), bg or (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for col, rects in self.items:
            for x, y, w, h in rects:
                x0, y0, x1, y1 = round(x * k), round(y * k), round((x + w) * k), round((y + h) * k)
                if x1 > x0 and y1 > y0:
                    d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=col)
        im.save(path, dpi=(DPI, DPI))
        return im


# ---------------------------------------------------------------- frente
def glitch_inteensos():
    """'INTEENSOS' com glitch: cópia rosa deslocada + faixas horizontais deslizadas.

    Trabalha numa grade 2x mais fina que o pixel da fonte, para fatias mais finas.
    """
    word = "INTEENSOS"
    m = text_bitmap(word, "PressStart2P-Regular.ttf")
    # cor por letra: IN e SOS verde, TEEN branco (monoespaçada: 8 px por letra)
    col = np.empty(m.shape, dtype=object)
    for i in range(len(word)):
        col[:, i * 8:(i + 1) * 8] = BRANCO if 2 <= i <= 5 else VERDE
    S = 2
    m = m.repeat(S, 0).repeat(S, 1)
    col = col.repeat(S, 0).repeat(S, 1)
    H, W = m.shape
    pad = 8
    g = np.full((H, W + 2 * pad), None, dtype=object)
    # cópia rosa (borda do glitch): deslocada para a esquerda e um pouco para baixo
    dx, dy = -1, 0
    for r in range(H):
        for c in range(W):
            if m[r, c]:
                rr, cc = r + dy, c + pad + dx
                if 0 <= rr < H:
                    g[rr, cc] = ROSA
    # texto principal por cima
    for r in range(H):
        for c in range(W):
            if m[r, c]:
                g[r, c + pad] = col[r, c]
    # faixas deslizadas (linhas da grade fina): (linha inicial, altura, deslocamento)
    for r0, hgt, sh in [(3, 2, 3), (10, 1, -2)]:
        band = g[r0:r0 + hgt].copy()
        g[r0:r0 + hgt] = None
        g[r0:r0 + hgt] = np.roll(band, sh, axis=1)
    # barras de ruído finas saindo do texto
    noise = np.full((H, W + 2 * pad), None, dtype=object)
    for r, c0, ln, cor in [(4, 0, 7, ROSA), (10, W + 2 * pad - 9, 9, VERDE)]:
        noise[r, c0:c0 + ln] = cor
    g = np.where(g == None, noise, g)  # noqa: E711
    return g


def frente(out):
    W, H = 120, 160  # mm (área da estampa no peito)
    cena = Cena(W, H)
    # leão: verde neon com sombras em verde escuro
    lc = 72 / len(LION[0])  # ~72 mm de largura
    lw, lh = len(LION[0]) * lc, len(LION) * lc
    cena.rows(LION, (W - lw) / 2, 0, lc, {"d": V_ESC, "m": VERDE, "l": VERDE, "h": VERDE})
    # inTEENsos com glitch
    g = glitch_inteensos()
    cell = 108 / g.shape[1]  # ~108 mm de largura total
    cena.grid(g, (W - g.shape[1] * cell) / 2, lh + 10, cell)
    cena.h = lh + 10 + g.shape[0] * cell + 2
    salvar(cena, out, "Camiseta_Frente_Leao_inTEENsos", "Camiseta Next Level - Frente")
    return cena


# ---------------------------------------------------------------- costas
def titulo(word, face, extr, p):
    """Título em Press Start 2P com extrusão em degraus (3D arcade) e scanlines na face."""
    m = text_bitmap(word, "PressStart2P-Regular.ttf")
    S = 4  # sub-grade
    m = m.repeat(S, 0).repeat(S, 1)
    H, W = m.shape
    depth = 3
    g = np.full((H + depth, W + depth), None, dtype=object)
    for k in range(depth, 0, -1):
        g[k:k + H, k:k + W][m] = extr
    face_rows = g[0:H, 0:W]
    face_rows[m] = face
    # scanlines: uma sub-linha vazada a cada 2 pixels da fonte (corta face e extrusão)
    for r in range(2 * S - 1, H + depth, 2 * S):
        g[r, :] = None
    return g, p / S


def costas(out):
    W, H = 300, 400  # mm (A3 aprox.)
    c = Cena(W, H)
    m, L, t = 14, 34, 3.2
    # cantos do HUD
    for (x, y, sx, sy) in [(m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)]:
        c.box(min(x, x + sx * L), min(y, y + sy * t), L, t, VERDE)
        c.box(min(x, x + sx * t), min(y, y + sy * L), t, L, VERDE)

    # HUD superior
    hp = 1.6  # mm por pixel do HUD
    top = 28
    c.text("1P", 28, top, hp, VERDE, font="Silkscreen-Bold.ttf")
    for i in range(4):
        cor = ROSA if i < 3 else None
        if cor:
            c.rows(ICONS["heart"], 28 + i * 9 * hp, top + 9 * hp, hp, {"#": ROSA, "o": BRANCO})
        else:  # coração vazio: só o contorno
            hm = heart()
            pad = np.pad(hm, 1)
            edge = hm & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
            c.mask(edge, 28 + i * 9 * hp, top + 9 * hp, hp, ROSA)
    rx = W - 28
    w25, _ = c.text("x 25", rx, top, hp, BRANCO, align="right")
    c.rows(ICONS["coin"], rx - w25 - 11 * hp, top - hp / 2, hp, {"#": OURO, "o": None})
    w03, _ = c.text("x 03", rx, top + 9 * hp, hp, BRANCO, align="right")
    c.rows(ICONS["star"], rx - w03 - 12 * hp, top + 8 * hp, hp, {"#": OURO})

    # ACAMPAMENTO
    y = 82
    c.text("ACAMPAMENTO", W / 2, y, 2.2, BRANCO, font="PressStart2P-Regular.ttf", align="center")

    # NEXT / LEVEL
    p = 5.0  # mm por pixel da fonte no título
    y = 112
    for word, face, extr in [("NEXT", VERDE, V_ESC), ("LEVEL", ROSA, R_ESC)]:
        g, cell = titulo(word, face, extr, p)
        c.grid(g, (W - g.shape[1] * cell) / 2, y, cell)
        y += g.shape[0] * cell + 2.2 * p

    # ★ 2026 ★
    y += 2
    w, h = c.text("2026", W / 2, y, 2.6, BRANCO, font="PressStart2P-Regular.ttf", align="center")
    sp = 2.0
    c.rows(ICONS["star"], W / 2 - w / 2 - 10 - 9 * sp, y - 1.5, sp, {"#": OURO})
    c.rows(ICONS["star"], W / 2 + w / 2 + 10, y - 1.5, sp, {"#": OURO})
    y += h + 26

    # barra de nível
    bw, bh, bt = 150, 14, 2
    bx = (W - bw) / 2
    lp = 1.5
    c.text("LVL 26", bx - 6, y + bh / 2 - 3.5 * lp, lp, BRANCO, font="Silkscreen-Bold.ttf", align="right")
    for r in [(bx, y, bw, bt), (bx, y + bh - bt, bw, bt), (bx, y, bt, bh), (bx + bw - bt, y, bt, bh)]:
        c.box(*r, BRANCO)
    segs, gap = 15, 2
    sw = (bw - 2 * bt - gap * (segs + 1)) / segs
    c.items.append((VERDE, [(bx + bt + gap + i * (sw + gap), y + bt + gap, sw, bh - 2 * bt - 2 * gap)
                            for i in range(11)]))
    c.text("73%", bx + bw + 6, y + bh / 2 - 3.5 * lp, lp, BRANCO, font="Silkscreen-Bold.ttf")
    y += bh + 26

    # ▶ PROSSIGO PARA O ALVO ◀
    sp_ = 1.4
    w, h = c.text("PROSSIGO PARA O ALVO", W / 2, y, sp_, VERDE, font="PressStart2P-Regular.ttf", align="center")
    arrow = ["#...", "##..", "###.", "####", "###.", "##..", "#..."]
    c.rows(arrow, W / 2 - w / 2 - 6 - 4 * sp_, y, sp_, {"#": ROSA})
    c.rows([r[::-1] for r in arrow], W / 2 + w / 2 + 6, y, sp_, {"#": ROSA})

    # rodapé: inTEENsos + selo LET'S START
    fy = H - 52
    fp = 1.1
    word = "INTEENSOS"
    x = 36
    for i, ch in enumerate(word):
        wch, _ = c.text(ch, x, fy, fp, BRANCO if 2 <= i <= 5 else VERDE, font="PressStart2P-Regular.ttf")
        x += 8 * fp
    label = "LET'S START"
    lm = text_bitmap(label, "PressStart2P-Regular.ttf")
    lp2 = 1.1
    tw, th = lm.shape[1] * lp2, lm.shape[0] * lp2
    pad = 3.3
    bx2 = W - 36 - tw - 2 * pad
    # selo rosa com texto vazado (a cor da camiseta aparece no texto)
    sel = np.full((lm.shape[0] + 2 * round(pad / lp2), lm.shape[1] + 2 * round(pad / lp2)), ROSA, dtype=object)
    o = round(pad / lp2)
    sel[o:o + lm.shape[0], o:o + lm.shape[1]][lm] = None
    c.grid(sel, bx2, fy - pad, lp2)

    salvar(c, out, "Camiseta_Costas_Tela_de_Game", "Camiseta Next Level - Costas")
    return c


def salvar(cena, out, nome, titulo_pdf):
    base = os.path.join(out, nome)
    cena.pdf(base + ".pdf", titulo_pdf)
    cena.svg(base + ".svg")
    cena.png(base + "_300dpi.png")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else HERE
    os.makedirs(out, exist_ok=True)
    frente(out)
    costas(out)
    print("ok")
