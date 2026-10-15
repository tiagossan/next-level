"""Costas da camiseta NEXT LEVEL 2026: tela de game em pixel art, em camadas.

Toda a arte vive numa grade única (CELL_MM = 0,508 mm = 6 px a 300 dpi). Cada elemento
é uma camada (máscara booleana + cor). A partir das mesmas camadas saem:
  - PSD em camadas, 300 dpi (3540 x 4722 px), para editar no Photoshop;
  - PDF e SVG vetoriais em tamanho real (300 x 400 mm);
  - PNG 300 dpi com fundo transparente.

Uso: python3 gerar_costas.py [pasta_saida]
"""
import os
import random
import sys

import numpy as np
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "paineis"))
from gerar_camiseta import FONTES, ICONS, text_bitmap  # noqa: E402
from gerar_paineis import BOLD  # noqa: E402  (fonte grossa do banner original)

VERDE, V_ESC = "#00E87A", "#009650"
ROSA, R_ESC = "#FF0066", "#99003D"
OURO, AZUL, BRANCO = "#FFD700", "#7B8FD4", "#FFFFFF"

PX = 6                       # px por célula a 300 dpi
CELL_MM = 25.4 / 300 * PX    # 0,508 mm
GW, GH = 590, 787            # 299,7 x 399,8 mm
MM_PT = 72 / 25.4


# ---------------------------------------------------------------- utilidades de máscara
def blank():
    return np.zeros((GH, GW), bool)


def stamp(small, x, y, unit=1, into=None):
    """Cola uma máscara pequena (ampliada 'unit' vezes) na posição (x, y) da grade."""
    m = into if into is not None else blank()
    s = np.kron(np.asarray(small, bool), np.ones((unit, unit), bool))
    h, w = s.shape
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(GW, x + w), min(GH, y + h)
    if x1 > x0 and y1 > y0:
        m[y0:y1, x0:x1] |= s[y0 - y:y1 - y, x0 - x:x1 - x]
    return m


def rows_mask(rows, ch="#"):
    return np.array([[c in ch for c in r] for r in rows], bool)


def dilate(m, r):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def shift(m, dy, dx):
    out = np.zeros_like(m)
    h, w = m.shape
    out[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)] = \
        m[max(0, -dy):h - max(0, dy), max(0, -dx):w - max(0, dx)]
    return out


def bold_bitmap(word):
    rows = []
    for r in range(7):
        rows.append(".".join(BOLD[ch][r] for ch in word))
    return rows_mask(rows)


SPARKLE = ["...#...", "...#...", "..###..", "#######", "..###..", "...#...", "...#..."]
PLUS = [".#.", "###", ".#."]


