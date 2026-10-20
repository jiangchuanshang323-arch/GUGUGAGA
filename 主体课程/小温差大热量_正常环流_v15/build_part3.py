from pathlib import Path
import sys,json,math,inspect,asyncio,subprocess,wave,re,hashlib
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
for x in ('素材','配音','.build','交付'):(ROOT/x).mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT.parent/'测体征_第二分钟_v10'))
import build_part2 as p
b=p.b;EXE=p.EXE;p.ROOT=ROOT
p.LINES=[
 ('回应','答案不在这半度，而在海洋有多大！',3),
 ('能量','同样升温，水量越大、比热容越大，对应的热量就越多。',8),
 ('小温差','所以，小温差背后，也可能是大热量。别把海洋当成一杯水！',3),
 ('过渡','测完体征，咕咕嘎嘎，换块板，咱们查病因！',3),
 ('方向','先看正常状态：左边西太平洋，右边东太平洋。',3),
 ('信风','近海面的东风信风，由东向西吹，把表层暖水推向西边。',6),
 ('水层','西侧暖水堆得厚，东侧暖水层薄。深层冷水在东侧上涌。',6),
 ('西升','西边暖池上方，暖湿空气上升，云和雨就多。',6),
 ('东沉','东侧相对冷，空气下沉，降水较少。',6),
 ('高空','高空空气再从西向东回流，和近海面的信风闭合起来。',6),
 ('沃克','这套大气环流，叫沃克环流。记住，西暖东冷，西升东沉！',8),
 ('悬念','要是信风变弱，这个平衡会怎样？下一步，我们看异常状态。',9),
]
audio_source=inspect.getsource(p.audio).replace("pause=3.0 if mode=='问题' else .10","pause=2.8 if mode=='过渡' else .10").replace('第二分钟_晓伊.wav','第三段_晓伊.wav')
exec(audio_source,p.__dict__)
LEFT=ROOT.parent/'跳起拉板_左向解说_v11'/'素材'/'20_朝左介绍.png'
PULL=ROOT/'素材'/'24_朝右双手侧拉.png'
MAP=ROOT/'素材'/'ENSO_blog_Bjerknes-feedback-Neutral_620.jpg'
ART=Image.open(PULL).convert('RGBA');LW,LH=Image.open(LEFT).size
S=350;SCALE=S/ART.width;GH=ART.height*SCALE;HX,HY=965,558
BRIDGE_START=BRIDGE_END=0
def ease(q):return b.ease(q)
def poly(s,points,fill,stroke=None,width=2):p.poly(s,points,fill,stroke,width)
def wrap(text,size,width):
 toks=[]
 for x in re.findall(r'[A-Za-zÀ-ÿ0-9]+(?:\.[0-9]+)*|.',text):
  if x in '，。？！：；、”）' and toks:toks[-1]+=x
  else:toks.append(x)
 out=[];line=''
 for x in toks:
  if line and b.F[size].getlength(line+x)>width:out.append(line);line=x
  else:line+=x
 if line:out.append(line)
 return out
def bubble(s,text,left,px,py,size):
 x=18 if left else 1500;width=395;font=40
 lines=wrap(text,font,width-40);height=51*len(lines)+40;y=max(70,py-height-25)
 mid=x+width*(.75 if left else .49);tip=(px+size*.52,py+size*.15)
 poly(s,[(mid-19,y+height-2),tip,(mid+19,y+height-2)],b.CREAM,'#98bcc8',3)
 s.rect(x,y,width,height,fill=b.CREAM,stroke='#98bcc8',width=3,r=25);s.rect(mid-15,y+height-6,30,9,fill=b.CREAM,stroke=None,r=0)
 for j,line in enumerate(lines):s.text(line,x+20,y+20+j*51,font,b.INK,'justify' if j<len(lines)-1 else 'left',width-40)
