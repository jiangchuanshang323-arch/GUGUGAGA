from pathlib import Path
import sys,json,math,wave,subprocess,importlib.util,shutil,hashlib
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;P=ROOT.parent
sys.path.insert(0,str(P/'卷图推板与五牌'))
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
o=module('domino_source',P/'卷图推板与五牌/update_parts.py')
from refine_components import install
install(o)
manager=module('delivery_manager',P/'demooo/manage_videos.py');FF=manager.EXE
M=json.loads((ROOT/'串讲配音.json').read_text(encoding='utf-8'))
S6=json.loads((P/'第六段_水收束与气/台词与时间轴.json').read_text(encoding='utf-8'))
S7=json.loads((P/'第七段_生与土/台词与时间轴.json').read_text(encoding='utf-8'))
q8=module('original_geo_quiz',P/'第八段_地形与配对/build_segment.py');S8=q8.M
DATA=json.loads(manager.MANIFEST.read_text(encoding='utf-8'))
KEYS=['05_环境多米诺_水','06_水收束与气','07_生与土','08_地形与配对']
for key in KEYS:
 p=ROOT/'.build'/f'原片_{key}.mp4'
 if not p.exists():shutil.copy2(manager.ROOT/DATA['segments'][key]['path'],p)
def read_pcm(p):
 with wave.open(str(p),'rb') as w:assert w.getframerate()==24000 and w.getnchannels()==1;return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').copy()
def wav(p,a):
 with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(a.astype('<i2').tobytes())
PCM={k:read_pcm(v['path']) for k,v in M.items()}
F=o.F;E=o.m.ease;INK=o.INK;BLUE=o.BLUE;CREAM=o.CREAM
WORDS=['水','气','生','土','地形'];TITLES={s:o.p.header(f'第{["一","二","三","四","五"][i]}张·{s}','自然环境各要素，通过过程相互联系') for i,s in enumerate(WORDS)}
RECAP=o.p.header('回看·环境多米诺','五张牌讲完了，试着找出联系')
SPRITES=P/'企鹅小老师_教学动作素材_20261012/独立动作PNG'
POSES={i:Image.open(next(SPRITES.glob(f'{i:02d}_*'))).convert('RGBA').resize((390,390),Image.Resampling.LANCZOS) for i in [3,4,6,9,12]}
MOUTHS={(p,s):o.m.mouth(p,s).resize((round(o.m.MOUTH_CENTERS[p][2]*390/512),round(o.m.MOUTH_CENTERS[p][3]*390/512)),Image.Resampling.LANCZOS) for p in [3,4,6] for s in range(4)}
AUDIT=[]
CHARACTER_PRESENT_AT_CARD_START={'水':True,'气':False,'生':False,'土':False,'地形':False}
def teacher(im,t,pcm,walk=False,thinking=False,feedback=False):
 x=20 if not walk else -390+410*E(t/.62);y=580+math.sin(t*2)*1.8
 if walk and t<.62:y-=abs(math.sin(t*14))*5
 pose=9 if thinking else 12 if feedback else 6 if t>1.4 else 3
 a=POSES[pose].copy()
 if pose in (3,4,6):
  lo=max(0,int(t*24000));v=pcm[lo:lo+960].astype(np.float32)/32768;rms=float(np.sqrt(np.mean(v*v))) if len(v) else 0
  state=0 if rms<.011 else 1 if rms<.055 else 2 if rms<.13 else 3
  mx,my,mw,mh=o.m.MOUTH_CENTERS[pose];a.alpha_composite(MOUTHS[pose,state],(round((mx-mw/2)*390/512),round((my-mh/2)*390/512)))
 im.paste(a,(round(x),round(y)),a)
 AUDIT.append(dict(kind='character',box=[round(x),round(y),round(x+390),round(y+390)],walking=walk and t<.62))
