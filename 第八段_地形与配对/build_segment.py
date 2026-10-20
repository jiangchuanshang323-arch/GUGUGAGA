from pathlib import Path
import sys,math,json,subprocess,importlib.util,hashlib
from PIL import Image,ImageDraw,ImageOps
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
sys.path.insert(0,str(PROJECT/'卷图推板与五牌'))
s=importlib.util.spec_from_file_location('base8',PROJECT/'卷图推板与五牌/update_parts.py');o=importlib.util.module_from_spec(s);s.loader.exec_module(o)
from refine_components import install
install(o)
M=json.loads((ROOT/'台词与时间轴.json').read_text(encoding='utf-8'));ROWS=M['lines'];DURATION=M['duration']
F=o.F;E=o.m.ease;INK=o.INK;BLUE=o.BLUE;ORANGE=o.ORANGE;CREAM=o.CREAM;V=o.p.native.v
TITLE=o.p.header('第五张·地形','气候变化 → 地表侵蚀与堆积')
QUIZ=o.p.header('互动·要素配对','按本课讲解重点，找出联系')
MAPS=[]
for name in ['论文页8_图0_Im13.png','论文页8_图1_Im14.png']:
 art=Image.open(ROOT/'素材'/name).convert('RGB')
 # Identical editorial crop in both dated maps, no rotation or nonuniform scaling.
 MAPS.append(art.crop((0,520,art.width,1173)).resize((820,644),Image.Resampling.LANCZOS))
AUDIT=[]
def row(mode):return next(r for r in ROWS if r['mode']==mode)
def txt(im,s,x,y,size=60,color=INK,center=False):
 o.txt(im,s,x,y,size,color,center);b=F(size).getbbox(s);w=b[2]-b[0];h=b[3]-b[1];box=[x-w/2 if center else x,y,x+w/2 if center else x+w,y+h]
 assert box[0]>=14 and box[2]<=1906 and box[1]>=12 and box[3]<=1068,(s,box)
 AUDIT.append(dict(text=s,box=box))
def pill(im,s,cx,y,size=56,color=INK):
 w=F(size).getlength(s)+38;h=size+25
 ImageDraw.Draw(im).rounded_rectangle((cx-w/2,y,cx+w/2,y+h),16,fill=CREAM,outline='#a9c7cd',width=2)
 txt(im,s,cx,y+12,size,color,True)
def arrow(im,pts,color=BLUE,width=7,q=1):
 if q<=0:return
 n=max(2,min(len(pts),round(1+(len(pts)-1)*E(q))));o.p.native.arrow(im,pts[:n],color,width,1)
def bg():
 im=o.m.BG.copy();ImageDraw.Draw(im).rounded_rectangle((34,179,1886,945),24,fill=CREAM,outline='#a8c5cf',width=2);return im
def process(t,closing=False):
 im=bg();d=ImageDraw.Draw(im);age=t-row('机制')['start']
 if closing:age=12
 txt(im,'改变地表过程，不直接推动地壳',960,218,65,INK,True)
 stages=[('海温异常','海洋',.0),('环流变化','大气',2.8),('降水与海浪','外力条件',4.6),('侵蚀与堆积','地表形态',6.0)]
 for i,(s,label,start) in enumerate(stages):
  q=E((age-start)/.55)
  if not q:continue
  x=110+i*448;y=352+12*(1-q)
  d.rounded_rectangle((x,y,x+355,y+185),20,fill='#e4eff0' if i<3 else '#f5e7d2',outline='#a7c2c9',width=2)
  txt(im,s,x+177,y+29,54,ORANGE if i==3 else INK,True);txt(im,label,x+177,y+111,43,BLUE,True)
  if i:arrow(im,[(x-74,y+90),(x-13,y+90)],BLUE,5,(age-start)/.55)
 # Sediment moves down a slope into a basin; this is a process section, not a map.
 d.polygon([(120,679),(490,725),(1030,785),(1500,798),(1800,798),(1800,912),(120,912)],fill='#bda480')
 d.polygon([(1020,690),(1800,690),(1800,798),(1500,798),(1030,785)],fill='#b5d5dc')
 path=V.cubic((140,660),(650,680),(980,770),(1460,778),90)
 if age>5:
  for i in range(22):
   q=((t*.2+i/22)%1);x,y=path[round(q*89)];d.ellipse((x-5,y-3,x+5,y+4),fill='#8d7459')
  d.polygon([(1310,788),(1480,775),(1630,798),(1310,798)],fill='#d9bd8c')
  pill(im,'搬运 → 堆积',1490,824,54,ORANGE)
 if closing:pill(im,'水和泥沙的重新分配',570,826,59,BLUE)
 return im
