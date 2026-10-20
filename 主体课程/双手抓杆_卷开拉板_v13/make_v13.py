from pathlib import Path
ROOT=Path(__file__).resolve().parent
src=(ROOT.parent/'卷开拉板_左向下拉_v12'/'build_v12.py').read_text(encoding='utf-8')
prefix=src[:src.index('alpha=np.asarray(G)')]
prefix=prefix.replace("'22_朝左上抓环下拉.png'","'23_双手抓短横杆.png'")
curl=src[src.index('def rolled_board('):src.index('def transition(age):',src.index('def rolled_board('))]
curl=curl.replace('(age-1.74)/.30','(age-1.94)/.25')
extra=r'''
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
 if age<.8:edge=450
 elif age<1.65:edge=450+(END_EDGE-450)*b.ease((age-.8)/.85)
 else:edge=END_EDGE+(1030-END_EDGE)*b.ease((age-1.65)/.50)
 # The short starting roll is already within jumping reach; board and hands move together while gripped.
 boardlayer=im.copy();rolled_board(boardlayer,(edge-140)/890,age)
 im=Image.blend(im,boardlayer,b.ease(age/.22));d=ImageDraw.Draw(im);hardware(d)
 if age<.25:
  q=b.ease(age/.25);width=390*(1+.08*q);height=390*(1-.13*q)
  place(im,L,1510-(width-390)/2,1050-height,width,height)
 elif age<.8:
  q=b.ease((age-.25)/.55)
  y=660+(450-HY*scale-660)*q;x=1510+(GRAB_X-1510)*q
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
 contact.save(ROOT/'双手卷板_六帧预览.jpg')
 if '--preview' in sys.argv:return
 out=ROOT/'交付'/'海洋发烧了_第二分钟_双手卷板_v13.mp4'
 encode(out,0,DURATION,ROOT/'配音'/'晓伊_拉板衔接.wav')
 V11=ROOT.parent/'跳起拉板_左向解说_v11'
 clip=ROOT/'交付'/'双手抓杆_卷开拉板_转场预览_v13.mp4'
 encode(clip,CUT-1.3,BRIDGE+4.3,V11/'配音'/'转场试听.wav')
 first=ROOT.parent/'出入场_无制作提示_v9'/'交付'/'海洋发烧了_最新批注落实_出入场_v9.mp4'
 joined=ROOT/'交付'/'海洋发烧了_开场与前两段_双手卷板_v13.mp4'
 graph='[0:v]setsar=1,setpts=PTS-STARTPTS[v0];[1:v]setsar=1,setpts=PTS-STARTPTS[v1];[0:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a0];[1:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]'
 with open(ROOT/'.build'/'join.log','w') as log:subprocess.run([EXE,'-y','-i',str(first),'-i',str(out),'-filter_complex',graph,'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','19','-c:a','aac','-b:a','160k','-movflags','+faststart',str(joined)],stdout=log,stderr=log,check=True)
 for path in (out,clip,joined):
  result=subprocess.run([EXE,'-v','error','-i',str(path),'-f','null','-'],capture_output=True);assert result.returncode==0,result.stderr
 for filename in ('素材说明.md','台词与时间轴.json'):shutil.copy2(V11/filename,ROOT/filename)
 (ROOT/'验证.json').write_text(json.dumps(dict(full_decode='PASS',seconds=DURATION,contact_center=[HX,HY],grip_screen_x=GRIP_X,final_grip_edge_y=END_EDGE,pose='both flippers holding short horizontal bar, left-facing',no_rope=True,no_external_pulley=True,audio='unchanged cached Xiaoyi',clip=str(clip),joined=str(joined)),ensure_ascii=False,indent=2),encoding='utf-8')
 print(joined,flush=True)
if __name__=='__main__':main()
'''
(ROOT/'build_v13.py').write_text(prefix+curl+extra,encoding='utf-8')
