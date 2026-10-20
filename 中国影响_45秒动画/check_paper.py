"""Post-encode semantic/motion audit against the previous approved 45s version."""
from pathlib import Path
import io,json,subprocess
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parent;Q=R/'检查/纸本水彩'
P=R.parent;OUT=P/'demooo/预览/中国影响全屏动画/海洋发烧了_中国影响全屏动画小样.mp4'
FF=P/'ocean_animation_demo_20261011/runtime/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
old=json.loads((Q/'动作与台词基线.json').read_text(encoding='utf-8'))
new=json.loads((R/'检查/逐帧对象与文字.json').read_text(encoding='utf-8'))
assert len(old)==len(new)==1080
for a,b in zip(old,new):
 objs=b['objects'];texts=sorted(set(o['text'] for o in objs if o['kind']=='text'))
 motion=[o for o in objs if o['kind'] in ['weather_character','typhoon','historical_photo','flood_risk_river_highlight','south_china_sea_inset']]
 assert texts==a['text'],(b['frame'],texts,a['text'])
 assert motion==a['motion'],(b['frame'],motion,a['motion'])
 assert any(o['kind']=='subtitle' for o in objs)==a['subtitle']

def frame(t):
 raw=subprocess.run([str(FF),'-v','error','-ss',str(t),'-i',str(OUT),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True,check=True).stdout
 return Image.open(io.BytesIO(raw)).convert('RGB')

diffs=[]
for name,t1,t2,box in [('umbrella/rain',7.65,7.9,(1010,438,1225,738)),('fan',33.15,33.35,(1000,510,1240,738)),('shiver',37.45,37.58,(1015,510,1230,738))]:
 a=np.asarray(frame(t1).crop(box),dtype=np.int16);b=np.asarray(frame(t2).crop(box),dtype=np.int16)
 delta=abs(a-b);mean=float(delta.mean());changed=int(np.count_nonzero(delta.max(axis=2)>12))
 assert mean>.15 and changed>80,(name,mean,changed)
 diffs.append(dict(action=name,times=[t1,t2],mean_pixel_difference=mean,changed_pixels_gt12=changed))
for t in [7.8,10.6,17.5,23,26.4,33.8,37.8,43.7]:frame(t).save(Q/f'编码复核_{t:.2f}.png')
frame(7.8).save(OUT.parent/'纸本水彩_预览.png')
report=json.loads((Q/'成片验证.json').read_text(encoding='utf-8'))
report.update(previous_version_per_frame_teaching_text='identical sets on all 1080 frames',previous_version_per_frame_object_motion='identical tracked objects on all 1080 frames',subtitle_presence='identical on all 1080 frames',encoded_actor_frame_differences=diffs,visual_review='actual encoded key frames extracted; pending human inspection')
(Q/'成片验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(content_and_motion_comparison='PASS: 1080 frames',action_differences=diffs),ensure_ascii=False),flush=True)
