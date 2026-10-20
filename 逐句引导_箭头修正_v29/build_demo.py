from pathlib import Path
import sys,json,wave,math,inspect,subprocess
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
for folder in ('交付','.build'):(ROOT/folder).mkdir(parents=True,exist_ok=True)
OLD=ROOT.parent/'精绘厄尔尼诺_讲解演示_v28'
sys.path.insert(0,str(OLD));import build_demo as v
v.DATA=json.loads((OLD/'台词与时间轴.json').read_text(encoding='utf-8'))
with wave.open(str(OLD/'配音'/'精绘演示_晓伊.wav'),'rb') as w:v.PCM=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
v.DURATION=len(v.PCM)/24000
CLAUSES=[
 ['先分清两股气流：近海面的东风信风，从东向西吹，也就是从右向左。'],
 ['上面这根箭头是高空回流，从西向东。它不是信风。'],
 ['正常时，西侧暖水厚','空气上升','东侧冷水上涌','空气下沉'],
 ['当东风信风减弱','暖水向东扩展','东部温跃层加深','冷水上涌受到抑制'],
 ['中东太平洋持续异常增暖，这就是厄尔尼诺现象。'],
 ['对流和降雨区域随之东移','沃克环流减弱'],
 ['海温差缩小','又会进一步削弱信风','海洋与大气互相推动，形成正反馈。']]
# Boundaries follow punctuation and the nearest quiet window in the cached narration.
PHASES=[]
for row,clauses in zip(v.DATA,CLAUSES):
 weights=[len(x)for x in clauses];cum=0;bounds=[row['start']]
 for weight in weights[:-1]:
  cum+=weight;target=row['start']+(row['speech_end']-row['start'])*cum/sum(weights)
  candidates=np.arange(max(bounds[-1]+.35,target-.22),min(row['speech_end']-.25,target+.22),.01)
  def energy(t):
   a=v.PCM[max(0,round((t-.035)*24000)):round((t+.035)*24000)].astype(np.float32)
   return float(np.mean(a*a)) if len(a) else 1e12
  bounds.append(float(min(candidates,key=energy)) if len(candidates) else target)
 bounds.append(row['end'])
 for i,line in enumerate(clauses):PHASES.append({'id':len(PHASES),'text':line,'mode':row['mode'],'start':bounds[i],'end':bounds[i+1]})
ACTIVE=None

def fixed_arrow(im,points,color,width=10,dots=0,alpha=1):
 # Stop the shaft inside the arrowhead; never stroke all the way through its tip.
 points=[tuple(p)for p in points];r=width*2.5
 lengths=[math.dist(a,z)for a,z in zip(points,points[1:])];total=sum(lengths);cut=max(0,total-r*.82)
 shaft=[points[0]];remaining=cut
 for a,z,length in zip(points,points[1:],lengths):
  if remaining>=length:shaft.append(z);remaining-=length
  else:
   q=remaining/max(.001,length);shaft.append((v.mix(a[0],z[0],q),v.mix(a[1],z[1],q)));break
 tip=points[-1];base=shaft[-1];angle=math.atan2(tip[1]-base[1],tip[0]-base[0])
 margin=width*4+5;left=math.floor(min(x for x,y in points)-margin);top=math.floor(min(y for x,y in points)-margin)
 ww=math.ceil(max(x for x,y in points)+margin)-left;hh=math.ceil(max(y for x,y in points)+margin)-top
 art=Image.new('RGBA',(ww*2,hh*2));d=ImageDraw.Draw(art)
 cv=lambda p:((p[0]-left)*2,(p[1]-top)*2)
 d.line([cv(p)for p in shaft],fill=color,width=width*2,joint='curve')
 triangle=[tip,(tip[0]-r*math.cos(angle-.45),tip[1]-r*math.sin(angle-.45)),(tip[0]-r*math.cos(angle+.45),tip[1]-r*math.sin(angle+.45))]
 d.polygon([cv(p)for p in triangle],fill=color)
 if dots:
  for i in range(9):
   goal=((i/9+dots)%1)*cut
   for a,z,length in zip(points,points[1:],lengths):
    if goal>length:goal-=length;continue
    q=goal/max(.001,length);x,y=cv((v.mix(a[0],z[0],q),v.mix(a[1],z[1],q)));d.ellipse((x-5,y-5,x+5,y+5),fill='#fff7dd');break
 art=art.resize((ww,hh),Image.Resampling.LANCZOS)
 if alpha<1:art.putalpha(art.getchannel('A').point(lambda x:round(x*alpha)))
 im.paste(art,(left,top),art)

