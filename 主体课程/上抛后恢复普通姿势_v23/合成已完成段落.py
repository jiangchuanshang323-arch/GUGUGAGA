from pathlib import Path
import sys,subprocess,json,inspect,re,hashlib
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));import build_v23 as m
v=m.v
OUT=ROOT.parents[1]/'合成成片_20261013_v23'
OUT.mkdir(exist_ok=True)
PREFIX=ROOT.parent/'横梁起卷_双手下拉_v14'/'交付'/'海洋发烧了_开场与前两段_双手卷板_v14.mp4'
THIRD=OUT/'海洋发烧了_第三段_普通姿势卷轴_v23.mp4'
JOINED=OUT/'海洋发烧了_开场与已完成三段_v23.mp4'
assert PREFIX.is_file()

def info(path):
    r=subprocess.run([v.EXE,'-hide_banner','-i',str(path)],capture_output=True)
    t=r.stderr.decode('utf-8','replace')
    a=re.search(r'Duration: (\d+):(\d+):(\d+(?:\.\d+)?)',t)
    duration=int(a[1])*3600+int(a[2])*60+float(a[3]) if a else None
    return {'file':str(path),'seconds':duration,'streams':[x.strip() for x in t.splitlines() if 'Stream #' in x]}

print('Render latest full third segment, cached voice only',flush=True)
src=inspect.getsource(v.encode).replace("'-c:v','libx264'","'-vf','setsar=1','-c:v','libx264'").replace("'-c:a','aac'","'-ar','48000','-ac','2','-c:a','aac'")
exec(src,v.__dict__)
if not THIRD.exists():v.encode(THIRD,0,v.DURATION)
print('Third segment complete; joining existing opening and first two segments',flush=True)
# Earlier filter-concatenated master uses a 1/1000000 video time base.
# Normalize the new MP4 container time base without encoding its video again.
NORMAL=OUT/'.第三段_统一时间基准.mp4'
subprocess.run([v.EXE,'-y','-v','error','-i',str(THIRD),'-c','copy','-video_track_timescale','1000000',str(NORMAL)],check=True)
files=OUT/'拼接清单.txt'
files.write_text('\n'.join("file '"+str(x).replace('\\','/')+"'" for x in (PREFIX,NORMAL))+'\n',encoding='utf-8')
with (OUT/'拼接.log').open('w',encoding='utf-8') as log:
    subprocess.run([v.EXE,'-y','-f','concat','-safe','0','-i',str(files),'-c','copy','-movflags','+faststart',str(JOINED)],stdout=log,stderr=log,check=True)
print('Check complete joined file decode',flush=True)
check=subprocess.run([v.EXE,'-v','error','-i',str(JOINED),'-f','null','-'],capture_output=True)
assert check.returncode==0 and not check.stderr.strip(),check.stderr.decode('utf-8','replace')
items=[info(x) for x in (PREFIX,THIRD,JOINED)]
assert abs(items[2]['seconds']-sum(x['seconds'] for x in items[:2]))<.3
report={'decode':'PASS','stream_copy_concat':True,'new_voice_synthesis':False,'duplicates_of_opening':False,'segments':items,'sha256':hashlib.sha256(JOINED.read_bytes()).hexdigest()}
(OUT/'合成验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':str(JOINED),'seconds':items[2]['seconds'],'decode':'PASS'},ensure_ascii=False),flush=True)
