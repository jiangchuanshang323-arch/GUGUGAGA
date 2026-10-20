from pathlib import Path
import sys,json,math,io,subprocess,importlib.util
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;P=R.parent
s=importlib.util.spec_from_file_location('base12',P/'多米诺转场_企鹅串讲/build_transitions.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
M=json.loads((R/'台词与时间轴.json').read_text(encoding='utf-8'));ROWS=M['lines'];D=M['duration'];F=b.F;E=b.E;INK=b.INK;BLUE=b.BLUE;ORANGE='#ce8561';CREAM=b.CREAM
OUT=P/'demooo/独立片段/12_总结与检测/海洋发烧了_第十二段_总结与检测.mp4';OUT.parent.mkdir(parents=True,exist_ok=True)
CHECK=R/'检查';CHECK.mkdir(exist_ok=True);AUDIT=[];PCM=b.read_pcm(R/'配音/第十二段.wav')
HEADS=[b.o.p.header('总结·四步会诊','从海气变化，看到环境整体性'),b.o.p.header('检测·学会迁移','判读、解释、区域联系与应对')]
POSES={i:Image.open(next(b.SPRITES.glob(f'{i:02d}_*'))).convert('RGBA').resize((390,390),Image.Resampling.LANCZOS) for i in [11,16,17,18]}
def row(mode):return next(r for r in ROWS if r['mode']==mode)
def text(im,s,x,y,size=56,color=INK,center=False):
 w=F(size).getlength(s);xx=x-w/2 if center else x;assert 20<=xx and xx+w<=1900 and 14<=y and y+size<=1062,(s,xx,y,w)
 b.o.txt(im,s,x,y,size,color,center);AUDIT.append(dict(text=s,box=[xx,y,xx+w,y+size]))
def panel(im,box,fill=CREAM,outline='#b3ccd1'):ImageDraw.Draw(im).rounded_rectangle(box,24,fill=fill,outline=outline,width=2)
def arrow(im,pts,color=BLUE,width=6):b.o.p.native.arrow(im,pts,color,width,1)
def bg():
 im=b.o.m.BG.copy();panel(im,(452,211,1880,947));return im
def emblem(im,k,cx,cy,t):
 d=ImageDraw.Draw(im)
 if k==0:
  d.rounded_rectangle((cx-13,cy-53,cx+13,cy+32),13,fill='#f7f2dc',outline=BLUE,width=3);d.ellipse((cx-24,cy+17,cx+24,cy+65),fill='#db9e79',outline=ORANGE,width=3);d.rounded_rectangle((cx-5,cy-24,cx+5,cy+33),5,fill=ORANGE)
 elif k==1:
  arrow(im,[(cx-71,cy+22),(cx-71,cy-40),(cx+65,cy-40)],BLUE,5);arrow(im,[(cx+71,cy-30),(cx+71,cy+35),(cx-65,cy+35)],ORANGE,5)
 elif k==2:
  for j,col in enumerate(['#90b7c5','#cbb18a','#a2ba93','#b7a398','#b7b0c4']):
   x=cx-84+j*35;d.rounded_rectangle((x,cy-39,x+25,cy+44),5,fill='#faf8ee',outline=col,width=3);d.ellipse((x+8,cy-15,x+17,cy-6),fill=col)
 else:
  d.rounded_rectangle((cx-54,cy-47,cx+54,cy+51),8,fill='#f1ead5',outline=BLUE,width=3)
  for j in range(3):d.line((cx-29,cy-23+j*25,cx+30,cy-23+j*25),fill=BLUE,width=4)
def recap(t):
 im=bg();d=ImageDraw.Draw(im);text(im,'海洋“发烧”，怎样完成会诊？',1165,241,63,INK,True)
 for i,label in enumerate(['测体征','查病因','追并发症','开处方']):
  age=t-(row('会诊')['start']+2.0+i*.8);q=E(age/.4)
  if q<=0:continue
  x=495+i*338;yy=350+round(12*(1-q));panel(im,(x,yy,x+300,yy+215),fill='#e8f2f3' if i%2==0 else '#f8eddd');emblem(im,i,x+150,yy+76,t);text(im,label,x+150,yy+153,48,INK,True)
 names=[['信风','减弱'],['暖水','东移'],['东部上涌','减弱'],['沃克环流','减弱或错位'],['水热格局','改变']];offsets=[0,1.1,2.5,4.5,6.5]
 for i,lines in enumerate(names):
  age=t-row('机制')['start']-offsets[i];q=E(age/.45)
  if q<=0:continue
  x=495+i*270;panel(im,(x,663,x+235,820),fill='#f0f4ef');text(im,lines[0],x+117,688,42,BLUE,True);text(im,lines[1],x+117,753,42,ORANGE,True)
  if i:arrow(im,[(x-30,740),(x-7,740)],BLUE,4)
 if t>=row('辨析')['start']:text(im,'遥相关 · 滞后 · 分清自然变率与人为增暖',1165,883,43,INK,True)
 return im
def quiz(t):
 im=bg();d=ImageDraw.Draw(im);text(im,'把知识用到一个新情境',1165,236,65,INK,True)
 text(im,'教学假设',520,316,35,ORANGE)
 panel(im,(495,362,1835,508),fill='#e8f2f3')
 text(im,'Niño3.4区持续异常偏暖，信风减弱；',1165,379,46,INK,True);text(im,'石河子某校收到当地强降雨预警。',1165,447,46,INK,True)
 questions=['1  海温距平正负？','2  东部上升流如何变化？','3  能断定石河子暴雨吗？','4  学校怎样应对，属于哪类？'];answers=['正值','上升流减弱','不能仅凭厄尔尼诺断定','按预警调整活动，属于适应']
 triggers=[row('答案')['start']+.2,row('答案')['start']+1.55,row('迁移')['start']+.25,row('迁移')['start']+3.2]
 for i,(q,a) in enumerate(zip(questions,answers)):
  y=541+i*86;panel(im,(495,y-5,1835,y+66),fill='#f3f5ef');text(im,q,521,y+3,42,INK)
  if t>=triggers[i]:text(im,a,1170,y+3,41,ORANGE if i>=2 else BLUE)
 if t>=row('评分')['start']:text(im,'每项1分 · 满分4分',1165,907,32,BLUE,True)
 thinking=M['thinking'][0]<=t<M['thinking'][1]
 if thinking:
  shade=Image.new('RGBA',im.size,(0,0,0,0));ImageDraw.Draw(shade).rounded_rectangle((452,211,1880,947),24,fill=(28,60,76,68));im=Image.alpha_composite(im.convert('RGBA'),shade).convert('RGB');panel(im,(1040,360,1290,605));text(im,str(3-int(t-M['thinking'][0])),1165,401,136,INK,True)
 return im
def character(im,t):
 r=next((r for r in ROWS if r['start']<=t<r['end']),None);thinking=M['thinking'][0]<=t<M['thinking'][1];tail=t-row('告别')['speech_end']
 if tail>=0:pose=16 if tail<.65 else 17 if tail<1.25 else 18
 elif thinking:pose=9
 elif M['chapter2']<=t<M['chapter2']+1.1:pose=11
 else:pose=6 if r and r['mode'] in ['机制','材料','问题','答案','迁移'] else 3
 art=(POSES[pose] if pose in POSES else b.POSES[pose]).copy()
 if pose in (3,6):
  a=PCM[int(t*24000):int(t*24000)+960].astype(np.float32)/32768;rms=float(np.sqrt(np.mean(a*a))) if len(a) else 0;state=0 if rms<.011 else 1 if rms<.055 else 2 if rms<.13 else 3
  mx,my,mw,mh=b.o.m.MOUTH_CENTERS[pose];art.alpha_composite(b.MOUTHS[pose,state],(round((mx-mw/2)*390/512),round((my-mh/2)*390/512)))
 yy=round(580+1.5*math.sin(t*2));im.paste(art,(20,yy),art);b.AUDIT.append(dict(kind='character',pose=pose,box=[20,yy,410,yy+390]))
 if r:b.bubble(im,r['text'],t-r['start'],max(.1,r['speech_end']-r['start']))
 elif thinking:b.bubble(im,'想一想，再核对答案。',0,3)
def frame(t):
 global AUDIT
 AUDIT=[];b.AUDIT=[];idx=int(t>=M['chapter2']);intro=t<2 or M['chapter2']<=t<M['chapter2']+2
 im=bg() if intro else recap(t) if not idx else quiz(t)
 head=HEADS[idx];age=t-(0 if idx==0 else M['chapter2'])
 if age<2:
  q=E(age-1);scale=1.28-.28*q;art=head.resize((round(head.width*scale),round(head.height*scale)),Image.Resampling.LANCZOS);im.paste(art,(round((960-art.width/2)*(1-q)),round((450-art.height/2)*(1-q))),art)
 else:im.paste(head,(0,0),head)
 if t>=row('告别')['start']:panel(im,(1425,40,1890,114));text(im,'下期会诊 · 拉尼娜',1655,57,39,INK,True)
 character(im,t);return im
def main():
 n=math.ceil(D*24);tmp=OUT.with_name('.第十二段.pending.mp4');log=(R/'编码日志.txt').open('wb');proc=subprocess.Popen([b.FF,'-v','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(R/'配音/第十二段.wav'),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart','-shortest',str(tmp)],stdin=subprocess.PIPE,stderr=log)
 audits=[]
 for i in range(n):
  im=frame(i/24);proc.stdin.write(im.convert('RGB').tobytes());audits.append(dict(frame=i,text=AUDIT,character=b.AUDIT))
  if i%240==0:print('frame',i,'/',n,flush=True)
 proc.stdin.close();assert proc.wait()==0;log.close();b.manager.decode(tmp);tmp.replace(OUT)
 times=[5,12,19,row('材料')['start']+2,row('问题')['start']+2,M['thinking'][0]+1,row('答案')['start']+2.2,row('迁移')['start']+4.5,row('告别')['start']+1,row('告别')['speech_end']+.3,D-.2]
 sheet=Image.new('RGB',(1920,1080),'#dfe9eb')
 for j,t in enumerate(times):
  raw=subprocess.run([b.FF,'-v','error','-ss',str(t),'-i',str(OUT),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True,check=True).stdout;im=Image.open(io.BytesIO(raw));im.save(CHECK/f'{j:02d}_{t:.2f}.png');sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),((j%4)*480,(j//4)*360));ImageDraw.Draw(sheet).text(((j%4)*480+8,(j//4)*360+278),f'{t:.2f}s',font=F(25),fill=INK)
 sheet.save(CHECK/'编码抽帧总览.jpg');(CHECK/'逐帧对象边界.json').write_text(json.dumps(audits,ensure_ascii=False),encoding='utf-8')
 info=b.manager.info(OUT);(CHECK/'验证.json').write_text(json.dumps(dict(**info,resolution='1920x1080',fps=24,frames=n,decode='PASS',review_nodes=times),ensure_ascii=False,indent=2),encoding='utf-8')
 data=json.loads(b.manager.MANIFEST.read_text(encoding='utf-8'));data['segments']['12_总结与检测']=dict(path=str(OUT.relative_to(b.manager.ROOT)),**info,decode='PASS',word_shots=[26,27]);b.manager.write_manifest(data);print(str(OUT),info,flush=True)
if __name__=='__main__':main()
