"""Three editable 1920x1080 style frames; no modification to the course video."""
from pathlib import Path
from functools import lru_cache
import math,json
from PIL import Image,ImageDraw,ImageFont,ImageFilter

R=Path(__file__).resolve().parent;P=R.parent
INK='#244b60';BLUE='#5599b0';CORAL='#cd8563';CREAM='#fffaf0';LINE='#bdd1d3'
FONT=P/'主体课程/得意黑_大字无水印_v6/素材/SmileySans-Oblique.ttf'
BG=Image.open(P/'主体课程/正文日系2D_配音_v2/素材/日系2D水下课堂.png').convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS)
SPR=P/'企鹅小老师_教学动作素材_20261012/独立动作PNG'
AUDIT=[]
@lru_cache(None)
def f(n):return ImageFont.truetype(str(FONT),n)
def txt(im,s,x,y,size=44,color=INK,center=False):
 font=f(size);w=font.getlength(s);left=x-w/2 if center else x
 assert 20<=left and left+w<=1900 and 12<=y and y+size<=1068,(s,left,y,w)
 ImageDraw.Draw(im).text((left,y),s,font=font,anchor='lt',fill=color)
 AUDIT.append(dict(text=s,box=[left,y,left+w,y+size]))
def rect(im,b,fill=CREAM,outline=LINE,r=22,width=2):ImageDraw.Draw(im).rounded_rectangle(b,r,fill=fill,outline=outline,width=width)
def paper(im,b,fill=CREAM):
 shadow=Image.new('RGBA',im.size);ImageDraw.Draw(shadow).rounded_rectangle((b[0]+4,b[1]+8,b[2]+4,b[3]+8),24,fill=(40,75,85,26))
 shadow=shadow.filter(ImageFilter.GaussianBlur(10));im.paste(shadow,(0,0),shadow);rect(im,b,fill)
def header(im,title,sub):
 w=max(f(57).getlength(title)+94,f(30).getlength(sub)+75)
 paper(im,(22,20,22+w,154));d=ImageDraw.Draw(im)
 d.line((46,52,46,107),fill=BLUE,width=3)
 txt(im,title,66,43,57);txt(im,sub,67,113,30,'#6b96a6')
 for j in range(2):d.line([(w-21+k*4,64+j*12+4*math.sin(k*.6)) for k in range(13)],fill='#8eb8c6',width=2)
def sprite(im,path,box):
 a=Image.open(path).convert('RGBA');bb=a.getbbox();a=a.crop(bb);scale=min(box[2]/a.width,box[3]/a.height)
 a=a.resize((round(a.width*scale),round(a.height*scale)),Image.Resampling.LANCZOS)
 x=round(box[0]+(box[2]-a.width)/2);y=round(box[1]+box[3]-a.height)
 im.paste(a,(x,y),a);return x,y,scale,bb
def bubble(im,words,box,tip,size=44):
 x,y,r,b=box;d=ImageDraw.Draw(im);d.polygon([(x+75,b-4),(x+134,b-4),tip],fill=CREAM)
 d.line([(x+75,b-4),tip,(x+134,b-4)],fill=LINE,width=2);rect(im,box)
 lines=[];s=''
 for ch in words:
  if ch=='\n':lines.append(s);s='';continue
  if f(size).getlength(s+ch)>r-x-44:lines.append(s);s=''
  s+=ch
 if s:lines.append(s)
 yy=y+(b-y-len(lines)*(size+12))/2
 for s in lines:txt(im,s,x+22,yy,size);yy+=size+12
def wave(d,x,y,w=100,c=BLUE):
 for j in range(2):d.line([(x+i,y+j*12+7*math.sin(i/w*math.pi*3)) for i in range(w+1)],fill=c,width=4)
