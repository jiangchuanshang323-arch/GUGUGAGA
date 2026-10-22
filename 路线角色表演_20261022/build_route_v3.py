from pathlib import Path
import math,json,subprocess,hashlib,io,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
import rig_reference_v1 as old
P,R,FF,SRC,BG,SCALE=old.P,old.R,old.FF,old.SRC,old.BG,old.SCALE
Q=R/'检查/原翅膀与帽子贴合';Q.mkdir(exist_ok=True);OUT=old.OUT
FPS=24;N=864; E=old.E;keys=old.keys;lerp=old.lerp;stamp=old.stamp;line=old.line
FIN,EDGE,PAPER,BLUE=old.FIN,old.EDGE,old.PAPER,old.BLUE

def curve(points,n=24):
 out=[tuple(points[0])];a=np.array(points[0],float)
 for b,c,d in zip(points[1::3],points[2::3],points[3::3]):
  b,c,d=np.array(b),np.array(c),np.array(d)
  out.extend([tuple((1-u)**3*a+3*(1-u)**2*u*b+3*(1-u)*u*u*c+u**3*d) for u in np.linspace(0,1,n)[1:]]);a=d
 return out

def pathdraw(im,pts,fill,edge=None,width=3):
 dd=ImageDraw.Draw(im);p=curve(pts);dd.polygon(p,fill=fill)
 if edge:dd.line(p+[p[0]],fill=edge,width=width,joint='curve')
BODY=Image.new('RGBA',(1536,1536))
def bp(pts,fill,edge=EDGE,w=5):pathdraw(BODY,[(x*3,y*3) for x,y in pts],fill,edge,w*3)
bp([(207,269),(220,259),(296,259),(312,272),(330,289),(350,352),(354,408),(360,448),(330,469),(264,470),(196,471),(162,449),(166,410),(168,361),(185,294),(207,269)],FIN)
bp([(220,288),(238,275),(285,275),(304,291),(326,320),(337,373),(333,411),(330,439),(307,454),(265,455),(220,456),(193,439),(191,409),(188,364),(200,312),(220,288)],'#fafaf5')
bp([(192,408),(225,433),(298,433),(333,408),(331,437),(309,454),(265,455),(220,456),(195,440),(192,408)],'#bfc0cb',None)
BODY=BODY.resize((512,512),Image.Resampling.LANCZOS)
# Keep only the yellow feet plus their original outline, excluding cut trouser strips.
FEET=[]
for part in old.FEET:
 ar=np.array(part);yellow=(ar[:,:,0]>150)&(ar[:,:,1]>100)&(ar[:,:,2]<105)&(ar[:,:,3]>0)
 m=Image.fromarray((yellow*255).astype('uint8')).filter(ImageFilter.MaxFilter(7));a=part.copy();a.putalpha(Image.fromarray(np.minimum(np.array(m),ar[:,:,3])));FEET.append(a)
