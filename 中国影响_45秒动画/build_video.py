from pathlib import Path
import math,json,sys,io,subprocess,importlib.util,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageChops
R=Path(__file__).resolve().parent;P=R.parent
spec=importlib.util.spec_from_file_location('ocean_shared',P/'多米诺转场_企鹅串讲/build_transitions.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
F=b.F;E=b.E;INK=b.INK;BLUE='#659eaf';ORANGE='#cf936d';CREAM='#fffaf0';W,H,FPS,D=1920,1080,24,45
OUT=P/'demooo/预览/中国影响全屏动画/海洋发烧了_中国影响全屏动画小样.mp4'
G=json.loads((R/'素材/中国轮廓参考.json').read_text(encoding='utf-8'))['features'][0]['geometry']['coordinates']
if (R/'台词与时间轴.json').exists():M=json.loads((R/'台词与时间轴.json').read_text(encoding='utf-8'))
else:
 assert '--preview' in sys.argv,'Generate narration first'
 import ast
 tree=ast.parse((R/'make_audio.py').read_text(encoding='utf-8'))
 entries=ast.literal_eval(next(v.value for v in tree.body if isinstance(v,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='LINES' for k in v.targets)))
 M={'lines':[dict(mode=mode,start=s,end=e,speech_end=e,text=words) for mode,s,e,words in entries]}
PCM=b.read_pcm(R/'配音/中国影响45秒.wav') if (R/'配音/中国影响45秒.wav').exists() else np.zeros(45*24000,dtype='<i2');AUDIT=[]
n=(math.sin(math.radians(25))+math.sin(math.radians(47)))/2
C=math.cos(math.radians(25))**2+2*n*math.sin(math.radians(25))
def albers(lon,lat):
 rho=math.sqrt(C-2*n*math.sin(math.radians(lat)))/n;theta=n*math.radians(lon-105)
 return rho*math.sin(theta),rho*math.cos(theta)
pts=[albers(*v) for poly in G for ring in poly for v in ring if v[1]>=18]
xmin,ymin=np.min(pts,axis=0);xmax,ymax=np.max(pts,axis=0);S=835/(ymax-ymin)
def xy(lon,lat):
 x,y=albers(lon,lat);return 70+(x-xmin)*S,112+(y-ymin)*S
POLYS=[[xy(*v) for v in poly[0]] for poly in G if max(v[1] for v in poly[0])>=18]
MASK=Image.new('L',(W,H));d=ImageDraw.Draw(MASK)
for p in POLYS:d.polygon(p,fill=255)
# Deterministic light paper grain; the geographic geometry stays fixed in every frame.
rng=np.random.default_rng(42);yy,xx=np.mgrid[0:H,0:W];grain=rng.normal(0,.65,(H,W))
wash=Image.fromarray(np.uint8(rng.uniform(82,174,(35,62)))).resize((W,H),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(12))
wash=(np.asarray(wash).astype(float)-128)/17
sea=np.stack([242-18*yy/H+grain,248-7*yy/H+grain,247-5*yy/H+grain],axis=2)
BG=Image.fromarray(np.uint8(np.clip(sea,0,255)))
land=np.stack([247+wash+grain,239+wash*1.5+grain,215+wash*2.4+grain],axis=2)
LAND=Image.fromarray(np.uint8(np.clip(land,0,255)))
shadow=MASK.filter(ImageFilter.GaussianBlur(7));BG.paste('#b5cbd0',(4,6),shadow.point(lambda a:round(a*.24)));BG.paste(LAND,(0,0),MASK)
bd=ImageDraw.Draw(BG)
for p in POLYS:bd.line(p+[p[0]],fill='#799da6',width=3,joint='curve')
for j in range(5):
 path=[(x,175+j*160+8*math.sin(x/180+j)) for x in range(1120,1920,6)]
 bd.line(path,fill='#dfedef',width=2)
# Nanhai inset remains visible below the western mainland, away from the character.
insetbox=(46,731,245,940);inset=Image.new('RGB',(199,209),'#edf5f4');idraw=ImageDraw.Draw(inset)
for poly in G:
 p=[((v[0]-105)/20*191+4,(25-v[1])/23*190+5) for v in poly[0]]
 idraw.polygon(p,fill='#f6efd9');idraw.line(p+[p[0]],fill='#809fa7',width=1)
BG.paste(inset,(46,731));ImageDraw.Draw(BG).rounded_rectangle(insetbox,10,outline='#aac5ca',width=2)
HEADER=b.o.p.header('厄尔尼诺·对中国的影响','降水 / 台风 / 冬季气温')
def text(im,s,x,y,size=52,color=INK,center=False):
 font=F(size);w=font.getlength(s);xx=x-w/2 if center else x
 assert 15<=xx and xx+w<=1905 and 10<=y and y+size<=1067,(s,xx,y,w)
 b.o.txt(im,s,x,y,size,color,center);AUDIT.append(dict(kind='text',text=s,box=[round(xx,1),y,round(xx+w,1),y+size]))
def tag(im,s,x,y,size=48,color=INK):
 width=F(size).getlength(s)+34;h=size+23
 ImageDraw.Draw(im).rounded_rectangle((x-width/2,y,x+width/2,y+h),14,fill=CREAM,outline='#b6ced1',width=1)
 text(im,s,x,y+10,size,color,True)
def composite(im,layer,alpha):
 if alpha<=0:return im
 a=layer.getchannel('A')
 if alpha<.999:a=a.point(lambda v:round(v*max(0,min(1,alpha))))
 im.paste(layer,(0,0),a);return im
def region(kind):
 lay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(lay)
 if kind=='rain':
  points=[xy(lon,30.1+.6*math.sin(lon*.6)) for lon in np.linspace(105,122.5,100)]
  poly=[(x,y-45-6*math.sin(i*.2)) for i,(x,y) in enumerate(points)]+[(x,y+39+6*math.sin(i*.24)) for i,(x,y) in reversed(list(enumerate(points)))]
  d.polygon(poly,fill=(84,165,193,110))
 elif kind=='dry':
  cx,cy=xy(115,38);d.ellipse((cx-90,cy-85,cx+115,cy+74),fill=(217,171,96,105))
 elif kind=='warm':
  for lon,lat,rx,ry in [(111,36,240,180),(121,43,150,220),(105,28,220,150)]:
   cx,cy=xy(lon,lat);d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=(225,164,109,83))
 lay=lay.filter(ImageFilter.GaussianBlur(20));lay.putalpha(ImageChops.multiply(lay.getchannel('A'),MASK));return lay
