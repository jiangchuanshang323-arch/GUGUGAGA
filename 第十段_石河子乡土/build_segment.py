from pathlib import Path
import sys,json,math,io,subprocess,importlib.util
import numpy as np
from PIL import Image,ImageDraw,ImageOps
R=Path(__file__).resolve().parent;P=R.parent
s=importlib.util.spec_from_file_location('base10',P/'多米诺转场_企鹅串讲/build_transitions.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
M=json.loads((R/'台词与时间轴.json').read_text(encoding='utf-8'));ROWS=M['lines'];D=M['duration'];F=b.F;E=b.E;INK=b.INK;BLUE=b.BLUE;ORANGE='#ce8561';CREAM=b.CREAM
OUT=P/'demooo/独立片段/10_石河子乡土/海洋发烧了_第十段_石河子乡土.mp4';OUT.parent.mkdir(parents=True,exist_ok=True)
CHECK=R/'检查';CHECK.mkdir(exist_ok=True);AUDIT=[]
HEAD=b.o.p.header('乡土·从太平洋到石河子','远距离的气候联系，需要本地证据')
MAPS={k:Image.open(R/'素材'/v).convert('RGB') for k,v in [('中国','中国标准图.jpg'),('新疆','新疆标准图.jpg'),('石河子','石河子标准图.jpg')]}
PHOTO=ImageOps.contain(Image.open(R/'素材/farm.jpg').convert('RGB'),(770,514),Image.Resampling.LANCZOS)
def row(mode):return next(r for r in ROWS if r['mode']==mode)
def text(im,s,x,y,size=56,color=INK,center=False):
 w=F(size).getlength(s);xx=x-w/2 if center else x;assert 20<=xx and xx+w<=1900 and 14<=y and y+size<=1064,(s,xx,y,w)
 b.o.txt(im,s,x,y,size,color,center);AUDIT.append(dict(text=s,box=[xx,y,xx+w,y+size]))
def panel(im,box,fill=CREAM):ImageDraw.Draw(im).rounded_rectangle(box,24,fill=fill,outline='#b3ccd1',width=2)
def arrow(im,pts,color=BLUE,width=6):b.o.p.native.arrow(im,pts,color,width,1)
def trace(im,pts,q,color=BLUE,width=7):
 n=max(0,min(len(pts),round(E(q)*len(pts))))
 if n>1:ImageDraw.Draw(im).line(pts[:n],fill=color,width=width,joint='curve')
def fitmap(name,box):
 art=MAPS[name];w,h=box[2]-box[0],box[3]-box[1];q=min(w/art.width,h/art.height);return art.resize((round(art.width*q),round(art.height*q)),Image.Resampling.LANCZOS),q
BASES={};GEO={}
for name in ['中国','新疆']:
 im=b.o.m.BG.copy();panel(im,(30,161,1890,949),fill='#fffefd');art,q=fitmap(name,(50,167,1870,940));x=(1920-art.width)//2;y=167+(773-art.height)//2;im.paste(art,(x,y));BASES[name]=im;GEO[name]=(x,y,q)
# Full city map remains visible beside a clearly separated city-centre detail.
im=b.o.m.BG.copy();panel(im,(30,161,1890,949),fill='#fffefd');art,q=fitmap('石河子',(55,170,650,938));im.paste(art,(70,170));GEO['石河子']=(70,170,q)
detail=MAPS['石河子'].crop((700,1250,2700,2800));detail=ImageOps.contain(detail,(1100,570),Image.Resampling.LANCZOS);im.paste(detail,(710+(1100-detail.width)//2,275));BASES['石河子']=im
def maps(t,name):
 im=BASES[name].copy();d=ImageDraw.Draw(im)
 if name=='中国':
  if t>=row('差异')['start']:
   text(im,'区域不同',178,338,50,BLUE,True);text(im,'季节不同',178,411,50,BLUE,True);text(im,'影响有差异',1740,650,46,ORANGE,True)
 elif name=='新疆':
  text(im,'新疆',178,310,63,BLUE,True)
  x,y,q=GEO[name];xx=x+2485*q;yy=y+1244*q
  d.ellipse((xx-13,yy-13,xx+13,yy+13),outline=ORANGE,width=3)
  # Leader ends at the existing official point, not at a guessed location.
  d.line([(xx-15,yy),(430,yy),(430,380),(280,380)],fill=ORANGE,width=3);text(im,'石河子',175,392,53,ORANGE,True)
 else:
  text(im,'石河子 · 城区局部',1265,186,61,INK,True)
  text(im,'天山北麓 · 准噶尔盆地南缘',1265,881,48,BLUE,True)
 return im
def water(t):
 im=b.o.m.BG.copy();panel(im,(30,172,1890,947));text(im,'石河子的绿洲农业，离不开水',960,204,67,INK,True)
 im.paste(PHOTO,(66,320));text(im,'新疆天业现代农业示范区',451,845,43,INK,True);text(im,'膜下滴灌稻田',451,901,36,BLUE,True)
 d=ImageDraw.Draw(im);age=t-row('水源')['start'];span=row('水源')['speech_end']-row('水源')['start']
 d.polygon([(888,690),(1100,418),(1280,675),(1455,706),(1820,706),(1820,810),(888,810)],fill='#c7ceb9')
 d.polygon([(1042,495),(1100,418),(1150,493),(1128,483),(1100,497),(1072,482)],fill='#fffdf3')
 d.polygon([(1435,706),(1820,706),(1820,810),(1450,810)],fill='#c1d2ad')
 text(im,'山地',1070,771,46,INK,True);text(im,'绿洲农田',1630,835,50,INK,True)
 for i in range(5):
  x=1485+i*62;d.line((x,725,x+30,790),fill='#8da67e',width=4)
 # Sequential rain -> snowmelt -> runoff -> irrigation demand. No claim of inevitable El Nino rain.
 if age>1.8:
  text(im,'山地降水',1105,310,49,BLUE,True)
  for i in range(13):
   x=986+(i%7)*33;y=365+((t*65+i*19)%94);d.line((x,y,x-5,y+13),fill='#7dafc0',width=3)
 if age>3.1:
  text(im,'冰雪融水',1330,479,46,BLUE,True);arrow(im,[(1230,530),(1168,553)],BLUE,5)
 pts=b.o.p.native.v.cubic((1146,565),(1260,580),(1210,720),(1500,743),95)
 if age>4.0:
  trace(im,pts,(age-4)/.75,BLUE,11);text(im,'河流来水',1430,647,48,BLUE,True)
  for i in range(7):
   u=(t*.28+i/7)%1;x,y=pts[round(u*94)];d.ellipse((x-5,y-3,x+5,y+3),fill='#d9eef0')
 if age>5.65:
  trace(im,[(1500,743),(1610,743),(1700,776)],(age-5.65)/.7,BLUE,6);text(im,'何时灌溉？',1640,590,53,ORANGE,True)
 text(im,'水源与用水需求，要一起看',1380,898,41,INK,True)
 return im
def connection(t):
 im=b.o.m.BG.copy();panel(im,(30,172,1890,947));d=ImageDraw.Draw(im);age=t-row('遥相关')['start']
 text(im,'遥相关：相隔很远，也可能有关联',960,220,65,INK,True)
 boxes=[(100,457,550,681),(735,457,1185,681),(1370,457,1820,681)]
 names=['热带太平洋','大气环流','区域气候']
 for i,(box,name) in enumerate(zip(boxes,names)):
  q=E((age-i*1.25)/.5)
  if q<=0:continue
  panel(im,box,fill='#e7f1f2' if i!=1 else '#f6ecd9');text(im,name,(box[0]+box[2])/2,510,60,BLUE if i!=1 else ORANGE,True)
  if i==0:
   for k in range(2):d.line([(x,610+k*20+5*math.sin(x/28+t*1.9)) for x in range(150,503,3)],fill='#91b8c6',width=4)
  elif i==1:
   for k in range(3):
    x=795+((t*48+k*100)%260);d.arc((x,608+k*9,x+64,626+k*9),190,355,fill='#cda17f',width=4)
  else:
   for k in range(4):
    x=1450+k*80;yy=606+((t*24+k*13)%40);d.line((x,yy,x-4,yy+12),fill='#92b9c8',width=3)
  if i and age>i*1.25+.25:arrow(im,[(box[0]-150,568),(box[0]-30,568)],BLUE,6)
 if age>3.2:
  text(im,'远距离气候变化之间的统计联系',960,752,59,INK,True)
  text(im,'还要结合当地条件判断',960,849,48,BLUE,True)
 # Wind strokes move only across the atmospheric connector, never as ocean water towards Xinjiang.
 if age>2:
  for k in range(3):
   x=800+((t*65+k*85)%250);y=390+k*13;d.arc((x,y,x+60,y+14),185,355,fill='#aec9d1',width=3)
 return im
def judgement(t):
 im=b.o.m.BG.copy();panel(im,(452,211,1880,947));text(im,'不能直接给石河子贴“旱涝标签”',1165,251,62,INK,True)
 d=ImageDraw.Draw(im)
 for x,s in [(565,'一定涝'),(1225,'一定旱')]:
  panel(im,(x,391,x+520,578),fill='#eef3ef');text(im,s,x+260,443,69,BLUE,True)
  if t>row('判断')['start']+1.1:d.line((x+100,536,x+420,430),fill=ORANGE,width=5)
 if t>=row('预报')['start']:
  age=t-row('预报')['start'];text(im,'本地监测 + 最新预报',1165,665,64,INK,True)
  if age>1.3:arrow(im,[(1165,749),(1165,788)],BLUE,6);text(im,'供水与农业风险',1165,812,60,ORANGE,True)
 return im
def teacher(t,im):
 pcm=b.read_pcm(R/'配音/第十段.wav') if False else PCM
 if t<.8:
  art=b.POSES[3];x=round(20-430*E(t/.8));im.paste(art,(x,580),art);return
 r=next((r for r in ROWS if r['start']<=t<r['end']),None)
 enter=row('判断')['start']-.7
 if t>=enter:
  local=t-enter;b.teacher(im,local,pcm[round(enter*24000):],walk=True)
  if r:b.bubble(im,r['text'],t-r['start'],r['speech_end']-r['start'])
def frame(t):
 global AUDIT
 AUDIT=[];b.AUDIT=[];r=next((r for r in ROWS if r['start']<=t<r['end']),None)
 if t<row('新疆')['start']:im=maps(t,'中国')
 elif t<row('石河子')['start']:im=maps(t,'新疆')
 elif t<row('绿洲')['start']:im=maps(t,'石河子')
 elif t<row('遥相关')['start']:im=water(t)
 elif t<row('判断')['start']-.7:im=connection(t)
 else:im=judgement(t)
 # Brief dissolves only at meaningful changes; nothing flies off the map.
 for mode,previous in [('新疆','中国'),('石河子','新疆')]:
  start=row(mode)['start']
  if start<=t<start+.32:im=Image.blend(maps(t,previous),im,E((t-start)/.32))
 if t<2:
  q=E(t-1);scale=1.28-.28*q;art=HEAD.resize((round(HEAD.width*scale),round(HEAD.height*scale)),Image.Resampling.LANCZOS);im.paste(art,(round((960-art.width/2)*(1-q)),round((450-art.height/2)*(1-q))),art)
 else:im.paste(HEAD,(0,0),HEAD)
 teacher(t,im)
 if r and .8<=t<row('判断')['start']:
  # Full sentence follows narration; original 46px subtitle renderer splits readable clauses.
  chunks=[];s=''
  for ch in r['text']:
   s+=ch
   if ch in '。！？' or (ch=='，' and len(s)>9):chunks.append(s);s=''
  if s:chunks.append(s)
  n=sum(map(len,chunks));pos=min(n-.001,(t-r['start'])/max(.1,r['speech_end']-r['start'])*n);total=0
  for c in chunks:
   total+=len(c)
   if pos<total:b.o.subtitle(im,c);break
 return im
PCM=b.read_pcm(R/'配音/第十段.wav')
def main():
 n=math.ceil(D*24);tmp=OUT.with_name('.第十段.pending.mp4');log=(R/'编码日志.txt').open('wb');proc=subprocess.Popen([b.FF,'-v','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(R/'配音/第十段.wav'),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart','-shortest',str(tmp)],stdin=subprocess.PIPE,stderr=log)
 audits=[]
 for i in range(n):
  im=frame(i/24);proc.stdin.write(im.convert('RGB').tobytes());audits.append(dict(frame=i,text=AUDIT,character=b.AUDIT))
  if i%240==0:print('frame',i,'/',n,flush=True)
 proc.stdin.close();assert proc.wait()==0;log.close();b.manager.decode(tmp);tmp.replace(OUT)
 times=[3,9,row('新疆')['start']+.6,row('石河子')['start']+1,row('绿洲')['start']+.5,row('水源')['start']+3,row('水源')['start']+6.8,row('遥相关')['start']+4,row('判断')['start']+2,row('预报')['start']+2,D-.5]
 sheet=Image.new('RGB',(1920,1080),'#dfe9eb')
 for j,t in enumerate(times):
  raw=subprocess.run([b.FF,'-v','error','-ss',str(t),'-i',str(OUT),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True,check=True).stdout;im=Image.open(io.BytesIO(raw));im.save(CHECK/f'{j:02d}_{t:.2f}.png');sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),((j%4)*480,(j//4)*360));ImageDraw.Draw(sheet).text(((j%4)*480+8,(j//4)*360+278),f'{t:.2f}s',font=F(25),fill=INK)
 sheet.save(CHECK/'编码抽帧总览.jpg');(CHECK/'逐帧对象边界.json').write_text(json.dumps(audits,ensure_ascii=False),encoding='utf-8')
 info=b.manager.info(OUT);(CHECK/'验证.json').write_text(json.dumps(dict(**info,resolution='1920x1080',fps=24,frames=n,decode='PASS',review_nodes=times),ensure_ascii=False,indent=2),encoding='utf-8')
 data=json.loads(b.manager.MANIFEST.read_text(encoding='utf-8'));data['segments']['10_石河子乡土']=dict(path=str(OUT.relative_to(b.manager.ROOT)),**info,decode='PASS',word_shots=[23],comment_ids=[19]);b.manager.write_manifest(data);print(str(OUT),info,flush=True)
if __name__=='__main__':main()
