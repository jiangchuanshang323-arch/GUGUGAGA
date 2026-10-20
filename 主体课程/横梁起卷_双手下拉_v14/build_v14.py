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
LEFT=ROOT.parent/'跳起拉板_左向解说_v11'/'素材'/'20_朝左介绍.png';GRAB=ROOT.parent/'双手抓杆_卷开拉板_v13'/'素材'/'23_双手抓短横杆.png'
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

def rolled_board(im,pull,age):
 from PIL import ImageFilter
 h=round(890*pull);end=140+h
 if h>0:
  section=BOARD.crop((0,0,1450,h));im.paste(section,(24,140),section)
 # A moving cylindrical paper edge with underside, shadow, curved print and spiral endcaps.
 settle=b.ease((age-1.94)/.25)
 radius=max(2,round((36-12*pull)*(1-settle)))
 if settle>=1:return
 layer=Image.new('RGBA',im.size);dd=ImageDraw.Draw(layer)
 dd.rounded_rectangle((30,end+radius-2,1476,end+radius+15),radius=10,fill=(88,113,117,80))
 im.paste(layer.filter(ImageFilter.GaussianBlur(9)),(0,0),layer.filter(ImageFilter.GaussianBlur(9)))
 d=ImageDraw.Draw(im)
 for offset in range(-radius,radius+1):
  z=offset/radius
  light=math.sqrt(max(0,1-z*z));shade=round(211+35*light-7*max(0,z))
  color=(min(255,shade+7),min(255,shade+3),max(0,shade-13))
  d.line([(24,end+offset),(1474,end+offset)],fill=color,width=1)
 # The printed edge bends around the upper half of the roll rather than being clipped flat.
 if h>radius*2:
  for k in range(-radius,-2):
   src=max(0,min(889,h-round(radius*(1-math.sin(k/radius*math.pi/2)))))
   strip=BOARD.crop((0,src,1450,src+1));im.paste(strip,(24,end+k),strip)
  d=ImageDraw.Draw(im)
 d.line([(24,end-radius),(1474,end-radius)],fill='#e5deca',width=2)
 d.line([(24,end+radius),(1474,end+radius)],fill='#b3b5a6',width=2)
 for x in (24,1474):
  d.ellipse((x-12,end-radius,x+12,end+radius),fill='#e4dcc4',outline='#a9ad9b',width=2)
  pts=[]
  for n in range(65):
   a=n/64*math.pi*4;r=1+(radius-3)*n/64
   pts.append((x+9*r/radius*math.cos(a),end+r*math.sin(a)))
  d.line(pts,fill='#b7ac8f',width=2)

# Contact center of the short handle in the generated sprite; verified visually.
HX,HY=245,378
GS=390
scale=GS/G.width
GH=G.height*scale
ys,xs=np.where(np.asarray(G)[:,:,3]>180);FY=float(ys.max())
GRIP_X=1490
GRAB_X=GRIP_X-HX*scale
END_EDGE=1050-(FY-HY)*scale
def hardware(d):
 d.rounded_rectangle((24,120,1474,153),radius=16,fill='#d8cdb3',outline='#91b7bc',width=3)
def transition(age):
 im=Image.blend(MAPBACK,ROOM,b.ease((age-.28)/.90))
 if age<.8:edge=140
 elif age<1.65:edge=140+(END_EDGE-140)*b.ease((age-.8)/.85)
 else:edge=END_EDGE+(1030-END_EDGE)*b.ease((age-1.65)/.50)
 # The short starting roll is already within jumping reach; board and hands move together while gripped.
 boardlayer=im.copy()
 if age>=.8:rolled_board(boardlayer,(edge-140)/890,age)
 im=Image.blend(im,boardlayer,b.ease(age/.22));d=ImageDraw.Draw(im);hardware(d)
 if age<.25:
  q=b.ease(age/.25);width=390*(1+.08*q);height=390*(1-.13*q)
  place(im,L,1510-(width-390)/2,1050-height,width,height)
 elif age<.8:
  q=b.ease((age-.25)/.55)
  y=660+(140-HY*scale-660)*q;x=1510+(GRAB_X-1510)*q
  place(im,G,x,y,GS,GH)
 elif age<1.65:
  # Exact common coordinate: painted horizontal bar center == board's moving lower edge.
  place(im,G,GRAB_X,edge-HY*scale,GS,GH)
 elif age<1.82:
  q=b.ease((age-1.65)/.17)
  held=im.copy();place(held,G,GRAB_X,END_EDGE-HY*scale,GS,GH)
  rest=im.copy();place(rest,L,1510,660,390);im=Image.blend(held,rest,q)
 else:
  q=(age-1.82)/.58;bounce=12*math.exp(-5*q)*math.sin(3*math.pi*q)
  place(im,L,1510,660+bounce,390)
 if age>1.65:
  d=ImageDraw.Draw(im);d.ellipse((1585,1040,1810,1053),fill='#bdc9c2')
 if age>1.6:
  title=im.copy();td=ImageDraw.Draw(title)
  td.text((40,35+b.F[53].getmetrics()[0]),'测体征 · 给海洋读“体温”',font=b.F[53],fill=b.INK,anchor='ls')
  im=Image.blend(im,title,b.ease((age-1.6)/.5))
 if age<.22:im=Image.blend(OLD_END,im,b.ease(age/.22))
 return im
