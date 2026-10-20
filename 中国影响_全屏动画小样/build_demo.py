from pathlib import Path
import json,math,sys,subprocess,importlib.util,io
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageChops
R=Path(__file__).resolve().parent;P=R.parent
s=importlib.util.spec_from_file_location('bchina',P/'多米诺转场_企鹅串讲/build_transitions.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
M=json.loads((R/'台词与时间轴.json').read_text(encoding='utf-8'));D=M['duration'];F=b.F;E=b.E;INK=b.INK;BLUE='#639dae';ORANGE='#cf936d';OUT=P/'demooo/预览/中国影响全屏动画/海洋发烧了_中国影响全屏动画小样.mp4';OUT.parent.mkdir(parents=True,exist_ok=True);AUDIT=[]
G=json.loads((R/'中国轮廓参考.json').read_text(encoding='utf-8'))['features'][0]['geometry']['coordinates']
# Native redraw from coordinates. Albers equal-area projection; no province borders or dense place names.
n=(math.sin(math.radians(25))+math.sin(math.radians(47)))/2;C=math.cos(math.radians(25))**2+2*n*math.sin(math.radians(25))
def albers(lon,lat):
 rho=math.sqrt(C-2*n*math.sin(math.radians(lat)))/n;theta=n*math.radians(lon-105);return rho*math.sin(theta),rho*math.cos(theta)
pts=[albers(*xy) for poly in G for ring in poly for xy in ring if xy[1]>=18]
xmin,ymin=np.min(pts,axis=0);xmax,ymax=np.max(pts,axis=0);S=min(1550/(xmax-xmin),755/(ymax-ymin));OX=100+(1550-(xmax-xmin)*S)/2;OY=170
def xy(lon,lat):
 x,y=albers(lon,lat);return OX+(x-xmin)*S,OY+(y-ymin)*S
POLYS=[]
for poly in G:
 if max(v[1] for v in poly[0])<18:continue
 POLYS.append([xy(*p) for p in poly[0]])
MASK=Image.new('L',(1920,1080));md=ImageDraw.Draw(MASK)
for p in POLYS:md.polygon(p,fill=255)
BASE=Image.new('RGB',(1920,1080));bd=ImageDraw.Draw(BASE)
for yy in range(1080):
 u=yy/1080;bd.line((0,yy,1920,yy),fill=(round(241-16*u),round(248-7*u),round(248-5*u)))
for j in range(4):bd.line([(x,270+j*180+12*math.sin(x/190+j)) for x in range(0,1921,5)],fill='#e0eef0',width=2)
shadow=MASK.filter(ImageFilter.GaussianBlur(8));BASE.paste('#b5cdd2',(4,7),shadow.point(lambda a:round(a*.35)))
BASE.paste('#f6efd9',(0,0),MASK)
bd=ImageDraw.Draw(BASE)
for p in POLYS:bd.line(p+[p[0]],fill='#6e939e',width=3,joint='curve')
# Country mask and paths are saved separately, so the illustration remains editable.
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080">']
for p in POLYS:svg.append('<path d="M '+' L '.join(f'{x:.2f},{y:.2f}' for x,y in p)+' Z" fill="#f6efd9" stroke="#6e939e" stroke-width="3"/>')
svg.append('</svg>');(R/'自绘中国轮廓.svg').write_text('\n'.join(svg),encoding='utf-8')
HEADER=b.o.p.header('中国影响·风与雨带','以厄尔尼诺次年夏季为例')
def text(im,s,x,y,size=54,color=INK,center=False):
 w=F(size).getlength(s);xx=x-w/2 if center else x;assert 20<=xx and xx+w<=1900 and 14<=y and y+size<=1064,(s,xx,y,w)
 b.o.txt(im,s,x,y,size,color,center);AUDIT.append(dict(text=s,box=[xx,y,xx+w,y+size]))
def cloud(im,cx,cy,scale=1,alpha=1):
 art=Image.new('RGBA',(250,140));d=ImageDraw.Draw(art)
 # A single curved cloud silhouette; soft corners are part of the contour.
 coords=[(17,89),(18,77),(24,65),(36,56),(50,53),(51,39),(59,26),(73,19),(88,21),(98,29),(107,15),(123,7),(139,9),(154,20),(160,35),(176,30),(193,33),(205,44),(210,59),(225,65),(237,77),(239,94),(228,108),(31,108)]
 d.polygon(coords,fill=(255,253,242,255));d.line(coords+[coords[0]],fill='#8db4bf',width=3,joint='curve')
 art=art.resize((round(200*scale),round(112*scale)),Image.Resampling.LANCZOS);art.putalpha(art.getchannel('A').point(lambda a:round(a*alpha)));im.paste(art,(round(cx-art.width/2),round(cy-art.height/2)),art)
def inset(im):
 d=ImageDraw.Draw(im);box=(1640,680,1880,926);d.rounded_rectangle(box,12,fill='#eef6f6',outline='#a7c6ce',width=2)
 def pp(p):return 1645+(p[0]-105)/20*230,688+(25-p[1])/23*224
 clip=Image.new('RGB',(240,246),'#eef6f6');cd=ImageDraw.Draw(clip)
 for poly in G:
  p=[(pp(v)[0]-1640,pp(v)[1]-680) for v in poly[0]]
  cd.polygon(p,fill='#f6efd9');cd.line(p+[p[0]],fill='#7b9ca5',width=1)
 im.paste(clip,(1640,680));d=ImageDraw.Draw(im);d.rounded_rectangle(box,12,outline='#a7c6ce',width=2);text(im,'南海诸岛',1760,884,28,INK,True)
def wind(im,path,t,age,width=8):
 q=E(age/2.7);k=max(2,round(q*(len(path)-1)));part=path[:k]
 if q<=0:return
 b.o.p.native.arrow(im,part,'#73aabd',width,1)
 d=ImageDraw.Draw(im)
 for i in range(6):
  u=(t*.27+i/6)%1
  if u>q:continue
  at=round(u*(len(path)-1));x,y=path[at];d.ellipse((x-4,y-4,x+4,y+4),fill='#e9f6f7')
PATHS=[]
for ps in [[(129,19),(127,24),(121,29),(116,31)],[(116,17),(115,22),(111,26),(110,30)]]:
 p=[xy(*v) for v in ps];PATHS.append(b.o.p.native.v.cubic(*p,100))
def frame(t):
 global AUDIT
 AUDIT=[];im=BASE.copy();d=ImageDraw.Draw(im);rain=max(0,min(1,(t-6.4)/1.1));diff=E((t-9.5)/2.6);shift=-17*diff
 if rain>0:
  layer=Image.new('RGBA',im.size);ld=ImageDraw.Draw(layer)
  # Organic, diffuse belt; clipped to the real country silhouette.
  center=[xy(lon,30+.7*math.sin(lon*.7)) for lon in np.linspace(105,122,90)]
  center=[(x,y+shift) for x,y in center];poly=[(x,y-47-8*math.sin(i*.32)) for i,(x,y) in enumerate(center)]+[(x,y+40+8*math.sin(i*.25)) for i,(x,y) in reversed(list(enumerate(center)))];ld.polygon(poly,fill=(100,176,192,round(95*rain)));layer=layer.filter(ImageFilter.GaussianBlur(16));layer.putalpha(ImageChops.multiply(layer.getchannel('A'),MASK));im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
 wind(im,PATHS[0],t,t-3.8);wind(im,PATHS[1],t,t-4.5,6)
 if t>4.2:
  text(im,'偏南风',1550,433,54,BLUE,True);text(im,'输送水汽',1550,501,50,BLUE,True)
 if t>6.1:
  q=E((t-6.1)/.7)
  for i,lon in enumerate([107.7,113.8,119.3]):
   cx,cy=xy(lon,30.7);cy+=shift;cloud(im,cx,cy-45+math.sin(t*1.5+i)*2,.77,q)
   rd=ImageDraw.Draw(im)
   if rain>0:
    for j in range(6):
     x=cx-49+j*20;y=cy+18+((t*65+j*17+i*11)%65);rd.line((x,y,x-7,y+16),fill='#74a9bd',width=3)
 if t>7:
  # Labels sit in open space; no pursuit circles, no obscured clouds or coast.
  text(im,'长江流域',1025,513,52,INK,True);text(im,'降水偏多的可能增加',1550,603,43,BLUE,True)
 inset(im);im.paste(HEADER,(0,0),HEADER)
 d=ImageDraw.Draw(im);d.rounded_rectangle((1390,32,1875,112),20,fill='#fffaf0',outline='#b7ced3',width=2);text(im,'次年夏季',1632,48,47,INK,True)
 if t>9.5:text(im,'事件不同，雨带也会变化',1520,155,36,INK,True)
 r=next((r for r in M['lines'] if r['start']<=t<r['end']),None)
 if r:
  words=r['text'];chunks=[];s=''
  for ch in words:
   s+=ch
   if ch in '。！？，' and len(s)>=8:chunks.append(s);s=''
  if s:chunks.append(s)
  pos=min(sum(map(len,chunks))-.001,(t-r['start'])/max(.1,r['speech_end']-r['start'])*sum(map(len,chunks)));acc=0
  for c in chunks:
   acc+=len(c)
   if pos<acc:b.o.subtitle(im,c);break
 return im
def main():
 n=math.ceil(D*24);tmp=OUT.with_name('.中国影响.pending.mp4');log=(R/'编码日志.txt').open('wb');proc=subprocess.Popen([b.FF,'-v','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(R/'配音/中国影响.wav'),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart','-shortest',str(tmp)],stdin=subprocess.PIPE,stderr=log);audits=[]
 for i in range(n):
  im=frame(i/24);proc.stdin.write(im.convert('RGB').tobytes());audits.append(dict(frame=i,text=AUDIT))
 proc.stdin.close();assert proc.wait()==0;log.close();b.manager.decode(tmp);tmp.replace(OUT)
 times=[1,4.8,7.3,9.0,11.5,D-.2];sheet=Image.new('RGB',(1440,700),'#e4eef0')
 for j,t in enumerate(times):
  raw=subprocess.run([b.FF,'-v','error','-ss',str(t),'-i',str(OUT),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True,check=True).stdout;im=Image.open(io.BytesIO(raw));im.save(R/'检查'/f'{j:02d}_{t:.2f}.png');sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),((j%3)*480,(j//3)*350));ImageDraw.Draw(sheet).text(((j%3)*480+10,(j//3)*350+280),f'{t:.2f}s',font=F(25),fill=INK)
 sheet.save(R/'检查/编码抽帧总览.jpg');info=b.manager.info(OUT);(R/'检查/验证.json').write_text(json.dumps(dict(**info,decode='PASS',frames=n,resolution='1920x1080',fps=24,review_nodes=times,character=False,shihezi=False),ensure_ascii=False,indent=2),encoding='utf-8')
 (R/'检查/逐帧文本边界.json').write_text(json.dumps(audits,ensure_ascii=False),encoding='utf-8');data=json.loads(b.manager.MANIFEST.read_text(encoding='utf-8'));data.setdefault('previews',{})['中国影响全屏动画']=dict(path=str(OUT.relative_to(b.manager.ROOT)),**info,decode='PASS');b.manager.write_manifest(data);print(str(OUT),info)
if __name__=='__main__':main()
