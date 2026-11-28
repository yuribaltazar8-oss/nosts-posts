import subprocess
from PIL import Image, ImageDraw, ImageFilter
exec(open('make.py').read().split("P=subprocess.Popen")[0])   # funções, OV (moldura Reels), card(), etc.
SRC='/mnt/user-data/uploads/0e3f96d6-r07qxo_-_R_Download.mov'
# 1) vídeo do Yuri inteiro, só redimensionado para 1080x1920
subprocess.run(['ffmpeg','-v','error','-y','-i',SRC,'-vf','scale=1080:1920,fps=30','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','44100','-ac','2','/tmp/rd/p1.mp4'],check=True)
dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','/tmp/rd/p1.mp4'],capture_output=True,text=True).stdout)
last=Image.open(subprocess.run(['ffmpeg','-v','error','-sseof','-0.1','-i','/tmp/rd/p1.mp4','-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True).stdout and __import__('io').BytesIO(subprocess.run(['ffmpeg','-v','error','-sseof','-0.1','-i','/tmp/rd/p1.mp4','-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True).stdout)).convert('RGB')
# 2) transição: o ecrã do fim (calculadora) sai, entra a aba Instagram com o nosso vídeo + o nosso vídeo inteiro
P=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
   '-i',R+'posts/prontos/reel_colleen_namorada.mp4','-i',R+'sons/sfx/whoosh.m4a',
   '-filter_complex','[1:a]adelay=1250:all=1[a1];[2:a]volume=1.2[w];[a1][w]amix=inputs=2:duration=first:normalize=0,aresample=44100[a]',
   '-map','0:v','-map','[a]','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ac','2','/tmp/rd/p2.mp4'],stdin=subprocess.PIPE)
first=frames(R+'posts/prontos/reel_colleen_namorada.mp4',0.5,0.04)[0]
def w(im): P.stdin.write(im.convert('RGB').tobytes())
n=int(0.35*FPS)
for k in range(n):   # o ecrã atual encolhe para o seletor de apps
    a=ease(k/n); s=1-0.28*a; c,m=card(last,s,radius=60*a+1); im=switcher_bg(last); im.paste(c,((W-c.width)//2,(H-c.height)//2),m); w(im)
n=int(0.55*FPS)
for k in range(n):   # desliza: sai o ecrã atual, entra a aba Instagram
    a=ease(k/n); im=switcher_bg(last); c1,m1=card(last,0.72); c2,m2=card(first,0.72)
    im.paste(c1,(int((W-c1.width)/2-900*a),(H-c1.height)//2),m1)
    x2=int((W-c2.width)/2+(1-a)*900); im.paste(c2,(x2,(H-c2.height)//2),m2)
    ImageDraw.Draw(im).text((x2+20,(H-c2.height)//2-70),'Instagram',font=f('Inter-Medium.otf',38),fill='white'); w(im)
n=int(0.35*FPS)
for k in range(n):   # abre a aba
    a=ease(k/n); s=0.72+0.28*a; c,m=card(first,s,radius=60*(1-a)+1); im=switcher_bg(last); im.paste(c,((W-c.width)//2,(H-c.height)//2),m); w(im)
src=subprocess.Popen(['ffmpeg','-v','error','-i',R+'posts/prontos/reel_colleen_namorada.mp4','-vf',f'fps={FPS}','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
while True:
    b=src.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    im=Image.frombuffer('RGB',(W,H),b).convert('RGBA'); im.alpha_composite(OV); w(im)
P.stdin.close(); P.wait()
open('/tmp/rd/list.txt','w').write("file '/tmp/rd/p1.mp4'\nfile '/tmp/rd/p2.mp4'\n")
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i','/tmp/rd/list.txt','-c','copy','-movflags','+faststart',R+'posts/prontos/reel_redirect_colleen.mp4'],check=True)
print(dur)
