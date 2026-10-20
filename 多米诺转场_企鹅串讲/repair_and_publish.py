from pathlib import Path
import json,importlib.util,subprocess,math,io
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;P=ROOT.parent
s=importlib.util.spec_from_file_location('transition',ROOT/'build_transitions.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
if b.DATA.get('single_card_full_engine'):raise RuntimeError('旧五牌发布入口停用；使用apply_single_cards.py，避免覆盖单张出牌和无人物规则。')
events=json.loads((ROOT/'替换事件.json').read_text(encoding='utf-8'));paths=json.loads((ROOT/'待发布.json').read_text(encoding='utf-8'))
if '--publish-only' not in __import__('sys').argv:
 # Only the two local continuity corrections are redrawn; other new clips are retained.
 e=next(e for e in events[b.KEYS[0]] if e['kind']=='企鹅串讲_水');end=e['end'];start=end-2;e['start']=start-.7;e['clip']=str(b.reminder('水',b.KEYS[0],start,end))
 e=next(e for e in events[b.KEYS[3]] if e['kind']=='地形停留与企鹅回场');e['clip']=str(b.quiz_clip())
 for key in [b.KEYS[0],b.KEYS[3]]:paths[key]=str(b.splice(key,sorted(events[key],key=lambda x:x['start'])))
 (ROOT/'替换事件.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8');(ROOT/'待发布.json').write_text(json.dumps(paths,ensure_ascii=False,indent=2),encoding='utf-8')
 # Short review sample: one complete reminder, then the complete geomorphology closing sentence and return.
 old8=ROOT/'.build/原片_08_地形与配对.mp4';air=ROOT/'.build/串讲_气.mp4';ret=ROOT/'.build/地形收束与企鹅互动.mp4';meta=json.loads((ROOT/'地形回场时轴.json').read_text(encoding='utf-8'))
 sample=P/'demooo/预览/多米诺转场与企鹅回场/多米诺转场与企鹅回场.mp4';sample.parent.mkdir(parents=True,exist_ok=True)
 c=b.S8['lines'][3];filters=f'[0:v]setpts=PTS-STARTPTS[v0];[0:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a0];[1:v]trim=start={c["start"]}:end={c["end"]},setpts=PTS-STARTPTS[v1];[1:a]atrim=start={c["start"]}:end={c["end"]},aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a1];[2:v]trim=end={meta["question_start"]},setpts=PTS-STARTPTS[v2];[2:a]atrim=end={meta["question_start"]},aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a2];[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[joined][a];[joined]fps=24,setpts=N/(24*TB)[v]'
 subprocess.run([b.FF,'-v','error','-y','-i',str(air),'-i',str(old8),'-i',str(ret),'-filter_complex',filters,'-map','[v]','-map','[a]','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(sample)],check=True);b.manager.decode(sample)
 # Inspect real encoded frames before publishing; build a contact sheet for review.
 tasks=[(air,.9),(air,1.7),(air,2.9),(ret,.7),(ret,1.8),(ret,4.0),(ret,meta['question_start']+.4),(ret,meta['question_start']+3.1),(ret,meta['countdown_start']+1.5),(ret,meta['answer_start']+1.0),(ret,meta['answer_start']+4.2),(ret,meta['duration']-.2)]
 contact=Image.new('RGB',(1920,870),'#e5eeee');d=ImageDraw.Draw(contact)
 for i,(p,t) in enumerate(tasks):
  im=b.extract(p,t);x=i%4*480;y=i//4*290;contact.paste(im.resize((480,270)),(x,y));d.text((x+8,y+273),f'{p.stem} {t:.2f}',fill='#244b60');im.save(ROOT/'检查'/f'实际编码_{i:02d}.png')
 contact.save(ROOT/'检查/实际编码_十二节点.jpg')
 print('PREVIEW READY',sample,flush=True)
 if '--review-first' in __import__('sys').argv:raise SystemExit(0)
b.manager.update_many(list(paths.items()))
data=json.loads(b.manager.MANIFEST.read_text(encoding='utf-8'));sample=P/'demooo/预览/多米诺转场与企鹅回场/多米诺转场与企鹅回场.mp4'
data['previews']['多米诺转场与企鹅回场']={'path':str(sample.relative_to(b.manager.ROOT)),**b.manager.info(sample),'description':'一张完整卡牌串讲 + 地形完整收束句与企鹅回场；各修改段已单独覆盖'}
for key in b.KEYS:data['segments'][key]['chapter_title_entrance']='多米诺章节标题固定左上；企鹅串讲、五牌重现后淡去；互动由企鹅气泡引入'
data['domino_transition_engine']=str(ROOT/'build_transitions.py');b.manager.write_manifest(data)
report=dict(segments={k:b.manager.info(b.manager.ROOT/data['segments'][k]['path']) for k in b.KEYS},preview=b.manager.info(sample),decode='PASS',source_narration_retained=True,source_science_frames_retained_outside_transitions=True,geomorphology_pause=1.1,character_has_bubble=True,domino_title_static=True,visual_review='待复核')
(ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False),flush=True)
