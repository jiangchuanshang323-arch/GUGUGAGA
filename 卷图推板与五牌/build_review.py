"""Make a short review cut from the latest rendered fifth segment."""
from pathlib import Path
import subprocess,json,hashlib,importlib.util
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
spec=importlib.util.spec_from_file_location('manager',PROJECT/'demooo'/'manage_videos.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
src=ROOT/'交付'/'part5.mp4'
if not src.exists():src=PROJECT/'demooo'/'独立片段'/'05_环境多米诺_水'/'海洋发烧了_第五段_环境多米诺_水.mp4'
dest=PROJECT/'demooo'/'预览'/'局部修正'/'海洋发烧了_局部修正.mp4';dest.parent.mkdir(parents=True,exist_ok=True)
clips=[(8.711958333,23.154541667),(39.057208333,44.398416667),(49.601916667,56.315875)]
graph=[]
for i,(a,b) in enumerate(clips):
 graph += [f'[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}]',f'[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS[a{i}]']
graph.append(''.join(f'[v{i}][a{i}]' for i in range(len(clips)))+'concat=n=3:v=1:a=1[v][a]')
pending=dest.with_name('.'+dest.stem+'.pending.mp4')
subprocess.run([m.EXE,'-v','error','-y','-i',str(src),'-filter_complex',';'.join(graph),'-map','[v]','-map','[a]','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(pending)],check=True)
m.commit(pending,dest)
report=dict(path=str(dest.relative_to(m.ROOT)),source_ranges=clips,**m.info(dest),decode='PASS')
(ROOT/'短样片_验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
data=json.loads(m.MANIFEST.read_text(encoding='utf-8'));data.setdefault('previews',{})['局部修正']=report;m.write_manifest(data)
print(json.dumps(report,ensure_ascii=False),flush=True)
