from pathlib import Path
import sys, json, math, wave, inspect, subprocess, shutil
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent
for x in ('交付','.build','配音','素材'):(ROOT/x).mkdir(exist_ok=True)
V10=ROOT.parent/'测体征_第二分钟_v10'
sys.path.insert(0,str(V10));import build_part2 as p
b=p.b;EXE=p.EXE
p.DATA=json.loads((V10/'台词与时间轴.json').read_text(encoding='utf-8'))
with wave.open(str(V10/'配音'/'第二分钟_晓伊.wav'),'rb') as w:original=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
p.PCM=original.astype(np.float32)/32768;p.prev.PCM=p.PCM;p.DURATION=len(original)/24000
CUT=next(r['start'] for r in p.DATA if r['mode']=='距平');BRIDGE=2.4
index=round(CUT*24000);samples=np.concatenate([original[:index],np.zeros(round(BRIDGE*24000),dtype='<i2'),original[index:]])
DURATION=len(samples)/24000
with wave.open(str(ROOT/'配音'/'晓伊_拉板衔接.wav'),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(samples.tobytes())
LEFT=ROOT/'素材'/'20_朝左介绍.png';GRAB=ROOT/'素材'/'21_抬臂抓环.png'
L=Image.open(LEFT).convert('RGBA');G=Image.open(GRAB).convert('RGBA')
assert L.getextrema()[-1][0]==0 and G.getextrema()[-1][0]==0,'Expected transparent sprites'
original_presenter=p.prev.presenter
def presenter(s,pose,px,py,size,t,custom=False):
 if pose!=3 or custom:return original_presenter(s,pose,px,py,size,t,custom)
 s.ellipse(px+size*.20,py+size*.94,size*.63,14,'#bdc9c2')
 s.image(str(LEFT),px,py,size,size)
 # The regenerated left explaining pose has its own mouth anchor, rather than mirroring the face.
 mx,my,mw,mh=590,542,67,49;scale=size/L.width
 s.image(str(p.v.V3/'素材'/f'口型_03_{p.prev.mouth(t)}.png'),px+(mx-mw/2)*scale,py+(my-mh/2)*scale,mw*scale,mh*scale)
p.prev.presenter=presenter
src=inspect.getsource(p.scene).replace("elif mode=='距平' and age<1.0:","elif False:")
exec(src,p.__dict__);p.env['scene']=p.scene
# Keep the original map and the editable classroom board; no generated geography or text.
map_scene=p.scene(CUT-.05);map_scene.items=map_scene.items[:5]
saved=p.env['scene'];p.env['scene']=lambda t:map_scene
MAPBACK=p.render(CUT-.05);p.env['scene']=saved
old_end=p.scene(CUT-.05);old_end.items=old_end.items[:8]
p.env['scene']=lambda t:old_end
OLD_END=p.render(CUT-.05);p.env['scene']=saved
ROOM=Image.open(b.BG).convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS)
BOARD=p.render(CUT+1.6).crop((24,140,1474,1030)).convert('RGBA')
BOARD.save(ROOT/'素材'/'下拉展示板_原有知识.png')
def place(im,art,x,y,width,height=None):
 height=height or width
 art=art.resize((max(1,round(width)),max(1,round(height))),Image.Resampling.LANCZOS)
 im.paste(art,(round(x),round(y)),art)
def transition(age):
 # Crouch -> leap -> grip -> pull -> release -> damped landing.
 roomq=b.ease((age-.45)/.95)
 im=Image.blend(MAPBACK,ROOM,roomq);d=ImageDraw.Draw(im)
 pull=b.ease((age-.83)/.98)
 h=max(1,round(890*pull))
 if pull>0:
  im.paste(BOARD.crop((0,0,1450,h)),(24,140),BOARD.crop((0,0,1450,h)))
  d=ImageDraw.Draw(im);d.rounded_rectangle((24,140+h-12,1474,140+h+3),radius=6,fill='#98bcc6')
 # Roller and a separate pulley cord on the right keep the hand reachable throughout the pull.
 alpha=b.ease(age/.18)
 d.rounded_rectangle((24,120,1474,153),radius=16,fill='#d8cdb3',outline='#91b7bc',width=3)
 d.line([(1472,137),(1755,137)],fill='#a4bfc1',width=6)
 d.ellipse((1742,124,1768,150),fill='#f3e5c3',outline='#91b7bc',width=3)
 if age<.30:
  q=b.ease(age/.30);width=390*(1+.08*q);height=390*(1-.13*q)
  x=1510-(width-390)/2;y=1050-height
  d.ellipse((1590,1040,1820,1054),fill='#bdc9c2')
  place(im,L,x,y,width,height);hand=452
 elif age<.83:
  q=(age-.30)/.53;y=660-240*(1-(1-q)**2)
  # Slight stretching is a traditional 2D take-off effect, not a static image jump-cut.
  stretch=1+.04*math.sin(q*math.pi);place(im,G,1510,y,430,430*stretch)
  hand=452
 elif age<1.81:
  y=420+220*pull;place(im,G,1510,y,430)
  hand=y+96/G.height*430
 else:
  q=(age-1.81)/.59;bounce=14*math.exp(-5*q)*math.sin(3*math.pi*q)
  y=660+bounce;place(im,L,1510,y,390)
  hand=672-(672-170)*b.ease((age-1.86)/.40)
 if age<2.27:
  d=ImageDraw.Draw(im)
  d.line([(1755,151),(1755,hand-9)],fill='#91b7bc',width=5)
  d.ellipse((1743,hand-12,1767,hand+12),fill=None,outline='#bd8962',width=5)
 if age>=1.81:
  d=ImageDraw.Draw(im);d.ellipse((1585,1040,1810,1053),fill='#bdc9c2')
 if age>1.6:
  titlelayer=Image.new('RGB',(1920,1080),b.CREAM);titlelayer.paste(im)
  td=ImageDraw.Draw(titlelayer);td.text((40,35+b.F[53].getmetrics()[0]),'测体征 · 给海洋读“体温”',font=b.F[53],fill=b.INK,anchor='ls')
  im=Image.blend(im,titlelayer,b.ease((age-1.6)/.5))
 if age<.22:im=Image.blend(OLD_END,im,b.ease(age/.22))
 # During the physical transition, no dialogue bubble or subtitles are drawn.
 return im
