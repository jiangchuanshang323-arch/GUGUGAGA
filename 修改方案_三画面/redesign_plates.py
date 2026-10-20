"""Illustrated route plate and print-led prescription, with separate type/actor layers."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
import build_concepts as b

R=Path(__file__).resolve().parent;INK='#193f53';ORANGE='#bc7950'
def brush(n):return ImageFont.truetype('C:/Windows/Fonts/STXINGKA.TTF',n)
def title(im,s,x,y,n=80):
 font=brush(n);ImageDraw.Draw(im).text((x,y),s,font=font,fill=INK,anchor='lt')
 b.AUDIT.append(dict(text=s,box=[x,y,x+font.getlength(s),y+n]))
def route():
 im=Image.open(R/'四步路线_插画原图.png').convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS)
 title(im,'海洋“发烧”了',85,62,94)
 b.txt(im,'四步会诊 · 跟着企鹅，一站一站找答案',91,177,38,INK)
 d=ImageDraw.Draw(im)
 d.line([(90,238),(260,233),(520,238),(813,231)],fill='#c5a36b',width=3)
 checkpoints=[(350,793),(765,532),(1223,843),(1692,531)]
 labels=[(350,885,'测体征'),(765,633,'查病因'),(1223,934,'追并发症'),(1692,634,'开处方')]
 for i,((x,y),(lx,ly,s)) in enumerate(zip(checkpoints,labels)):
  b.txt(im,str(i+1),x,y-21,44,'#fff8e7',True)
  w=b.f(48).getlength(s)+62
  d.rounded_rectangle((lx-w/2,ly,lx+w/2,ly+75),35,fill='#284b5e',outline='#f0e4c8',width=2)
  b.txt(im,s,lx,ly+13,48,'#fff8e7',True)
 (R/'站点坐标.json').write_text(json.dumps(dict(canvas=[1920,1080],checkpoints=checkpoints,walking_layer='separate character, not baked into the route image'),ensure_ascii=False,indent=2),encoding='utf-8')
 return im

def prescription(actor=True):
 im=Image.open(R/'处方笺_插画原图.png').convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS)
 d=ImageDraw.Draw(im)
 b.txt(im,'海 洋 会 诊 室',1253,88,33,'#fff8e7',True)
 b.txt(im,'海洋会诊 · 适应处方笺',1250,151,60,INK,True)
 for s,x,y in [
  ('姓名：海洋',662,224),('类型：适应',1030,224),('目标：减少暴露与损失',1418,224),
  ('关注：当地天气风险',662,275),('依据：监测与预警',1030,275),('应对：因地因时',1420,275)]:b.txt(im,s,x,y,29,INK)
 b.txt(im,'R：主要诉求',661,377,52,INK)
 b.txt(im,'减少天气灾害带来的损失',667,450,40,INK)
 b.txt(im,'建议执行',666,529,40,INK)
 items=[('早发现｜关注官方监测','先了解气候背景。'),('早预警｜核对本地预警','看清地区与有效时间。'),('早行动｜按指引做好准备','调整出行和用水安排。')]
 for j,(s,sub) in enumerate(items):
  y=594+j*88;d.rectangle((665,y+7,683,y+25),outline=INK,width=2)
  b.txt(im,s,701,y,36,INK);b.txt(im,sub,702,y+45,30,'#3e626b')
 b.txt(im,'医嘱：减少损失，不是消灭厄尔尼诺。',665,868,33,INK)
 for s,x in [('签名：咕咕嘎嘎',650),('会诊主题：海洋升温',1090),('分类：适应',1575)]:b.txt(im,s,x,934,29,INK)
 d.ellipse((1610,360,1802,422),outline='#ba7353',width=3);b.txt(im,'适应',1706,374,38,'#a9674c',True)
 if actor:
  title(im,'开处方',70,88,68)
  b.bubble(im,'这张处方，先减少损失。',(40,240,514,378),(250,480),42)
  x,y,s,bb=b.sprite(im,R/'企鹅_拿处方单.png',(20,426,510,612))
  px=x+(742-bb[0])*s;py=y+(778-bb[1])*s
  b.txt(im,'处方单',px,py,30,INK,True)
  for j in range(3):
   yy=py+46+j*22;d.rectangle((px-42,yy,px-34,yy+8),outline='#6299a6',width=1);d.line((px-24,yy+3,px+44,yy+3),fill='#aac0be',width=2)
 return im

def main():
 b.AUDIT.clear();a=route();a.save(R/'01_四步会诊路线.png');a.save(R/'四步会诊路线_独立主图.png');a1=list(b.AUDIT)
 b.AUDIT.clear();plain=prescription(False);plain.save(R/'适应处方笺_独立主图.png')
 b.AUDIT.clear();c=prescription(True);c.save(R/'03_适应处方单.png');a3=list(b.AUDIT)
 c2=Image.open(R/'02_厄尔尼诺与人为增暖.png').convert('RGB')
 sheet=Image.new('RGB',(1440,2544),'#e6eeec')
 for i,(name,im) in enumerate([('01  Illustrated route',a),('02  Concept comparison (unchanged)',c2),('03  Prescription',c)]):
  sheet.paste(im.resize((1440,810),Image.Resampling.LANCZOS),(0,i*848));ImageDraw.Draw(sheet).text((24,i*848+818),name,font=b.f(24),fill=INK)
 sheet.save(R/'三个画面总览.jpg',quality=95)
 (R/'重新设计_文字检查.json').write_text(json.dumps([dict(frame=1,text=a1),dict(frame=3,text=a3)],ensure_ascii=False,indent=2),encoding='utf-8')
 print('Redesigned plates ready',R,flush=True)
if __name__=='__main__':main()