# ---------------------------------------------------------------- cena em camadas
class Arte:
    def __init__(self):
        self.layers = []  # [grupo, nome, cor, máscara]

    def add(self, group, name, color, mask):
        self.layers.append([group, name, color, mask])

    def knockout(self, hole, groups):
        """Vaza 'hole' das camadas dos grupos indicados (contorno que mostra a camiseta)."""
        for lay in self.layers:
            if lay[0] in groups:
                lay[3] = lay[3] & ~hole

    def composite(self, bg=(0, 0, 0, 0)):
        img = np.zeros((GH, GW, 4), np.uint8)
        img[:] = bg
        for _, _, col, m in self.layers:
            img[m] = [int(col[i:i + 2], 16) for i in (1, 3, 5)] + [255]
        return img

    # ---- vetorial
    @staticmethod
    def rects(m):
        """Retângulos (x, y, w, h) em células, mesclando corridas iguais entre linhas."""
        out, open_runs = [], {}
        for y in range(GH + 1):
            runs = {}
            if y < GH:
                row = m[y]
                d = np.diff(np.concatenate([[0], row.astype(np.int8), [0]]))
                for a, b in zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)):
                    runs[(a, b)] = open_runs.get((a, b), y)
            for (a, b), s in open_runs.items():
                if (a, b) not in runs:
                    out.append((a, s, b - a, y - s))
            open_runs = runs
        return out

    def pdf(self, path):
        if "PressStart2P" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("PressStart2P", os.path.join(FONTES, "PressStart2P-Regular.ttf")))
        k = CELL_MM * MM_PT
        c = canvas.Canvas(path, pagesize=(GW * k, GH * k), initialFontName="PressStart2P")
        c.setTitle("Camiseta Next Level - Costas")
        c.setAuthor("INTEENSOS · Next Level 2026")
        for _, _, col, m in self.layers:
            rs = self.rects(m)
            if not rs:
                continue
            p = c.beginPath()
            for x, y, w, h in rs:
                p.rect(x * k, (GH - y - h) * k, w * k, h * k)
            c.setFillColor(col)
            c.drawPath(p, stroke=0, fill=1)
        c.showPage()
        c.save()

    def svg(self, path):
        f = lambda v: f"{v:.3f}".rstrip("0").rstrip(".")
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{f(GW * CELL_MM)}mm" '
               f'height="{f(GH * CELL_MM)}mm" viewBox="0 0 {GW} {GH}" shape-rendering="crispEdges">']
        for group, name, col, m in self.layers:
            rs = self.rects(m)
            if rs:
                d = "".join(f"M{x} {y}h{w}v{h}h{-w}z" for x, y, w, h in rs)
                out.append(f'<path id="{group} - {name}" fill="{col}" d="{d}"/>')
        out.append("</svg>")
        open(path, "w").write("\n".join(out))

    def png(self, path):
        img = Image.fromarray(self.composite()).resize((GW * PX, GH * PX), Image.NEAREST)
        img.save(path, dpi=(300, 300))

    def psd(self, path):
        from psd_tools import PSDImage
        from psd_tools.api.layers import Group, PixelLayer
        psd = PSDImage.new("RGB", (GW * PX, GH * PX), color=(7, 9, 26))
        # camada de fundo com a cor da camiseta (só para visualizar; ocultar ao exportar)
        bgl = PixelLayer.frompil(Image.new("RGBA", (GW * PX, GH * PX), (12, 12, 14, 255)), psd,
                                 "Camiseta preta (só referência - ocultar)", 0, 0)
        bgl.visible = False
        psd.append(bgl)
        groups = {}
        for group, name, col, m in self.layers:
            if not m.any():
                continue
            ys, xs = np.nonzero(m)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            crop = m[y0:y1, x0:x1].repeat(PX, 0).repeat(PX, 1)
            rgba = np.zeros(crop.shape + (4,), np.uint8)
            rgba[crop] = [int(col[i:i + 2], 16) for i in (1, 3, 5)] + [255]
            if group not in groups:
                groups[group] = Group.new(psd, group, open_folder=False)
            groups[group].append(PixelLayer.frompil(Image.fromarray(rgba), psd, name, int(y0 * PX), int(x0 * PX)))
        psd.save(path)


