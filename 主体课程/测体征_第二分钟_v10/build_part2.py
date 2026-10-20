from pathlib import Path
import sys, json, asyncio, wave, subprocess, math, inspect, re
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent
for x in ('配音','交付','.build','素材'):(ROOT/x).mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT.parent/'出入场_无制作提示_v9'))
import build_v9 as prev
b=prev.b;v=prev.v;EXE=prev.EXE
LINES=[
 ('区域','这片海域圈好了！接下来，读读它的体温。',19),
 ('距平','海温距平，就是现在的海温，减去常年同期平均海温。',3),
 ('读数','看，二零二六年七月到九月，读数一路升高：二点零九、二点五九、二点九四摄氏度。',19),
 ('平均','别急着只看最高那根！把这三个月相加，再除以三，得到二点五四摄氏度。',8),
 ('滑动','下个月，就换成八月到十月来平均。这就是三个月滑动平均。',3),
 ('持续','还要看持续时间：滑动平均至少零点五摄氏度，持续至少五个月，才能判定一次事件。',3),
 ('等级','再看强度标尺：弱、中等、强、超强。二点五摄氏度，是超强的门槛！',8),
 ('判级','七到九月平均二点五四摄氏度，已经跨过这条线。',19),
 ('历史','把它放回历史：八二、九七、一五年，都曾出现超强事件。',3),
 ('预测','这次预测峰值三点二到三点五摄氏度。注意，是预测，不能当成实测！',8),
 ('问题','咕咕嘎嘎，留个问题：只升温零点五摄氏度，为什么科学家还这么紧张？',9),
]
DATA=[];PCM=np.zeros(1);DURATION=1
async def audio():
 global DATA,PCM,DURATION
 cursor=.18;parts=[np.zeros(round(cursor*24000),dtype='<i2')]
 for i,(mode,text,pose) in enumerate(LINES):
  path=ROOT/'配音'/f'{i+1:02d}_{mode}.mp3'
  if not path.exists() or path.stat().st_size<1000:
   for attempt in range(4):
    try:
     await prev.old.edge_tts.Communicate(text,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=35).save(str(path));break
    except Exception:
     if attempt==3:raise
     await asyncio.sleep(2+attempt)
  raw=subprocess.check_output([EXE,'-v','error','-i',str(path),'-f','s16le','-ac','1','-ar','24000','-'])
  z=np.frombuffer(raw,dtype='<i2');idx=np.flatnonzero(np.abs(z.astype(np.int32))>220)
  if len(idx):z=z[max(0,idx[0]-900):min(len(z),idx[-1]+1200)]
  # Keep expressive short pauses, cut long synthesis silences inside sentences.
  quiet=np.abs(z.astype(np.int32))<150;cuts=[];start=None
  for k,val in enumerate(quiet):
   if val and start is None:start=k
   elif not val and start is not None:
    if k-start>9600:cuts.append((start+3000,k-3000))
    start=None
  if cuts:
   keep=np.ones(len(z),dtype=bool)
   for a,c in cuts:keep[a:c]=False
   z=z[keep]
  speechend=cursor+len(z)/24000
  pause=3.0 if mode=='问题' else .10
  z=np.concatenate([z,np.zeros(round(pause*24000),dtype='<i2')])
  end=cursor+len(z)/24000
  DATA.append(dict(mode=mode,text=text,pose=pose,start=cursor,speech_end=speechend,end=end))
  cursor=end;parts.append(z);print(f'Voice {i+1}/{len(LINES)} {cursor:.2f}s',flush=True)
 samples=np.concatenate(parts);PCM=samples.astype(np.float32)/32768;DURATION=len(samples)/24000;prev.PCM=PCM
 with wave.open(str(ROOT/'配音'/'第二分钟_晓伊.wav'),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(samples.tobytes())
 (ROOT/'台词与时间轴.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2),encoding='utf-8')
def poly(s,p,fill,stroke=None,width=2):s.items.append(dict(kind='polygon',points=p,fill=fill,stroke=stroke,width=width))
def circle(s,x,y,w,h,t):s.ellipse(x,y,w,h,None,b.CORAL,5+round(2*(1+math.sin(t*5))))
def dashed(s,p1,p2,color,width=4):
 x,y=p1;a,c=p2;dist=math.hypot(a-x,c-y)
 for k in range(0,round(dist),24):
  q=k/dist;r=min(k+13,dist)/dist;s.line([(x+(a-x)*q,y+(c-y)*q),(x+(a-x)*r,y+(c-y)*r)],color,width)
def bar(s,x,base,val,width,scale,q=1,color=None,outline=False):
 h=max(1,val*scale*q);top=base-h;depth=17;color=color or b.CORAL
 if outline:
  for a,c in [((x,base),(x,top)),((x,top),(x+width,top)),((x+width,top),(x+width,base))]:dashed(s,a,c,color,5)
 else:
  s.rect(x+10,base+6,width+16,13,fill='#d7ddd3',stroke=None,r=7)
  poly(s,[(x+width,top),(x+width+depth,top-depth),(x+width+depth,base-depth),(x+width,base)],'#bf654b')
  poly(s,[(x,top),(x+depth,top-depth),(x+width+depth,top-depth),(x+width,top)],'#ffd1a7')
  s.rect(x,top,width,h,fill=color,stroke='#c17860',width=2,r=5)
 return top
def panel(s,title):
 s.image(str(b.BG),0,0,1920,1080)
 s.rect(24,140,1450,890,fill=b.CREAM,stroke='#98bcc6',width=3,r=30)
 s.text('测体征 · 给海洋读“体温”',40,35,53,b.INK,w=1385)
 s.text(title,75,181,48,b.INK,w=1330)
def bubble(s,text,px,py,size,custom=False):
 # The tail follows the actual face, including positions used to point at a chart.
 width=395;x=1500;y=70;font=40
 display=text
 for a,c in [('二零二六年','2026年'),('二点零九','2.09'),('二点五九','2.59'),('二点九四','2.94'),('二点五四','2.54'),('三点二到三点五','3.2—3.5'),('二点五','2.5'),('零点五','0.5'),('摄氏度','℃')]:display=display.replace(a,c)
 tokens=[]
 for token in re.findall(r'[A-Za-zÀ-ÿ0-9]+(?:\.[0-9]+)*|.',display):
  if token in '，。？！：；、”）' and tokens:tokens[-1]+=token
  else:tokens.append(token)
 lines=[];line=''
 for token in tokens:
  if line and b.F[font].getlength(line+token)>width-40:lines.append(line);line=token
  else:line+=token
 if line:lines.append(line)
 h=len(lines)*51+40
 y=max(65,(py+30 if custom else py-25)-h)
 tip=(px+(.63 if custom else .53)*size,py+(.22 if custom else .16)*size)
 mid=x+width*.48
 poly(s,[(mid-19,y+h-2),tip,(mid+19,y+h-2)],b.CREAM,'#98bcc8',3)
 s.rect(x,y,width,h,fill=b.CREAM,stroke='#98bcc8',width=3,r=25);s.rect(mid-15,y+h-5,30,8,fill=b.CREAM,stroke=None,r=0)
 for j,line in enumerate(lines):s.text(line,x+20,y+20+j*51,font,b.INK,'justify' if j<len(lines)-1 else 'left',width-40)
def scene(t):
 row=next((r for r in DATA if r['start']<=t<r['end']),DATA[-1] if t>=DATA[-1]['end'] else DATA[0]);mode=row['mode'];age=max(0,t-row['start']);s=b.Scene()
 px,py,size,pose,custom=1510,660,390,3 if row['pose']==19 else row['pose'],False
 reposition=None
 if mode=='区域':
  # Match the preceding chapter's last NOAA map composition.
  s.rect(0,0,1920,1080,fill='#eef9fa',stroke=None,r=0)
  s.text('定位Niño3.4区',40,38,55,b.INK,w=1390)
  scale=1850/prev.MW;tx=35+458*scale;ty=245+113*scale;zoom=1.08
  mx=tx-458*scale*zoom;my=ty-113*scale*zoom
  s.image(str(prev.MAP),mx,my,prev.MW*scale*zoom,prev.MH*scale*zoom)
  s.rect(mx+280*scale*zoom,my+95*scale*zoom,178*scale*zoom,37*scale*zoom,fill=None,stroke=b.CORAL,width=6,r=2)
  s.text('170°W—120°W  ·  5°N—5°S',40,939,44,b.INK,'center',1410)
  size=500;px=tx-55/1254*size;py=ty-100/1254*size;custom=True
 elif mode=='距平':
  panel(s,'不是海水有多热，而是比常年暖多少')
  for x,txt,col in [(92,'现在的海温',b.CORAL),(807,'常年同期平均海温',b.BLUE)]:
   s.rect(x,370,595,210,fill='#ffedd5' if x==92 else '#e2f0f1',stroke='#9ebfc4',r=25)
   s.text(txt,x+20,427,46,col,'center',555)
  s.text('−',695,411,70,b.INK,'center',110)
  s.text('海温距平 = 现在 − 常年同期',110,669,55,b.CORAL,'center',1270)
  s.text('正值：偏暖     负值：偏冷',110,839,46,b.BLUE,'center',1270)
 elif mode in ('读数','平均','滑动'):
  panel(s,'2026年7—9月 · Niño3.4海温距平')
  base=864;scale=150
  for val in (0,1,2,3):
   y=base-val*scale;s.line([(180,y),(1260,y)],'#d8e2df',2);s.text(f'{val:.0f}',95,y-24,32,b.INK,'right',64)
  s.text('℃',93,300,34,b.INK,w=80)
  rs=next(r['start'] for r in DATA if r['mode']=='读数')
  vals=[2.09,2.59,2.94];xs=[290,645,1000]
  selected=min(2,int(max(0,t-rs)/(max(.1,next(r['end'] for r in DATA if r['mode']=='读数')-rs)/3)))
  for j,(x,val) in enumerate(zip(xs,vals)):
   q=b.ease((t-rs-j*1.1)/1.0) if mode=='读数' else 1
   top=bar(s,x,base,val,125,scale,q,color=b.CORAL if mode!='读数' or j==selected else '#87b9c7')
   if q>.05:s.text(f'+{val:.2f}',x-42,top-74,43,b.CORAL if j==selected else b.INK,'center',210)
   s.text(f'{j+7}月',x-25,900,39,b.INK,'center',175)
   if mode=='读数' and j==selected and q>.9:circle(s,x-40,top-77,212,60,t)
  if mode=='平均':
   y=base-2.54*scale;s.line([(194,y),(1260,y)],b.BLUE,5)
   s.rect(190,267,1160,85,fill='#e1eff1',stroke=None,r=20)
   s.text('(2.09 + 2.59 + 2.94) ÷ 3 = 2.54℃',210,278,44,b.BLUE,'center',1120)
  elif mode=='滑动':
   s.rect(165,272,1160,80,fill='#e1eff1',stroke=None,r=20)
   s.text('7—9月 → 8—10月 → 9—11月',180,282,43,b.BLUE,'center',1130)
  if mode=='读数':
   # Move the teacher close to September's value after the first two bars have been read.
   if selected==2:
    size=430;px=1185;py=430;custom=True
    third=rs+(next(r['end'] for r in DATA if r['mode']=='读数')-rs)*2/3
    if t-third<.65:
     q=b.ease((t-third)/.65);reposition=(1510+(1185-1510)*q,660+(430-660)*q)
    tipx=px+55/1254*size;tipy=py+100/1254*size
    s.arrow([(tipx,tipy),(1170,tipy),(1119,base-2.94*scale)],b.CORAL,5)
 elif mode=='持续':
  panel(s,'先确认事件，再讨论强弱')
  s.text('三个月滑动平均达到 +0.5℃',90,360,58,b.CORAL,'center',1305)
  s.text('持续至少5个月',90,513,55,b.BLUE,'center',1305)
  for j in range(5):
   x=150+j*240;q=b.ease((age-j*.45)/.45)
   s.rect(x,680,180,130,fill='#ffedc8' if q>.5 else '#e5f0ef',stroke='#99bec6',r=23)
   s.text(str(j+1),x,705,58,b.CORAL if q>.5 else b.SOFT,'center',180)
  s.text('区域 + 距平 + 持续时间',100,900,42,b.INK,'center',1290)
 elif mode in ('等级','判级'):
  panel(s,'强度看事件峰值：四级标尺')
  colors=['#91c7c6','#71b0c3','#f0b078','#e78b6b']
  for j,(name,ran) in enumerate(zip(['弱','中等','强','超强'],['0.5至不足1.3','1.3至不足2.0','2.0至不足2.5','2.5℃及以上'])):
   x=90+j*330;s.rect(x,390,306,250,fill=colors[j],stroke=None,r=24)
   s.text(name,x,428,58,b.INK,'center',306);s.text(ran,x+10,553,33,b.INK,'center',286)
  if mode=='判级':
   circle(s,1070,375,310,280,t)
   s.text('7—9月平均：2.54℃',90,732,57,b.CORAL,'center',1315)
   s.text('超过2.5℃门槛 → 超强',90,868,48,b.INK,'center',1315)
   custom=True;size=410;px=1370;py=500
  else:s.text('单位：℃     门槛：0.5 / 1.3 / 2.0 / 2.5',110,823,43,b.BLUE,'center',1260)
 elif mode in ('历史','预测'):
  panel(s,'历史峰值对照 · 本次预测单独表示')
  base=852;scale=125
  for val in (0,1,2,3,4):
   y=base-val*scale;s.line([(140,y),(1330,y)],'#d9e4df',2);s.text(str(val),62,y-23,32,b.INK,'right',60)
  vals=[2.7,2.7,2.8];labs=['1982/83','1997/98','2015/16']
  histstart=next(r['start'] for r in DATA if r['mode']=='历史')
  for j,val in enumerate(vals):
   x=230+j*268;q=b.ease((t-histstart-j*.40)/.8);top=bar(s,x,base,val,114,scale,q,color='#76b1c5')
   if q>.1:s.text(f'{val:.1f}℃',x-32,top-63,40,b.INK,'center',180)
   s.text(labs[j],x-45,890,34,b.INK,'center',200)
  if mode=='预测':
   x=1050;q=b.ease(age/1.0);bar(s,x,base,3.5,114,scale,q,outline=True)
   if q>.6:
    s.line([(x,base-3.2*scale),(x+114,base-3.2*scale)],b.CORAL,5)
    s.text('3.2—3.5℃',960,331,42,b.CORAL,'center',290);circle(s,968,323,288,63,t)
   s.text('2026/27',1005,890,34,b.INK,'center',200)
  s.text('实测历史峰值',150,960,31,b.BLUE,w=350)
  s.text('国家气候中心 · 9月29日预测',625,960,30,b.CORAL,w=760)
 elif mode=='问题':
  panel(s,'想一想：小温差，为什么值得关注？')
  s.text('+0.5℃',90,390,92,b.CORAL,'center',1305)
  s.text('“只暖了一点点”，真的没关系吗？',90,605,51,b.INK,'center',1305)
  s.text('海洋水量很大 · 从热量角度想一想',90,759,40,b.BLUE,'center',1305)
  if t>=row['speech_end']:
   left=max(1,math.ceil(row['end']-t));s.ellipse(637,864,105,105,'#e1efee','#aac6c7',3);s.text(str(left),637,869,62,b.BLUE,'center',105)
 # Small walking transitions: exit at the edge and re-enter on the same side.
 moving=False
 if reposition is not None:
  moving=True;wx,wy=reposition
  prev.presenter(s,13 if int(t/.16)%2==0 else 14,wx,wy,410,t)
 elif mode=='距平' and age<1.0:
  moving=True
  if age<.45:prev.presenter(s,13 if int(age/.15)%2==0 else 14,1430+600*b.ease(age/.45),650,410,t)
  else:prev.presenter(s,13 if int(age/.15)%2==0 else 14,1920-410*b.ease((age-.45)/.55),650,410,t)
 else:
  prev.presenter(s,19 if custom else pose,px,py+math.sin(t*1.7)*2,size,t,custom)
 if not moving and (mode!='问题' or t<row['speech_end']):bubble(s,row['text'],px,py,size,custom)
 s.rect(0,1075,1920,5,fill='#d6e7e5',stroke=None,r=0);s.rect(0,1075,1920*t/DURATION,5,fill=b.BLUE,stroke=None,r=0)
 return s
source=inspect.getsource(v.render).replace("fw=b.F[a['size']].getlength(line)","fw=b.F[a['size']].getlength(line);y+=b.F[a['size']].getmetrics()[0]").replace("anchor='lt'","anchor='ls'")
source=source.replace("if t<.18:return Image.new('RGB',(W,H),'black')","if False:return im").replace("if t<.53:im=Image.blend","if False:im=Image.blend")
env=dict(v.__dict__);env['scene']=scene;exec(source,env);render=env['render']
def main():
 asyncio.run(audio())
 for mode in ('区域','距平','读数','平均','持续','等级','判级','历史','预测','问题'):
  row=next(r for r in DATA if r['mode']==mode);t=row['start']+max(1.1,(row['speech_end']-row['start'])*.72)
  render(t).save(ROOT/f'预览_{mode}.png')
 (ROOT/'素材说明.md').write_text('''依据最新批注版第二幕镜头05—08，承接v9定位图，保留原有知识顺序。当前切片以互动问题结束，能量观答案将在下一片开头接续。
地图沿用NOAA PSL原图：https://psl.noaa.gov/data/timeseries/month/Nino34_CPC/ 。仅透明高亮，不自绘地理底图。
2026年7/8/9月距平2.09/2.59/2.94℃，平均2.54℃。9月和平均值来自国家气候中心10月9日通报：https://e.weather.com.cn/news/2026/10/4815391.shtml 。8月=2.94−0.35=2.59；7月由3×2.54−2.59−2.94=2.09复核，原始参赛文档也列明此值，四舍五入一致。
国内四级阈值和持续判据、历史峰值采用中国气象报社2026年5月15日稿《科普看台丨海气联动的奥秘：厄尔尼诺如何影响全球气候？》https://www.zgqxb.com.cn/zx/yw/hyxw/202605/t20260515_7793558.html 。历史三次2.7/2.7/2.8℃沿用此国内口径，不混用NOAA ONI值。
2026年峰值预测更新为国家气候中心9月29日发布3.2—3.5℃，替代原稿未经确认的WMO3.7℃：https://cnr.weather.com.cn/news/2026/09/4806926.shtml 。虚线空心柱标注预测，不将预报当作实测。
当前只有7—9月三个月值，不虚构其他月份或一整条滑动平均序列；平均值用水平线与计算式展现，滚动窗口单独演示。判别持续5个月以时间条件示意展现，不捏造5个月读数。
图表侧面17px增强层次，柱体正面高度按数据线性绘制。字体得意黑，晓伊+5%配音，自动缩短长静音，音量驱动口型。制作与资料说明留在本文件。
''',encoding='utf-8')
 if '--preview' in sys.argv:print(f'PREVIEW {DURATION:.2f}s',flush=True);return
 out=ROOT/'交付'/'海洋发烧了_第二分钟_测体征_v10.mp4'
 cmd=[EXE,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(ROOT/'配音'/'第二分钟_晓伊.wav'),'-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)]
 with open(ROOT/'.build'/'render.log','w') as log:
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for n in range(math.ceil(DURATION*24)):
   p.stdin.write(render(n/24).tobytes())
   if n%240==0:print(f'Render {n/24:.0f}/{DURATION:.2f}',flush=True)
  p.stdin.close();assert p.wait()==0
 check=subprocess.run([EXE,'-v','error','-i',str(out),'-f','null','-'],capture_output=True);assert check.returncode==0,check.stderr
 # Append to the already verified opening and first minute.
 first=ROOT.parent/'出入场_无制作提示_v9'/'交付'/'海洋发烧了_最新批注落实_出入场_v9.mp4'
 joined=ROOT/'交付'/'海洋发烧了_开场与前两段_v10.mp4'
 graph='[0:v]setsar=1,setpts=PTS-STARTPTS[v0];[1:v]setsar=1,setpts=PTS-STARTPTS[v1];[0:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a0];[1:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]'
 with open(ROOT/'.build'/'join.log','w') as log:subprocess.run([EXE,'-y','-i',str(first),'-i',str(out),'-filter_complex',graph,'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','19','-c:a','aac','-b:a','160k','-movflags','+faststart',str(joined)],stdout=log,stderr=log,check=True)
 check=subprocess.run([EXE,'-v','error','-i',str(joined),'-f','null','-'],capture_output=True);assert check.returncode==0,check.stderr
 (ROOT/'验证.json').write_text(json.dumps(dict(decode='PASS',seconds=DURATION,resolution=[1920,1080],fps=24,monthly=[2.09,2.59,2.94],mean=2.54,forecast=[3.2,3.5],bubble_hidden_during_walk=True,output=str(out),joined=str(joined)),ensure_ascii=False,indent=2),encoding='utf-8')
 print(joined,flush=True)
if __name__=='__main__':main()
