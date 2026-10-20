from pathlib import Path
import sys,math,json,asyncio,subprocess,wave,hashlib
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'上抛后恢复普通姿势_v23'));import build_v23 as previous
sys.path.insert(0,str(ROOT.parent/'正文日系2D_配音_v2'/'runtime'));import edge_tts
b=previous.b;EXE=previous.v.EXE
for folder in ('素材','配音','.build','交付'):(ROOT/folder).mkdir(exist_ok=True)
NORMAL=Image.open(ROOT.parent/'抛卷轴_高清全屏_v17'/'素材'/'NOAA_正常态_1860原图.jpg').convert('RGB').crop((0,102,1860,1209))
EL=Image.open(ROOT/'素材'/'NOAA_厄尔尼诺_1860原图.jpg').convert('RGB').crop((0,102,1860,1209))
NORMAL_BIG=NORMAL.resize((1750,1042),Image.Resampling.LANCZOS)
EL_BIG=EL.resize((1750,1042),Image.Resampling.LANCZOS)
MAP_SOURCE=ROOT.parent/'右侧左指_批注落实_v8'/'素材'/'NOAA_PSL_ENSO区域图.png'
MAP=Image.open(MAP_SOURCE).convert('RGB').resize((1820,round(244*1820/685)),Image.Resampling.LANCZOS)
LINES=[
 ('承接','信风变弱，刚才的平衡就会改变。'),
 ('信风','先看近海面：由东向西吹的东风信风减弱，推动暖水向西的力量变小。'),
 ('暖水','暖水向中东太平洋扩展，东部温跃层加深，冷水上升流受到抑制。'),
 ('海温','冷水补给减少，中东太平洋海面增暖，东西海温差随之缩小。'),
 ('大气','对流和降雨区域向东移动，沃克环流减弱。'),
 ('反馈','海温差缩小，又会进一步削弱信风。海洋和大气互相推动，形成正反馈。'),
 ('对照风','对照两幅图：正常年东风信风较强；厄尔尼诺年，信风减弱。'),
 ('对照水','暖水不再主要堆在西侧，而是向东扩展；东部上升流也减弱。'),
 ('对照气','沃克环流减弱，降雨区域东移。关键是海洋异常带动了大气响应。'),
 ('预测','再看地图：印尼在西侧，秘鲁在东侧。根据气流变化，两地降水会怎样？'),
 ('思考','先作出预测，再用下一段的案例验证。'),
]
DATA=[];PCM=None;DURATION=0

