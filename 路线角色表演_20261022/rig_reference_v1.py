from pathlib import Path
import math, json, subprocess, hashlib, sys, io, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
P=Path(__file__).resolve().parent.parent; R=P/'路线角色表演_20261022'; Q=R/'检查'; A=R/'素材'
OUT=P/'demooo/预览/四步会诊路线全程'; OUT.mkdir(parents=True,exist_ok=True)
FF=P/'ocean_animation_demo_20261011/runtime/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
BG=Image.open(P/'修改方案_三画面/四步会诊路线_独立主图.png').convert('RGBA')
SRC=Image.open(P/'企鹅小老师_教学动作素材_20261012/独立动作PNG/15_走位后站稳.png').convert('RGBA')
W,H=1920,1080; FPS=24; N=800; SCALE=368.671875/493
INK='#282c35'; FIN='#444955'; EDGE='#22262e'; PAPER='#fff7e7'; BLUE='#407f91'
def E(u):
 u=max(0.,min(1.,u)); return u*u*(3-2*u)
def lerp(a,b,q):return np.array(a,float)*(1-q)+np.array(b,float)*q
def keys(t,ls):
 if t<=ls[0][0]:return np.array(ls[0][1],float)
 for (a,v),(b,w) in zip(ls,ls[1:]):
  if t<=b:return lerp(v,w,E((t-a)/(b-a)))
 return np.array(ls[-1][1],float)
def part(points):
 mask=Image.new('L',SRC.size); ImageDraw.Draw(mask).polygon(points,fill=255)
 a=SRC.copy();a.putalpha(Image.fromarray(np.minimum(np.array(mask),np.array(SRC.getchannel('A')))));return a
