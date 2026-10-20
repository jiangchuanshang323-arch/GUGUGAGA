from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parent
fontpath=root.parent/'主体课程'/'得意黑_大字无水印_v6'/'素材'/'SmileySans-Oblique.ttf'
font=ImageFont.truetype(str(fontpath),28)
title=ImageFont.truetype(str(fontpath),42)
canvas=Image.new('RGB',(1800,1460),'#fffaf0')
d=ImageDraw.Draw(canvas)
d.text((45,20),'企鹅小老师 · 18个教学姿势',font=title,fill='#36566b')
for i,path in enumerate(sorted((root/'独立动作PNG').glob('*.png'))):
    col,row=i%6,i//6;x=col*300;y=90+row*450
    d.rounded_rectangle((x+10,y+5,x+290,y+432),radius=20,fill='#edf6f5',outline='#b9d6da',width=2)
    art=Image.open(path).convert('RGBA');art.thumbnail((280,345),Image.Resampling.LANCZOS)
    canvas.paste(art,(x+(300-art.width)//2,y+25+(345-art.height)//2),art)
    label=path.stem.replace('_','  ');width=d.textlength(label,font=font)
    d.text((x+(300-width)/2,y+383),label,font=font,fill='#36566b')
out=root/'企鹅小老师_18动作总览.jpg'
canvas.save(out,quality=94)
print(out)