REGIONS={s:region(s) for s in ['rain','dry','warm']}
# Cache a soft, antialiased cloud sprite. Local scale/position animates, never the map.
def cloud_art():
 a=Image.new('RGBA',(440,250));d=ImageDraw.Draw(a)
 p=[(21,164),(23,143),(36,123),(58,110),(80,108),(84,83),(99,61),(124,53),(147,61),(162,78),(178,48),(204,29),(233,35),(255,56),(265,85),(290,76),(315,82),(334,100),(341,123),(364,131),(385,149),(393,174),(382,193),(361,202),(54,202),(30,191)]
 d.polygon(p,fill='#fffdf3');d.line(p+[p[0]],fill='#93b4bf',width=4,joint='curve');d.line([(73,175),(151,179),(208,175)],fill='#e4edef',width=4)
 return a
CLOUD=cloud_art()
def cloud(im,cx,cy,scale=1,opacity=1):
 a=CLOUD.resize((round(206*scale),round(117*scale)),Image.Resampling.LANCZOS)
 if opacity<1:a.putalpha(a.getchannel('A').point(lambda v:round(v*max(0,opacity))))
 im.paste(a,(round(cx-a.width/2),round(cy-a.height/2)),a)
def arrow(im,path,progress=1,color=BLUE,width=6):
 progress=max(0,min(1,progress));count=round(progress*(len(path)-1))+1
 if count<3:return
 b.o.p.native.arrow(im,path[:count],color,width,1)