def case(t):
 im=bg();age=t-row('河口')['start'];d=ImageDraw.Draw(im)
 if age<6.9:pill(im,'三次事件：三角洲长约1.7—1.8 km',1275,57,45,BLUE)
 else:pill(im,'邻近海滩影响最远约7 km',1300,57,49,BLUE)
 for x,art in zip((65,1035),MAPS):im.paste(art,(x,285))
 pill(im,'2017年4月 · 河口三角洲',475,195,49,BLUE)
 pill(im,'2018年1月 · 九个月后',1445,195,49,BLUE)
 # Source coordinates below refer to the identical (0,520) crop of Figure 7.
 if 3.6<age<6.9:
  q=E((age-3.6)/.5);layer=Image.new('RGBA',im.size);ld=ImageDraw.Draw(layer)
  x=65+565*820/831;y=285+(1015-520)*644/653
  ld.ellipse((x-95,y-80,x+92,y+74),outline=(255,239,185,round(210*q)),width=4)
  im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
 if age>=6.9:
  path=V.cubic((1575,819),(1520,713),(1620,590),(1688,433),70)
  arrow(im,path,'#f3ddb0',6,(age-6.9)/.6)
  pill(im,'沿岸输沙',1330,364,49,BLUE)
 txt(im,'图七：2017沿岸厄尔尼诺后的里马克河口 · 论文原图7局部',960,931,28,BLUE,True)
 return im
def floodplain(t):
 im=bg();d=ImageDraw.Draw(im);age=t-row('漫滩')['start'];flood=E((age-1.1)/2.4);settle=E((age-3.8)/2.3)
 txt(im,'亚马孙流域部分漫滩：冷事件也能促进堆积',960,211,59,INK,True)
 d.rounded_rectangle((85,326,1835,831),18,fill='#e6efec')
 # Stationary section: the water rises above the banks, spreads and then recedes.
 d.polygon([(88,594),(715,594),(755,742),(1165,742),(1205,594),(1832,594),(1832,828),(88,828)],fill='#b8a380')
 d.polygon([(90,690),(720,690),(750,750),(1170,750),(1200,690),(1830,690),(1830,828),(90,828)],fill='#9b8668')
 level=685-155*flood+85*settle
 if level<594:
  d.rectangle((88,level,1832,594),fill='#afd0d7')
  d.polygon([(715,594),(755,742),(1165,742),(1205,594)],fill='#9bc6d2')
 else:
  inset=(level-594)/148*40;d.polygon([(715+inset,level),(755,742),(1165,742),(1205-inset,level)],fill='#9bc6d2')
 if flood>.15:
  for side in [-1,1]:
   for i in range(11):
    q=(t*.17+i/11)%1;x=960+side*(210+q*620);y=566+math.sin(i+t)*10
    if settle>.05:y+=settle*(25+q*5)
    d.ellipse((x-4,y-3,x+4,y+3),fill='#b89d70')
  if not settle:
   arrow(im,[(735,553),(330,553)],BLUE,6,(age-2)/.5);arrow(im,[(1185,553),(1590,553)],BLUE,6,(age-2)/.5)
 if settle:
  thickness=round(17*settle)
  d.rectangle((90,594-thickness,710,594),fill='#dfc89f');d.rectangle((1210,594-thickness,1830,594),fill='#dfc89f')
  pill(im,'泥沙留在漫滩',1490,676,55,ORANGE)
 else:pill(im,'洪水漫出河槽' if level<594 else '水位上升',960,754,53,BLUE)
 pill(im,'拉尼娜相关洪水',960,331,55,BLUE)
 txt(im,'Aalto等，Nature，2003｜安第斯—亚马孙前陆研究',960,877,38,BLUE,True)
 return im
