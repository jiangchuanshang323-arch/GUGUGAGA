from pathlib import Path
import sys,math,json,subprocess,hashlib,importlib.util
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont,ImageFilter

ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
for f in ('交付','.build','检查'):(ROOT/f).mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(PROJECT/'ocean_animation_demo_20261011'/'runtime'))
import imageio_ffmpeg
EXE=imageio_ffmpeg.get_ffmpeg_exe()
SOURCE=PROJECT/'阶段合成_v32'/'交付'/'海洋发烧了_目前阶段新版_v32.mp4'
OUT=ROOT/'交付'/'海洋发烧了_统一章节标题_v35.mp4'
REPORT32=json.loads((PROJECT/'阶段合成_v32'/'合成验证.json').read_text(encoding='utf-8'))
FIRST,SECOND,THIRD=REPORT32['segment_start_seconds'][1:]
ROWS=json.loads((PROJECT/'阶段合成_v32'/'第一段修订时间轴.json').read_text(encoding='utf-8'))
FONT=PROJECT/'主体课程'/'得意黑_大字无水印_v6'/'素材'/'SmileySans-Oblique.ttf'
BG=Image.open(PROJECT/'主体课程'/'正文日系2D_配音_v2'/'素材'/'日系2D水下课堂.png').convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS)
PLAIN=Image.new('RGB',(1920,1080),'#eef9fa')
CREAM=Image.new('RGB',(1920,1080),'#fffaf0')
CARDS={};CARD_META={}

def smooth(q):q=max(0,min(1,q));return q*q*(3-2*q)

def seal(key,title,subtitle=None,size=53,subsize=31):
 f=ImageFont.truetype(str(FONT),size);fs=ImageFont.truetype(str(FONT),subsize)
 width=max(440 if subtitle else 0,round(max(f.getlength(title)+110,fs.getlength(subtitle)+58 if subtitle else 0)))
 height=max(130,91+(fs.getbbox(subtitle)[3]-fs.getbbox(subtitle)[1])+8) if subtitle else max(85,size+32)
 art=Image.new('RGBA',((width+16)*2,(height+12)*2));shadow=Image.new('RGBA',art.size)
 pts=[(0,20),(0,height*2-20),(18,height*2),(width*2-30,height*2),(width*2,height*2-20),(width*2,26),(width*2-24,0),(20,0)]
 d=ImageDraw.Draw(shadow);d.polygon([(x+3,y+9) for x,y in pts],fill=(61,91,105,18))
 art=Image.alpha_composite(art,shadow.filter(ImageFilter.GaussianBlur(9)));d=ImageDraw.Draw(art)
 d.polygon(pts,fill='#fffaf0');d.line(pts+[pts[0]],fill='#a9c5ce',width=2,joint='curve')
 d.rounded_rectangle((48,0,178,12),5,fill='#b7d1d6');d.line((49,40,49,min(140,height*2-35)),fill='#7ba3b4',width=5)
 texts=[(title,43,19,size,'#36566b')]
 if subtitle:texts.append((subtitle,29,91,subsize,'#668697'))
 rects=[]
 for words,x,y,s,color in texts:
  ff=ImageFont.truetype(str(FONT),s*2);b=ff.getbbox(words)
  d.text((x*2-b[0],y*2-b[1]),words,font=ff,fill=color)
  rect=[x,y,x+(b[2]-b[0])/2,y+(b[3]-b[1])/2]
  assert rect[2]<width-18 and rect[3]<height-5,(words,rect,width,height)
  rects.append({'text':words,'rect':rect,'size':s})
 for j in range(2):
  wave_start=width-78 if subtitle else width-43
  wave_step=.84 if subtitle else .50
  d.line([((wave_start+n*wave_step)*2,(31+j*8+3*math.sin(n/50*2*math.pi))*2) for n in range(51)],fill='#a5c5d0',width=3)
 assert rects[0]['rect'][2]<wave_start-5,('decoration touches title',key,rects[0]['rect'],wave_start)
 art=art.resize((width+16,height+12),Image.Resampling.LANCZOS)
 art.save(ROOT/'.build'/f'标题_{key}.png')
 CARDS[key]=art;CARD_META[key]={'title':title,'subtitle':subtitle,'width':width,'height':height,'text_rects':rects}

