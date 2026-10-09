"""Gera os painéis luminosos NEXT LEVEL (3000x4124) em PDF 100% vetorial.

Toda a arte é pixel art desenhada como paths vetoriais (sem imagens embutidas).
Uso: python3 gerar_paineis.py <pasta_saida>
"""
import os
import random
import sys

from reportlab.pdfgen import canvas

W, H = 3000, 4124
HERE = os.path.dirname(os.path.abspath(__file__))

PALETA = {
    "verde": "#00E87A", "rosa": "#FF0066", "ouro": "#FFD700", "preto": "#07091A",
    "azul": "#7B8FD4", "branco": "#FFFFFF", "vesc": "#009650", "resc": "#640028",
}

# ---------------------------------------------------------------- fontes
# Fonte do título (mesma do banner: 7 linhas, traço de 2 pixels)
BOLD = {
    "N": ["##...##", "###..##", "####.##", "##.####", "##..###", "##...##", "##...##"],
    "E": ["#######", "##.....", "##.....", "######.", "##.....", "##.....", "#######"],
    "X": ["##...##", "##...##", ".##.##.", "..###..", ".##.##.", "##...##", "##...##"],
    "T": ["######", "..##..", "..##..", "..##..", "..##..", "..##..", "..##.."],
    "L": ["##....", "##....", "##....", "##....", "##....", "##....", "######"],
    "V": ["##...##", "##...##", "##...##", "###.###", ".#####.", "..###..", "...#..."],
    " ": ["...", "...", "...", "...", "...", "...", "..."],
}

# Fonte pequena 5x7 (textos de apoio)
SMALL_SRC = """
A .###. #...# #...# ##### #...# #...# #...#
B ####. #...# #...# ####. #...# #...# ####.
C .###. #...# #.... #.... #.... #...# .###.
D ####. #...# #...# #...# #...# #...# ####.
E ##### #.... #.... ####. #.... #.... #####
F ##### #.... #.... ####. #.... #.... #....
G .###. #...# #.... #.### #...# #...# .####
H #...# #...# #...# ##### #...# #...# #...#
I ##### ..#.. ..#.. ..#.. ..#.. ..#.. #####
J ..### ...#. ...#. ...#. #..#. #..#. .##..
K #...# #..#. #.#.. ##... #.#.. #..#. #...#
L #.... #.... #.... #.... #.... #.... #####
M #...# ##.## #.#.# #.#.# #...# #...# #...#
N #...# ##..# #.#.# #..## #...# #...# #...#
O .###. #...# #...# #...# #...# #...# .###.
P ####. #...# #...# ####. #.... #.... #....
Q .###. #...# #...# #...# #.#.# #..#. .##.#
R ####. #...# #...# ####. #.#.. #..#. #...#
S .#### #.... #.... .###. ....# ....# ####.
T ##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..
U #...# #...# #...# #...# #...# #...# .###.
V #...# #...# #...# #...# #...# .#.#. ..#..
W #...# #...# #...# #.#.# #.#.# ##.## #...#
X #...# #...# .#.#. ..#.. .#.#. #...# #...#
Y #...# #...# .#.#. ..#.. ..#.. ..#.. ..#..
Z ##### ....# ...#. ..#.. .#... #.... #####
0 .###. #...# #..## #.#.# ##..# #...# .###.
1 ..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.
2 .###. #...# ....# ...#. ..#.. .#... #####
3 ####. ....# ....# .###. ....# ....# ####.
4 ...#. ..##. .#.#. #..#. ##### ...#. ...#.
5 ##### #.... ####. ....# ....# #...# .###.
6 .###. #.... #.... ####. #...# #...# .###.
7 ##### ....# ...#. ..#.. .#... .#... .#...
8 .###. #...# #...# .###. #...# #...# .###.
9 .###. #...# #...# .#### ....# ....# .###.
x ..... ..... #...# .#.#. ..#.. .#.#. #...#
% ##..# ##..# ...#. ..#.. .#... #..## #..##
! ..#.. ..#.. ..#.. ..#.. ..#.. ..... ..#..
> #.... ##... ###.. ####. ###.. ##... #....
< ....# ...## ..### .#### ..### ...## ....#
. ..... ..... ..... ..... ..... ..... ..#..
- ..... ..... ..... .###. ..... ..... .....
"""
SMALL = {" ": ["..."] * 7}
for line in SMALL_SRC.strip().splitlines():
    ch, *rows = line.split()
    SMALL[ch] = rows

