from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
O='otimizadas/'
R=[ # (pessoa, arquivo, data, estabelecimento, descricao, valor)
('Bruno','bruno/WhatsApp Image 2026-11-04 at 14.51.40.jpeg','30/10/2026','Pani Premium (Ceilândia)','200 mini coxinhas, 100 mini risoles, 100 mini churros','200,00'),
('Bruno','bruno/WhatsApp Image 2026-11-04 at 14.51.20.jpeg','02/11/2026','NK Comércio de Alimentos (Brazlândia)','Refrigerantes, água mineral, sacolas','107,00'),
('Dogão','dogão/WhatsApp Image 2026-11-03 at 13.54.49 (1).jpeg','30/10/2026','(nome da loja cortado na foto)','24 itens: energéticos Baly 2L e outros','323,47'),
('Dogão','dogão/WhatsApp Image 2026-11-03 at 13.54.49 (2).jpeg','30/10/2026','N Y Panificadora e Confeitaria – Gringo (Taguatinga)','Confeitaria (1 item)','200,00'),
('Dogão','dogão/WhatsApp Image 2026-11-03 at 14.07.43.jpeg','31/10/2026','Pátria Alimentos','Pão francês, abóbora, linguiça, bacon, papel-toalha','198,06'),
('Dogão','dogão/WhatsApp Image 2026-11-03 at 13.54.50 (3).jpeg','31/10/2026','Verdinha Comercial de Alimentos (Brazlândia)','Rúcula, hortelã, copos, farinha, filme PVC, saco de lixo, cebola','132,43'),
('Dogão','dogão/WhatsApp Image 2026-11-03 at 13.54.49.jpeg','01/11/2026','JP de Carvalho Derivados de Petróleo (Taguatinga)','Gasolina comum 7,634 L','50,00'),
('Dogão','dogão/WhatsApp Image 2026-11-03 at 13.54.50 (2).jpeg','01/11/2026','Pátria Alimentos','Detergentes, pão francês 7,06 kg, sacola','134,01'),
('Dogão','dogão/WhatsApp Image 2026-11-03 at 13.54.50.jpeg','01/11/2026','NK Comércio de Alimentos (Brazlândia)','Copos descartáveis, água, refrigerantes','175,30'),
('Dogão','dogão/WhatsApp Image 2026-11-03 at 13.54.50 (1).jpeg','sem data','Auto Posto Samdu (Taguatinga)','Gasolina comum 7,950 L','50,00'),
]
W,H=A4; c=canvas.Canvas('comprovantes-acampamento.pdf',pagesize=A4); c.setTitle('Comprovantes – Acampamento')
def v(s): return float(s.replace('.','').replace(',','.'))
def brl(x): return f'{x:,.2f}'.replace(',','X').replace('.',',').replace('X','.')
# resumo
c.setFont('Helvetica-Bold',16); c.drawString(40,H-50,'Comprovantes de gastos – Acampamento')
y=H-85
for p in ('Bruno','Dogão'):
    c.setFont('Helvetica-Bold',12); c.drawString(40,y,p); y-=16; tot=0
    for i,r in enumerate(R,1):
        if r[0]!=p: continue
        c.setFont('Helvetica',8.5); c.drawString(48,y,f'#{i:02d}  {r[2]}'); c.drawString(140,y,r[3][:48]); c.drawRightString(W-40,y,'R$ '+r[5]); y-=12; tot+=v(r[5])
    c.setFont('Helvetica-Bold',9); c.drawRightString(W-40,y,'Subtotal '+p+': R$ '+brl(tot)); y-=24
c.setFont('Helvetica-Bold',11); c.drawRightString(W-40,y,'TOTAL: R$ '+brl(sum(v(r[5]) for r in R)))
c.showPage()
# 2 comprovantes por página
m=24; cw=(W-3*m)/2; top=H-m-34
for k in range(0,len(R),2):
    for j,r in enumerate(R[k:k+2]):
        i=k+j+1; x=m+j*(cw+m)
        c.setFont('Helvetica-Bold',9); c.drawString(x,H-m-8,f'#{i:02d} {r[0]} – {r[2]} – R$ {r[5]}')
        c.setFont('Helvetica',7.5); c.drawString(x,H-m-20,r[3][:60])
        img=ImageReader(O+r[1]); iw,ih=img.getSize(); s=min(cw/iw,(top-m)/ih)
        c.drawImage(img,x,top-ih*s,iw*s,ih*s); c.rect(x,top-ih*s,iw*s,ih*s)
    c.showPage()
c.save()
