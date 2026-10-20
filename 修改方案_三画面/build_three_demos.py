"""Three separate 5-second clips, with measured character-size and motion checks."""
from pathlib import Path
import json,math,wave,subprocess,hashlib,io
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
import build_concepts as b
import redesign_plates as p

R=Path(__file__).resolve().parent;P=R.parent
OUT=P/'demooo/预览/三个画面5秒样片';OUT.mkdir(parents=True,exist_ok=True)
Q=R/'5秒样片检查';Q.mkdir(exist_ok=True)
FF=P/'ocean_animation_demo_20261011/runtime/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
MOUTH=P/'主体课程/正文晓伊_口型与大画面_v3/素材'
FPS=24;N=120;H=368.671875
def E(u):u=max(0,min(1,u));return u*u*(3-2*u)
def box(a):return a.getchannel('A').point(lambda v:255 if v>=128 else 0).getbbox()
def pcm(path):
 with wave.open(str(path),'rb') as w:
  assert w.getframerate()==24000 and w.getnchannels()==1
  return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').copy()
def write_wav(path,a):
 with wave.open(str(path),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(a.astype('<i2').tobytes())
def audio_clip(source,s,e,lead):
 a=np.zeros(120000,dtype='<i2');v=pcm(source)[round(s*24000):round(e*24000)]
 assert round(lead*24000)+len(v)<=len(a)
 a[round(lead*24000):round(lead*24000)+len(v)]=v;return a

meta9=json.loads((P/'第九段_辨析与滞后/台词与时间轴.json').read_text(encoding='utf-8'))
meta11=json.loads((P/'第十一段_适应与减缓/台词与时间轴.json').read_text(encoding='utf-8'))
r9=meta9['lines'][0];r11=meta11['lines'][0]
AUDIO=[np.zeros(120000,dtype='<i2'),audio_clip(P/'第九段_辨析与滞后/配音/第九段.wav',r9['start'],r9['speech_end'],.25),audio_clip(P/'第十一段_适应与减缓/配音/第十一段.wav',r11['start'],r11['speech_end'],.35)]
for i,a in enumerate(AUDIO):write_wav(Q/f'配音_{i+1}.wav',a)
def voice(i,t):
 a=AUDIO[i][max(0,round(t*24000)):max(0,round(t*24000))+960].astype(float)/32768
 rms=float(np.sqrt(np.mean(a*a))) if len(a) else 0
 state=0 if rms<.011 else 1 if rms<.055 else 2 if rms<.13 else 3
 return rms,state

BASE={k:Image.open(b.SPR/f'{k:02d}_{name}.png').convert('RGBA') for k,name in [(6,'教尺指向'),(15,'走位后站稳')]}
BASE[99]=Image.open(R/'企鹅_拿处方单.png').convert('RGBA')
BOUNDS={k:box(a) for k,a in BASE.items()};SCALE={k:H/(BOUNDS[k][3]-BOUNDS[k][1]) for k in BASE}
MOUTHS=[Image.open(MOUTH/f'口型_06_{j}.png').convert('RGBA') for j in range(4)]
RXM=[]
for state in range(4):
 # Reconstruct only the original mouth area from neighboring skin, then animate
 # the mouth itself. Never transfer the opaque rectangular teacher patch.
 a=BASE[99].crop((594,451,706,549)).copy()
 ar=np.asarray(a).copy()
 for yy in range(98):
  l=np.asarray(BASE[99].getpixel((594,451+yy)),float)
  r=np.asarray(BASE[99].getpixel((706,451+yy)),float)
  for xx in range(112):ar[yy,xx]=np.clip(l*(1-xx/111)+r*xx/111,0,255)
 a=Image.fromarray(ar)
 mask=Image.new('L',a.size);ImageDraw.Draw(mask).rounded_rectangle((0,0,111,97),20,fill=255);mask=mask.filter(ImageFilter.GaussianBlur(3));a.putalpha(mask)
 d=ImageDraw.Draw(a)
 if state==0:d.arc((26,32,87,64),0,170,fill='#7b3439',width=3)
 else:
  hh=[0,24,42,60][state];cy=49
  d.ellipse((29,cy-hh/2,85,cy+hh/2),fill='#a23d4d',outline='#77313b',width=3)
  if state>=2:d.ellipse((37,cy+2,78,cy+hh/2-3),fill='#ed8c94')
 RXM.append(a)

def walking(t,envelope):
 a=BASE[15];mesh=[];phase=t*math.pi*2*2.05
 def vertex(x,y):
  gate=max(0,min(1,(y-345)/150))**1.7
  left=1-E((x-233)/48);right=1-left
  lift=(left*max(0,math.sin(phase))+right*max(0,-math.sin(phase)))*17*gate*envelope
  swing=(left-right)*13*math.sin(phase)*gate*envelope
  return x-swing,y+lift
 for y in range(0,512,32):
  for x in range(0,512,32):
   corners=[vertex(x,y),vertex(x,y+32),vertex(x+32,y+32),vertex(x+32,y)]
   mesh.append(((x,y,x+32,y+32),tuple(v for c in corners for v in c)))
 return a.transform(a.size,Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)

def actor(im,kind,cx,foot,t,clip,walk=0):
 a=walking(t,walk) if kind==15 and walk>0 else BASE[kind].copy()
 rms,state=voice(clip,t)
 if kind==6:
  a.alpha_composite(MOUTHS[state],(202,196))
 elif kind==99:
  a.alpha_composite(RXM[state],(594,451))
  d=ImageDraw.Draw(a);d.text((742,778),'处方单',font=b.f(82),anchor='mt',fill=b.INK)
  for j in range(3):d.line((642,892+j*52,840,892+j*52),fill='#89aeb4',width=4)
 s=SCALE[kind];bb=BOUNDS[kind]
 a=a.resize((round(a.width*s),round(a.height*s)),Image.Resampling.LANCZOS)
 px=round(cx-(bb[0]+bb[2])/2*s);py=round(foot-bb[3]*s)
 im.paste(a,(px,py),a)
 actual=box(a);bounds=[px+actual[0],py+actual[1],px+actual[2],py+actual[3]]
 assert 0<=bounds[0]<bounds[2]<=1920 and 0<=bounds[1]<bounds[3]<=1080,bounds
 return dict(kind='character',pose=kind,box=bounds,physical_height=bounds[3]-bounds[1],target_height=H,reference='06 pointer scaled to original 390px canvas',rms=rms,mouth=state,walking=walk>0)

# Sample the existing drawn road, keeping feet on its actual navy walking lane.
ROUTE=p.route();ar=np.asarray(ROUTE)
anchors=np.array([(350,793),(400,796),(450,780),(500,740),(550,690),(600,630),(650,576),(700,542),(765,532)],float)
path=[]
for x in range(350,766):
 estimate=np.interp(x,anchors[:,0],anchors[:,1]);lo=max(0,round(estimate-56));hi=min(1080,round(estimate+56))
 c=ar[lo:hi,x,:].astype(int);ok=(c[:,0]<90)&(c[:,1]<140)&(c[:,2]<180)&(c[:,2]>c[:,1])
 idx=np.flatnonzero(ok)
 y=(idx[0]+idx[-1])/2+lo if len(idx)>12 else estimate
 path.append((x,y))
path=np.array(path);path[:,1]=np.convolve(np.pad(path[:,1],(8,8),mode='edge'),np.ones(17)/17,mode='valid')
path[0]=[350,793];path[-1]=[765,532]
length=np.concatenate([[0],np.cumsum(np.linalg.norm(np.diff(path,axis=0),axis=1))]);length/=length[-1]
def route_frame(t):
 im=ROUTE.copy();progress=E((t-.3)/3.4);ix=np.interp(progress,length,np.arange(len(path)));i=min(len(path)-2,int(ix));u=ix-i
 x,y=path[i]*(1-u)+path[i+1]*u
 d=ImageDraw.Draw(im)
 if i>1:d.line([tuple(q) for q in path[:i+1]],fill='#d5ad69',width=6,joint='curve')
 q=E((t-3.2)/.5)
 if q:d.ellipse((725,492,805,572),outline='#cf9568',width=5)
 env=E(t/.3)*(1-E((t-3.25)/.45));bob=2.0*math.sin(t*2*math.pi*4.1)*env
 o=actor(im,15,float(x),float(y+bob),t,0,env)
 return im,[o,dict(kind='walk_path',progress=progress,foot=[float(x),float(y)],arrived=t>=3.7)]

# The glove sprite sheet has a real transparent gap; both silhouettes remain intact.
sheet=Image.open(R/'拳套_分离图层原料.png').convert('RGBA');mid=sheet.width//2
GLOVES=[]
for region in [(0,0,mid,sheet.height),(mid,0,sheet.width,sheet.height)]:
 a=sheet.crop(region);a=a.crop(box(a));a=a.resize((round(a.width*270/a.height),270),Image.Resampling.LANCZOS);GLOVES.append(a)
for j,a in enumerate(GLOVES):a.save(R/['拳套_左蓝.png','拳套_右橙.png'][j])
edges=[]
for a in GLOVES:
 mask=np.asarray(a.getchannel('A'))>=128;edges.append([(np.flatnonzero(row)[0],np.flatnonzero(row)[-1]) if row.any() else (None,None) for row in mask])
D=max(l[1]-r[0]+1 for l,r in zip(*edges) if l[0] is not None and r[0] is not None)
leftx=1210-(D+GLOVES[1].width)/2;rightx=leftx+D
peaks=[]
for target in [1.1,2.35]:
 candidates=[i/24 for i in range(120) if abs(i/24-target)<.22 and voice(1,i/24)[0]>.035]
 peaks.append(min(candidates,key=lambda x:abs(x-target)) if candidates else target)
def bump(t,c):return E((t-(c-.5))/.44)*(1-E((t-(c+.06))/.46))
COMPARE=b.compare(actor=False,gloves=False)
def compare_frame(t):
 im=COMPARE.copy();q=max(bump(t,c) for c in peaks);gap=80*(1-q);dy=round(1.3*math.sin(t*3))
 positions=[(round(leftx-gap/2),442+dy),(round(rightx+gap/2),442+dy)]
 for a,xy in zip(GLOVES,positions):im.paste(a,xy,a)
 o=actor(im,6,196,970+math.sin(t*2)*1.2,t,1)
 b.bubble(im,r9['text'],(35,300,476,510),(190,620),46)
 return im,[o,dict(kind='glove_pair',gap=gap,contact=q>.998,left=list(positions[0]),right=list(positions[1]),contact_times=peaks,speaking_interval=[.25,.25+r9['speech_end']-r9['start']])]

RX=p.prescription(False)
def rx_frame(t):
 im=RX.copy();p.title(im,'开处方',70,88,68)
 for j,at in enumerate([1.9,2.7,3.45]):
  q=E((t-at)/.18)
  if q:
   y=594+j*88;pts=[(667,y+16),(673,y+22),(684,y+5)];k=max(2,round(2+q))
   ImageDraw.Draw(im).line(pts[:k],fill='#317f83',width=3,joint='curve')
 o=actor(im,99,253,985+math.sin(t*2)*1.2,t,2)
 b.bubble(im,'第一张处方叫适应：\n早发现、早预警、\n早行动。',(35,350,524,560),(250,660),46)
 return im,[o,dict(kind='prescription_checks',completed=sum(t>=v+.18 for v in [1.9,2.7,3.45]))]

def extract(path,t):
 a=subprocess.run([str(FF),'-v','error','-ss',str(t),'-i',str(path),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True,check=True).stdout
 return Image.open(io.BytesIO(a)).convert('RGB')

def main():
 reports=[];montage=Image.new('RGB',(1600,950),'#e9efed')
 old2=Image.open(R/'02_厄尔尼诺与人为增暖.png').size;assert old2==(1920,1080)
 for index,(name,fn) in enumerate([('四步会诊路线_5秒',route_frame),('概念辨析_拳套轻碰_5秒',compare_frame),('适应处方单_5秒',rx_frame)]):
  out=OUT/f'{name}.mp4';pending=out.with_name('.'+out.stem+'.pending.mp4');audit=[]
  log=(Q/f'{name}_编码日志.txt').open('wb')
  proc=subprocess.Popen([str(FF),'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(Q/f'配音_{index+1}.wav'),'-t','5','-frames:v','120','-c:v','libx264','-profile:v','baseline','-level:v','4.0','-g','24','-bf','0','-refs','1','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-ac','2','-b:a','128k','-movflags','+faststart',str(pending)],stdin=subprocess.PIPE,stderr=log)
  for i in range(120):
   b.AUDIT.clear();im,objs=fn(i/24);proc.stdin.write(im.tobytes());audit.append(dict(frame=i,objects=objs,text=list(b.AUDIT)))
  proc.stdin.close();assert proc.wait()==0;log.close()
  dec=subprocess.run([str(FF),'-v','error','-i',str(pending),'-f','null','-'],capture_output=True);assert dec.returncode==0 and not dec.stderr,dec.stderr
  info=subprocess.run([str(FF),'-hide_banner','-i',str(pending),'-map','0:v:0','-c','copy','-f','null','-'],capture_output=True,check=True).stderr.decode('utf-8','replace')
  import re
  assert '00:00:05.00' in info and '1920x1080' in info
  assert int(re.findall(r'frame=\s*(\d+)',info)[-1])==120
  heights=[o['physical_height'] for row in audit for o in row['objects'] if o['kind']=='character'];assert min(heights)>=H-5 and max(heights)<=H+2,(name,min(heights),max(heights))
  if index==1:
   contacts=[row for row in audit if any(o['kind']=='glove_pair' and o['contact'] for o in row['objects'])];assert len(contacts)>=2
   assert all(.25<=row['frame']/24<=.25+r9['speech_end']-r9['start'] for row in contacts)
   assert len({o['mouth'] for row in audit for o in row['objects'] if o['kind']=='character'})>1
  if index==2:assert len({o['mouth'] for row in audit for o in row['objects'] if o['kind']=='character'})>1
  pending.replace(out);report=dict(name=name,path=str(out),seconds=5,frames=120,resolution='1920x1080',fps=24,decode='PASS',sha256=hashlib.sha256(out.read_bytes()).hexdigest(),bytes=out.stat().st_size,character_height_range=[min(heights),max(heights)],reference_height=H,voice='none during route walk' if index==0 else 'existing Xiaoyi audio, not newly generated')
  reports.append(report);(Q/f'{name}_逐帧检查.json').write_text(json.dumps(audit,ensure_ascii=False),encoding='utf-8')
  for j,t in enumerate([.4,1.1,2.35,4.2]):
   im=extract(out,t);im.save(Q/f'{index+1}_{t:.2f}.png');montage.paste(im.resize((400,225),Image.Resampling.LANCZOS),(j*400,index*315));ImageDraw.Draw(montage).text((j*400+8,index*315+232),f'{index+1}: {t:.2f}s',font=b.f(24),fill=b.INK)
  print('DELIVERED',name,'5s',report['character_height_range'],flush=True)
 montage.save(Q/'三个样片编码总览.jpg')
 (Q/'验证.json').write_text(json.dumps(dict(outputs=reports,gloves_contact_times=peaks,character_sizing='original 390px sprite canvas; alpha>=128 body height normalized to 368.67px',visual_review='pending encoded frame inspection',existing_videos_modified=False),ensure_ascii=False,indent=2),encoding='utf-8')
 sheet=Image.new('RGB',(1600,510),'#e6eef0')
 for j,(label,kind) in enumerate([('Original course',6),('Route',15),('Comparison',6),('Prescription',99)]):
  im=Image.new('RGB',(400,510),'#e6eef0');actor(im,kind,200,450,0,0)
  ImageDraw.Draw(im).line((15,450,385,450),fill='#769da8',width=1);ImageDraw.Draw(im).text((20,466),label,font=b.f(22),fill=b.INK);sheet.paste(im,(j*400,0))
 sheet.save(Q/'角色比例对照.png');print('ALL_THREE_DEMOS_READY',OUT,flush=True)
if __name__=='__main__':main()

