from pathlib import Path
import importlib.util,math,json,wave,subprocess,hashlib
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
CHECK=ROOT/'检查';CHECK.mkdir(parents=True,exist_ok=True)
OUTDIR=PROJECT/'demooo'/'预览'/'太平洋云雨';OUTDIR.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('lesson',PROJECT/'环境多米诺_水_v37'/'build_part.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.load_audio();m.p.load_audio()
P=m.p;V=P.native.v;EXE=m.EXE
PREFIX=P.DATA[-1];LEAD=P.DURATION-PREFIX['start'];END=next(r['end'] for r in m.DATA if r['mode']=='整体');DURATION=LEAD+END
HEADER=P.header('降水重分配 · 从海洋到河流','信风减弱，云雨变化，地表响应')
SKY=V.gradient((1920,1080),(239,250,248),(190,224,231)).convert('RGB')
SEA=V.gradient((1200,325),(110,186,206),(39,108,146))
WARM=V.gradient((1200,220),(247,210,159),(232,164,127))

def path(a,b,c,d,n=65):return V.cubic(a,b,c,d,n)
def curve(draw,pts,color,width):
 draw.line(pts,fill=color,width=round(width),joint='curve')
 r=width/2
 for x,y in [pts[0],pts[-1]]:draw.ellipse((x-r,y-r,x+r,y+r),fill=color)

def rounded_outline(points):
 result=[];n=len(points)
 for i in range(n):
  p0,p1,p2,p3=[points[j%n] for j in (i-1,i,i+1,i+2)]
  for q in np.linspace(0,1,10,endpoint=False):
   result.append(tuple(.5*((2*p1[k])+(-p0[k]+p2[k])*q+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*q*q+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*q*q*q) for k in (0,1)))
 return result

def cloud(im,cx,base,strength,t,seed):
 w=120+190*strength;h=45+105*strength
 art=Image.new('RGBA',(720,400));d=ImageDraw.Draw(art)
 # A single softly outlined silhouette grows/shrinks in place rather than sliding like a sticker.
 pts=[(35,245),(35,216),(54,198),(88,194),(86,152),(112,123),(150,126),(171,76),(212,63),(251,84),(275,121),(318,103),(358,114),(374,151),(411,142),(445,164),(452,198),(491,202),(509,228),(496,251)]
 pts=rounded_outline(pts)
 d.polygon(pts,fill='#fdf9eb');d.line(pts+[pts[0]],fill='#9bbbc6',width=3,joint='curve')
 d.polygon([(39,234),(125,251),(257,246),(390,254),(502,236),(496,251),(140,269),(50,255)],fill='#d7e7e7')
 for x,y in [(125,169),(219,116),(324,151)]:d.arc((x-25,y-16,x+32,y+25),190,305,fill='#e0e8df',width=3)
 art=art.crop((25,54,520,273)).resize((round(w),round(h)),Image.Resampling.LANCZOS)
 alpha=.25+.75*strength;art.putalpha(art.getchannel('A').point(lambda x:round(x*alpha)))
 im.paste(art,(round(cx-w/2),round(base-h)),art)
 rain=Image.new('RGBA',im.size);rd=ImageDraw.Draw(rain)
 for i in range(23):
  if (i*.618+seed*.17)%1>strength:continue
  phase=(t*(1.35+strength*.3)+i*.381+seed*.2)%1
  x=cx-w*.34+(i%9)*w*.085;y=base+9+phase*max(20,584-base)
  a=round(190*strength*math.sin(math.pi*phase));rd.line((x,y,x-4,y+14),fill=(74,145,175,a),width=3)
 im.paste(rain,(0,0),rain)

def river(im,side,level,t):
 d=ImageDraw.Draw(im)
 if side==0:
  hill=[(0,564),(58,542),(102,580),(151,560),(217,603),(292,607),(360,651),(360,958),(0,958)]
  pts=path((23,590),(299,630),(45,755),(309,934))
 else:
  hill=[(1560,650),(1620,615),(1664,625),(1720,573),(1795,592),(1855,544),(1920,564),(1920,958),(1560,958)]
  pts=path((1898,591),(1640,624),(1860,760),(1609,934))
 d.polygon(hill,fill='#b8c9a6');d.line(hill[:7],fill='#8da99b',width=3,joint='curve')
 # Bank exposure and channel width change continuously with runoff.
 curve(d,pts,'#d9c4a0',74)
 curve(d,pts,'#acb9a0',58)
 width=13+38*level;curve(d,pts,'#68a6bf',width)
 curve(d,[(x+2,y) for x,y in pts],'#9bcede',max(4,width*.34))
 for i in range(7):
  q=(t*(.11+.08*level)+i/7)%1;j=min(len(pts)-4,max(1,round(q*(len(pts)-5))))
  curve(d,pts[j:j+3],'#d7edf0',2)
 # Uneven riparian foliage is anchored to land, never moved as a whole.
 for j in range(8):
  x=35+j*39 if side==0 else 1590+j*41;y=790+(j%3)*49
  if abs(x-pts[round(j/8*(len(pts)-1))][0])<29:continue
  color='#839f82' if level>.3 else '#a7ae86'
  d.line((x,y,x-4,y-29),fill='#7e9280',width=3)
  d.ellipse((x-13,y-41,x+6,y-23),fill=color);d.ellipse((x-1,y-34,x+17,y-15),fill=color)

def diagram(t,records):
 west=m.ease((t-3.3)/4.8);east=m.ease((t-8.5)/4.8)
 im=SKY.copy();im.paste(HEADER,(16,14),HEADER);d=ImageDraw.Draw(im)
 m.card(im,'西太平洋 · 印尼一侧',(65,182,605,250),40,m.INK,records)
 m.card(im,'强事件 · 秘鲁北部沿岸',(1280,182,1855,250),38,m.INK,records)
 # One unbroken ocean profile; the upper layer evolves instead of an oval moving across a map.
 xs=np.arange(1200);q=xs/1199
 dep=(160-98*q)*(1-east)+(108-4*q)*east+3*np.sin(xs/83+t*.45)
 mask=Image.new('L',(1200,325));md=ImageDraw.Draw(mask)
 edge=[(int(x),float(dep[x])) for x in range(0,1200,3)]+[(1199,float(dep[-1]))]
 md.polygon([(0,0),(1199,0)]+edge[::-1],fill=255)
 sea=SEA.copy();warm=WARM.resize((1200,325));sea.paste(warm,(0,0),mask);im.paste(sea,(360,620));d=ImageDraw.Draw(im)
 curve(d,[(360+x,620+y) for x,y in edge],'#f7e8c8',3)
 curve(d,[(360+x,620+3*math.sin(x/75+t*.75)) for x in range(0,1200,8)],'#f5fbef',4)
 # Small warm-water glints travel east, confined to the continuous warm layer.
 for i in range(17):
  u=(i/17+t*.035*east)%1;x=388+u*1130;y=651+(i%3)*15
  d.line((x,y,x+16+east*10,y),fill='#fbe7c1',width=2)
 river(im,0,1-.85*west,t);river(im,1,.12+.88*east,t)
 d=ImageDraw.Draw(im)
 # Easterly wind streaks weaken without reversing direction.
 for j in range(3):
  length=590-310*west;right=1295-j*24;yy=303+j*28
  pts=[(right-length*u,yy+3*math.sin(u*math.pi*2+j)) for u in np.linspace(0,1,80)]
  curve(d,pts,'#9ab9c3',3)
  for k in range(2):
   u=(t*(.3-.08*west)+k/2+j*.15)%1;ix=round(u*72);curve(d,pts[ix:ix+6],'#f0faf4',4)
  x,y=pts[-1];d.polygon([(x-1,y),(x+10,y-5),(x+10,y+5)],fill='#8daebc')
 m.text(im,'东风信风减弱',1010,263,29,m.BLUE,True,records)
 cloud(im,475,472,.96-.75*west,t,0)
 cloud(im,1640,476,.13+.85*east,t,1)
 if t>5.5:
  m.card(im,'降水减少',(86,308,348,372),36,m.BLUE,records)
 if t>10.4:
  m.card(im,'降雨增强',(1575,260,1836,318),32,m.CORAL,records)
 if t>12.8:
  m.card(im,'雨水补给减少',(54,871,329,937),29,m.BLUE,records)
  m.card(im,'地表径流增多',(1590,871,1865,937),29,m.CORAL,records)
 m.text(im,'暖水层',760,680,30,m.CORAL,True,records)
 return im

def render(t):
 if t<LEAD:return P.render(PREFIX['start']+t)[0],{'time':t,'scene':'前段提问','labels':[]}
 u=t-LEAD;row=next((r for r in m.DATA if r['start']<=u<r['end']),m.DATA[0]);records=[]
 im=diagram(u,records)
 # The opening map establishes positions, then gives way to a fixed illustrated profile.
 if u<3.7:
  mapim=P.map_scene('承下',0)[0];head=P.header('预测揭晓 · 从哪里开始变化','先定位，再看海洋与陆地的连续响应');mapim.paste(head,(16,14),head)
  im=Image.blend(mapim,im,m.ease((u-2.6)/1.1))
 d=ImageDraw.Draw(im);d.rectangle((0,958,1920,1080),fill='#244b60')
 lines=[];line=''
 for ch in row['text']:
  if m.font(46).getlength(line+ch)>1750:lines.append(line);line=ch
  else:line+=ch
 if line:lines.append(line)
 y=965 if len(lines)>1 else 987
 for line in lines:m.text(im,line,960,y,46,'#fffaf0',True,records);y+=49
 return im,{'time':t,'scene':'连续剖面' if u>=3.7 else '地图转入','labels':records,'camera_fixed':True}

def main():
 a=P.PCM[round(PREFIX['start']*24000):];b=m.PCM[:round(END*24000)];pcm=np.concatenate([a,b])
 audio=ROOT/'复用配音.wav'
 with wave.open(str(audio),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm.tobytes())
 times=[1,LEAD+1,LEAD+4.3,LEAD+7.5,LEAD+11.5,LEAD+16]
 contact=Image.new('RGB',(1920,1140),'#e8f0ef');dd=ImageDraw.Draw(contact)
 for i,t in enumerate(times):
  im,_=render(t);im.save(CHECK/f'节点_{i}.png');x=i%2*960;y=i//2*380
  contact.paste(im.resize((640,360),Image.Resampling.LANCZOS),(x,y));dd.text((x+650,y+12),f'{t:.2f}s',fill=m.INK)
 contact.save(CHECK/'连续场景检查.jpg',quality=95)
 if '--preview' in __import__('sys').argv:return
 out=OUTDIR/'.太平洋云雨.pending.mp4';cmd=[EXE,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(audio),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE);audit=[];count=math.ceil(DURATION*24)
 for i in range(count):
  im,meta=render(i/24);audit.append(meta);proc.stdin.write(im.tobytes())
  if i%120==0:print('Render',i,'/',count,flush=True)
 proc.stdin.close();err=proc.stderr.read();assert proc.wait()==0,err
 check=subprocess.run([EXE,'-v','error','-i',str(out),'-f','null','-'],capture_output=True);assert check.returncode==0 and not check.stderr,check.stderr
 (CHECK/'逐帧检查.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 report=dict(pending=str(out),output=str(OUTDIR/'海洋发烧了_太平洋云雨.mp4'),seconds=DURATION,frames_checked=count,resolution=[1920,1080],fps=24,decode='PASS',visual_review='待抽帧复核',audio='原v36结句及v37前四句，不新生成配音',full_segments_unchanged=True,sha256=hashlib.sha256(out.read_bytes()).hexdigest())
 (ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
