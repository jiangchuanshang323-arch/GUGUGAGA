"""Render and validate the authorized 45-second paper-watercolor restyle."""
from pathlib import Path
import hashlib,json,runpy,re
import build_video as v
from refine_scene import install

R=v.R;Q=R/'检查/纸本水彩';Q.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources=[R/'台词与时间轴.json',R/'配音/中国影响45秒.wav']
sources += [R/'素材'/n for n in ['中国轮廓参考.json','中国省界参考.json','ne_50m_rivers_lake_centerlines.geojson','长江主河道_核实.geojson','长江显示河道_海岸收束.geojson','1998长江洪水_原图.jpg','企鹅_双翅握伞杆.png','企鹅_扇风.png','企鹅_围巾怕冷表情.png']]
before={str(p.relative_to(R)):sha(p) for p in sources}
old=sha(v.OUT)
(Q/'内容保持基线.json').write_text(json.dumps(dict(previous_video=old,immutable_sources=before),ensure_ascii=False,indent=2),encoding='utf-8')
install(v)
assert v.REFINED.in_mainland(*v.REFINED.shore_clip['render_end'])
assert not v.REFINED.in_mainland(*v.REFINED.shore_clip['removed_next_point'])
v.main()
runpy.run_path(str(R/'check_video.py'),run_name='__main__')
after={str(p.relative_to(R)):sha(p) for p in sources};assert after==before
report=json.loads((R/'检查/独立复核.json').read_text(encoding='utf-8'))
report.update(art_direction='ivory paper, scanned blue watercolor, ochre land, brush title and handwritten notes',narration_and_timeline='unchanged byte for byte',geography_and_river_sources='unchanged byte for byte',weather_actor_assets='unchanged byte for byte',geographic_shore_clip=v.REFINED.shore_clip,visual_review='encoded-frame review pending',imagegen_asset='texture only, no map or characters',whole_course_remerged=False)
(Q/'成片验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
html=v.OUT.parent/'播放视频.html';s=html.read_text(encoding='utf-8');s=re.sub(r'china_impact_playback\.mp4\?rev=[a-f0-9]+','china_impact_playback.mp4?rev='+report['sha256'][:12],s);html.write_text(s,encoding='utf-8')
print('PAPER_DELIVERED',v.OUT,report['sha256'],flush=True)