async def audio():
 global DATA,PCM,DURATION
 cursor=0;parts=[];DATA=[]
 for i,(mode,text) in enumerate(LINES):
  assert '咕咕嘎嘎' not in text
  file=ROOT/'配音'/f'{i+1:02d}_{mode}.mp3'
  if not file.exists():
   for attempt in range(3):
    try:
     await edge_tts.Communicate(text,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=40).save(str(file));break
    except Exception:
     if attempt==2:raise
     await asyncio.sleep(1)
  raw=subprocess.check_output([EXE,'-v','error','-i',str(file),'-f','s16le','-ar','24000','-ac','1','-'])
  a=np.frombuffer(raw,dtype='<i2');idx=np.flatnonzero(np.abs(a.astype(np.int32))>220)
  if len(idx):a=a[max(0,idx[0]-720):min(len(a),idx[-1]+960)]
  pause=3.0 if mode=='思考' else .10
  duration=len(a)/24000
  DATA.append({'mode':mode,'text':text,'start':cursor,'speech_end':cursor+duration,'end':cursor+duration+pause,'word_shot':11 if i<6 else 12 if i<9 else 13})
  parts.extend([a,np.zeros(round(pause*24000),dtype='<i2')]);cursor+=duration+pause
  print(f'Voice {i+1}/{len(LINES)}',flush=True)
 PCM=np.concatenate(parts);DURATION=len(PCM)/24000
 with wave.open(str(ROOT/'配音'/'第四段_异常环流_晓伊.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(PCM.tobytes())
 (ROOT/'台词与时间轴.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2),encoding='utf-8')

def ease(q):return b.ease(q)
def text(im,t,x,y,size=44,color=None,center=False):
 d=ImageDraw.Draw(im);font=b.F[size];color=color or b.INK
 if center:x-=font.getlength(t)/2
 d.text((x,y+font.getmetrics()[0]),t,font=font,fill=color,anchor='ls')
def chip(im,t,x,y,w,size=44,color=None):
 d=ImageDraw.Draw(im);d.rounded_rectangle((x,y,x+w,y+62),radius=16,fill=b.CREAM,outline='#c8d9da',width=2)
 text(im,t,x+w/2,y+5,size,color,True)
def arrow(im,pts,color,width=10,progress=1):
 if progress<=0:return
 d=ImageDraw.Draw(im);lengths=[math.dist(a,z) for a,z in zip(pts,pts[1:])];goal=sum(lengths)*min(1,progress);out=[pts[0]]
 for a,z,length in zip(pts,pts[1:],lengths):
  if goal>=length:out.append(z);goal-=length
  else:
   q=goal/length;out.append((a[0]+(z[0]-a[0])*q,a[1]+(z[1]-a[1])*q));break
 d.line(out,fill=color,width=width,joint='curve');a,z=out[-2:];ang=math.atan2(z[1]-a[1],z[0]-a[0]);head=width*2.5
 d.polygon([z,(z[0]-head*math.cos(ang-.42),z[1]-head*math.sin(ang-.42)),(z[0]-head*math.cos(ang+.42),z[1]-head*math.sin(ang+.42))],fill=color)
def at(x,y):return 85+x*1750/1860,(y-102)*1750/1860

def diagram(t,row):
 mode=row['mode'];age=t-row['start'];index=next(i for i,r in enumerate(DATA) if r is row)
 im=Image.new('RGB',(1920,1080),b.CREAM)
 # Read the actual corresponding institution diagrams. Transition ocean first, then atmosphere.
 if mode in ('承接','信风'):art=NORMAL_BIG
 elif mode=='暖水':
  q=ease(age/2.3);art=NORMAL_BIG.copy();water=Image.blend(NORMAL_BIG.crop((0,425,1750,1042)),EL_BIG.crop((0,425,1750,1042)),q);art.paste(water,(0,425))
 elif mode=='海温':
  art=NORMAL_BIG.copy();art.paste(EL_BIG.crop((0,425,1750,1042)),(0,425))
 elif mode=='大气':
  art=EL_BIG.copy();art.paste(Image.blend(NORMAL_BIG.crop((0,0,1750,425)),EL_BIG.crop((0,0,1750,425)),ease(age/1.5)),(0,0))
 else:art=EL_BIG
 im.paste(art,(85,0))
 chip(im,'西太平洋',28,170,350,47,b.CORAL);chip(im,'东太平洋',1510,170,370,47,b.BLUE)
 chip(im,'正常状态' if mode=='承接' else '东风信风减弱',1450,9,425,43,b.INK)
 if mode in ('承接','信风'):
  q=ease(age/1.0) if mode=='信风' else 0
  start=at(1250,660);end=at(520+350*q,660)
  arrow(im,[start,end],b.CORAL,round(12-5*q))
  chip(im,'东风信风：东 → 西',650,450,670,46,b.CORAL)
 if mode in ('暖水','海温','大气','反馈'):
  arrow(im,[at(600,730),at(1250,730)],b.CORAL,11,ease(age/1) if mode=='暖水' else 1)
  chip(im,'暖水向东扩展',260,770,420,46,b.CORAL)
  chip(im,'东部温跃层加深',1215,855,620,45,b.BLUE)
  chip(im,'东部上升流受抑',1285,690,570,44,b.BLUE)
 if mode in ('海温','大气','反馈'):
  chip(im,'东西海温差缩小',655,450,620,46,b.CORAL)
 if mode in ('大气','反馈'):
  arrow(im,[at(990,510),at(990,245)],b.CORAL,11,ease(age/1) if mode=='大气' else 1)
  chip(im,'对流、降雨区域东移',645,190,690,43,b.CORAL)
  chip(im,'沃克环流减弱',28,287,420,43,b.BLUE)
  # Sparse rain marks follow the shifted cloud, without decorative bubbles.
  if mode=='大气':
   d=ImageDraw.Draw(im)
   for j in range(9):
    x,y=at(900+(j%3)*65,425+(j//3)*30+(age*25)%24);d.line((x,y,x-4,y+15),fill='#75acc4',width=3)
 if mode=='反馈':
  cover=Image.new('RGB',im.size,b.CREAM);im=Image.blend(im,cover,.18)
  boxes=[('东风信风减弱',40,400),('暖水东移·上升流受抑',535,615),('中东部增暖·海温差缩小',1240,640)]
  for label,x,w in boxes:chip(im,label,x,736,w,39,b.CORAL)
  arrow(im,[(453,767),(519,767)],b.CORAL,9);arrow(im,[(1165,767),(1223,767)],b.CORAL,9)
  arrow(im,[(1530,814),(1530,887),(245,887),(245,816)],'#c3a055',8,ease(age/1.8))
  chip(im,'海洋—大气正反馈',659,840,650,43,b.INK)
 return im

def comparison(t,row):
 im=Image.new('RGB',(1920,1080),b.CREAM)
 chip(im,'正常年',320,15,360,49,b.BLUE);chip(im,'厄尔尼诺年',1190,15,420,49,b.CORAL)
 for source,x in ((NORMAL,24),(EL,982)):
  art=source.resize((914,544),Image.Resampling.LANCZOS);im.paste(art,(x,96))
  ImageDraw.Draw(im).rounded_rectangle((x,95,x+914,641),radius=15,outline='#c8d9da',width=2)
 values=[('东风信风','较强','减弱'),('暖水层','西侧堆积较厚','向中东部扩展'),('东部上升流','较强','受抑、减弱'),('沃克环流','较强','减弱'),('对流与降雨','偏西侧','向东移动')]
 active=0 if row['mode']=='对照风' else 1 if row['mode']=='对照水' else 2
 for i,(name,a,z) in enumerate(values):
  yy=649+i*57
  hit=(i==0 and active==0) or (i in (1,2) and active==1) or (i in (3,4) and active==2)
  if hit:ImageDraw.Draw(im).rounded_rectangle((32,yy-1,1888,yy+53),radius=12,fill='#f8e9ce')
  text(im,name,55,yy+2,38);text(im,a,755,yy+2,40,b.BLUE,True);text(im,z,1475,yy+2,40,b.CORAL,True)
 return im

def prediction(t,row):
 im=Image.new('RGB',(1920,1080),b.CREAM)
 text(im,'根据气流变化，预测两地降水',960,20,52,b.INK,True)
 im.paste(MAP,(50,185));chip(im,'印尼：降水？',90,104,470,48,b.CORAL);chip(im,'秘鲁：降水？',1360,104,470,48,b.BLUE)
 # Coordinates mapped from the institution's 120E–60W, 30N–30S map, no redrawn coastline.
 scale=1820/685
 pins=[(50+(33+(125-120)*640/180)*scale,185+(114+3*216/60)*scale),(50+(33+(282-120)*640/180)*scale,185+(114+9*216/60)*scale)]
 d=ImageDraw.Draw(im)
 for (x,y),col,start in zip(pins,(b.CORAL,b.BLUE),((325,169),(1595,169))):
  d.line([start,(x,y-15)],fill=col,width=4);d.ellipse((x-12,y-12,x+12,y+12),fill=b.CREAM,outline=col,width=5)
 text(im,'用上升、下沉气流解释你的预测',960,858,43,b.INK,True)
 if row['mode']=='思考':
  count=max(1,math.ceil(row['end']-t));chip(im,'思考 '+str(count)+' 秒',780,740,360,42,b.BLUE)
 return im

def subtitles(im,row,t):
 ImageDraw.Draw(im).rectangle((0,940,1920,1080),fill='#244559')
 lines=previous.v.old.wrap(row['text'],46,1790)
 y=955 if len(lines)>1 else 974
 for i,line in enumerate(lines):text(im,line,960,y+i*57,46,'#fffaf0',True)
 return im

def render(t):
 row=next((r for r in DATA if r['start']<=t<r['end']),DATA[-1])
 if row['mode'].startswith('对照'):im=comparison(t,row)
 elif row['mode'] in ('预测','思考'):im=prediction(t,row)
 else:im=diagram(t,row)
 return subtitles(im,row,t)

def main():
 asyncio.run(audio());print(f'Duration {DURATION:.2f} s',flush=True)
 modes=('信风','暖水','大气','反馈','对照水','预测')
 sheet=Image.new('RGB',(1920,720),b.CREAM)
 for i,mode in enumerate(modes):
  row=next(r for r in DATA if r['mode']==mode);im=render(row['start']+min(2.5,(row['speech_end']-row['start'])*.7));im.save(ROOT/f'检查_{mode}.png');sheet.paste(im.resize((640,360)),((i%3)*640,(i//3)*360))
 sheet.save(ROOT/'第四段_六帧检查.jpg')
 if '--preview' in sys.argv:return
 movie=ROOT/'交付'/'海洋发烧了_第四段_异常环流与预测_v24.mp4'
 cmd=[EXE,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(ROOT/'配音'/'第四段_异常环流_晓伊.wav'),'-vf','setsar=1','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(movie)]
 with (ROOT/'.build'/'encode.log').open('w') as log:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for n in range(math.ceil(DURATION*24)):proc.stdin.write(render(n/24).tobytes())
  proc.stdin.close();assert proc.wait()==0
 check=subprocess.run([EXE,'-v','error','-i',str(movie),'-f','null','-'],capture_output=True)
 assert check.returncode==0 and not check.stderr.strip(),check.stderr
 doc=next((ROOT.parents[1]/'00_原始资料').glob('*最新批注版*.docx'))
 (ROOT/'验证.json').write_text(json.dumps({'decode':'PASS','seconds':DURATION,'word_source':str(doc),'word_sha256':hashlib.sha256(doc.read_bytes()).hexdigest(),'word_shots':[11,12,13],'voice':'Xiaoyi +5%, compact pauses','no_catchphrase':True,'no_presenter':True,'no_answer_revealed':True,'reasoning_pause':3.0,'official_diagram_original':[1860,1239],'new_segment_only':True,'output':str(movie)},ensure_ascii=False,indent=2),encoding='utf-8')
 print(movie,flush=True)
if __name__=='__main__':main()
