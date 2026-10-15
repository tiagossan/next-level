"""Mockup simples (escala real em mm) da camiseta preta com as duas estampas."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
K = 2  # px por mm no mockup


def camiseta(costas=False):
    w, h = 860, 780
    im = Image.new("RGBA", (w * K, h * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # tamanho M aprox.: 52 cm de largura no peito, 74 cm de comprimento
    pts = [(330, 30), (530, 30), (780, 150), (725, 290), (690, 270), (690, 770),
           (170, 770), (170, 270), (135, 290), (80, 150)]
    d.polygon([(x * K, y * K) for x, y in pts], fill=(16, 16, 18, 255))
    if costas:
        d.line([(345 * K, 42 * K), (515 * K, 42 * K)], fill=(30, 30, 34, 255), width=6 * K)
    else:
        d.chord([(345 * K, -20 * K), (515 * K, 100 * K)], 0, 180, fill=(225, 225, 225, 255))
        d.arc([(345 * K, -20 * K), (515 * K, 100 * K)], 0, 180, fill=(38, 38, 42, 255), width=8 * K)
    return im


def colar(shirt, png, largura_mm, topo_mm):
    art = Image.open(png)
    alt = art.height * largura_mm / art.width
    art = art.resize((round(largura_mm * K), round(alt * K)), Image.NEAREST)
    shirt.alpha_composite(art, (round((430 - largura_mm / 2) * K), round(topo_mm * K)))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else HERE
    f = camiseta()
    colar(f, os.path.join(out, "Camiseta_Frente_Leao_inTEENsos_300dpi.png"), 120 * 0.85, 140)
    b = camiseta(costas=True)
    colar(b, os.path.join(out, "Camiseta_Costas_Tela_de_Game_300dpi.png"), 300, 110)
    m = Image.new("RGB", (f.width * 2 + 60, f.height + 120), (226, 226, 230))
    m.paste(f, (20, 80), f)
    m.paste(b, (f.width + 40, 80), b)
    d = ImageDraw.Draw(m)
    try:
        fnt = ImageFont.truetype(os.path.join(HERE, "fontes", "PressStart2P-Regular.ttf"), 28)
    except OSError:
        fnt = None
    d.text((20 + f.width // 2, 40), "FRENTE", fill=(7, 9, 26), font=fnt, anchor="mm")
    d.text((f.width + 40 + b.width // 2, 40), "COSTAS", fill=(7, 9, 26), font=fnt, anchor="mm")
    m.save(os.path.join(out, "Mockup_Camiseta_Next_Level.png"))
