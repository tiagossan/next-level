"""Exporta o leão pixelado (grade 46x64) em SVG e PDF vetoriais e PNG de alta resolução.

Uso: python3 gerar_leao.py [pasta_saida]
"""
import os
import sys

from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
LION = open(os.path.join(HERE, "..", "paineis", "leao_64.txt")).read().split()
GW, GH = len(LION[0]), len(LION)

PNG_CELL = 64   # 46x64 pixels -> 2944x4096 px
VEC_CELL = 10   # tamanho do pixel no SVG/PDF (vetorial: escala sem perda)

PRETO = "#07091A"
VERSOES = {
    # tons originais do arquivo do banner
    "azul_original": {"d": "#215FD6", "m": "#3D8EFC", "l": "#5CB2FB", "h": "#7CD0FF"},
    # quase um tom só, como no painel
    "preto_dois_tons": {"d": PRETO, "m": PRETO, "l": "#33354A", "h": "#33354A"},
    "preto_solido": {"d": PRETO, "m": PRETO, "l": PRETO, "h": PRETO},
    "branco_solido": {"d": "#FFFFFF", "m": "#FFFFFF", "l": "#FFFFFF", "h": "#FFFFFF"},
}


def spans(colors):
    """Retângulos (x, y, w, h) em unidades de grade, agrupados por cor e mesclados."""
    out = {}
    grid = [[colors.get(ch) for ch in row] for row in LION]
    open_runs = {}
    for y in range(GH + 1):
        runs = {}
        if y < GH:
            row = grid[y]
            x = 0
            while x < GW:
                col = row[x]
                j = x
                while j < GW and row[j] == col:
                    j += 1
                if col:
                    runs[(x, j, col)] = open_runs.get((x, j, col), y)
                x = j
        for key, start in open_runs.items():
            if key not in runs:
                x0, x1, col = key
                out.setdefault(col, []).append((x0, start, x1 - x0, y - start))
        open_runs = runs
    return out


def svg(path, colors):
    w, h = GW * VEC_CELL, GH * VEC_CELL
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {GW} {GH}" '
             'shape-rendering="crispEdges">']
    for col, rects in spans(colors).items():
        d = "".join(f"M{x} {y}h{rw}v{rh}h{-rw}z" for x, y, rw, rh in rects)
        parts.append(f'<path fill="{col}" d="{d}"/>')
    parts.append("</svg>")
    open(path, "w").write("\n".join(parts))


def pdf(path, colors):
    c = canvas.Canvas(path, pagesize=(GW * VEC_CELL, GH * VEC_CELL))
    c.setTitle("Leão pixel - Next Level")
    for col, rects in spans(colors).items():
        p = c.beginPath()
        for x, y, rw, rh in rects:
            p.rect(x * VEC_CELL, (GH - y - rh) * VEC_CELL, rw * VEC_CELL, rh * VEC_CELL)
        c.setFillColor(col)
        c.drawPath(p, stroke=0, fill=1)
    c.showPage()
    c.save()


def png(path, colors):
    im = Image.new("RGBA", (GW * PNG_CELL, GH * PNG_CELL), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for col, rects in spans(colors).items():
        for x, y, rw, rh in rects:
            d.rectangle((x * PNG_CELL, y * PNG_CELL, (x + rw) * PNG_CELL - 1, (y + rh) * PNG_CELL - 1), fill=col)
    im.save(path, dpi=(300, 300))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else HERE
    os.makedirs(out, exist_ok=True)
    for nome, colors in VERSOES.items():
        base = os.path.join(out, f"leao_pixel_{nome}")
        svg(base + ".svg", colors)
        pdf(base + ".pdf", colors)
        png(base + f"_{GW * PNG_CELL}x{GH * PNG_CELL}.png", colors)
        print("ok", nome)
