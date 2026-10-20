from pathlib import Path
import sys,math,json,wave,subprocess,hashlib
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance,ImageOps
import numpy as np

ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
for folder in ('交付','检查','配音'):(ROOT/folder).mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(PROJECT/'主体课程'/'出入场_无制作提示_v9'))
import build_v9 as old
EXE=old.EXE
INK='#2c4b60';SOFT='#6d8798';EDGE='#bacdd7';PAPER='#fcfaf5';BLUE='#7da9bf'
FONT_PATH=PROJECT/'主体课程'/'得意黑_大字无水印_v6'/'素材'/'SmileySans-Oblique.ttf'
BODY_FONT=Path('C:/Windows/Fonts/msyh.ttc');BOLD_FONT=Path('C:/Windows/Fonts/msyhbd.ttc')
@lru_cache(None)
def font(size,kind='body'):
 return ImageFont.truetype(str(FONT_PATH if kind=='display' else BOLD_FONT if kind=='bold' else BODY_FONT),size)

WORDS={'chapter':'海洋“发烧”了','subchapter':'厄尔尼诺 · 从三地情境开始','question':'相隔上万公里，它们会不会有共同的线索？',
 'panel':'相隔万里的三幅画面，有什么联系？','captions':['图一：秘鲁渔港','图二：印度尼西亚烟霾','图三：江南洪水与积水']}
ROW=next(r for r in old.DATA if r['mode']=='联系')
assert ROW['text']==WORDS['question']
start=round(ROW['start']*24000);end=round(ROW['end']*24000)
voice=(old.PCM[start:end]*32768).astype('<i2')
PCM=np.concatenate([np.zeros(round(.65*24000),dtype='<i2'),voice,np.zeros(120000-round(.65*24000)-len(voice),dtype='<i2')])
AUDIO=ROOT/'配音'/'五秒样片_复用晓伊提问.wav'
with wave.open(str(AUDIO),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(PCM.tobytes())

def ease(q):q=max(0,min(1,q));return q*q*q*(q*(q*6-15)+10)
def curved(points,n=28):
 a,b,c,d=points;out=[]
 for i in range(n+1):
  t=i/n;u=1-t;out.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*d[0],u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*d[1]))
 return out
def shadow(im,box,radius=22,alpha=18,blur=9,offset=(0,6)):
 layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer);x,y,z,b=box
 d.rounded_rectangle((x+offset[0],y+offset[1],z+offset[0],b+offset[1]),radius,fill=(46,79,101,alpha))
 im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
def drawtext(im,words,x,y,size,color=INK,kind='body',container=None,center=False,records=None):
 f=font(size,kind);d=ImageDraw.Draw(im);box=f.getbbox(words);w=box[2]-box[0];h=box[3]-box[1]
 if center:x-=w/2
 d.text((x-box[0],y-box[1]),words,font=f,fill=color)
 rect=[x,y,x+w,y+h]
 if container:
  a,b,c,d=container
  assert a<=rect[0] and b<=rect[1] and rect[2]<=c and rect[3]<=d,(words,rect,container)
 if records is not None:records.append({'text':words,'rect':rect,'container':container})
 return rect
def waves(d,x,y,width=50,color='#9abaca',weight=2):
 for j in range(2):
  pts=curved([(x,y+j*9),(x+width*.32,y-10+j*9),(x+width*.55,y+10+j*9),(x+width,y+j*9)])
  d.line(pts,fill=color,width=weight,joint='curve')

# Keep the original aquarium, but calm its contrast behind the information layers.
bg=Image.open(old.b.BG).convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS)
bg=ImageEnhance.Color(bg).enhance(.80)
BASE=Image.blend(bg,Image.new('RGB',bg.size,'#f2f6f5'),.17).convert('RGBA')
STATIC_RECORDS=[]

# Compact editorial chapter seal: a clipped corner, a small binding tab, and minimal waves.
TITLE_W=round(max(font(58,'display').getlength(WORDS['chapter'])+118,font(27).getlength(WORDS['subchapter'])+64))
TITLE_W=max(440,min(540,TITLE_W))
tx,ty=30,30;tw,th=TITLE_W,144
shadow(BASE,(tx,ty,tx+tw,ty+th),20,15,7,(0,5))
hi=Image.new('RGBA',(tw*2+4,th*2+4));hd=ImageDraw.Draw(hi)
outline=[(0,22),(0,th*2-26),(20,th*2),(tw*2-36,th*2),(tw*2,th*2-26),(tw*2,30),(tw*2-26,0),(22,0)]
hd.polygon(outline,fill=PAPER);hd.line(outline+[outline[0]],fill=EDGE,width=2,joint='curve')
hi=hi.resize((tw+2,th+2),Image.Resampling.LANCZOS);BASE.alpha_composite(hi,(tx,ty))
bd=ImageDraw.Draw(BASE);bd.rounded_rectangle((tx+24,ty-4,tx+92,ty+7),5,fill='#afcad7')
bd.line((tx+25,ty+24,tx+25,ty+75),fill='#799daf',width=4)
drawtext(BASE,WORDS['chapter'],tx+43,ty+24,58,kind='display',container=[tx+34,ty+17,tx+tw-18,ty+91],records=STATIC_RECORDS)
drawtext(BASE,WORDS['subchapter'],tx+33,ty+104,27,SOFT,container=[tx+25,ty+94,tx+tw-22,ty+th-13],records=STATIC_RECORDS)
waves(bd,tx+tw-80,ty+34,43,'#a5c3d0',2)

