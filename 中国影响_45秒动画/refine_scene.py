"""Refine the existing 45-second animation: geographic context, actions and climate transitions."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageChops

class Scene:
 def __init__(self,v):
  self.v=v;self.R=v.R;self.t=0;self.audit=[];self.F=v.F;self.E=v.E
  self.mainland_geo=np.array(max(v.G,key=lambda poly:len(poly[0]))[0])
  self.shore_clip=None
  self.geometries=[]
  world=json.loads((self.R/'素材/ne_110m_land.geojson').read_text(encoding='utf-8'))
  for feature in world['features']:
   geom=feature['geometry'];polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
   for poly in polys:
    ring=poly[0]
    if not any(50<=x<=180 and 0<=y<=80 for x,y in ring):continue
    self.geometries.append(np.array([self.geo_xy(x,y) for x,y in ring]))
  self.china=[np.array([self.geo_xy(x,y) for x,y in poly[0]]) for poly in v.G]
  self.provinces=[];self.rivers=[]
  provinces=json.loads((self.R/'素材/中国省界参考.json').read_text(encoding='utf-8'))
  for f in provinces['features']:
   if f['properties'].get('adcode')=='100000_JD':continue # Boundary dashes belong to the inset, not province outlines.
   g=f['geometry'];polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
   for poly in polys:
    self.provinces.append(np.array([self.geo_xy(x,y) for x,y in poly[0]]))
  rivers=json.loads((self.R/'素材/ne_50m_rivers_lake_centerlines.geojson').read_text(encoding='utf-8'))
  for f in rivers['features']:
   name=f['properties'].get('name')
   if name!='Huang':continue
   g=f['geometry'];lines=g['coordinates'] if g['type']=='MultiLineString' else [g['coordinates']]
   for line in lines:
    if not all(90<=x<=125 and 24<=y<=43 for x,y in line):continue
    self.rivers.append((name,np.array([self.geo_xy(x,y) for x,y in line])))
  # OSM waterway relation: connected main-stream nodes including the river mouth.
  river=json.loads((self.R/'素材/长江主河道_核实.geojson').read_text(encoding='utf-8'))
  self.yangtze=[]
  for f in river['features']:
   if self.shore_clip is not None:break
   coords=f['geometry']['coordinates'];kept=[]
   for lon,lat in coords:
    if lon>121 and not self.in_mainland(lon,lat):
     assert kept,'Unexpected offshore start in ordered main-stream chain'
     a=np.array(kept[-1],float);b=np.array([lon,lat],float)
     for _ in range(36):
      mid=(a+b)/2
      if self.in_mainland(*mid):a=mid
      else:b=mid
     kept.append(a.tolist());self.shore_clip=dict(render_end=a.tolist(),removed_next_point=[lon,lat],reason='first intersection with displayed mainland coastline');break
    kept.append([lon,lat])
   if len(kept)<2:continue
   line=np.array([self.geo_xy(x,y) for x,y in kept])
   self.rivers.append(('Yangtze',line));self.yangtze.append((kept,line))
  assert self.shore_clip is not None
  rng=np.random.default_rng(58)
  grain=Image.fromarray(np.uint8(rng.uniform(90,165,(100,170)))).resize((1920,1080),Image.Resampling.BICUBIC)
  yy,xx=np.mgrid[0:1080,0:1920];g=(np.asarray(grain).astype(float)-128)/15
  sea=np.stack([219-17*xx/1920+g,235-8*yy/1080+g,241+3*xx/1920+g],axis=2)
  # Warm paper around the coast, blue open ocean; no artificial exhibition-room effects.
  edge=np.maximum(0,1-xx/450)*.34
  sea=sea*(1-edge[:,:,None])+np.array([250,242,219])[None,None,:]*edge[:,:,None]
  self.paper=Image.fromarray(np.uint8(np.clip(sea,0,255)))
  self.main=self.background(0);self.zoom=self.background(1)
  self.mask=Image.new('L',(1920,1080));d=ImageDraw.Draw(self.mask)
  for p in self.china:d.polygon(self.transform(p,0),fill=255)
  self.warm=self.heat()
  self.colds=[self.cold_layer(k/20) for k in range(21)]
  self.photo=Image.open(self.R/'素材/1998长江洪水_原图.jpg').convert('RGB').resize((880,572),Image.Resampling.LANCZOS)
  self.rigs={}
  for name,file,mouth,top,foot in [
   ('rain','企鹅_双翅握伞杆.png',(587,820),385,1390),
   ('fan','企鹅_扇风.png',(625,535),28,1216),
   ('cold','企鹅_围巾怕冷表情.png',(658,537),37,1215)]:
   a=Image.open(self.R/'素材'/file).convert('RGBA')
   if name=='cold':a=a.resize((1280,1280),Image.Resampling.LANCZOS)
   scale=390/(foot-top)
   self.rigs[name]=dict(image=a,scale=scale,mouth=mouth,foot=foot)
  # A separate fan, rotating about the held handle. The original black flipper stays in place.
  a=self.rigs['fan']['image'];m=Image.new('L',a.size);d=ImageDraw.Draw(m)
  d.polygon([(846,495),(940,442),(1040,449),(1157,519),(1225,613),(1225,716),(1200,808),(1028,757),(966,735),(953,676),(899,590)],fill=255)
  self.fan=Image.new('RGBA',a.size);self.fan.paste(a,(0,0),m)
  body=a.copy();body.putalpha(ImageChops.subtract(body.getchannel('A'),m));self.rigs['fan']['image']=body
  self.header=v.HEADER

 def geo_xy(self,lon,lat):
  # Equirectangular at 35N: one geographic projection shared by every map layer.
  # The wider outline fits the reference composition without stretching a bitmap.
  return (lon-73)*math.cos(math.radians(35))*25,(53.5-lat)*25

 def in_mainland(self,lon,lat):
  p=self.mainland_geo;x1,y1=p[:-1,0],p[:-1,1];x2,y2=p[1:,0],p[1:,1]
  dy=np.where(abs(y2-y1)<1e-12,1e-12,y2-y1)
  return bool(np.count_nonzero(((y1>lat)!=(y2>lat)) & (lon<(x2-x1)*(lat-y1)/dy+x1))%2)

 def point(self,lon,lat,z=0):
  x,y=self.geo_xy(lon,lat);fx,fy=self.geo_xy(119,29)
  return x*(1+z)+210*(1-z)+(850-2*fx)*z,y*(1+z)+70*(1-z)+(450-2*fy)*z

 def transform(self,points,z):
  fx,fy=self.geo_xy(119,29)
  p=points.copy();p[:,0]=p[:,0]*(1+z)+210*(1-z)+(850-2*fx)*z;p[:,1]=p[:,1]*(1+z)+70*(1-z)+(450-2*fy)*z
  return [tuple(q) for q in p]

 def river_mask(self,z):
  mask=Image.new('L',(1920,1080));d=ImageDraw.Draw(mask)
  for poly in self.china:d.polygon(self.transform(poly,z),fill=255)
  return mask

 def linework(self,im,z=0,labels=True):
  d=ImageDraw.Draw(im)
  for poly in self.provinces:
   p=self.transform(poly,z);d.line(p+[p[0]],fill='#b9b69e',width=1 if z<.4 else 2,joint='curve')
  layer=Image.new('RGBA',im.size);rd=ImageDraw.Draw(layer)
  for name,line in self.rivers:
   p=self.transform(line,z)
   rd.line(p,fill='#bad7d9',width=round(6+2*z),joint='curve')
   rd.line(p,fill='#609bb0',width=round(3+z),joint='curve')
  layer.putalpha(ImageChops.multiply(layer.getchannel('A'),self.river_mask(z)))
  im.paste(layer,(0,0),layer)
  if labels:
   for s,lon,lat in [('黄河',110,39.3),('长江',112.7,29.3)]:
    x,y=self.point(lon,lat,z)
    if 100<x<1800 and 160<y<870:self.text(im,s,x,y,32,'#477f99',True)
   if z>.95:
    for s,lon,lat in [('浙江',120,29.3),('福建',117.5,25.8),('江西',115.5,27.5),('安徽',117,32),('江苏',120,33.1),('广东',113.2,23.8)]:
     x,y=self.point(lon,lat,z)
     if 110<x<1800 and 210<y<860:self.text(im,s,x,y,32,'#777e72',True)

 def background(self,z):
  im=self.paper.copy();d=ImageDraw.Draw(im)
  for poly in self.geometries:
   p=self.transform(poly,z);d.polygon(p,fill='#e2e5d0');d.line(p+[p[0]],fill='#b8c4b4',width=2,joint='curve')
  # China uses the original coordinate source and is the main focus, with neutral neighbours.
  for poly in self.china:
   p=self.transform(poly,z);d.polygon(p,fill='#f5e9c8');d.line(p+[p[0]],fill='#7e9691',width=3,joint='curve')
  # Delicate irregular watercolor grain, clipped to land rather than changing the border.
  texture=Image.new('RGBA',im.size);td=ImageDraw.Draw(texture)
  for k,(lon,lat,rx,ry) in enumerate([(85,41,130,90),(90,31,160,78),(104,38,130,110),(113,28,120,70),(125,46,80,120)]):
   x,y=self.point(lon,lat,z)
   td.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(216,186,124,36))
   td.ellipse((x-rx*.7,y-ry*.6,x+rx*.3,y+ry*.9),fill=(179,195,153,20))
  texture=texture.filter(ImageFilter.GaussianBlur(35));im=Image.alpha_composite(im.convert('RGBA'),texture).convert('RGB')
  self.linework(im,z)
  return im

 def text(self,im,s,x,y,size=48,color=None,center=False):
  self.v.text(im,s,x,y,size,color or self.v.INK,center)

 def tag(self,im,s,x,y,size=46,color=None,alpha=1):
  if alpha<=0:return
  w=round(self.F(size).getlength(s)+32);h=size+24
  assert x-w/2>=15 and x+w/2<=1905,(s,x,w)
  before=im.crop((round(x-w/2-2),round(y-2),round(x+w/2+2),round(y+h+2))) if alpha<1 else None
  self.v.tag(im,s,x,y,size,color or self.v.INK)
  if before:
   rect=(round(x-w/2-2),round(y-2),round(x+w/2+2),round(y+h+2));after=im.crop(rect);im.paste(Image.blend(before,after,alpha),(rect[0],rect[1]))

 def right_card(self,im,first,second,y,large,small,color=None):
  cx=1680;w=max(self.F(large).getlength(first),self.F(small).getlength(second))+48
  box=(round(cx-w/2),y,round(cx+w/2),y+large+small+58)
  assert box[0]>=15 and box[2]<=1905,(first,second,box)
  ImageDraw.Draw(im).rounded_rectangle(box,18,fill='#fffaf0',outline='#c4d6d5',width=1)
  self.text(im,first,cx,y+16,large,color,True)
  self.text(im,second,cx,y+large+32,small,color,True)

 def heat(self):
  yy,xx=np.mgrid[0:270,0:480];xx=xx*4;yy=yy*4;field=np.zeros(xx.shape)
  # Qualitative warm tendency, no numerical forecast scale or claimed event-year pattern.
  for lon,lat,rx,ry,weight in [(126,45,170,220,.90),(114,38,190,180,.75),(107,29,160,150,.60),(120,26,110,120,.55),(88,42,170,90,.32)]:
   x,y=self.point(lon,lat);field+=weight*np.exp(-(((xx-x)/rx)**2+((yy-y)/ry)**2)*1.8)
  field=np.clip(field*(1+.08*np.sin(xx/27)*np.sin(yy/33)),0,1)
  palette=np.array([[249,227,173],[246,191,116],[240,144,79],[222,99,64],[185,65,56]])
  rgb=np.stack([np.interp(field,np.linspace(0,1,5),palette[:,j]) for j in range(3)],axis=2)
  alpha=np.clip(field*240,0,225)
  a=Image.fromarray(np.uint8(np.dstack([rgb,alpha]))).resize((1920,1080),Image.Resampling.BICUBIC)
  a.putalpha(ImageChops.multiply(a.getchannel('A'),self.mask));return a

 def cold_layer(self,u):
  yy,xx=np.mgrid[0:270,0:480];xx=xx*4;yy=yy*4;field=np.zeros(xx.shape)
  for lon,lat,weight in [(115,49-23*u,1),(124,46-20*u,.65),(104,45-17*u,.60)]:
   x,y=self.point(lon,lat);field+=weight*np.exp(-(((xx-x)/175)**2+((yy-y)/160)**2)*1.1)
  field=(1-np.exp(-field))*(1+.11*np.sin(xx/37+yy/29)*np.sin(yy/43))
  field=np.clip(field,0,1)
  palette=np.array([[205,229,234],[151,198,219],[102,160,196],[70,125,168]])
  rgb=np.stack([np.interp(field,np.linspace(0,1,4),palette[:,j]) for j in range(3)],axis=2)
  a=Image.fromarray(np.uint8(np.dstack([rgb,field*226]))).resize((1920,1080),Image.Resampling.BICUBIC)
  a.putalpha(ImageChops.multiply(a.getchannel('A'),self.mask));return a

 def inset(self,im):
  box=(1698,741,1890,942);layer=Image.new('RGB',(192,201),'#e2eff0');d=ImageDraw.Draw(layer)
  for poly in self.v.G:
   p=[((lon-105)/20*184+4,(25-lat)/23*182+5) for lon,lat in poly[0]]
   d.polygon(p,fill='#f4e8c8');d.line(p+[p[0]],fill='#9aafa8',width=1)
  im.paste(layer,(1698,741));ImageDraw.Draw(im).rounded_rectangle(box,10,outline='#9eb8b6',width=2)
  self.text(im,'南海诸岛',1794,901,25,center=True)
  self.audit.append(dict(kind='south_china_sea_inset',box=list(box)))

 def geography(self,im,z=0):
  if 20<=self.t<31:
   for s,lon,lat in [('中国东南沿海',117,33.5),('日本',140,38),('菲律宾',123,14),('西北太平洋',144,27)]:
    x,y=self.point(lon,lat,z)
   if 190<x<1740 and 280<y<890:self.text(im,s,x,y,40,'#648b91',True)
  elif self.t<14:
   x,y=self.point(139,38);self.text(im,'日本',x,y,36,'#92aaa4',True)

 def rain(self,im,t):
  q=self.E((t-4.6)/1.1)*(1-self.E((t-19.15)/.85))
  # Layered organic rain belt; moving particles and clouds establish the water transport.
  belt=Image.new('RGBA',im.size);d=ImageDraw.Draw(belt)
  line=[self.point(lon,30.2+.5*math.sin(lon*.6)) for lon in np.linspace(105,123,80)]
  polygon=[(x,y-38-5*math.sin(i*.2+t*.2)) for i,(x,y) in enumerate(line)]+[(x,y+40+5*math.sin(i*.24)) for i,(x,y) in reversed(list(enumerate(line)))]
  d.polygon(polygon,fill=(74,153,180,116));belt=belt.filter(ImageFilter.GaussianBlur(16));belt.putalpha(ImageChops.multiply(belt.getchannel('A'),self.mask));self.v.composite(im,belt,q)
  for j,coords in enumerate([[(129,18),(128,24),(121,28),(116,30)],[(114,17),(114,23),(110,27),(111,30)]]):
   path=self.v.b.o.p.native.v.cubic(*[self.point(*p) for p in coords],100)
   progress=self.E((t-4.2-j*.25)/2.3);limit=round(progress*99)
   breeze=Image.new('RGBA',im.size);bd=ImageDraw.Draw(breeze)
   for k in range(1,limit):
    if (k//5)%2==0:bd.line([path[k-1],path[k]],fill='#47776d',width=5)
   if limit>8:self.v.arrow(breeze,path[max(0,limit-8):limit+1],1,'#8eaa9a',3)
   for k in range(7):
    u=(t*.22+k/7)%1
    if u>progress:continue
    x,y=path[round(u*99)];bd.ellipse((x-4,y-4,x+4,y+4),fill='#fff9e9',outline='#47776d',width=2)
   self.v.composite(im,breeze,q*.8)
  for j,lon in enumerate([109,115,120]):
   x,y=self.point(lon,30.7);self.v.cloud(im,x,y-48+math.sin(t+j)*2,.72,q)
   if q>.05:
    d=ImageDraw.Draw(im)
    for k in range(6):
     rx=x-43+k*17;ry=y+((t*74+k*19+j*17)%53);d.line((rx,ry,rx-5,ry+13),fill='#6fa6bf',width=3)
    for k in range(2):
     r=(t*18+k*12)%22;d.arc((x-25-r,y+64-r/4,x-25+r,y+64+r/4),0,340,fill='#7fb0c2',width=2)
  if 5.7<t<11.7:
   target=self.point(113.8,30.2);d=ImageDraw.Draw(im)
   d.line([(770,737),(782,711),target],fill='#fff9e9',width=9,joint='curve')
   d.line([(770,737),(782,711),target],fill='#2c7187',width=5,joint='curve')
   d.ellipse((target[0]-6,target[1]-6,target[0]+6,target[1]+6),fill='#2c7187',outline='#fff9e9',width=2)
   self.tag(im,'长江中下游',680,738,46,self.v.BLUE)
  if 7<t<9.8:self.tag(im,'降水偏多的可能增加',740,831,44,self.v.BLUE)
  if 9.8<=t<11.85:
   x,y=self.point(115,38);lay=Image.new('RGBA',im.size);ld=ImageDraw.Draw(lay);ld.ellipse((x-95,y-75,x+100,y+75),fill=(215,162,83,98));lay=lay.filter(ImageFilter.GaussianBlur(22));lay.putalpha(ImageChops.multiply(lay.getchannel('A'),self.mask));self.v.composite(im,lay,self.E((t-9.8)/.35)*(1-self.E((t-11.45)/.4)))
   self.tag(im,'部分地区可能偏旱',x-20,y-120,42,'#bf8d56')
  if 11.95<=t<19.6:
   a=self.E((t-11.95)/1.2)*(1-self.E((t-18.9)/.7))
   lay=Image.new('RGBA',im.size);d=ImageDraw.Draw(lay)
   for coords,line in self.yangtze:
    if max(p[0] for p in coords)<110:continue
    p=self.transform(line,0);d.line(p,fill='#a5d0d5',width=9,joint='curve');d.line(p,fill='#4a95ae',width=4,joint='curve')
   lay.putalpha(ImageChops.multiply(lay.getchannel('A'),self.mask));self.v.composite(im,lay,a*.72)
   self.audit.append(dict(kind='flood_risk_river_highlight',alpha=a))
  if t>=14.35:self.flood(im,t)

 def flood(self,im,t):
  fade=1-self.E((t-19.65)/.35)
  coords=min((c for raw,_ in self.yangtze for c in raw),key=lambda c:(c[0]-110)**2+(c[1]-31)**2)
  source=self.point(*coords);end=(1001,590)
  path=self.v.b.o.p.native.v.cubic(source,(source[0]+65,source[1]+50),(955,660),end,100)
  lay=im.copy();self.v.arrow(lay,path,self.E((t-14.35)/.85),'#8c9e91',3)
  im.paste(Image.blend(im,lay,fade),(0,0))
  q=self.E((t-15.75)/.85)*fade
  if q<=0:return
  lay=im.copy();d=ImageDraw.Draw(lay);offset=round(12*(1-self.E((t-15.75)/.85)))
  # Thin photo edge; captions have their own clear space to the left of the inset.
  d.rounded_rectangle((1000+offset,147,1896+offset,735),12,fill='#fffaf0',outline='#a9bdb8',width=2)
  lay.paste(self.photo,(1008+offset,155))
  d.rounded_rectangle((1000,744,1680,875),12,fill='#fffaf0')
  self.text(lay,'1998年·长江洪水',1040,756,60)
  self.text(lay,'湖北嘉鱼抗洪｜新华社资料照片',1040,836,29,'#6e898d')
  im.paste(Image.blend(im,lay,q),(0,0));self.audit.append(dict(kind='historical_photo',box=[1008+offset,155,1888+offset,727],source='Xinhua 1998 Jiayu',native_size=[1024,666],alpha=q))

 def cyclone(self,im,x,y,t,size=1,opacity=1):
  # Reuse the existing smooth rotating cloud bands, on a pale cloud haze.
  layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer);r=125*size
  d.ellipse((x-r,y-r*.8,x+r,y+r*.8),fill=(235,246,244,50));layer=layer.filter(ImageFilter.GaussianBlur(13));self.v.composite(im,layer,opacity)
  self.v.cyclone(im,x,y,t,.62*size,opacity)

 def typhoon(self,im,t,z):
  q=self.E((t-20.65)/.65)*(1-self.E((t-30.3)/.7))
  # The storm starts offshore on the right. A single uninterrupted northwestward track.
  # Camera focus finishes before the storm begins travelling; no eastward relocation.
  start=(1580,630);end=(1260,390)
  u=self.E((t-22)/7.5)
  path=self.v.b.o.p.native.v.cubic(start,(1500,610),(1360,485),end,180)
  k=u*(len(path)-1);i=min(len(path)-2,int(k));f=k-i
  cx=path[i][0]*(1-f)+path[i+1][0]*f;cy=path[i][1]*(1-f)+path[i+1][1]*f
  if u>0:self.v.arrow(im,path,u,'#6897a7',5)
  self.cyclone(im,cx,cy,t,1.12*(.7+.40*self.E((t-24.9)/2.5)),q)
  if t<24.8:self.right_card(im,'生成位置','偏东、偏南',240,72,60,self.v.BLUE)
  elif t<27.6:self.right_card(im,'海上时间更长','部分台风更易增强',240,62,48,self.v.BLUE)
  else:self.right_card(im,'强度与登陆地点','仍看具体环境',240,54,54)
  self.audit.append(dict(kind='typhoon',center=[cx,cy],regional_view=z,map_scale=1+z,projection='equirectangular_35N',direction='northwest',opacity=q))

 def winter(self,im,t):
  cold=self.E((t-35.6)/1.7)*(1-self.E((t-38.4)/2.2))
  envelope=self.E((t-31)/.6)*(1-self.E((t-40.4)/.6))
  self.v.composite(im,self.warm,(.95-.74*cold)*envelope)
  age=self.E((t-35.6)/3.2)*20;k=min(19,int(age));frac=min(1,age-k)
  if cold>.001:self.v.composite(im,Image.blend(self.colds[k],self.colds[k+1],frac),cold)
  self.linework(im)
  if t<35.6:self.right_card(im,'整体偏暖','地区有差异',240,72,60,'#bd7453')
  elif t<39:self.right_card(im,'冷空气南下','阶段性降温',240,72,60,'#5688ad')
  else:self.right_card(im,'冷空气减弱','气温回升',240,72,60,'#bd7453')
  if cold>.02:
   coords=[(117,49),(116,44),(113,37),(111,29)];path=self.v.b.o.p.native.v.cubic(*[self.point(*p) for p in coords],100)
   self.v.arrow(im,path,self.E((t-35.6)/2.3),'#79aac5',10)
   for j in range(11):
    u=(t*.13+j/11)%1
    if u>self.E((t-35.6)/2.3):continue
    sx,sy=path[round(u*99)];self.v.snow(im,sx+35*math.sin(j*2),sy+10*math.sin(t+j),6)
  # A qualitative palette only, without invented degree values.
  d=ImageDraw.Draw(im)
  for j,col in enumerate(['#689ab9','#b2d2df','#f5d391','#ec9b63','#cd6750']):d.rounded_rectangle((1490+j*78,478,1558+j*78,506),5,fill=col)
  self.text(im,'偏冷',1490,520,40,'#618aa1');self.text(im,'偏暖',1790,520,40,'#b27956')
  return cold

 def character(self,im,t,name,entry=1,exit=0):
  rig=self.rigs[name];a=rig['image'].copy();s=rig['scale'];mx,my=rig['mouth'];foot=rig['foot']
  if name=='fan':
   angle=13*math.sin((t-31.2)*2*math.pi*2.6)
   a.alpha_composite(self.fan.rotate(angle,resample=Image.Resampling.BICUBIC,center=(967,714),expand=False))
  # Matching source mouth region, compressed during pauses; speech uses the existing RMS rhythm.
  rms=0  # Weather vignette: the character is reacting, not presenting or lip-syncing.
  if rms<.012 and name!='cold':
   d=ImageDraw.Draw(a);skin=tuple(a.getpixel((min(a.width-1,mx+50),my-18)))
   if skin[3]<220:skin=(255,213,193,255)
   d.ellipse((mx-33,my-32,mx+34,my+32),fill=skin);d.arc((mx-22,my-10,mx+22,my+10),0,180,fill='#865453',width=5)
  image=a.resize((round(a.width*s),round(a.height*s)),Image.Resampling.LANCZOS)
  px=1680-mx*s;py=944-foot*s+math.sin(t*2)*1.2
  actual=image.getbbox();px=min(px,1886-actual[2])
  px+=410*(1-entry)+410*exit
  if name=='cold':px+=2.8*math.sin(t*2*math.pi*7);py+=1.7*math.sin(t*2*math.pi*8)
  if entry<1 or exit>0:py-=abs(math.sin(t*15))*4
  im.paste(image,(round(px),round(py)),image)
  if name=='rain':
   opening=self.E((t-3.6)/.7)*(1-self.E((t-14.65)/.35));canopy=self.v.umbrella_art(opening,t)
   ux=px+350*s;uy=py+250*s;im.paste(canopy,(round(ux-240),round(uy-88)),canopy)
   if opening>.7:
    d=ImageDraw.Draw(im)
    for j in range(16):
     rx=ux-205+j*28;ry=uy-205+((t*125+j*27)%110);d.line((rx,ry,rx-5,ry+13),fill='#6d9fb5',width=3)
    for side in [-1,1]:
     for j in range(3):
      rx=ux+side*220;ry=uy+40+((t*85+j*29)%75);d.ellipse((rx-2,ry,rx+2,ry+6),fill='#82b4bf')
  if name=='cold':
   d=ImageDraw.Draw(im)
   for side in [-1,1]:
    x=1680+side*125;ys=735+math.sin(t*12)*3
    d.line([(x+5*math.sin(j*.8+t*10),ys+j*7) for j in range(8)],fill='#7ba1b5',width=3)
  if name=='fan':
   d=ImageDraw.Draw(im)
   for j in range(2):d.arc((1730-j*12,640+j*26,1840-j*12,695+j*26),160,275,fill='#7eb3bf',width=2)
   # Small animated sweat beads support the warm expression without changing the face.
   for j in range(2):
    sx=px+(mx+105+j*30)*s;sy=py+(my-105)*s+((t*18+j*14)%30)
    d.ellipse((sx-3,sy,sx+3,sy+10),fill='#b5dbe4',outline='#7fadb9',width=1)
  visible=px+actual[0]<1919 and px+actual[2]>0
  if visible:self.audit.append(dict(kind='character',pose=name,walking=entry<1 or exit>0,box=[px+actual[0],py+actual[1],px+actual[2],py+actual[3]],rigged_prop=name=='fan'))
  return visible,entry>=1 and exit==0

 def map_character(self,im,t,name,alpha=1):
  layer=Image.new('RGBA',im.size)
  self.character(layer,t,name)
  self.audit=[o for o in self.audit if o['kind']!='character']
  crop=layer.crop((1320,260,1910,955));scale=.52
  crop=crop.resize((round(crop.width*scale),round(crop.height*scale)),Image.Resampling.LANCZOS)
  gx,gy=self.point(118,27.4)
  px=round(gx-(1680-1320)*scale);py=round(gy-(944-260)*scale)
  if name=='rain':
   puddle=Image.new('RGBA',im.size);d=ImageDraw.Draw(puddle)
   d.ellipse((gx-82,gy-9,gx+74,gy+12),fill='#a5cbd0',outline='#76a8b2',width=2)
   self.v.composite(im,puddle,alpha)
  crop.putalpha(crop.getchannel('A').point(lambda x:round(x*alpha)))
  im.paste(crop,(px,py),crop)
  self.audit.append(dict(kind='weather_character',pose=name,anchor='Jiangnan',box=[px,py,px+crop.width,py+crop.height],alpha=alpha))

 def bubble(self,im,words):
  # Retain 46px original size and shared baselines; use compact clauses beside the actor.
  self.v.bubble(im,words)

 def frame(self,t):
  self.t=t;self.v.AUDIT=[];self.audit=[]
  z=self.E((t-20)/1.1)*(1-self.E((t-30)/1)) if 20<=t<31 else 0
  im=self.main.copy() if z<=0 else self.zoom.copy() if z>=1 else self.background(z)
  self.geography(im,z)
  if t<3.5:
   path=self.v.b.o.p.native.v.cubic(*[self.point(*p) for p in [(140,25),(133,28),(126,31),(120,33)]],100);self.v.flow(im,path,t,self.E((t-.2)/2.1))
  if 3.8<=t<20:self.rain(im,t)
  if 20<=t<31:self.typhoon(im,t,z)
  if 31<=t<41:self.winter(im,t)
  if t>=41:
   for j,(x,s) in enumerate([(1245,'降水'),(1480,'台风'),(1725,'气温')]):
    q=self.E((t-41-j*.28)/.45)
    if not q:continue
    if j==0:
     self.v.cloud(im,x,450,.8,q);d=ImageDraw.Draw(im)
     for k in range(5):d.line((x-36+k*20,488,x-42+k*20,504),fill='#71a6bc',width=3)
    elif j==1:self.cyclone(im,x,450,t,.6,q)
    else:self.v.thermometer(im,x,450,34)
    self.text(im,s,x,610,46,center=True)
   self.tag(im,'关注预报，科学应对',1480,746,47)
  if 3.8<=t<15.1:self.map_character(im,t,'rain',self.E((t-3.8)/.5)*(1-self.E((t-14.65)/.45)))
  if 31<=t<41:
   blend=self.E((t-35.62)/.44)*(1-self.E((t-39.02)/.46));alpha=self.E((t-31)/.30)*(1-self.E((t-40.6)/.4))
   if blend<=0:self.map_character(im,t,'fan',alpha)
   elif blend>=1:self.map_character(im,t,'cold',alpha)
   else:
    original=im.copy();self.map_character(im,t,'fan',alpha);self.map_character(original,t,'cold',alpha);im=Image.blend(im,original,blend)
  row=next((r for r in self.v.M['lines'] if r['start']<=t<r['speech_end']),None)
  if row:
   words=self.v.current_clause(row,t)
   self.v.b.o.subtitle(im,words);self.audit.append(dict(kind='subtitle',text=words,box=[0,958,1920,1080]))
  self.inset(im);im.paste(self.header,(16,14),self.header)
  period='次年夏季·部分事件' if t<20 else '发展期·生成位置变化' if t<31 else '冬季·冷暖变化示意' if t<41 else '因事件、地区而异'
  width=self.F(60).getlength(period)+32
  self.tag(im,period,1885-width/2,28,60)
  self.v.AUDIT.extend(self.audit)
  return im

def install(v):
 from paper_watercolor import PaperScene
 scene=PaperScene(v);v.frame=scene.frame;v.REFINED=scene
