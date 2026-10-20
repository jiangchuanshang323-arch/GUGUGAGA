from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parent
FONT=ROOT.parent/'主体课程'/'得意黑_大字无水印_v6'/'素材'/'SmileySans-Oblique.ttf'
photo=ROOT/'素材'/'太平洋海浪_4941原图.jpg'
im=ImageOps.fit(Image.open(photo).convert('RGB'),(1920,1080),centering=(.5,.48)).convert('RGBA')
veil=Image.new('RGBA',im.size)
d=ImageDraw.Draw(veil)
for y in range(1080):
    alpha=round(65*(1-y/1080))
    d.line((0,y,1920,y),fill=(232,249,251,alpha))
im=Image.alpha_composite(im,veil)
letter=Image.open(ROOT/'素材'/'艺术字_蓝绿金橙渐变.png').convert('RGBA')
letter.thumbnail((1080,700),Image.Resampling.LANCZOS)
im.alpha_composite(letter,(round(1350-letter.width/2),95))
board=Image.open(ROOT/'素材'/'31_企鹅向右上举板.png').convert('RGBA')
label=Image.new('RGBA',(480,150));ld=ImageDraw.Draw(label)
ld.text((240,75),'Action!',font=ImageFont.truetype(str(FONT),76),fill='#fffbed',anchor='mm')
label=label.rotate(6,Image.Resampling.BICUBIC,expand=True)
board.alpha_composite(label,(round(1035-label.width/2),round(515-label.height/2)))
board=board.resize((940,940),Image.Resampling.LANCZOS)
im.alpha_composite(board,(-20,139))
pill=Image.new('RGBA',im.size);pd=ImageDraw.Draw(pill)
pd.rounded_rectangle((765,845,1868,1000),radius=52,fill=(255,250,236,244),outline=(240,249,249,255),width=3)
font=ImageFont.truetype(str(FONT),64);words='追踪厄尔尼诺的环境多米诺'
pd.text((1315,922),words,font=font,fill='#204b61',anchor='mm')
im=Image.alpha_composite(im,pill).convert('RGB')
out=ROOT/'交付'/'海洋发烧了_渐变右举封面_v26.png';im.save(out)
im.resize((960,540),Image.Resampling.LANCZOS).save(ROOT/'交付'/'封面_手机预览_v26.png')
record={'output':str(out),'size':[1920,1080],'photo_original_dimensions':Image.open(photo).size,'photo_author':'Andywallxyz','photo_date':'2017-05-22','photo_page':'https://commons.wikimedia.org/wiki/File:Waves_in_the_Pacific_Ocean.jpg','photo_url':'https://upload.wikimedia.org/wikipedia/commons/4/45/Waves_in_the_Pacific_Ocean.jpg','license':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/','photo_changes':'16:9 crop, resize and light transparent veil; no AI redraw','photo_sha256':hashlib.sha256(photo.read_bytes()).hexdigest(),'title_gradient':'aqua to turquoise/blue; golden yellow to coral orange','scope':'cover only, no video or lesson segment modified'}
(ROOT/'来源与验证.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(out)
