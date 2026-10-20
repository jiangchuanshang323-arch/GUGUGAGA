from pathlib import Path
import sys,json,math,asyncio,wave,subprocess,inspect,re
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
for name in ('素材','配音','.build','交付'):(ROOT/name).mkdir(exist_ok=True)
V15=ROOT.parent/'小温差大热量_正常环流_v15'
sys.path.insert(0,str(V15));import build_part3 as old
p=old.p;b=old.b;EXE=old.EXE
DATA=json.loads((V15/'台词与时间轴.json').read_text(encoding='utf-8'))
with wave.open(str(V15/'配音'/'第三段_晓伊.wav'),'rb') as w:ORIGINAL=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
POSE=ROOT/'素材'/'25_肚兜取卷轴.png';TAKE=Image.open(POSE).convert('RGBA')
assert TAKE.getextrema()[-1][0]==0
MAP=ROOT/'素材'/'NOAA正常态_图解内容.png'
# Camera crop removes the original English page heading and external footer, never redraws scientific elements.
Image.open(old.MAP).crop((0,34,620,403)).save(MAP)
BRIDGE_START=BRIDGE_END=DURATION=0;PCM=None;OLD_BOARD=None;POSTER=None
NEW_TEXT='测完体征，咕咕嘎嘎，拿出卷轴，咱们查病因！'
async def audio():
 global DATA,PCM,DURATION,BRIDGE_START,BRIDGE_END
 mp3=ROOT/'配音'/'04_卷轴转场.mp3'
 if not mp3.exists():
  for attempt in range(4):
   try:
    await p.prev.old.edge_tts.Communicate(NEW_TEXT,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=35).save(str(mp3));break
   except Exception:
    if attempt==3:raise
    await asyncio.sleep(2+attempt)
 raw=subprocess.check_output([EXE,'-v','error','-i',str(mp3),'-f','s16le','-ar','24000','-ac','1','-'])
 samples=np.frombuffer(raw,dtype='<i2');idx=np.flatnonzero(np.abs(samples.astype(np.int32))>220)
 samples=samples[max(0,idx[0]-900):min(len(samples),idx[-1]+1200)]
 row=next(r for r in DATA if r['mode']=='过渡');a=round(row['start']*24000);z=round(row['speech_end']*24000)
 joined=np.concatenate([ORIGINAL[:a],samples,ORIGINAL[z:]])
 delta=len(samples)/24000-(row['speech_end']-row['start'])
 row['text']=NEW_TEXT;row['speech_end']+=delta;row['end']+=delta
 for r in DATA:
  if r['start']>=z/24000-1e-5 and r is not row:
   for key in ('start','speech_end','end'):r[key]+=delta
 PCM=joined;DURATION=len(joined)/24000;BRIDGE_START=row['speech_end'];BRIDGE_END=row['end']
 p.DATA=DATA;p.DURATION=DURATION;p.prev.PCM=PCM.astype(np.float32)/32768
 old.BRIDGE_START=BRIDGE_START;old.BRIDGE_END=BRIDGE_END
 with wave.open(str(ROOT/'配音'/'第三段_卷轴版.wav'),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(PCM.tobytes())
 (ROOT/'台词与时间轴.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2),encoding='utf-8')
def label(s,text,x,y,width,color=None,size=44):
 s.rect(x-10,y-3,width+20,60,fill=b.CREAM,stroke='#bfd1d0',width=1,r=16)
 s.text(text,x,y,size,color or b.INK,'center',width)
def full_scene(t,subtitle=True):
 row=next((r for r in DATA if r['start']<=t<r['end']),DATA[-1]);mode=row['mode'];age=max(0,t-row['start']);s=b.Scene()
 s.rect(0,0,1920,1080,fill=b.CREAM,stroke=None,r=0)
 sc=1750/620;mx=85
 s.image(str(MAP),mx,0,1750,369*sc)
 def at(x,y):return mx+x*sc,(y-34)*sc
 label(s,'西太平洋',38,180,365,b.CORAL,49);label(s,'东太平洋',1490,180,365,b.BLUE,49)
 label(s,'正常状态',1540,8,310,b.INK,43)
 if mode in ('信风','水层','西升','东沉','高空','沃克','悬念'):
  old.arrow(s,[at(430,190),at(190,190)],b.CORAL,11,b.ease(age/.8) if mode=='信风' else 1)
  label(s,'东风信风：东 → 西',673,467,654,b.CORAL,46)
 if mode in ('水层','西升','东沉','高空','沃克','悬念'):
  label(s,'暖水层较厚',39,789,420,b.CORAL,46)
  label(s,'暖水层较薄',1410,852,430,b.BLUE,46)
  old.arrow(s,[at(411,346),at(411,303)],b.BLUE,11,b.ease(age/.75) if mode=='水层' else 1)
  label(s,'冷水上涌',1460,727,360,b.BLUE,47)
  label(s,'温跃层',812,869,280,b.INK,39)
 if mode in ('西升','东沉','高空','沃克','悬念'):
  old.arrow(s,[at(160,172),at(160,72)],b.CORAL,13,b.ease(age/.75) if mode=='西升' else 1)
  label(s,'暖湿空气上升',39,302,410,b.CORAL,44)
  if mode=='西升':
   for j in range(10):
    x,y=at(142+(j%3)*18,110+(j//3)*19+(t*22)%16);s.line([(x,y),(x-4,y+17)],'#65aac7',4)
 if mode in ('东沉','高空','沃克','悬念'):
  old.arrow(s,[at(405,72),at(405,172)],b.BLUE,13,b.ease(age/.75) if mode=='东沉' else 1)
  label(s,'空气下沉',1490,302,350,b.BLUE,46)
 if mode in ('高空','沃克','悬念'):
  old.arrow(s,[at(175,62),at(388,62)],b.CORAL,12,b.ease(age/1) if mode=='高空' else 1)
  label(s,'高空回流：西 → 东',615,5,650,b.CORAL,44)
 if mode in ('沃克','悬念'):
  route=[at(160,174),at(160,62),at(405,62),at(405,174),at(190,190),at(160,174)]
  if mode=='沃克':old.arrow(s,route,'#d2a453',8,b.ease(age/1.4))
  label(s,'沃克环流',760,190,410,b.CORAL,50)
 if subtitle:
  s.rect(0,940,1920,140,fill='#244559',stroke=None,r=0)
  lines=old.wrap(row['text'],46,1790)
  y=955 if len(lines)>1 else 974
  for j,line in enumerate(lines):s.text(line,65,y+j*57,46,'#fffaf0','center',1790)
 return s
src=inspect.getsource(p.v.render).replace("fw=b.F[a['size']].getlength(line)","fw=b.F[a['size']].getlength(line);y+=b.F[a['size']].getmetrics()[0]").replace("anchor='lt'","anchor='ls'")
src=src.replace("if t<.18:return Image.new('RGB',(W,H),'black')","if False:return im").replace("if t<.53:im=Image.blend","if False:im=Image.blend")
env=dict(p.v.__dict__);env['scene']=full_scene;exec(src,env);diagram_render=env['render']
def scroll(im,cx,cy,width,height,content=None):
 d=ImageDraw.Draw(im);x=cx-width/2;y=cy-height/2;radius=max(7,min(21,width*.025))
 if width>45:
  d.rounded_rectangle((x,y,x+width,y+height),radius=8,fill='#fff8e4',outline='#c9ad78',width=3)
  if content:
   art=content.resize((max(1,round(width-16)),max(1,round(height-12))),Image.Resampling.LANCZOS)
   im.paste(art,(round(x+8),round(y+6)));d=ImageDraw.Draw(im)
 for xx in (x,x+width) if width>45 else (cx,):
  for k in range(-round(radius),round(radius)+1):
   z=k/radius;shade=round(183+53*math.sqrt(max(0,1-z*z)))
   d.line([(xx+k,y-12),(xx+k,y+height+12)],fill=(min(255,shade+12),shade,max(0,shade-33)),width=1)
  d.ellipse((xx-radius,y-17,xx+radius,y+1),fill='#efd49a',outline='#aa8654',width=2)
  d.ellipse((xx-radius,y+height-1,xx+radius,y+height+17),fill='#d3b67a',outline='#aa8654',width=2)
def transition(age):
 stage=Image.open(b.BG).convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS);stage.paste(OLD_BOARD,(24,140),OLD_BOARD)
 actor=TAKE.resize((390,390),Image.Resampling.LANCZOS);stage.paste(actor,(1510,660),actor)
 pocket=(1510+660/TAKE.width*390,660+790/TAKE.height*390)
 if age<.70:
  q=b.ease((age-.16)/.54);cx=pocket[0];cy=pocket[1]+45-53*q
  layer=Image.new('RGBA',(1920,1080));scroll(layer,cx,cy,25,60)
  # The lower scroll remains occluded by the pouch opening until it rises out.
  cutoff=round(pocket[1]+8);layer.paste((0,0,0,0),(0,cutoff,1920,1080));stage.paste(layer,(0,0),layer)
  return stage
 travel=b.ease((age-.70)/.72);openq=b.ease((age-1.04)/1.30)
 cx=pocket[0]+(960-pocket[0])*travel;cy=pocket[1]-8+(520-(pocket[1]-8))*travel
 width=25+(1920-25)*openq;height=60+(1080-60)*openq
 scroll(stage,cx,cy,width,height,POSTER if openq>.03 else None)
 if age>2.30:stage=Image.blend(stage,POSTER,b.ease((age-2.30)/.38))
 return stage
def render(t):
 if t<BRIDGE_START:return old.base_render(t)
 if t<BRIDGE_END:return transition(t-BRIDGE_START)
 return diagram_render(t)
def encode(path,start,length):
 wav=ROOT/'配音'/(path.stem+'.wav')
 with wave.open(str(wav),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(PCM[round(start*24000):round((start+length)*24000)].tobytes())
 cmd=[EXE,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(wav),'-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(path)]
 with open(ROOT/'.build'/(path.stem+'.log'),'w') as log:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for n in range(math.ceil(length*24)):proc.stdin.write(render(start+n/24).tobytes())
  proc.stdin.close();assert proc.wait()==0
 check=subprocess.run([EXE,'-v','error','-i',str(path),'-f','null','-'],capture_output=True);assert check.returncode==0,check.stderr
def main():
 global OLD_BOARD,POSTER
 asyncio.run(audio())
 saved=old.bubble;old.bubble=lambda *args,**kwargs:None
 OLD_BOARD=old.base_render(BRIDGE_START-.05).crop((24,140,1474,1030)).convert('RGBA');old.bubble=saved
 scene_saved=env['scene'];env['scene']=lambda t:full_scene(BRIDGE_END+.2,False);POSTER=diagram_render(BRIDGE_END+.2);env['scene']=scene_saved
 for a in (.3,.68,1.25,1.9,2.7):render(BRIDGE_START+a).save(ROOT/f'卷轴检查_{a}.png')
 for mode in ('方向','信风','水层','沃克'):
  row=next(r for r in DATA if r['mode']==mode);render(row['start']+(row['speech_end']-row['start'])*.65).save(ROOT/f'全屏检查_{mode}.png')
 if '--preview' in sys.argv:return
 end=next(r['end'] for r in DATA if r['mode']=='方向')
 demo=ROOT/'交付'/'肚兜取卷轴_全屏图解_demo_v16.mp4';encode(demo,BRIDGE_START,end-BRIDGE_START)
 if '--full' in sys.argv:encode(ROOT/'交付'/'海洋发烧了_第三段_全屏图解_v16.mp4',0,DURATION)
 (ROOT/'验证.json').write_text(json.dumps(dict(demo_decode='PASS',demo_seconds=end-BRIDGE_START,full_segment_rendered='--full' in sys.argv,transition_seconds=2.8,source='same NOAA original; camera crop and enlarged independent Chinese labels',diagram_width_px=1750,subtitles='bottom band; 46px',no_presenter_after_transition=True,no_concat=True,output=str(demo)),ensure_ascii=False,indent=2),encoding='utf-8')
 print(demo,flush=True)
if __name__=='__main__':main()