HEAD=part([(65,0),(450,0),(450,279),(318,279),(310,253),(286,259),(263,270),(239,262),(211,252),(203,279),(65,284)])
arr=np.array(SRC); red=((arr[:,:,0]>arr[:,:,1]*1.35)&(arr[:,:,0]>arr[:,:,2]*1.25)&(np.indices(arr.shape[:2])[0]>248)&(np.indices(arr.shape[:2])[0]<314)&(np.indices(arr.shape[:2])[1]>207)&(np.indices(arr.shape[:2])[1]<319))
m=Image.fromarray((red*255).astype('uint8')).filter(ImageFilter.MaxFilter(7));BOW=SRC.copy();BOW.putalpha(Image.fromarray(np.minimum(np.array(m),arr[:,:,3])))
FEET=[part([(140,453),(257,453),(257,512),(140,512)]),part([(263,453),(382,453),(382,512),(263,512)])]
TAIL=part([(313,428),(351,422),(380,445),(416,446),(390,465),(337,469),(312,455)])
BODY=Image.new('RGBA',(512,512));d=ImageDraw.Draw(BODY)
# Same costume silhouette, clean shoulder sockets for independently articulated fins.
d.polygon([(213,267),(309,267),(329,298),(343,340),(355,412),(349,443),(324,460),(207,462),(176,445),(166,417),(179,338),(192,296)],fill=FIN,outline=EDGE,width=5)
d.ellipse((190,280,334,452),fill='#fcfcf9',outline=EDGE,width=3)
d.pieslice((190,322,334,453),0,180,fill='#bfc0cb')
d.arc((190,280,334,452),0,180,fill=EDGE,width=3)
for name,im in [('头部',HEAD),('领结',BOW),('身体',BODY),('尾部',TAIL),('左脚',FEET[0]),('右脚',FEET[1])]:im.save(A/(name+'.png'))
CACHE={}
def face(gaze=(0,0),blink=1,mood='smile'):
 gx,gy=[round(float(v)) for v in gaze]; blink=round(float(blink)*10)/10
 key=(gx,gy,blink,mood)
 if key in CACHE:return CACHE[key]
 a=HEAD.copy()
 for poly,cx in [([(186,181),(232,181),(236,191),(231,209),(215,215),(191,207)],213), ([(282,181),(328,181),(336,191),(332,208),(308,215),(286,209)],307)]:
  mask=Image.new('L',(512,512));ImageDraw.Draw(mask).polygon(poly,fill=255)
  layer=Image.new('RGBA',(512,512),'#ffdfc7')
  if blink>.15:
   patch=SRC.crop((cx-29,176,cx+30,218));hh=max(2,round(42*blink));patch=patch.resize((59,hh),Image.Resampling.BICUBIC)
   layer.alpha_composite(patch,(cx-29+gx,197-hh//2+gy))
  dd=ImageDraw.Draw(layer)
  if blink<.25:dd.arc((cx-25,188,cx+23,204),0,180,fill='#453c37',width=3)
  layer.putalpha(mask);a.alpha_composite(layer)
 # Reconstruct just the original mouth, never cover the glasses or nose.
 region=(242,224,289,249);skin=Image.new('RGBA',(47,25));sa=np.asarray(skin).copy()
 for yy in range(25):
  l=np.array(SRC.getpixel((241,224+yy)),float);r=np.array(SRC.getpixel((290,224+yy)),float)
  for xx in range(47):sa[yy,xx]=l*(1-xx/46)+r*xx/46
 skin=Image.fromarray(sa);mask=Image.new('L',(47,25));ImageDraw.Draw(mask).ellipse((0,0,46,24),fill=255);skin.putalpha(mask.filter(ImageFilter.GaussianBlur(1)));a.alpha_composite(skin,(242,224))
 dd=ImageDraw.Draw(a)
 if mood=='surprise':dd.ellipse((258,230,271,246),fill='#9a4e50',outline='#703c3b',width=2)
 elif mood in ('think','worry'):dd.arc((251,232,278,245),185,350,fill='#713e3b',width=2)
 else:dd.arc((250,226,279,241),5,170,fill='#75413e',width=2)
 if mood=='worry':
  dd.line((192,163,228,169),fill='#51443d',width=3);dd.line((287,169,322,163),fill='#51443d',width=3)
 CACHE[key]=a
 return a

def stamp(dst,src,pivot,xy,ang=0,scale=SCALE):
 bb=src.getbbox()
 if not bb:return
 a=src.crop(bb);p=np.array(pivot)-bb[:2];th=math.radians(ang);c=math.cos(th);s=math.sin(th)
 mat=scale*np.array([[c,-s],[s,c]])
 corners=np.array([[0,0],[a.width,0],[a.width,a.height],[0,a.height]])
 pts=(corners-p)@mat.T+xy;lo=np.floor(pts.min(0)-2).astype(int);hi=np.ceil(pts.max(0)+2).astype(int)
 inv=np.linalg.inv(mat);off=p+inv@(lo-np.array(xy));sz=tuple((hi-lo).tolist())
 tile=a.transform(sz,Image.Transform.AFFINE,tuple([*inv[0],off[0],*inv[1],off[1]]),Image.Resampling.BICUBIC)
 dst.alpha_composite(tile,tuple(lo))
def line(dst,pts,fill,width=3):ImageDraw.Draw(dst).line([tuple(map(float,p)) for p in pts],fill=fill,width=width,joint='curve')
def fin(dst,a,b):
 a=np.array(a,float);b=np.array(b,float);v=b-a;ln=np.linalg.norm(v);n=np.array([-v[1],v[0]])/max(ln,1);mid=a+v*.53+n*4
 points=[]
 for i in range(16):
  u=i/15;center=a*(1-u)**2+mid*2*u*(1-u)+b*u*u;wide=13*(1-u)+7*u+2*math.sin(math.pi*u);points.append(tuple(center+n*wide))
 for i in range(15,-1,-1):
  u=i/15;center=a*(1-u)**2+mid*2*u*(1-u)+b*u*u;wide=13*(1-u)+7*u+2*math.sin(math.pi*u);points.append(tuple(center-n*wide))
 dd=ImageDraw.Draw(dst);dd.polygon(points,fill=FIN);dd.line(points+[points[0]],fill=EDGE,width=3,joint='curve');line(dst,[a+n*7,(a+b)/2+n*10], '#707482',2)
def grip(dst,p):
 x,y=p;ImageDraw.Draw(dst).ellipse((x-5,y-5,x+5,y+5),fill=FIN)

class Rig:
 def __init__(self,x,y,phase=0,walk=0,lean=0,tilt=0,gaze=(0,0),mood='smile',headup=0,t=0):
  self.xy=np.array([x,y]);self.pel=np.array([x,y-77-2*math.cos(phase*2)*walk]);self.angle=lean;self.phase=phase;self.walk=walk
  th=math.radians(lean);self.mat=SCALE*np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]])
  self.head=self.B((256,270))+np.array([0,-headup]);self.tilt=lean*.45+tilt
  self.gaze=gaze;self.mood=mood;self.t=t
  self.shoulders=[self.B((188,298)),self.B((325,298))]
  self.hands=[self.B((164-12*math.sin(phase)*walk,410)),self.B((350+12*math.sin(phase)*walk,410))]
 def B(self,p):return self.pel+self.mat@(np.array(p)-[256,405])
 def front(self,im):
  stamp(im,TAIL,(256,405),self.pel,self.angle+2*math.sin(self.t*3))
  for j,piv in enumerate([(225,470),(300,470)]):
   cyc=self.phase+j*math.pi;lift=max(0,math.sin(cyc))*13*self.walk;swing=math.cos(cyc)*8*self.walk
   ankle=self.B(piv)+[swing,-lift];hip=self.B((piv[0],449));line(im,[hip,ankle],FIN,20)
   stamp(im,FEET[j],piv,ankle,self.angle+8*math.sin(cyc)*self.walk)
  stamp(im,BODY,(256,405),self.pel,self.angle)
  blink=1-E((self.t%3.65-3.32)/.075)*(1-E((self.t%3.65-3.43)/.10))
  stamp(im,face(self.gaze,blink,self.mood),(256,270),self.head,self.tilt)
  stamp(im,BOW,(263,282),self.B((263,282)),self.angle+4*math.sin(self.phase-.6)*self.walk+math.sin(self.t*3))
 def arms(self,im,hands=None):
  hands=hands or self.hands
  for a,b in zip(self.shoulders,hands):fin(im,a,b)
  return hands