def curve(coords):return b.o.p.native.v.cubic(*[xy(*p) for p in coords],100)
WINDS=[curve([(128,18),(126,23),(121,27),(117,30)]),curve([(114,16),(113,22),(109,26),(110,30)])]
INTRO=curve([(139,24),(132,27),(126,31),(120,33)])
def flow(im,path,t,progress,opacity=1):
 if opacity<=0:return
 target=im if opacity>=.999 else Image.new('RGBA',im.size)
 arrow(target,path,progress,'#78afbd',6);d=ImageDraw.Draw(target)
 for j in range(7):
  u=(t*.22+j/7)%1
  if u>progress:continue
  k=round(u*(len(path)-1));x,y=path[k];d.ellipse((x-4,y-4,x+4,y+4),fill='#ecf8f8')
 if target is not im:composite(im,target,opacity)
def current_clause(r,t):
 chunks=[];s=''
 for ch in r['text']:
  s+=ch
  if ch in '。！？' or (ch=='，' and len(s)>=7):chunks.append(s);s=''
 if s:chunks.append(s)
 count=sum(map(len,chunks));pos=min(count-.001,max(0,(t-r['start'])/(r['speech_end']-r['start']))*count);acc=0
 for s in chunks:
  acc+=len(s)
  if pos<acc:return s
 return chunks[-1]
def bubble(im,words):
 x=1148;w=407;size=46;inner=w-42;lines=b.o.wrap(words,size,inner)
 # Prevent punctuation from starting a new line, with a shared baseline for every glyph.
 for j in range(1,len(lines)):
  if lines[j] and lines[j][0] in '，。！？；：、':lines[j]=lines[j-1][-1]+lines[j];lines[j-1]=lines[j-1][:-1]
 if len(lines)>1 and len(lines[-1])<=2:
  joined=lines[-2]+lines[-1];cut=len(joined)//2
  while cut<len(joined)-1 and joined[cut] in '，。！？；：、':cut+=1
  lines[-2:]=[joined[:cut],joined[cut:]]
 h=len(lines)*57+36;y=731-h/2;d=ImageDraw.Draw(im)
 d.rounded_rectangle((x,y,x+w,y+h),20,fill=CREAM,outline='#94b8c4',width=2)
 tip=(1640,735);d.polygon([(x+w-2,y+h*.39),tip,(x+w-2,y+h*.67)],fill=CREAM)
 d.line([(x+w,y+h*.39),tip,(x+w,y+h*.67)],fill='#94b8c4',width=2)
 bases=[]
 for j,line in enumerate(lines):
  base=y+17+j*57-F(size).getbbox('国',anchor='ls')[1];bases.append(base);xx=x+21
  extra=(inner-F(size).getlength(line))/max(1,len(line)-1) if j<len(lines)-1 else 0
  for ch in line:d.text((xx,base),ch,font=F(size),fill=INK,anchor='ls');xx+=F(size).getlength(ch)+extra
 AUDIT.append(dict(kind='bubble',text=words,box=[x,y,x+w,y+h],tip=tip,baseline_anchor='ls',baselines=bases))
SPRITE=Image.open(R/'素材/企鹅_双翅握伞杆.png').convert('RGBA');SW,SH=SPRITE.size
def sprite():
 # Animate the existing sprite's mouth only; no synthetic replacement arms.
 a=SPRITE.resize((369,492),Image.Resampling.LANCZOS);return a
BODY=sprite();MOUTH=SPRITE.crop((552,788,625,852)).resize((25,22),Image.Resampling.LANCZOS)
def umbrella_art(q,t):
 a=Image.new('RGBA',(480,200));d=ImageDraw.Draw(a);cx=240;top=20;edge=124
 # The shaft is physically held in the source sprite. Open canopy pivots around its top.
 q=max(.025,min(1,q));rx=225*q;depth=70+28*q
 outline=[(cx-rx,edge)]
 for z in np.linspace(-1,1,100):outline.append((cx+rx*z,edge-depth*math.sqrt(max(0,1-z*z))))
 for i in range(5,-1,-1):
  for z in np.linspace(0,1,10):
   x=cx-rx+(i+z)*2*rx/6;y=edge-7*math.sin(z*math.pi)*q;outline.append((x,y))
 d.polygon(outline,fill='#a5cfdd');d.line(outline+[outline[0]],fill='#628f9f',width=3,joint='curve')
 for j,z in enumerate([-.66,-.33,0,.33,.66]):
  path=[(cx+(rx*z)*u,edge-depth*(1-u)+u*edge*.0-15*math.sin(u*math.pi)) for u in np.linspace(0,1,35)]
  # Ribs end on the same hem, with no overshoot.
  path=[(cx+rx*z*u,edge-depth+(depth-6*math.sin((j+1)/6*math.pi))*u) for u in np.linspace(0,1,35)]
  d.line(path,fill='#7cabbc',width=2)
 d.line((cx,edge-depth-8,cx,edge-depth+1),fill='#7295a0',width=4)
 return a