# Reuse the original shaded flippers, with native shoulder and grip landmarks.
WINGS=[old.part([(177,276),(215,276),(200,312),(183,352),(169,394),(145,407),(106,414),(99,393),(110,352),(141,306),(177,276)]),old.part([(316,277),(341,281),(372,319),(398,358),(424,390),(422,407),(400,413),(367,393),(346,370),(333,327),(316,277)])]
WP=[np.array([192.,289.]),np.array([330.,289.])];WT=[np.array([122.,393.]),np.array([407.,394.])]
for i,im in enumerate(WINGS):im.save(R/'素材'/f'原画翅膀_{i+1}.png')
def fin(im,a,b,side):
 a,b=np.array(a,float),np.array(b,float);original=WT[side]-WP[side];L=np.linalg.norm(original);axis=original/L;perp=np.array([-axis[1],axis[0]])
 D=np.linalg.norm(b-a);v=(b-a)/max(1,D);n=np.array([-v[1],v[0]]);bend=math.sqrt(max(0,(L*SCALE)**2-D**2))*.54
 # Fold inward without changing the original painted outline or adding a human elbow.
 control=(a+b)/2+n*bend*(1 if side==0 else -1)
 us=np.linspace(0,1,25);centers=np.array([(1-u)**2*a+2*(1-u)*u*control+u*u*b for u in us]);lo=np.floor(centers.min(0)-43).astype(int);hi=np.ceil(centers.max(0)+43).astype(int)
 xs=list(range(0,int(hi[0]-lo[0]),6))+[int(hi[0]-lo[0])];ys=list(range(0,int(hi[1]-lo[1]),6))+[int(hi[1]-lo[1])]
 grid=np.array([(x,y) for y in ys for x in xs],float)+lo;segs=centers[1:]-centers[:-1];base=centers[:-1]
 delta=grid[:,None,:]-base[None,:,:];proj=np.clip(np.sum(delta*segs,axis=2)/np.maximum(1e-5,np.sum(segs*segs,axis=1)),0,1);near=base[None,:,:]+proj[:,:,None]*segs[None,:,:];dist=np.sum((grid[:,None,:]-near)**2,axis=2);ix=np.argmin(dist,axis=1);sel=near[np.arange(len(grid)),ix];u=(ix+proj[np.arange(len(grid)),ix])/24;tan=segs[ix];tan/=np.maximum(1e-5,np.linalg.norm(tan,axis=1))[:,None];norm=np.stack([-tan[:,1],tan[:,0]],axis=1);q=np.sum((grid-sel)*norm,axis=1)/SCALE;u+=np.sum((grid-sel)*tan,axis=1)/(L*SCALE)
 mapped=WP[side]+u[:,None]*L*axis+q[:,None]*perp;mesh=[];nx=len(xs)
 for yi in range(len(ys)-1):
  for xi in range(len(xs)-1):
   k=yi*nx+xi;quad=mapped[[k,k+nx,k+nx+1,k+1]].flatten();mesh.append(((xs[xi],ys[yi],xs[xi+1],ys[yi+1]),tuple(quad)))
 tile=WINGS[side].transform(tuple(hi-lo),Image.Transform.MESH,mesh,Image.Resampling.BICUBIC);im.alpha_composite(tile,tuple(lo))
# Eye and mouth expressions preserve the original glasses, irises and face.
FC={}
def face(gaze,blink,mood):
 gaze=tuple(int(v) for v in gaze);blink=round(blink*10)/10;k=(gaze,blink,mood)
 if k in FC:return FC[k]
 a=old.face(gaze,blink,'surprise' if mood=='surprise' else 'worry' if mood=='worry' else 'think' if mood=='think' else 'smile').copy();d=ImageDraw.Draw(a)
 if mood=='surprise':
  d.arc((185,151,235,171),190,350,fill='#51443d',width=3);d.arc((282,151,332,171),190,350,fill='#51443d',width=3)
  d.ellipse((256,229,274,247),fill='#9a4e50',outline='#743f3f',width=2)
 elif mood=='think':
  d.arc((191,158,235,173),195,345,fill='#51443d',width=3);d.line((286,166,325,160),fill='#51443d',width=3)
 elif mood=='proud':
  d.arc((249,225,280,243),0,180,fill='#843f47',width=3)
 FC[k]=a;return a

ANCH=np.vstack([old.ANCH,[(1780,550),(1900,615)]])
def road(x):return np.interp(x,ANCH[:,0],ANCH[:,1])
STOPS=[(1.5,6.5,220),(10.5,15.5,630),(19,24,995),(29.5,34.5,1760)]
LEGS=[(0,1.5,150,220),(6.5,10.5,220,630),(15.5,19,630,995),(24,29.5,995,1760)]
TRAVEL=[]
for a,b,x0,x1 in LEGS:
 xs=np.linspace(x0,x1,max(2,round(x1-x0)));ys=road(xs);ds=np.r_[0,np.cumsum(np.hypot(np.diff(xs),np.diff(ys)))];TRAVEL.append((a,b,x0,x1,xs,ds))
def travel(t):
 for a,b,x0,x1,xs,ds in TRAVEL:
  if a<=t<b:
   u=(t-a)/(b-a);dist=E(u)*ds[-1];x=np.interp(dist,ds,xs);w=E((t-a)/.3)*(1-E((t-b+.35)/.35));slope=(road(x+5)-road(x-5))/10
   return float(x),float(road(x)),w,float(np.clip(math.degrees(math.atan(slope))*.28,-14,14)),t-a,-1,(x0,x1,x)
 for j,(a,b,x) in enumerate(STOPS):
  if a<=t<b:return x,float(road(x)),0,0,t-a,j,None
 return 1760,float(road(1760)),0,0,t-29.5,3,None