def thermometer(im,p,ang=0):
 a=Image.new('RGBA',(60,160));dd=ImageDraw.Draw(a)
 dd.rounded_rectangle((23,15,36,126),6,fill='#e8f5ee',outline=BLUE,width=3);dd.ellipse((16,113,43,142),fill='#e67752',outline=BLUE,width=3);dd.line((29,65,29,125),fill='#df694b',width=5)
 for yy in range(32,112,12):dd.line((34,yy,42,yy),fill=BLUE,width=2)
 stamp(im,a,(29,68),p,ang,.65)
def notebook(im,p,angle=0,closed=False):
 a=Image.new('RGBA',(110,115));dd=ImageDraw.Draw(a);dd.rounded_rectangle((9,4,101,108),7,fill='#68929b',outline=INK,width=3)
 if not closed:
  dd.rounded_rectangle((18,9,96,102),3,fill=PAPER);dd.line((24,17,24,94),fill='#a0b1ad',width=2)
  for yy in [31,49,67,85]:dd.line((34,yy,85,yy),fill='#95aaa8',width=2)
 for yy in range(17,101,16):dd.ellipse((6,yy,20,yy+5),fill='#dde2d6',outline=INK,width=1)
 stamp(im,a,(54,64),p,angle,.76)
def pencil(im,p,target=None):
 p=np.array(p);v=np.array([27,-35]) if target is None else np.array(target)-p;v=v/max(1,np.linalg.norm(v));line(im,[p-v*16,p+v*25],'#b98243',5);line(im,[p+v*25,p+v*30],INK,3)
def magnifier(im,p,ang=0,t=0):
 # Lens moves with its handle. The wave inside the lens is a genuine crop enlargement.
 rad=31;th=math.radians(ang);v=np.array([math.sin(th),-math.cos(th)]);c=np.array(p)+v*51
 crop=BG.crop((790,338,840,388)).resize((rad*2,rad*2),Image.Resampling.BICUBIC);mask=Image.new('L',crop.size);ImageDraw.Draw(mask).ellipse((1,1,61,61),fill=210);crop.putalpha(mask);im.alpha_composite(crop,(round(c[0]-rad),round(c[1]-rad)))
 dd=ImageDraw.Draw(im);dd.ellipse((c[0]-rad-3,c[1]-rad-3,c[0]+rad+3,c[1]+rad+3),outline='#b58a4c',width=6);dd.arc((c[0]-rad+6,c[1]-rad+6,c[0]+rad-5,c[1]+rad-5),210,280,fill='#fff8df',width=3)
 line(im,[np.array(p)-v*15,c-v*32],'#93653e',10);line(im,[np.array(p)-v*13,c-v*34],'#d4b075',4)