# ---------------------------------------------------------------- ícones
HEART = [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."]
HEART_HL = [".##.##.", "#o#####", "#######", ".#####.", "..###..", "...#..."]
COIN = ["..####..", ".######.", "###oo###", "###oo###", "###oo###", "###oo###", ".######.", "..####.."]
STAR = ["....#....", "....#....", "...###...", "#########", ".#######.", "..#####..", "..##.##..", ".##...##.", ".#.....#."]
CONTROLLER = [
    "..#########..",
    ".###########.",
    "##.######.###",
    "#...####.#.##",
    "##.######.###",
    "#############",
    "####.....####",
    ".##.......##.",
]
SPARK = ["..#..", "..#..", "##.##", "..#..", "..#.."]
ARROW_UP = ["...#...", "..###..", ".#####.", "#######", "..###..", "..###..", "..###.."]
PLUS = [".#.", "###", ".#."]

LION = open(os.path.join(HERE, "leao_64.txt")).read().split()


def tri(n):
    """Triângulo em escada (montanha) com base 2n-1."""
    return ["." * (n - 1 - i) + "#" * (2 * i + 1) + "." * (n - 1 - i) for i in range(n)]


# ---------------------------------------------------------------- desenho
class Art:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=(W, H))
        self.c.setTitle("Next Level - painel luminoso")
        self.c.setAuthor("Inteensos")
        # origem no topo-esquerdo, y para baixo
        self.c.translate(0, H)
        self.c.scale(1, -1)
        self.cur = ("", "Camada")
        self.ops = []  # (grupo, camada, cor, retângulos) para exportar o PSD

    def layer(self, group, name):
        self.cur = (group, name)

    def rects(self, rects, color):
        if not rects:
            return
        self.ops.append((*self.cur, color, list(rects)))
        p = self.c.beginPath()
        for x, y, w, h in rects:
            p.rect(x, y, w, h)
        self.c.setFillColor(color)
        self.c.drawPath(p, stroke=0, fill=1)

    def bitmap(self, rows, x, y, cell, colors):
        """rows: lista de strings; colors: {char: cor}. Junta pixels da mesma cor em retângulos."""
        keys = {ch: "%d" % i for i, ch in enumerate(dict.fromkeys(colors.values()))}
        key_of = {ch: keys[col] for ch, col in colors.items()}
        color_of = {k: col for col, k in keys.items()}
        rows = ["".join(key_of.get(ch, ".") for ch in row) for row in rows]
        colors = color_of
        by_color = {}
        prev = {}
        for r, row in enumerate(rows):
            runs = {}
            k = 0
            while k < len(row):
                ch = row[k]
                j = k
                while j < len(row) and row[j] == ch:
                    j += 1
                if ch in colors:
                    runs[(k, j, ch)] = r
                k = j
            new_prev = {}
            for key in runs:
                start = prev.get(key, r)
                new_prev[key] = start
            for key, start in prev.items():
                if key not in runs:
                    by_color.setdefault(key[2], []).append((key[0], key[1], start, r))
            prev = new_prev
        for key, start in prev.items():
            by_color.setdefault(key[2], []).append((key[0], key[1], start, len(rows)))
        for ch, spans in by_color.items():
            self.rects([(x + a * cell, y + s * cell, (b - a) * cell, (e - s) * cell) for a, b, s, e in spans],
                       colors[ch])

    def text(self, s, x, y, cell, color, font=SMALL, gap=1, align="left"):
        w = text_width(s, font, gap)
        if align == "center":
            x -= w * cell / 2
        elif align == "right":
            x -= w * cell
        cx = x
        for ch in s:
            g = font[ch]
            self.bitmap(g, cx, y, cell, {"#": color})
            cx += (len(g[0]) + gap) * cell
        return w * cell

    def box(self, x, y, w, h, color):
        self.rects([(x, y, w, h)], color)

    def frame(self, x, y, w, h, t, color):
        self.rects([(x, y, w, t), (x, y + h - t, w, t), (x, y, t, h), (x + w - t, y, t, h)], color)

    def save(self):
        self.c.showPage()
        self.c.save()

    def save_psd(self, path, scale=1):
        """PSD em camadas: um grupo por bloco, uma camada por elemento e cor."""
        from PIL import Image, ImageDraw
        from psd_tools import PSDImage
        from psd_tools.api.layers import Group, PixelLayer

        # junta as operações em camadas mantendo a ordem de empilhamento
        layers = {}
        for group, name, color, rects in self.ops:
            layers.setdefault((group, name), {}).setdefault(color, []).extend(rects)
        psd = PSDImage.new("RGB", (W * scale, H * scale))
        groups = {}
        for (group, name), by_color in layers.items():
            parent = psd
            if group:
                if group not in groups:
                    groups[group] = Group.new(psd, group, open_folder=False)
                parent = groups[group]
            multi = len(by_color) > 1
            for color, rects in by_color.items():
                px = [tuple(round(v * scale) for v in (x, y, x + w, y + h)) for x, y, w, h in rects]
                x0 = max(0, min(r[0] for r in px))
                y0 = max(0, min(r[1] for r in px))
                x1 = min(W * scale, max(r[2] for r in px))
                y1 = min(H * scale, max(r[3] for r in px))
                im = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
                d = ImageDraw.Draw(im)
                for a, b, c2, d2 in px:
                    if c2 > a and d2 > b:
                        d.rectangle((a - x0, b - y0, c2 - x0 - 1, d2 - y0 - 1), fill=color)
                label = f"{name} - {NOMES_COR.get(color, 'cor ' + color)}" if multi else name
                parent.append(PixelLayer.frompil(im, psd, label, y0, x0))
        psd.save(path)