class Rig:
 def __init__(self,x,y,t,walk,lean,tilt=0,gaze=(0,0),mood='smile',step=None):
  self.x,self.y,self.t,self.walk=x,y,t,walk;self.angle=lean;self.step=step
  self.phase=0 if step is None else (x-step[0])/70*2*math.pi
  self.pel=np.array([x,y-77-3.5*math.cos(self.phase*2)*walk]);th=math.radians(lean);self.mat=SCALE*np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]])
  self.head=self.B((256,270));self.tilt=lean*.35+tilt;self.gaze=gaze;self.mood=mood
  self.shoulders=[self.B((192,289)),self.B((330,289))]
  self.hands=[self.B((126-5*math.sin(self.phase)*walk,391)),self.B((403+5*math.sin(self.phase)*walk,391))]
  self.footlog=[]
 def B(self,p):return self.pel+self.mat@(np.array(p)-[256,405])
 def bound(self,hands):
  out=[]
  for side,(a,b) in enumerate(zip(self.shoulders,hands)):
   v=np.array(b)-a;L=np.linalg.norm(v);native=np.linalg.norm(WT[side]-WP[side])*SCALE;out.append(a+v*min(1,native/max(.01,L)))
  return out
 def base(self,im):
  stamp(im,old.TAIL,(256,405),self.pel,self.angle)
  for j,piv in enumerate([(225,470),(300,470)]):
   rest=self.B(piv);ankle=rest.copy();stance=False
   if self.step:
    x0,x1,x=self.step;L=70.;offset=(piv[0]-256)*SCALE;ph=(x-x0)/L+j*.5;n=math.floor(ph);f=ph-n;touch=x0+L*(n-j*.5+.28)+offset
    if f<.6:fx=touch;lift=0;stance=True
    else:q=(f-.6)/.4;fx=touch+L*E(q);lift=22*math.sin(math.pi*q)
    planned=np.array([fx,road(fx)-26-lift]);ankle=lerp(rest,planned,self.walk)
   hip=self.B((piv[0],444));line(im,[hip,ankle],FIN,21)
   stamp(im,FEET[j],piv,ankle,0 if stance else 7*math.sin(self.phase+j*math.pi)*self.walk)
   self.footlog.append(dict(x=float(ankle[0]),y=float(ankle[1]),stance=stance and self.walk>.999))
  stamp(im,BODY,(256,405),self.pel,self.angle)
 def arms(self,im,hands):
  for side,(a,b) in enumerate(zip(self.shoulders,hands)):fin(im,a,b,side)
 def finish(self,im):
  neck=Image.new('RGBA',(512,512));ImageDraw.Draw(neck).ellipse((232,245,291,283),fill='#ffdfc7');stamp(im,neck,(256,270),self.head,self.tilt)
  b=self.t%4.1;blink=1-E((b-3.7)/.08)*(1-E((b-3.84)/.12))
  stamp(im,face(self.gaze,blink,self.mood),(256,270),self.head,self.tilt)
  stamp(im,old.BOW,(263,282),self.B((263,282)),self.angle+3*math.sin(self.phase-.4)*self.walk)

# A hinged cover projects around the left spine. Paper is never replaced by a wipe.
def clipboard(im,p,angle=0,checks=0,close=0):
 a=Image.new('RGBA',(180,174));d=ImageDraw.Draw(a);d.rounded_rectangle((18,15,149,163),8,fill='#b39370',outline=EDGE,width=3);d.rectangle((26,25,141,153),fill=PAPER);d.rounded_rectangle((65,8,103,33),5,fill='#91b7ba',outline=BLUE,width=2)
 for j in range(3):
  y=56+j*30;d.rectangle((36,y,48,y+12),outline=BLUE,width=2);d.line((61,y+6,127,y+6),fill='#94a59c',width=2);q=E(checks-j)
  if q>0:
   pts=[(36,y+5),(42,y+11),(52,y-2)];d.line([pts[0],tuple(lerp(pts[0],pts[1],min(1,q*2)))],fill='#458c7c',width=3)
   if q>.5:d.line([pts[1],tuple(lerp(pts[1],pts[2],q*2-1))],fill='#458c7c',width=3)
 if close>0:
  theta=math.pi*(1-close);width=126*math.cos(theta);left=21;tip=left+width;rise=12*math.sin(theta);poly=[(left,20),(tip,20-rise),(tip,157+rise),(left,157)];d.polygon(poly,fill='#b89978' if close>.5 else '#d5c0a0');d.line(poly+[poly[0]],fill='#735e48',width=3);d.line((left+2,21,left+2,156),fill='#826749',width=2)
 stamp(im,a,(86,96),p,angle,.72)
