import json,os
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance
R='/home/claude/nosts-posts/'; F=R+'engine/fonts/'
W,H=1080,1350; NAVY=(2,36,108); CREAM=(246,239,224); GOLD=(255,214,120); WHITE=(255,255,255)
def f(n,s): return ImageFont.truetype(F+n,s)
BOLD,MED='Inter-ExtraBold.otf','Inter-Medium.otf'; SER='EBG.ttf'; IT='DMSerifDisplay-Italic.ttf'; EBI='EBGi.ttf'
def ctext(d,y,t,font,fill):
    d.text(((W-d.textlength(t,font=font))/2,y),t,font=font,fill=fill)
def wrapc(d,y,t,font,fill,maxw=900,lh=1.18):
    words=t.split(); line=''; lines=[]
    for w in words:
        if d.textlength((line+' '+w).strip(),font=font)<=maxw: line=(line+' '+w).strip()
        else: lines.append(line); line=w
    lines.append(line)
    for l in lines: ctext(d,y,l,font,fill); y+=int(font.size*lh)
    return y
def logo(img):
    lg=Image.open(R+'engine/logo_marca.png').convert('RGBA')
    lg=Image.merge('RGBA',[Image.new('L',lg.size,c) for c in (251,248,240)]+[lg.getchannel('A')])
    lw=170; lg=lg.resize((lw,int(lg.height*lw/lg.width))); img.alpha_composite(lg,((W-lw)//2,H-lg.height-50))
def base(): 
    im=Image.new('RGBA',(W,H),NAVY+(255,)); return im
out=R+'posts/2026-11-27/'
# 1 hook
im=base(); d=ImageDraw.Draw(im)
ctext(d,250,'BLACK FRIDAY',f(BOLD,58),GOLD)
y=wrapc(d,380,'Os livros que mudam a forma como pensa',f(SER,96),CREAM,maxw=920,lh=1.12)
y=wrapc(d,y+30,'ficaram mais baratos.',f(IT,92),WHITE)
ctext(d,y+90,'Deslize →',f(EBI,52),(200,206,224))
logo(im); im.convert('RGB').save(out+'feed_tarde_v2_1.jpg',quality=93)
books=[('Manual de Epicteto','Epicteto','1 550 MT','1 300 MT',('raw','fotos/livros/manual-de-epicteto_mao_hd.jpg',(225,330,1005,1330)),'Para não sofrer com o que não controla.'),
 ('Sobre a Brevidade da Vida','Séneca','1 550 MT','1 350 MT',('raw','fotos/livros/sobre-a-brevidade-da-vida_mao_hd.jpg',(150,320,775,1120)),'A vida não é curta. Nós é que a desperdiçamos.'),
 ('Como Parar de se Preocupar e Começar a Viver','Dale Carnegie','2 300 MT','1 850 MT',('photo','fotos/livros/como-parar-de-se-preocupar_anuncio.jpg','como-parar-de-se-preocupar'),'Para quem anda cansado de pensar em tudo.'),
 ('A República','Platão','2 500 MT','2 150 MT',('photo','fotos/livros/a-republica_anuncio.jpg','a-republica'),'O que é justo? A pergunta que nunca envelhece.'),
 ('As Coisas que Você Só Vê Quando Desacelera','Haemin Sunim · capa dura','1 850 MT','1 700 MT',('raw','fotos/livros/as-coisas-que-voce-so-ve-quando-desacelera_anuncio_hd.jpg',(252,400,928,1290)),'Para quem vive a correr e já não vê nada.'),
 ('Deixa para Lá','Mel Robbins','1 900 MT','1 750 MT',('photo','fotos/livros/deixa-pra-la_anuncio.jpg','deixa-pra-la'),'Para parar de gastar energia com os outros.'),
 ('Pense Rápido, Fale Melhor','Matt Abrahams','1 900 MT','1 750 MT',('raw','fotos/livros/pense-rapido-fale-melhor_mao_hd.jpg',(195,330,955,1310)),'Para não ficar sem palavras na hora certa.')]
rec=json.load(open(R+'data/recortes.json'))
for i,(t,a,old,new,img,line) in enumerate(books):
    im=Image.new('RGBA',(W,H),CREAM+(255,)); d=ImageDraw.Draw(im)
    pw=d.textlength('BLACK OFERTA',font=f(BOLD,30)); d.rounded_rectangle([60,60,60+pw+56,118],29,fill=NAVY)
    d.text((88,72),'BLACK OFERTA',font=f(BOLD,30),fill=GOLD)
    d.text((W-170,70),f'{i+1}/7',font=f(MED,32),fill=(120,120,140))
    area=(140,160,940,860)  # zona da imagem
    if img and img[0]=='cover':
        c=Image.open(R+f'fotos/livros/capas/{img[1]}.png').convert('RGB'); hh=640; c=c.resize((int(c.width*hh/c.height),hh))
        sh=Image.new('RGBA',(c.width+80,c.height+80),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle([40,52,c.width+40,c.height+52],10,fill=(0,0,0,110))
        sh=sh.filter(ImageFilter.GaussianBlur(16)); x=(W-c.width)//2; im.alpha_composite(sh,(x-40,180-40)); im.paste(c,(x,180))
    elif img and img[0]=='raw':
        ph=Image.open(R+img[1]).convert('RGB').crop(img[2])
        ph=ImageEnhance.Contrast(ph).enhance(1.05); ph=ph.filter(ImageFilter.UnsharpMask(radius=2,percent=70,threshold=2))
        hh=660; ph=ph.resize((int(ph.width*hh/ph.height),hh),Image.LANCZOS); m=Image.new('L',ph.size,0); ImageDraw.Draw(m).rounded_rectangle([0,0,ph.width-1,hh-1],26,fill=255)
        x=(W-ph.width)//2; im.paste(ph,(x,175),m)
    elif img:
        ph=Image.open(R+img[1]).convert('RGB'); ph=ph.resize((1350,1350)); cr=rec[img[2]]; ph=ph.crop(cr)
        hh=660; ph=ph.resize((int(ph.width*hh/ph.height),hh)); m=Image.new('L',ph.size,0); ImageDraw.Draw(m).rounded_rectangle([0,0,ph.width-1,hh-1],26,fill=255)
        x=(W-ph.width)//2; im.paste(ph,(x,175),m)
    else:  # cartão tipográfico (sem foto real)
        cw,ch=470,640; x=(W-cw)//2; y0=180
        sh=Image.new('RGBA',(cw+80,ch+80),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle([40,52,cw+40,ch+52],10,fill=(0,0,0,90)); sh=sh.filter(ImageFilter.GaussianBlur(16)); im.alpha_composite(sh,(x-40,y0-40))
        d.rounded_rectangle([x,y0,x+cw,y0+ch],8,fill=NAVY)
        d.rectangle([x+28,y0+28,x+cw-28,y0+ch-28],outline=GOLD,width=2)
        # título no cartão
        ft=f(SER,58); words=t.split(); lines=[]; line=''
        for w in words:
            if d.textlength((line+' '+w).strip(),font=ft)<=cw-110: line=(line+' '+w).strip()
            else: lines.append(line); line=w
        lines.append(line); ty=y0+ch//2-len(lines)*34-40
        for l in lines: d.text((x+(cw-d.textlength(l,font=ft))/2,ty),l,font=ft,fill=CREAM); ty+=68
        fa=f(EBI,40); an=a.split(' · ')[0]; d.text((x+(cw-d.textlength(an,font=fa))/2,ty+30),an,font=fa,fill=GOLD)
    # textos
    y=880
    fl=f(SER,52); y=wrapc(d,y,t,fl,(30,30,40),maxw=940,lh=1.12)
    y=wrapc(d,y+4,a,f(MED,32),(110,104,96))
    fo=f(IT,52); fn=f(IT,96); ow=d.textlength(old,font=fo); nw=d.textlength(new,font=fn); x0=(W-(ow+36+nw))/2; py=y+18
    d.text((x0,py+34),old,font=fo,fill=(150,140,130)); d.line([(x0-4,py+70),(x0+ow+4,py+60)],fill=(200,50,50),width=4)
    d.text((x0+ow+36,py),new,font=fn,fill=NAVY)
    im.convert('RGB').save(out+f'feed_tarde_v2_{i+2}.jpg',quality=93)
# CTA
im=base(); d=ImageDraw.Draw(im)
ctext(d,230,'BLACK FRIDAY NA NOSTOS',f(BOLD,46),GOLD)
y=wrapc(d,330,'Escolha o seu (ou o de quem ama).',f(SER,84),CREAM,maxw=900)
y=wrapc(d,y+30,'Livros novos · entrega em Maputo, Matola e todo o país.',f(MED,40),(210,214,230),maxw=880)
t3='WhatsApp 87 943 1217'; f3=f(BOLD,56); tw=d.textlength(t3,font=f3)
d.rounded_rectangle([(W-tw)/2-44,y+60,(W+tw)/2+44,y+170],55,fill=CREAM); d.text(((W-tw)/2,y+84),t3,font=f3,fill=NAVY)
ctext(d,y+230,'Leia. Regresse a si.',f(EBI,64),CREAM)
logo(im); im.convert('RGB').save(out+'feed_tarde_v2_9.jpg',quality=93)