def arrow(im,points,color,width=10,dots=0,alpha=1):
 i=ACTIVE['id'];ys=[p[1]for p in points];xs=[p[0]for p in points]
 high=max(ys)<305;low=max(ys)<520 and min(ys)>490
 upwell=min(xs)>1550 and max(ys)>800
 warm=min(ys)>620 and max(ys)<700
 if high and i<1:return
 if upwell and (i<4 or 6<=i<9):return
 if warm and i<7:return
 if not(high or low or upwell or warm)and i<3:return
 focus=(i==0 and low)or(i==1 and high)or(i in (4,9)and upwell)or(i==7 and warm)
 fixed_arrow(im,points,color,width,dots,alpha if focus else alpha*.55)

oldpill=v.pill
def pill(im,words,x,y,width,size=40,color=v.INK,fill=v.CREAM,height=62):
 i=ACTIVE['id']
 if words.startswith('高空回流')and i not in (1,2,3,4,5,12):return
 if words=='表层暖水'and i not in (2,7,10,13):return
 if words=='深层冷水'and i not in (4,9):return
 if words=='温跃层':
  if i!=8:return
  x,y=850,818
 if words.startswith('冷水上涌'):
  if i not in (4,9):return
  x,y,width=1090,824,450
 if words=='东部温跃层加深':
  if i!=8:return
  x,y=1220,594
 if words in ('沃克环流减弱','海气正反馈')and i not in (12,15):return
 if words=='空气上升'and i!=3:return
 if words=='空气下沉'and i not in (5,11):return
 if words.startswith('近海面东风信风'):
  if i not in (0,1,6,12,14,15):return
  words='近海面东风信风：西 ← 东' if i<6 else '东风信风减弱：西 ← 东'
 oldpill(im,words,x,y,width,size,color,fill,height)

def params(t,row):
 i=ACTIVE['id']
 def q(index,length):return v.ease((t-PHASES[index]['start'])/length)
 wind=q(6,1.2)if i>=6 else 0
 water=0 if i<7 else .45*q(7,max(.5,PHASES[7]['end']-PHASES[7]['start']))if i==7 else .45+.55*q(8,max(.5,PHASES[8]['end']-PHASES[8]['start']))
 air=q(11,max(.8,PHASES[11]['end']-PHASES[11]['start']-.1))if i>=11 else 0
 return wind,water,air

v.arrow=arrow;v.pill=pill;v.params=params
oldtext=v.text
def world_text(im,words,x,y,size=42,color=v.INK,center=False):
 if words.startswith(('西太平洋','东太平洋')):return
 oldtext(im,words,x,y,size,color,center)
v.text=world_text
source=inspect.getsource(v.render)
a=source.index(' # Natural layered cloud');z=source.index(' # The low branch',a)
block=source[a:z]
source=source[:a]+' if ACTIVE[\'id\']>=3:\n'+''.join(' '+line+'\n'for line in block.splitlines())+source[z:]
source=source.replace("text(im,'分清气流方向，看懂海气联动',75,96,33,BLUE)","text(im,'分清气流方向，看懂海气联动',75,96,33,BLUE)")
v.__dict__['ACTIVE']=None
exec(source,v.__dict__);world_render=v.render

FOCUS=[
 ((400,466,590,542),(850,510),1.12),
 ((1380,245,1535,320),(1240,290),1.18),
 ((170,600,475,780),(420,690),1.28),
 ((350,415,505,515),(425,432),1.22),
 ((1535,585,1705,885),(1560,737),1.35),
 ((1450,312,1570,495),(1450,400),1.20),
 ((1090,458,1510,552),(1230,501),1.18),
 ((680,617,1490,704),(1120,663),1.22),
 ((1510,716,1750,795),(1570,747),1.30),
 ((1530,745,1720,887),(1600,808),1.35),
 ((1090,570,1740,784),(1340,689),1.21),
 ((825,225,1375,474),(1110,345),1.26),
 ((500,240,1580,510),(1040,377),1.12),
 ((480,580,1750,778),(1200,690),1.14),
 ((1090,458,1520,552),(1230,501),1.17),
 ((470,330,885,418),(790,480),1.05)]

