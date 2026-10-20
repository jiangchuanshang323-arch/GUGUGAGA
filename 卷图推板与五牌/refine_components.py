"""Local corrections of existing scene components; retain source narration and art."""
from pathlib import Path
import math,importlib.util
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

def install(o):
 o.INSERT=4.8
 o.NEW=[]
 for row in o.OLD:
  r=dict(row);delta=o.INSERT if r['start']>=o.CUT else 0
  if r['start']>=o.EXIT:delta+=o.EXITLEN
  for k in ('start','speech_end','end'):r[k]+=delta
  o.NEW.append(r)
 o.STOP=next(r['start'] for r in o.NEW if r['mode']=='整体')
 o.CARDS=next(r['start'] for r in o.NEW if r['mode']=='五牌')
 o.EXITSTART=o.EXIT+o.INSERT
 roll_start=o.CUT+1;push_start=roll_start+1.3
 original_map=o.map_scene;original_board=o.board_scene;original_global=o.global_scene
 F=o.F;ease=o.m.ease

 def header(im,title,subtitle=''):
  if getattr(o,'HIDE_CHAPTER',None)==title:return
  art=o.p.header(title,subtitle);im.paste(art,(16,14),art)
 o.header=header

 def subtitle(im,words):
  d=ImageDraw.Draw(im);d.rectangle((0,958,1920,1080),fill='#244b60')
  lines=o.wrap(words,46,1750);assert len(lines)<=2
  y=965 if len(lines)>1 else 987
  for s in lines:o.txt(im,s,960,y,46,'#fffaf0',True);y+=49
 o.subtitle=subtitle

 def label(im,s,box,size=60,color=o.INK,fill=o.CREAM):
  x,y,z,b=box;cx=(x+z)/2;cy=(y+b)/2
  lines=o.wrap(s,size,z-x-32)
  w=min(z-x,max(F(size).getlength(line) for line in lines)+36)
  h=len(lines)*size*1.08+22
  xx=max(22,min(1898-w,cx-w/2));yy=max(160,min(938-h,cy-h/2))
  ImageDraw.Draw(im).rounded_rectangle((xx,yy,xx+w,yy+h),16,fill=fill,outline='#a6c4ce',width=2)
  for i,line in enumerate(lines):o.txt(im,line,xx+w/2,yy+11+i*size*1.08,size,color,True)
 o.label=label

 def bubble(im,words,age,span):
  # Complete clauses and original 46px type; compact bubble near the teacher.
  chunks=[];s=''
  for ch in words:
   s+=ch
   if ch in '。？！' or ch=='，' and len(s)>=7:chunks.append(s);s=''
  if s:chunks.append(s)
  total=sum(map(len,chunks));pos=min(total-1,age/max(.01,span)*total);acc=0;line=chunks[-1]
  for c in chunks:
   acc+=len(c)
   if pos<acc:line=c;break
  lines=o.wrap(line,46,350);h=len(lines)*57+38;x=35;y=620-h
  w=min(396,max(F(46).getlength(q) for q in lines)+42)
  d=ImageDraw.Draw(im);d.rounded_rectangle((x,y,x+w,y+h),20,fill=o.CREAM,outline='#92b9c6',width=2)
  tip=(240,685);d.polygon([(x+w*.50,y+h-2),tip,(x+w*.68,y+h-2)],fill=o.CREAM)
  d.line([(x+w*.50,y+h),tip,(x+w*.68,y+h)],fill='#92b9c6',width=2)
  for i,q in enumerate(lines):o.txt(im,q,x+21,y+18+i*57,46,o.INK)
 o.bubble=bubble

 spec=importlib.util.spec_from_file_location('continuous_approved',o.PROJECT/'连续场景重做'/'build_preview.py')
 c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
 c.HEADER=o.p.header('预测揭晓·两侧为何不同','信风减弱，云雨变化，地表响应')
 def ccard(im,words,box,size=38,color=o.INK,records=None):
  # Content grows 50%; long place names wrap without growing the UI title.
  size=round(size*1.5);x,y,z,b=box;maxw=max(z-x,350)
  if '秘鲁北部' in words:maxw=610
  if '雨水补给' in words or '地表径流' in words:maxw=350
  cx=(x+z)/2;cy=(y+b)/2
  return label(im,words,(max(22,cx-maxw/2),y,min(1898,cx+maxw/2),b),size,color)
 c.m.card=ccard
 def ctext(im,s,x,y,size,color=o.INK,center=False,records=None):
  size=round(size*1.5)
  o.txt(im,s,x,y,size,color,center)
 c.m.text=ctext

 def continuous(t):
  im=c.diagram(min(t,o.CUT),[])
  if t<3.7:
   before=original_map('承下',t,4)
   header(before,'预测揭晓·两侧为何不同','先辨位置，再看海陆响应')
   im=Image.blend(before,im,ease((t-2.6)/1.1))
  return im

 push=Image.open(o.ROOT/'素材'/'企鹅_双翼推板.png').convert('RGBA')
 # One continuous source drawing is deformed at the ankles; no replacement tube arms.
 push=push.resize((400,400),Image.Resampling.LANCZOS)
 def push_art(t,effort):
  phase=t*10;mesh=[]
  for left,right,sign in [(0,220,1),(220,400,-1)]:
   for a,b in [(0,310),(310,340),(340,370),(370,400)]:
    da=max(0,(a-310)/90);db=max(0,(b-310)/90)
    dx=math.sin(phase)*5*sign*effort;dy=-max(0,math.sin(phase)*sign)*8*effort
    mesh.append(((left,a,right,b),(left-da*dx,a-da*dy,left-db*dx,b-db*dy,right-db*dx,b-db*dy,right-da*dx,a-da*dy)))
  return push.transform((400,400),Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)

 def puppet(im,x,y,t,push=False,target=(650,560),speech_t=None,fade=1):
  if push:
   # Push rig is a cohesive redrawing with the original short flipper design.
   art=push_art(t,1)
   # Source wing tips sit at x=350 and x=338; narrow contact cap belongs to board frame.
   im.paste(art,(round(x),round(y)),art)
   return
  age=t-o.STOP
  pose=3 if age<.33 or t>=o.EXITSTART else 6
  art=o.m.POSES[pose].resize((390,390),Image.Resampling.LANCZOS)
  if speech_t is not None:
   lo=max(0,int((speech_t-.02)*24000));a=o.m.PCM[lo:lo+1080].astype(np.float32)/32768
   rms=float(np.sqrt(np.mean(a*a))) if len(a) else 0;state=0 if rms<.011 else 1 if rms<.055 else 2 if rms<.13 else 3
   mx,my,mw,mh=o.m.MOUTH_CENTERS[pose];s=390/512
   mouth=o.m.mouth(pose,state).resize((round(mw*s),round(mh*s)),Image.Resampling.LANCZOS)
   art.alpha_composite(mouth,(round((mx-mw/2)*s),round((my-mh/2)*s)))
  # Use the whole approved pose; no polygon cuts across shoulders or white belly.
  if fade<1:art.putalpha(art.getchannel('A').point(lambda z:round(z*fade)))
  im.paste(art,(round(x),round(y+math.sin(t*2)*1.2)),art)
 o.puppet=puppet

 def board(t,mode,row):
  if t>=o.STOP:return original_board(t,mode,row)
  im=o.m.BG.copy();header(im,'追并发症·环境多米诺','自然环境具有整体性')
  u=max(0,min(1,(t-push_start)/2.5))
  # Front-load entry, then leave visible time for pushing and a controlled stop.
  a=1-(1-u)**3.5;bx=-1430+1880*a
  panel=Image.new('RGBA',(1430,750));d=ImageDraw.Draw(panel)
  d.rounded_rectangle((5,8,1427,748),22,fill='#3a6267');d.rounded_rectangle((0,0,1420,730),22,fill='#c9ad85');d.rounded_rectangle((13,13,1407,717),14,fill='#315d64');d.line((22,18,1390,18),fill='#ecd8ae',width=4)
  im.paste(panel,(round(bx),220),panel)
  px=bx-348;py=624
  art=push_art(t,1-ease((u-.88)/.12));im.paste(art,(round(px),py),art)
  # The two short wing tips press against the same vertical wooden edge.
  ImageDraw.Draw(im).rounded_rectangle((bx-6,790,bx+5,890),5,fill='#ccb68e')
  return im
 o.board_scene=board

 snap={}
 def roll(t):
  if 'im' not in snap:snap['im']=continuous(o.CUT)
  source=snap['im'];im=o.m.BG.copy();header(im,'预测揭晓·两侧为何不同','先看气流，再看降水')
  q=ease((t-roll_start)/1.3);y=164+1060*q;r=28+24*q;x0,x1=28,1892
  bottom=950;boundary=round(y+r)
  if boundary<bottom:im.paste(source.crop((x0,max(164,boundary),x1,bottom)),(x0,max(164,boundary)))
  if y-r>1080:return im
  shadow=Image.new('RGBA',im.size);sd=ImageDraw.Draw(shadow)
  sd.rectangle((x0+5,y+r-4,x1-5,y+r+19),fill=(35,66,72,62));shadow=shadow.filter(ImageFilter.GaussianBlur(9));im.paste(shadow,(0,0),shadow)
  # A bent lip is contiguous with the remaining printed paper, ahead of the cylinder.
  for k in range(24):
   yy=boundary+k
   if yy>=bottom or yy>=1080:break
   sy=max(164,min(949,round(boundary+24*(k/24)**1.5)))
   strip=source.crop((x0,sy,x1,sy+1));shade=.78+.22*k/24
   strip=Image.blend(Image.new('RGB',strip.size,'#405d61'),strip,shade);im.paste(strip,(x0,yy))
  for yy in range(max(164,round(y-r)),min(1080,round(y+r))):
   v=(yy-y)/r;angle=math.acos(max(-1,min(1,v)));sy=max(164,min(949,round(y-r*angle)))
   strip=source.crop((x0,sy,x1,sy+1));light=.62+.38*math.sqrt(max(0,1-v*v))
   paper=Image.new('RGB',strip.size,tuple(round(k*light) for k in (246,233,203)))
   strip=Image.blend(paper,strip,.17 if v<0 else .32);im.paste(strip,(x0,yy))
  d=ImageDraw.Draw(im);d.line((x0,y-r+2,x1,y-r+2),fill='#fff2d7',width=3)
  for xx in (x0,x1):
   d.ellipse((xx-10,y-r,xx+10,y+r),fill='#ecdabc',outline='#a9916d',width=2)
   for a in (.74,.43,.16):d.ellipse((xx-8*a,y-r*a,xx+8*a,y+r*a),outline='#b49c76',width=1)
  return im
 o.roll=roll

 def global_scene(mode,t):
  im=original_global('全球');row=next(r for r in o.NEW if r['mode']==mode)
  age=t-row['start']
  if mode not in ('偏干','偏湿'):return im
  dry=mode=='偏干';pt=(785,661) if dry else (1245,650)
  tx=125+(pt[0]-60)*1670/1800;ty=215+(pt[1]-180)*686/740
  rx,ry=(100,67) if dry else (205,66);q=ease(age/.5)
  layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer);color=(110,164,174) if dry else (220,151,113)
  d.ellipse((tx-rx,ty-ry,tx+rx,ty+ry),fill=color+(round(48*q),),outline=color+(round(165*q),),width=3)
  im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
  label(im,'印尼一带 · 偏干' if dry else '赤道中东太平洋 · 偏暖湿',(530,290,1640,386),60,o.BLUE if dry else o.ORANGE)
  ImageDraw.Draw(im).line((1085,385,tx,ty-ry-3),fill='#829fa6',width=3)
  return im

 def hydro(mode,t):
  im=o.m.BG.copy();header(im,'第一张·水','环流变化 → 降水重分配 → 水循环响应')
  d=ImageDraw.Draw(im);d.rounded_rectangle((50,200,1870,940),25,fill=o.CREAM)
  o.txt(im,'降水重分配，怎样传到河流？',960,239,81,o.INK,True)
  for side,title,items,color,key,times in [
   (0,'持续少雨',['降水减少','雨水补给减少','低流量 / 缺水风险'],o.BLUE,'少雨',(1.1,2.7,4.3)),
   (1,'强降雨集中',['降水集中','地表径流增加','洪涝风险增加'],o.ORANGE,'强雨',(.25,1.5,3.0))]:
   start=next(r['start'] for r in o.NEW if r['mode']==key)
   age=t-start
   if age<0:continue
   cx=500+side*920
   label(im,title,(cx-350,350,cx+350,440),70,color)
   prev=440
   for j,s in enumerate(items):
    at=times[j]
    if age<at:break
    yy=495+j*140;q=ease((age-at)/.4)
    # Draw connector first; the next concept only appears after its incoming arrow.
    ytip=prev+18+(yy-prev-28)*q
    if q>0:o.p.native.arrow(im,[(cx,prev+12),(cx,ytip)],color,5,1)
    if q>.55:
     layer=im.copy();label(layer,s,(cx-370,yy,cx+370,yy+91),63,color if j==2 else o.INK)
     im=Image.blend(im,layer,ease((q-.55)/.45))
    prev=yy+91
  return im

 def render5(t):
  if o.CUT<=t<roll_start:return continuous(o.CUT)
  if roll_start<=t<push_start:return roll(t)
  row=next((r for r in o.NEW if r['start']<=t<r['end']),o.NEW[0] if t<.2 else o.NEW[-1])
  if push_start<=t<o.STOP:return board(t,'push',row)
  if o.STOP<=t<o.EXITSTART+o.EXITLEN:return board(t,row['mode'],row)
  mode=row['mode'];source=t-o.INSERT-(o.EXITLEN if t>=o.EXITSTART+o.EXITLEN else 0)
  if mode in ('回扣','西侧','东侧'):im=continuous(t)
  elif mode in ('全球','偏干','偏湿'):im=global_scene(mode,t)
  else:im=hydro(mode,t)
  subtitle(im,row['text']);return im
 o.render5=render5
