from pathlib import Path
import importlib.util,json,math,subprocess,hashlib,sys
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;P=ROOT.parent
s=importlib.util.spec_from_file_location('single_card_components',ROOT/'build_transitions.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
mode='气' if '--air' in sys.argv else '水';character_present=b.CHARACTER_PRESENT_AT_CARD_START[mode]
if mode=='水':
 row=next(r for r in b.o.m.DATA if r['mode']=='选水');source_pcm=b.o.m.PCM
else:
 air=b.module('air_preview',P/'第六段_水收束与气/build_segment.py');row=next(r for r in air.ROWS if r['mode']=='气');source_pcm=b.read_pcm(P/'第六段_水收束与气/配音/第六段_晓伊.wav')
speech=source_pcm[round(row['start']*24000):round(row['speech_end']*24000)]
lead=.35;tail=.55;pcm=np.concatenate([np.zeros(round(lead*24000),dtype='<i2'),speech,np.zeros(round(tail*24000),dtype='<i2')])
wav=ROOT/'配音'/f'单张{mode}牌_复用原讲解.wav';b.wav(wav,pcm);duration=len(pcm)/24000
# The first clause introduces the card. The card starts fading only after the explanation has begun.
fade_start=lead+len(speech)/24000*.60;fade_end=fade_start+.75
body_at=next(r['start'] for r in b.o.NEW if r['mode']=='全球')
native_global=dict(zip(b.o.render5.__code__.co_freevars,(c.cell_contents for c in b.o.render5.__closure__)))['global_scene']
def render(t):
 if mode=='水':
  target=native_global('全球',body_at+max(0,t-fade_start));b.o.header(target,'第一张·水','环流变化 → 降水重分配 → 水循环响应')
 else:target=air.energy_scene(row['start']+max(0,t-lead),row)
 if t>=fade_end:
  if lead<=t<lead+len(speech)/24000:b.o.subtitle(target,row['text'])
  return target
 im=b.cards(t,b.WORDS.index(mode),center_x=1135 if character_present else 960)
 if character_present:b.teacher(im,t,pcm,False)
 if character_present and lead<=t<lead+len(speech)/24000:b.bubble(im,row['text'],t-lead,len(speech)/24000)
 im.paste(b.TITLES[mode],(16,14),b.TITLES[mode])
 q=b.E((t-fade_start)/(fade_end-fade_start))
 if q:
  # No bottom captions while the character is still visible in the dissolve.
  ImageDraw.Draw(target).rectangle((0,958,1920,1080),fill='#244b60');im=Image.blend(im,target,q)
 if not character_present and lead<=t<lead+len(speech)/24000:b.o.subtitle(im,row['text'])
 return im
clip=b.encode(f'单张牌_{mode}_短样片',duration,wav,render)
dest=P/'demooo/预览/单张多米诺牌'/f'单张多米诺牌_{mode}.mp4';dest.parent.mkdir(parents=True,exist_ok=True);b.manager.copy_exact(clip,dest)
times=[.8,1.8,fade_start+.02,fade_start+.45,fade_end+.1,duration-.65]
contact=Image.new('RGB',(1440,580),'#e5eeee');d=ImageDraw.Draw(contact)
for i,t in enumerate(times):
 im=b.extract(dest,t);x=i%3*480;y=i//3*290;contact.paste(im.resize((480,270)),(x,y));d.text((x+8,y+273),f'{t:.2f}s',fill='#244b60');im.save(ROOT/'检查'/f'单张{mode}牌_实际_{i}.png')
contact.save(ROOT/'检查'/f'单张{mode}牌_实际编码.jpg')
data=json.loads(b.manager.MANIFEST.read_text(encoding='utf-8'));key='单张多米诺牌' if mode=='水' else '单张多米诺牌_气';data['previews'][key]={'path':str(dest.relative_to(b.manager.ROOT)),**b.manager.info(dest),'description':'只出现当前牌；沿用前一镜角色状态，开始讲解后淡去；复用原配音；正式段暂未重新渲染'};b.manager.write_manifest(data)
report=dict(output=str(dest),**b.manager.info(dest),fade_start=fade_start,fade_end=fade_end,single_card_count=1,character_present=character_present,bubble_baseline='shared ls anchor',narration=row['text'],new_voice=False,title_static=True,formal_segments_unchanged=True,decode='PASS',visual_review='待抽查')
(ROOT/f'单张牌样片_{mode}_验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False),flush=True)
