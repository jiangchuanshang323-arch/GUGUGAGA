from pathlib import Path
import sys,math,json,wave,subprocess,asyncio,hashlib,importlib.util,re
from functools import lru_cache
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
for name in ('交付','素材','配音','检查','.build'):(ROOT/name).mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(PROJECT/'ocean_animation_demo_20261011'/'runtime'))
sys.path.insert(0,str(PROJECT/'主体课程'/'正文日系2D_配音_v2'/'runtime'))
sys.path.insert(0,str(ROOT/'.runtime'))
import imageio_ffmpeg,edge_tts
EXE=imageio_ffmpeg.get_ffmpeg_exe()
spec=importlib.util.spec_from_file_location('native30',PROJECT/'固定剖面_局部强调_v30'/'build_demo.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
INK=native.INK;BLUE=native.BLUE;CORAL=native.CORAL;CREAM=native.CREAM
FONT=native.v.FONT
@lru_cache(None)
def font(s):return ImageFont.truetype(str(FONT),s)
LINES=[
 ('引入','接着，把正常年和厄尔尼诺年放在一起，检验刚才的机制。'),
 ('信风','先看近海面：正常年东风信风较强，厄尔尼诺时，信风减弱。'),
 ('暖水','再看海水：暖水向东扩展，东部的暖水层增厚，温跃层加深。'),
 ('上涌','东部冷水上涌受到抑制，来自深层的冷水补给减少。'),
 ('环流','对比大气：沃克环流减弱，对流和降雨区域向东移动。'),
 ('收束','这五项变化互相关联，说明海洋异常会带动大气响应。'),
 ('地图','现在，把剖面放回地图。印尼在太平洋西侧，秘鲁在东侧。'),
 ('两地','两地分居海洋两侧，受到的降水影响，可能并不相同。'),
 ('推理','判断时，先找上升和下沉气流，再想云雨会在哪里形成。'),
 ('解释','别急着背结论，尝试用气流的变化，解释你的判断。'),
 ('提问','轮到你来预测：厄尔尼诺发生时，印尼和秘鲁的降水，会怎样变化？'),
 ('思考',''),
 ('承下','先记下你的判断。下一部分，我们用真实案例来验证。')]
DATA=[];PCM=None;DURATION=0
async def audio():
 global DATA,PCM,DURATION
 parts=[np.zeros(6000,dtype='<i2')];cursor=.25;DATA=[]
 for i,(mode,words) in enumerate(LINES):
  if not words:
   DATA.append({'mode':mode,'text':'','start':cursor,'speech_end':cursor,'end':cursor+3,'word_shot':13})
   parts.append(np.zeros(72000,dtype='<i2'));cursor+=3;continue
  p=ROOT/'配音'/f'{i:02d}_{mode}.mp3'
  if not p.exists() or p.stat().st_size<1000:
   for attempt in range(3):
    try:await edge_tts.Communicate(words,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=40).save(str(p));break
    except Exception:
     if attempt==2:raise
     await asyncio.sleep(1)
  raw=subprocess.check_output([EXE,'-v','error','-i',str(p),'-f','s16le','-ar','24000','-ac','1','-'])
  a=np.frombuffer(raw,dtype='<i2');nz=np.flatnonzero(np.abs(a.astype(np.int32))>220)
  if len(nz):a=a[max(0,nz[0]-600):min(len(a),nz[-1]+720)]
  pause=.10 if mode!='承下' else .28;dur=len(a)/24000
  DATA.append({'mode':mode,'text':words,'start':cursor,'speech_end':cursor+dur,'end':cursor+dur+pause,'word_shot':12 if i<6 else 13})
  parts.extend([a,np.zeros(round(pause*24000),dtype='<i2')]);cursor+=dur+pause
  print(f'Voice {i+1}/{len(LINES)} {cursor:.2f}s',flush=True)
 PCM=np.concatenate(parts);DURATION=len(PCM)/24000
 with wave.open(str(ROOT/'配音'/'正常异常对照_区域预测_晓伊.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(PCM.tobytes())
 (ROOT/'台词与时间轴.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2),encoding='utf-8')

def load_audio():
 global DATA,PCM,DURATION
 DATA=json.loads((ROOT/'台词与时间轴.json').read_text(encoding='utf-8'))
 with wave.open(str(ROOT/'配音'/'正常异常对照_区域预测_晓伊.wav'),'rb') as w:PCM=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
 DURATION=len(PCM)/24000

def ease(q):q=max(0,min(1,q));return q*q*q*(q*(q*6-15)+10)
def text(im,words,x,y,size=42,color=INK,center=False,records=None):
 f=font(size);box=f.getbbox(words);ww=box[2]-box[0];hh=box[3]-box[1]
 if center:x-=ww/2
 ImageDraw.Draw(im).text((x-box[0],y-box[1]),words,font=f,fill=color)
 if records is not None:
  rect=[x,y,x+ww,y+hh];assert 16<=x and x+ww<=1904 and 14<=y and y+hh<=1068,(words,rect)
  records.append({'text':words,'rect':rect})
def card(im,words,box,size=38,color=INK,records=None):
 x,y,z,b=box;d=ImageDraw.Draw(im);d.rounded_rectangle(box,16,fill=CREAM,outline='#b8cfd5',width=2)
 f=font(size);bb=f.getbbox(words);ww=bb[2]-bb[0];hh=bb[3]-bb[1]
 assert ww<=z-x-24 and hh<=b-y-12,(words,ww,box)
 text(im,words,(x+z)/2,(y+b-hh)/2,size,color,True,records)
 return list(box)

def header(title,subtitle):
 f=font(57);sf=font(31);w=round(max(f.getlength(title)+140,sf.getlength(subtitle)+60,440));h=132
 art=Image.new('RGBA',((w+12)*2,(h+10)*2));d=ImageDraw.Draw(art)
 pts=[(0,20),(0,h*2-20),(20,h*2),(w*2-30,h*2),(w*2,h*2-20),(w*2,25),(w*2-25,0),(20,0)]
 d.polygon(pts,fill=CREAM);d.line(pts+[pts[0]],fill='#a9c5ce',width=2,joint='curve')
 d.rounded_rectangle((48,0,178,12),5,fill='#b7d1d6');d.line((48,42,48,141),fill='#7ba3b4',width=5)
 for words,x,y,s,color in [(title,43,20,57,INK),(subtitle,29,92,31,'#668697')]:
  ff=ImageFont.truetype(str(FONT),s*2);bb=ff.getbbox(words);d.text((x*2-bb[0],y*2-bb[1]),words,font=ff,fill=color)
 for j in range(2):d.line([((w-62+n*.6)*2,(31+j*8+3*math.sin(n/50*math.pi*2))*2) for n in range(51)],fill='#a5c5d0',width=3)
 return art.resize((w+12,h+10),Image.Resampling.LANCZOS)
HEADERS={'compare':header('查病因 · 正常与异常对照','从海洋变化，看大气响应'),'map':header('互动 · 预测两地降水','先辨位置，再用机制推理')}
SKY=native.v.gradient((850,190),(244,251,250),(221,239,242))
WARM=native.v.gradient((850,150),(255,227,191),(240,182,149))
COLD=native.v.gradient((850,150),(166,210,221),(89,151,183))
CLOUD=native.v.CLOUD.resize((140,84),Image.Resampling.LANCZOS)

def diagram(el,focus):
 im=Image.new('RGB',(850,340),'#e6f1f3');im.paste(SKY,(0,0))
 xs=np.arange(850);q=xs/849
 depths=(85+np.sin(xs/75)*2) if el else (115-78*(q*q*(3-2*q))+np.sin(xs/75)*2)
 mask=Image.new('L',(850,150));pts=[(int(x),float(y)) for x,y in zip(xs[::2],depths[::2])]+[(849,float(depths[-1]))]
 ImageDraw.Draw(mask).polygon([(0,0),(849,0)]+pts[::-1],fill=255)
 sea=COLD.copy();sea.paste(WARM,(0,0),mask);im.paste(sea,(0,190));d=ImageDraw.Draw(im)
 d.line([(x,y+190) for x,y in pts],fill='#c18a61' if focus=='暖水' else '#fff4df',width=3,joint='curve')
 d.line((0,190,850,190),fill='#8fb6c5',width=2)
 cx=490 if el else 170
 im.paste(CLOUD,(cx-70,42),CLOUD)
 for j in (-2,-1,1,2):d.line((cx+j*20,120,cx+j*20-3,133),fill='#85b2c8',width=2)
 alpha=lambda key:1 if focus==key else .58
 native.arrow(im,[(718,165),(490 if el else 176,165)],CORAL,6,alpha('信风'))
 native.arrow(im,[(cx+18,27),(719,27)],native.v.GOLD,5,alpha('环流')*(.7 if el else 1))
 native.arrow(im,native.v.cubic((cx,149),(cx-74,144),(cx-78,64),(cx,27),24),CORAL,5,alpha('环流')*(.7 if el else 1))
 native.arrow(im,[(739,53),(739,147)],BLUE,5,alpha('环流')*(.6 if el else 1))
 if el:native.arrow(im,[(95,50),(95,145)],BLUE,4,.55)
 native.arrow(im,[(783,322),(783,297 if el else 233)],BLUE,6,alpha('上涌')*(.55 if el else 1))
 text(im,'西 ← 东',640 if el else 440,128,28,CORAL,True)
 text(im,'暖水',135,207,28,CORAL)
 text(im,'冷水',414,302,28,INK)
 d.line((638,295,638,190+float(depths[638])+5),fill='#638fa4',width=2)
 text(im,'温跃层',638,303,25,INK,True)
 return im

NASA=Image.open(ROOT/'素材'/'NASA_BlueMarble_5400.jpg').convert('RGB')
assert NASA.size==(5400,2700)
# Re-centre an official equirectangular basemap without redrawing any coastlines.
crop=Image.new('RGB',(3150,1313));crop.paste(NASA.crop((4050,675,5400,1988)),(0,0));crop.paste(NASA.crop((0,675,1800,1988)),(1350,0))
MAP=crop.resize((1800,750),Image.Resampling.LANCZOS)
MAP.save(ROOT/'素材'/'NASA_太平洋裁切_1800.png')
def geo(lon,lat):return 60+(lon-90)/210*1800,180+(45-lat)/87.5*750
INDO=geo(118,-3);PERU=geo(282,-9)

COMPARISONS=[('东风信风','较强','减弱'),('暖水层','西侧堆积较厚','向中东部扩展'),('东部冷水上涌','较强','受抑、减弱'),('沃克环流','较强','减弱'),('对流与降雨','偏西侧','向东移动')]
@lru_cache(None)
def compare(mode):
 im=Image.new('RGB',(1920,1080),CREAM);im.paste(HEADERS['compare'],(16,14),HEADERS['compare'])
 focus={'信风':'信风','暖水':'暖水','上涌':'上涌','环流':'环流','降雨':'环流'}.get(mode)
 records=[];boxes=[]
 for el,x in [(False,70),(True,1000)]:
  boxes.append(card(im,'厄尔尼诺年' if el else '正常年',(x,176,x+850,232),40,CORAL if el else BLUE,records))
  text(im,'西 · 印尼',x+20,239,30,INK,False,records);text(im,'东 · 秘鲁',x+675,239,30,INK,False,records)
  im.paste(diagram(el,focus),(x,278))
 active={'信风':0,'暖水':1,'上涌':2,'环流':3,'降雨':4}.get(mode,-1)
 d=ImageDraw.Draw(im)
 for i,(name,a,b) in enumerate(COMPARISONS):
  y=635+i*57
  if i==active:d.rounded_rectangle((60,y-5,1860,y+49),12,fill='#f9e9d4',outline='#ddba97',width=1)
  elif i%2==0:d.rounded_rectangle((60,y-5,1860,y+49),12,fill='#edf3f2')
  text(im,name,90,y+4,37,INK,False,records)
  text(im,a,685,y+4,38,BLUE,True,records);text(im,b,1430,y+4,38,CORAL,True,records)
 return im,records,boxes

def map_scene(mode,t):
 im=Image.new('RGB',(1920,1080),CREAM);im.paste(MAP,(60,180));im.paste(HEADERS['map'],(16,14),HEADERS['map'])
 records=[];boxes=[];d=ImageDraw.Draw(im)
 # Geographic annotations only. No rainfall answer is exposed before the next chapter.
 eq=geo(90,0)[1];d.line((60,eq,1860,eq),fill='#9bbac9',width=2)
 text(im,'赤道',930,eq-40,31,'#e6f1ef',True,records)
 for (x,y),label,box,color in [(INDO,'印尼 · 西太平洋',(115,445,445,508),BLUE),(PERU,'秘鲁 · 东太平洋',(1480,488,1825,551),CORAL)]:
  d.ellipse((x-7,y-7,x+7,y+7),fill='#fff8df',outline=color,width=3)
  d.line(((box[0]+box[2])/2,box[3],x,y-13),fill='#c9dce1',width=3)
  boxes.append(card(im,label,box,38,color,records))
 if mode not in ('地图',):
  boxes.append(card(im,'降水：？',(120,735,445,802),43,INK,records))
  boxes.append(card(im,'降水：？',(1480,735,1815,802),43,INK,records))
 if mode in ('推理','解释'):
  boxes.append(card(im,'气流升降  →  云雨变化',(585,824,1335,899),42,INK,records))
 if mode=='思考':
  age=t-next(r['start'] for r in DATA if r['mode']=='思考')
  im=Image.blend(im,Image.new('RGB',im.size,'#1a3a50'),.18)
  number=str(max(1,3-int(age)))
  ImageDraw.Draw(im).ellipse((886,330,1034,478),fill=CREAM,outline='#b3cdd6',width=3)
  text(im,number,960,358,72,INK,True,records)
 return im,records,boxes

PREVIOUS=None
def render(t):
 row=next((r for r in DATA if r['start']<=t<r['end']),DATA[0] if t<DATA[0]['start'] else DATA[-1])
 if row['word_shot']==12:
  mode=row['mode']
  if mode=='环流' and t-row['start']>(row['speech_end']-row['start'])*.45:mode='降雨'
  a,records,boxes=compare(mode);im=a.copy()
 else:im,records,boxes=map_scene(row['mode'],t)
 mapstart=next(r['start'] for r in DATA if r['mode']=='地图')
 if mapstart<=t<mapstart+.55:
  old,_,_=compare('收束');im=Image.blend(old,im,ease((t-mapstart)/.55))
 if PREVIOUS is not None and t<.65:im=Image.blend(PREVIOUS,im,ease(t/.65))
 d=ImageDraw.Draw(im);d.rectangle((0,958,1920,1080),fill='#244b60')
 sub=row['text'];lines=[];line=''
 for ch in sub:
  if font(46).getlength(line+ch)>1750:lines.append(line);line=ch
  else:line+=ch
 if line:lines.append(line)
 yy=965 if len(lines)>1 else 987
 for line in lines:text(im,line,960,yy,46,'#fffaf0',True,records);yy+=49
 for x,y,z,b in boxes:assert 55<=x<z<=1865 and 160<=y<b<=935
 return im,{'time':t,'mode':row['mode'],'word_shot':row['word_shot'],'text_rects':records,'boxes':boxes,'camera_fixed':True,'answer_revealed':False}

def main():
 global PREVIOUS
 if '--audio' in sys.argv:asyncio.run(audio());return
 load_audio()
 prev=ROOT/'.build'/'前段结束帧.png'
 if not prev.exists():subprocess.run([EXE,'-y','-v','error','-sseof','-0.50','-i',str(PROJECT/'demooo'/'合成版本'/'开场及前三段'/'海洋发烧了_开场及前三段.mp4'),'-frames:v','1',str(prev)],check=True)
 PREVIOUS=Image.open(prev).convert('RGB')
 times=[1]+[r['start']+.6 for r in DATA if r['mode'] in ('信风','暖水','上涌','环流','地图','两地','推理','提问','思考','承下')]
 for i,t in enumerate(times):render(t)[0].save(ROOT/'检查'/f'节点_{i:02d}.png')
 if '--preview' in sys.argv:return
 out=ROOT/'交付'/'海洋发烧了_第四段_对照与区域预测_v36.mp4'
 cmd=[EXE,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(ROOT/'配音'/'正常异常对照_区域预测_晓伊.wav'),
 '-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-vf','setsar=1','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE);count=math.ceil(DURATION*24);audit=[]
 for n in range(count):
  im,meta=render(n/24);audit.append(meta);proc.stdin.write(im.tobytes())
  if n%240==0:print(f'Render {n}/{count}',flush=True)
 proc.stdin.close();err=proc.stderr.read();assert proc.wait()==0,err
 check=subprocess.run([EXE,'-v','error','-i',str(out),'-f','null','-'],capture_output=True);assert check.returncode==0 and not check.stderr,check.stderr
 contact=Image.new('RGB',(1920,870),'#e7eeee');dd=ImageDraw.Draw(contact)
 for i,t in enumerate(times[:12]):
  x=i%4*480;y=i//4*290;im,_=render(t);contact.paste(im.resize((480,270),Image.Resampling.LANCZOS),(x,y));dd.text((x+8,y+273),f'{t:.2f}s',fill=INK)
 contact.save(ROOT/'检查'/'内容与接续检查.jpg',quality=94)
 (ROOT/'检查'/'逐帧版面检查.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 report={'output':str(out),'seconds':DURATION,'resolution':[1920,1080],'fps':24,'frames_checked':count,'decode':'PASS','word_shots':[12,13],
 'digital_human':False,'answer_revealed':False,'think_seconds':3,'map_original_size':[5400,2700],'map_crop_size':[3150,1313],
 'map_coordinates':{'印尼':[118,-3],'秘鲁':[-78,-9]},'source_word':str(next((PROJECT/'00_原始资料').glob('*最新批注版*.docx'))),
 'visual_review':'待抽帧复核','sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
 (ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