NOMES_COR = {v.upper(): k for k, v in {
    "verde": "#00E87A", "rosa": "#FF0066", "ouro": "#FFD700", "preto": "#07091A",
    "azul": "#7B8FD4", "branco": "#FFFFFF", "v.esc": "#009650", "r.esc": "#640028",
}.items()}


def text_width(s, font=SMALL, gap=1):
    return sum(len(font[ch][0]) + gap for ch in s) - gap


def dilate(rows, r):
    """Silhueta da arte expandida em r pixels (contorno), com margem r em volta."""
    h, w = len(rows), len(rows[0])
    on = {(y, x) for y in range(h) for x in range(w) if rows[y][x] != "."}
    out = []
    for y in range(-r, h + r):
        out.append("".join("#" if any((y + dy, x + dx) in on for dy in range(-r, r + 1) for dx in range(-r, r + 1))
                           else "." for x in range(-r, w + r)))
    return out


def mix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


# ---------------------------------------------------------------- painel
def painel(path, tema, psd_path=None):
    base, ink = tema["base"], PALETA["preto"]
    a = Art(path)
    c = a

    # fundo
    c.layer("Fundo", "Cor de fundo")
    c.box(0, 0, W, H, base)

    # scanlines CRT sutis
    c.layer("Fundo", "Scanlines")
    c.rects([(0, y, W, 6) for y in range(0, H, 24)], mix(base, ink, 0.045))

    # padrão de fundo tom sobre tom (como os ícones do painel DETOX)
    tone = mix(base, ink, tema["tom"])
    c.layer("Fundo", "Ícones tom sobre tom")
    rnd = random.Random(tema["seed"])
    icons = [HEART, COIN, STAR, CONTROLLER, ARROW_UP, tri(6)]
    spots = [
        (180, 420, 40), (2180, 520, 34), (1250, 260, 22), (2550, 1050, 28),
        (40, 1250, 30), (2420, 2150, 42), (150, 2350, 26), (1150, 3000, 20),
        (2300, 3250, 30), (60, 3350, 36), (1700, 3700, 24), (900, 650, 18),
        (1700, 2400, 16), (520, 3720, 18), (2650, 2800, 20),
    ]
    for i, (x, y, cell) in enumerate(spots):
        ic = icons[i % len(icons)]
        c.bitmap(ic, x, y, cell, {"#": tone, "o": tone})
    c.layer("Fundo", "Brilhos tom sobre tom")
    for _ in range(46):
        c.bitmap(rnd.choice([SPARK, PLUS]), rnd.randrange(60, W - 120), rnd.randrange(400, H - 200),
                 rnd.choice([10, 14, 18]), {"#": tone})

    # cantos do HUD
    c.layer("HUD", "Cantos")
    m, L, t = 110, 260, 22
    for (x, y, sx, sy) in [(m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)]:
        c.box(min(x, x + sx * L), min(y, y + sy * t), L, t, ink)
        c.box(min(x, x + sx * t), min(y, y + sy * L), t, L, ink)

    # HUD superior
    hc = 16
    c.layer("HUD", "1P")
    c.text("1P", 220, 230, hc, tema["hud1"])
    for i in range(4):
        c.layer("HUD", "Corações cheios" if i < 3 else "Coração vazio")
        col = tema["coracao"] if i < 3 else mix(base, ink, 0.55)
        c.bitmap(HEART_HL, 220 + i * 9 * hc, 230 + 10 * hc, hc, {"#": col, "o": tema["brilho"] if i < 3 else col})
    rx = W - 220
    c.layer("HUD", "Texto x 25")
    c.text("x 25", rx, 230, hc, ink, align="right")
    c.layer("HUD", "Moeda")
    c.bitmap(COIN, rx - text_width("x 25") * hc - 11 * hc, 230 - hc // 2, hc, {"#": tema["moeda"], "o": ink})
    c.layer("HUD", "Texto x 03")
    c.text("x 03", rx, 230 + 10 * hc, hc, ink, align="right")
    c.layer("HUD", "Estrela")
    c.bitmap(STAR, rx - text_width("x 03") * hc - 12 * hc, 230 + 9 * hc, hc, {"#": tema["moeda"]})

    # bloco do título
    c.layer("Título", "ACAMPAMENTO")
    c.text("ACAMPAMENTO", W / 2, 690, 30, ink, align="center")

    tc = 70
    TY = 1010
    sh = tema["sombra"]
    off = 28
    nx = W / 2 - text_width("NEXT", BOLD) * tc / 2
    c.layer("Título", "NEXT sombra")
    c.text("NEXT", nx + off, TY + off, tc, sh, font=BOLD)
    c.layer("Título", "NEXT")
    c.text("NEXT", nx, TY, tc, tema["titulo"], font=BOLD)
    lx = W / 2 - text_width("LEVEL", BOLD) * tc / 2
    c.layer("Título", "LEVEL sombra")
    c.text("LEVEL", lx + off, TY + 8 * tc + off, tc, sh, font=BOLD)
    c.layer("Título", "LEVEL")
    c.text("LEVEL", lx, TY + 8 * tc, tc, tema["titulo"], font=BOLD)

    # linha "★ 2026 ★"
    yc = 2140
    c.layer("Título", "2026")
    c.text("2026", W / 2, yc, 30, ink, align="center")
    c.layer("Título", "Estrelas 2026")
    sw = text_width("2026") * 30 / 2
    c.bitmap(STAR, W / 2 - sw - 80 - 9 * 26, yc - 10, 26, {"#": tema["destaque"]})
    c.bitmap(STAR, W / 2 + sw + 80, yc - 10, 26, {"#": tema["destaque"]})

    # leão + montanhas
    lc = 16
    lw, lh = len(LION[0]) * lc, len(LION) * lc
    lx, ly = W / 2 - lw / 2, 2470
    mt = mix(base, ink, tema["tom"] * 2.2)
    c.layer("Leão", "Montanhas")
    for n, cx, cell in [(14, W / 2 - 900, 34), (19, W / 2 + 420, 34), (10, W / 2 - 1300, 30), (9, W / 2 + 1150, 30)]:
        tw = (2 * n - 1) * cell
        c.bitmap(tri(n), cx - tw / 2, ly + lh - n * cell, cell, {"#": mt})
    claro = mix(base, ink, tema["leao_claro"])
    c.layer("Leão", "Leão contorno")
    c.bitmap(dilate(LION, 1), lx - lc, ly - lc, lc, {"#": base})
    c.layer("Leão", "Leão sombra")
    c.bitmap(LION, lx, ly, lc, {"d": ink, "m": ink})
    c.layer("Leão", "Leão luz")
    c.bitmap(LION, lx, ly, lc, {"l": claro, "h": claro})

    # barra de nível
    by = ly + lh + 120
    bw, bh = 1300, 96
    bx = W / 2 - bw / 2
    c.layer("Barra de nível", "LVL 26")
    c.text("LVL 26", bx - 40, by + bh / 2 - 3.5 * 18, 18, ink, align="right")
    c.layer("Barra de nível", "Moldura")
    c.frame(bx, by, bw, bh, 12, ink)
    c.layer("Barra de nível", "Preenchimento")
    seg = 14
    segs = 15
    sw_ = (bw - 24 - seg * (segs + 1)) / segs
    filled = 11
    c.rects([(bx + 12 + seg + i * (sw_ + seg), by + 12 + seg, sw_, bh - 24 - 2 * seg) for i in range(filled)],
            tema["barra"])
    c.layer("Barra de nível", "73%")
    c.text("73%", bx + bw + 40, by + bh / 2 - 3.5 * 18, 18, ink)

    # rodapé
    fy = H - 290
    c.layer("Rodapé", "INTEENSOS")
    c.text("INTEENSOS", 240, fy, 16, ink)
    # selo "PRESS START" (como o selo DANGER)
    label = "PRESS START"
    fc = 14
    tw = text_width(label) * fc
    pad = 34
    bx2 = W - 240 - tw - 2 * pad
    c.layer("Rodapé", "Selo fundo")
    c.box(bx2, fy - pad, tw + 2 * pad, 7 * fc + 2 * pad, tema["selo_fundo"])
    c.layer("Rodapé", "Selo borda")
    c.frame(bx2, fy - pad, tw + 2 * pad, 7 * fc + 2 * pad, 8, ink)
    c.layer("Rodapé", "PRESS START")
    c.text(label, bx2 + pad, fy, fc, tema["selo_texto"])

    a.save()
    if psd_path:
        a.save_psd(psd_path)


TEMAS = {
    "ouro": dict(base=PALETA["ouro"], tom=0.10, seed=7, titulo=PALETA["preto"], sombra=PALETA["rosa"],
                 hud1=PALETA["preto"], coracao=PALETA["rosa"], brilho=PALETA["branco"],
                 moeda=PALETA["rosa"], destaque=PALETA["rosa"], leao_claro=0.38,
                 barra=PALETA["rosa"], selo_fundo=PALETA["preto"], selo_texto=PALETA["ouro"]),
    "rosa": dict(base=PALETA["rosa"], tom=0.12, seed=11, titulo=PALETA["branco"], sombra=PALETA["preto"],
                 hud1=PALETA["branco"], coracao=PALETA["ouro"], brilho=PALETA["branco"],
                 moeda=PALETA["ouro"], destaque=PALETA["ouro"], leao_claro=0.45,
                 barra=PALETA["ouro"], selo_fundo=PALETA["preto"], selo_texto=PALETA["rosa"]),
}

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else HERE
    os.makedirs(out, exist_ok=True)
    for nome, tema in TEMAS.items():
        painel(os.path.join(out, f"Next_Level_Painel_{nome.capitalize()}_3000x4124.pdf"), tema,
               os.path.join(out, f"Next_Level_Painel_{nome.capitalize()}_3000x4124.psd"))
        print("ok", nome)
