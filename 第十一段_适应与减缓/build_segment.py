from pathlib import Path
import sys,json,math,io,subprocess,importlib.util
import numpy as np
from PIL import Image,ImageDraw,ImageOps
R=Path(__file__).resolve().parent;P=R.parent
s=importlib.util.spec_from_file_location('base11',P/'多米诺转场_企鹅串讲/build_transitions.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
M=json.loads((R/'台词与时间轴.json').read_text(encoding='utf-8'));ROWS=M['lines'];D=M['duration'];F=b.F;E=b.E;INK=b.INK;BLUE=b.BLUE;ORANGE='#ce8561';CREAM=b.CREAM
OUT=P/'demooo/独立片段/11_适应与减缓/海洋发烧了_第十一段_适应与减缓.mp4';OUT.parent.mkdir(parents=True,exist_ok=True)
CHECK=R/'检查';CHECK.mkdir(exist_ok=True);AUDIT=[];PCM=b.read_pcm(R/'配音/第十一段.wav')
HEADS=[b.o.p.header('处方一·适应行动','早发现、早预警、早行动'),b.o.p.header('处方二·减缓增暖','控制排放，降低长期风险背景')]
SCREEN=Image.open(R/'素材/NOAA_CPC官方页面原始截图.png').convert('RGB').crop((0,0,1600,355)).resize((1280,284),Image.Resampling.LANCZOS)
PHOTOS=[ImageOps.fit(Image.open(R/'素材'/n).convert('RGB'),(630,395),Image.Resampling.LANCZOS) for n in ['光伏原图.jpg','风电原图.jpg']]
POSES={i:Image.open(next(b.SPRITES.glob(f'{i:02d}_*'))).convert('RGBA').resize((390,390),Image.Resampling.LANCZOS) for i in [8,11]}
def row(mode):return next(r for r in ROWS if r['mode']==mode)
def text(im,s,x,y,size=56,color=INK,center=False):
 w=F(size).getlength(s);xx=x-w/2 if center else x;assert 20<=xx and xx+w<=1900 and 14<=y and y+size<=1062,(s,xx,y,w)
 b.o.txt(im,s,x,y,size,color,center);AUDIT.append(dict(text=s,box=[xx,y,xx+w,y+size]))
def panel(im,box,fill=CREAM,outline='#b3ccd1'):
 ImageDraw.Draw(im).rounded_rectangle(box,24,fill=fill,outline=outline,width=2)
def arrow(im,pts,color=BLUE,width=6):b.o.p.native.arrow(im,pts,color,width,1)
def icon(im,kind,cx,cy,size=100,t=0):
 d=ImageDraw.Draw(im);q=size/100
 if kind=='bag':
  d.rounded_rectangle((cx-40*q,cy-28*q,cx+40*q,cy+38*q),12*q,fill='#dba780',outline=ORANGE,width=3)
  d.arc((cx-20*q,cy-53*q,cx+20*q,cy-8*q),180,360,fill=ORANGE,width=max(2,round(5*q)))
  d.rounded_rectangle((cx-8*q,cy-9*q,cx+8*q,cy+21*q),3*q,fill=CREAM);d.rounded_rectangle((cx-23*q,cy-1*q,cx+23*q,cy+13*q),3*q,fill=CREAM)
 elif kind=='lamp':
  d.ellipse((cx-31*q,cy-45*q,cx+31*q,cy+17*q),fill='#f4d391',outline='#c5a46a',width=3)
  d.rounded_rectangle((cx-17*q,cy+10*q,cx+17*q,cy+39*q),5*q,fill='#a6bbc2');d.line((cx-12*q,cy+45*q,cx+12*q,cy+45*q),fill=INK,width=3)
  for a in [-math.pi*.9,-math.pi*.5,-math.pi*.1]:
   rr=(57+2*math.sin(t*2))*q;d.line((cx+rr*math.cos(a),cy-12*q+rr*math.sin(a),cx+(rr+11*q)*math.cos(a),cy-12*q+(rr+11*q)*math.sin(a)),fill='#d9b571',width=3)
 elif kind=='monitor':
  d.rounded_rectangle((cx-39*q,cy-30*q,cx+39*q,cy+22*q),6*q,fill='#b3d4df',outline=BLUE,width=3);d.line((cx,cy+23*q,cx,cy+40*q),fill=BLUE,width=4);d.line((cx-23*q,cy+41*q,cx+23*q,cy+41*q),fill=BLUE,width=4)
  d.line([(cx-29*q,cy+5*q),(cx-12*q,cy-6*q),(cx+3*q,cy+1*q),(cx+27*q,cy-18*q)],fill=CREAM,width=4)
 elif kind=='bell':
  d.pieslice((cx-32*q,cy-39*q,cx+32*q,cy+34*q),180,360,fill='#e2b788',outline=ORANGE,width=3);d.line((cx-36*q,cy,cx+36*q,cy),fill=ORANGE,width=5);d.ellipse((cx-6*q,cy+10*q,cx+6*q,cy+22*q),fill=ORANGE)
def check(im,x,y,q=1,color=BLUE):
 pts=[(x,y),(x+13,y+14),(x+40,y-19)];d=ImageDraw.Draw(im)
 if q<.45:d.line([pts[0],(x+13*q/.45,y+14*q/.45)],fill=color,width=5)
 else:d.line([pts[0],pts[1],(pts[1][0]+27*(q-.45)/.55,pts[1][1]-33*(q-.45)/.55)],fill=color,width=5)
def bg():
 im=b.o.m.BG.copy();panel(im,(452,211,1880,947));return im
def adaptation(t):
 im=bg();d=ImageDraw.Draw(im);age=t-2;text(im,'适应：把暴露与损失降下来',1165,238,64,INK,True)
 for i,(name,k) in enumerate(zip(['监测','预警','行动'],['monitor','bell','bag'])):
  q=E((age-.2-i*.95)/.45)
  if q<=0:continue
  x=495+i*452;y=344+round(14*(1-q));panel(im,(x,y,x+405,y+188),fill='#e8f2f3' if i!=1 else '#f8eddd');icon(im,k,x+88,y+91,80,t);text(im,name,x+238,y+65,62,BLUE if i!=1 else ORANGE,True)
  if i:arrow(im,[(x-38,y+94),(x-10,y+94)],BLUE,4)
 if t<row('行动')['start']:
  im.paste(SCREEN,(520,600));text(im,'NOAA CPC · 通报2026-10-08 · 截取2026-10-16',1165,899,33,BLUE,True)
  if t>=row('监测')['start']:text(im,'先看官方监测，再查本地预警',1165,544,41,INK,True)
 else:
  text(im,'按预警指引，把准备变成行动',1165,574,52,INK,True)
  for j,words in enumerate(['准备应急物品','调整出行安排','合理安排用水']):
   q=E((t-row('行动')['start']-.3-j*.7)/.4)
   if q<=0:continue
   yy=672+j*76;panel(im,(650,yy-6,1720,yy+59),fill='#f1f4ed');check(im,690,yy+25,q);text(im,words,1165,yy+2,47,INK,True)
  if t>=row('损失')['start']:text(im,'准备应对影响 ≠ 消除厄尔尼诺',1165,899,40,ORANGE,True)
 return im
def mitigation(t):
 im=bg();text(im,'减缓：减少温室气体排放',1165,238,64,INK,True)
 age=t-row('减缓')['start'];d=ImageDraw.Draw(im)
 for j,(photo,name,loc) in enumerate(zip(PHOTOS,['光伏发电','风力发电'],['新疆巴州 · 乌若高速附近','新疆巴里坤 · 三塘湖风电场'])):
  q=E((age-j*.16)/.48);x=495+j*680;yy=342+round(10*(1-q));im.paste(photo,(x,yy),Image.new('L',photo.size,round(255*q)))
  if q>.3:text(im,name,x+315,757,53,BLUE,True);text(im,loc,x+315,819,36,INK,True)
 if age>2.2:
  q=E((age-2.2)/.6);text(im,'限制长期人为增暖',1165,879,55,ORANGE,True)
 if t>=row('自然')['start']:
  panel(im,(585,865,1745,934),fill='#f8eddd');text(im,'不能阻止自然发生的厄尔尼诺',1165,878,47,ORANGE,True)
 return im
def choices(t):
 im=bg();d=ImageDraw.Draw(im);thinking=M['thinking'][0]<=t<M['thinking'][1]
 text(im,'今天，你选哪一项？' if t>=row('选择')['start'] else '适应和减缓，别混成一类',1165,239,64,INK,True)
 for i,(name,task,kind,col) in enumerate([('适应','和家人检查应急包','bag',BLUE),('减缓','完成一次节能行动','lamp',ORANGE)]):
  x=495+i*680;panel(im,(x,382,x+630,869),fill='#e8f2f3' if i==0 else '#f8efdc');text(im,name,x+315,410,64,col,True);icon(im,kind,x+315,594,150,t);text(im,task,x+315,728,53,INK,True)
  text(im,'降低暴露与损失' if i==0 else '减少温室气体排放',x+315,810,40,col,True)
 if not thinking and t<row('选择')['start']:
  start=row('区分')['start'];age=t-start
  if age>1.5:check(im,560,750,E((age-1.5)/.4))
  if age>3.0:check(im,1240,750,E((age-3)/.4),ORANGE)
 if thinking:
  shade=Image.new('RGBA',im.size,(0,0,0,0));ImageDraw.Draw(shade).rounded_rectangle((452,211,1880,947),24,fill=(28,60,76,72));im=Image.alpha_composite(im.convert('RGBA'),shade).convert('RGB')
  panel(im,(1030,350,1300,615));text(im,str(3-int(t-M['thinking'][0])),1165,392,142,INK,True)
 return im
def character(im,t):
 r=next((r for r in ROWS if r['start']<=t<r['end']),None);thinking=M['thinking'][0]<=t<M['thinking'][1]
 if t<1.2:pose=8
 elif M['chapter2']<=t<M['chapter2']+1.2:pose=11
 elif thinking:pose=9
 elif t>=row('记录')['speech_end']:pose=12
 else:pose=6 if r and r['mode'] in ['监测','行动','减缓','区分'] else 3
 art=(POSES[pose] if pose in POSES else b.POSES[pose]).copy()
 if pose in (3,6):
  a=PCM[int(t*24000):int(t*24000)+960].astype(np.float32)/32768;rms=float(np.sqrt(np.mean(a*a))) if len(a) else 0;state=0 if rms<.011 else 1 if rms<.055 else 2 if rms<.13 else 3
  mx,my,mw,mh=b.o.m.MOUTH_CENTERS[pose];art.alpha_composite(b.MOUTHS[pose,state],(round((mx-mw/2)*390/512),round((my-mh/2)*390/512)))
 yy=round(580+1.8*math.sin(t*2));im.paste(art,(20,yy),art);b.AUDIT.append(dict(kind='character',pose=pose,box=[20,yy,410,yy+390]))
 if r:b.bubble(im,r['text'],t-r['start'],max(.1,r['speech_end']-r['start']))
 elif thinking:b.bubble(im,'你选哪一项？',0,3)
def frame(t):
 global AUDIT
 AUDIT=[];b.AUDIT=[];idx=int(t>=M['chapter2']);intro=t<2 or M['chapter2']<=t<M['chapter2']+2
 if intro:im=bg()
 elif t<row('减缓')['start']:im=adaptation(t)
 elif t<row('区分')['start']:im=mitigation(t)
 else:im=choices(t)
 head=HEADS[idx];age=t-(0 if idx==0 else M['chapter2'])
 if age<2:
  q=E(age-1);scale=1.28-.28*q;art=head.resize((round(head.width*scale),round(head.height*scale)),Image.Resampling.LANCZOS);im.paste(art,(round((960-art.width/2)*(1-q)),round((450-art.height/2)*(1-q))),art)
 else:im.paste(head,(0,0),head)
 character(im,t);return im
def main():
 n=math.ceil(D*24);tmp=OUT.with_name('.第十一段.pending.mp4');log=(R/'编码日志.txt').open('wb');proc=subprocess.Popen([b.FF,'-v','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(R/'配音/第十一段.wav'),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart','-shortest',str(tmp)],stdin=subprocess.PIPE,stderr=log)
 audits=[]
 for i in range(n):
  im=frame(i/24);proc.stdin.write(im.convert('RGB').tobytes());audits.append(dict(frame=i,text=AUDIT,character=b.AUDIT))
  if i%240==0:print('frame',i,'/',n,flush=True)
 proc.stdin.close();assert proc.wait()==0;log.close();b.manager.decode(tmp);tmp.replace(OUT)
 times=[3.8,7.5,11.7,16,row('减缓')['start']+2.5,row('自然')['start']+1,row('区分')['start']+3.8,row('选择')['start']+2,M['thinking'][0]+1.1,row('记录')['start']+1,D-.2]
 sheet=Image.new('RGB',(1920,1080),'#dfe9eb')
 for j,t in enumerate(times):
  raw=subprocess.run([b.FF,'-v','error','-ss',str(t),'-i',str(OUT),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True,check=True).stdout;im=Image.open(io.BytesIO(raw));im.save(CHECK/f'{j:02d}_{t:.2f}.png');sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),((j%4)*480,(j//4)*360));ImageDraw.Draw(sheet).text(((j%4)*480+8,(j//4)*360+278),f'{t:.2f}s',font=F(25),fill=INK)
 sheet.save(CHECK/'编码抽帧总览.jpg');(CHECK/'逐帧对象边界.json').write_text(json.dumps(audits,ensure_ascii=False),encoding='utf-8')
 info=b.manager.info(OUT);(CHECK/'验证.json').write_text(json.dumps(dict(**info,resolution='1920x1080',fps=24,frames=n,decode='PASS',review_nodes=times),ensure_ascii=False,indent=2),encoding='utf-8')
 data=json.loads(b.manager.MANIFEST.read_text(encoding='utf-8'));data['segments']['11_适应与减缓']=dict(path=str(OUT.relative_to(b.manager.ROOT)),**info,decode='PASS',word_shots=[24,25],comment_ids=[20]);b.manager.write_manifest(data);print(str(OUT),info,flush=True)
if __name__=='__main__':main()
