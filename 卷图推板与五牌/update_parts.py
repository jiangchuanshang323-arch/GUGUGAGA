from pathlib import Path
import sys,math,json,wave,subprocess,importlib.util,hashlib,re
from functools import lru_cache
import numpy as np
from PIL import Image,ImageDraw,ImageOps,ImageChops

ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
for n in ('检查','交付'):(ROOT/n).mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('old37',PROJECT/'环境多米诺_水_v37'/'build_part.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.load_audio();p=m.p;p.load_audio()
EXE=m.EXE;F=m.font;INK=m.INK;CREAM=m.CREAM;BLUE=m.BLUE;ORANGE=m.CORAL
OLD=[dict(r) for r in m.DATA];CUT=OLD[3]['start'];EXIT=OLD[6]['start'];INSERT=3.8;EXITLEN=.7
NEW=[]
for r in OLD:
 q=dict(r);delta=INSERT if r['start']>=CUT else 0
 if r['start']>=EXIT:delta+=EXITLEN
 for k in ('start','speech_end','end'):q[k]+=delta
 NEW.append(q)
STOP=next(r['start'] for r in NEW if r['mode']=='整体')
CARDS=next(r['start'] for r in NEW if r['mode']=='五牌')
EXITSTART=EXIT+INSERT
LARGE_LOG=[]

def txt(im,s,x,y,size,color=INK,center=False):
 f=F(round(size));b=f.getbbox(s);w=b[2]-b[0];h=b[3]-b[1]
 if center:x-=w/2
 assert x>=14 and x+w<=1906 and y>=12 and y+h<=1068,(s,x,y,w,h)
 ImageDraw.Draw(im).text((x-b[0],y-b[1]),s,font=f,fill=color);LARGE_LOG.append((s,round(x),round(y),round(w),round(h)))
def wrap(s,size,width):
 lines=[];line=''
 for ch in s:
  if F(size).getlength(line+ch)>width:lines.append(line);line=ch
  else:line+=ch
 if line:lines.append(line)
 return lines
def label(im,s,box,size=60,color=INK,fill=CREAM):
 x,y,z,b=box;lines=wrap(s,size,z-x-36);lh=size if len(lines)==1 else size*1.12
 assert len(lines)*lh<=b-y-12,(s,box,size,lines)
 ImageDraw.Draw(im).rounded_rectangle(box,18,fill=fill,outline='#a6c4ce',width=2)
 yy=(y+b-len(lines)*lh)/2+3
 for line in lines:txt(im,line,(x+z)/2,yy,size,color,True);yy+=lh
@lru_cache(None)
def header_art(title,subtitle):
 a=p.header(title,subtitle);return a.resize(tuple(round(x*1.5) for x in a.size),Image.Resampling.LANCZOS)
def header(im,title,subtitle=''):
 art=header_art(title,subtitle)
 assert art.width<1890
 im.paste(art,(16,14),art)
def subtitle(im,words):
 d=ImageDraw.Draw(im);d.rectangle((0,912,1920,1080),fill='#244b60')
 lines=wrap(words,69,1770);assert len(lines)<=2,(words,lines)
 yy=922 if len(lines)==2 else 961
 for s in lines:txt(im,s,960,yy,69,'#fffaf0',True);yy+=77

def diagram(el,focus):
 im=Image.new('RGB',(850,280),'#e2f0f1');d=ImageDraw.Draw(im)
 xs=np.arange(850);depth=(72+np.sin(xs/75)*2) if el else (99-65*(xs/849)+np.sin(xs/75)*2)
 d.rectangle((0,155,850,280),fill='#5a9cba')
 edge=[(x,155+float(depth[x])) for x in range(850)]
 d.polygon([(0,155),(850,155)]+edge[::-1],fill='#f6c99f');d.line(edge,fill='#fff2db',width=3)
 cx=490 if el else 165;cloud=p.CLOUD.resize((110,60));im.paste(cloud,(cx-55,60),cloud)
 p.native.arrow(im,[(720,143),(490 if el else 170,143)],ORANGE,7,1 if focus=='信风' else .6)
 p.native.arrow(im,[(cx+8,58),(790,58)],p.native.v.GOLD,5,.7)
 p.native.arrow(im,[(795,75),(795,128)],BLUE,5,.7)
 p.native.arrow(im,[(790,267),(790,240 if el else 190)],BLUE,6,1 if focus=='上涌' else .6)
 for s,x,y,size,color in [('西 · 印尼',135,3,45,INK),('东 · 秘鲁',710,3,45,INK),('西 ← 东',640,90,42,ORANGE),('暖水',180,170,42,ORANGE),('冷水',425,230,42,INK),('温跃层',666,231,37,INK)]:
  f=F(size);b=f.getbbox(s);d.text((x-(b[2]-b[0])/2-b[0],y-b[1]),s,font=f,fill=color)
 return im

def compare(mode):
 im=Image.new('RGB',(1920,1080),CREAM);header(im,'查病因 · 正常与异常对照','从海洋变化，看大气响应')
 for el,x in [(False,70),(True,1000)]:
  label(im,'厄尔尼诺年' if el else '正常年',(x,220,x+850,292),60,ORANGE if el else BLUE)
  im.paste(diagram(el,mode),(x,302))
 active={'信风':0,'暖水':1,'上涌':2,'环流':3,'降雨':4}.get(mode,-1);d=ImageDraw.Draw(im)
 for i,(name,a,b) in enumerate(p.COMPARISONS):
  y=590+i*62
  d.rounded_rectangle((50,y-3,1870,y+59),12,fill='#f9e6ce' if i==active else ('#eaf1ef' if i%2==0 else CREAM))
  txt(im,name,75,y+3,55);txt(im,a,740,y+3,57,BLUE,True);txt(im,b,1480,y+3,57,ORANGE,True)
 return im

MAP=p.MAP.resize((1670,696),Image.Resampling.LANCZOS)
def geo(pt):return 125+(pt[0]-60)*1670/1800,210+(pt[1]-180)*696/750
def map_scene(mode,t,part=4):
 im=Image.new('RGB',(1920,1080),CREAM);im.paste(MAP,(125,210))
 header(im,'互动 · 预测两地降水' if part==4 else '预测揭晓·两侧为何不同','先看气流，再看降水')
 d=ImageDraw.Draw(im)
 for point,name,box,color in [(p.INDO,'印尼 · 西太平洋',(145,390,725,490),BLUE),(p.PERU,'秘鲁 · 东太平洋',(1200,440,1780,540),ORANGE)]:
  x,y=geo(point);d.line(((box[0]+box[2])/2,box[3],x,y-10),fill='#cee2e5',width=3);d.ellipse((x-7,y-7,x+7,y+7),fill=CREAM,outline=color,width=3);label(im,name,box,57,color)
 left='降水：偏少' if part==5 and mode in ('西侧','东侧') else '降水：？'
 right='降水：可能偏多' if part==5 and mode=='东侧' else '降水：？'
 label(im,left,(145,754,725,855),63,BLUE);label(im,right,(1200,754,1780,855),60,ORANGE)
 if part==4 and mode in ('推理','解释'):label(im,'气流升降 → 云雨变化',(550,565,1370,705),63)
 if part==4 and mode=='思考':
  age=t-next(r['start'] for r in p.DATA if r['mode']=='思考');d.ellipse((875,350,1045,520),fill=CREAM);txt(im,str(max(1,3-int(age))),960,380,108,INK,True)
 if part==5:
  if mode=='西侧':label(im,'上升对流减弱 → 偏干',(530,250,1660,355),64,BLUE)
  if mode=='东侧':label(im,'强事件：秘鲁北部沿岸可偏湿',(485,250,1830,365),61,ORANGE)
  if mode in ('西侧','东侧'):
   spec=importlib.util.spec_from_file_location('cloudhelper',PROJECT/'太平洋云雨动效_v38'/'build_demo.py') if False else None
   q=m.ease((t-OLD[2]['start'])/3.8);layer=Image.new('RGBA',im.size)
   cloudhelper.rain_cloud(layer,530,610,t,(1-.7*m.ease((t-OLD[1]['start'])/2.5))*(1-q),.93*(1-.86*q))
   if q:cloudhelper.rain_cloud(layer,530+490*q,610,t,.35+.65*q,q)
   im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
 return im

spec=importlib.util.spec_from_file_location('cloud38',PROJECT/'太平洋云雨动效_v38'/'build_demo.py');cloudhelper=importlib.util.module_from_spec(spec);spec.loader.exec_module(cloudhelper)
SPRITE=m.POSES[3]
def puppet(im,x,y,t,push=False,target=(650,560),speech_t=None,fade=1):
 a=Image.new('RGBA',(520,550));d=ImageDraw.Draw(a)
 # Feet are separately articulated, never replaced by different whole-body poses.
 mix=1 if push else 1-m.ease((t-STOP)/.35)
 step=math.sin(t*11)*mix
 a.alpha_composite(SPRITE.crop((75,405,210,466)),(75,405))
 for box,dx,dy in [((165,460,258,512),-7*step,abs(step)*-11),((260,460,354,512),7*step,-abs(step)*5)]:a.alpha_composite(SPRITE.crop(box),(round(box[0]+dx),round(box[1]+dy)))
 vx=target[0]-(x+250);vy=target[1]-(y+220);ang=math.atan2(vy,vx)
 normal=(340+100*math.cos(ang),307+100*math.sin(ang))
 end=((1-mix)*normal[0]+mix*495,(1-mix)*normal[1]+mix*414)
 left=((1-mix)*151+mix*495,(1-mix)*393+mix*343)
 for start,finish in [((205,303),left),((330,303),end)]:
  pts=p.native.v.cubic(start,(start[0]+12,start[1]+20),(finish[0]-24,finish[1]-12),finish,30)
  for color,width in [('#242b34',45),('#555f6b',36)]:
   d.line(pts,fill=color,width=width,joint='curve')
   for xx,yy in [start,finish]:d.ellipse((xx-width/2,yy-width/2,xx+width/2,yy+width/2),fill=color)
 torso=SPRITE.copy();mask=Image.new('L',torso.size);ImageDraw.Draw(mask).polygon([(205,267),(325,267),(347,285),(352,380),(349,430),(326,458),(293,470),(220,467),(182,449),(164,420),(170,361)],fill=255);torso.putalpha(ImageChops.multiply(torso.getchannel('A'),mask));a.alpha_composite(torso)
 head=SPRITE.crop((70,0,425,282));a.alpha_composite(head,(70,0))
 if speech_t is not None:
  lo=max(0,int((speech_t-.02)*24000));s=m.PCM[lo:lo+1080].astype(np.float32)/32768;rms=float(np.sqrt(np.mean(s*s))) if len(s) else 0
  state=0 if rms<.011 else 1 if rms<.055 else 2 if rms<.13 else 3
  mouth=m.mouth(3,state).resize((43,37));a.alpha_composite(mouth,(244,210))
 # Tiny gaze highlights follow the selected target while preserving the supplied face.
 gaze=max(-2,min(2,(target[0]-x-250)/450))
 for xx in (228,313):d.ellipse((xx+gaze-2,188,xx+gaze+2,192),fill='#e1f7fc')
 a=a.resize((370,391),Image.Resampling.LANCZOS)
 if mix:a=a.rotate(-5*mix,Image.Resampling.BICUBIC,expand=False)
 if fade<1:a.putalpha(a.getchannel('A').point(lambda z:round(z*fade)))
 im.paste(a,(round(x),round(y+abs(step)*2)),a)
 if not push:
  pivot=(x+end[0]*370/520,y+end[1]*391/550);ang=math.atan2(target[1]-pivot[1],target[0]-pivot[0]);tip=(pivot[0]+400*math.cos(ang),pivot[1]+400*math.sin(ang))
  ImageDraw.Draw(im).line((pivot,tip),fill='#61483d',width=8);ImageDraw.Draw(im).line((pivot,tip),fill='#be9165',width=4)

def bubble(im,words,age,span):
 chunks=[];line=''
 for ch in words:
  line+=ch
  if ch in '，。？！' or len(line)>=12:chunks.append(line);line=''
 if line:chunks.append(line)
 total=sum(map(len,chunks));pos=min(total-1,max(0,age/max(.01,span)*total));acc=0;s=chunks[-1]
 for c in chunks:
  acc+=len(c)
  if pos<acc:s=c;break
 lines=wrap(s,69,346);h=len(lines)*80+52;x=24;y=240
 d=ImageDraw.Draw(im);d.rounded_rectangle((x,y,426,y+h),24,fill=CREAM,outline='#92b9c6',width=3);d.polygon([(195,y+h-2),(224,650),(251,y+h-2)],fill=CREAM);d.line([(195,y+h),(224,650),(251,y+h)],fill='#92b9c6',width=3)
 for i,line in enumerate(lines):
  f=F(69);extra=(346-f.getlength(line))/(len(line)-1) if i<len(lines)-1 and len(line)>1 else 0;xx=52;yy=y+25+i*80-f.getbbox(line)[1]
  for ch in line:d.text((xx,yy),ch,font=f,fill=INK);xx+=f.getlength(ch)+extra

def card_art(i,age,highlight=0):
 w,h=235,355;a=Image.new('RGBA',(w,h));d=ImageDraw.Draw(a);color=m.COLORS[i]
 d.rounded_rectangle((2,2,w-3,h-3),20,fill='#fff8e9',outline='#b6d4cd' if highlight else color,width=6 if highlight else 3);d.rounded_rectangle((20,23,w-20,36),6,fill=color)
 q=m.ease(age/.55);cx=118;cy=130
 if i==0:
  m.icon(d,0,cx,cy-19*(1-q),color,1.1)
  r=42*m.ease(age/.65);d.ellipse((cx-r,181-r*.2,cx+r,181+r*.2),outline='#8cc9d4',width=3)
 elif i==1:
  for j in range(3):
   pts=[(58+120*u,105+j*24+7*math.sin(u*math.pi*2+age*2)) for u in np.linspace(0,q,50)];d.line(pts,fill=color,width=5)
 elif i==2:
  m.icon(d,2,cx+9*math.sin(age*5)*q,130,color,1.1);d.ellipse((151,171,151+33*q,191),fill='#80aa8d');d.line((150,191,180,175),fill='#668e75',width=2)
 elif i==3:
  for j in range(3):
   u=m.ease((age-j*.13)/.36);wet=m.ease(age/.8);c=tuple(round(a*(1-.17*wet)+b*.17*wet) for a,b in zip((198,148,126),(93,134,126)));d.rounded_rectangle((62,93+j*29,62+112*u,112+j*29),5,fill=c)
 else:
  pts=[(63,172),(107,94),(136,140),(156,116),(185,172)];progress=q*4;n=min(3,int(progress));part=progress-n;drawn=pts[:n+1]+[(pts[n][0]*(1-part)+pts[n+1][0]*part,pts[n][1]*(1-part)+pts[n+1][1]*part)];d.line(drawn,fill=color,width=6)
  if q>.9:d.polygon(pts,fill=color)
 word=['水','气','生','土','地形'][i];f=F(96 if i<4 else 74);b=f.getbbox(word);d.text(((w-(b[2]-b[0]))/2-b[0],231-b[1]),word,font=f,fill=INK)
 return a

def board_scene(t,mode,row):
 im=m.BG.copy();header(im,'追并发症·环境多米诺','自然环境具有整体性')
 pushing=t<STOP
 elapsed=t-(CUT+1.3);u=m.ease(elapsed/2.5)
 bx=-1430+(450+1430)*u
 if not pushing:bx=450+5*math.sin((t-STOP)*9)*math.exp(-(t-STOP)*5)
 by=220;board=Image.new('RGBA',(1430,750));d=ImageDraw.Draw(board)
 d.rounded_rectangle((5,8,1427,748),22,fill='#3a6267');d.rounded_rectangle((0,0,1420,730),22,fill='#c9ad85');d.rounded_rectangle((13,13,1407,717),14,fill='#315d64');d.line((22,18,1390,18),fill='#ecd8ae',width=4)
 im.paste(board,(round(bx),by),board)
 if pushing:
  puppet(im,bx-350,640,t,True);return im
 txt(im,'自然环境具有整体性',1150,272,77,'#fff6df',True);txt(im,'牵一发而动全身',1150,378,96,'#f3d7a4',True)
 c_age=t-CARDS;selected=max(0,min(4,int(c_age/.7)))
 for i in range(5):
  age=c_age-i*.7
  if age<0:continue
  q=m.ease(age/.45);dy=48*(1-q)-7*math.sin(min(1,age/.6)*math.pi)
  wave=t-(CARDS+3.5)-i*.18;hit=math.sin(math.pi*max(0,min(1,wave/.48))) if 0<wave<.48 else 0
  art=card_art(i,age,hit);art.putalpha(art.getchannel('A').point(lambda z:round(z*q)))
  angle=-4*hit if i==0 else 2.7*math.sin(max(0,wave)*16)*hit
  if angle:
   padded=Image.new('RGBA',(395,515));padded.alpha_composite(art,(80,80));padded=padded.rotate(angle,Image.Resampling.BICUBIC,expand=False,center=(197,430));im.paste(padded,(395+i*270,round(455+dy)),padded)
  else:im.paste(art,(475+i*270,round(535+dy)),art)
  if hit:ImageDraw.Draw(im).arc((460+i*270,860,720+i*270,922),190,350,fill='#a1d2c5',width=4)
 target=(1140,350)
 if c_age>=0:
  j=min(4,int(c_age/.7));q=m.ease((c_age-j*.7)/.30);old=(1140,350) if j==0 else (590+(j-1)*270,580);target=(old[0]*(1-q)+(590+j*270)*q,old[1]*(1-q)+580*q)
  if c_age>=3.25:
   q=m.ease((c_age-3.25)/.35);target=(1670*(1-q)+590*q,580)
 if c_age>=3.5:txt(im,'要素相互联系，影响路径因情境而异',1150,490,36,'#dcebe4',True)
 leaving=t>=EXITSTART
 x=100-500*m.ease((t-EXITSTART)/EXITLEN) if leaving else 100
 source_t=t-INSERT
 puppet(im,x,640,t,target=target,speech_t=source_t if not leaving else None)
 if not leaving:bubble(im,row['text'],t-row['start'],row['speech_end']-row['start'])
 return im

SNAP=None
def roll(t):
 global SNAP
 if SNAP is None:SNAP=map_scene('东侧',CUT-.02,5)
 im=m.BG.copy();header(im,'预测揭晓·两侧为何不同','先看气流，再看降水')
 q=m.ease((t-CUT)/1.3);y=210+920*q;r=12+14*q;x0,x1=125,1795
 if y<906:im.paste(SNAP.crop((x0,round(y),x1,906)),(x0,round(y)))
 if y-r<1080:
  yy=np.arange(max(210,round(y-r)),min(1080,round(y+r)))
  band=Image.new('RGB',(1670,len(yy)),CREAM)
  for j,vv in enumerate(yy):
   u=(vv-y)/r;srcy=max(210,min(905,round(y-r*(math.acos(max(-1,min(1,u)))))))
   line=SNAP.crop((x0,srcy,x1,srcy+1));shade=.62+.36*math.sqrt(max(0,1-u*u));line=Image.blend(Image.new('RGB',line.size,'#eadbb8'),line,.38*shade);band.paste(line,(0,j))
  im.paste(band,(x0,int(yy[0])));d=ImageDraw.Draw(im)
  d.line((x0,y-r,x1,y-r),fill='#f7e7bd',width=3)
  for xx in (x0,x1):
   d.ellipse((xx-7,y-r,xx+7,y+r),fill='#e7d5af',outline='#aa9878',width=2)
   d.ellipse((xx-4,y-r*.65,xx+4,y+r*.65),outline='#ae9d7d',width=1)
 return im

def global_scene(mode):
 im=Image.new('RGB',(1920,1080),CREAM);header(im,'第一张·水','环流变化 → 降水重分配 → 水循环响应')
 im.paste(m.GLOBAL.resize((1670,686),Image.Resampling.LANCZOS),(125,215));txt(im,'典型影响·12月至次年2月',1370,26,48,INK,True)
 d=ImageDraw.Draw(im)
 legends=[('#4d91c6','偏冷'),('#4d9d85','偏湿'),('#a3d0e5','偏冷干'),('#4c7287','偏冷湿'),('#f69c76','偏暖'),('#d6c19a','偏干'),('#b18443','偏暖干'),('#b2d19a','偏暖湿')]
 for i,(color,name) in enumerate(legends):
  x=865+i%4*255;y=92+i//4*58;d.rounded_rectangle((x,y,x+35,y+34),5,fill=color);txt(im,name,x+45,y,39)
 if mode in ('偏干','偏湿'):
  dry=mode=='偏干';label(im,'印尼一带 · 偏干' if dry else '赤道中东太平洋 · 偏暖湿',(530,362,1640,462),60,BLUE if dry else ORANGE)
 return im

def hydro(mode):
 im=m.BG.copy();header(im,'第一张·水','环流变化 → 降水重分配 → 水循环响应');d=ImageDraw.Draw(im);d.rounded_rectangle((50,220,1870,900),25,fill=CREAM)
 txt(im,'降水重分配，怎样传到河流？',960,250,81,INK,True)
 for side,title,items,color in [(0,'持续少雨',['降水减少','雨水补给减少','低流量 / 缺水风险'],BLUE),(1,'强降雨集中',['降水集中','地表径流增加','洪涝风险增加'],ORANGE)]:
  if side and mode=='少雨':continue
  x=100+side*915;label(im,title,(x,365,x+795,465),70,color)
  for j,s in enumerate(items):label(im,s,(x+30,495+j*113,x+765,588+j*113),63,color if j==2 else INK)
 return im

def render4(t):
 row=next((r for r in p.DATA if r['start']<=t<r['end']),p.DATA[0] if t<.25 else p.DATA[-1]);mode=row['mode']
 if row['word_shot']==12:
  if mode=='环流' and t-row['start']>(row['speech_end']-row['start'])*.45:mode='降雨'
  im=compare(mode)
 else:im=map_scene(mode,t,4)
 subtitle(im,row['text']);return im

def render5(t):
 if CUT<=t<CUT+1.3:return roll(t)
 row=next((r for r in NEW if r['start']<=t<r['end']),NEW[0] if t<.2 else NEW[-1])
 if CUT+1.3<=t<STOP:return board_scene(t,'push',row)
 if STOP<=t<EXITSTART+EXITLEN:return board_scene(t,row['mode'],row)
 mode=row['mode'];source=t-INSERT-(EXITLEN if t>=EXITSTART+EXITLEN else 0)
 if mode in ('回扣','西侧','东侧'):im=map_scene(mode,source,5)
 elif mode in ('全球','偏干','偏湿'):im=global_scene(mode)
 else:im=hydro(mode)
 subtitle(im,row['text']);return im

def encode(part):
 global LARGE_LOG
 if part==4:pcm=p.PCM;duration=p.DURATION;render=render4
 else:
  a=round(CUT*24000);b=round(EXIT*24000)
  # Brief paper and soft footstep Foley fill the newly inserted action beats.
  rng=np.random.default_rng(8);sfx=np.zeros(round(INSERT*24000),dtype=np.float32)
  hold=max(0,INSERT-3.8);offset=round(hold*24000)
  n=round(1.3*24000);noise=rng.normal(0,1,n);noise=np.convolve(noise,np.ones(12)/12,'same');sfx[offset:offset+n]=noise*np.sin(np.linspace(0,math.pi,n))*.018
  for base_tm in [1.65,1.98,2.32,2.66,3.0,3.34]:
   tm=base_tm+hold
   k=round(tm*24000);z=np.arange(2400)/24000;sfx[k:k+2400]+=.025*np.sin(z*math.pi*2*105)*np.exp(-z*45)
  pcm=np.concatenate([m.PCM[:a],np.int16(np.clip(sfx,-1,1)*32767),m.PCM[a:b],np.zeros(round(EXITLEN*24000),dtype='<i2'),m.PCM[b:]])
  duration=len(pcm)/24000;render=render5
 audio=ROOT/f'part{part}.wav'
 with wave.open(str(audio),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm.tobytes())
 rows=p.DATA if part==4 else NEW;times=[r['start']+.5 for r in rows]
 if part==5:times += [CUT+.3,CUT+.9,CUT+2.4,STOP-.1,STOP+.3,CARDS+.3,CARDS+2,CARDS+4,EXITSTART+.3]
 contact=Image.new('RGB',(1920,math.ceil(len(times)/4)*290),'#e6efed');dd=ImageDraw.Draw(contact)
 for i,t in enumerate(times):
  if t>=duration:continue
  im=render(t);im.save(ROOT/'检查'/f'part{part}_{i:02d}.png');x=i%4*480;y=i//4*290;contact.paste(im.resize((480,270),Image.Resampling.LANCZOS),(x,y));dd.text((x+5,y+273),f'{t:.2f}s',fill=INK)
 contact.save(ROOT/'检查'/f'part{part}_节点检查.jpg',quality=95)
 if '--preview' in sys.argv:return
 out=ROOT/'交付'/f'part{part}.mp4';cmd=[EXE,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(audio),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE);n=math.ceil(duration*24)
 for i in range(n):
  LARGE_LOG=[];proc.stdin.write(render(i/24).tobytes())
  if i%240==0:print('Part',part,i,'/',n,flush=True)
 proc.stdin.close();err=proc.stderr.read();assert proc.wait()==0,err
 test=subprocess.run([EXE,'-v','error','-i',str(out),'-f','null','-'],capture_output=True);assert test.returncode==0 and not test.stderr,test.stderr
 (ROOT/f'part{part}_验证.json').write_text(json.dumps(dict(output=str(out),seconds=duration,frames=n,decode='PASS',font_scale=1.5,visual_review='待抽帧复核',character_uses_bubble=True,sha256=hashlib.sha256(out.read_bytes()).hexdigest()),ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
 from refine_components import install
 install(sys.modules[__name__])
 encode(int(sys.argv[1]))