def penguin(im,t):
 if not 3<=t<20:return False
 enter=E((t-3)/.65);leave=E((t-19.30)/.70)
 px=1520+410*(1-enter)+410*leave;py=446+math.sin(t*2)*1.3
 walking=t<3.65 or t>=19.30
 if walking:py-=abs(math.sin(t*16))*4
 a=BODY.copy();k=round(t*24000);v=PCM[k:k+720].astype(float)/32768;rms=float(np.sqrt(np.mean(v*v))) if len(v) else 0
 if walking:
  for j,box in enumerate([(116,449,183,484),(209,449,270,484)]):
   foot=a.crop(box);a.paste((0,0,0,0),box);dy=round(max(0,math.sin(t*16+j*math.pi))*5);a.alpha_composite(foot,(box[0],box[1]-dy))
 # Exact source-space facial landmarks, transformed together with the sprite.
 mx,my=round(587*369/SW),round(820*492/SH)
 ad=ImageDraw.Draw(a);ad.ellipse((mx-15,my-16,mx+16,my+17),fill=(255,208,187,255))
 if rms<.009:ad.arc((mx-9,my-5,mx+9,my+5),0,180,fill='#78484b',width=2)
 else:
  h=9 if rms<.05 else 15 if rms<.12 else 20;mo=MOUTH.resize((24,h),Image.Resampling.LANCZOS);a.alpha_composite(mo,(mx-12,my-h//2))
 im.paste(a,(round(px),round(py)),a)
 q=E((t-3.72)/.65)*(1-E((t-19.08)/.24));canopy=umbrella_art(q,t)
 # Top of held shaft is (350,250) in the 1086x1448 source. Canopy attaches there.
 ux=px+350*369/SW;uy=py+250*492/SH
 im.paste(canopy,(round(ux-240),round(uy-88)),canopy)
 if t>4.15 and t<18.95:
  d=ImageDraw.Draw(im)
  for j in range(15):
   x=ux-205+j*29;y=uy-210+((t*125+j*23)%115);d.line((x,y,x-5,y+13),fill='#77acc0',width=3)
  for side in [-1,1]:
   for j in range(3):
    y=uy+40+((t*95+j*29)%80);x=ux+side*(220+4*math.sin(t*3+j));d.ellipse((x-2,y,x+2,y+6),fill='#82b6c7')
 if not walking:AUDIT.append(dict(kind='character',box=[px,py,px+369,py+492],umbrella_attached=True))
 else:AUDIT.append(dict(kind='character',walking=True,visible=px<1919))
 return px<1919
def rain_scene(im,t):
 a=E((t-5.5)/1.2)*(1-E((t-19.1)/.9));composite(im,REGIONS['rain'],a)
 for k,path in enumerate(WINDS):flow(im,path,t,E((t-4.4-k*.3)/2.4),a)
 for i,lon in enumerate([109,115,120.5]):
  cx,cy=xy(lon,30.5);cy+=3*math.sin(t*.8+i)
  cloud(im,cx,cy-55,.70,a)
  if a>.01:
   d=ImageDraw.Draw(im)
   for j in range(6):
    x=cx-43+j*17;y=cy+((t*61+j*17+i*11)%52);d.line((x,y,x-5,y+12),fill='#79abc0',width=3)
   for j in range(2):
    rr=4+((t*15+j*10)%19);d.arc((cx-22-rr,cy+64-rr/4,cx-22+rr,cy+64+rr/4),0,330,fill='#8bbdce',width=2)
 if t>=6.1 and t<19.1:
  lx,ly=xy(115.5,33.7);tag(im,'长江中下游',lx,ly-85,48,BLUE)
 if 7.2<t<10.9:tag(im,'降水偏多的可能增加',760,815,46,BLUE)
 dry=E((t-11)/.8)*(1-E((t-14.0)/.8));composite(im,REGIONS['dry'],dry)
 if 11.2<t<14.1:
  cx,cy=xy(115,38);d=ImageDraw.Draw(im);d.arc((cx-35,cy-28,cx+35,cy+28),0,180,fill=ORANGE,width=4)
  d.line((cx-31,cy+2,cx+31,cy+2),fill='#b7ab89',width=3);d.line((cx-25,cy+17,cx+25,cy+17),fill='#b7ab89',width=3)
  tag(im,'部分地区可能偏旱',675,250,43,ORANGE)
 if 14.3<t<19.12:
  tag(im,'1998年·长江洪水',720,788,48,BLUE)
  # One gentle regional pulse rather than a large moving emphasis circle.
  composite(im,REGIONS['rain'],.18+.12*math.sin((t-14.3)*1.4)**2)
def cyclone(im,cx,cy,t,scale=1,alpha=1):
 a=Image.new('RGBA',(430,430));d=ImageDraw.Draw(a);rot=t*.60
 # Broad, tapering spiral cloud bands, animated counterclockwise in screen coordinates.
 for j in range(3):
  points=[]
  for z in np.linspace(0,1,100):
   rr=22+155*z;theta=j*2*math.pi/3-rot+4.5*z;points.append((215+rr*math.cos(theta),215+rr*.81*math.sin(theta)))
  for extra,fill in [(6,(195,222,230,215)),(0,(255,254,247,250))]:
   left=[];right=[]
   for k,(x,y) in enumerate(points):
    p0=points[max(0,k-1)];p1=points[min(len(points)-1,k+1)];dx=p1[0]-p0[0];dy=p1[1]-p0[1];length=math.hypot(dx,dy)
    radius=(34-26*k/(len(points)-1)+extra)/2;nx=-dy/length;ny=dx/length
    left.append((x+nx*radius,y+ny*radius));right.append((x-nx*radius,y-ny*radius))
   d.polygon(left+right[::-1],fill=fill)
  d.line(points,fill=(160,197,210,150),width=2,joint='curve')
 d.ellipse((196,198,234,232),fill='#d8edf1',outline='#81afc2',width=2)
 a=a.resize((round(430*scale),round(430*scale)),Image.Resampling.LANCZOS);a.putalpha(a.getchannel('A').point(lambda v:round(v*alpha)))
 im.paste(a,(round(cx-a.width/2),round(cy-a.height/2)),a)
def typhoon_scene(im,t):
 q=E((t-20.15)/.75)*(1-E((t-30.4)/.6));d=ImageDraw.Draw(im)
 u=E((t-21.2)/3);v=E((t-25)/4)
 start=(1280,540);east=(1560,701);end=(1430,482)
 if t<25:
  arrow(im,b.o.p.native.v.cubic(start,(start[0]+60,start[1]+5),(east[0]-50,east[1]-10),east,75),u,'#a1bac5',4)
 else:
  path=b.o.p.native.v.cubic(east,(east[0]+100,east[1]-85),(end[0]+100,end[1]+90),end,90)
  arrow(im,path,v,'#8eafbd',5)
 if t<25:
  cx=start[0]+(east[0]-start[0])*u;cy=start[1]+(east[1]-start[1])*u
 else:
  cx,cy=path[round(v*(len(path)-1))]
 cyclone(im,cx,cy,t,.66+.30*E((t-24.9)/2),q)
 if 20.5<t<24.85:tag(im,'生成位置偏东、偏南',1390,223,49,BLUE)
 if 25<t<27.6:tag(im,'部分台风有更长发展时间',1320,230,46,BLUE)
 if 27.65<t<30.65:
  tag(im,'风险：强度与路径',1390,235,51,INK)
  # No fabricated landfall track; the illustrated track stays over ocean.
 text(im,'西北太平洋',1390,860,43,'#83a9b7',True)
def thermometer(im,x,y,t):
 d=ImageDraw.Draw(im);d.rounded_rectangle((x-19,y-105,x+19,y+90),20,fill=CREAM,outline='#8ba7b0',width=3)
 d.ellipse((x-34,y+66,x+34,y+134),fill=CREAM,outline='#8ba7b0',width=3)
 h=80+58*E((t-31.4)/3);d.rounded_rectangle((x-8,y+81-h,x+8,y+95),8,fill='#d69c74');d.ellipse((x-23,y+77,x+23,y+123),fill='#d69c74')
 for j in range(5):d.line((x+28,y+58-j*29,x+42,y+58-j*29),fill='#8ba7b0',width=2)
def snow(im,x,y,r=8):
 d=ImageDraw.Draw(im)
 for a in [0,math.pi/3,2*math.pi/3]:d.line((x-r*math.cos(a),y-r*math.sin(a),x+r*math.cos(a),y+r*math.sin(a)),fill='#7eafc7',width=2)
COLD=curve([(117,48),(115,44),(113,39),(112,33)])
def winter_scene(im,t):
 q=E((t-31)/1)*(1-E((t-40.4)/.6));composite(im,REGIONS['warm'],q);thermometer(im,1420,520,t)
 if 31.2<t<35.65:tag(im,'冬季偏暖的概率增加',1390,225,49,ORANGE)
 if t>35.6:
  z=E((t-35.6)/2.6);arrow(im,COLD,z,'#86b3cb',14)
  # Cooling remains local and temporary, on top of the seasonal tendency.
  lay=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(lay)
  k=min(len(COLD)-1,round(z*(len(COLD)-1)));cx,cy=COLD[k]
  ld.ellipse((cx-130,cy-115,cx+130,cy+115),fill=(121,175,203,70));lay=lay.filter(ImageFilter.GaussianBlur(26));lay.putalpha(ImageChops.multiply(lay.getchannel('A'),MASK));composite(im,lay,E((t-35.6)/.7)*q)
  for i in range(9):
   u=(t*.12+i/9)%max(.01,z)
   if u>z:continue
   sx,sy=COLD[min(len(COLD)-1,round(u*(len(COLD)-1)))];snow(im,sx+35*math.sin(i*3.5),sy+18*math.sin(t*1.5+i),6)
  tag(im,'暖冬仍需防范寒潮',1390,225,49,BLUE)
def summary(im,t):
 # The same map stays present: three small symbols recap, rather than a new slide.
 z=t-41;xs=[1265,1490,1715]
 for j,x in enumerate(xs):
  q=E((z-j*.35)/.45)
  if q<=0:continue
  if j==0:
   cloud(im,x,410,.7,q);d=ImageDraw.Draw(im)
   for k in range(4):d.line((x-35+k*23,450,x-40+k*23,470),fill=BLUE,width=3)
  elif j==1:cyclone(im,x,410,t,.30,q)
  else:thermometer(im,x,410,34)
  text(im,['降水','台风','气温'][j],x,570,46,INK,True)
 tag(im,'关注预报，科学应对',1490,708,49,INK)
def frame(t):
 global AUDIT
 AUDIT=[];im=BG.copy()
 if t<3.4:flow(im,INTRO,t,E((t-.25)/2),1)
 if 3.8<=t<20:
  original=im.copy();rain_scene(im,t);fade=E((t-3.8)/.4)*(1-E((t-19.1)/.9));im=Image.blend(original,im,fade)
 if 20<=t<31:
  original=im.copy();typhoon_scene(im,t);fade=E((t-20)/.5)*(1-E((t-30.5)/.5));im=Image.blend(original,im,fade)
 if 31<=t<41:
  original=im.copy();winter_scene(im,t);fade=E((t-31)/.5)*(1-E((t-40.5)/.5));im=Image.blend(original,im,fade)
 if t>=41:summary(im,t)
 character=penguin(im,t)
 r=next((r for r in M['lines'] if r['start']<=t<r['speech_end']),None)
 if r:
  words=current_clause(r,t)
  if character and 3.65<=t<19.3:bubble(im,words)
  elif not character:
   b.o.subtitle(im,words);AUDIT.append(dict(kind='subtitle',text=words,box=[0,958,1920,1080]))
 im.paste(HEADER,(16,14),HEADER)
 text(im,'南海诸岛',145,895,26,INK,True)
 period='次年夏季·部分事件' if t<20 else '厄尔尼诺发展期' if t<31 else '冬季·整体倾向' if t<41 else '影响因事件与地区而异'
 tag(im,period,1510,45,38,INK)
 return im
def previews():
 times=[1.5,4.4,7.8,12,15.3,17.5,20.7,23,26.4,29.3,31.6,33.8,36.2,37.8,40.3,43.7]
 sheet=Image.new('RGB',(1920,1240),'#e6eef0')
 for j,t in enumerate(times):
  im=frame(t);im.save(R/'检查'/f'设计_{t:.2f}.png');sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),((j%4)*480,(j//4)*310));ImageDraw.Draw(sheet).text(((j%4)*480+10,(j//4)*310+275),f'{t:.2f}s',font=F(24),fill=INK)
 sheet.save(R/'检查/设计总览.jpg');print('preview ready',flush=True)
def main():
 OUT.parent.mkdir(parents=True,exist_ok=True);tmp=OUT.with_name('.中国影响45秒.pending.mp4');log=(R/'编码日志.txt').open('wb')
 proc=subprocess.Popen([b.FF,'-v','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',str(FPS),'-i','-','-i',str(R/'配音/中国影响45秒.wav'),'-t','45','-c:v','libx264','-profile:v','baseline','-level:v','4.0','-g','24','-bf','0','-refs','1','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-ac','2','-b:a','128k','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE,stderr=log)
 audits=[]
 for i in range(FPS*D):
  im=frame(i/FPS);proc.stdin.write(im.convert('RGB').tobytes());audits.append(dict(frame=i,t=i/FPS,objects=AUDIT))
  if i%120==0:print('frames',i,'/',FPS*D,flush=True)
 proc.stdin.close();assert proc.wait()==0;log.close();b.manager.decode(tmp)
 (R/'检查/逐帧对象与文字.json').write_text(json.dumps(audits,ensure_ascii=False),encoding='utf-8')
 # Promotion happens only after all frames have been rendered and decoded successfully.
 assert abs(b.manager.info(tmp)['seconds']-45)<.03
 tmp.replace(OUT);finalize()
def finalize():
 info=b.manager.info(OUT)
 report=dict(**info,decode='PASS',resolution='1920x1080',fps=FPS,frames=FPS*D,expected_duration=45,shihezi=False,independent=True)
 assert abs(info['seconds']-45)<.03,info
 (R/'检查/验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 sheet=Image.new('RGB',(1920,1240),'#e6eef0')
 times=[1.5,4.4,7.8,12,15.3,17.5,20.7,23,26.4,29.3,31.6,33.8,36.2,37.8,40.3,43.7]
 for j,t in enumerate(times):
  raw=subprocess.run([b.FF,'-v','error','-ss',str(t),'-i',str(OUT),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True,check=True).stdout
  im=Image.open(io.BytesIO(raw));im.save(R/'检查'/f'编码_{t:.2f}.png');sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),((j%4)*480,(j//4)*310));ImageDraw.Draw(sheet).text(((j%4)*480+10,(j//4)*310+275),f'{t:.2f}s',font=F(24),fill=INK)
 sheet.save(R/'检查/编码总览.jpg')
 data=json.loads(b.manager.MANIFEST.read_text(encoding='utf-8'));data.setdefault('previews',{})['中国影响全屏动画']=dict(path=str(OUT.relative_to(b.manager.ROOT)),**info,decode='PASS');b.manager.write_manifest(data)
 import shutil
 shutil.copy2(OUT,OUT.with_name('china_impact_playback.mp4'))
 print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':
 from refine_scene import install
 install(sys.modules[__name__])
 if '--preview' in sys.argv:previews()
 elif '--verify' in sys.argv:finalize()
 else:main()
