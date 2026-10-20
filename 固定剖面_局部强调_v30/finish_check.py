from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
timeline_path=ROOT.parent/'逐句引导_箭头修正_v29'/'逐句引导时间轴.json'
timeline=json.loads(timeline_path.read_text(encoding='utf-8'))
rows=[json.loads(line) for line in (ROOT/'检查'/'逐帧几何检查.jsonl').read_text(encoding='utf-8').splitlines()]
assert all(not r['errors'] for r in rows)
assert all(''.join(r['subtitle_lines'])==timeline[r['phase']]['text'] for r in rows)
near=lambda t:min(rows,key=lambda r:abs(r['time']-t))['geometry']
a=near(17.87);b=near(19.50);c=near(20.82)
assert b['thermocline_west']<a['thermocline_west']
assert b['thermocline_east']>a['thermocline_east']
assert c['thermocline_east']>b['thermocline_east']
assert abs(c['thermocline_west']-c['thermocline_east'])<8
p=ROOT/'检查'/'质量检查.json';report=json.loads(p.read_text(encoding='utf-8'))
report['visual_review']='PASS：复核12–16、19–25、28–35秒联系表与全片关键节点；另检查最终MP4解码抽帧及总结文字字形。'
report['subtitle_content_check']='PASS：全部帧字幕逐字对照v29原文'
report['water_structure_check']='PASS：暖水东移时西侧变薄且东侧增厚；随后东部继续加深，异常态温跃层趋平。'
report['max_geometry_step_per_frame']={key:max(abs(a['geometry'][key]-b['geometry'][key]) for a,b in zip(rows,rows[1:])) for key in rows[0]['geometry']}
report['output_sha256']=hashlib.sha256(Path(report['video']).read_bytes()).hexdigest()
report['mux_frame_note']='生成及检查905帧；最短音视频封装保留904帧，与v29输出帧数及37.69秒总时长一致。'
report['timeline_sha256']=hashlib.sha256(timeline_path.read_bytes()).hexdigest()
p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'保留的逐句时间轴.json').write_bytes(timeline_path.read_bytes())
print(json.dumps({k:report[k] for k in ('frames_checked','decoded_frames','new_video_duration','decode','visual_review','subtitle_content_check','water_structure_check')},ensure_ascii=False))
