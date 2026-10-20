from pathlib import Path
ROOT=Path(__file__).resolve().parent
V11=ROOT.parent/'跳起拉板_左向解说_v11'
source=(V11/'build_v11.py').read_text(encoding='utf-8').split('def main():')[0]
source=source.replace("LEFT=ROOT/'素材'/'20_朝左介绍.png';GRAB=ROOT/'素材'/'21_抬臂抓环.png'", "LEFT=ROOT.parent/'跳起拉板_左向解说_v11'/'素材'/'20_朝左介绍.png';GRAB=ROOT/'素材'/'22_朝左上抓环下拉.png'")
extra=r'''
def hardware(d):
 d.rounded_rectangle((24,120,1474,153),radius=16,fill='#d8cdb3',outline='#91b7bc',width=3)
 d.line([(1472,137),(1755,137)],fill='#a4bfc1',width=6)
 d.ellipse((1742,124,1768,150),fill='#f3e5c3',outline='#91b7bc',width=3)
def rolled_board(im,pull,age):
 from PIL import ImageFilter
 h=round(890*pull);end=140+h
 if h>0:
  section=BOARD.crop((0,0,1450,h));im.paste(section,(24,140),section)
 # A moving cylindrical paper edge with underside, shadow, curved print and spiral endcaps.
 settle=b.ease((age-1.74)/.30)
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
def transition(age):
 roomq=b.ease((age-.45)/.95);im=Image.blend(MAPBACK,ROOM,roomq)
 pull=b.ease((age-.83)/.98)
 if age>.65:rolled_board(im,pull,age)
 d=ImageDraw.Draw(im);hardware(d)
 if age<.30:
  q=b.ease(age/.30);width=390*(1+.08*q);height=390*(1-.13*q)
  place(im,L,1510-(width-390)/2,1050-height,width,height);hand=PEAK_HAND
 elif age<.83:
  q=(age-.30)/.53;y=660-240*(1-(1-q)**2);x=1510+(GRAB_X-1510)*b.ease(q)
  place(im,G,x,y,430,430*(1+.04*math.sin(q*math.pi)));hand=PEAK_HAND
 elif age<1.81:
  y=420+220*pull;place(im,G,GRAB_X,y,430);hand=y+GY/G.height*430
 else:
  q=(age-1.81)/.59;bounce=14*math.exp(-5*q)*math.sin(3*math.pi*q)
  place(im,L,1510,660+bounce,390);hand=END_HAND-(END_HAND-170)*b.ease((age-1.86)/.40)
 if age<2.27:
  d=ImageDraw.Draw(im);d.line([(ANCHOR,151),(ANCHOR,hand-9)],fill='#91b7bc',width=5)
  d.ellipse((ANCHOR-12,hand-12,ANCHOR+12,hand+12),fill=None,outline='#bd8962',width=5)
 if age>=1.81:
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
 for a in (.90,1.13,1.40,1.67,1.92):render(CUT+a).save(ROOT/f'卷边检查_{a}.png')
 contact=Image.new('RGB',(1920,720),b.CREAM)
 for i,a in enumerate((.60,.90,1.13,1.40,1.67,2.15)):
  contact.paste(render(CUT+a).resize((640,360)),((i%3)*640,(i//3)*360))
 contact.save(ROOT/'卷开拉板_六帧预览.jpg')
 if '--preview' in sys.argv:return
 V11=ROOT.parent/'跳起拉板_左向解说_v11'
 # Only rerender the revised transition; keep the lesson's other frames and cached narration.
 a=math.ceil(CUT*24);z=math.ceil((CUT+BRIDGE)*24);bridge=ROOT/'.build'/'卷开转场_替换帧.mp4'
 command=[EXE,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-an','-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p',str(bridge)]
 with open(ROOT/'.build'/'bridge.log','w') as log:
  proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=log)
  for n in range(a,z):proc.stdin.write(render(n/24).tobytes())
  proc.stdin.close();assert proc.wait()==0
 old=V11/'交付'/'海洋发烧了_第二分钟_跳起拉板_v11.mp4'
 out=ROOT/'交付'/'海洋发烧了_第二分钟_卷开拉板_v12.mp4'
 graph=f'[0:v]split=2[x][y];[x]trim=end_frame={a},setpts=PTS-STARTPTS[v0];[1:v]setpts=PTS-STARTPTS[v1];[y]trim=start_frame={z},setpts=PTS-STARTPTS[v2];[v0][v1][v2]concat=n=3:v=1:a=0[v]'
 with open(ROOT/'.build'/'patch.log','w') as log:subprocess.run([EXE,'-y','-i',str(old),'-i',str(bridge),'-filter_complex',graph,'-map','[v]','-map','0:a','-c:v','libx264','-preset','fast','-crf','19','-c:a','copy','-movflags','+faststart',str(out)],stdout=log,stderr=log,check=True)
 clip=ROOT/'交付'/'面朝左_卷开拉板_转场预览_v12.mp4'
 encode(clip,CUT-1.3,BRIDGE+4.3,V11/'配音'/'转场试听.wav')
 first=ROOT.parent/'出入场_无制作提示_v9'/'交付'/'海洋发烧了_最新批注落实_出入场_v9.mp4'
 joined=ROOT/'交付'/'海洋发烧了_开场与前两段_卷开拉板_v12.mp4'
 graph='[0:v]setsar=1,setpts=PTS-STARTPTS[v0];[1:v]setsar=1,setpts=PTS-STARTPTS[v1];[0:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a0];[1:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]'
 with open(ROOT/'.build'/'join.log','w') as log:subprocess.run([EXE,'-y','-i',str(first),'-i',str(out),'-filter_complex',graph,'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','19','-c:a','aac','-b:a','160k','-movflags','+faststart',str(joined)],stdout=log,stderr=log,check=True)
 for path in (out,clip,joined):
  result=subprocess.run([EXE,'-v','error','-i',str(path),'-f','null','-'],capture_output=True);assert result.returncode==0,result.stderr
 for filename in ('素材说明.md','台词与时间轴.json'):shutil.copy2(V11/filename,ROOT/filename)
 (ROOT/'验证.json').write_text(json.dumps(dict(full_decode='PASS',seconds=DURATION,changed_frames=[a,z],pose='left-facing upward left pull, no mirroring',curl='cylindrical moving edge, printed curvature, spiral endcaps, soft shadow, smooth flattening',audio='cached v11, unchanged',clip=str(clip),joined=str(joined)),ensure_ascii=False,indent=2),encoding='utf-8')
 print(joined,flush=True)
if __name__=='__main__':main()
'''
# Contact coordinate will be verified against the generated pose before rendering.
extra=extra.replace('def hardware(d):',"alpha=np.asarray(G)[:,:,3]\nys,xs=np.where(alpha[:,:round(G.width*.27)]>180)\nGY=int(ys.min())+5\nGX=float(xs[ys<ys.min()+12].mean())\nGRAB_X=1440\nANCHOR=GRAB_X+GX/G.width*430\nPEAK_HAND=420+GY/G.height*430\nEND_HAND=640+GY/G.height*430\ndef hardware(d):")
(ROOT/'build_v12.py').write_text(source+extra,encoding='utf-8')