CASES=['降水重分配','海气热交换','珊瑚白化','泥炭燃烧','河口堆积'];ANSWERS=['地形','生','水','土','气'];MATCH=[2,4,1,3,0]
def quiz(t):
 im=bg();d=ImageDraw.Draw(im)
 txt(im,'按本课讲解重点，把案例与要素相连',960,205,63,INK,True)
 reveal=t-row('揭晓')['start']
 for i,s in enumerate(CASES):
  y=309+i*122;d.rounded_rectangle((140,y,695,y+88),16,fill='#e7eff0',outline='#adc6ce',width=2);txt(im,s,418,y+17,56,INK,True)
 for i,s in enumerate(ANSWERS):
  y=309+i*122;d.rounded_rectangle((1315,y,1770,y+88),16,fill='#f3eadb',outline='#c8c5af',width=2);txt(im,s,1542,y+17,56,INK,True)
 if reveal>=0:
  for i,j in enumerate(MATCH):
   start=i*.52;q=E((reveal-start)/.45)
   if q<=0:continue
   y1=353+i*122;y2=353+j*122
   path=V.cubic((712,y1),(900,y1),(1115,y2),(1296,y2),65)
   arrow(im,path,BLUE if reveal<start+.8 else '#9dbdc7',6,q)
 if M['pause_start']<=t<M['pause_start']+3:
  # Darken the teaching board during the complete three-second thinking interval.
  overlay=Image.new('RGBA',im.size);ld=ImageDraw.Draw(overlay);ld.rounded_rectangle((35,180,1885,945),24,fill=(22,51,66,100))
  im=Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB');d=ImageDraw.Draw(im)
  d.ellipse((860,443,1060,643),fill=CREAM,outline='#b5cbd1',width=4)
  n=3-int(t-M['pause_start']);txt(im,str(n),960,480,108,BLUE,True)
 return im
def raw(t,r):
 if r['mode']=='机制':return process(t)
 if r['mode']=='河口':return case(t)
 if r['mode']=='漫滩':return floodplain(t)
 if r['mode']=='收束':return process(t,True)
 return quiz(t)
def title(im,art,age):
 q=E(age-1);scale=2.15-1.15*q;cx=960*(1-q)+(16+art.width/2)*q;cy=540*(1-q)+(14+art.height/2)*q
 a=art.resize((round(art.width*scale),round(art.height*scale)),Image.Resampling.LANCZOS);x=round(cx-a.width/2);y=round(cy-a.height/2)
 assert x>=0 and y>=0 and x+a.width<=1920 and y+a.height<=1080
 im.paste(a,(x,y),a)
def render(t):
 global AUDIT
 AUDIT=[];intro=next((a for a in M['intros'] if a['start']<=t<a['start']+2),None)
 if intro:r=row('机制') if intro==M['intros'][0] else row('提问')
 elif M['pause_start']<=t<M['pause_start']+3:r=row('提问')
 else:r=next((a for a in ROWS if a['start']<=t<a['end']),ROWS[0] if t<2 else ROWS[-1])
 im=raw(t,r)
 if r['mode'] in ('河口','漫滩','收束') and 0<=t-r['start']<.35:
  prev=ROWS[ROWS.index(r)-1];im=Image.blend(raw(prev['end']-.01,prev),im,E((t-r['start'])/.35))
 art=QUIZ if r['mode'] in ('提问','揭晓') else TITLE
 silent=bool(intro) or M['pause_start']<=t<M['pause_start']+3
 if intro:title(im,art,t-intro['start'])
 else:
  im.paste(art,(16,14),art)
  if not silent:o.subtitle(im,r['text'])
 return im,dict(t=t,mode=r['mode'],silent=silent,labels=AUDIT)
def main():
 times=[.5,1.7,5.7,9,13,17.3,21.5,25.5,29,M['intros'][1]['start']+.5,M['pause_start']+.5,DURATION-1.4]
 contact=Image.new('RGB',(1920,870),'#e5eeee');d=ImageDraw.Draw(contact)
 for i,t in enumerate(times):
  im,_=render(t);im.save(ROOT/'检查'/f'节点_{t:.2f}.png');x=i%4*480;y=i//4*290;contact.paste(im.resize((480,270)),(x,y));d.text((x+8,y+273),f'{t:.2f}s',fill=INK)
 contact.save(ROOT/'检查/设计节点.jpg')
 if '--preview' in sys.argv:return
 dest=PROJECT/'demooo/独立片段/08_地形与配对/海洋发烧了_第八段_地形与配对.mp4';dest.parent.mkdir(parents=True,exist_ok=True);pending=dest.with_name('.'+dest.stem+'.pending.mp4')
 proc=subprocess.Popen([o.EXE,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(ROOT/'配音/第八段_晓伊.wav'),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(pending)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 audit=[];count=math.ceil(DURATION*24)
 for i in range(count):
  im,a=render(i/24);audit.append(a);proc.stdin.write(im.tobytes())
  if i%240==0:print('Render',i,'/',count,flush=True)
 proc.stdin.close();err=proc.stderr.read();assert proc.wait()==0,err
 p=subprocess.run([o.EXE,'-v','error','-i',str(pending),'-f','null','-'],capture_output=True);assert p.returncode==0 and not p.stderr,p.stderr
 pending.replace(dest)
 (ROOT/'检查/逐帧文字边界.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 report=dict(output=str(dest),seconds=DURATION,frames=count,resolution=[1920,1080],fps=24,decode='PASS',character_present=False,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size)
 (ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
