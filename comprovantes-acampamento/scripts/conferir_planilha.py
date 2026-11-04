import re, sys, zipfile, shutil, html
src, dst = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(src); files = {n: z.read(n) for n in z.namelist()}; infos = z.infolist()
sheet = files['xl/worksheets/sheet1.xml'].decode()
styles = files['xl/styles.xml'].decode()
ss = files['xl/sharedStrings.xml'].decode()

# ---- shared strings: append new
sis = re.findall(r'<si>.*?</si>', ss, re.S)
def add_str(t):
    global ss
    idx = len(sis); sis.append(t)
    ss = ss.replace('</sst>', '<si><t>%s</t></si></sst>' % html.escape(t, quote=False))
    return idx

# ---- yellow styles: clone xf with fillId=8 (FFFFFF00 already exists)
cx = re.search(r'<cellXfs count="(\d+)">(.*?)</cellXfs>', styles, re.S)
xfs = re.findall(r'<xf\b[^>]*?(?:/>|>.*?</xf>)', cx.group(2), re.S)
newxfs = []; cache = {}
def yellow(s):
    s = int(s)
    if s in cache: return cache[s]
    x = xfs[s]
    x = re.sub(r'fillId="\d+"', 'fillId="8"', x)
    x = re.sub(r'applyFill="\d"', '', x).replace('<xf ', '<xf applyFill="1" ', 1)
    newxfs.append(x); cache[s] = len(xfs) + len(newxfs) - 1
    return cache[s]

def cell(ref):
    m = re.search(r'<c r="%s"(?: [^>]*?)?(?:/>|>.*?</c>)' % ref, sheet, re.S)
    assert m, ref; return m
def set_cell(ref, new):
    global sheet
    m = cell(ref); sheet = sheet[:m.start()] + new + sheet[m.end():]
def style_of(ref):
    m = re.search(r' s="(\d+)"', cell(ref).group(0)); return m.group(1) if m else '0'

# 1) entradas em espécie: descrição sem nomes
novos = {
 10: 'ENTRADA INSCRIÇÃO', 16: 'ENTRADA INSCRIÇÃO', 17: 'ENTRADA INSCRIÇÃO', 18: 'ENTRADA INSCRIÇÃO',
 22: 'ENTRADA INSCRIÇÃO', 32: 'ENTRADA INSCRIÇÃO', 34: 'ENTRADA INSCRIÇÃO', 35: 'ENTRADA INSCRIÇÃO',
 36: 'ENTRADA INSCRIÇÃO', 37: 'ENTRADA INSCRIÇÃO', 38: 'ENTRADA INSCRIÇÃO', 44: 'ENTRADA INSCRIÇÃO',
 45: 'ENTRADA INSCRIÇÃO', 48: 'ENTRADA INSCRIÇÃO (USADO NOS SALGADOS)', 60: 'ENTRADA INSCRIÇÃO',
}
for r, t in novos.items():
    ref = 'C%d' % r; s = style_of(ref)
    set_cell(ref, '<c r="%s" s="%s" t="s"><v>%d</v></c>' % (ref, s, add_str(t)))

# 2) conferidas em amarelo (B:E)
for r in (52, 53):
    for col in 'BCDE':
        ref = '%s%d' % (col, r); m = cell(ref); c = m.group(0)
        s = style_of(ref); y = yellow(s)
        c2 = re.sub(r' s="\d+"', ' s="%d"' % y, c) if ' s="' in c else c.replace('<c r="%s"' % ref, '<c r="%s" s="%d"' % (ref, y), 1)
        set_cell(ref, c2)

# 3) pendências
pend = [
 (140, 46325, 'SALGADOS BRUNO - SÓ HÁ CUPOM DE R$ 200 (PANI PREMIUM); FALTAM R$ 200', 200),
 (141, 46328, 'CUPOM NK BEBIDAS (BRUNO) SEM LANÇAMENTO NA PLANILHA', 107),
]
for r, d, t, v in pend:
    set_cell('B%d' % r, '<c r="B%d" s="54"><v>%d</v></c>' % (r, d))
    set_cell('C%d' % r, '<c r="C%d" s="%s" t="s"><v>%d</v></c>' % (r, style_of('C%d' % r), add_str(t)))
    set_cell('D%d' % r, '<c r="D%d" s="%s"><v>%s</v></c>' % (r, style_of('D%d' % r), v))

# write back styles / ss counts
allx = xfs + newxfs
styles = styles[:cx.start()] + '<cellXfs count="%d">%s</cellXfs>' % (len(allx), ''.join(allx)) + styles[cx.end():]
n = len(sis)
ss = re.sub(r'uniqueCount="\d+"', 'uniqueCount="%d"' % n, ss)
cnt = int(re.search(r' count="(\d+)"', ss).group(1)) + len(novos) + len(pend)
ss = re.sub(r' count="\d+"', ' count="%d"' % cnt, ss, 1)
files['xl/worksheets/sheet1.xml'] = sheet.encode(); files['xl/styles.xml'] = styles.encode(); files['xl/sharedStrings.xml'] = ss.encode()
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as out:
    for i in infos: out.writestr(i, files[i.filename])
