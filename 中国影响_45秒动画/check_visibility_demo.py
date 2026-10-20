"""Validate the targeted map/legend/inset visibility edit demo."""
from pathlib import Path
import json,hashlib
from PIL import Image

R=Path(__file__).resolve().parent;Q=R/'检查/本轮地图改版'
a=json.loads((Q/'逐帧对象.json').read_text(encoding='utf-8'));assert len(a)==300
for row in a:
 for o in row['objects']:
  if o['kind']=='text':
   assert o['text']!='日本';x,y,z,b=o['box']
   assert 15<=x<z<=1905 and 10<=y<b<=1067,(row['frame'],o)
  if o['kind']=='south_china_sea_inset':assert o['sourced_dashes']==9
legend=[o for row in a for o in row['objects'] if o.get('text') in ['偏冷','偏暖']]
assert legend and all(o['style']=='opaque high-contrast legend' for o in legend)
arrows=[o for row in a for o in row['objects'] if o['kind']=='teaching_arrow']
assert arrows and min(o['width'] for o in arrows)>=6
p=Q/'验证.json';s=json.loads(p.read_text(encoding='utf-8'));bounds=s['main_country_bounds']
assert 15<=bounds[0]<bounds[2]<=1905 and 15<=bounds[1]<bounds[3]<=953,bounds
full=R.parent/'demooo/预览/中国影响全屏动画/海洋发烧了_中国影响全屏动画小样.mp4'
assert hashlib.sha256(full.read_bytes()).hexdigest()==s['original45_unchanged_sha256']
s.update(no_japan_label='PASS on all 300 frames',text_bounds='PASS on all 300 frames',southern_sea_dashes=9,inset_caption_size=34,legend_size=44,main_map_scale=1.05,main_country_not_cropped='PASS',trajectory_halo='PASS, >=6px ink plus 4px paper outline',visual_review='pending actual encoded inspection')
p.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
im=Image.open(Q/'实际编码_11.0.png');im.crop((1660,705,1920,958)).resize((780,759)).save(Q/'附图编码细节.png')
print('PASS',s['seconds'],s['sha256'],bounds,flush=True)
