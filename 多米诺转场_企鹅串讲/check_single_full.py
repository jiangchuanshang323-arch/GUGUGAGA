from pathlib import Path
import json,importlib.util,sys,math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;P=ROOT.parent
s=importlib.util.spec_from_file_location('single_check_components',ROOT/'build_transitions.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
r=json.loads((ROOT/'单牌正式_制作清单.json').read_text(encoding='utf-8'))
if '--combined' not in sys.argv:
 tasks=[]
 for item in r['stages']:
  audit=json.loads((ROOT/'检查'/f'正式单牌_{item["mode"]}_边界.json').read_text(encoding='utf-8'))
  assert all(sum(o['kind']=='domino_card' for o in f['objects'])<=1 for f in audit)
  if not item['character_present']:assert all(not any(o['kind'] in ('character','bubble') for o in f['objects']) for f in audit)
  assert all(o.get('baseline_anchor')=='ls' for f in audit for o in f['objects'] if o['kind']=='bubble')
  b.manager.decode(item['clip'])
  for t in [1.3,item['fade_start']+.4,min(item['duration']-.08,item['fade_end']+.25)]:tasks.append((item['mode'],Path(item['clip']),t))
 name='正式单牌_十五节点';columns=5
else:
 report=json.loads((ROOT/'单牌整段_验证.json').read_text(encoding='utf-8'));out=Path(report['output']);sec=report['seconds']
 manifest=json.loads(b.manager.MANIFEST.read_text(encoding='utf-8'));entry=manifest['merges']['环境多米诺_水气生土地形'];offset=-entry['trim_start_seconds'];starts={}
 for key in entry['segments']:starts[key]=offset;offset+=manifest['segments'][key]['seconds']
 events=r['events']
 def mapped(key,t):
  shift=0
  for e in sorted(events[key],key=lambda a:a['start']):
   if e['start']>=t-.001:break
   shift+=b.manager.info(e['clip'])['seconds']-(e['end']-e['start'])
  return starts[key]+t+shift
 card_starts={}
 for key,items in events.items():
  for e in items:
   if e['kind'].startswith('单牌_'):card_starts[e['kind'][3:]]=mapped(key,e['start'])
 marks=[card_starts['水']+.9,5,card_starts['气']+1.2,card_starts['气']+8,card_starts['生']+1.2,card_starts['生']+14,card_starts['土']+1.2,card_starts['土']+15,card_starts['地形']+1.2,card_starts['地形']+15,sec-20,sec-2]
 tasks=[('combined',out,min(sec-.05,t)) for t in marks];name='多米诺整段_十二节点';columns=4
 (ROOT/'整段章节时间.json').write_text(json.dumps(dict(segments_start=starts,card_starts=card_starts,trim=entry['trim_start_seconds'],duration=sec),ensure_ascii=False,indent=2),encoding='utf-8')
contact=Image.new('RGB',(columns*480,math.ceil(len(tasks)/columns)*290),'#e5eeee');d=ImageDraw.Draw(contact)
for i,(label,path,t) in enumerate(tasks):
 im=b.extract(path,t);x=i%columns*480;y=i//columns*290;contact.paste(im.resize((480,270)),(x,y));d.text((x+8,y+273),f'{i:02d} {t:.2f}s',fill='#244b60');im.save(ROOT/'检查'/f'{name}_{i:02d}.png')
contact.save(ROOT/'检查'/f'{name}.jpg');print('CHECK READY',name,flush=True)
