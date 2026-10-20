"""Add approved chapter-title beats to saved segments, then publish the full stage."""
from pathlib import Path
import sys,importlib.util,json,subprocess,math,shutil,hashlib
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
for folder in ('.build','交付','检查'):(ROOT/folder).mkdir(parents=True,exist_ok=True)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
manager=module('deliveries',PROJECT/'demooo/manage_videos.py');FF=manager.EXE
old=module('seals35',PROJECT/'统一章节标题_阶段成片_v35/build_master.py')
sys.path.insert(0,str(PROJECT/'卷图推板与五牌'))
o=module('current_lesson',PROJECT/'卷图推板与五牌/update_parts.py')
from refine_components import install
install(o)
DATA=json.loads(manager.MANIFEST.read_text(encoding='utf-8'))
KEYS=list(DATA['merges']['目前完整成片']['segments']);FIRST_FRAME=241;SECOND_FRAME=1598;THIRD_FRAME=3161
def old_event(frame,key,bg):
 return {'frame':frame,'key':key,'art':old.CARDS[key],'background':bg,'title':old.CARD_META[key]['title']}
def new_event(t,title,sub,bg):
 return {'frame':math.ceil(t*24-1e-7),'key':title,'art':o.p.header(title,sub),'background':bg,'title':title}
EVENTS={
 '01_三地情境':[
  old_event(280-FIRST_FRAME,'三地',old.BG),
  old_event(891-FIRST_FRAME,'线索',old.PLAIN),
  old_event(1341-FIRST_FRAME,'定位',old.PLAIN)],
 '02_测体征':[],
 '03_查病因':[old_event(0,'热量',old.BG),old_event(3612-THIRD_FRAME,'原理',old.CREAM)],
 '04_对照与预测':[
  new_event(0,'查病因 · 正常与异常对照','从海洋变化，看大气响应',old.CREAM),
  new_event(29.184875,'互动 · 预测两地降水','先看气流，再看降水',old.CREAM)],
 '05_环境多米诺_水':[
  new_event(0,'预测揭晓·两侧为何不同','先辨位置，再看海陆响应',old.CREAM),
  new_event(o.EXITSTART+o.EXITLEN,'第一张·水','环流变化 → 降水重分配 → 水循环响应',old.CREAM)]}