def clipboard(im,p,angle=0,checks=0,closed=False):
 a=Image.new('RGBA',(140,154));dd=ImageDraw.Draw(a);dd.rounded_rectangle((8,8,130,149),8,fill='#bd9670',outline=INK,width=3)
 if closed<1:
  dd.rectangle((16,17,122,139),fill=PAPER);dd.rounded_rectangle((46,2,93,27),5,fill='#8aafb4',outline=INK,width=2)
  for j in range(3):
   y=49+j*29;dd.rectangle((27,y,39,y+11),outline=BLUE,width=2);dd.line((48,y+5,108,y+5),fill='#929f96',width=2)
   q=E(checks-j)
   if q:
    pts=[(26,y+4),(32,y+10),(42,y-3)];a0=lerp(pts[0],pts[1],min(1,q*2));dd.line([pts[0],tuple(a0)],fill='#3e8d79',width=3)
    if q>.5:dd.line([pts[1],tuple(lerp(pts[1],pts[2],q*2-1))],fill='#3e8d79',width=3)
 if closed>0:
  cover=int(106*closed);dd.rectangle((122-cover,17,122,139),fill='#bd9670');dd.line((122-cover,17,122-cover,139),fill='#987755',width=2)
 stamp(im,a,(70,86),p,angle,.79)
def doctorhat(im,p,ang=0):
 a=Image.new('RGBA',(134,74));dd=ImageDraw.Draw(a);dd.polygon([(12,60),(19,17),(40,9),(95,9),(115,18),(122,60)],fill='#fffbed',outline=BLUE,width=3);dd.line((16,51,118,51),fill='#94c3cb',width=3);dd.rectangle((61,19,73,44),fill='#ce7d65');dd.rectangle((54,26,80,37),fill='#ce7d65');stamp(im,a,(67,61),p,ang,.85)
def bulb(im,p,q):
 if q<=0:return
 layer=Image.new('RGBA',im.size);dd=ImageDraw.Draw(layer);x,y=p;dd.ellipse((x-16,y-20,x+16,y+12),fill='#f5d58c',outline='#af8d4f',width=2);dd.rounded_rectangle((x-8,y+12,x+8,y+23),3,fill='#80a4a7',outline=BLUE,width=2)
 for aa in [-135,-90,-45,0,180]:
  a=math.radians(aa);line(layer,[(x+24*math.cos(a),y-3+24*math.sin(a)),(x+31*math.cos(a),y-3+31*math.sin(a))],'#d4aa58',2)
 layer.putalpha(layer.getchannel('A').point(lambda v:round(v*q)));im.alpha_composite(layer)

ANCH=np.array([(90,585),(180,700),(260,772),(350,793),(450,780),(550,690),(650,576),(765,532),(850,555),(950,657),(1050,778),(1150,831),(1223,843),(1320,838),(1400,801),(1500,683),(1600,563),(1692,531)],float)
ROAD=np.array([(x,np.interp(x,ANCH[:,0],ANCH[:,1])) for x in range(90,1693)],float)
# Smooth anchors without changing stop coordinates.
def road(x):return np.interp(x,ROAD[:,0],ROAD[:,1])
STOPS=[(1.5,6.5,220),(10,15,765),(18.5,23.5,1223),(27.3,32.3,1692)]
LEGS=[(0,1.5,150,220),(6.5,10,220,765),(15,18.5,765,1223),(23.5,27.3,1223,1692)]
def travel(t):
 for a,b,x0,x1 in LEGS:
  if a<=t<b:
   xs=ROAD[(ROAD[:,0]>=x0)&(ROAD[:,0]<=x1)];dist=np.r_[0,np.cumsum(np.linalg.norm(np.diff(xs,axis=0),axis=1))];s=E((t-a)/(b-a))*dist[-1];x=np.interp(s,dist,xs[:,0]);y=road(x);slope=(road(x+3)-road(x-3))/6
   w=E((t-a)/.23)*(1-E((t-b+.28)/.28));return x,y,s/37, w,max(-9,min(9,slope*10)),0,-1
 for j,(a,b,x) in enumerate(STOPS):
  if a<=t<b:return x,road(x),0,0,0,t-a,j
 return 1692,531,0,0,0,t-27.3,3