seal('三地','海洋“发烧”了','厄尔尼诺 · 从三地情境开始',63)
seal('线索','线索藏在赤道中东太平洋',size=55)
seal('定位','定位Niño3.4区',size=55)
seal('体温','测体征 · 给海洋读“体温”',size=53)
seal('热量','测体征 · 小温差，大热量',size=53)
seal('原理','厄尔尼诺现象','太平洋东西向剖面',61,33)

def paste_seal(im,key,background,area,alpha=1):
 # Restore only the old heading's native background; all lower teaching content stays untouched.
 im.paste(background.crop(area),(area[0],area[1]))
 if alpha>.001:
  art=CARDS[key]
  if alpha<.999:
   art=art.copy();art.putalpha(art.getchannel('A').point(lambda a:round(a*alpha)))
  im.paste(art,(16,14),art)

BRIDGE_START=THIRD+15.916666666666666
BRIDGE_FRAME=math.ceil(BRIDGE_START*24)
SCIENCE_START=THIRD+18.75
SCIENCE_FRAME=math.ceil(SCIENCE_START*24)
BRIDGE_IMAGES={}

def prepare_bridge():
 # The approved motion is reused. Only its background chapter seal and scroll artwork are updated.
 sys.path.insert(0,str(PROJECT/'主体课程'/'上抛后恢复普通姿势_v23'))
 import build_v23 as actor
 spec=importlib.util.spec_from_file_location('diagram30',PROJECT/'固定剖面_局部强调_v30'/'build_demo.py')
 diagram=importlib.util.module_from_spec(spec);spec.loader.exec_module(diagram)
 poster,_=diagram.render(0);paste_seal(poster,'原理',CREAM,(0,0,730,157))
 ImageDraw.Draw(poster).rectangle((0,958,1920,1080),fill='#244b60')
 actor.s.POSTER=poster
 room=BG.copy();room.paste(CARDS['热量'],(16,14),CARDS['热量'])
 roompath=ROOT/'.build'/'卷轴衔接背景.png';room.save(roompath)
 original_bg=actor.b.BG;actor.b.BG=roompath
 count=SCIENCE_FRAME-BRIDGE_FRAME
 for i in range(count):BRIDGE_IMAGES[BRIDGE_FRAME+i]=actor.transition(2.8*i/max(1,count-1))
 actor.b.BG=original_bg
 print(f'Prepared {count} scroll frames with the new chapter seal',flush=True)

def apply(im,n):
 t=n/24;key=None;alpha=1
 if n in BRIDGE_IMAGES:return BRIDGE_IMAGES[n],{'time':t,'key':'卷轴内外统一封签'}
 if FIRST+1.6<=t<SECOND:
  u=t-FIRST;row=next((r for r in ROWS if r['start']<=u<r['end']),ROWS[0] if u<ROWS[0]['start'] else ROWS[-1])
  mode=row['mode']
  if mode in ('欢迎','观察','秘鲁','印尼','江南','思考','联系','会诊','四步'):
   key='三地';paste_seal(im,key,BG,(0,0,715,151))
  else:
   key='定位' if mode in ('测量','定位','结束') else '线索'
   paste_seal(im,key,PLAIN,(0,0,1390,115))
 elif SECOND<=t<THIRD:
  u=t-SECOND;start=3.454875;end=5.854875
  if u<start:key='定位';paste_seal(im,key,PLAIN,(0,0,1390,115))
  elif u<end:
   age=u-start;q=smooth((age-.28)/.90)
   native=Image.blend(PLAIN,BG,q)
   im.paste(native.crop((0,0,1475,115)),(0,0))
   if age<.8:key='定位';alpha=1-smooth((age-.08)/.7)
   elif age>1.6:key='体温';alpha=smooth((age-1.6)/.5)
   if key:
    art=CARDS[key].copy();art.putalpha(art.getchannel('A').point(lambda a:round(a*alpha)));im.paste(art,(16,14),art)
  else:key='体温';paste_seal(im,key,BG,(0,0,1475,115))
 elif THIRD<=t<BRIDGE_FRAME/24:
  key='热量';paste_seal(im,key,BG,(0,0,1475,115))
 elif n>=SCIENCE_FRAME:
  key='原理';paste_seal(im,key,CREAM,(0,0,730,157))
 if key:
  w,h=CARDS[key].size
  assert 16+w<1390 and 14+h<=172
  if key in ('定位','线索','体温','热量'):assert 14+CARD_META[key]['height']<120
 return im,{'time':t,'key':key,'alpha':alpha}

