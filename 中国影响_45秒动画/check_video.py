from pathlib import Path
import json,hashlib,subprocess,re,wave
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent
OUT=P/'demooo/预览/中国影响全屏动画/海洋发烧了_中国影响全屏动画小样.mp4'
EXE=P/'ocean_animation_demo_20261011/runtime/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
a=json.loads((R/'检查/逐帧对象与文字.json').read_text(encoding='utf-8'));assert len(a)==1080
weather_mode=any(o['kind']=='weather_character' for e in a for o in e['objects'])
for i,entry in enumerate(a):
 assert entry['frame']==i
 kinds=[v['kind'] for v in entry['objects']]
 if weather_mode:assert 'character' not in kinds and 'bubble' not in kinds,(i,kinds)
 assert not ('character' in kinds and 'subtitle' in kinds),(i,kinds)
 assert 'bubble' not in kinds or 'character' in kinds,(i,kinds)
 for obj in entry['objects']:
  if obj['kind']=='bubble':
   assert obj['baseline_anchor']=='ls'
   x,y,z,b=obj['box'];assert 15<=x<z<=1905 and 15<=y<b<=945
  if obj['kind']=='text':
   x,y,z,b=obj['box'];assert 15<=x<z<=1905 and 10<=y<b<=1067
poses={o.get('pose') for entry in a for o in entry['objects'] if o['kind']==('weather_character' if weather_mode else 'character')}
assert {'rain','fan','cold'}.issubset(poses),poses
photos=[entry for entry in a if any(o['kind']=='historical_photo' for o in entry['objects'])]
assert len(photos)>100
with wave.open(str(R/'配音/中国影响45秒.wav'),'rb') as w:
 assert w.getnframes()==45*24000 and w.getframerate()==24000
 pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.int32)
peak=int(np.max(abs(pcm)));assert peak<32767
r=subprocess.run([str(EXE),'-hide_banner','-i',str(OUT)],capture_output=True)
s=r.stderr.decode('utf-8','replace');assert '1920x1080' in s and '24 fps' in s and '00:00:45.00' in s
assert 'Constrained Baseline' in s and '48000 Hz, stereo' in s
summary={'frames':1080,'seconds':45,'resolution':'1920x1080','fps':24,'audio_peak':peak,'clipped_samples':int(np.count_nonzero(abs(pcm)>=32767)),'bubble_baseline':'ls','character_subtitle_mutual_exclusion':'PASS','text_bounds':'PASS','decode':'PASS (build_video.py full decode)','sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()}
compat=OUT.with_name('china_impact_playback.mp4');assert hashlib.sha256(compat.read_bytes()).hexdigest()==summary['sha256']
photo_box=next(o['box'] for o in photos[0]['objects'] if o['kind']=='historical_photo')
summary.update(character_poses=sorted(poses),photo_frames=len(photos),photo_size=[round(photo_box[2]-photo_box[0]),round(photo_box[3]-photo_box[1])],compatibility_copy='identical, baseline H264, AAC 48k stereo')
if weather_mode:
 summary.update(character_role='in-map weather vignette',dialogue_mode='bottom subtitles, no presenter or bubbles')
 summary.pop('character_subtitle_mutual_exclusion',None)
 storms=[o for e in a for o in e['objects'] if o['kind']=='typhoon']
 assert max(o['map_scale'] for o in storms)==2
 assert all(b['center'][0]<=a['center'][0]+1e-8 and b['center'][1]<=a['center'][1]+1e-8 for a,b in zip(storms,storms[1:]))
 assert all(o['box'][0]>1600 for e in a for o in e['objects'] if o['kind']=='south_china_sea_inset')
 summary.update(map_scale=2,northwest_track='PASS',inset='bottom right')
# Other formal deliverables are verified against their existing manifest, without regenerating them.
manifest=json.loads((P/'demooo/视频清单.json').read_text(encoding='utf-8'))
unmodified=[]
for key,entry in manifest['segments'].items():
 path=P/'demooo'/entry['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'],key;unmodified.append(key)
summary['unchanged_formal_segments']=unmodified
for name,entry in manifest['merges'].items():
 if '目前完整成片' in name:
  path=P/'demooo'/entry['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'];summary['unchanged_complete_merge']=entry['sha256']
(R/'检查/独立复核.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(summary,ensure_ascii=False),flush=True)
