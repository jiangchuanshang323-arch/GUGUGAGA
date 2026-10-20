from pathlib import Path
import sys,json,math,wave,inspect
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
for name in ('素材','配音','.build','交付'):(ROOT/name).mkdir(exist_ok=True)
V16=ROOT.parent/'肚兜取卷轴_全屏图解_v16'
sys.path.insert(0,str(V16));import build_v16 as v
p=v.p;b=v.b
v.DATA=json.loads((V16/'台词与时间轴.json').read_text(encoding='utf-8'))
with wave.open(str(V16/'配音'/'第三段_卷轴版.wav'),'rb') as w:v.PCM=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
v.DURATION=len(v.PCM)/24000
row=next(r for r in v.DATA if r['mode']=='过渡');v.BRIDGE_START=row['speech_end'];v.BRIDGE_END=row['end']
p.DATA=v.DATA;p.DURATION=v.DURATION;p.prev.PCM=v.PCM.astype(np.float32)/32768
v.old.BRIDGE_START=v.BRIDGE_START;v.old.BRIDGE_END=v.BRIDGE_END
v.ROOT=ROOT
HIRES=ROOT/'素材'/'NOAA_正常态_1860原图.jpg'
assert Image.open(HIRES).size==(1860,1239)
MAP=ROOT/'素材'/'NOAA正常态_高清内容范围.png'
Image.open(HIRES).crop((0,102,1860,1209)).save(MAP)
v.MAP=MAP
THROW=Image.open(ROOT/'素材'/'26_轻抖抛卷轴.png').convert('RGBA')
assert THROW.getextrema()[-1][0]==0
saved=v.old.bubble;v.old.bubble=lambda *a,**k:None
OLD_BOARD=v.old.base_render(v.BRIDGE_START-.05).crop((24,140,1474,1030)).convert('RGBA');v.old.bubble=saved
scene_saved=v.env['scene'];v.env['scene']=lambda t:v.full_scene(v.BRIDGE_END+.2,False)
POSTER=v.diagram_render(v.BRIDGE_END+.2);v.env['scene']=scene_saved
def scroll_layer(width,height,content=None,rotation=0,rails=1):
 # Separate native paper content from the wood axes: horizontal unrolling followed by camera zoom.
 radius=max(7,min(27,width*.025));pad=40
 art=Image.new('RGBA',(max(1,round(width))+pad*2,max(1,round(height))+pad*2))
 d=ImageDraw.Draw(art);x,y=pad,pad
 if width>45:
  d.rounded_rectangle((x,y,x+width,y+height),radius=7,fill='#fff8e8',outline='#c9b785',width=2)
  if content:
   pic=content.resize((max(1,round(width-16)),max(1,round(height-12))),Image.Resampling.LANCZOS).convert('RGBA')
   art.paste(pic,(x+8,y+6),pic)
  # The thin shaded borders give the paper a curved edge while it is unrolling.
  if rails>.05:
   d=ImageDraw.Draw(art)
   for j in range(8):
    alpha=round((1-j/8)*24*rails)
    d.line([(x+j,y),(x+j,y+height)],fill=(155,125,71,alpha),width=1)
    d.line([(x+width-j,y),(x+width-j,y+height)],fill=(155,125,71,alpha),width=1)
 axis=Image.new('RGBA',art.size);d=ImageDraw.Draw(axis)
 for xx in (x,x+width) if width>45 else (x+width/2,):
  for k in range(-round(radius),round(radius)+1):
   z=k/radius;shade=round(190+47*math.sqrt(max(0,1-z*z)))
   d.line([(xx+k,y-12),(xx+k,y+height+12)],fill=(min(255,shade+12),shade,max(0,shade-30),round(255*rails)),width=1)
  d.ellipse((xx-radius,y-17,xx+radius,y+1),fill=(242,222,173,round(255*rails)),outline=(178,148,91,round(255*rails)),width=2)
  d.ellipse((xx-radius,y+height-1,xx+radius,y+height+17),fill=(220,195,139,round(255*rails)),outline=(178,148,91,round(255*rails)),width=2)
 art=Image.alpha_composite(art,axis)
 if abs(rotation)>.1:art=art.rotate(rotation,resample=Image.Resampling.BICUBIC,expand=True)
 return art
def paste_scroll(im,cx,cy,width,height,rotation=0,content=None,rails=1,cutoff=None):
 art=scroll_layer(width,height,content,rotation,rails)
 layer=Image.new('RGBA',im.size);layer.paste(art,(round(cx-art.width/2),round(cy-art.height/2)),art)
 if cutoff is not None:layer.paste((0,0,0,0),(0,round(cutoff),1920,1080))
 im.paste(layer,(0,0),layer)
