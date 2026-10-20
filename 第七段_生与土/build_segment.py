from pathlib import Path
import sys,math,json,subprocess,importlib.util,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageOps
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
sys.path.insert(0,str(PROJECT/'卷图推板与五牌'))
s=importlib.util.spec_from_file_location('base7',PROJECT/'卷图推板与五牌/update_parts.py');o=importlib.util.module_from_spec(s);s.loader.exec_module(o)
from refine_components import install
install(o)
META=json.loads((ROOT/'台词与时间轴.json').read_text(encoding='utf-8'));ROWS=META['lines'];DURATION=META['duration']
F=o.F;E=o.m.ease;INK=o.INK;BLUE=o.BLUE;ORANGE=o.ORANGE;CREAM=o.CREAM
CORAL=Image.open(ROOT/'素材/NOAA_Jarvis珊瑚白化.jpg').convert('RGB')
SMOKE=Image.open(PROJECT/'环境多米诺_水_v37/素材/NASA_2015印尼烟霾.jpg').convert('RGB')
TITLES=[o.p.header('第三张·生','上升流、食物来源与珊瑚热压力'),o.p.header('第四张·土','干旱、泥炭火灾与土壤保护')]
AUDIT=[]
def txt(im,s,x,y,size=60,color=INK,center=False):
 o.txt(im,s,x,y,size,color,center);b=F(size).getbbox(s);w=b[2]-b[0];h=b[3]-b[1]
 box=[x-w/2 if center else x,y,x+w/2 if center else x+w,y+h]
 assert box[0]>=14 and box[2]<=1906 and box[1]>=12 and box[3]<=1068,(s,box)
 AUDIT.append(dict(text=s,box=box))
def pill(im,s,cx,y,size=56,color=INK):
 w=F(size).getlength(s)+38;h=size+25
 ImageDraw.Draw(im).rounded_rectangle((cx-w/2,y,cx+w/2,y+h),16,fill=CREAM,outline='#a9c7cd',width=2)
 txt(im,s,cx,y+12,size,color,True)
def arrow(im,pts,color=BLUE,width=7,q=1):
 n=max(2,min(len(pts),round(1+(len(pts)-1)*E(q))))
 if q>0:o.p.native.arrow(im,pts[:n],color,width,1)
def row(mode):return next(r for r in ROWS if r['mode']==mode)
def bg():
 im=o.m.BG.copy();ImageDraw.Draw(im).rounded_rectangle((34,179,1886,945),24,fill=CREAM,outline='#a8c5cf',width=2);return im
def fish(d,x,y,s=1,c='#507c8e',phase=0):
 d.ellipse((x-35*s,y-13*s,x+35*s,y+13*s),fill=c)
 wig=math.sin(phase)*5*s
 d.polygon([(x-29*s,y),(x-53*s,y-17*s+wig),(x-53*s,y+17*s+wig)],fill=c)
 d.arc((x-23*s,y-8*s,x+26*s,y+8*s),0,140,fill='#cce4df',width=max(1,round(s*2)))
 d.ellipse((x+22*s,y-5*s,x+27*s,y),fill=CREAM)