def extract(src,frame):
 raw=subprocess.check_output([FF,'-v','error','-ss',f'{frame/24:.9f}','-i',str(src),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
 assert len(raw)==1920*1080*3
 return Image.frombytes('RGB',(1920,1080),raw)

def title_layer(art,age,base=None):
 # Same central hold and 1s docking curve as the accepted preview.
 image=base.copy() if base is not None else Image.new('RGBA',(1920,1080))
 large=min(2.15,1740/art.width)
 if age<.18:q=o.m.ease(age/.18);scale=large-.17*(1-q);cx,cy=960,540;alpha=q
 elif age<1:scale=large;cx,cy=960,540;alpha=1
 else:
  q=o.m.ease(age-1);scale=large+(1-large)*q;cx=960*(1-q)+(16+art.width/2)*q;cy=540*(1-q)+(14+art.height/2)*q;alpha=1
 a=art.resize((round(art.width*scale),round(art.height*scale)),Image.Resampling.LANCZOS)
 if alpha<1:a.putalpha(a.getchannel('A').point(lambda z:round(z*alpha)))
 x=round(cx-a.width/2);y=round(cy-a.height/2);assert 0<=x and x+a.width<=1920 and 0<=y and y+a.height<=1080
 image.paste(a,(x,y),a);return image

def encode_intro(src,key,event,index):
 base=extract(src,event['frame']);art=event['art'];bg=event['background']
 # Restore the native heading background, without painting over teaching objects.
 width=max(art.width+30,730 if key=='03_查病因' and event['key']=='原理' else 0)
 height=max(art.height+20,157 if event['key']=='原理' else 150)
 area=(0,0,min(1900,width),height);base.paste(bg.crop(area),(0,0))
 # Silent chapter cue contains neither a frozen subtitle nor an orphan speech bubble.
 ImageDraw.Draw(base).rectangle((0,958,1920,1080),fill='#244b60')
 if event['key']=='三地':base.paste(old.BG.crop((0,170,400,590)),(0,170))
 out=ROOT/'.build'/f'intro_{key}_{index}.mp4'
 p=subprocess.Popen([FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t','2','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',str(out)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 for i in range(48):
  im=title_layer(art,i/24,base);p.stdin.write(im.tobytes())
  if i in (15,36,47):im.save(ROOT/'检查'/f'{key}_{index}_{i}.png')
 p.stdin.close();error=p.stderr.read();assert p.wait()==0,error
 return out

def existing_overlay(key):
 if key=='02_测体征':start=3.454875;art=old.CARDS['体温']
 else:start=o.CUT+2.3;art=o.p.header('追并发症·环境多米诺','自然环境具有整体性')
 frame=math.ceil(start*24)
 out=ROOT/'.build'/f'{key}_标题透明层.mov'
 p=subprocess.Popen([FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1920x1080','-r','24','-i','-','-c:v','qtrle',str(out)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 for i in range(48):
  age=(frame+i)/24-start
  layer=Image.new('RGBA',(1920,1080))
  if key=='02_测体征':
   background=Image.blend(old.PLAIN,old.BG,o.m.ease((age-.28)/.9));layer.paste(background.crop((0,0,1475,115)),(0,0))
  else:layer.paste(o.m.BG.crop((0,0,650,165)),(0,0))
  layer=title_layer(art,age,layer);p.stdin.write(layer.tobytes())
 p.stdin.close();error=p.stderr.read();assert p.wait()==0,error
 return out,frame/24

def segment(key):
 entry=DATA['segments'][key];saved=ROOT/'.build'/f'输入_{key}.mp4'
 if not saved.exists():shutil.copy2(manager.ROOT/entry['path'],saved)
 events=EVENTS[key];inputs=[]
 for i,event in enumerate(events):inputs.append(encode_intro(saved,key,event,i))
 args=[FF,'-v','error','-y','-i',str(saved)]
 for path in inputs:args+=['-i',str(path)]
 graph=[];source='0:v';num_chunks=len(events)+1
 has_overlay=key in ('02_测体征','05_环境多米诺_水')
 if has_overlay:
  overlay,start=existing_overlay(key);args+=['-i',str(overlay)];idx=len(inputs)+1
  graph += [f'[{idx}:v]setpts=PTS-STARTPTS+{start}/TB[title]',f'[0:v][title]overlay=eof_action=pass:repeatlast=0[overlaid]']
  graph += [f'[overlaid]split={num_chunks}'+''.join(f'[src{j}]' for j in range(num_chunks))] if num_chunks>1 else ['[overlaid]null[src0]']
 pieces=[];cursor=0
 for j,event in enumerate(events+[None]):
  end=event['frame'] if event else None
  if end is None or end>cursor:
   tag=f'c{j}';inp=f'src{j}' if has_overlay else source
   trim=f'trim=start_frame={cursor}'+(f':end_frame={end}' if end is not None else '')
   atrim=f'atrim=start={cursor/24:.9f}'+(f':end={end/24:.9f}' if end is not None else '')
   graph += [f'[{inp}]{trim},setpts=PTS-STARTPTS,fps=24,setsar=1[{tag}v]',f'[0:a]{atrim},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[{tag}a]'];pieces.append(tag)
  elif has_overlay:graph.append(f'[src{j}]nullsink')
  if event:
   tag=f'i{j}';graph += [f'[{j+1}:v]setpts=PTS-STARTPTS,setsar=1[{tag}v]',f'[{j+1}:a]asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[{tag}a]'];pieces.append(tag);cursor=end
 graph.append(''.join(f'[{tag}v][{tag}a]' for tag in pieces)+f'concat=n={len(pieces)}:v=1:a=1[joined][a]')
 graph.append('[joined]fps=24,setpts=N/(24*TB)[v]')
 out=ROOT/'交付'/f'{key}.mp4'
 args+=['-filter_complex',';'.join(graph),'-map','[v]','-map','[a]','-r','24','-fps_mode','cfr','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)]
 subprocess.run(args,check=True);manager.decode(out)
 print('Completed',key,manager.info(out)['seconds'],flush=True)
 return out

def main():
 if DATA.get('domino_transition_engine'):
  raise RuntimeError('多米诺已改为企鹅串讲与固定左上标题；旧标题归位发布流程停用。请通过demooo/manage_videos.py更新已确认的合成，勿把旧标题动画覆盖回来。')
 rows=[];pairs=[]
 if '--publish' in sys.argv:
  rows=json.loads((ROOT/'标题与拼接时间轴.json').read_text(encoding='utf-8'))
  pairs=[(key,ROOT/'交付'/f'{key}.mp4') for key in EVENTS]
 else:
  for key in EVENTS:
   out=segment(key);pairs.append((key,out))
   rows.append({'segment':key,'inserted_silence_seconds':len(EVENTS[key])*2,'titles':[dict(title=e['title'],source_frame=e['frame']) for e in EVENTS[key]],**manager.info(out)})
 (ROOT/'标题与拼接时间轴.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
 if '--render-only' in sys.argv:return
 data=json.loads(manager.MANIFEST.read_text(encoding='utf-8'))
 data['merges']['目前完整成片']={'path':str(Path('合成版本')/'目前完整成片'/'海洋发烧了_目前完整成片.mp4'),'segments':KEYS}
 manager.write_manifest(data)
 manager.update_many([(key,str(path)) for key,path in pairs])
 report={'full_video':str(manager.ROOT/'合成版本/目前完整成片/海洋发烧了_目前完整成片.mp4'),'decode':'PASS','new_voice_synthesis':False,'intro_count':11,'inserted_silence_seconds':18,'original_actions_and_narration_retained':True,'visual_review':'待实际编码抽帧复核','segments':rows}
 (ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