# Small cap is placed against the side of the penguin hood, then straightened by hand.
def cap(im,p,ang):
 # Coordinates share the exact native head pivot, including head rotation.
 art=Image.new('RGBA',(512,612));shadow=Image.new('RGBA',art.size);d=ImageDraw.Draw(shadow)
 d.ellipse((210,122,316,138),fill=(43,48,51,48));shadow=shadow.filter(ImageFilter.GaussianBlur(2));art.alpha_composite(shadow)
 pathdraw(art,[(166,123),(173,99),(173,65),(189,50),(213,38),(309,38),(334,50),(350,65),(351,99),(359,123),(317,135),(210,135),(166,123)],'#fff8e8',BLUE,3)
 # Curved lower rim follows the crown, no dangling side strip.
 d=ImageDraw.Draw(art);d.line(curve([(169,122),(215,135),(313,135),(356,122)]),fill='#8ab1b7',width=4);d.rectangle((255,64,270,104),fill='#c97864');d.rectangle((242,77,283,91),fill='#c97864')
 stamp(im,art,(256,370),p,ang,SCALE)

def lens(im,p,target,angle=0):
 p=np.array(p);v=np.array(target)-p;v/=max(1,np.linalg.norm(v));c=p+v*45;rad=29
 cx,cy=np.round(target).astype(int);sample=BG.crop((cx-17,cy-17,cx+17,cy+17)).resize((58,58),Image.Resampling.LANCZOS);mask=Image.new('L',(58,58));ImageDraw.Draw(mask).ellipse((1,1,56,56),fill=255);sample.putalpha(mask);im.alpha_composite(sample,(round(c[0]-29),round(c[1]-29)))
 d=ImageDraw.Draw(im);d.ellipse((c[0]-rad,c[1]-rad,c[0]+rad,c[1]+rad),outline='#a47d46',width=5);d.arc((c[0]-23,c[1]-23,c[0]+23,c[1]+23),205,280,fill='#fff6db',width=3);line(im,[p-v*12,c-v*29],'#947048',9);line(im,[p-v*10,c-v*31],'#d4b27c',3)