def render(t):
 if t<CUT:return p.render(t)
 if t<CUT+BRIDGE:return transition(t-CUT)
 im=p.render(t-BRIDGE);d=ImageDraw.Draw(im)
 d.rounded_rectangle((24,120,1474,153),radius=16,fill='#d8cdb3',outline='#91b7bc',width=3)
 d.line([(1472,137),(1755,137)],fill='#a4bfc1',width=6)
 d.ellipse((1742,124,1768,150),fill='#f3e5c3',outline='#91b7bc',width=3)
 return im
def encode(path,start,length,audio):
 cmd=[EXE,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(audio),'-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(path)]
 with open(ROOT/'.build'/f'{path.stem}.log','w') as log:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for n in range(math.ceil(length*24)):
   proc.stdin.write(render(start+n/24).tobytes())
   if n%240==0:print(f'Render {n/24:.0f}/{length:.2f}',flush=True)
  proc.stdin.close();assert proc.wait()==0
def main():
 for a in (.15,.60,.88,1.30,1.75,2.15):render(CUT+a).save(ROOT/f'转场检查_{a:.2f}.png')
 render(CUT+BRIDGE+1.6).save(ROOT/'预览_朝左讲解.png')
 frames=[render(CUT+a).resize((640,360)) for a in (.15,.60,.88,1.30,1.75,2.15)]
 contact=Image.new('RGB',(1920,720),b.CREAM)
 for i,im in enumerate(frames):contact.paste(im,((i%3)*640,(i//3)*360))
 contact.save(ROOT/'跳跃拉板_六帧预览.jpg')
 if '--preview' in sys.argv:return
 out=ROOT/'交付'/'海洋发烧了_第二分钟_跳起拉板_v11.mp4'
 encode(out,0,DURATION,ROOT/'配音'/'晓伊_拉板衔接.wav')
 # Short preview lets the user assess the revised movement without replaying the whole lesson.
 with wave.open(str(ROOT/'配音'/'转场试听.wav'),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(samples[round((CUT-1.3)*24000):round((CUT+BRIDGE+3)*24000)].tobytes())
 clip=ROOT/'交付'/'跳起拉板_转场预览_v11.mp4';encode(clip,CUT-1.3,BRIDGE+4.3,ROOT/'配音'/'转场试听.wav')
 first=ROOT.parent/'出入场_无制作提示_v9'/'交付'/'海洋发烧了_最新批注落实_出入场_v9.mp4'
 joined=ROOT/'交付'/'海洋发烧了_开场与前两段_拉板_v11.mp4'
 graph='[0:v]setsar=1,setpts=PTS-STARTPTS[v0];[1:v]setsar=1,setpts=PTS-STARTPTS[v1];[0:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a0];[1:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]'
 with open(ROOT/'.build'/'join.log','w') as log:subprocess.run([EXE,'-y','-i',str(first),'-i',str(out),'-filter_complex',graph,'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','19','-c:a','aac','-b:a','160k','-movflags','+faststart',str(joined)],stdout=log,stderr=log,check=True)
 for path in (out,clip,joined):
  result=subprocess.run([EXE,'-v','error','-i',str(path),'-f','null','-'],capture_output=True);assert result.returncode==0,result.stderr
 timeline=[]
 for row in p.DATA:
  r=dict(row)
  if r['start']>=CUT:
   for key in ('start','speech_end','end'):r[key]+=BRIDGE
  timeline.append(r)
 timeline.insert(1,dict(mode='跳起拉板',start=CUT,end=CUT+BRIDGE,text='',bubble=False))
 (ROOT/'台词与时间轴.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'验证.json').write_text(json.dumps(dict(full_decode='PASS',seconds=DURATION,transition_seconds=BRIDGE,voice='v10 cached Xiaoyi; no synthesis',new_sprites=[str(LEFT),str(GRAB)],mouth_anchor=[590,542],bubble_during_transition=False,joined=str(joined),clip=str(clip)),ensure_ascii=False,indent=2),encoding='utf-8')
 shutil.copy2(V10/'素材说明.md',ROOT/'素材说明.md')
 (ROOT/'动作制作说明.md').write_text('使用内置imagegen生成两张透明动作PNG：20朝左介绍、21抬臂抓环。参考03常态解说，保留观看者左侧发夹、眼镜、红领结和企鹅服，不做整体镜像。提示要求：screen-left open-flipper explaining pose; overhead clasping flippers jump-and-tug pose; preserve exact identity; real transparent backdrop.跳跃拉板采用本地逐帧合成，蹲身压缩、起跳拉伸、弧线升降、手与拉环接触、展示板揭示及落地缓冲，总长2.4秒；期间气泡隐藏。原配音切片插入等长静音，讲解内容不改。\n',encoding='utf-8')
 print(joined,flush=True)
if __name__=='__main__':main()