# Stable primary information panel, different from the chapter seal and the dialogue silhouette.
PANEL=(410,210,1888,1018)
shadow(BASE,PANEL,26,21,10,(0,8));bd=ImageDraw.Draw(BASE)
bd.rounded_rectangle(PANEL,26,fill=PAPER,outline='#afc6d2',width=2)
bd.line((448,324,1850,324),fill='#dbe5e9',width=2)
bd.rounded_rectangle((448,255,455,299),3,fill='#88aebe')
drawtext(BASE,WORDS['panel'],475,258,44,kind='bold',container=[468,246,1775,310],records=STATIC_RECORDS)
waves(bd,1798,278,44,'#b6cdd6',2)
bd.line((1848,970,1848,985,1828,985),fill='#c1d3db',width=2)

CARDS=[];CARD_RECORDS=[]
for i,path in enumerate(old.b.PHOTOS):
 # Render on a local double-resolution canvas for clean rounded masks and borders.
 art=Image.new('RGBA',(896,1224));ad=ImageDraw.Draw(art)
 ad.rounded_rectangle((0,0,894,1220),32,fill='#f7f9f9',outline='#c7d7df',width=2)
 photo=ImageOps.fit(Image.open(path).convert('RGB'),(848,988),centering=(.5,.62 if i==0 else .5)).convert('RGBA')
 mask=Image.new('L',photo.size);ImageDraw.Draw(mask).rounded_rectangle((0,0,847,987),18,fill=255)
 photo.putalpha(mask);art.alpha_composite(photo,(24,24))
 ad=ImageDraw.Draw(art);ad.line((24,1034,872,1034),fill='#dce6e9',width=2)
 # Use the same text metrics and inset in all three caption bands.
 drawtext(art,WORDS['captions'][i],448,1090,70,INK,center=True,container=[24,1050,872,1200])
 art=art.resize((448,612),Image.Resampling.LANCZOS)
 CARDS.append(art)
 CARD_RECORDS.append({'rect':[446+i*480,354,894+i*480,966],'text':WORDS['captions'][i]})

# Modern role-specific speech silhouette, with a real tail directed at the hood.
BUBBLE=Image.new('RGBA',(380,350));dd=ImageDraw.Draw(BUBBLE)
BX,BY=30,298;BW,BH=350,242
tail=[(182,239),(167,301),(226,239)]
dd.polygon([(x+1,y+4)for x,y in tail],fill=(56,89,108,15))
dd.rounded_rectangle((1,4,351,246),31,fill=(56,89,108,15))
BUBBLE=BUBBLE.filter(ImageFilter.GaussianBlur(4));dd=ImageDraw.Draw(BUBBLE)
dd.polygon(tail,fill='#fbfcf9');dd.line(tail+[tail[0]],fill=EDGE,width=2,joint='curve')
dd.rounded_rectangle((0,0,BW,BH),31,fill='#fbfcf9',outline=EDGE,width=2)
dd.polygon([(184,235),(167,301),(224,235)],fill='#fbfcf9')
dd.line([(182,242),(167,301),(226,242)],fill=EDGE,width=2,joint='curve')
LINES=['相隔上万公里，','它们会不会有','共同的线索？']
assert ''.join(LINES)==WORDS['question']
BUBBLE_RECORDS=[]
for j,line in enumerate(LINES):
 if j<len(LINES)-1:
  ff=font(39);space=(286-sum(ff.getlength(ch) for ch in line))/(len(line)-1)
  x=32;baseline=35+j*57-ff.getbbox(line,anchor='ls')[1]
  for ch in line:
   # Chinese glyphs and punctuation share one baseline, rather than top-aligning ink boxes.
   dd.text((x,baseline),ch,font=ff,fill=INK,anchor='ls')
   cb=ff.getbbox(ch,anchor='ls')
   assert 28<=x+cb[0] and x+cb[2]<=324 and 26<=baseline+cb[1] and baseline+cb[3]<=216
   x+=ff.getlength(ch)+space
  BUBBLE_RECORDS.append({'text':line,'rect':[BX+32,BY+35+j*57,BX+318,BY+35+j*57+40]})
 else:
  r=drawtext(BUBBLE,line,32,35+j*57,39,container=[28,26,324,216])
  BUBBLE_RECORDS.append({'text':line,'rect':[BX+r[0],BY+r[1],BX+r[2],BY+r[3]]})