def frame(t):
 im=BG.copy();x,y,w,lean,u,j,step=travel(t);mood='smile';tilt=0;gaze=(5,-1) if w else (0,0)
 if j==0:
  lean=-8*E(u/.6)*(1-E((u-2.15)/.5));tilt=keys(u,[(0,0),(1,-5),(2.15,-5),(2.55,6),(3,0),(5,0)]).item();gaze=(5,3) if u<2.2 else (5,-4) if u<3 else (-3,3);mood='surprise' if 2.15<u<3.1 else 'worry' if 3.1<u<4.5 else 'smile'
 elif j==1:
  tilt=keys(u,[(0,0),(.8,7),(1.6,4),(2.3,-5),(3,-8),(3.7,0),(5,0)]).item();lean=5*E(u/.5)*(1-E((u-2.7)/.5));gaze=(-4,4) if u<1.8 else (5,4) if u<2.8 else (1,-4);mood='think' if 2.6<u<3.6 else 'proud' if u>=3.6 else 'smile'
 elif j==2:tilt=2.5*math.sin(u*7) if u<3.3 else -6 if u<4.35 else 0;gaze=(5,3);mood='think' if u>3.3 else 'smile'
 elif j==3:tilt=-4*E(u/.5)*(1-E((u-1.2)/.4))+2.5*math.sin((u-2.1)*3)*E((u-2.1)/.3)*(1-E((u-3.9)/.3));gaze=(4,-5) if u<1.4 else (-3,3) if u<3.9 else (0,0);mood='proud' if u>3.9 else 'smile'
 r=Rig(x,y,t,w,lean,tilt,gaze,mood,step);hands=[h.copy() for h in r.hands];props=[];rear=[]
 # The large instrument starts low and rises only after the small probe reaches water.
 d=ImageDraw.Draw(im);d.rounded_rectangle((329,571,340,694),4,fill='#e4f0e7');d.rounded_rectangle((331,691-round(112*E((t-3.05)/.8)),338,704),3,fill='#e4714c')
 if j==0:
  rh=keys(u,[(0,r.hands[1]),(.4,r.B((354,406))),(.9,(289,651)),(1.5,(292,676)),(2.0,(292,676)),(2.55,r.B((358,328))),(2.85,r.B((355,405))),(3.35,r.B((337,210))),(3.75,r.B((345,349))),(4.6,r.B((352,405))),(5,r.hands[1])]);lh=keys(u,[(0,r.hands[0]),(3.35,r.hands[0]),(3.65,r.B((204,370))),(4.45,r.B((204,370))),(4.85,r.hands[0])]);write=E((u-3.8)/.25)*(1-E((u-4.45)/.2));rh=lerp(rh,lh+[35+2*math.sin(u*17),-12],write);hands=r.bound([lh,rh])
  if .16<u<2.98:props.append(('therm',hands[1],0))
  if 3.4<u<4.8:props.append(('note',hands[0]+[19,-9],0))
  if 3.85<u<4.6:props.append(('pen',hands[1],None))
  if 1.5<u<2.1:
   rr=15+9*math.sin((u-1.5)*4);d.ellipse((292-rr,725-rr/4,292+rr,725+rr/4),outline='#79b5b8',width=2)
 elif j==1:
  rh=keys(u,[(0,r.hands[1]),(.4,r.B((357,402))),(.85,r.B((365,356))),(1.5,r.B((367,349))),(2.3,r.B((382,371))),(2.9,r.B((368,352))),(3.75,r.B((366,360))),(4.45,r.B((355,406))),(4.85,r.hands[1])]);hands=r.bound([hands[0],rh]);target=keys(u,[(0,(685,502)),(1.2,(700,477)),(1.7,(705,475)),(2.4,(725,461)),(2.9,(728,458)),(5,(700,477))])
  if .18<u<4.75:props.append(('lens',hands[1],target))
  old.bulb(im,(x+128,y-408),E((u-3.15)/.3)*(1-E((u-4.15)/.4)))
 elif j==2:
  lh=keys(u,[(0,hands[0]),(.45,r.B((191,368))),(3.2,r.B((191,368))),(3.65,r.B((218,360))),(4.15,r.B((218,360))),(4.55,r.B((164,395))),(4.9,hands[0])]);target=keys(u,[(0,(1119,709)),(.8,(1119,709)),(1.05,(1180,694)),(1.45,(1180,694)),(1.7,(1243,687)),(2.1,(1243,687)),(2.35,(1308,704)),(2.75,(1308,704)),(3.0,(1373,719)),(5,(1373,719))]);rh=keys(u,[(0,hands[1]),(.45,r.B((376,352))),(3.2,r.B((378,351))),(3.6,lh+[36,-13]),(4.0,lh+[36,-13]),(4.4,r.B((382,330))),(4.9,hands[1])]);hands=r.bound([lh,rh])
  if .2<u<4.6:props.append(('note',hands[0]+[18,-8],0))
  if .4<u<3.28:props.append(('indicate',hands[1],target))
  if 3.45<u<4.15:props.append(('pen',hands[1],None))
  for k,(aa,bb) in enumerate(old.CARDS):
   pulse=math.sin(math.pi*max(0,min(1,(u-(.35+k*.65))/.55)));sy=1+.035*pulse;tile=aa.resize((aa.width,round(aa.height*sy)),Image.Resampling.BICUBIC);im.alpha_composite(tile,(bb[0],bb[3]-tile.height))
   if pulse>.05:
    poly=[(px,bb[3]-(bb[3]-py)*sy) for px,py in old.CARDPOLYS[k]];ImageDraw.Draw(im).line(poly+[poly[0]],fill='#cba767',width=3,joint='curve')
 elif j==3:
  end=r.head+[77,-93]
  rh=keys(u,[(0,hands[1]),(.3,r.B((358,405))),(.65,r.B((372,321))),(1.2,end),(1.5,end+[0,-3]),(2.1,r.B((355,365))),(2.35,r.B((286,346))),(3.85,r.B((286,346))),(4.15,r.B((351,363))),(4.55,r.B((370,285))),(6.5,r.B((370,285)))]);lh=keys(u,[(0,hands[0]),(1.4,hands[0]),(1.9,r.B((246,345))),(3.95,r.B((246,345))),(4.4,r.B((200,380))),(6.5,r.B((200,380)))]);hands=r.bound([lh,rh]);capq=E((u-.65)/.55)
  props.append(('cap',r.head,r.tilt))
  if u>1.45:
   cp=hands[0]+[25,-5];checks=np.clip((u-2.15)/.55,0,3);close=E((u-4.0)/.45);props.append(('clip',cp,(checks,close)))
   if 2.1<u<3.95:
    yy=keys(u,[(2.1,0),(2.5,0),(2.73,22),(3.12,22),(3.35,44),(3.95,44)]).item();weight=E((u-2.1)/.25)*(1-E((u-3.65)/.3));desired=cp+[-31,-4+yy]+[2*math.sin(u*20),2*math.sin(u*15)];hands[1]=lerp(hands[1],desired,weight);hands=r.bound(hands);props.append(('pen',hands[1],None))
  if u>4.6:hands[1]=hands[1]+[7*math.sin((u-4.6)*8),0]
 # Draw pocket props behind the body while taking out or returning them.
 def drawprop(prop):
  kind,p,a=prop
  if kind=='therm':old.thermometer(im,p,8)
  elif kind=='note':old.notebook(im,p,-5)
  elif kind=='pen':old.pencil(im,p)
  elif kind=='lens':lens(im,p,a)
  elif kind=='indicate':
   vec=np.array(a)-p;vec/=max(1,np.linalg.norm(vec));line(im,[p-vec*12,p+vec*38],'#a9814a',4)
  elif kind=='cap':cap(im,p,a)
  elif kind=='clip':clipboard(im,p,-4,*a)
 for prop in props:
  kind=prop[0];behind=(j==0 and kind=='therm' and (u<.48 or u>2.78)) or (j==0 and kind=='note' and (u<3.6 or u>4.55)) or (j==1 and kind=='lens' and (u<.6 or u>4.4)) or (j==2 and kind=='note' and (u<.42 or u>4.4))  or (j==3 and kind=='clip' and u<1.72)
  if behind:drawprop(prop);rear.append(id(prop))
 r.base(im);r.arms(im,hands);r.finish(im)
 for prop in props:
  if id(prop) not in rear:drawprop(prop)
 for h in hands:
  if any(np.linalg.norm(np.array(prop[1])-h)<25 and prop[0]!='cap' for prop in props):
   ImageDraw.Draw(im).ellipse((h[0]-6,h[1]-4,h[0]+6,h[1]+5),fill='#50525f',outline='#22252b',width=1)
 # Badges are only foreground if they are near the feet, never pasted across a torso.
 for aa,bb in old.BADGES:
  if bb[1]>y-40:im.alpha_composite(aa,bb[:2])
 return im.convert('RGB'),dict(t=t,station=j+1,foot=[x,y],walking=w,hands=[list(map(float,h)) for h in hands],shoulders=[list(map(float,p)) for p in r.shoulders],feet=r.footlog,props=[p[0] for p in props])