# Original five cards are separated along their native borders and always keep their design.
CARDPOLYS=[[(1080,672),(1141,659),(1157,755),(1093,768)],[(1140,651),(1204,644),(1220,742),(1157,755)],[(1207,637),(1270,635),(1280,733),(1217,744)],[(1277,642),(1340,652),(1330,751),(1272,739)],[(1344,655),(1401,674),(1392,767),(1333,752)]]
CARDS=[]
for poly in CARDPOLYS:
 mask=Image.new('L',BG.size);ImageDraw.Draw(mask).polygon(poly,fill=255);bb=mask.getbbox();a=BG.crop(bb);a.putalpha(mask.crop(bb));CARDS.append((a,bb))
BADGES=[]
for cx,cy in [(350,793),(765,532),(1223,843),(1692,531)]:
 box=(cx-41,cy-43,cx+41,cy+43);a=BG.crop(box);m=Image.new('L',a.size);ImageDraw.Draw(m).ellipse((3,3,a.width-3,a.height-3),fill=255);a.putalpha(m);BADGES.append((a,box))

def frame(t):
 im=BG.copy();dd=ImageDraw.Draw(im);dd.rounded_rectangle((330,569,338,691),3,fill='#e6ece0');dd.rectangle((331,691-round(115*E((t-3.1)/.65)),337,697),fill='#e8764c');x,y,ph,walk,lean,u,j=travel(t);gaze=(3,0) if walk else (0,0);tilt=0;mood='smile';up=0
 if j==0:
  lean=-12*E(u/.65)*(1-E((u-2)/.6));tilt=keys(u,[(0,0),(1,-5),(2.1,-3),(2.7,5),(3.3,0),(5,0)]).item();gaze=(3,-2) if u>2 else (3,2);mood='surprise' if 2.1<u<3.2 else 'worry' if 3.2<u<4.5 else 'smile'
 if j==1:
  lean=7*E((u-.25)/.5)*(1-E((u-3)/.5));tilt=keys(u,[(0,0),(1,6),(1.8,-5),(2.5,5),(3.2,-8),(4,0),(5,0)]).item();gaze=(-3,2) if 1<u<2 else (3,2) if 2<u<3 else (0,-2);mood='think' if 2.7<u<4 else 'smile'
 if j==2:up=12*E(u/.3)*(1-E((u-4.6)/.4));tilt=2*math.sin(u*9) if u<3.5 else -5;gaze=(int(3*math.sin(u*2)),2);mood='think' if u>3.4 else 'smile'
 if j==3:tilt=2*math.sin(u*7) if 1<u<3.7 else 0;gaze=(-3,3) if u<3.7 else (0,0)
 r=Rig(x,y,ph,walk,lean,tilt,gaze,mood,up,t);hands=r.hands;props=[];backprops=[];state='行走' if j<0 else ['测体征','查病因','追并发症','开处方'][j]
 if j==0:
  # Hands, not opacity, retrieve the instrument from the side and return it there.
  h=keys(u,[(0,r.B((345,415))),(.45,r.B((363,403))),(1.1,(293,660)),(1.8,(296,677)),(2.2,(296,677)),(2.6,r.B((354,320))),(2.9,r.B((345,415))),(3.25,r.B((338,215))),(3.5,r.B((365,343))),(4.25,r.B((360,350))),(4.8,r.B((345,415))),(5,r.hands[1])]);hands=[r.hands[0],h]
  if .18<u<2.98:props.append(('therm',h,10))
  if u>3.5:
   q=E((u-3.5)/.25)*(1-E((u-4.65)/.25));lh=lerp(r.B((190,412)),r.B((199,365)),q);hands[0]=lh;props.append(('note',lh+np.array([18,-9]),0));w=E((u-3.7)/.2)*(1-E((u-4.3)/.2));hands[1]=lerp(hands[1],lh+[35+2*math.sin(u*20),-13+2*math.sin(u*15)],w);props.append(('pen',hands[1],None))
  dd=ImageDraw.Draw(im)
  if 1.6<u<2.3:
   rr=14+8*math.sin((u-1.2)*4);dd.ellipse((285-rr,724-rr/4,285+rr,724+rr/4),outline='#7eb8bd',width=2)
 elif j==1:
  h=keys(u,[(0,r.hands[1]),(.4,r.B((339,340))),(1,r.B((376,350))),(1.65,r.B((351,355))),(2.45,r.B((382,360))),(3,r.B((365,340))),(4.4,r.B((350,410))),(4.85,r.hands[1])]);hands=[r.hands[0],h]
  if .2<u<4.75:props.append(('magnify',h,15*math.sin(u*2)))
  bulb(im,(x+172,y-390),E((u-3.1)/.35)*(1-E((u-4.3)/.5)))
 elif j==2:
  q=E(u/.4)*(1-E((u-4.5)/.5));lh=lerp(r.hands[0],r.B((115,358)),q);write=E((u-3.35)/.35)*(1-E((u-4.0)/.35));lh=lerp(lh,r.B((214,363)),write);h=keys(u,[(0,r.hands[1]),(.45,(1188,710)),(1.1,(1210,704)),(1.75,(1243,699)),(2.4,(1272,710)),(3.05,(1305,718)),(3.7,r.B((361,340))),(4.2,r.B((382,330))),(4.75,r.hands[1])]);h=lerp(h,lh+[29+2*math.sin(u*19),-13+2*math.sin(u*17)],write);hands=[lh,h]
  if .2<u<4.7:
   props.append(('note',lh+np.array([13,0]),-8))
   if .35<u<3.38:
    target=keys(u,[(.35,(1119,709)),(.9,(1119,709)),(1.1,(1180,694)),(1.55,(1180,694)),(1.75,(1243,687)),(2.2,(1243,687)),(2.4,(1308,704)),(2.85,(1308,704)),(3.05,(1373,719))]);props.append(('pointer',h,target))
   else:props.append(('pen',h,None))
 elif j==3:
  # A visible small toss puts the hat on; it cannot appear on the hood by a cut.
  lh=keys(u,[(0,r.hands[0]),(.4,r.B((157,346))),(.8,r.B((142,309))),(1.05,r.B((185,365))),(1.2,r.B((250,340))),(3.9,r.B((250,340))),(4.3,r.hands[0])]);rh=keys(u,[(0,r.hands[1]),(.5,r.B((353,373))),(1.6,r.B((285,355))),(3.5,r.B((285,355))),(3.9,r.B((350,375))),(4.4,r.B((371,285))),(5.0,r.B((362,292))),(6,r.B((370,286)))]);hands=[lh,rh]
  capend=r.head+np.array([0,-189]);start=lh+np.array([0,-12])
  if .18<u<.8:props.append(('hat',start,0))
  elif .8<=u<1.4:
   q=E((u-.8)/.6);pos=lerp(r.B((142,309))+[0,-12],capend,q)+[0,-80*math.sin(math.pi*q)];props.append(('hat',pos,-15*math.sin(math.pi*q)))
  elif u>=1.4:props.append(('hat',capend,0))
  if u>.9:props.append(('clip',lh+np.array([30,0]),min(3,max(0,(u-1.4)/.72))))
  if 1.2<u<3.8:
   yy=keys(u,[(1.2,0),(1.85,0),(2.1,23),(2.55,23),(2.82,46),(3.8,46)]).item();w=E((u-1.2)/.25)*(1-E((u-3.55)/.25));rh=lerp(rh,lh+[-15+3*math.sin(u*17),-5+yy+2*math.cos(u*17)],w);hands[1]=rh;props.append(('pen',rh,None))
  if u>4.5:hands[1]=hands[1]+[8*math.sin((u-4.5)*9),0]
 # Retrieval and stowing use real occlusion by the body.
 hidden=[]
 for prop in props:
  kind=prop[0]
  rear=(j==0 and kind=='therm' and (u<.5 or u>2.78)) or (j==0 and kind=='note' and (u<3.7 or u>4.65)) or (j==1 and kind=='magnify' and (u<.6 or u>4.35)) or (j==2 and kind=='note' and (u<.45 or u>4.45)) or (j==3 and kind=='hat' and u<.4)
  if rear:
   if kind=='therm':thermometer(im,prop[1],prop[2])
   elif kind=='note':notebook(im,prop[1],prop[2])
   elif kind=='magnify':magnifier(im,prop[1],prop[2],t)
   elif kind=='hat':doctorhat(im,prop[1],prop[2])
   hidden.append(id(prop))
 r.front(im)
 # Native road badges stay legible in the foreground.
 for aa,bb in BADGES:im.alpha_composite(aa,bb[:2])
 if abs(x-1223)<205:
  for k,(aa,bb) in enumerate(CARDS):
   pulse=math.sin(math.pi*max(0,min(1,(u-(.35+k*.65))/.55))) if j==2 else 0
   sy=1+.045*pulse;tile=aa.resize((aa.width,round(aa.height*sy)),Image.Resampling.BICUBIC);im.alpha_composite(tile,(bb[0],bb[3]-tile.height))
   if pulse>.01:
    dd=ImageDraw.Draw(im);poly=[(px,bb[3]-(bb[3]-py)*sy) for px,py in CARDPOLYS[k]];dd.line(poly+[poly[0]],fill=(224,187,111,round(190*pulse)),width=3,joint='curve')
 r.arms(im,hands)
 for prop in props:
  if id(prop) in hidden:continue
  kind,p,a=prop
  if kind=='therm':thermometer(im,p,a)
  elif kind=='pointer':line(im,[p,a],'#ad854d',4)
  elif kind=='note':notebook(im,p,a)
  elif kind=='pen':pencil(im,p)
  elif kind=='magnify':magnifier(im,p,a,t)
  elif kind=='hat':doctorhat(im,p,a)
  elif kind=='clip':clipboard(im,p,-5,a,E((u-3.75)/.4))
 for h in hands:grip(im,h)
 return im.convert('RGB'),dict(t=round(t,4),station=j+1,state=state,foot=[round(x,2),round(y,2)],walking=walk,lean=lean,head_tilt=tilt,props=[v[0] for v in props],hands=[list(map(float,h)) for h in hands],shoulders=[list(map(float,a)) for a in r.shoulders])