def icon(im,kind,cx,cy,color=BLUE,scale=1):
 d=ImageDraw.Draw(im);s=scale
 if kind==0:
  d.rounded_rectangle((cx-12*s,cy-40*s,cx+12*s,cy+28*s),12*s,fill=CREAM,outline=color,width=3)
  d.ellipse((cx-21*s,cy+12*s,cx+21*s,cy+54*s),fill=CREAM,outline=color,width=3)
  d.line((cx,cy-10*s,cx,cy+32*s),fill=CORAL,width=7);d.ellipse((cx-11*s,cy+22*s,cx+11*s,cy+44*s),fill=CORAL)
 elif kind==1:
  d.ellipse((cx-35*s,cy-37*s,cx+22*s,cy+20*s),outline=color,width=6)
  d.line((cx+16*s,cy+17*s,cx+44*s,cy+47*s),fill=color,width=9);wave(d,cx-27*s,cy-11*s,42,color)
 elif kind==2:
  for j in range(3):
   x=cx-48*s+j*34*s;d.rounded_rectangle((x,cy-33*s,x+26*s,cy+35*s),4,fill='#edf5f4',outline=color,width=3)
   d.ellipse((x+10*s,cy-18*s,x+15*s,cy-13*s),fill=color);d.ellipse((x+10*s,cy+12*s,x+15*s,cy+17*s),fill=color)
 else:
  d.rounded_rectangle((cx-35*s,cy-39*s,cx+35*s,cy+47*s),7,fill=CREAM,outline=color,width=3)
  d.rounded_rectangle((cx-16*s,cy-46*s,cx+16*s,cy-32*s),4,fill=color)
  for j in range(3):d.line((cx-20*s,cy-12*s+j*16*s,cx+21*s,cy-12*s+j*16*s),fill=color,width=3)

def road():
 im=BG.copy();header(im,'四步会诊·跟着企鹅走','从海温读数出发，一站一站找答案')
 paper(im,(78,222,1842,1000));txt(im,'跟我当一回“地球医生”',960,260,64,center=True)
 names=['测体征','查病因','追并发症','开处方'];subs=['读懂海温距平','找出海气机制','追踪连锁影响','学会科学应对'];xs=[300,740,1160,1580]
 for j,x in enumerate(xs):
  active=j==1;fill='#fbefdf' if active else '#f0f6f4'
  rect(im,(x-158,365,x+158,540),fill,CORAL if active else LINE,20,3 if active else 1)
  icon(im,j,x-93,421,CORAL if active else BLUE,.72)
  txt(im,names[j],x+28,396,49,CORAL if active else INK,True)
  txt(im,subs[j],x,482,30,'#698f9b',True)
 d=ImageDraw.Draw(im);pts=[]
 for i in range(1001):
  u=i/1000;x=171+1575*u;y=808+45*math.sin(u*math.pi*3.1+.1);pts.append((x,y))
 def band(points,width,color):
  left=[];right=[]
  for i,(x,y) in enumerate(points):
   before=points[max(0,i-1)];after=points[min(len(points)-1,i+1)]
   dx=after[0]-before[0];dy=after[1]-before[1];norm=math.hypot(dx,dy)
   nx=-dy/norm*width/2;ny=dx/norm*width/2;left.append((x+nx,y+ny));right.append((x-nx,y-ny))
  d.polygon(left+right[::-1],fill=color)
 band(pts,102,'#e0d6b8');band(pts,87,'#8dbdcb');band(pts[:365],87,'#ce996c')
 for i in range(7,len(pts)-4,17):d.line(pts[i:i+8],fill='#f8f7e8',width=4,joint='curve')
 for j,x in enumerate(xs):
  y=808+45*math.sin((x-171)/1575*math.pi*3.1+.1)
  d.ellipse((x-30,y-30,x+30,y+30),fill=CREAM,outline=CORAL if j<=1 else '#6fa4b4',width=4)
  txt(im,str(j+1),x,y-18,38,CORAL if j<=1 else '#5e91a3',True)
 # Walking pose is an existing full-body asset, not a mirrored replacement.
 sprite(im,SPR/'13_迈步A.png',(435,548,320,292))
 txt(im,'下一站：查病因',960,587,42,CORAL,True)
 for k in range(3):d.arc((491-k*15,798+k*7,540-k*15,815+k*7),165,290,fill='#bf8a5d',width=3)
 txt(im,'找机制、看影响、想应对',960,935,38,'#668d99',True)
 return im

