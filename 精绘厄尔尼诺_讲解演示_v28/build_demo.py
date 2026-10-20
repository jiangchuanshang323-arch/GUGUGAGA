from pathlib import Path
import sys,math,json,asyncio,subprocess,wave,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parent
for name in ('交付','配音','.build'):(ROOT/name).mkdir(parents=True,exist_ok=True)
PROJECT=ROOT.parent
sys.path.insert(0,str(PROJECT/'主体课程'/'正文日系2D_配音_v2'/'runtime'))
sys.path.insert(0,str(PROJECT/'ocean_animation_demo_20261011'/'runtime'))
import edge_tts,imageio_ffmpeg
EXE=imageio_ffmpeg.get_ffmpeg_exe()
FONT=PROJECT/'主体课程'/'得意黑_大字无水印_v6'/'素材'/'SmileySans-Oblique.ttf'
F={s:ImageFont.truetype(str(FONT),s) for s in range(28,69)}
INK='#274e61';CREAM='#fffaf0';CORAL='#d8805f';BLUE='#619cb8';GOLD='#c8a568'
LINES=[
 ('信风','先分清两股气流：近海面的东风信风，从东向西吹，也就是从右向左。'),
 ('高空','上面这根箭头是高空回流，从西向东。它不是信风。'),
 ('正常','正常时，西侧暖水厚、空气上升；东侧冷水上涌，空气下沉。'),
 ('减弱','当东风信风减弱，暖水向东扩展，东部温跃层加深，冷水上涌受到抑制。'),
 ('定义','中东太平洋持续异常增暖，这就是厄尔尼诺现象。'),
 ('大气','对流和降雨区域随之东移，沃克环流减弱。'),
 ('反馈','海温差缩小，又会进一步削弱信风。海洋与大气互相推动，形成正反馈。'),
]
DATA=[];PCM=None;DURATION=0
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def mix(a,z,q):return a+(z-a)*q
async def audio():
 global DATA,PCM,DURATION
 parts=[];cursor=0;DATA=[]
 for i,(mode,line) in enumerate(LINES):
  p=ROOT/'配音'/f'{i+1:02d}_{mode}.mp3'
  if not p.exists():
   for attempt in range(3):
    try:
     await edge_tts.Communicate(line,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=40).save(str(p));break
    except Exception:
     if attempt==2:raise
     await asyncio.sleep(1)
  raw=subprocess.check_output([EXE,'-v','error','-i',str(p),'-f','s16le','-ac','1','-ar','24000','-'])
  a=np.frombuffer(raw,dtype='<i2');idx=np.flatnonzero(np.abs(a.astype(np.int32))>220)
  if len(idx):a=a[max(0,idx[0]-720):min(len(a),idx[-1]+960)]
  pause=.10 if i<len(LINES)-1 else .35;length=len(a)/24000
  DATA.append({'mode':mode,'text':line,'start':cursor,'speech_end':cursor+length,'end':cursor+length+pause})
  parts.extend([a,np.zeros(round(24000*pause),dtype='<i2')]);cursor+=length+pause
  print(f'Voice {i+1}/{len(LINES)}',flush=True)
 PCM=np.concatenate(parts);DURATION=len(PCM)/24000
 with wave.open(str(ROOT/'配音'/'精绘演示_晓伊.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(PCM.tobytes())
 (ROOT/'台词与时间轴.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2),encoding='utf-8')

def text(im,words,x,y,size=42,color=INK,center=False):
 font=F[size];d=ImageDraw.Draw(im)
 if center:x-=font.getlength(words)/2
 d.text((x,y+font.getmetrics()[0]),words,font=font,fill=color,anchor='ls')
def pill(im,words,x,y,width,size=40,color=INK,fill=CREAM,height=62):
 d=ImageDraw.Draw(im);d.rounded_rectangle((x,y,x+width,y+height),radius=19,fill=fill,outline='#cbdcde',width=1)
 text(im,words,x+width/2,y+(height-size)/2-4,size,color,True)
def cubic(a,b,c,d,n=32):
 out=[]
 for i in range(n+1):
  t=i/n;u=1-t;out.append(tuple(u**3*a[k]+3*u*u*t*b[k]+3*u*t*t*c[k]+t**3*d[k] for k in (0,1)))
 return out
def arrow(im,points,color,width=10,dots=0,alpha=1):
 margin=width*4+6
 left=math.floor(min(x for x,y in points)-margin);top=math.floor(min(y for x,y in points)-margin)
 ww=math.ceil(max(x for x,y in points)+margin)-left;hh=math.ceil(max(y for x,y in points)+margin)-top
 layer=Image.new('RGBA',(ww*2,hh*2));d=ImageDraw.Draw(layer)
 points=[((x-left)*2,(y-top)*2) for x,y in points];width*=2
 d.line(points,fill=color,width=width,joint='curve')
 a,z=points[-2:];angle=math.atan2(z[1]-a[1],z[0]-a[0]);r=width*2.5
 d.polygon([z,(z[0]-r*math.cos(angle-.45),z[1]-r*math.sin(angle-.45)),(z[0]-r*math.cos(angle+.45),z[1]-r*math.sin(angle+.45))],fill=color)
 if dots:
  lengths=[math.dist(a,z) for a,z in zip(points,points[1:])];total=sum(lengths)
  for i in range(9):
   goal=((i/9+dots)%1)*total
   for a,z,length in zip(points,points[1:],lengths):
    if goal>length:goal-=length;continue
    q=goal/max(1,length);x=mix(a[0],z[0],q);y=mix(a[1],z[1],q);d.ellipse((x-6,y-6,x+6,y+6),fill='#fff7dd');break
 layer=layer.resize((ww,hh),Image.Resampling.LANCZOS)
 if alpha<1:layer.putalpha(layer.getchannel('A').point(lambda x:round(x*alpha)))
 im.paste(layer,(left,top),layer)
def gradient(size,top,bottom):
 im=Image.new('RGB',size);d=ImageDraw.Draw(im)
 for y in range(size[1]):
  q=y/max(1,size[1]-1);d.line((0,y,size[0],y),fill=tuple(round(mix(a,z,q)) for a,z in zip(top,bottom)))
 return im

# Own hand-drawn cloud contour, not an online illustration or AI scientific diagram.
def cloud_art():
 im=Image.new('RGBA',(510,305));d=ImageDraw.Draw(im)
 paths=[((40,223),(1,210),(5,160),(58,155)),((58,155),(34,92),(119,68),(154,119)),((154,119),(151,28),(266,32),(280,103)),((280,103),(328,41),(403,75),(396,144)),((396,144),(460,112),(503,162),(465,206)),((465,206),(525,225),(474,265),(419,260)),((419,260),(319,278),(151,270),(40,252)),((40,252),(27,242),(25,230),(40,223))]
 pts=[]
 for curve in paths:pts+=cubic(*curve,22)
 d.polygon([(x+2,y+8)for x,y in pts],fill='#c4dce1')
 d.polygon(pts,fill='#fffdf5');d.line(pts+[pts[0]],fill='#a8c5ce',width=3,joint='curve')
 shade=cubic((55,223),(149,251),(344,248),(455,224),45)+[(445,257),(100,262)]
 d.polygon(shade,fill='#e0eced')
 for p in [((84,159),(101,140),(125,142),(142,153)),((293,114),(319,96),(345,108),(354,126)),((181,97),(195,66),(224,66),(243,80))]:d.line(cubic(*p,20),fill='#eef5f1',width=6,joint='curve')
 return im
CLOUD=cloud_art()
SKY=gradient((1800,422),(245,251,250),(217,237,243))
COLD=gradient((1760,333),(142,196,215),(78,138,174))
WARM=gradient((1760,333),(255,226,186),(239,178,140))
BASE=Image.new('RGB',(1920,1080),CREAM)
bd=ImageDraw.Draw(BASE);bd.rounded_rectangle((56,160,1864,906),radius=34,fill='#e8f2f3',outline='#c8dce0',width=2)
BASE.paste(SKY,(60,164))
np_rng=np.random.default_rng(28);paper=np_rng.integers(-2,3,(1080,1920,1),dtype=np.int16)
BASE=Image.fromarray(np.clip(np.asarray(BASE).astype(np.int16)+paper,0,255).astype('uint8'))

def params(t,row):
 if row['mode'] in ('信风','高空','正常'):return 0,0,0
 if row['mode']=='减弱':
  age=t-row['start'];return ease(age/1.6),ease((age-.75)/2.8),0
 if row['mode']=='定义':return 1,1,0
 if row['mode']=='大气':return 1,1,ease((t-row['start'])/2.2)
 return 1,1,1

def render(t,subtitles=True):
 row=next((r for r in DATA if r['start']<=t<r['end']),DATA[-1]);mode=row['mode'];age=t-row['start'];wind,water,air=params(t,row)
 im=BASE.copy();d=ImageDraw.Draw(im)
 text(im,'厄尔尼诺现象',75,24,61);text(im,'分清气流方向，看懂海气联动',75,96,33,BLUE)
 pill(im,'正常状态' if wind==0 else '状态变化' if air<.99 else '厄尔尼诺状态',1430,37,413,42)
 text(im,'西太平洋 · 印尼一侧',100,177,42);text(im,'东太平洋 · 秘鲁一侧',1380,177,42)
 # A high, individually labelled return branch. Its eastward arrow cannot be mistaken for trade winds.
 upx=mix(425,1110,air)
 high=cubic((upx+28,285),(750,264),(1210,272),(1480,285),60)
 arrow(im,high,GOLD,12 if mode=='高空' else 8,dots=(t*.10)%1,alpha=1 if mode=='高空' else .78)
 pill(im,'高空回流：西 → 东',675,112,620,40,GOLD)
 # Natural layered cloud follows the changed convection centre.
 cloud=CLOUD.resize((432,258),Image.Resampling.LANCZOS)
 cx=upx;cy=321+math.sin(t*.8)*2
 im.paste(cloud,(round(cx-216),round(cy-129)),cloud)
 arrow(im,[(upx,487),(upx,448),(upx,430)],CORAL,11 if mode=='正常' else 9)
 arrow(im,cubic((1510,330),(1540,360),(1518,421),(1510,483),30),BLUE,11 if mode=='正常' else 8,alpha=mix(.92,.45,air))
 if air>.01:arrow(im,cubic((277,333),(251,388),(280,433),(294,482),30),BLUE,7,alpha=air*.7)
 for j in range(8):
  rx=cx-140+j*39;ry=416+((t*22+j*11)%47)
  d.line((rx,ry,rx-4,ry+12),fill='#76aac1',width=3)
 pill(im,'空气上升' if air<.5 else '空气下沉',84,361,235,36,CORAL if air<.5 else BLUE)
 pill(im,'空气下沉',1570,365,235,36,BLUE)
 # The low branch is explicitly separate: x decreases, hence right-to-left / east-to-west.
 start=(1470,501);end=(mix(478,1125,wind),501)
 arrow(im,[start,end],CORAL,13 if mode=='信风' else round(mix(10,6,wind)),dots=(t*mix(.14,.045,wind))%1)
 pill(im,'近海面东风信风：东 → 西' if wind<.5 else '近海面东风信风减弱',628,513,720,39,CORAL,height=52)
 # Continuous wavy water layers, clipped to the ocean rectangle.
 ox,oy=80,571;w,h=1760,333
 ocean=COLD.copy();mask=Image.new('L',(w,h));md=ImageDraw.Draw(mask)
 top=[(x,4+3*math.sin(x*.025+t*1.1))for x in range(0,w+1,12)]
 boundary=[]
 for x in range(0,w+1,10):
  s=x/w;normal=204-151*(s*s*(3-2*s));changed=148+44*s
  yy=mix(normal,changed,water)+3*math.sin(s*math.pi*5+t*.6)
  boundary.append((x,yy))
 md.polygon(top+list(reversed(boundary)),fill=255);ocean.paste(WARM,(0,0),mask)
 od=ImageDraw.Draw(ocean);od.line(boundary,fill='#d79772',width=3);od.line(top,fill='#fff8e6',width=3)
 # Quiet contour strokes add depth without independent geometric water icons.
 for j in range(3):
  pts=[(x,mix(227+26*j,215+25*j,water)+4*math.sin(x*.006+j+t*.24))for x in range(0,w+1,10)]
  od.line(pts,fill=(127,179,199),width=1)
 im.paste(ocean,(ox,oy))
 if water>.01:
  for j in range(0,1760,25):
   s=j/1760;y=571+204-151*(s*s*(3-2*s));d.line((80+j,y,80+j+12,y-1),fill='#f9e4cc',width=2)
  arrow(im,[(mix(600,750,water),669),(mix(1030,1430,water),669)],CORAL,8,alpha=water*.9)
 arrow(im,cubic((1640,860),(1610,816),(1632,mix(659,810,water)),(1640,mix(626,805,water)),40),BLUE,round(mix(10,5,water)),alpha=mix(1,.40,water))
 pill(im,'表层暖水',120,595,350,43,CORAL,fill='#fff2dc')
 pill(im,'深层冷水',335,818,340,43,BLUE,fill='#edf6f5')
 ty=571+mix(126,169,water)
 pill(im,'温跃层',910,ty,290,40,INK)
 pill(im,'冷水上涌较强' if water<.5 else '冷水上涌受抑',1310,824,470,40,BLUE)
 if water>.6:pill(im,'东部温跃层加深',1235,708,505,40,CORAL)
 if air>.7:pill(im,'海气正反馈' if mode=='反馈' else '沃克环流减弱',500,337,370,39,GOLD)
 if mode=='反馈':
  # Sea temperature contrast feeds back to the low-level wind, shown separately from upper return.
  arrow(im,cubic((1340,751),(1810,705),(1810,480),(1375,488),45),GOLD,6,alpha=ease(age/1.5))
 if subtitles:
  d.rectangle((0,958,1920,1080),fill='#244559')
  # Two lines when required; same baseline and readable 46px type.
  line='';lines=[]
  for ch in row['text']:
   if line and F[46].getlength(line+ch)>1780:lines.append(line);line=ch
   else:line+=ch
  if line:lines.append(line)
  yy=966 if len(lines)>1 else 988
  for i,line in enumerate(lines):text(im,line,960,yy+i*54,46,'#fffaf0',True)
 return im

def main():
 asyncio.run(audio());print(f'Duration {DURATION:.2f}',flush=True)
 sheet=Image.new('RGB',(1920,720),CREAM)
 for i,mode in enumerate(('信风','高空','正常','减弱','大气','反馈')):
  row=next(r for r in DATA if r['mode']==mode);age=min(3,(row['speech_end']-row['start'])*.72)
  im=render(row['start']+age);im.save(ROOT/f'检查_{mode}.png');sheet.paste(im.resize((640,360)),((i%3)*640,(i//3)*360))
 sheet.save(ROOT/'六帧检查.jpg')
 if '--preview' in sys.argv:return
 output=ROOT/'交付'/'厄尔尼诺_精绘自制图_晓伊讲解_demo_v28.mp4'
 cmd=[EXE,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(ROOT/'配音'/'精绘演示_晓伊.wav'),'-vf','setsar=1','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(output)]
 with (ROOT/'.build'/'encode.log').open('w') as log:
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for n in range(math.ceil(DURATION*24)):
   p.stdin.write(render(n/24).tobytes())
   if n%240==0:print(f'Render {n/24:.0f}/{DURATION:.1f}',flush=True)
  p.stdin.close();assert p.wait()==0
 check=subprocess.run([EXE,'-v','error','-i',str(output),'-f','null','-'],capture_output=True);assert check.returncode==0 and not check.stderr.strip(),check.stderr
 doc=next((PROJECT/'00_原始资料').glob('*最新批注版*.docx'))
 (ROOT/'验证.json').write_text(json.dumps({'decode':'PASS','seconds':DURATION,'own_drawn_diagram':True,'surface_wind_direction':'east to west / decreasing x','high_return_direction':'west to east / increasing x','labels_separate':True,'word_source':str(doc),'word_sha256':hashlib.sha256(doc.read_bytes()).hexdigest(),'voice':'zh-CN-XiaoyiNeural +5%','no_catchphrase':True,'no_concat':True,'scope':'diagram demo only, not next whole lesson segment','output':str(output)},ensure_ascii=False,indent=2),encoding='utf-8')
 print(output,flush=True)
if __name__=='__main__':main()