def presenter(s,pose,px,py,size,t,left=False):
 if not left and pose==3:
  s.ellipse(px+size*.2,py+size*.94,size*.63,14,'#bdc9c2');s.image(str(LEFT),px,py,size,size)
  sc=size/LW;state=p.prev.mouth(t)
  s.image(str(p.v.V3/'素材'/f'口型_03_{state}.png'),px+(590-33.5)*sc,py+(542-24.5)*sc,67*sc,49*sc)
 else:p.prev.presenter(s,pose,px,py,size,t)
def energy(s,t,mode):
 s.rect(24,140,1450,890,fill=b.CREAM,stroke='#98bcc6',width=3,r=30)
 s.text('小温差，为什么值得关注？',80,186,52,b.INK,w=1330)
 s.text('同样升温 +0.5℃',80,294,55,b.CORAL,'center',1330)
 s.rect(210,495,260,218,fill='#dcedef',stroke='#96bcc7',r=35)
 s.rect(690,423,600,290,fill='#dcedef',stroke='#96bcc7',r=35)
 for x,y,w,h in [(225,575,230,124),(705,530,570,169)]:
  points=[(x,y+h),(x,y)]+[(x+w*j/44,y+5*math.sin(j*.50+t*1.1)) for j in range(45)]+[(x+w,y+h)]
  poly(s,points,'#82bbcd')
  count=5 if w==230 else 18
  for j in range(count):
   xx=x+15+(j*37)%(w-30);yy=y+18+(j*41)%(h-30)+4*math.sin(t*1.5+j)
   s.ellipse(xx,yy,10,10,'#ffda94')
 s.text('水量少',175,742,42,b.BLUE,'center',330);s.text('水量大',705,742,42,b.CORAL,'center',580)
 s.text('热量 = 质量 × 比热容 × 温差',75,847,49,b.INK,'center',1335)
 if mode=='小温差':
  s.rect(593,957,770,60,fill='#ffedcc',stroke=None,r=18)
  s.text('小温差，也可能对应大热量',613,960,38,b.CORAL,'center',730)
def label(s,text,x,y,w=260,color=None,size=39):
 s.rect(x-8,y-4,w+16,55,fill=b.CREAM,stroke='#c5d8d9',width=1,r=13)
 s.text(text,x,y,size,color or b.INK,'center',w)
def arrow(s,points,color,width=7,progress=1):
 # Filled arrow head, correct direction, and progressive tracing.
 lengths=[math.hypot(c-a,d-bb) for (a,bb),(c,d) in zip(points,points[1:])];total=sum(lengths);remain=total*max(0,min(1,progress));draw=[points[0]]
 for i,length in enumerate(lengths):
  if remain>=length:draw.append(points[i+1]);remain-=length
  else:
   q=remain/max(1,length);a,bb=points[i];c,d=points[i+1];draw.append((a+(c-a)*q,bb+(d-bb)*q));break
 if len(draw)<2 or math.dist(draw[-1],draw[-2])<1:return
 s.line(draw,color,width);x,y=draw[-1];a,bb=draw[-2];ang=math.atan2(y-bb,x-a);r=17
 poly(s,[(x,y),(x-r*math.cos(ang-.48),y-r*math.sin(ang-.48)),(x-r*math.cos(ang+.48),y-r*math.sin(ang+.48))],color)
