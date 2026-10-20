"""Verify and register full-length promotion of the visibility edit."""
from pathlib import Path
import hashlib,json,re,runpy
R=Path(__file__).resolve().parent;Q=R/'检查/本轮地图改版'
runpy.run_path(str(R/'check_video.py'),run_name='__main__')
a=json.loads((R/'检查/逐帧对象与文字.json').read_text(encoding='utf-8'));assert len(a)==1080
for row in a:
 for o in row['objects']:
  if o['kind']=='text':assert o['text']!='日本'
  if o['kind']=='south_china_sea_inset':assert o['sourced_dashes']==9
  if o['kind']=='teaching_arrow':assert o['width']>=6 and o['halo']>=o['width']+4
legend=[o for row in a for o in row['objects'] if o.get('text') in ['偏冷','偏暖']]
assert legend and all(o['style']=='opaque high-contrast legend' for o in legend)
baseline=json.loads((R/'检查/纸本水彩/内容保持基线.json').read_text(encoding='utf-8'))['immutable_sources']
for rel,h in baseline.items():assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==h,rel
report=json.loads((R/'检查/独立复核.json').read_text(encoding='utf-8'))
report.update(no_japan_label='PASS on all 1080 frames',sourced_south_sea_dashes=9,inset_caption_size=34,legend_size=44,arrow_halo='>=6px ink, plus 4px paper',main_map_scale=1.05,regional_final_scale=2,unchanged_narration_timeline_assets='all hashes match prior 45s',visual_review='pending actual encoded montage review')
(Q/'完整45秒验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
html=R.parent/'demooo/预览/中国影响全屏动画/播放视频.html'
s=html.read_text(encoding='utf-8');s=re.sub(r'china_impact_playback\.mp4\?rev=[a-f0-9]+','china_impact_playback.mp4?rev='+report['sha256'][:12],s);html.write_text(s,encoding='utf-8')
print('FULL45_VISIBILITY_PASS',report['sha256'],flush=True)