def main():
 if '--stills' in sys.argv:
  ts=[.75,2.9,4.25,5.5,8.2,11.6,13.4,16.5,19.4,20.7,22.4,25.4,28.3,29.6,31.5,33.0];mont=Image.new('RGB',(1920,1080))
  for i,t in enumerate(ts):
   im,meta=frame(t);im.save(Q/f'动作_{t:05.2f}.png');tile=im.resize((480,270));mont.paste(tile,((i%4)*480,(i//4)*270))
  mont.save(Q/'动作总览.png');print('stills complete',flush=True);return
 target=OUT/'四步会诊路线_全程动作展示.mp4';tmp=target.with_name('.四步会诊路线_编码中.mp4');log=(Q/'编码日志.txt').open('wb');audit=[]
 cmd=[str(FF),'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',str(FPS),'-i','-','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-frames:v',str(N),'-t',str(N/FPS),'-c:v','libx264','-profile:v','baseline','-level','4.0','-g','24','-bf','0','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(tmp)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
 for i in range(N):
  im,meta=frame(i/FPS);proc.stdin.write(im.tobytes());audit.append(meta)
  if i%120==0:print(f'render {i}/{N}',flush=True)
 proc.stdin.close();assert proc.wait()==0;log.close();d=subprocess.run([str(FF),'-v','error','-i',str(tmp),'-f','null','-'],capture_output=True);assert d.returncode==0 and not d.stderr,d.stderr
 tmp.replace(target);(Q/'逐帧动作记录.json').write_text(json.dumps(audit,ensure_ascii=False),encoding='utf-8');report=dict(path=str(target),duration=N/FPS,frames=N,fps=FPS,resolution=[W,H],decode='PASS',sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size,merged_into_full=False)
 (Q/'交付验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