# ---------------------------------------------------------------- composição
def costas():
    a = Arte()
    cx = GW // 2

    # ---------- cenário: sol pixelado com faixas
    R, su = 32, 4                     # raio em "pixels do sol" e tamanho do pixel (células)
    scy = 300
    horizon = scy + int(0.62 * R) * su
    yy, xx = np.mgrid[0:2 * R, 0:2 * R]
    disk = (xx - R + 0.5) ** 2 + (yy - R + 0.5) ** 2 <= R * R
    t = yy / (2 * R)
    r = yy - R
    gaps = (r > 2) & ((r % 5) < (1 + r // 9))
    ouro_s = disk & ((t < 0.36) | ((t < 0.5) & ((xx + yy) % 2 == 0))) & ~gaps
    rosa_s = disk & ~ouro_s & ~gaps
    sx, sy = cx - R * su, scy - R * su
    cut = blank()
    cut[horizon:, :] = True
    a.add("Cenário", "Sol - ouro", OURO, stamp(ouro_s, sx, sy, su) & ~cut)
    a.add("Cenário", "Sol - rosa", ROSA, stamp(rosa_s, sx, sy, su) & ~cut)

    # ---------- estrelas do céu
    rnd = random.Random(26)
    stars_w, stars_a, stars_o = blank(), blank(), blank()
    sun_zone = dilate(stamp(disk, sx, sy, su), 14)
    n = 0
    while n < 70:
        x, y = rnd.randrange(40, GW - 50), rnd.randrange(100, horizon - 10)
        kind = rnd.random()
        shape, unit = (PLUS, 2) if kind < 0.35 else (SPARKLE, 2) if kind < 0.45 else (["#"], 2)
        m = stamp(rows_mask(shape), x, y, unit)
        if (m & sun_zone).any():
            continue
        target = stars_w if rnd.random() < 0.55 else stars_a if rnd.random() < 0.8 else stars_o
        target |= m
        n += 1
    a.add("Cenário", "Estrelas brancas", BRANCO, stars_w)
    a.add("Cenário", "Estrelas azuis", AZUL, stars_a)
    a.add("Cenário", "Estrelas douradas", OURO, stars_o)

    # ---------- montanhas na linha do horizonte
    mt, ridge = blank(), blank()
    mu = 3
    for peak, hgt in [(95, 30), (175, 22), (420, 34), (505, 24)]:
        rows = []
        for i in range(hgt):
            w = 2 * i + 1
            rows.append(w)
        for i, w in enumerate(rows):
            y = horizon - (hgt - i) * mu
            x0 = peak - (w // 2) * mu
            mt[y:y + mu, max(0, x0):x0 + w * mu] = True
            ridge[y:y + mu, max(0, x0):x0 + 2 * mu] = True  # aresta iluminada (lado esquerdo)
    a.add("Cenário", "Montanhas", V_ESC, mt & ~ridge)
    a.add("Cenário", "Montanhas - aresta", VERDE, ridge)

    # ---------- chão quadriculado em perspectiva
    floor_h = 128
    fl = blank()
    fl[horizon:horizon + 3, 40:GW - 40] = True
    for i in range(1, 8):
        y = horizon + int(floor_h * (i / 7) ** 1.8)
        fl[y:y + 2, 40:GW - 40] = True
    for k in range(-7, 8):
        xb = cx + k * 72
        for y in range(horizon + 8, horizon + floor_h + 2):
            f = (y - horizon) / floor_h
            x = int(round(cx + (xb - cx) * f))
            if 40 <= x < GW - 41:
                fl[y, x - 1:x + 1] = True
    a.add("Cenário", "Chão quadriculado", AZUL, fl)

    # ---------- título NEXT / LEVEL
    p = 9
    title_all = blank()
    plates = blank()  # retângulo de cada letra: o cenário não aparece dentro das letras
    for word, face_c, low_c, top in [("NEXT", VERDE, V_ESC, 292), ("LEVEL", ROSA, R_ESC, 372)]:
        bm = bold_bitmap(word)
        x = cx - bm.shape[1] * p // 2
        face = stamp(bm, x, top, p)
        col = 0
        for ch in word:
            gw = len(BOLD[ch][0])
            plates[top:top + 7 * p + 6, x + col * p:x + (col + gw + 1) * p + 6] = True
            col += gw + 1
        ext = blank()
        for k in range(1, 7):
            ext |= shift(face, k, k)
        ext &= ~face
        shine = face & ~shift(face, 2, 0)                     # 2 células no topo...
        shine[top + p:, :] = False                            # ...só na linha de cima das letras
        band_cut = blank()
        band_cut[top + 4 * p + 2: top + 4 * p + 4, :] = True  # fresta entre as duas faixas
        low = blank()
        low[top + 4 * p + 4:, :] = True
        low &= face
        body = face & ~shine & ~low & ~band_cut
        a.add(f"Título {word}", "Extrusão 3D", AZUL, ext)
        a.add(f"Título {word}", "Face", face_c, body)
        a.add(f"Título {word}", "Faixa inferior", low_c, low & ~band_cut)
        a.add(f"Título {word}", "Brilho", BRANCO, shine)
        title_all |= face | ext
    # contorno vazado em volta do título (mostra o preto da camiseta)
    a.knockout(dilate(title_all, 4) | plates, {"Cenário"})
    sp = blank()
    stamp(rows_mask(SPARKLE), cx - 152, 280, 3, sp)
    stamp(rows_mask(SPARKLE), cx + 160, 358, 3, sp)
    stamp(rows_mask(PLUS), cx + 178, 396, 3, sp)
    a.add("Título NEXT", "Brilhos", BRANCO, sp)

    # ---------- ACAMPAMENTO (pequeno) com traços
    ac = text_bitmap("ACAMPAMENTO", "PressStart2P-Regular.ttf")
    u = 2
    w = ac.shape[1] * u
    y_ac = 132
    acm = stamp(ac, cx - w // 2, y_ac, u)
    a.knockout(dilate(acm, 6), {"Cenário"})
    a.add("Textos", "ACAMPAMENTO", BRANCO, acm)
    tr = blank()
    tr[y_ac + 6:y_ac + 8, cx - w // 2 - 70:cx - w // 2 - 14] = True
    tr[y_ac + 6:y_ac + 8, cx + w // 2 + 14:cx + w // 2 + 70] = True
    a.add("Textos", "Traços ACAMPAMENTO", AZUL, tr)

    # ---------- ★ 2026 ★
    y26 = horizon + floor_h + 26
    t26 = text_bitmap("2026", "PressStart2P-Regular.ttf")
    u = 3
    w = t26.shape[1] * u
    a.add("Textos", "2026", BRANCO, stamp(t26, cx - w // 2, y26, u))
    st = rows_mask(ICONS["star"])
    a.add("Textos", "Estrelas 2026", OURO,
          stamp(st, cx - w // 2 - 24 - 9 * 2, y26 + 2, 2) | stamp(st, cx + w // 2 + 24, y26 + 2, 2))

    # ---------- HUD
    m, L, tt = 28, 66, 6
    cor = blank()
    for (x, y, sx, sy) in [(m, m, 1, 1), (GW - m, m, -1, 1), (m, GH - m, 1, -1), (GW - m, GH - m, -1, -1)]:
        xa, ya = min(x, x + sx * L), min(y, y + sy * tt)
        cor[ya:ya + tt, xa:xa + L] = True
        xb, yb = min(x, x + sx * tt), min(y, y + sy * L)
        cor[yb:yb + L, xb:xb + tt] = True
    a.add("HUD", "Cantos", VERDE, cor)
    hu, top = 3, 56
    a.add("HUD", "1P", VERDE, stamp(text_bitmap("1P", "Silkscreen-Bold.ttf"), 56, top, hu))
    hearts, hl, empty = blank(), blank(), blank()
    hm = rows_mask(ICONS["heart"], "#o")
    for i in range(4):
        x = 56 + i * 9 * hu
        if i < 3:
            stamp(rows_mask(ICONS["heart"], "#"), x, top + 9 * hu, hu, hearts)
            stamp(rows_mask(ICONS["heart"], "o"), x, top + 9 * hu, hu, hl)
        else:
            pad = np.pad(hm, 1)
            edge = hm & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
            stamp(edge, x, top + 9 * hu, hu, empty)
    a.add("HUD", "Corações", ROSA, hearts | empty)
    a.add("HUD", "Corações - brilho", BRANCO, hl)
    rx = GW - 56
    for i, (label, icon, dx_icon, dy_icon) in enumerate([("x 25", "coin", 11, -1), ("x 03", "star", 12, -1)]):
        tb = text_bitmap(label, "Silkscreen-Bold.ttf")
        y = top + i * 9 * hu
        a.add("HUD", f"Texto {label}", BRANCO, stamp(tb, rx - tb.shape[1] * hu, y, hu))
        ic = rows_mask(ICONS[icon], "#")
        a.add("HUD", "Moeda" if icon == "coin" else "Estrela", OURO,
              stamp(ic, rx - tb.shape[1] * hu - dx_icon * hu, y + dy_icon * hu, hu))

    # ---------- barra de nível
    yb = y26 + 66
    bw, bh, bt = 280, 28, 4
    bx = cx - bw // 2
    fr = blank()
    fr[yb:yb + bh, bx:bx + bw] = True
    fr[yb + bt:yb + bh - bt, bx + bt:bx + bw - bt] = False
    a.add("Barra de nível", "Moldura", BRANCO, fr)
    segs, gap = 15, 3
    sw = (bw - 2 * bt - gap * (segs + 1)) // segs
    fill = blank()
    for i in range(11):
        x = bx + bt + gap + i * (sw + gap)
        fill[yb + bt + gap:yb + bh - bt - gap, x:x + sw] = True
    a.add("Barra de nível", "Preenchimento", VERDE, fill)
    lu = 3
    lv = text_bitmap("LVL 26", "Silkscreen-Bold.ttf")
    a.add("Barra de nível", "LVL 26", BRANCO, stamp(lv, bx - 12 - lv.shape[1] * lu, yb + bh // 2 - 10, lu))
    pc = text_bitmap("73%", "Silkscreen-Bold.ttf")
    a.add("Barra de nível", "73%", BRANCO, stamp(pc, bx + bw + 12, yb + bh // 2 - 10, lu))

    # ---------- rodapé
    fy = GH - 92
    u = 2
    word = "INTEENSOS"
    wb = text_bitmap(word, "PressStart2P-Regular.ttf")
    green, white = blank(), blank()
    x0 = 70
    for i in range(len(word)):
        part = np.zeros_like(wb)
        part[:, i * 8:(i + 1) * 8] = wb[:, i * 8:(i + 1) * 8]
        stamp(part, x0, fy, u, white if 2 <= i <= 5 else green)
    a.add("Rodapé", "inTEENsos - IN SOS", VERDE, green)
    a.add("Rodapé", "inTEENsos - TEEN", BRANCO, white)
    lb = text_bitmap("LET'S START", "PressStart2P-Regular.ttf")
    pad = 6
    sw_, sh_ = lb.shape[1] * u + 2 * pad, lb.shape[0] * u + 2 * pad
    sx_ = GW - 70 - sw_
    sel = blank()
    sel[fy - pad:fy - pad + sh_, sx_:sx_ + sw_] = True
    sel &= ~stamp(lb, sx_ + pad, fy, u)
    a.add("Rodapé", "Selo LET'S START (texto vazado)", ROSA, sel)
    return a


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    out = args[0] if args else HERE
    os.makedirs(out, exist_ok=True)
    arte = costas()
    base = os.path.join(out, "Camiseta_Costas_Tela_de_Game")
    arte.pdf(base + ".pdf")
    arte.svg(base + ".svg")
    arte.png(base + "_300dpi.png")
    if "--psd" in sys.argv:
        arte.psd(base + "_300dpi.psd")
    print("ok")