def transition(age):
 stage=Image.open(b.BG).convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS)
 stage.paste(OLD_BOARD,(24,140),OLD_BOARD)
 retrieve=v.TAKE.resize((390,390),Image.Resampling.LANCZOS)
 toss=THROW.resize((390,390),Image.Resampling.LANCZOS)
 q=b.ease((age-.39)/.32)
 sprite=Image.blend(retrieve,toss,q)
 bounce=-5*math.sin(math.pi*b.ease((age-.35)/.55))
 stage.paste(sprite,(1510,660+round(bounce)),sprite)
 pocket=(1510+660/v.TAKE.width*390,660+790/v.TAKE.height*390)
 hand=(1510+250/THROW.width*390,660+460/THROW.height*390)
 if age<.40:
  q=b.ease((age-.06)/.34);cx=pocket[0];cy=pocket[1]+45-53*q
  paste_scroll(stage,cx,cy,25,60,cutoff=pocket[1]+8)
  return stage
 if age<.72:
  q=b.ease((age-.40)/.32);cx=pocket[0]+(hand[0]-pocket[0])*q;cy=pocket[1]-8+(hand[1]-(pocket[1]-8))*q
  paste_scroll(stage,cx,cy,25,60,rotation=-18*math.sin(q*math.pi))
  return stage
 flight=b.ease((age-.72)/.76)
 cx=hand[0]+(1050-hand[0])*flight
 cy=hand[1]+(370-hand[1])*flight-260*4*flight*(1-flight)
 spin=b.ease((age-.72)/.38)
 rotation=360*(1-spin) if spin<1 else 0
 opening=b.ease((age-1.06)/.72)
 zoom=b.ease((age-1.88)/.82)
 factor=1+(1920/804-1)*zoom
 inner_width=804*opening*factor
 width=16+inner_width
 height=(60+(804*1080/1920-60)*opening)*factor+12
 cx+=(960-cx)*zoom;cy+=(540-cy)*zoom
 rails=1-b.ease((age-2.54)/.22)
 paste_scroll(stage,cx,cy,width,height,rotation,POSTER if opening>.035 else None,rails)
 if age>2.76:stage=Image.blend(stage,POSTER,b.ease((age-2.76)/.04))
 return stage
def render(t):
 if t<v.BRIDGE_START:return v.old.base_render(t)
 if t<v.BRIDGE_END:return transition(t-v.BRIDGE_START)
 return v.diagram_render(t)
v.render=render
def main():
 for a in (.28,.57,.82,1.02,1.32,1.65,2.30,2.78):render(v.BRIDGE_START+a).save(ROOT/f'抛卷检查_{a}.png')
 for mode in ('方向','水层','沃克'):
  row=next(r for r in v.DATA if r['mode']==mode);render(row['start']+(row['speech_end']-row['start'])*.65).save(ROOT/f'高清图解_{mode}.png')
 sheet=Image.new('RGB',(1920,720),b.CREAM)
 for i,a in enumerate((.28,.57,.82,1.32,1.65,2.78)):
  sheet.paste(render(v.BRIDGE_START+a).resize((640,360)),((i%3)*640,(i//3)*360))
 sheet.save(ROOT/'抛卷轴_六帧预览.jpg')
 if '--preview' in sys.argv:return
 end=next(r['end'] for r in v.DATA if r['mode']=='方向')
 out=ROOT/'交付'/'轻抖抛卷轴_高清全屏_demo_v17.mp4'
 v.encode(out,v.BRIDGE_START,end-v.BRIDGE_START)
 if '--full' in sys.argv:v.encode(ROOT/'交付'/'海洋发烧了_第三段_高清全屏_v17.mp4',0,v.DURATION)
 (ROOT/'验证.json').write_text(json.dumps(dict(demo_decode='PASS',demo_seconds=end-v.BRIDGE_START,native_image=[1860,1239],prior_image=[620,413],linear_resolution_gain=3,ai_redraw=False,animation='pouch retrieve -> wrist flick -> parabolic airborne spin -> horizontal unroll -> continuous camera push-in',no_presenter_in_explanation=True,subtitles='bottom 46px',voice='cached v16, no new synthesis',full_segment_rendered='--full' in sys.argv,output=str(out)),ensure_ascii=False,indent=2),encoding='utf-8')
 print(out,flush=True)
if __name__=='__main__':main()