def compare(actor=True,gloves=True):
 im=BG.copy();header(im,'辨析·不是同一个概念','厄尔尼诺与人为全球增暖')
 paper(im,(515,224,1870,1012))
 rect(im,(637,264,1165,352),'#e6f2f5','#bdd4dc',18)
 rect(im,(1230,264,1780,352),'#faeee3','#e1c4ae',18)
 txt(im,'厄尔尼诺',901,281,66,'#327f9e',True);txt(im,'人为增暖',1505,281,66,'#b96e4b',True)
 if gloves:sprite(im,R/'蓝橙拳套.png',(620,382,1170,382))
 txt(im,'自然波动',910,793,52,'#327f9e',True);txt(im,'长期趋势',1510,793,52,'#b96e4b',True)
 txt(im,'海气耦合 · 年际起伏',910,863,36,center=True);txt(im,'温室气体增加推动',1510,863,36,center=True)
 ImageDraw.Draw(im).line((680,926,1740,926),fill='#d5ded7',width=2)
 txt(im,'概念不同，风险可能共同抬高',1190,950,41,center=True)
 if actor:
  sprite(im,SPR/'06_教尺指向.png',(5,485,560,570))
  bubble(im,'先分清这两个概念，再判断影响。',(35,243,446,421),(225,515),44)
 return im

def prescription():
 im=BG.copy();header(im,'开处方·适应行动','早发现、早预警、早行动')
 # One prescription per screen, rather than two small sheets competing for attention.
 paper(im,(575,219,1810,1004))
 d=ImageDraw.Draw(im);d.rounded_rectangle((1050,200,1340,244),12,fill='#9dbbc1',outline='#6c969f',width=2)
 txt(im,'海 洋 会 诊 处 方 单',1193,280,45,center=True)
 d.line((649,353,1740,353),fill='#7faab5',width=2)
 rect(im,(654,383,1736,477),'#e9f2ee','#bbd0ca',12)
 txt(im,'处方一：适应',700,401,65,'#337f92');txt(im,'目标：减少暴露与损失',1240,422,35)
 lines=[('01','早发现','先看官方监测，了解气候背景。'),('02','早预警','核对本地预警的地区和有效时间。'),('03','早行动','按指引准备应急物品，调整出行和用水。')]
 for j,(number,title,body) in enumerate(lines):
  y=529+j*117
  rect(im,(662,y,732,y+64),'#e1efec','#b7cfc8',12);txt(im,number,697,y+15,36,'#4a8c91',True)
  txt(im,title,766,y+1,48,'#3d7d8c');txt(im,body,766,y+62,35)
 d.line((651,902,1738,902),fill='#c8d7ce',width=2)
 txt(im,'减少损失，而不是消灭厄尔尼诺',1193,936,42,'#607e85',True)
 x,y,s,bb=sprite(im,R/'企鹅_拿处方单.png',(18,444,505,593))
 # Precisely overlaid type on the blank clipboard, not AI-generated Chinese glyphs.
 px=x+(742-bb[0])*s;py=y+(778-bb[1])*s
 txt(im,'处方单',px,py,30,center=True)
 for j in range(3):
  yy=py+46+j*22;d.rectangle((px-42,yy,px-34,yy+8),outline='#6299a6',width=1);d.line((px-24,yy+3,px+44,yy+3),fill='#aac0be',width=2)
 bubble(im,'先开第一张：适应处方。',(40,233,486,385),(250,492),44)
 return im

def main():
 if (R/'四步路线_插画原图.png').exists():
  from redesign_plates import main as redesign
  redesign();return
 records=[];sheet=Image.new('RGB',(1440,2544),'#e6eeec')
 for i,(name,fn) in enumerate([('01_四步会诊路线',road),('02_厄尔尼诺与人为增暖',compare),('03_适应处方单',prescription)]):
  AUDIT.clear();im=fn();assert im.size==(1920,1080);im.save(R/f'{name}.png');records.append(dict(name=name,text=list(AUDIT)))
  sheet.paste(im.resize((1440,810),Image.Resampling.LANCZOS),(0,i*848));ImageDraw.Draw(sheet).text((24,i*848+818),name,font=f(24),fill=INK)
 sheet.save(R/'三个画面总览.jpg',quality=95)
 (R/'文字与边界检查.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Three design frames ready',R,flush=True)
if __name__=='__main__':main()
