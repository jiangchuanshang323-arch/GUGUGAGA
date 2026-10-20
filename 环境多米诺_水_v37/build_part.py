from pathlib import Path
import sys, math, json, wave, subprocess, asyncio, hashlib, importlib.util
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parent; PROJECT=ROOT.parent
for name in ('交付','素材','配音','检查','.build'):(ROOT/name).mkdir(exist_ok=True)
sys.path.insert(0,str(PROJECT/'ocean_animation_demo_20261011'/'runtime'))
sys.path.insert(0,str(PROJECT/'正常异常对照_区域预测_v36'/'.runtime'))
import imageio_ffmpeg,edge_tts
EXE=imageio_ffmpeg.get_ffmpeg_exe()
spec=importlib.util.spec_from_file_location('previous36',PROJECT/'正常异常对照_区域预测_v36'/'build_part.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
INK,BLUE,CORAL,CREAM=p.INK,p.BLUE,p.CORAL,p.CREAM
font=p.font; ease=p.ease
LINES=[
 ('回扣','先揭晓预测。关键是气流在哪里升降。'),
 ('西侧','印尼一侧，上升对流减弱，降水偏少，干旱风险增加。'),
 ('东侧','对流和降雨向东移动。强事件中，偏多降雨可延伸到秘鲁北部沿岸。'),
 ('整体','自然环境具有整体性，牵一发而动全身。'),
 ('五牌','下面沿着水、气、生、土、地形五张牌，追踪这场环境多米诺。'),
 ('选水','先翻开第一张，水。环流改变，让降水重新分配。'),
 ('全球','这张官方图，展示十二月到二月厄尔尼诺的典型影响。'),
 ('偏干','先找印尼一带，偏干；原本湿润的地方，干旱风险可能增加。'),
 ('偏湿','赤道中东太平洋偏暖、偏湿；影响还要看季节和事件强度。'),
 ('少雨','降雨的变化，还会传到河流。持续少雨，雨水补给减少，缺水风险增加。'),
 ('强雨','强降雨集中，地表径流可能迅速增加，洪涝风险上升。'),
 ('风险','一些地区要防旱，另一些地区要防涝。'),
 ('承下','记住：环流变化，降水重分配，再影响水循环。')]
DATA=[];PCM=np.zeros(1,dtype='<i2');DURATION=0

async def audio():
 global DATA,PCM,DURATION
 parts=[np.zeros(4800,dtype='<i2')];cursor=.2;DATA=[]
 for i,(mode,words) in enumerate(LINES):
  f=ROOT/'配音'/f'{i:02d}_{mode}.mp3'
  if not f.exists() or f.stat().st_size<1000:
   await edge_tts.Communicate(words,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz').save(str(f))
  raw=subprocess.check_output([EXE,'-v','error','-i',str(f),'-f','s16le','-ar','24000','-ac','1','-'])
  a=np.frombuffer(raw,dtype='<i2');nz=np.flatnonzero(np.abs(a.astype(np.int32))>220)
  if len(nz):a=a[max(0,nz[0]-480):min(len(a),nz[-1]+600)]
  gap=.10 if i<len(LINES)-1 else .30
  DATA.append(dict(mode=mode,text=words,start=cursor,speech_end=cursor+len(a)/24000,end=cursor+len(a)/24000+gap))
  parts.extend([a,np.zeros(round(gap*24000),dtype='<i2')]);cursor=DATA[-1]['end']
  print('Voice',i+1,round(cursor,2),flush=True)
 PCM=np.concatenate(parts);DURATION=len(PCM)/24000
 with wave.open(str(ROOT/'配音'/'环境多米诺_水_晓伊.wav'),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(PCM.tobytes())
 (ROOT/'台词与时间轴.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2),encoding='utf-8')

def load_audio():
 global DATA,PCM,DURATION
 DATA=json.loads((ROOT/'台词与时间轴.json').read_text(encoding='utf-8'))
 with wave.open(str(ROOT/'配音'/'环境多米诺_水_晓伊.wav'),'rb') as w:PCM=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
 DURATION=len(PCM)/24000

def text(im,s,x,y,size=42,color=INK,center=False,records=None):
 return p.text(im,s,x,y,size,color,center,records)
def card(im,s,box,size=38,color=INK,records=None):
 return p.card(im,s,box,size,color,records)
HEADS={k:p.header(a,b) for k,a,b in [
 ('回扣','预测揭晓 · 两侧为何不同','先看气流，再看降水'),
 ('多米诺','追并发症 · 环境多米诺','从海气异常，追踪地理要素的联系'),
 ('水','第一张 · 水','环流变化 → 降水重分配 → 水循环响应')]}
BG=Image.open(PROJECT/'主体课程'/'正文日系2D_配音_v2'/'素材'/'日系2D水下课堂.png').convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS)
NOAA=Image.open(ROOT/'素材'/'NOAA_冬季全球影响_原图.png').convert('RGB')
# Only select the original El Nino panel. Coastlines, source colours, and projection are unchanged.
GLOBAL=NOAA.crop((0,70,1800,810))
GLOBAL.save(ROOT/'素材'/'NOAA_厄尔尼诺上半图_原比例.png')
SPRITES=PROJECT/'企鹅小老师_教学动作素材_20261012'/'独立动作PNG'
POSES={i:Image.open(next(SPRITES.glob(f'{i:02d}_*.png'))).convert('RGBA') for i in (3,4,5,6,7)}
MOUTH_DIR=PROJECT/'主体课程'/'正文晓伊_口型与大画面_v3'/'素材'
MOUTH_CENTERS={3:(266,229,43,37),4:(306,220,35,29),5:(274,218,35,29),6:(227,218,50,44),7:(288,235,50,44)}
@lru_cache(None)
def mouth(pose,state):return Image.open(MOUTH_DIR/f'口型_{pose:02d}_{state}.png').convert('RGBA')

def penguin(im,t,age):
 pose=6 if age>1 else 5
 if 1.5<age<1.7:pose=7
 if age>4:pose=4 if age%4.5>4.34 else 3
 size=350;x=38;y=590+math.sin(t*1.6)*2
 body=POSES[pose].resize((size,size),Image.Resampling.LANCZOS)
 im.paste(body,(x,round(y)),body)
 lo=max(0,int((t-.02)*24000));hi=min(len(PCM),int((t+.025)*24000));a=PCM[lo:hi].astype(np.float32)/32768
 rms=float(np.sqrt(np.mean(a*a))) if len(a) else 0
 state=0 if rms<.011 else 1 if rms<.055 else 2 if rms<.13 else 3
 mx,my,mw,mh=MOUTH_CENTERS[pose];s=size/512
 m=mouth(pose,state).resize((round(mw*s),round(mh*s)),Image.Resampling.LANCZOS)
 im.paste(m,(round(x+(mx-mw/2)*s),round(y+(my-mh/2)*s)),m)

COLORS=['#6dabc0','#e0bb7e','#8eb69e','#c6947e','#a8a6bd']
def icon(d,kind,cx,cy,color,scale=1):
 s=scale
 if kind==0:
  pts=[(cx,cy-43*s),(cx-26*s,cy),(cx-22*s,cy+24*s),(cx,cy+34*s),(cx+22*s,cy+24*s),(cx+26*s,cy)]
  d.polygon(pts,fill=color);d.arc((cx-15*s,cy-8*s,cx+13*s,cy+24*s),20,110,fill='#edf9fb',width=max(2,round(4*s)))
 elif kind==1:
  for j in range(3):d.arc((cx-45*s,cy-29*s+j*22*s,cx+30*s,cy+2*s+j*22*s),180,355,fill=color,width=max(2,round(5*s)))
 elif kind==2:
  d.ellipse((cx-38*s,cy-26*s,cx+23*s,cy+26*s),fill=color);d.polygon([(cx+17*s,cy),(cx+43*s,cy-25*s),(cx+43*s,cy+25*s)],fill=color);d.ellipse((cx-24*s,cy-8*s,cx-18*s,cy-2*s),fill=CREAM)
 elif kind==3:
  for j in range(3):d.rounded_rectangle((cx-42*s,cy-30*s+j*23*s,cx+42*s,cy-13*s+j*23*s),4*s,fill=color)
 else:
  d.polygon([(cx-46*s,cy+30*s),(cx-6*s,cy-34*s),(cx+15*s,cy+3*s),(cx+29*s,cy-15*s),(cx+48*s,cy+30*s)],fill=color)

def tile(im,kind,box,selected=False,angle=0):
 x,y,z,b=box;w=z-x;h=b-y
 a=Image.new('RGBA',(round(w+35),round(h+35)));d=ImageDraw.Draw(a)
 d.polygon([(w,13),(w+17,0),(w+17,h-15),(w,h)],fill='#a4b9bc')
 d.polygon([(0,13),(17,0),(w+17,0),(w,13)],fill='#e5eeeb')
 d.rounded_rectangle((0,13,w,h),20,fill='#fff9ed' if selected else '#eef2ee',outline=COLORS[kind],width=4 if selected else 2)
 d.rounded_rectangle((18,33,w-18,45),5,fill=COLORS[kind])
 icon(d,kind,w/2,h*.40,COLORS[kind],min(w/170,h/260))
 word=['水','气','生','土','地形'][kind];f=font(round(min(w*.45,64 if kind<4 else 49)));bb=f.getbbox(word)
 d.text(((w-(bb[2]-bb[0]))/2-bb[0],h*.64-bb[1]),word,font=f,fill=INK)
 if angle:a=a.rotate(angle,Image.Resampling.BICUBIC,expand=True,center=(0,a.height))
 im.paste(a,(round(x),round(y)),a)

def reveal(mode,t,records):
 im=Image.new('RGB',(1920,1080),CREAM);im.paste(p.MAP,(60,180))
 im.paste(HEADS['回扣'],(16,14),HEADS['回扣']);d=ImageDraw.Draw(im)
 for pt,label,box,color in [(p.INDO,'印尼 · 西太平洋',(115,445,445,508),BLUE),(p.PERU,'秘鲁 · 东太平洋',(1480,488,1825,551),CORAL)]:
  x,y=pt;d.ellipse((x-7,y-7,x+7,y+7),fill=CREAM,outline=color,width=3);d.line(((box[0]+box[2])/2,box[3],x,y-13),fill='#d7e7e9',width=3);card(im,label,box,38,color,records)
 card(im,'降水：偏少' if mode in ('西侧','东侧') else '降水：？',(115,735,465,806),42,BLUE,records)
 card(im,'降水：可能偏多' if mode=='东侧' else '降水：？',(1430,735,1825,806),40,CORAL,records)
 if mode=='西侧':
  card(im,'上升对流减弱 → 偏干',(160,285,750,365),43,BLUE,records)
 if mode=='东侧':
  card(im,'强事件：秘鲁北部沿岸可偏湿',(810,300,1740,385),41,CORAL,records)
 return im

def domino(mode,t,age,records):
 im=BG.copy();im.paste(HEADS['多米诺'],(16,14),HEADS['多米诺']);d=ImageDraw.Draw(im)
 d.rounded_rectangle((360,190,1860,925),28,fill=CREAM,outline='#a6c4cc',width=2)
 text(im,'自然环境具有整体性',1115,240,51,INK,True,records)
 text(im,'牵一发而动全身',1115,318,64,CORAL,True,records)
 labels=['水','气','生','土','地形']
 select=mode=='选水';q=ease(age/1.15) if select else 0
 for i in reversed(range(5)):
  x=480+i*270;y=510-i*25;w=210-i*9;h=330-i*13
  if i==0 and select:x-=q*14;y-=q*28;w+=q*32;h+=q*38
  elif select:y+=q*22;w*=1-.08*q;h*=1-.08*q
  d.ellipse((x-5,y+h-8,x+w+38,y+h+28),fill='#e0e8e5')
  tile(im,i,(x,y,x+w,y+h),selected=(i==0 and select))
 penguin(im,t,age)
 if select:text(im,'第一张：降水与水循环',990,849,43,BLUE,True,records)
 return im

def global_map(mode,t,records):
 im=Image.new('RGB',(1920,1080),CREAM);im.paste(HEADS['水'],(16,14),HEADS['水']);im.paste(GLOBAL,(60,180));d=ImageDraw.Draw(im)
 text(im,'典型影响 · 12月至次年2月',1360,22,32,INK,True,records)
 # All eight native legend categories remain available in Chinese; no map region is covered.
 legends=[('#4d91c6','偏冷'),('#4d9d85','偏湿'),('#a3d0e5','偏冷干'),('#4c7287','偏冷湿'),('#f69c76','偏暖'),('#d6c19a','偏干'),('#b18443','偏暖干'),('#b2d19a','偏暖湿')]
 for i,(color,label) in enumerate(legends):
  x=885+i%4*242;y=75+i//4*49
  d.rounded_rectangle((x,y,x+38,y+28),5,fill=color);text(im,label,x+51,y,26,INK,False,records)
 if mode in ('偏干','偏湿'):
  dry=mode=='偏干';target=(785,661) if dry else (1245,650)
  box=(570,360,1040,437) if dry else (1090,360,1710,437)
  card(im,'印尼一带 · 偏干' if dry else '赤道中东太平洋 · 偏暖湿',box,40,BLUE if dry else CORAL,records)
  d.line(((box[0]+box[2])/2,box[3],target[0],target[1]-19),fill=BLUE if dry else CORAL,width=3)
  d.ellipse((target[0]-7,target[1]-7,target[0]+7,target[1]+7),fill=CREAM,outline=BLUE if dry else CORAL,width=3)
 return im

def hydro(mode,t,age,records):
 im=BG.copy();im.paste(HEADS['水'],(16,14),HEADS['水']);d=ImageDraw.Draw(im)
 d.rounded_rectangle((60,180,1860,925),28,fill=CREAM,outline='#a6c4cc',width=2)
 text(im,'降水重分配，怎样传到河流？',960,230,54,INK,True,records)
 # Two causal branches share a stable scale; each appears in speech order.
 branch=1 if mode=='少雨' else 2
 for side,title,items,color in [(0,'持续少雨',['降水减少','河流补给减少','低流量 / 缺水风险'],BLUE),(1,'强降雨集中',['降水集中','地表径流增加','洪涝风险增加'],CORAL)]:
  x=140+side*900
  visible=side==0 or branch==2
  if not visible:continue
  card(im,title,(x,340,x+740,418),47,color,records)
  for j,s in enumerate(items):
   box=(x+65,460+j*125,x+675,540+j*125)
   if side==0 and j==1:s='雨水补给减少'
   card(im,s,box,42,color if j==2 else INK,records)
   if j<2:p.native.arrow(im,[(x+370,box[3]+10),(x+370,box[3]+37)],color,5,1)
 if mode=='承下':
  d.rounded_rectangle((300,825,1620,903),18,fill='#e7f0ef',outline='#a9c7cf',width=2)
  text(im,'环流变化 → 降水重分配 → 区域水循环响应',960,845,42,INK,True,records)
 return im

PREVIOUS=None
def scene(mode,t,age,records):
 if mode in ('回扣','西侧','东侧'):return reveal(mode,t,records)
 if mode in ('整体','五牌','选水'):return domino(mode,t,age,records)
 if mode in ('全球','偏干','偏湿'):return global_map(mode,t,records)
 return hydro(mode,t,age,records)

def render(t):
 row=next((r for r in DATA if r['start']<=t<r['end']),DATA[0] if t<DATA[0]['start'] else DATA[-1]);records=[]
 age=max(0,t-row['start']);im=scene(row['mode'],t,age,records)
 # A brief dissolve only at real scene changes. Labels never inherit camera transforms.
 if row['mode'] in ('整体','全球','少雨') and age<.45:
  idx=DATA.index(row);before=DATA[idx-1]
  old=scene(before['mode'],before['end']-.02,before['end']-before['start']-.02,[])
  im=Image.blend(old,im,ease(age/.45))
 if PREVIOUS is not None and t<.4:im=Image.blend(PREVIOUS,im,ease(t/.4))
 d=ImageDraw.Draw(im);d.rectangle((0,958,1920,1080),fill='#244b60')
 words=row['text'];lines=[];line=''
 for ch in words:
  if font(46).getlength(line+ch)>1750:lines.append(line);line=ch
  else:line+=ch
 if line:lines.append(line)
 assert len(lines)<=2
 yy=965 if len(lines)>1 else 987
 for line in lines:text(im,line,960,yy,46,'#fffaf0',True,records);yy+=49
 return im,dict(time=t,mode=row['mode'],labels=records,main_emphasis_count=1 if row['mode'] in ('西侧','东侧','选水','偏干','偏湿') else 0,camera_fixed=True)

def main():
 global PREVIOUS
 if '--audio' in sys.argv:asyncio.run(audio());return
 load_audio()
 prev=ROOT/'.build'/'v36结束帧.png'
 if not prev.exists():subprocess.run([EXE,'-v','error','-sseof','-0.5','-i',str(PROJECT/'demooo'/'独立片段'/'04_对照与预测'/'海洋发烧了_第四段_对照与预测.mp4'),'-frames:v','1','-y',str(prev)],check=True)
 PREVIOUS=Image.open(prev).convert('RGB')
 times=[min(r['start']+.8,r['end']-.05) for r in DATA]
 contact=Image.new('RGB',(1920,math.ceil(len(times)/4)*300),'#e8f0ef');d=ImageDraw.Draw(contact)
 for i,t in enumerate(times):
  im,_=render(t);im.save(ROOT/'检查'/f'节点_{i:02d}.png');x=i%4*480;y=i//4*300
  contact.paste(im.resize((480,270),Image.Resampling.LANCZOS),(x,y));d.text((x+8,y+277),f'{t:.2f}s',fill=INK)
 contact.save(ROOT/'检查'/'内容节点检查.jpg',quality=95)
 if '--preview' in sys.argv:return
 out=ROOT/'交付'/'海洋发烧了_第五段_环境多米诺水_v37.mp4'
 cmd=[EXE,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(ROOT/'配音'/'环境多米诺_水_晓伊.wav'),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-vf','setsar=1','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE);nframes=math.ceil(DURATION*24);audit=[]
 for n in range(nframes):
  im,meta=render(n/24);audit.append(meta);proc.stdin.write(im.tobytes())
  if n%240==0:print('Render',n,'/',nframes,flush=True)
 proc.stdin.close();err=proc.stderr.read();assert proc.wait()==0,err
 result=subprocess.run([EXE,'-v','error','-i',str(out),'-f','null','-'],capture_output=True)
 assert result.returncode==0 and not result.stderr,result.stderr
 (ROOT/'检查'/'逐帧版面检查.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 report=dict(output=str(out),seconds=DURATION,resolution=[1920,1080],fps=24,frames_checked=nframes,decode='PASS',visual_review='待抽帧复核',source_word=str(PROJECT/'00_原始资料'/'《海洋“发烧”了》批注版.docx'),word_shots=[13,14,15],categories=['水','气','生','土','地形'],standalone=True,sha256=hashlib.sha256(out.read_bytes()).hexdigest())
 (ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
