from pathlib import Path
import sys,json,math,subprocess,importlib.util,io
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;P=R.parent
s=importlib.util.spec_from_file_location('bridge9',P/'多米诺转场_企鹅串讲/build_transitions.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
M=json.loads((R/'台词与时间轴.json').read_text(encoding='utf-8'));ROWS=M['lines'];D=M['duration'];F=b.F;INK=b.INK;BLUE=b.BLUE;ORANGE='#ce8561';E=b.E
OUT=P/'demooo/独立片段/09_辨析与滞后/海洋发烧了_第九段_辨析与滞后.mp4';OUT.parent.mkdir(parents=True,exist_ok=True)
CHECK=R/'检查';CHECK.mkdir(exist_ok=True)
PCM=b.read_pcm(R/'配音/第九段.wav');AUDIT=[]
POSE10=Image.open(next(b.SPRITES.glob('10_*'))).convert('RGBA').resize((390,390),Image.Resampling.LANCZOS)
HEADS=[b.o.p.header('辨析·不是同一个概念','厄尔尼诺与人为全球增暖'),b.o.p.header('解释·为什么会滞后','海温变化与区域影响，不必同步')]
def row(mode):return next(r for r in ROWS if r['mode']==mode)
def text(im,s,x,y,size=55,color=INK,center=False):
 box=F(size).getbbox(s);w=F(size).getlength(s);xx=x-w/2 if center else x
 assert 20<=xx and xx+w<=1900 and 14<=y and y+size<=1062,(s,xx,y,w)
 b.o.txt(im,s,x,y,size,color,center);AUDIT.append((s,[xx,y,xx+w,y+size]))
def panel(im,box,fill='#fffaf0',outline='#b6cdd2'):
 ImageDraw.Draw(im).rounded_rectangle(box,24,fill=fill,outline=outline,width=2)
def arrow(im,pts,color=BLUE,width=6):b.o.p.native.arrow(im,pts,color,width,1)
def curve(im,pts,q,color,width=7):
 n=min(len(pts),max(0,round(len(pts)*E(q))))
 if n>1:ImageDraw.Draw(im).line(pts[:n],fill=color,width=width,joint='curve')
def chapter(im,t,index):
 begin=0 if index==0 else M['chapter2'];age=t-begin;h=HEADS[index]
 if age>=2:im.paste(h,(0,0),h);return
 # Same approved one-second hold, one-second docking; speech starts after docking.
 q=E(age-1);scale=1.28-.28*q;art=h.resize((round(h.width*scale),round(h.height*scale)),Image.Resampling.LANCZOS)
 x=round((960-art.width/2)*(1-q));y=round((450-art.height/2)*(1-q));im.paste(art,(x,y),art)
def concepts(im,t):
 d=ImageDraw.Draw(im)
 text(im,'分清概念，再判断影响',1165,235,65,INK,True)
 for k,(name,sub,col,y,mode) in enumerate([('自然波动','年际起伏',BLUE,360,'自然'),('人为增暖','长期趋势',ORANGE,635,'增暖')]):
  age=t-row(mode)['start'];active=row(mode)['start']<=t<row(mode)['end']
  panel(im,(492,y-18,1840,y+225),fill='#edf5f6' if k==0 else '#fbf0e4',outline=col if active else '#c2d2d5')
  text(im,name,520,y+7,58,col);text(im,sub,520,y+91,44,INK)
  x0,x1=895,1765;cy=y+139
  d.line((x0,y+183,x1,y+183),fill='#b2c6cb',width=3)
  text(im,'示意',1745,y+188,26,BLUE)
  if age>=0:
   pts=[]
   for n in range(181):
    u=n/180;x=x0+u*(x1-x0)
    yy=cy-40*math.sin(u*math.pi*5.3)-18*math.sin(u*math.pi*11+.4) if k==0 else cy+15-112*u+9*math.sin(u*12)
    pts.append((x,yy))
   curve(im,pts,age/2,col,8)
 if t>=row('风险')['start']:
  text(im,'我们的责任：减少温室气体排放' if t>=row('责任')['start'] else '概念不同 · 风险可能共同抬高',1165,890,48,INK,True)
def lag(im,t):
 d=ImageDraw.Draw(im);age=t-row('储热')['start'];later=t>=row('调整')['start']
 text(im,'海温与区域影响，峰值不必同步' if later else '海洋储热、释热都需要时间',1165,235,62,INK,True)
 if not later:
  # Conceptual ocean section: no geographical outline and no invented observations.
  panel(im,(510,350,1820,828),fill='#edf5f5')
  for y in range(495,785):
   c=(round(163-(y-495)*.19),round(208-(y-495)*.16),round(220-(y-495)*.10));d.line((535,y,1795,y),fill=c)
  water=[(x,493+6*math.sin(x/100+t)) for x in range(535,1796,6)];d.line(water,fill='#7eafc1',width=5)
  for i in range(8):
   x=630+i*145;y=568+36*math.sin(t*.7+i);d.ellipse((x-12,y-12,x+12,y+12),fill='#e8b581')
  text(im,'储热',770,392,59,ORANGE,True);text(im,'缓慢释放',1490,392,59,ORANGE,True)
  arrow(im,[(770,455),(770,558)],ORANGE,7);arrow(im,[(1490,556),(1490,455)],ORANGE,7)
  text(im,'水的比热容大',1165,719,61,'#315b6c',True)
  text(im,'海洋像一个大热库',1165,862,53,BLUE,True)
 else:
  text(im,'同一时间轴，响应可能错开',1165,328,43,BLUE,True)
  x0,x1=770,1755
  for i,(name,y,col,peak,mode) in enumerate([('海温变化',530,BLUE,.38,'调整'),('区域影响',765,ORANGE,.66,'错峰')]):
   text(im,name,520,y-52,48,col)
   d.line((x0,y+55,x1,y+55),fill='#aec5cc',width=3)
   text(im,'时间',1770,y+41,30,BLUE)
   q=(t-row(mode)['start'])/2.2
   pts=[(x0+u*(x1-x0),y+36-118*math.exp(-((u-peak)/.17)**2)) for u in np.linspace(0,1,181)]
   curve(im,pts,q,col,8)
   if q>=1:
    xx=x0+peak*(x1-x0);d.ellipse((xx-8,y-90,xx+8,y-74),fill=col)
  if t>=row('错峰')['start']+2.2:
   xa=x0+.38*(x1-x0);xb=x0+.66*(x1-x0)
   for yy in range(455,604,14):d.line((xa,yy,xa,yy+6),fill='#a9c7d0',width=2)
   for yy in range(611,676,14):d.line((xb,yy,xb,yy+6),fill='#dfb59e',width=2)
   arrow(im,[(xa,606),(xb,606)],ORANGE,5)
   text(im,'响应可能滞后',1275,621,35,ORANGE,True)
  text(im,'因地区、季节和影响类型而异',1165,897,43,INK,True)
  text(im,'示意',1795,396,29,BLUE)
def frame(t):
 global AUDIT
 AUDIT=[];b.AUDIT=[];im=b.o.m.BG.copy();idx=int(t>=M['chapter2']);intro=(t<2 or M['chapter2']<=t<M['chapter2']+2)
 panel(im,(452,211,1880,956))
 if not intro:
  if not idx:concepts(im,t)
  else:lag(im,t)
 chapter(im,t,idx)
 thinking=M['thinking'][0]<=t<M['thinking'][1]
 r=next((r for r in ROWS if r['start']<=t<r['end']),None)
 mode=r['mode'] if r else ''
 pose=9 if thinking or (mode=='储热' and t-r['start']<1.7) else 10 if mode=='风险' else 3 if mode in ('开题','自然','增暖','责任','提问','回答','衔接') else 6
 art=(POSE10 if pose==10 else b.POSES[pose]).copy()
 if pose in (3,6):
  p=PCM[int(t*24000):int(t*24000)+960].astype(np.float32)/32768;rms=float(np.sqrt(np.mean(p*p))) if len(p) else 0
  state=0 if rms<.011 else 1 if rms<.055 else 2 if rms<.13 else 3
  mx,my,mw,mh=b.o.m.MOUTH_CENTERS[pose];art.alpha_composite(b.MOUTHS[pose,state],(round((mx-mw/2)*390/512),round((my-mh/2)*390/512)))
 yy=round(580+1.8*math.sin(t*2));im.paste(art,(20,yy),art);b.AUDIT.append(dict(kind='character',pose=pose,box=[20,yy,410,yy+390]))
 if r and not intro:b.bubble(im,r['text'],t-r['start'],r['speech_end']-r['start'])
 if thinking:
  shade=Image.new('RGBA',im.size,(0,0,0,0));ImageDraw.Draw(shade).rounded_rectangle((452,211,1880,956),24,fill=(30,60,75,65));im=Image.alpha_composite(im.convert('RGBA'),shade).convert('RGB')
  panel(im,(950,405,1380,725));text(im,str(3-int(t-M['thinking'][0])),1165,453,140,INK,True)
  b.bubble(im,'能全算在厄尔尼诺头上吗？',0,3)
 return im
def main():
 n=math.ceil(D*24);tmp=OUT.with_name('.第九段.pending.mp4');log=(R/'编码日志.txt').open('wb')
 proc=subprocess.Popen([b.FF,'-v','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(R/'配音/第九段.wav'),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart','-shortest',str(tmp)],stdin=subprocess.PIPE,stderr=log)
 audits=[]
 for i in range(n):
  im=frame(i/24);proc.stdin.write(im.convert('RGB').tobytes());audits.append(dict(frame=i,text=AUDIT,character=b.AUDIT))
  if i%240==0:print('frame',i,'/',n,flush=True)
 proc.stdin.close();assert proc.wait()==0;log.close();b.manager.decode(tmp);tmp.replace(OUT)
 times=[2.3,row('自然')['start']+2,row('增暖')['start']+2,row('风险')['start']+2,M['thinking'][0]+1,row('回答')['start']+1,row('储热')['start']+3,row('调整')['start']+2,row('错峰')['end']-.2,row('条件')['start']+2,D-.5]
 sheet=Image.new('RGB',(1920,1080),'#dde8eb')
 for j,t in enumerate(times):
  raw=subprocess.run([b.FF,'-v','error','-ss',str(t),'-i',str(OUT),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True,check=True).stdout
  im=Image.open(io.BytesIO(raw));im.save(CHECK/f'{j:02d}_{t:.2f}.png');thumb=im.resize((480,270),Image.Resampling.LANCZOS);sheet.paste(thumb,((j%4)*480,(j//4)*360));ImageDraw.Draw(sheet).text(((j%4)*480+12,(j//4)*360+278),f'{t:.2f}s',font=F(25),fill=INK)
 sheet.save(CHECK/'编码抽帧总览.jpg')
 (CHECK/'逐帧对象边界.json').write_text(json.dumps(audits,ensure_ascii=False),encoding='utf-8')
 info=b.manager.info(OUT);(CHECK/'验证.json').write_text(json.dumps(dict(**info,resolution='1920x1080',fps=24,frames=n,decode='PASS',review_nodes=times,subtitle_rule='角色全程在场，仅使用46号公共基线气泡'),ensure_ascii=False,indent=2),encoding='utf-8')
 data=json.loads(b.manager.MANIFEST.read_text(encoding='utf-8'));data['segments']['09_辨析与滞后']=dict(path=str(OUT.relative_to(b.manager.ROOT)),**info,decode='PASS');b.manager.write_manifest(data);print(str(OUT),info,flush=True)
if __name__=='__main__':main()
