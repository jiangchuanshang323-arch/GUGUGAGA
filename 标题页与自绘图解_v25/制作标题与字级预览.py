from pathlib import Path
import sys,inspect,json
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parent
FONT=ROOT.parent/'主体课程'/'得意黑_大字无水印_v6'/'素材'/'SmileySans-Oblique.ttf'
def f(size):return ImageFont.truetype(str(FONT),size)
def baseline(im,t,x,y,size,color,stroke=0,outline=None):
 d=ImageDraw.Draw(im);font=f(size)
 d.text((x,y+font.getmetrics()[0]),t,font=font,fill=color,stroke_width=stroke,stroke_fill=outline,anchor='ls')

def title():
 im=ImageOps.fit(Image.open(ROOT/'素材'/'秘鲁渔港_实拍背景.jpg').convert('RGB'),(1920,1080),centering=(.5,.60)).convert('RGBA')
 # Photograph remains the background. Native typography and mascot are separate layers.
 shapes=Image.new('RGBA',im.size);d=ImageDraw.Draw(shapes)
 d.rounded_rectangle((644,797,1858,940),radius=55,fill=(255,249,231,238))
 im=Image.alpha_composite(im,shapes)
 lettering=Image.open(ROOT/'素材'/'艺术字_海洋发烧了.png').convert('RGBA')
 lettering.thumbnail((1240,705),Image.Resampling.LANCZOS)
 im.alpha_composite(lettering,(round(1250-lettering.width/2),78))
 baseline(im,'追踪厄尔尼诺的环境多米诺',1245-f(67).getlength('追踪厄尔尼诺的环境多米诺')/2,829,67,'#204b61')
 mascot=Image.open(ROOT/'素材'/'30_企鹅抱场记板.png').convert('RGBA').resize((920,920),Image.Resampling.LANCZOS)
 # Board lettering is added at the exact empty center of the generated prop.
 d=ImageDraw.Draw(mascot);word='Action!';font=f(52)
 d.text((635/1280*920-font.getlength(word)/2,811/1280*920),word,font=font,fill='#fffbed')
 im.alpha_composite(mascot,(-124,158))
 im.convert('RGB').save(ROOT/'交付'/'海洋发烧了_艺术字标题页_v25.png')
 im.convert('RGB').resize((960,540)).save(ROOT/'交付'/'标题页_手机检查.png')

def captions():
 source=ROOT.parent/'主体课程'/'出入场_无制作提示_v9'
 sys.path.insert(0,str(source));import build_v9 as c
 src=inspect.getsource(c.scene)
 src=src.replace("s.text('海洋“发烧”了',36,30,57,b.INK,w=1000);s.text('厄尔尼诺 · 从三地情境开始',38,101,30,b.SOFT,w=1000)","s.rect(16,14,690,130,fill=b.CREAM,stroke='#98bcc6',width=2,r=23);s.text('海洋“发烧”了',40,23,63,b.INK,w=650);s.text('厄尔尼诺 · 从三地情境开始',42,96,31,b.INK,w=650)")
 src=src.replace('lines=wrap(labels[j],32,449)','lines=wrap(labels[j],52,449)').replace('877+k*42,32,b.INK','866+k*62,52,b.INK')
 exec(src,c.__dict__);c.env['scene']=c.scene
 row=next(r for r in c.DATA if r['mode']=='观察')
 im=c.render(row['start']+.5);im.save(ROOT/'交付'/'三案例_标题图注放大预览_v25.png')
 (ROOT/'正文样式替换.patch.txt').write_text(src,encoding='utf-8')

title();captions()
(ROOT/'版式与字号.json').write_text(json.dumps({'title':[250,198],'subtitle':67,'case_title':63,'case_caption':52,'previous_caption':32,'video_exported':False,'real_photo_source':'Jon Kolbert / Wikimedia Commons, Paracas 2019-10-17, CC BY-SA 4.0','no_new_lesson_segment':True},ensure_ascii=False,indent=2),encoding='utf-8')
print('Title PNG and caption comparison PNG saved')