def render(t):
 if t<CUT:return p.render(t)
 if t<CUT+BRIDGE:return transition(t-CUT)
 im=p.render(t-BRIDGE);hardware(ImageDraw.Draw(im));return im
def main():
 for a in (.7,.85,1.15,1.55,2.15):render(CUT+a).save(ROOT/f'双手接触检查_{a}.png')
 contact=Image.new('RGB',(1920,720),b.CREAM)
 for i,a in enumerate((.15,.70,.85,1.15,1.55,2.15)):
  contact.paste(render(CUT+a).resize((640,360)),((i%3)*640,(i//3)*360))
 contact.save(ROOT/'横梁起卷_六帧预览.jpg')
 if '--preview' in sys.argv:return
 out=ROOT/'交付'/'海洋发烧了_第二分钟_双手卷板_v14.mp4'
 a=math.ceil(CUT*24);z=math.ceil((CUT+BRIDGE)*24)
 patch=ROOT/'.build'/'横梁起卷_替换帧.mp4'
 cmd=[EXE,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p',str(patch)]
 with open(ROOT/'.build'/'patch_frames.log','w') as log:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for n in range(a,z):proc.stdin.write(render(n/24).tobytes())
  proc.stdin.close();assert proc.wait()==0
 previous=ROOT.parent/'双手抓杆_卷开拉板_v13'/'交付'/'海洋发烧了_第二分钟_双手卷板_v13.mp4'
 graph=f'[0:v]split=2[x][y];[x]trim=end_frame={a},setpts=PTS-STARTPTS[v0];[1:v]setpts=PTS-STARTPTS[v1];[y]trim=start_frame={z},setpts=PTS-STARTPTS[v2];[v0][v1][v2]concat=n=3:v=1:a=0[v]'
 with open(ROOT/'.build'/'patch_video.log','w') as log:subprocess.run([EXE,'-y','-i',str(previous),'-i',str(patch),'-filter_complex',graph,'-map','[v]','-map','0:a','-c:v','libx264','-preset','fast','-crf','19','-c:a','copy','-movflags','+faststart',str(out)],stdout=log,stderr=log,check=True)
 V11=ROOT.parent/'跳起拉板_左向解说_v11'
 clip=ROOT/'交付'/'双手抓杆_卷开拉板_转场预览_v14.mp4'
 encode(clip,CUT-1.3,BRIDGE+4.3,V11/'配音'/'转场试听.wav')
 first=ROOT.parent/'出入场_无制作提示_v9'/'交付'/'海洋发烧了_最新批注落实_出入场_v9.mp4'
 joined=ROOT/'交付'/'海洋发烧了_开场与前两段_双手卷板_v14.mp4'
 graph='[0:v]setsar=1,setpts=PTS-STARTPTS[v0];[1:v]setsar=1,setpts=PTS-STARTPTS[v1];[0:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a0];[1:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]'
 with open(ROOT/'.build'/'join.log','w') as log:subprocess.run([EXE,'-y','-i',str(first),'-i',str(out),'-filter_complex',graph,'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','19','-c:a','aac','-b:a','160k','-movflags','+faststart',str(joined)],stdout=log,stderr=log,check=True)
 for path in (out,clip,joined):
  result=subprocess.run([EXE,'-v','error','-i',str(path),'-f','null','-'],capture_output=True);assert result.returncode==0,result.stderr
 for filename in ('素材说明.md','台词与时间轴.json'):shutil.copy2(V11/filename,ROOT/filename)
 (ROOT/'验证.json').write_text(json.dumps(dict(full_decode='PASS',seconds=DURATION,contact_center=[HX,HY],grip_screen_x=GRIP_X,final_grip_edge_y=END_EDGE,pose='both flippers holding short horizontal bar, left-facing',no_rope=True,no_external_pulley=True,audio='unchanged cached Xiaoyi',clip=str(clip),joined=str(joined)),ensure_ascii=False,indent=2),encoding='utf-8')
 print(joined,flush=True)
if __name__=='__main__':main()
