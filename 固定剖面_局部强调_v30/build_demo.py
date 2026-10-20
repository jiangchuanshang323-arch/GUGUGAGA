from pathlib import Path
import sys, importlib.util, math, json, wave, subprocess, hashlib, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
for folder in ('交付','.build','检查'): (ROOT/folder).mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('art28',PROJECT/'精绘厄尔尼诺_讲解演示_v28'/'build_demo.py')
v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
PHASES=json.loads((PROJECT/'逐句引导_箭头修正_v29'/'逐句引导时间轴.json').read_text(encoding='utf-8'))
AUDIO=PROJECT/'精绘厄尔尼诺_讲解演示_v28'/'配音'/'精绘演示_晓伊.wav'
with wave.open(str(AUDIO),'rb') as wav: DURATION=wav.getnframes()/wav.getframerate()
FPS=24; COUNT=math.ceil(DURATION*FPS)
FONT={s:ImageFont.truetype(str(v.FONT),s) for s in range(28,69)}
INK=v.INK; CREAM=v.CREAM; BLUE=v.BLUE; CORAL=v.CORAL
FOCUS=['信风','高空回流','西侧暖水','上升气流','冷水上涌','下沉气流','信风','暖水东移','温跃层','冷水上涌','中东部增暖','降雨区','沃克环流','东西温差','信风','正反馈']
BASE=Image.new('RGB',(1920,1080),CREAM)
BASE.paste(v.gradient((1792,448),(245,251,250),(220,239,243)),(64,172))
dd=ImageDraw.Draw(BASE); dd.rounded_rectangle((60,166,1860,926),28,outline='#b9d1d6',width=2)
paper=np.random.default_rng(30).integers(-1,2,(1080,1920,1),dtype=np.int16)
BASE=Image.fromarray(np.clip(np.asarray(BASE).astype(np.int16)+paper,0,255).astype('uint8'))
WARM=v.gradient((1760,300),(255,227,191),(240,182,149))
COLD=v.gradient((1760,300),(166,210,221),(89,151,183))
CLOUD=v.CLOUD.resize((318,190),Image.Resampling.LANCZOS)

def smooth(q):
 q=max(0,min(1,q)); return q*q*q*(q*(q*6-15)+10)
def ramp(t,start,end): return smooth((t-start)/max(.001,end-start))
def stage(t): return next((p for p in reversed(PHASES) if t>=p['start']),PHASES[0])
def introduced(t,index): return ramp(t,PHASES[index]['start'],PHASES[index]['start']+.3)
def blend(a,b,q): return tuple(round(x+(y-x)*q) for x,y in zip(a,b))
def overlap(a,b,pad=0): return a[0]<b[2]+pad and b[0]<a[2]+pad and a[1]<b[3]+pad and b[1]<a[3]+pad
def arrow(im,points,color,width=9,alpha=1):
 if alpha<=.001:return None
 # The shaft ends inside the triangular head, never at/beyond its tip.
 r=width*2.5; lengths=[math.dist(a,b) for a,b in zip(points,points[1:])]
 remain=max(0,sum(lengths)-r*.82); shaft=[points[0]]
 for a,b,length in zip(points,points[1:],lengths):
  if remain>=length:shaft.append(b);remain-=length
  else:
   q=remain/max(.001,length);shaft.append((a[0]+q*(b[0]-a[0]),a[1]+q*(b[1]-a[1])));break
 tip=points[-1]; angle=math.atan2(tip[1]-shaft[-1][1],tip[0]-shaft[-1][0])
 tri=[tip,(tip[0]-r*math.cos(angle-.45),tip[1]-r*math.sin(angle-.45)),(tip[0]-r*math.cos(angle+.45),tip[1]-r*math.sin(angle+.45))]
 extent=points+tri; margin=width+3
 left=math.floor(min(p[0] for p in extent)-margin);top=math.floor(min(p[1] for p in extent)-margin)
 ww=math.ceil(max(p[0] for p in extent)+margin)-left;hh=math.ceil(max(p[1] for p in extent)+margin)-top
 art=Image.new('RGBA',(ww*2,hh*2));d=ImageDraw.Draw(art);cv=lambda p:((p[0]-left)*2,(p[1]-top)*2)
 d.line([cv(p) for p in shaft],fill=color,width=width*2,joint='curve');d.polygon([cv(p) for p in tri],fill=color)
 art=art.resize((ww,hh),Image.Resampling.LANCZOS)
 art.putalpha(art.getchannel('A').point(lambda a:round(a*alpha)))
 im.paste(art,(left,top),art)
 return [min(p[0] for p in extent)-width/2,min(p[1] for p in extent)-width/2,max(p[0] for p in extent)+width/2,max(p[1] for p in extent)+width/2]