def main():
 prepare_bridge()
 decoder=subprocess.Popen([EXE,'-v','error','-i',str(SOURCE),'-map','0:v:0','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 encoder=subprocess.Popen([EXE,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(SOURCE),
 '-map','0:v','-map','1:a','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-vf','setsar=1','-c:a','copy','-movflags','+faststart',str(OUT)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 frame_bytes=1920*1080*3;n=0;audit=[]
 while True:
  raw=decoder.stdout.read(frame_bytes)
  if not raw:break
  assert len(raw)==frame_bytes
  im=Image.frombytes('RGB',(1920,1080),raw);im,meta=apply(im,n)
  audit.append(meta);encoder.stdin.write(im.tobytes())
  if n%480==0:print(f'Update titles {n/24:.0f}s /188s',flush=True)
  n+=1
 encoder.stdin.close();derr=decoder.stderr.read();eerr=encoder.stderr.read()
 assert decoder.wait()==0,derr;assert encoder.wait()==0,eerr
 result=subprocess.run([EXE,'-v','error','-i',str(OUT),'-progress','pipe:1','-nostats','-f','null','-'],capture_output=True)
 assert result.returncode==0 and not result.stderr,result.stderr
 import re
 decoded=int(re.findall(rb'frame=(\d+)',result.stdout)[-1]);assert decoded==n
 def audio_hash(path):
  audio=subprocess.check_output([EXE,'-v','error','-i',str(path),'-map','0:a','-c:a','copy','-f','adts','-'])
  return hashlib.sha256(audio).hexdigest()
 before=audio_hash(SOURCE);after=audio_hash(OUT);assert before==after
 times=[13,25,41,61,69,73,91,120,136,149.9,151.2,179]
 sheet=Image.new('RGB',(1920,870),'#e6eeee');sd=ImageDraw.Draw(sheet)
 for i,t in enumerate(times):
  p=ROOT/'检查'/f'解码检查_{t}.png'
  subprocess.run([EXE,'-y','-v','error','-ss',str(t),'-i',str(OUT),'-frames:v','1',str(p)],check=True)
  image=Image.open(p).convert('RGB');x=i%4*480;y=i//4*290
  sheet.paste(image.resize((480,270),Image.Resampling.LANCZOS),(x,y));sd.text((x+8,y+273),f'{t:.1f}s',fill='#36566b')
 sheet.save(ROOT/'检查'/'全片统一标题检查.jpg',quality=94)
 (ROOT/'检查'/'逐帧标题检查.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 info=subprocess.run([EXE,'-hide_banner','-i',str(OUT)],capture_output=True).stderr.decode('utf-8','replace')
 report={'output':str(OUT),'source':str(SOURCE),'frames':n,'decode':'PASS','audio_compressed_sha256':after,'audio_bit_identical':True,
 'source_duration':188.23,'media_info':info,'titles':CARD_META,'all_frames_layout_checked':True,'scroll_frames':len(BRIDGE_IMAGES),
 'old_theme_preserved':True,'new_voice_synthesis':False,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'visual_review':'待最终抽帧复核'}
 (ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'output':str(OUT),'frames':n,'audio_bit_identical':True,'decode':'PASS'},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