def bubble(im,words,age,span):
 # Current clause only; 46px as before, full-character baseline and justified non-final lines.
 chunks=[];s=''
 for ch in words:
  s+=ch
  if ch in '。？！' or (ch=='，' and len(s)>=7):chunks.append(s);s=''
 if s:chunks.append(s)
 pos=min(sum(map(len,chunks))-.001,max(0,age/span)*sum(map(len,chunks)));n=0;clause=chunks[-1]
 for c in chunks:
  n+=len(c)
  if pos<n:clause=c;break
 lines=o.wrap(clause,46,344)
 # Balance a short final line; punctuation must never become an orphan at the left edge.
 if len(lines)>1 and len(lines[-1])<=2:
  s=lines[-2]+lines[-1];cut=len(s)//2
  while cut<len(s)-1 and s[cut] in '，。！？；：、）》」』':cut+=1
  if F(46).getlength(s[:cut])<=344 and F(46).getlength(s[cut:])<=344:lines[-2:]=[s[:cut],s[cut:]]
 for j in range(1,len(lines)):
  if lines[j] and lines[j][0] in '，。！？；：、）》」』':
   char=lines[j-1][-1];lines[j-1]=lines[j-1][:-1];lines[j]=char+lines[j]
 h=len(lines)*57+36;x=30;y=547-h;w=386
 d=ImageDraw.Draw(im);d.rounded_rectangle((x,y,x+w,y+h),20,fill=CREAM,outline='#92b9c6',width=2)
 d.polygon([(x+174,y+h-2),(215,627),(x+230,y+h-2)],fill=CREAM);d.line([(x+174,y+h),(215,627),(x+230,y+h)],fill='#92b9c6',width=2)
 font=F(46);baselines=[]
 for j,line in enumerate(lines):
  extra=(344-F(46).getlength(line))/max(1,len(line)-1) if j<len(lines)-1 else 0;xx=x+21
  baseline=y+17+j*57-font.getbbox('国',anchor='ls')[1];baselines.append(baseline)
  for ch in line:
   # One shared baseline per line. Bounding-box top alignment incorrectly lifts commas.
   d.text((xx,baseline),ch,font=font,fill=INK,anchor='ls');xx+=font.getlength(ch)+extra
 AUDIT.append(dict(kind='bubble',text=clause,box=[x,y,x+w,y+h],tip=[215,627],baseline_anchor='ls',baselines=baselines))
def cards(t,index,recap=False,center_x=None):
 if not recap:
  # Current user correction: a chapter introduces one card, never the five-card overview.
  im=o.m.BG.copy();age=max(0,t-.10);q=E(age/.38)
  art=o.card_art(index,age,0);scale=1.38
  art=art.resize((round(235*scale),round(355*scale)),Image.Resampling.LANCZOS)
  x=(1135 if center_x is None else center_x)-art.width/2;y=530-art.height/2+20*(1-q)
  shadow=Image.new('RGBA',im.size);sd=ImageDraw.Draw(shadow)
  sd.rounded_rectangle((x+6,y+10,x+art.width+6,y+art.height+10),26,fill=(43,76,91,round(18*q)))
  im=Image.alpha_composite(im.convert('RGBA'),shadow).convert('RGB')
  art.putalpha(art.getchannel('A').point(lambda v:round(v*q)));im.paste(art,(round(x),round(y)),art)
  AUDIT.append(dict(kind='domino_card',index=index,count=1,box=[x,y,x+art.width,y+art.height]))
  return im
 im=o.m.BG.copy();d=ImageDraw.Draw(im);d.rounded_rectangle((452,215,1880,940),24,fill=CREAM,outline='#abc7ce',width=2)
 o.txt(im,'自然环境具有整体性',1165,260,68,INK,True)
 for i in range(5):
  age=max(0,t-.12-i*.045);a=o.card_art(i,age,1 if recap or i==index else 0)
  if not recap and i!=index:
   tint=Image.new('RGBA',a.size,'#fffaf0');a=Image.blend(a,tint,.20)
  scale=1.08 if i==index and not recap else 1
  a=a.resize((round(235*scale),round(355*scale)),Image.Resampling.LANCZOS)
  q=E(age/.35);y=415+22*(1-q)-(18 if i==index and not recap else 0);x=492+i*270+(235-a.width)/2
  a.putalpha(a.getchannel('A').point(lambda v:round(v*q)));im.paste(a,(round(x),round(y)),a)
 if not recap:o.txt(im,'这一张 · '+WORDS[index],1165,840,59,o.ORANGE,True)
 return im
def intro(t,mode,target,character_present=None):
 if character_present is None:character_present=CHARACTER_PRESENT_AT_CARD_START[mode]
 meta=M[mode];im=cards(t,WORDS.index(mode),center_x=1135 if character_present else 960)
 if character_present:teacher(im,t,PCM[mode],False)
 if character_present and meta['lead']<=t<meta['speech_end']:bubble(im,meta['text'],t-meta['lead'],meta['speech_end']-meta['lead'])
 art=TITLES[mode];im.paste(art,(16,14),art)
 q=E((t-(meta['duration']-.65))/.65)
 if q:im=Image.blend(im,target,q)
 if not character_present and meta['lead']<=t<meta['speech_end']:o.subtitle(im,meta['text'])
 return im
