"""Paper atlas art direction over the existing, unchanged geographic animation.

The generated asset contains pigment and paper only. All mapped boundaries,
rivers, projection, actor rigs, narration, and timing remain native source data.
"""
from functools import lru_cache
import math,json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from refine_scene import Scene

INK = '#173f50'
SEPIA = '#887e60'

@lru_cache(None)
def brush(size):
 return ImageFont.truetype('C:/Windows/Fonts/STXINGKA.TTF', round(size))

@lru_cache(None)
def note(size):
 return ImageFont.truetype('C:/Windows/Fonts/simkai.ttf', round(size))

class PaperScene(Scene):
 def __init__(self,v):
  # Initialize textures before the parent builds its two fixed camera views.
  self.R=v.R
  scan=Image.open(self.R/'素材/纸本水彩_蓝色海洋原料.png').convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS)
  self.scan=np.asarray(scan,dtype=np.float32)
  rng=np.random.default_rng(730)
  fine=rng.normal(0,.72,(1080,1920)).astype(np.float32)
  def noise(w,h):
   a=Image.fromarray(np.uint8(rng.uniform(55,201,(h,w))))
   return (np.asarray(a.resize((1920,1080),Image.Resampling.BICUBIC),dtype=np.float32)-128)/72
  self.pigment=noise(47,27)*.40+noise(123,69)*.23+noise(384,216)*.12
  self.fine=fine
  base=np.empty((1080,1920,3),dtype=np.float32);base[:]=[248,242,224]
  base+=self.pigment[:,:,None]*2.3+fine[:,:,None]
  self.stock=Image.fromarray(np.uint8(np.clip(base,0,255)))
  sea=np.asarray(Image.blend(self.stock,scan,.73),dtype=np.float32)
  self.ocean=Image.fromarray(np.uint8(sea))
  # Same wash coordinates are used for every frame; pigment never boils.
  self.land_wash=self.make_land([240,220,166],12)
  self.neighbour_wash=self.make_land([211,216,187],17)
  self.granulation=Image.fromarray(np.uint8(np.clip(220+self.pigment*42+fine*3,145,255)))
  super().__init__(v)
  self.header=self.header_art()
  self.v.b.o.subtitle=self.subtitle
  self.v.INK=INK
  self.v.BLUE='#3c8ba6'
  self.v.ORANGE='#c27b4f'
  self.original_arrow=v.arrow
  self.v.arrow=self.strong_arrow
  features=json.loads((self.R/'素材/中国省界参考.json').read_text(encoding='utf-8'))['features']
  jd=next(f for f in features if f['properties'].get('adcode')=='100000_JD')
  self.inset_land_rings=[]
  for feature in features:
   if feature['properties'].get('adcode')=='100000_JD':continue
   geom=feature['geometry'];polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
   self.inset_land_rings.extend(p[0] for p in polys)
  self.south_sea_dashes=[p[0] for p in jd['geometry']['coordinates'] if max(c[1] for c in p[0])<22]
  assert len(self.south_sea_dashes)==9
  self.redraw_cloud()

 def point(self,lon,lat,z=0):
  x,y=super().point(lon,lat,z);s=1+.05*(1-z)
  return 900+(x-900)*s,952+(y-957.45)*s

 def transform(self,points,z):
  p=np.asarray(super().transform(points,z));s=1+.05*(1-z)
  p[:,0]=900+(p[:,0]-900)*s;p[:,1]=952+(p[:,1]-957.45)*s
  return [tuple(q) for q in p]

 def strong_arrow(self,im,path,progress=1,color=None,width=6):
  if len(path)<3 or progress<=0:return
  # Paper halo separates the complete trajectory from watercolor pigment.
  w=max(6,round(width*1.45))
  ink='#266b83'
  if color in ('#8c9e91','#8eaa9a'):ink='#446f60'
  if color=='#8c9e91':ink='#916b37'
  self.original_arrow(im,path,progress,'#fff9e9',w+4)
  self.original_arrow(im,path,progress,ink,w)
  self.audit.append(dict(kind='teaching_arrow',width=w,halo=w+4,color=ink))

 def make_land(self,color,strength):
  a=np.empty((1080,1920,3),dtype=np.float32);a[:]=color
  # Transparent earthy underpainting with small dry-brush variation.
  p=self.pigment*strength+self.fine*.9
  a+=p[:,:,None]*np.array([.62,.85,1.05])[None,None,:]
  yy,xx=np.mgrid[0:1080,0:1920]
  for cx,cy,rx,ry,shade in [(470,380,210,130,[12,-2,-22]),(820,570,180,160,[-10,2,-8]),(1150,310,150,190,[-12,0,-12]),(900,780,220,90,[10,-3,-16])]:
   bloom=np.exp(-(((xx-cx)/rx)**2+((yy-cy)/ry)**2)*1.6)
   bloom*=np.clip(1+self.pigment*.7,.4,1.6)
   a+=bloom[:,:,None]*np.array(shade)[None,None,:]
  return Image.fromarray(np.uint8(np.clip(a,0,255)))

 def background(self,z):
  im=self.ocean.copy()
  world=Image.new('L',im.size);china=Image.new('L',im.size)
  wd=ImageDraw.Draw(world);cd=ImageDraw.Draw(china)
  for poly in self.geometries:wd.polygon(self.transform(poly,z),fill=255)
  for poly in self.china:cd.polygon(self.transform(poly,z),fill=255)
  # No displaced or invented coastline: soft pigment lies inside the exact mask.
  im.paste(self.neighbour_wash,(0,0),world)
  im.paste(self.land_wash,(0,0),china)
  edge=ImageChops.subtract(china,china.filter(ImageFilter.MinFilter(5)))
  edge=edge.point(lambda p:round(p*.22));im.paste('#a98c57',(0,0),edge)
  d=ImageDraw.Draw(im)
  for poly in self.geometries:
   p=self.transform(poly,z);d.line(p+[p[0]],fill='#a3ac92',width=2,joint='curve')
  for poly in self.china:
   p=self.transform(poly,z);d.line(p+[p[0]],fill=SEPIA,width=2,joint='curve')
  self.linework(im,z)
  return im

 def text(self,im,s,x,y,size=48,color=None,center=False):
  if s=='日本':return
  if s in ('偏冷','偏暖'):
   size=44;f=self.v.F(size);width=f.getlength(s);xx=x-width/2 if center else x
   d=ImageDraw.Draw(im);d.rounded_rectangle((xx-10,y-6,xx+width+10,y+size+12),8,fill='#fff9e9')
   d.text((xx,y),s,font=f,fill='#234e68' if s=='偏冷' else '#99472e',anchor='lt')
   self.v.AUDIT.append(dict(kind='text',text=s,box=[xx,y,xx+width,y+size],style='opaque high-contrast legend'))
   return
  # Handwritten atlas notes; body subtitles retain the original reading font.
  f=note(size);width=f.getlength(s);xx=x-width/2 if center else x
  assert 15<=xx and xx+width<=1905 and 10<=y and y+size<=1067,(s,xx,y,width)
  ImageDraw.Draw(im).text((xx,y),s,font=f,fill=color or INK,anchor='lt',stroke_width=0)
  self.v.AUDIT.append(dict(kind='text',text=s,box=[round(xx,1),y,round(xx+width,1),y+size],style='atlas handwritten'))

 def swash(self,im,box,color,alpha=70):
  x,y,r,b=box
  a=Image.new('RGBA',im.size);d=ImageDraw.Draw(a)
  # A quiet double stroke, rather than a UI rectangle or moving emphasis circle.
  points=[(x+5,y+3),(r-4,y),(r,b-3),(r-22,b),(x,b-1)]
  d.polygon(points,fill=color)
  a.putalpha(ImageChops.multiply(a.getchannel('A'),self.granulation).point(lambda v:round(v*alpha/255)))
  im.paste(a,(0,0),a)

 def tag(self,im,s,x,y,size=46,color=None,alpha=1):
  if alpha<=0:return
  w=note(size).getlength(s)+28;h=size+24
  x=max(20+w/2,min(x,1890-w/2))
  assert x-w/2>=15 and x+w/2<=1905,(s,x,w)
  original=im.copy() if alpha<1 else None
  # Pale paper mat restores contrast without the repeated rounded-box look.
  box=(round(x-w/2),round(y-3),round(x+w/2),round(y+h))
  mat=self.stock.crop(box);mask=Image.new('L',mat.size,228)
  im.paste(mat,(box[0],box[1]),mask)
  self.swash(im,(x-w/2+8,y+size+9,x+w/2-8,y+size+18),'#d6af65',55)
  self.text(im,s,x,y+6,size,color or INK,True)
  if original:im.paste(Image.blend(original,im,alpha),(0,0))

 def right_card(self,im,first,second,y,large,small,color=None):
  cx=1680;f1=brush(large);f2=note(small)
  w=max(f1.getlength(first),f2.getlength(second))+40
  assert cx-w/2>=15 and cx+w/2<=1905,(first,second,w)
  box=(round(cx-w/2-4),y-6,round(cx+w/2+4),y+large+small+60)
  # The teaching notes have their own open paper margin, not a mini whiteboard.
  mat=self.stock.crop(box);im.paste(mat,(box[0],box[1]),Image.new('L',mat.size,235))
  d=ImageDraw.Draw(im)
  d.text((cx,y+12),first,font=f1,anchor='mt',fill=color or INK)
  self.swash(im,(cx-w/2+20,y+large+22,cx+w/2-20,y+large+40),'#d6af65',85)
  self.text(im,second,cx,y+large+34,small,color or INK,True)
  self.audit.append(dict(kind='text',text=first,box=[cx-f1.getlength(first)/2,y+12,cx+f1.getlength(first)/2,y+large+12],style='brush teaching emphasis'))

 def header_art(self):
  # Compact original title footprint and 57px size; handmade type replaces UI trim.
  a=self.stock.crop((0,0,675,144)).convert('RGBA');a.putalpha(245)
  d=ImageDraw.Draw(a);s='厄尔尼诺·对中国的影响';f=brush(57)
  d.text((17,16),s,font=f,anchor='lt',fill=INK)
  d.line([(17,86),(170,84),(346,87),(641,83)],fill='#c9a45e',width=4)
  d.text((19,104),'降水 / 台风 / 冬季气温',font=note(30),anchor='lt',fill='#597c85')
  return a

 def subtitle(self,im,words):
  # Same words, 46px original font and time windows, now printed on ivory paper.
  im.paste(self.stock.crop((0,958,1920,1080)),(0,958))
  d=ImageDraw.Draw(im);d.line([(36,958),(1884,958)],fill='#c9c0a4',width=1)
  lines=self.v.b.o.wrap(words,46,1750)
  assert len(lines)<=2,(words,lines)
  y=965 if len(lines)>1 else 987
  for s in lines:
   self.v.b.o.txt(im,s,960,y,46,INK,True);y+=54

 def heat(self):
  a=super().heat();a.putalpha(ImageChops.multiply(a.getchannel('A'),self.granulation));return a

 def cold_layer(self,u):
  a=super().cold_layer(u);a.putalpha(ImageChops.multiply(a.getchannel('A'),self.granulation));return a

 def redraw_cloud(self):
  original=self.v.CLOUD
  a=np.asarray(original,dtype=np.float32).copy();mask=a[:,:,3].copy()
  yy,xx=np.mgrid[0:a.shape[0],0:a.shape[1]]
  shade=np.clip((yy-30)/210,0,1)
  rgb=np.stack([251-49*shade,248-34*shade,232-6*shade],axis=2)
  rng=np.random.default_rng(12);rgb+=rng.normal(0,1.1,yy.shape)[:,:,None]
  inside=(a[:,:,0]>180)&(mask>0)
  a[:,:,:3]=np.where(inside[:,:,None],rgb,a[:,:,:3])
  self.v.CLOUD=Image.fromarray(np.uint8(np.clip(a,0,255)))

 def inset(self,im):
  # Isolated cartographic plate: its own pale sea, nine sourced dashes, separate caption.
  box=(1698,741,1900,944);ss=3;layer=Image.new('RGB',(202*ss,203*ss),'#fff9e9');d=ImageDraw.Draw(layer)
  d.rectangle((7*ss,7*ss,195*ss,149*ss),fill='#e1eff0')
  def pt(lon,lat):return ((lon-105)/20*180+11)*ss,((25-lat)/23*142+8)*ss
  land=Image.new('RGBA',layer.size);ld=ImageDraw.Draw(land)
  for ring in self.inset_land_rings:
   p=[pt(lon,lat) for lon,lat in ring]
   ld.polygon(p,fill='#ead5a0');ld.line(p+[p[0]],fill='#7a8062',width=2)
   lons=[c[0] for c in ring];lats=[c[1] for c in ring]
   if max(lons)-min(lons)<.25 and max(lats)-min(lats)<.25:
    x,y=pt(sum(lons)/len(lons),sum(lats)/len(lats))
    if 8*ss<x<194*ss and 8*ss<y<154*ss:ld.ellipse((x-2,y-2,x+2,y+2),fill='#667659')
  clip=Image.new('L',layer.size);ImageDraw.Draw(clip).rectangle((7*ss,7*ss,195*ss,149*ss),fill=255)
  land.putalpha(ImageChops.multiply(land.getchannel('A'),clip));layer.paste(land,(0,0),land)
  d=ImageDraw.Draw(layer)
  for ring in self.south_sea_dashes:
   # Centerlines derived from the actual narrow boundary polygons; no invented placements.
   p=np.array(ring);axis=np.linalg.svd(p-p.mean(axis=0),full_matrices=False)[2][0]
   u=(p-p.mean(axis=0))@axis;centres=[]
   for a,b in zip(np.linspace(u.min()-.0001,u.max()+.0001,8)[:-1],np.linspace(u.min()-.0001,u.max()+.0001,8)[1:]):
    group=p[(u>=a)&(u<b)]
    if len(group):centres.append(pt(*group.mean(axis=0)))
   d.line(centres,fill='#fff9e9',width=10,joint='curve');d.line(centres,fill='#344e60',width=6,joint='curve')
  d.line((10*ss,153*ss,192*ss,153*ss),fill='#c1b28e',width=2)
  layer=layer.resize((202,203),Image.Resampling.LANCZOS)
  im.paste(layer,(1698,741));d=ImageDraw.Draw(im);d.rectangle(box,outline='#576e72',width=3)
  f=self.v.F(34);s='南海诸岛';d.text((1799,900),s,font=f,anchor='mt',fill=INK)
  self.audit.append(dict(kind='text',text=s,box=[1799-f.getlength(s)/2,900,1799+f.getlength(s)/2,934],style='inset caption on opaque paper'))
  self.audit.append(dict(kind='south_china_sea_inset',box=list(box),sourced_dashes=9,background='opaque pale sea with separate paper caption'))

