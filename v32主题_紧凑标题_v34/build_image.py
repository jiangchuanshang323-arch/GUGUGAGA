from pathlib import Path
import sys,importlib.util,json
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
(ROOT/'交付').mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('master32',PROJECT/'阶段合成_v32'/'build_current.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);c=m.c
FONT=PROJECT/'主体课程'/'得意黑_大字无水印_v6'/'素材'/'SmileySans-Oblique.ttf'
title='海洋“发烧”了';subtitle='厄尔尼诺 · 从三地情境开始'
f1=ImageFont.truetype(str(FONT),63);f2=ImageFont.truetype(str(FONT),31)
width=round(max(f1.getlength(title)+110,f2.getlength(subtitle)+58))
width=max(440,width);height=130
header=Image.new('RGBA',((width+16)*2,(height+12)*2));d=ImageDraw.Draw(header)
pts=[(0,20),(0,240),(18,260),(width*2-30,260),(width*2,240),(width*2,26),(width*2-24,0),(20,0)]
shadow=Image.new('RGBA',header.size);sd=ImageDraw.Draw(shadow)
sd.polygon([(x+3,y+9)for x,y in pts],fill=(61,91,105,18))
header=Image.alpha_composite(header,shadow.filter(ImageFilter.GaussianBlur(9)));d=ImageDraw.Draw(header)
d.polygon(pts,fill='#fffaf0');d.line(pts+[pts[0]],fill='#a9c5ce',width=2,joint='curve')
d.rounded_rectangle((48,0,178,12),5,fill='#b7d1d6')
d.line((49,45,49,145),fill='#7ba3b4',width=5)
rects=[]
for words,x,y,size,color in [(title,43,19,63,'#36566b'),(subtitle,29,91,31,'#668697')]:
 font=ImageFont.truetype(str(FONT),size*2);box=font.getbbox(words)
 d.text((x*2-box[0],y*2-box[1]),words,font=font,fill=color)
 rect=[x,y,x+(box[2]-box[0])/2,y+(box[3]-box[1])/2]
 assert rect[2]<width-18 and rect[3]<height-5,(words,rect)
 rects.append({'text':words,'rect':rect,'font':'得意黑','size':size})
for j in range(2):
 points=[]
 for n in range(51):
  x=width-78+n*.84;y=31+j*8+3*__import__('math').sin(n/50*2*__import__('math').pi)
  points.append((x*2,y*2))
 d.line(points,fill='#a5c5d0',width=3)
header=header.resize((width+16,height+12),Image.Resampling.LANCZOS)
HEADER=ROOT/'交付'/'紧凑标题_得意黑_v34.png';header.save(HEADER)
old_scene=m.scene
def scene(t):
 s=old_scene(t)
 s.items=[item for item in s.items if not(
  item['kind']=='rect' and item.get('x')==16 and item.get('y')==14 and item.get('w')==690
  or item['kind']=='text' and item.get('x') in (40,42) and item.get('y') in (23,96))]
 s.items.insert(1,{'kind':'image','path':str(HEADER),'x':16,'y':14,'w':width+16,'h':height+12})
 return s
c.env['scene']=scene
t=next(row['start'] for row in c.DATA if row['mode']=='联系')+.65
output=ROOT/'交付'/'v32主题_新版标题_风格样张_v34.png'
c.render(t).save(output)
(ROOT/'样张说明.json').write_text(json.dumps({'output':str(output),'resolution':[1920,1080],'base':'v32第一段场景','only_changed':'章节标题形状、宽度、细线装饰与轻投影','original_title_width':690,'new_title_width':width,'fonts_unchanged':'得意黑63/31','title_text_bounds':rects,'video_exported':False,'master_v32_changed':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(output)