def extract(src,t):
 a=subprocess.check_output([FF,'-v','error','-ss',str(t),'-i',str(src),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-']);assert len(a)==1920*1080*3;return Image.frombytes('RGB',(1920,1080),a)
def encode(name,duration,audio,render):
 out=ROOT/'.build'/f'{name}.mp4';count=math.ceil(duration*24)
 proc=subprocess.Popen([FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(audio),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 audit=[]
 for i in range(count):
  global AUDIT
  AUDIT=[];im=render(i/24);audit.append(dict(t=i/24,objects=list(AUDIT)));proc.stdin.write(im.tobytes())
  if i in (12,count//2,count-3):im.save(ROOT/'检查'/f'{name}_{i}.png')
 proc.stdin.close();err=proc.stderr.read();assert proc.wait()==0,err;manager.decode(out)
 (ROOT/'检查'/f'{name}_边界.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8');print('Rendered',name,round(duration,2),flush=True);return out
def reminder(mode,key,start,end):
 src=ROOT/'.build'/f'原片_{key}.mp4';target=extract(src,end+.02)
 ImageDraw.Draw(target).rectangle((0,958,1920,1080),fill='#244b60')
 # The original title is already docked at this frame; no central seal remains in the target.
 return encode('串讲_'+mode,M[mode]['duration'],M[mode]['path'],lambda t:intro(t,mode,target))
def quiz_frame(t,pcm,qstart,astart,hold,show_bubble=True):
 # Let the completed geomorphology diagram breathe before the mascot returns.
 if t<hold:
  im=q8.process(q8.row('收束')['end']+t,True);im.paste(q8.TITLE,(16,14),q8.TITLE);return im
 age=t-hold;ret=M['回场'];question=S8['lines'][-2];answer=S8['lines'][-1]
 if age<ret['duration']:
  # The post-lesson recap is the matching board, not a repeat of the rejected five-card overview.
  ready=quiz_frame(qstart+.001,pcm,qstart,astart,hold,False)
  im=o.m.BG.copy();im.paste(ready.crop((452,215,1880,940)),(452,215));teacher(im,age,pcm[round(hold*24000):],True)
  if ret['lead']<=age<ret['speech_end']:bubble(im,ret['text'],age-ret['lead'],ret['speech_end']-ret['lead'])
  im.paste(RECAP,(16,14),RECAP)
  # Recap cards dissolve as a group before the matching task appears; the teacher stays planted.
  fade=E((age-(ret['duration']-.5))/.5)
  if fade:im=Image.blend(im,quiz_frame(qstart+.001,pcm,qstart,astart,hold,False),fade)
  return im
 im=o.m.BG.copy();d=ImageDraw.Draw(im);d.rounded_rectangle((452,215,1880,940),24,fill=CREAM,outline='#abc7ce',width=2)
 o.txt(im,'按讲解重点，把案例与要素相连',1160,246,59,INK,True)
 for i,s in enumerate(q8.CASES):
  y=355+i*112;d.rounded_rectangle((495,y,1035,y+83),16,fill='#e7eff0',outline='#adc6ce',width=2);o.txt(im,s,765,y+15,54,INK,True)
 for i,s in enumerate(q8.ANSWERS):
  y=355+i*112;d.rounded_rectangle((1500,y,1800,y+83),16,fill='#f3eadb',outline='#c8c5af',width=2);o.txt(im,s,1650,y+15,54,INK,True)
 pause=qstart+(question['end']-question['start']);thinking=pause<=t<astart
 if t>=astart:
  for i,j in enumerate(q8.MATCH):
   progress=E((t-astart-i*.52)/.45)
   if progress:q8.arrow(im,q8.V.cubic((1048,396+i*112),(1230,396+i*112),(1310,396+j*112),(1482,396+j*112),65),BLUE if t-astart-i*.52<.8 else '#9dbdc7',6,progress)
 if thinking:
  overlay=Image.new('RGBA',im.size);ImageDraw.Draw(overlay).rounded_rectangle((452,215,1880,940),24,fill=(22,51,66,100));im=Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB');d=ImageDraw.Draw(im)
  d.ellipse((1150,523,1350,723),fill=CREAM,outline='#b5cbd1',width=4);o.txt(im,str(3-int(t-pause)),1250,560,105,BLUE,True)
 teacher(im,t,pcm,thinking=thinking,feedback=t>astart+(answer['speech_end']-answer['start']))
 if show_bubble and qstart<=t<pause:bubble(im,question['text'],t-qstart,question['speech_end']-question['start'])
 if astart<=t<astart+answer['speech_end']-answer['start']:bubble(im,answer['text'],t-astart,answer['speech_end']-answer['start'])
 im.paste(q8.QUIZ,(16,14),q8.QUIZ);return im
def quiz_clip():
 old=read_pcm(P/'第八段_地形与配对/配音/第八段_晓伊.wav');question=S8['lines'][-2];answer=S8['lines'][-1];hold=1.1
 q=old[round(question['start']*24000):round(question['end']*24000)];a=old[round(answer['start']*24000):]
 pcm=np.concatenate([np.zeros(round(hold*24000),dtype='<i2'),PCM['回场'],q,np.zeros(72000,dtype='<i2'),a]);audio=ROOT/'配音/地形收束与企鹅互动.wav';wav(audio,pcm)
 qstart=hold+M['回场']['duration'];astart=qstart+len(q)/24000+3
 meta=dict(hold=hold,return_start=hold,question_start=qstart,countdown_start=astart-3,answer_start=astart,duration=len(pcm)/24000)
 (ROOT/'地形回场时轴.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
 return encode('地形收束与企鹅互动',len(pcm)/24000,audio,lambda t:quiz_frame(t,pcm,qstart,astart,hold))
def splice(key,events):
 src=ROOT/'.build'/f'原片_{key}.mp4';args=[FF,'-v','error','-y','-i',str(src)];graph=[];pieces=[];cursor=0
 source_seconds=manager.info(src)['seconds']
 for e in events:args+=['-i',str(e['clip'])]
 for i,e in enumerate(events+[None]):
  end=e['start'] if e else None
  if (end is None and cursor<source_seconds-.02) or (end is not None and end>cursor+.0001):
   tag=f's{i}';v=f'trim=start={cursor}'+(f':end={end}' if end is not None else '');a=f'atrim=start={cursor}'+(f':end={end}' if end is not None else '')
   graph.extend([f'[0:v]{v},setpts=PTS-STARTPTS,fps=24,setsar=1[{tag}v]',f'[0:a]{a},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[{tag}a]']);pieces.append(tag)
  if e:
   tag=f'n{i}';graph.extend([f'[{i+1}:v]setpts=PTS-STARTPTS,setsar=1[{tag}v]',f'[{i+1}:a]asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[{tag}a]']);pieces.append(tag);cursor=e['end']
 graph.append(''.join(f'[{p}v][{p}a]' for p in pieces)+f'concat=n={len(pieces)}:v=1:a=1[joined][a]');graph.append('[joined]fps=24,setpts=N/(24*TB)[v]')
 out=ROOT/'交付'/f'{key}.mp4';args+=['-filter_complex',';'.join(graph),'-map','[v]','-map','[a]','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)]
 subprocess.run(args,check=True);manager.decode(out);print('Updated',key,manager.info(out)['seconds'],flush=True);return out
def main():
 events={k:[] for k in KEYS}
 # Part five's inserted center title during the original board push is replaced with native fixed-title frames.
 start=o.CUT+2.3+2;end=start+2;src=ROOT/'.build/原片_05_环境多米诺_水.mp4';aud=ROOT/'配音/原推板两秒.wav'
 subprocess.run([FF,'-v','error','-y','-ss',str(start),'-i',str(src),'-t','2','-ar','24000','-ac','1',str(aud)],check=True)
 clip=encode('推板固定左上标题',2,aud,lambda t:o.render5(start-2+t));events[KEYS[0]].append(dict(start=start,end=end,clip=clip,kind='推板标题固定'))
 # Source event 832/24 plus the preceding two-second chapter card.
 specs=[('水',KEYS[0],832/24+2),('气',KEYS[1],S6['title_intro_start']),('生',KEYS[2],0),('土',KEYS[2],S7['intros'][1]['start']),('地形',KEYS[3],0)]
 for mode,key,start in specs:
  clip=reminder(mode,key,start,start+2);events[key].append(dict(start=start-.7 if mode=='水' else start,end=start+2,clip=clip,kind='企鹅串讲_'+mode))
 clip=quiz_clip();events[KEYS[3]].append(dict(start=S8['intros'][1]['start'],end=DATA['segments'][KEYS[3]]['seconds']+.04,clip=clip,kind='地形停留与企鹅回场'))
 paths={}
 for key in KEYS:paths[key]=str(splice(key,sorted(events[key],key=lambda a:a['start'])))
 (ROOT/'替换事件.json').write_text(json.dumps({k:[dict(e,clip=str(e['clip'])) for e in v] for k,v in events.items()},ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'待发布.json').write_text(json.dumps(paths,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':
 if DATA.get('single_card_full_engine'):raise RuntimeError('旧五牌串讲入口停用；使用apply_single_cards.py应用单张出牌规则。')
 main()