def render(t):
 p=stage(t);idx=p['id']; age=t-p['start']; remaining=p['end']-t
 strength=min(smooth(age/.22),smooth(remaining/.22))
 wind=ramp(t,PHASES[6]['start'],PHASES[6]['end'])
 east=ramp(t,PHASES[7]['start'],PHASES[7]['end'])
 deep=ramp(t,PHASES[8]['start'],PHASES[8]['end'])
 suppress=ramp(t,PHASES[9]['start'],PHASES[9]['end'])
 air=ramp(t,PHASES[11]['start'],PHASES[11]['end'])
 walker=ramp(t,PHASES[12]['start'],PHASES[12]['end'])
 feedback=ramp(t,PHASES[14]['start'],PHASES[14]['end'])
 cx=460+650*air; windtip=485+565*wind+90*feedback
 im=BASE.copy();d=ImageDraw.Draw(im);labels=[];objects=[]
 def txt(words,x,y,size=40,color=INK,center=False):
  font=FONT[size];xx=x-font.getlength(words)/2 if center else x
  d.text((xx,y+font.getmetrics()[0]),words,font=font,fill=color,anchor='ls')
 def label(key,words,x,y,w,h=58,size=36,color=INK,opacity=1):
  if opacity<=.001:return
  # No parent transforms or clipping. Every label uses the same 12px text inset.
  art=Image.new('RGBA',(w,h));ad=ImageDraw.Draw(art)
  ad.rounded_rectangle((0,0,w-1,h-1),17,fill=CREAM,outline='#bdd1d5',width=1)
  font=FONT[size];box=font.getbbox(words);tw=box[2]-box[0];th=box[3]-box[1]
  assert tw<=w-24 and th<=h-12,(key,words,tw,w)
  tx=(w-tw)/2-box[0];ty=(h-th)/2-box[1]
  ad.text((tx,ty),words,font=font,fill=color)
  art.putalpha(art.getchannel('A').point(lambda a:round(a*opacity)))
  im.paste(art,(x,y),art)
  labels.append({'id':key,'text':words,'rect':[x,y,x+w,y+h],'ink':[x+(w-tw)/2,y+(h-th)/2,x+(w+tw)/2,y+(h+th)/2],'opacity':opacity})
 def ar(key,pts,color,width=9,opacity=1):
  focus=(FOCUS[idx]==key or (idx==12 and key in ('高空回流','上升气流','下沉气流')))
  alpha=opacity*(.64+.36*strength if focus else .56)
  bbox=arrow(im,pts,color,width,alpha)
  if bbox:objects.append({'id':key,'rect':bbox})
 txt('厄尔尼诺现象',76,22,61)
 txt('太平洋东西向剖面',78,100,33,BLUE)
 label('状态','正常状态' if t<PHASES[6]['start'] else '变化过程' if t<PHASES[10]['start'] else '厄尔尼诺状态',1430,36,412,66,42)
 label('西侧','西太平洋 · 印尼一侧',92,178,540,60,40)
 label('东侧','东太平洋 · 秘鲁一侧',1290,178,540,60,40)
 # Fixed layered cross-section: surface at620, base920. Only the thermocline morphs.
 xs=np.arange(1760);q=xs/1759
 normal=200-150*smooth_array(q)
 # Warm-water redistribution begins first; eastern deepening follows its own clause.
 depths=normal-55*east*(1-q)+50*east*q+45*deep*q
 depths+=3*np.sin(xs/135)+1.8*np.sin(xs/59)
 mask=Image.new('L',(1760,300));md=ImageDraw.Draw(mask)
 pts=[(int(x),float(y)) for x,y in zip(xs[::3],depths[::3])]+[(1759,float(depths[-1]))]
 md.polygon([(0,0),(1759,0)]+pts[::-1],fill=255)
 sea=COLD.copy();sea.paste(WARM,(0,0),mask)
 if idx in (2,7,10,13):
  # One gentle water tint, with no extra circle, glowing arrow or camera movement.
  hot=Image.new('RGB',sea.size,(255,218,177));am=np.asarray(mask,dtype=np.float32)/255
  local=(1-q if idx==2 else q if idx in (7,10) else np.ones_like(q))
  a=(am*local[None,:]*strength*.15)[:,:,None]
  sea=Image.fromarray(np.clip(np.asarray(sea)*(1-a)+np.asarray(hot)*a,0,255).astype('uint8'))
 im.paste(sea,(80,620));d=ImageDraw.Draw(im)
 boundary=[(80+x,620+y) for x,y in pts]
 d.line(boundary,fill='#fff3dc',width=4,joint='curve')
 if idx==8 and strength>.001:
  d.line(boundary[len(boundary)//2:],fill=blend((255,243,220),(191,131,76),strength),width=5,joint='curve')
 d.line((80,620,1840,620),fill='#93bccb',width=3)
 d.line((80,920,1840,920),fill='#6193aa',width=2)
 # The scientific arrows are local and have fixed safe lanes.
 ar('信风',[(1490,525),(windtip,525)],CORAL,10)
 ar('高空回流',[(cx+25,274),(1510,274)],v.GOLD,9,introduced(t,1)*(1-.35*walker))
 ar('上升气流',v.cubic((cx,503),(cx-145,486),(cx-156,330),(cx,274),40),CORAL,8,introduced(t,3)*(1-.25*walker))
 ar('下沉气流',v.cubic((1530,312),(1560,370),(1540,452),(1530,502),30),BLUE,8,introduced(t,5)*(1-.40*walker))
 if air>.001: ar('西侧下沉',[(350,318),(350,495)],BLUE,7,air*.7)
 up_end=679+144*suppress
 ar('冷水上涌',[(1670,890),(1670,up_end)],BLUE,9,introduced(t,4)*(1-.5*suppress))
 # An eastward water arrow is only needed while teaching that specific motion.
 if introduced(t,8)>.001:
  d=ImageDraw.Draw(im)
  target=620+float(depths[850])
  d.line((930,838,930,target+7),fill='#638fa4',width=2)
  d.ellipse((926,target-4,934,target+4),fill='#638fa4')
 # Clouds only move horizontally and remain above the wind lane; no camera-follow.
 cloud_alpha=introduced(t,3)
 if cloud_alpha>.001:
  cl=CLOUD.copy();cl.putalpha(cl.getchannel('A').point(lambda a:round(a*cloud_alpha)))
  pos=(round(cx-159),285);im.paste(cl,pos,cl)
  b=CLOUD.getchannel('A').getbbox();objects.append({'id':'降雨云','rect':[b[0]+pos[0],b[1]+pos[1],b[2]+pos[0],b[3]+pos[1]]})
  rain=Image.new('RGBA',(230,30));rd=ImageDraw.Draw(rain)
  for j in (-3,-2,-1,1,2,3):
   x=115+j*28;rd.line((x,4,x-5,21),fill='#91b8c9',width=3)
  rain.putalpha(rain.getchannel('A').point(lambda a:round(a*cloud_alpha)))
  im.paste(rain,(round(cx-115),457),rain)
 # Draw labels AFTER all objects, in reserved non-intersecting lanes.
 label('高空','高空回流：西 → 东',678,178,574,60,38,v.GOLD,introduced(t,1))
 label('信风','近海面东风信风：西 ← 东' if wind<.999 else '东风信风减弱：西 ← 东',586,550,775,56,38,CORAL)
 label('暖水','西侧暖水较厚' if east<.999 else '暖水向东扩展',123,644,360,58,36,CORAL,introduced(t,2))
 label('上升','空气上升' if air<.5 else '空气下沉',84,379,210,58,36,CORAL if air<.5 else BLUE,introduced(t,3))
 label('下沉','空气下沉',1595,379,210,58,36,BLUE,introduced(t,5))
 label('中部上升','空气上升',1300,379,210,58,36,CORAL,smooth((air-.65)/.25))
 label('冷水','深层冷水',250,850,300,58,36,BLUE,introduced(t,4))
 label('上涌','冷水上涌' if suppress<.999 else '冷水上涌受抑',1190,850,380,58,36,BLUE,introduced(t,4))
 label('温跃层','温跃层',788,850,284,58,38,INK,introduced(t,8))
 if idx==8:label('加深','东部温跃层加深',1100,432,410,58,38,CORAL,min(introduced(t,8),smooth(remaining/.2)))
 if idx>=11:label('雨区','降雨区东移',1050,104,340,58,36,BLUE,introduced(t,11))
 if idx>=12:label('沃克','沃克环流减弱',573,346,350,58,36,INK,introduced(t,12))
 if idx==13:label('温差','东西海温差缩小',1180,650,530,58,38,CORAL,min(introduced(t,13),smooth(remaining/.2)))
 if idx==15:
  # A single unobtrusive concept ribbon connects water and air; no extra moving motifs.
  label('反馈','海洋与大气：正反馈',570,650,700,58,40,INK,introduced(t,15))
 d=ImageDraw.Draw(im);d.rectangle((0,958,1920,1080),fill='#244b60')
 words=p['text'];chunks=[];chunk=''
 for ch in words:
  if FONT[46].getlength(chunk+ch)>1760:chunks.append(chunk);chunk=ch
  else:chunk+=ch
 if chunk:chunks.append(chunk)
 y=963 if len(chunks)>1 else 986
 subrects=[]
 for line in chunks:
  txt(line,960,y,46,'#fffaf0',True)
  x=960-FONT[46].getlength(line)/2
  b=FONT[46].getbbox(line,anchor='ls');base=y+FONT[46].getmetrics()[0]
  subrects.append([x+b[0],base+b[1],x+b[2],base+b[3]]);y+=49
 meta={'frame':round(t*FPS),'time':t,'phase':idx,'focus':FOCUS[idx] if strength>.001 else None,'emphasis_count':int(strength>.001),'camera':[0,0,1920,1080],
       'labels':labels,'objects':objects,'boundary':boundary,'geometry':{'cloud_x':cx,'wind_tip':windtip,'thermocline_west':float(depths[0]),'thermocline_east':float(depths[-1]),'upwell_tip':up_end},'subtitle_lines':chunks,'subtitle_rects':subrects}
 return im,meta

def smooth_array(q): return q*q*q*(q*(q*6-15)+10)

def validate(meta,prev):
 errors=[]
 for label in meta['labels']:
  x,y,z,b=label['rect']
  if not(60<=x<z<=1860 and 18<=y<b<=926):errors.append('label_outside:'+label['id'])
  ix,iy,iz,ib=label['ink']
  if not(x+11<=ix<iz<=z-11 and y+5<=iy<ib<=b-5):errors.append('ink_clipped:'+label['id'])
 for i,a in enumerate(meta['labels']):
  for b in meta['labels'][i+1:]:
   if overlap(a['rect'],b['rect'],4):errors.append('label_overlap:'+a['id']+'/'+b['id'])
  for o in meta['objects']:
   if overlap(a['rect'],o['rect'],4):errors.append('label_object_overlap:'+a['id']+'/'+o['id'])
  x,y,z,b=a['rect']
  if any(x-4<=px<=z+4 and y-4<=py<=b+4 for px,py in meta['boundary']):errors.append('label_thermocline_overlap:'+a['id'])
 for o in meta['objects']:
  x,y,z,b=o['rect']
  if not(64<=x<=z<=1856 and 242<=y<=b<=924):errors.append('object_outside:'+o['id'])
 if meta['emphasis_count']>1:errors.append('multiple_focus')
 if meta['camera']!=[0,0,1920,1080]:errors.append('camera_moved')
 for x,y,z,b in meta['subtitle_rects']:
  if not(64<=x<z<=1856 and 964<=y<b<=1068):errors.append('subtitle_outside')
 if prev:
  for key,value in meta['geometry'].items():
   if abs(value-prev['geometry'][key])>35:errors.append('abrupt_motion:'+key)
 return errors

def main():
 if '--preview' in sys.argv:
  times=[12,14,15.5,19.9,24,28,29,34,36]
  for t in times:im,meta=render(t);im.save(ROOT/'检查'/f'预览_{t:04.1f}.png');print(t,validate(meta,None),flush=True)
  contact(times,'预览联系表.jpg');return
 output=ROOT/'交付'/'厄尔尼诺_固定剖面逐句讲解_v30.mp4'
 if '--qa-only' in sys.argv:
  audit=[json.loads(line) for line in (ROOT/'检查'/'逐帧几何检查.jsonl').read_text(encoding='utf-8').splitlines()]
  failures=[{'frame':m['frame'],'time':m['time'],'errors':m['errors']} for m in audit if m['errors']]
  finalize(output,audit,failures);return
 cmd=[v.EXE,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',str(FPS),'-i','-','-i',str(AUDIO),'-map','0:v','-map','1:a','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-vf','setsar=1','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(output)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 audit=[];failures=[];prev=None
 with (ROOT/'检查'/'逐帧几何检查.jsonl').open('w',encoding='utf-8') as log:
  for n in range(COUNT):
   im,meta=render(n/FPS);errors=validate(meta,prev);meta['errors']=errors
   log.write(json.dumps(meta,ensure_ascii=False)+'\n');audit.append(meta)
   if errors:failures.append({'frame':n,'time':n/FPS,'errors':errors})
   proc.stdin.write(im.tobytes());prev=meta
   if n%120==0:print(f'Render {n}/{COUNT}; geometry errors={len(failures)}',flush=True)
 proc.stdin.close();err=proc.stderr.read();code=proc.wait()
 if code:raise RuntimeError(err.decode(errors='replace'))
 finalize(output,audit,failures)

def finalize(output,audit,failures):
 result=subprocess.run([v.EXE,'-v','error','-i',str(output),'-progress','pipe:1','-nostats','-f','null','-'],capture_output=True)
 assert result.returncode==0 and not result.stderr,result.stderr
 decoded=int(re.findall(rb'frame=(\d+)',result.stdout)[-1]);assert decoded in (COUNT,COUNT-1)
 old_video=PROJECT/'逐句引导_箭头修正_v29'/'交付'/'厄尔尼诺_逐句出现圈选推近_demo_v29.mp4'
 old_decode=subprocess.run([v.EXE,'-v','error','-i',str(old_video),'-progress','pipe:1','-nostats','-f','null','-'],capture_output=True)
 old_count=int(re.findall(rb'frame=(\d+)',old_decode.stdout)[-1]);assert decoded==old_count
 def duration_of(path):
  info=subprocess.run([v.EXE,'-hide_banner','-i',str(path)],capture_output=True).stderr.decode(errors='replace')
  match=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',info)
  h,m,s=map(float,match.groups());return h*3600+m*60+s
 old_duration=duration_of(old_video);new_duration=duration_of(output)
 assert abs(old_duration-new_duration)<=1/FPS
 for name,start,end in [('云团_12至16秒',12,16),('温跃层_19至25秒',19,25),('云雨信风_28至35秒',28,35)]:
  contact(np.linspace(start,end,12).tolist(),name+'.jpg')
 contact([.5,7,11.5,13.5,14.5,15.9,17.4,18.7,20.1,21.8,24.5,28.1,29.8,31.4,32.9,35.5],'全片关键节点.jpg')
 report={'video':str(output),'resolution':[1920,1080],'fps':FPS,'frames_checked':len(audit),'decoded_frames':decoded,'old_decoded_frames':old_count,'old_video_duration':old_duration,'new_video_duration':new_duration,'audio_duration':DURATION,'source_audio_sha256':hashlib.sha256(AUDIO.read_bytes()).hexdigest(),
 'audio_reused':True,'subtitles_equal_v29':True,'camera_fixed':True,'circles':0,'max_primary_emphasis':max(m['emphasis_count'] for m in audit),'decode':'PASS','geometry_failures':failures,
 'checks':['每帧标签安全区与文字内边距','每帧标签相互避让','每帧标签与箭头云朵及温跃层边界避让','每帧字幕安全区','每帧对象边界','每帧连续参数位移','每帧固定镜头及单主强调','输出解码帧数及新旧视频时长'],
 'visual_review':'待检查三组时间段联系表及全片关键节点','limit':'几何检测使用对象包围盒，逐帧自动检查并不等于逐帧人工观看。科学水层是定性剖面，未使用真实深度比例。'}
 (ROOT/'检查'/'质量检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'output':str(output),'checked':COUNT,'failures':len(failures),'decode':'PASS'},ensure_ascii=False),flush=True)
 if failures:raise RuntimeError('Geometry audit failed; inspect quality report')

def contact(times,name):
 cols=4;rows=math.ceil(len(times)/cols);sheet=Image.new('RGB',(cols*480,rows*290),'#e5ecee')
 sd=ImageDraw.Draw(sheet)
 for i,t in enumerate(times):
  im,_=render(t);x=(i%cols)*480;y=(i//cols)*290
  sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),(x,y));sd.text((x+8,y+273),f'{t:.2f}s',fill=INK)
 sheet.save(ROOT/'检查'/name,quality=93)

if __name__=='__main__':main()