def mechanism(s,t,mode,age):
 s.rect(430,140,1465,890,fill=b.CREAM,stroke='#98bcc6',width=3,r=30)
 s.text('正常状态：先看海洋，再看大气',478,183,47,b.INK,w=1370)
 # Original NOAA image intact; separate Chinese annotations explain rather than redraw geography.
 mx,my,sc=610,275,1.74
 s.image(str(MAP),mx,my,620*sc,413*sc)
 def at(x,y):return mx+x*sc,my+y*sc
 label(s,'西太平洋',490,298,220,b.CORAL,39);label(s,'东太平洋',1640,298,220,b.BLUE,39)
 if mode in ('信风','水层','西升','东沉','高空','沃克','悬念'):
  arrow(s,[at(430,190),at(190,190)],b.CORAL,8,ease(age/.8) if mode=='信风' else 1)
  label(s,'东风信风：东 → 西',1100,647,425,b.CORAL,37)
 if mode in ('水层','西升','东沉','高空','沃克','悬念'):
  label(s,'西侧暖水层较厚',480,927,360,b.CORAL,36)
  label(s,'东侧暖水层较薄',1280,927,360,b.BLUE,36)
  arrow(s,[at(411,346),at(411,303)],b.BLUE,8,ease(age/.75) if mode=='水层' else 1)
  label(s,'冷水上涌',1487,811,265,b.BLUE,37)
 if mode in ('西升','东沉','高空','沃克','悬念'):
  arrow(s,[at(160,172),at(160,72)],b.CORAL,10,ease(age/.75) if mode=='西升' else 1)
  label(s,'暖湿空气上升',469,442,330,b.CORAL,35)
  if mode=='西升':
   for j in range(9):
    x,y=at(143+(j%3)*18,110+(j//3)*22+(t*22)%16);s.line([(x,y),(x-3,y+13)],'#65aac7',3)
 if mode in ('东沉','高空','沃克','悬念'):
  arrow(s,[at(405,72),at(405,172)],b.BLUE,10,ease(age/.75) if mode=='东沉' else 1)
  label(s,'空气下沉',1530,444,260,b.BLUE,36)
 if mode in ('高空','沃克','悬念'):
  arrow(s,[at(175,62),at(388,62)],b.CORAL,9,ease(age/1.0) if mode=='高空' else 1)
  label(s,'高空回流：西 → 东',983,321,450,b.CORAL,37)
 if mode in ('沃克','悬念'):
  label(s,'沃克环流',1000,981,365,b.CORAL,42)
  # Highlight the connected atmospheric loop, not an ocean current closing through the air.
  route=[at(160,174),at(160,62),at(405,62),at(405,174),at(190,190),at(160,174)]
  if mode=='沃克':arrow(s,route,'#dbad62',6,ease(age/1.4))
def scene(t):
 row=next((r for r in p.DATA if r['start']<=t<r['end']),p.DATA[0] if t<p.DATA[0]['start'] else p.DATA[-1]);mode=row['mode'];age=max(0,t-row['start']);s=b.Scene()
 s.image(str(b.BG),0,0,1920,1080)
 left=t>=BRIDGE_END
 s.text('查病因 · 正常海气环流' if left else '测体征 · 小温差，大热量',40,35,53,b.INK,w=1420)
 if left:mechanism(s,t,mode,age)
 else:energy(s,t,mode)
 px,py,size=(0,650,410) if left else (1510,660,390)
 walking=False
 if mode=='水层':
  px=200*ease(age/.6);walking=age<.6
 elif mode=='西升' and age<.6:
  px=200*(1-ease(age/.6));walking=True
 presenter(s,(13 if int(age/.15)%2==0 else 14) if walking else row['pose'],px,py+math.sin(t*1.6)*2,size,t,left)
 if not walking:bubble(s,row['text'],left,px,py,size)
 s.rect(0,1075,1920,5,fill='#d6e7e5',stroke=None,r=0);s.rect(0,1075,1920*t/p.DURATION,5,fill=b.BLUE,stroke=None,r=0)
 return s
source=inspect.getsource(p.v.render).replace("fw=b.F[a['size']].getlength(line)","fw=b.F[a['size']].getlength(line);y+=b.F[a['size']].getmetrics()[0]").replace("anchor='lt'","anchor='ls'")
source=source.replace("if t<.18:return Image.new('RGB',(W,H),'black')","if False:return im").replace("if t<.53:im=Image.blend","if False:im=Image.blend")
env=dict(p.v.__dict__);env['scene']=scene;exec(source,env);base_render=env['render']
OLD_BOARD=NEW_BOARD=None
def render(t):
 if not BRIDGE_START<=t<BRIDGE_END:return base_render(t)
 age=t-BRIDGE_START;im=Image.open(b.BG).convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS)
 if age<.65:
  q=ease(age/.65);im.paste(OLD_BOARD,(-round(1800*q),140),OLD_BOARD)
  s=b.Scene();p.prev.presenter(s,13 if int(age/.15)%2==0 else 14,1510+130*q,660,390,t)
  # Render just sprite layers against the existing stage without replacing its background.
  for item in s.items:
   if item['kind']=='image':
    art=b.img(item['path'],round(item['w']),round(item['h']));im.paste(art,(round(item['x']),round(item['y'])),art)
 elif age<2.20:
  q=ease((age-.65)/1.55);edge=1920+(430-1920)*q
  im.paste(NEW_BOARD,(round(edge),140),NEW_BOARD)
  x=edge+10-HX*SCALE;y=790-HY*SCALE
  art=ART.resize((S,round(GH)),Image.Resampling.LANCZOS);im.paste(art,(round(x),round(y)),art)
 else:
  q=ease((age-2.20)/.60);im.paste(NEW_BOARD,(430,140),NEW_BOARD)
  x=440-HX*SCALE;y=790-HY*SCALE
  held=im.copy();art=ART.resize((S,round(GH)),Image.Resampling.LANCZOS);held.paste(art,(round(x),round(y)),art)
  s=b.Scene();presenter(s,3,0,650,410,t,True)
  rest=im.copy()
  for item in s.items:
   if item['kind']=='image':
    art=b.img(item['path'],round(item['w']),round(item['h']));rest.paste(art,(round(item['x']),round(item['y'])),art)
  im=Image.blend(held,rest,q)
 return im
def main():
 global BRIDGE_START,BRIDGE_END,OLD_BOARD,NEW_BOARD
 asyncio.run(p.audio())
 row=next(r for r in p.DATA if r['mode']=='过渡');BRIDGE_START=row['speech_end'];BRIDGE_END=row['end']
 OLD_BOARD=base_render(BRIDGE_START-.2).crop((24,140,1474,1030)).convert('RGBA')
 NEW_BOARD=base_render(BRIDGE_END+.25).crop((430,140,1895,1030)).convert('RGBA')
 for mode in ('回应','小温差','方向','信风','水层','西升','东沉','高空','沃克'):
  row=next(r for r in p.DATA if r['mode']==mode);t=row['start']+(row['speech_end']-row['start'])*.65
  render(t).save(ROOT/f'预览_{mode}.png')
 for a in (.4,1.05,1.7,2.45):render(BRIDGE_START+a).save(ROOT/f'换板检查_{a}.png')
 if '--preview' in sys.argv:print(f'PREVIEW {p.DURATION:.2f}s',flush=True);return
 out=ROOT/'交付'/'海洋发烧了_第三段_小温差与正常环流_v15.mp4'
 cmd=[EXE,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(ROOT/'配音'/'第三段_晓伊.wav'),'-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)]
 with open(ROOT/'.build'/'encode.log','w') as log:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for n in range(math.ceil(p.DURATION*24)):
   proc.stdin.write(render(n/24).tobytes())
   if n%240==0:print(f'Render {n/24:.0f}/{p.DURATION:.2f}',flush=True)
  proc.stdin.close();assert proc.wait()==0
 result=subprocess.run([EXE,'-v','error','-i',str(out),'-f','null','-'],capture_output=True);assert result.returncode==0,result.stderr
 report=dict(decode='PASS',seconds=p.DURATION,chapters=['回答0.5℃互动','正常态东风信风与暖水/上升流','沃克环流闭合'],transition=[BRIDGE_START,BRIDGE_END],source_image='NOAA original image intact with separate Chinese annotations',no_full_concat=True,output=str(out))
 (ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(out,flush=True)
if __name__=='__main__':main()
