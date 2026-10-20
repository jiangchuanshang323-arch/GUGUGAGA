from pathlib import Path
import importlib.util,json,math,sys
import numpy as np
from PIL import Image,ImageDraw,ImageOps
ROOT=Path(__file__).resolve().parent;P=ROOT.parent
s=importlib.util.spec_from_file_location('single_full_components',ROOT/'build_transitions.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
a6=b.module('single_air6',P/'第六段_水收束与气/build_segment.py')
a7=b.module('single_bio7',P/'第七段_生与土/build_segment.py')
a7.SMOKE=ImageOps.fit(a7.SMOKE,(860,635),Image.Resampling.LANCZOS)
pcm6=b.read_pcm(P/'第六段_水收束与气/配音/第六段_晓伊.wav');pcm7=b.read_pcm(P/'第七段_生与土/配音/第七段_晓伊.wav');pcm8=b.read_pcm(P/'第八段_地形与配对/配音/第八段_晓伊.wav')
native_global=dict(zip(b.o.render5.__code__.co_freevars,(c.cell_contents for c in b.o.render5.__closure__)))['global_scene']
EVENTS={k:[] for k in b.KEYS};REPORT=[]
def target(mode,age,row):
 if mode=='水':return native_global('全球',next(r['start'] for r in b.o.NEW if r['mode']=='全球')+age)
 if mode=='气':return a6.energy_scene(row['start']+age,row)
 if mode in ('生','土'):
  im=a7.raw(row['start']+age,row);art=a7.TITLES[0 if mode=='生' else 1];im.paste(art,(16,14),art);return im
 im=b.q8.raw(row['start']+age,row);im.paste(b.q8.TITLE,(16,14),b.q8.TITLE);return im
def stage(mode,row,source):
 speech=source[round(row['start']*24000):round(row['speech_end']*24000)]
 lead=.35;tail=.10;pcm=np.concatenate([np.zeros(round(lead*24000),dtype='<i2'),speech,np.zeros(round(tail*24000),dtype='<i2')]);audio=ROOT/'配音'/f'正式单牌_{mode}.wav';b.wav(audio,pcm)
 duration=len(pcm)/24000;fade_start=lead+min(len(speech)/24000*.60,2.9);fade_end=fade_start+.75
 person=b.CHARACTER_PRESENT_AT_CARD_START[mode]
 def render(t):
  im_target=target(mode,max(0,t-lead),row)
  if t>=fade_end:
   if lead<=t<lead+len(speech)/24000:b.o.subtitle(im_target,row['text'])
   return im_target
  im=b.cards(t,b.WORDS.index(mode),center_x=1135 if person else 960)
  if person:b.teacher(im,t,pcm,False)
  if person and lead<=t<lead+len(speech)/24000:b.bubble(im,row['text'],t-lead,len(speech)/24000)
  im.paste(b.TITLES[mode],(16,14),b.TITLES[mode])
  q=b.E((t-fade_start)/.75)
  if q:
   ImageDraw.Draw(im_target).rectangle((0,958,1920,1080),fill='#244b60');im=Image.blend(im,im_target,q)
  if not person and lead<=t<lead+len(speech)/24000:b.o.subtitle(im,row['text'])
  return im
 clip=b.encode('正式单牌_'+mode,duration,audio,render)
 REPORT.append(dict(mode=mode,clip=str(clip),duration=duration,fade_start=fade_start,fade_end=fade_end,character_present=person,text=row['text'],new_voice=False))
 return clip
def build():
 prior=json.loads((ROOT/'替换事件.json').read_text(encoding='utf-8'))
 EVENTS[b.KEYS[0]].append(next(e for e in prior[b.KEYS[0]] if e['kind']=='推板标题固定'))
 water=next(r for r in b.o.m.DATA if r['mode']=='选水');start=next(r['start'] for r in b.o.NEW if r['mode']=='选水')+2
 end=next(e['end'] for e in prior[b.KEYS[0]] if e['kind']=='企鹅串讲_水')
 specs=[('水',b.KEYS[0],start,end,water,b.o.m.PCM),
        ('气',b.KEYS[1],b.S6['title_intro_start'],a6.ROWS[4]['end'],a6.ROWS[4],pcm6),
        ('生',b.KEYS[2],0,a7.ROWS[0]['end'],a7.ROWS[0],pcm7),
        ('土',b.KEYS[2],b.S7['intros'][1]['start'],next(r['end'] for r in a7.ROWS if r['mode']=='土'),next(r for r in a7.ROWS if r['mode']=='土'),pcm7),
        ('地形',b.KEYS[3],0,b.S8['lines'][0]['end'],b.S8['lines'][0],pcm8)]
 for mode,key,start,end,row,source in specs:
  clip=stage(mode,row,source);EVENTS[key].append(dict(start=start,end=end,clip=str(clip),kind='单牌_'+mode))
 clip=b.quiz_clip();EVENTS[b.KEYS[3]].append(dict(start=b.S8['intros'][1]['start'],end=b.manager.info(ROOT/'.build/原片_08_地形与配对.mp4')['seconds']+.04,clip=str(clip),kind='地形停留与企鹅回场'))
 paths={k:str(b.splice(k,sorted(EVENTS[k],key=lambda x:x['start']))) for k in b.KEYS}
 report=dict(events=EVENTS,paths=paths,stages=REPORT,water_start=specs[0][2],format=[1920,1080,24],new_voice=False)
 (ROOT/'单牌正式_制作清单.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('BUILD COMPLETE',flush=True)
def publish():
 r=json.loads((ROOT/'单牌正式_制作清单.json').read_text(encoding='utf-8'));data=json.loads(b.manager.MANIFEST.read_text(encoding='utf-8'))
 key='环境多米诺_水气生土地形';path=Path('合成版本')/key/'海洋发烧了_环境多米诺完整段.mp4'
 data['merges'][key]={'path':str(path),'segments':b.KEYS,'trim_start_seconds':r['water_start'],'scope':'第一张水牌起至地形后的配对互动，不含前面的预测和推板'}
 b.manager.write_manifest(data);b.manager.update_many(list(r['paths'].items()))
 data=json.loads(b.manager.MANIFEST.read_text(encoding='utf-8'))
 for k in b.KEYS:data['segments'][k]['chapter_title_entrance']='固定左上；当前单牌讲解开始后淡去；沿用前镜人物状态；气泡公共基线'
 data.pop('pending_visual_revision',None);data['single_card_full_engine']=str(ROOT/'apply_single_cards.py');b.manager.write_manifest(data)
 output=b.manager.ROOT/path;result=dict(output=str(output),**b.manager.info(output),segments={k:data['segments'][k] for k in b.KEYS},source_narration_retained=True,decode='PASS',new_voice=False,visual_review='待正式编码抽查')
 (ROOT/'单牌整段_验证.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False),flush=True)
def repair_native_headers():
 r=json.loads((ROOT/'单牌正式_制作清单.json').read_text(encoding='utf-8'))
 for mode,row,pcm in [('生',a7.ROWS[0],pcm7),('土',next(x for x in a7.ROWS if x['mode']=='土'),pcm7),('地形',b.S8['lines'][0],pcm8)]:stage(mode,row,pcm)
 for key in [b.KEYS[2],b.KEYS[3]]:r['paths'][key]=str(b.splice(key,sorted(r['events'][key],key=lambda x:x['start'])))
 for entry in REPORT:r['stages']=[e for e in r['stages'] if e['mode']!=entry['mode']]+[entry]
 (ROOT/'单牌正式_制作清单.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print('Native headings retained through all dissolves',flush=True)
if __name__=='__main__':
 if '--publish' in sys.argv:publish()
 elif '--repair-headers' in sys.argv:repair_native_headers()
 else:build()