waves(dd,286,216,32,'#c5d9e0',2)

SPRITE=Image.open(old.b.SPRITES[9]).convert('RGBA')
SPRITE_SIZE=425
SPRITE=SPRITE.resize((SPRITE_SIZE,SPRITE_SIZE),Image.Resampling.LANCZOS)
MOUTH=[Image.open(old.v.V3/'素材'/f'口型_09_{k}.png').convert('RGBA') for k in range(4)]
mx,my,mw,mh=old.b.MOUTH_CENTERS[9];scale=SPRITE_SIZE/512
MOUTH=[m.resize((round(mw*scale),round(mh*scale)),Image.Resampling.LANCZOS) for m in MOUTH]

def render(t):
 im=BASE.copy();positions=[]
 for i,card in enumerate(CARDS):
  q=ease((t-.10-i*.09)/.52);dy=round(12*(1-q));opacity=.50+.50*q
  x=446+i*480;y=354+dy
  # The card outline and its image move together; their contents never clip each other.
  shadow(im,(x,y,x+448,y+612),16,11,5,(0,4))
  art=card.copy();art.putalpha(art.getchannel('A').point(lambda a:round(a*opacity)))
  im.alpha_composite(art,(x,y));positions.append([x,y,x+448,y+612])
 py=600+round(math.sin(t*2.0)*2);px=-1
 actor=SPRITE.copy()
 lo=max(0,round((t-.02)*24000));hi=min(len(PCM),round((t+.025)*24000))
 sample=PCM[lo:hi].astype(np.float32)/32768;rms=float(np.sqrt(np.mean(sample*sample))) if len(sample) else 0
 state=0 if rms<.011 else 1 if rms<.055 else 2 if rms<.13 else 3
 actor.alpha_composite(MOUTH[state],(round((mx-mw/2)*scale),round((my-mh/2)*scale)))
 d=ImageDraw.Draw(im);d.ellipse((86,1007,325,1022),fill=(68,91,102,32))
 im.alpha_composite(actor,(px,py))
 q=ease((t-.28)/.32)
 bubble=BUBBLE.copy();bubble.putalpha(bubble.getchannel('A').point(lambda a:round(a*q)))
 im.alpha_composite(bubble,(BX,BY))
 return im.convert('RGB'),{'time':t,'card_rects':positions,'bubble_rect':[BX,BY,BX+BW,BY+BH],'bubble_tail_tip':[BX+167,BY+301],
 'presenter_rect':[px,py,px+425,py+425],'mouth_state':state,'speech_rms':rms,'chapter_width':TITLE_W}

def main():
 for t in (.35,1.1,2.4,4.6):
  im,_=render(t);im.save(ROOT/'检查'/f'版式_{t}.png')
 render(2.4)[0].save(ROOT/'交付'/'三地情境_海洋知识动画版式_v33.png')
 if '--preview' in sys.argv:return
 out=ROOT/'交付'/'海洋知识动画版式_5秒样片_v33.mp4'
 cmd=[EXE,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(AUDIO),'-c:v','libx264',
 '-preset','fast','-crf','18','-pix_fmt','yuv420p','-vf','setsar=1','-c:a','aac','-b:a','160k','-t','5','-movflags','+faststart',str(out)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE);audit=[]
 for n in range(120):
  im,meta=render(n/24)
  assert all(410<=x<z<=1888 and 338<=y<b<=1000 for x,y,z,b in meta['card_rects'])
  assert meta['bubble_rect'][2]<PANEL[0]-20
  assert meta['bubble_tail_tip'][1]<meta['presenter_rect'][1]+70
  audit.append(meta);proc.stdin.write(im.tobytes())
 proc.stdin.close();err=proc.stderr.read();assert proc.wait()==0,err
 check=subprocess.run([EXE,'-v','error','-i',str(out),'-f','null','-'],capture_output=True)
 assert check.returncode==0 and not check.stderr,check.stderr
 report={'output':str(out),'resolution':[1920,1080],'seconds':5,'fps':24,'frames_checked':120,'decode':'PASS','new_voice_synthesis':False,
 'chapter_width':TITLE_W,'fonts':{'chapter':'得意黑58','subchapter':'微软雅黑27','dialogue':'微软雅黑39','main_question':'微软雅黑粗体44','caption':'微软雅黑35'},
 'content':WORDS,'text_geometry':STATIC_RECORDS+BUBBLE_RECORDS,'card_geometry':CARD_RECORDS,'visual_review':'待版式抽帧复核','sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
 (ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'检查'/'逐帧布局记录.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'output':str(out),'seconds':5,'decode':'PASS'},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