def main():
 moments=[7.3,8.8,10.2,32,32.8,33.5,34.5,35.5];sheet=Image.new('RGB',(1600,900))
 for i,t in enumerate(moments):
  im,_=frame(t);im.save(Q/f'原翅膀帽子_{t:.2f}.png');x,y,*_=travel(t);tile=im.crop((round(x-200),round(y-430),round(x+200),round(y+20))).resize((400,450));sheet.paste(tile,((i%4)*400,(i//4)*450))
 sheet.save(Q/'局部动作总览.png')
 if '--stills' in sys.argv:return
 dest=OUT/'四步会诊路线_原翅膀与帽子贴合_8秒小样.mp4';tmp=dest.with_name('.原翅膀帽子编码中.mp4');times=[6.75+i/24 for i in range(84)]+[31.5+i/24 for i in range(108)];audit=[]
 with (Q/'编码日志.txt').open('wb') as log:
  proc=subprocess.Popen([str(FF),'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-frames:v','192','-t','8','-c:v','libx264','-profile:v','baseline','-level','4.0','-g','24','-bf','0','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE,stderr=log)
  for i,t in enumerate(times):
   im,meta=frame(t);proc.stdin.write(im.tobytes());audit.append(meta)
   if i%48==0:print('render',i,'/192',flush=True)
  proc.stdin.close();assert proc.wait()==0
 check=subprocess.run([str(FF),'-v','error','-i',str(tmp),'-f','null','-'],capture_output=True);assert check.returncode==0 and not check.stderr
 tmp.replace(dest);report=dict(path=str(dest),duration=8,frames=192,resolution=[1920,1080],fps=24,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),decode='PASS',native_wing_source=str(P/'企鹅小老师_教学动作素材_20261012/独立动作PNG/15_走位后站稳.png'),cap_pivot='same as head: native (256,270), art offset +100y',full_route_updated=False,full_course_updated=False)
 (Q/'交付验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=True),flush=True)
if __name__=='__main__':main()