def circle(im,bounds,progress):
 x,y,x2,y2=bounds;ww=round(x2-x)+20;hh=round(y2-y)+20
 art=Image.new('RGBA',(ww*2,hh*2));d=ImageDraw.Draw(art)
 d.arc((20,20,(ww-10)*2,(hh-10)*2),-110,-110+359*v.ease(progress),fill='#de9760',width=12)
 art=art.resize((ww,hh),Image.Resampling.LANCZOS);im.paste(art,(round(x-10),round(y-10)),art)

def render(t):
 global ACTIVE
 ACTIVE=next((p for p in PHASES if p['start']<=t<p['end']),PHASES[-1]);v.__dict__['ACTIVE']=ACTIVE
 row=next((r for r in v.DATA if r['start']<=t<r['end']),v.DATA[-1]);i=ACTIVE['id'];age=t-ACTIVE['start']
 im=world_render(t,False);box,center,zoom=FOCUS[i]
 circle(im,box,(age-.14)/.48)
 # Camera zoom applies only to the scientific illustration; title and subtitles stay fixed.
 blend=v.ease(age/.65)*v.ease((ACTIVE['end']-t)/.40)
 factor=1+(zoom-1)*blend;cw=1800/factor;ch=730/factor
 x=max(60,min(1860-cw,center[0]-cw/2));y=max(178,min(908-ch,center[1]-ch/2))
 if factor>1.001:im.paste(im.crop((round(x),round(y),round(x+cw),round(y+ch))).resize((1800,730),Image.Resampling.LANCZOS),(60,178))
 oldtext(im,'西侧（印尼方向）',100,181,38)
 oldtext(im,'东侧（秘鲁方向）',1440,181,38)
 # Current spoken clause alone: reduces visual and subtitle load for beginners.
 d=ImageDraw.Draw(im);d.rectangle((0,958,1920,1080),fill='#244559')
 text=ACTIVE['text'];lines=[];line=''
 for char in text:
  if line and v.F[46].getlength(line+char)>1770:lines.append(line);line=char
  else:line+=char
 if line:lines.append(line)
 for j,line in enumerate(lines):v.text(im,line,960,(966 if len(lines)>1 else 988)+j*54,46,'#fffaf0',True)
 return im

def main():
 (ROOT/'逐句引导时间轴.json').write_text(json.dumps(PHASES,ensure_ascii=False,indent=2),encoding='utf-8')
 sheet=Image.new('RGB',(1920,720),v.CREAM)
 for j,i in enumerate((0,1,4,8,11,15)):
  p=PHASES[i];t=p['start']+min(.85,(p['end']-p['start'])*.65);im=render(t);im.save(ROOT/f'检查_{i}.png');sheet.paste(im.resize((640,360)),((j%3)*640,(j//3)*360))
 sheet.save(ROOT/'逐句引导_六帧.jpg')
 if '--preview' in sys.argv:return
 out=ROOT/'交付'/'厄尔尼诺_逐句出现圈选推近_demo_v29.mp4'
 cmd=[v.EXE,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(OLD/'配音'/'精绘演示_晓伊.wav'),'-vf','setsar=1','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)]
 with (ROOT/'.build'/'encode.log').open('w')as log:
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for n in range(math.ceil(v.DURATION*24)):
   p.stdin.write(render(n/24).tobytes())
   if n%240==0:print(f'Render {n/24:.0f}/{v.DURATION:.1f}',flush=True)
  p.stdin.close();assert p.wait()==0
 r=subprocess.run([v.EXE,'-v','error','-i',str(out),'-f','null','-'],capture_output=True);assert r.returncode==0 and not r.stderr.strip(),r.stderr
 (ROOT/'验证.json').write_text(json.dumps({'decode':'PASS','seconds':v.DURATION,'shaft_trimmed_before_tip':True,'surface_label':'西 ← 东','progressive_reveal':True,'circle_and_camera_zoom':True,'perspective':'2D zoom, no 3D conversion','cached_audio_only':True,'no_concat':True},ensure_ascii=False,indent=2),encoding='utf-8')
 print(out,flush=True)
if __name__=='__main__':main()
