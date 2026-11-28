import subprocess, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R='/home/claude/nosts-posts/'; F=R+'engine/fonts/'
W,H,FPS=1080,1920,30
def f(n,s): return ImageFont.truetype(F+n,s)
def ease(t): t=max(0,min(1,t)); return 1-(1-t)**3
def frames(path,start,dur,w=W,h=H):
    raw=subprocess.run(['ffmpeg','-v','error','-ss',str(start),'-t',f'{dur:.3f}','-i',path,'-vf',f'scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={FPS}','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    n=len(raw)//(w*h*3); return [Image.frombuffer('RGB',(w,h),raw[i*w*h*3:(i+1)*w*h*3]) for i in range(n)]
# --- calculadora genérica
def calc():
    im=Image.new('RGB',(W,H),(0,0,0)); d=ImageDraw.Draw(im)
    d.text((W-140,780),'0',font=f('Inter-Medium.otf',190),fill='white')
    keys=[['⌫','AC','%','÷'],['7','8','9','×'],['4','5','6','−'],['1','2','3','+'],['+/−','0',',','=']]
    r=105; gx=[150,400,650,900]; y0=1080
    for i,row in enumerate(keys):
        for j,k in enumerate(row):
            cx,cy=gx[j],y0+i*245
            col=(255,159,10) if j==3 else ((165,165,165) if i==0 else (51,51,51))
            d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col)
            fk=f('Inter-Medium.otf',80 if len(k)<3 else 60); tc=(0,0,0) if (i==0 and j<3) else (255,255,255)
            d.text((cx-d.textlength(k,font=fk)/2,cy-48),k,font=fk,fill=tc)
    return im
CALC=calc()
# --- moldura tipo Reels (genérica, sem logótipo)
def reels_overlay():
    o=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(o)
    g=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(g)
    for y in range(320): gd.line([(0,H-y),(W,H-y)],fill=(0,0,0,int(160*(1-y/320))))
    o.alpha_composite(g)
    d.text((40,70),'‹  Reels',font=f('Inter-ExtraBold.otf',52),fill='white')
    x=W-95; y=1180
    for ico,num in [('♡','2,4 mil'),('💬',''),('↻',''),('➤','')]:
        pass
    # ícones simples desenhados
    def heart(cx,cy,s):
        d.polygon([(cx-s,cy-s*0.2),(cx,cy+s),(cx+s,cy-s*0.2)],outline='white',width=6)
        d.ellipse([cx-s,cy-s*0.8,cx,cy+0.1*s],outline='white',width=6); d.ellipse([cx,cy-s*0.8,cx+s,cy+0.1*s],outline='white',width=6)
    heart(x,y,34); d.ellipse([x-34,y+120,x+34,y+188],outline='white',width=6)
    d.polygon([(x-34,y+300),(x+38,y+268),(x-4,y+340)],outline='white',width=6)
    d.ellipse([60,H-235,140,H-155],fill=(2,36,108)); d.text((76,H-222),'N',font=f('EBG.ttf',54),fill=(251,248,240))
    d.text((160,H-222),'nostos_livraria_mz',font=f('Inter-ExtraBold.otf',40),fill='white')
    bw=d.textlength('Seguir',font=f('Inter-Medium.otf',36))
    d.rounded_rectangle([590,H-228,590+bw+40,H-168],14,outline='white',width=3); d.text((610,H-222),'Seguir',font=f('Inter-Medium.otf',36),fill='white')
    d.text((60,H-140),'5 livros que ela nunca vai esquecer… ver mais',font=f('Inter-Medium.otf',34),fill=(235,235,235))
    return o
OV=reels_overlay()
def card(img,scale,radius=60):
    w,h=int(W*scale),int(H*scale); c=img.resize((w,h),Image.BILINEAR)
    m=Image.new('L',(w,h),0); ImageDraw.Draw(m).rounded_rectangle([0,0,w-1,h-1],int(radius*scale*1.6),fill=255); return c,m
def switcher_bg(src):
    return src.resize((W//10,H//10)).filter(ImageFilter.GaussianBlur(3)).resize((W,H))
P=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','/tmp/rd/v.mp4'],stdin=subprocess.PIPE)
class O:
    n=0
    def append(self,im): P.stdin.write(im.convert('RGB').tobytes()); O.n+=1; self.last=im
    def __iadd__(self,l):
        for i in l: self.append(i)
        return self
out=O()
# 1) abertura (choque): livros quase a cair – vídeo real, tremor + zoom rápido + texto
op=frames(R+'fotos/videos/colleen-hoover-5-livros.mp4',5.5,2.6)
for k,fr in enumerate(op):
    t=k/FPS; z=1+0.25*ease(t/2.6); sx=int(14*math.sin(k*1.7)) if t>1.2 else 0
    zw,zh=int(W*z),int(H*z); im=fr.resize((zw,zh)).crop(((zw-W)//2+sx,(zh-H)//2,(zw-W)//2+sx+W,(zh-H)//2+H))
    d=ImageDraw.Draw(im); txt='Não… não… NÃO 😳' if t>1.0 else 'Espere…'
    fo=f('Inter-ExtraBold.otf',72); tw=d.textlength(txt.replace(' 😳',''),font=fo)
    d.text(((W-tw)/2+3,383),txt.replace(' 😳',''),font=fo,fill=(0,0,0)); d.text(((W-tw)/2,380),txt.replace(' 😳',''),font=fo,fill='white')
    out.append(im)
last=out.last
# 2) swipe para o seletor de apps: cartão encolhe e desliza; calculadora entra
n=int(1.0*FPS)
for k in range(n):
    a=ease(k/n); bg=switcher_bg(last); s=1-0.28*a
    c1,m1=card(last,s); c2,m2=card(CALC,0.72)
    im=bg.copy(); x1=int((W-c1.width)/2 - 700*a); y1=(H-c1.height)//2
    im.paste(c1,(x1,y1),m1); x2=int(W - (W-c2.width)/2*a - c2.width*a + (1-a)*200)
    x2=int((W-c2.width)/2 + (1-a)*900); im.paste(c2,(x2,(H-c2.height)//2),m2)
    ImageDraw.Draw(im).text((x2+20,(H-c2.height)//2-70),'Calculadora',font=f('Inter-Medium.otf',38),fill='white'); out.append(im)
# 3) calculadora aberta (abre ao centro) e fica 1,2 s
n=int(0.35*FPS)
for k in range(n):
    a=ease(k/n); s=0.72+0.28*a; c,m=card(CALC,s,radius=60*(1-a)+1); im=switcher_bg(last); im.paste(c,((W-c.width)//2,(H-c.height)//2),m); out.append(im)
out+= [CALC for _ in range(int(1.0*FPS))]
# 4) swipe: calculadora sai, aba do Instagram (Reels) com o nosso vídeo entra
ours=[frames(R+'posts/prontos/reel_colleen_namorada.mp4',0,0.04)[0]]
n=int(0.9*FPS)
for k in range(n):
    a=ease(k/n); bg=switcher_bg(CALC); c1,m1=card(CALC,0.72); c2,m2=card(ours[0],0.72)
    im=bg.copy(); im.paste(c1,(int((W-c1.width)/2-900*a),(H-c1.height)//2),m1)
    x2=int((W-c2.width)/2+(1-a)*900); im.paste(c2,(x2,(H-c2.height)//2),m2)
    ImageDraw.Draw(im).text((x2+20,(H-c2.height)//2-70),'Instagram',font=f('Inter-Medium.otf',38),fill='white'); out.append(im)
n=int(0.35*FPS)
for k in range(n):
    a=ease(k/n); s=0.72+0.28*a; c,m=card(ours[0],s,radius=60*(1-a)+1); im=switcher_bg(CALC); im.paste(c,((W-c.width)//2,(H-c.height)//2),m); out.append(im)
src=subprocess.Popen(['ffmpeg','-v','error','-i',R+'posts/prontos/reel_colleen_namorada.mp4','-vf',f'fps={FPS}','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
while True:
    b=src.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    im=Image.frombuffer('RGB',(W,H),b).convert('RGBA'); im.alpha_composite(OV); out.append(im)
P.stdin.close(); P.wait(); print(O.n/FPS)