def ocean(t,mode):
 im=bg();d=ImageDraw.Draw(im);ab=E((t-row('异常')['start'])/2.2)
 txt(im,'秘鲁近海的食物来源',116,208,60,INK)
 # A conceptual coastal section, not a geographic map or quantitative reconstruction.
 d.rounded_rectangle((78,310,1842,836),18,fill='#d7eaf0')
 d.polygon([(80,690),(580,706),(1050,702),(1510,639),(1695,469),(1840,430),(1840,834),(80,834)],fill='#8bb7c7')
 d.polygon([(1530,834),(1640,648),(1730,395),(1840,360),(1840,834)],fill='#d9c5a2')
 warmedge=[(x,435-65*((x-80)/1680)+120*ab*((x-80)/1680)**2+6*math.sin(x/170+t*.5)) for x in range(80,1765,6)]
 d.polygon([(80,345),(1760,345)]+warmedge[::-1],fill='#f0c09f')
 d.line(warmedge,fill='#fff1d6',width=5,joint='curve')
 d.line([(x,344+3*math.sin(x/87-t)) for x in range(80,1765,4)],fill='#faf5e7',width=4)
 txt(im,'陆地',1770,538,46,INK,True)
 path=o.p.native.v.cubic((1130,737),(1180,680),(1430,620),(1440,360+ab*120),70)
 age=t-row('正常')['start'];q=E(age/.8) if mode!='引入' else E((t-4)/1)
 if q:arrow(im,path,BLUE,round(8-4*ab),q)
 # Nutrient parcels visibly travel with the upward water, slowing and stopping below the surface.
 for i in range(16):
  z=(t*(.20-.13*ab)+i/16)%1;j=min(69,int(z*69));x,y=path[j]
  x+=math.sin(i*2.3)*26;y+=math.cos(i)*16
  d.ellipse((x-6,y-6,x+6,y+6),fill='#f2d889',outline='#a18f63',width=1)
 if age>1.8:
  density=1-.68*ab
  for i in range(35):
   x=380+i*29;y=409+math.sin(i*1.4+t*.35)*29
   r=2.5+4*density;d.ellipse((x-r,y-r,x+r,y+r),fill='#86ae8b')
  for i in range(9):
   x=405+i%4*210+math.sin(t*.6+i)*22-ab*110;y=520+(i//4)*58+math.sin(t+i)*4
   fish(d,x,y,.73,'#527b89',t*5+i)
  pill(im,'营养盐补给减少' if ab>.5 else '营养盐 → 浮游植物 → 食物来源',810,742,52,BLUE)
 if ab>.02:
  pill(im,'厄尔尼诺：上升流受抑制',1450,215,48,ORANGE)
 else:pill(im,'正常状态',1510,215,52,BLUE)
 pill(im,'深层冷水',420,649,52,BLUE)
 if age>.8:pill(im,'上升流',1430,583,50,BLUE)
 for i,s in enumerate(['海水变化','食物来源','渔业响应']):
  if mode=='异常' or (age>i*1.2):
   cx=420+i*540;pill(im,s,cx,854,58,ORANGE if mode=='异常' and i==2 else INK)
   if i:arrow(im,[(cx-333,895),(cx-193,895)],BLUE,5)
 return im
def coral(t):
 im=bg();age=t-row('珊瑚')['start'];d=ImageDraw.Draw(im)
 art=ImageOps.fit(CORAL,(1110,642),Image.Resampling.LANCZOS);im.paste(art,(66,218))
 txt(im,'图五：贾维斯岛珊瑚白化 · NOAA',622,882,39,BLUE,True)
 steps=[('持续热压力',0),('共生藻流失',2.3),('珊瑚白化',4.3)]
 for i,(s,delay) in enumerate(steps):
  q=E((age-delay)/.6)
  if q:
   yy=240+i*155+15*(1-q);pill(im,s,1510,yy,64,ORANGE if i==2 else INK)
   if i:arrow(im,[(1510,yy-55),(1510,yy-13)],BLUE,5)
 if age>5.8:pill(im,'白化 ≠ 死亡',1510,742,58,BLUE)
 if age>4.9:txt(im,'污染也会加重压力',1510,872,45,BLUE,True)
 return im
def tree(d,x,y,q=0,damage=0):
 d.line((x,y,x,y-160),fill='#8f795f' if damage<.5 else '#746b60',width=11)
 green=tuple(round(a*(1-q)+b*q) for a,b in zip((131,169,139),(177,156,111)))
 radius=43*(1-.78*damage)
 for dx,dy in [(-31,-138),(27,-150),(0,-183)]:
  d.line((x,y-110,x+dx,y+dy),fill='#8f795f',width=6)
  d.ellipse((x+dx-radius,y+dy-radius,x+dx+radius,y+dy+radius),fill=green)
def soil(t,mode):
 im=bg();age=t-row('土')['start'];dry=E((t-row('干旱')['start'])/3);burn=E((t-row('泥炭')['start'])/2)
 d=ImageDraw.Draw(im)
 # Keep satellite photography still; dynamic processes are clearly separate conceptual graphics.
 art=ImageOps.fit(SMOKE,(860,635),Image.Resampling.LANCZOS);im.paste(art,(63,222))
 txt(im,'图六：2015年印尼烟霾 · NASA',493,881,39,BLUE,True)
 x0,x1=995,1830
 d.rounded_rectangle((x0,222,x1,855),16,fill='#e5f0ed',outline='#b6c9c5',width=2)
 for x in [1125,1370,1680]:tree(d,x,522,dry,burn)
 d.rectangle((x0+2,523,x1-2,585),fill='#b2a17c')
 # Peat layer with visible organic fragments; no cartoon flames used as the explanatory mechanism.
 d.rectangle((x0+2,585,x1-2,760),fill='#887765');d.rectangle((x0+2,760,x1-2,853),fill='#ad9980')
 for j in range(45):
  x=1020+(j*79)%780;y=611+(j*47)%131;d.line((x,y,x+18,y-4),fill='#b3a388',width=2)
 if dry>.01:
  for i in range(12):
   x=1020+i*65;y=540+math.sin(i)*11;d.line((x,y,x+10,y+12,x+5,y+23),fill='#796f59',width=round(1+2*dry))
 if burn>.01:
  for i in range(5):
   x=1210+i*57;y=667+math.sin(i)*12
   d.ellipse((x-17,y-7,x+24,y+15),fill='#bd875e')
  # Wisps rise from peat to atmosphere, kept inside the section boundary.
  for i in range(9):
   q=(t*.22+i/9)%1;x=1370+math.sin(q*5+i)*60;y=660-q*400
   r=8+q*25;d.ellipse((x-r,y-r,x+r,y+r),fill='#bbc6bd')
 if mode in ('土','干旱'):
  pill(im,'土壤与植被变干',1410,245,55,ORANGE)
  pill(im,'泥炭：富含有机质',1410,775,49,CREAM if False else INK)
 else:
  pill(im,'泥炭燃烧',1400,610,58,CREAM if False else INK)
  pill(im,'释放碳与烟尘',1410,247,54,ORANGE)
 if mode=='干旱':pill(im,'干旱 ＋ 点火、排水等因素',1400,868,45,BLUE)
 if mode=='泥炭':pill(im,'植被受损 → 土壤失去保护',1410,867,44,BLUE)
 return im
def runoff(t):
 im=bg();d=ImageDraw.Draw(im);age=t-row('侵蚀')['start'];q=E(age/2)
 d.rounded_rectangle((75,215,1845,832),16,fill='#e4eff0')
 slope=[(x,474+(x-150)*.14+5*math.sin(x/170)) for x in range(150,1775,5)]
 d.polygon(slope+[(1770,831),(150,831)],fill='#ba9f7d');d.line(slope,fill='#9a886d',width=6)
 for i in range(34):
  x=190+(i*83)%1450;y=255+(t*155+i*29)%205
  if age>1:d.line((x,y,x-11,y+31),fill='#8eafc1',width=3)
 if age>2:
  path=[(x,y-15) for x,y in slope];arrow(im,path,BLUE,9,(age-2)/1.3)
  for i in range(12):
   z=((t-row('侵蚀')['start'])*.15+i/12)%1;idx=int(z*(len(path)-1));x,y=path[idx]
   d.ellipse((x-5,y-3,x+5,y+5),fill='#8c745d')
 for i,(s,delay) in enumerate([('强降雨',.3),('地表径流',2.1),('侵蚀风险',4)]):
  if age>delay:
   cx=420+i*540;pill(im,s,cx,855,60,ORANGE if i==2 else BLUE)
   if i:arrow(im,[(cx-330,896),(cx-193,896)],BLUE,5,(age-delay)/.6)
 txt(im,'失去植被保护的坡面',950,244,64,INK,True)
 return im
def raw(t,r):
 if r['mode'] in ('引入','正常','异常'):return ocean(t,r['mode'])
 if r['mode']=='珊瑚':return coral(t)
 if r['mode']=='侵蚀':return runoff(t)
 return soil(t,r['mode'])
def title(im,art,age):
 q=E(age-1);scale=2.15-1.15*q;cx=960*(1-q)+(16+art.width/2)*q;cy=540*(1-q)+(14+art.height/2)*q
 a=art.resize((round(art.width*scale),round(art.height*scale)),Image.Resampling.LANCZOS);x=round(cx-a.width/2);y=round(cy-a.height/2)
 assert x>=0 and y>=0 and x+a.width<=1920 and y+a.height<=1080
 im.paste(a,(x,y),a)
def render(t):
 global AUDIT
 AUDIT=[];r=next((r for r in ROWS if r['start']<=t<r['end']),ROWS[0] if t<2 else row('土'))
 intro=next((a for a in META['intros'] if a['start']<=t<a['start']+2),None)
 if intro:r=ROWS[0] if intro==META['intros'][0] else row('土')
 im=raw(t,r)
 if r['mode'] in ('珊瑚','侵蚀') and 0<=t-r['start']<.4:
  prior=ROWS[ROWS.index(r)-1];im=Image.blend(raw(prior['end']-.01,prior),im,E((t-r['start'])/.4))
 art=TITLES[1 if r['mode'] in ('土','干旱','泥炭','侵蚀') else 0]
 if intro:title(im,art,t-intro['start'])
 else:im.paste(art,(16,14),art);o.subtitle(im,r['text'])
 return im,dict(t=t,mode=r['mode'],silent_title=bool(intro),labels=AUDIT)
def main():
 times=[.5,1.6,4,10,16,22,27,META['intros'][1]['start']+.5,35,41,47,DURATION-2]
 contact=Image.new('RGB',(1920,3*290),'#e5eeee');d=ImageDraw.Draw(contact)
 for i,t in enumerate(times):
  t=min(t,DURATION-.1);im,_=render(t);im.save(ROOT/'检查'/f'节点_{t:.2f}.png');x=i%4*480;y=i//4*290;contact.paste(im.resize((480,270)),(x,y));d.text((x+8,y+273),f'{t:.2f}s',fill=INK)
 contact.save(ROOT/'检查/设计节点.jpg')
 if '--preview' in sys.argv:return
 dest=PROJECT/'demooo/独立片段/07_生与土/海洋发烧了_第七段_生与土.mp4';dest.parent.mkdir(parents=True,exist_ok=True);pending=dest.with_name('.'+dest.stem+'.pending.mp4')
 proc=subprocess.Popen([o.EXE,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(ROOT/'配音/第七段_晓伊.wav'),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(pending)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 audit=[];count=math.ceil(DURATION*24)
 for i in range(count):
  im,meta=render(i/24);audit.append(meta);proc.stdin.write(im.tobytes())
  if i%240==0:print('Render',i,'/',count,flush=True)
 proc.stdin.close();err=proc.stderr.read();assert proc.wait()==0,err
 test=subprocess.run([o.EXE,'-v','error','-i',str(pending),'-f','null','-'],capture_output=True);assert test.returncode==0 and not test.stderr,test.stderr
 pending.replace(dest)
 (ROOT/'检查/逐帧文字边界.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 report=dict(output=str(dest),seconds=DURATION,frames=count,resolution=[1920,1080],fps=24,decode='PASS',character_present=False,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size)
 (ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
