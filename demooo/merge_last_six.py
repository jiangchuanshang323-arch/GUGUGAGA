"""Render exactly the final six minutes, with the current China-impact replacement.

Review composition only: leaves the formal independent segments and full-course file intact.
"""
from pathlib import Path
import json,re,subprocess,hashlib,io,math
from PIL import Image,ImageDraw
import manage_videos as m

def frame_info(path):
 r=subprocess.run([m.EXE,'-hide_banner','-i',str(path),'-map','0:v:0','-c','copy','-f','null','-'],capture_output=True,check=True)
 s=r.stderr.decode('utf-8','replace');assert '1920x1080' in s and re.search(r'24(?:\.\d+)? fps',s),s[:1200]
 counts=re.findall(r'frame=\s*(\d+)',s);assert counts,s[-1000:]
 return int(counts[-1])

def main():
 data=json.loads(m.MANIFEST.read_text(encoding='utf-8'))
 keys=[k for k in sorted(data['segments']) if int(k.split('_')[0])>=6]
 assert [int(k.split('_')[0]) for k in keys]==list(range(6,13))
 records=[]
 for k in keys:
  entry=data['previews']['中国影响全屏动画'] if k.startswith('10_') else data['segments'][k]
  path=m.ROOT/entry['path'];assert m.digest(path)==entry['sha256'],k
  raw_frames=frame_info(path);n=round(entry['seconds']*24)
  assert abs(raw_frames-n)<=3,(k,raw_frames,n)
  records.append(dict(segment_key=k,content='中国影响' if k.startswith('10_') else k,path=str(path),frames=n,source_frames=raw_frames,seconds=n/24,sha256=entry['sha256']))
 n_total=sum(r['frames'] for r in records);crop=n_total-8640;assert 0<=crop<records[0]['frames']
 for r in records:print(r['content'],r['frames'],r['seconds'],flush=True)
 print('trim first segment',crop/24,'seconds; output 360 seconds',flush=True)
 dest=m.ROOT/'合成版本/后六分钟/海洋发烧了_后六分钟.mp4';dest.parent.mkdir(parents=True,exist_ok=True)
 check=dest.parent/'检查';check.mkdir(exist_ok=True)
 tmp=dest.with_name('.后六分钟.pending.mp4')
 full=m.ROOT/data['merges']['目前完整成片']['path'];full_hash=m.digest(full)
 args=[m.EXE,'-hide_banner','-v','error','-y'];graph=[]
 for i,r in enumerate(records):
  args+=['-i',r['path']]
  graph.extend([f'[{i}:v]fps=24,tpad=stop_mode=clone:stop_duration=0.15,trim=end_frame={r["frames"]},setsar=1,setpts=N/(24*TB)[v{i}]',f'[{i}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad,atrim=duration={r["seconds"]:.9f},asetpts=PTS-STARTPTS[a{i}]'])
 graph.append(''.join(f'[v{i}][a{i}]' for i in range(len(records)))+f'concat=n={len(records)}:v=1:a=1[joined][audio]')
 graph.append(f'[joined]trim=start_frame={crop}:end_frame={crop+8640},setpts=N/(24*TB)[v]')
 graph.append(f'[audio]atrim=start={crop/24:.9f}:duration=360,asetpts=PTS-STARTPTS,apad,atrim=duration=360[a]')
 args+=['-filter_complex',';'.join(graph),'-map','[v]','-map','[a]','-t','360','-c:v','libx264','-preset','fast','-crf','18','-profile:v','baseline','-level:v','4.0','-g','24','-bf','0','-refs','1','-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-ac','2','-b:a','160k','-movflags','+faststart','-progress',str(check/'编码进度.txt'),str(tmp)]
 with (check/'编码日志.txt').open('wb') as log:subprocess.run(args,stderr=log,check=True)
 m.decode(tmp);assert frame_info(tmp)==8640
 info=m.info(tmp);assert abs(info['seconds']-360)<.02,info
 assert all(m.digest(Path(r['path']))==r['sha256'] for r in records)
 assert m.digest(full)==full_hash
 tmp.replace(dest)
 elapsed=-crop/24;boundaries=[]
 for r in records:
  boundaries.append(dict(content=r['content'],start=elapsed,end=elapsed+r['seconds']))
  elapsed+=r['seconds']
 times=[.2,4.0,359.5]
 for b in boundaries:
  if b['start']>0:times.extend([max(0,b['start']-.18),min(359.8,b['start']+.18)])
 china=next(b for b in boundaries if b['content']=='中国影响')
 times.extend([china['start']+7.8,china['start']+17.5,china['start']+23,china['start']+37.8])
 times=sorted(times);sheet=Image.new('RGB',(1600,math.ceil(len(times)/4)*250),'#e2ebed')
 for j,t in enumerate(times):
  raw=subprocess.run([m.EXE,'-v','error','-ss',str(t),'-i',str(dest),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True,check=True).stdout
  im=Image.open(io.BytesIO(raw)).convert('RGB');assert im.size==(1920,1080)
  im.save(check/f'编码_{t:.3f}.jpg')
  x=j%4*400;y=j//4*250;sheet.paste(im.resize((400,225),Image.Resampling.LANCZOS),(x,y));ImageDraw.Draw(sheet).text((x+6,y+230),f'{t:.3f}s',fill='#254f61')
 sheet.save(check/'衔接与中国影响抽帧.jpg')
 report=dict(**info,decode='PASS',resolution='1920x1080',fps=24,frames=8640,source_segments=records,boundaries=boundaries,trim_first_segment_seconds=crop/24,shihezi_included=False,china_replacement_sha256=next(r['sha256'] for r in records if r['content']=='中国影响'),full_course_sha256_unchanged=full_hash,sources_unchanged=True,review_times=times)
 (check/'合成验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 (dest.parent/'内容范围.txt').write_text('更新后顺序的最后6分00秒。起点在第六段《水收束与气》中途，依次包含生与土、地形与配对、辨析与滞后、最新45秒中国影响、适应与减缓、总结与检测。\n原石河子段不纳入；原独立片段及全片合成文件均未修改。\n复现入口：demooo/merge_last_six.py。\n',encoding='utf-8')
 # A review snapshot with a dedicated generator, not a generic merge of the old formal segment 10.
 data.setdefault('previews',{})['后六分钟合成']=dict(path=str(dest.relative_to(m.ROOT)),**info,decode='PASS',generator='merge_last_six.py',scope='最后6:00；第六段中途至结尾；原石河子位置替换为最新45秒中国影响',trim_first_segment_seconds=crop/24,source_records=records)
 m.write_manifest(data)
 print('DELIVERED',str(dest),json.dumps(info),flush=True)

if __name__=='__main__':main()
