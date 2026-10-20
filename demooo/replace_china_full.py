"""Replace the old China/Shihezi lesson, remove its lead-in, and rebuild the course."""
from pathlib import Path
import json,math,subprocess,shutil,wave,io
from PIL import Image,ImageDraw
import manage_videos as m

def compose(data,overrides=None):
 overrides=overrides or {};keys=sorted(data['segments'])
 assert [int(k.split('_')[0]) for k in keys]==list(range(13))
 entry=data['merges']['目前完整成片'];dest=m.ROOT/entry['path'];check=dest.parent/'检查';check.mkdir(exist_ok=True)
 pending=dest.with_name('.完整成片替换.pending.mp4');args=[m.EXE,'-hide_banner','-v','error','-y'];graph=[];records=[];elapsed=0
 for i,k in enumerate(keys):
  e=data['segments'][k];p=overrides.get(k,m.ROOT/e['path']);assert m.digest(p)==e['sha256'],k
  n=round(e['seconds']*24);seconds=n/24;args+=['-i',str(p)]
  graph.extend([f'[{i}:v]fps=24,tpad=stop_mode=clone:stop_duration=0.15,trim=end_frame={n},setsar=1,setpts=N/(24*TB)[v{i}]',f'[{i}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad,atrim=duration={seconds:.9f},asetpts=PTS-STARTPTS[a{i}]'])
  records.append(dict(key=k,path=e['path'],start=elapsed,end=elapsed+seconds,frames=n,sha256=e['sha256']));elapsed+=seconds
 graph.append(''.join(f'[v{i}][a{i}]' for i in range(len(keys)))+f'concat=n={len(keys)}:v=1:a=1[v][a]')
 args+=['-filter_complex',';'.join(graph),'-map','[v]','-map','[a]','-t',str(elapsed),'-c:v','libx264','-preset','fast','-crf','18','-profile:v','baseline','-level:v','4.0','-g','24','-bf','0','-refs','1','-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-ac','2','-b:a','160k','-movflags','+faststart','-progress',str(check/'替换编码进度.txt'),str(pending)]
 print('COMPOSE',round(elapsed,3),'seconds',flush=True)
 with (check/'替换编码日志.txt').open('wb') as log:subprocess.run(args,stderr=log,check=True)
 m.decode(pending);info=m.info(pending);assert abs(info['seconds']-elapsed)<.04,(info,elapsed)
 r=subprocess.run([m.EXE,'-hide_banner','-i',str(pending),'-map','0:v:0','-c','copy','-f','null','-'],capture_output=True,check=True)
 import re
 count=int(re.findall(r'frame=\s*(\d+)',r.stderr.decode('utf-8','replace'))[-1]);assert count==sum(a['frames'] for a in records)
 times=[1.,elapsed-.4]
 for a in records:
  times.extend([a['start']+min(2.3,(a['end']-a['start'])/2),a['end']-.22])
 china=next(a for a in records if a['key']=='10_中国影响')
 for start in [china['start'],china['end']]:times.extend([start-.10,start+.12])
 times.extend([china['start']+7.8,china['start']+17.5,china['start']+29.3,china['start']+37.8])
 times=sorted(set(times));sheet=Image.new('RGB',(1600,math.ceil(len(times)/4)*250),'#e5ebeb')
 for j,t in enumerate(times):
  raw=subprocess.run([m.EXE,'-v','error','-ss',str(t),'-i',str(pending),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True,check=True).stdout
  im=Image.open(io.BytesIO(raw)).convert('RGB');assert im.size==(1920,1080)
  if abs(t-china['start'])<.2 or abs(t-china['end'])<.2 or any(abs(t-china['start']-z)<.01 for z in [7.8,17.5,29.3,37.8]):im.save(check/f'替换衔接_{t:.3f}.png')
  x=j%4*400;y=j//4*250;sheet.paste(im.resize((400,225),Image.Resampling.LANCZOS),(x,y));ImageDraw.Draw(sheet).text((x+7,y+231),f'{t:.3f}s',fill='#254f61')
 sheet.save(check/'全阶段编码抽帧.jpg')
 report=dict(**info,decode='PASS',resolution='1920x1080',fps=24,frames=count,source_segments=records,review_times=times,china_interval=[china['start'],china['end']],china_seconds=45,shihezi_case_included=False,shihezi_quiz_retained=True)
 return pending,dest,report

def main():
 data=json.loads(m.MANIFEST.read_text(encoding='utf-8'));old=json.loads(json.dumps(data))
 k9='09_辨析与滞后';k10=next(k for k in data['segments'] if k.startswith('10_'))
 project=m.PROJECT;src=project/'中国影响_45秒动画';china=m.ROOT/data['previews']['中国影响全屏动画']['path']
 assert m.digest(china)=='90006f77332e9cd4bbeb9231c28b530be1a9006f9808a15ea0259fc69d266b8b'
 meta_path=project/'第九段_辨析与滞后/台词与时间轴.json';meta=json.loads(meta_path.read_text(encoding='utf-8'))
 stage=m.ROOT/'.build/中国影响替换';stage.mkdir(parents=True,exist_ok=True)
 old9=m.ROOT/data['segments'][k9]['path'];new9=stage/'第九段_去除旧引入.mp4'
 cut=next((r['start'] for r in meta['lines'] if r['mode']=='衔接'),None)
 if cut is not None:
  n=math.ceil(cut*24);duration=n/24
  args=[m.EXE,'-v','error','-y','-i',str(old9),'-vf',f'fps=24,trim=end_frame={n},setpts=N/(24*TB)','-af',f'atrim=end={cut:.9f},apad,atrim=duration={duration:.9f},asetpts=PTS-STARTPTS','-t',str(duration),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-ac','2','-b:a','160k','-movflags','+faststart',str(new9)]
  subprocess.run(args,check=True);m.decode(new9)
 else:shutil.copy2(old9,new9)
 data['segments'][k9].update(m.info(new9));data['segments'][k9]['removed_lead_in']='接下来，把视线移向中国，再落到石河子。'
 dest10=m.ROOT/'独立片段/10_中国影响/海洋发烧了_第十段_中国影响.mp4';dest10.parent.mkdir(parents=True,exist_ok=True)
 staged10=stage/'第十段_中国影响.mp4';shutil.copy2(china,staged10);m.decode(staged10)
 data['segments'].pop(k10)
 data['segments']['10_中国影响']=dict(path=str(dest10.relative_to(m.ROOT)),**m.info(staged10),decode='PASS',generator='中国影响_45秒动画/build_video.py',replaces=k10,source_preview='中国影响全屏动画')
 pending,dest,report=compose(data,{k9:new9,'10_中国影响':staged10})
 for k,e in old['segments'].items():assert m.digest(m.ROOT/e['path'])==e['sha256'],k
 # Publish only after the replacement composition has decoded and passed frame checks.
 m.copy_exact(new9,old9);m.copy_exact(staged10,dest10);pending.replace(dest)
 if cut is not None:
  meta['lines']=[r for r in meta['lines'] if r['mode']!='衔接'];meta['duration']=cut
  meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
  audio=project/'第九段_辨析与滞后/配音/第九段.wav'
  with wave.open(str(audio),'rb') as w:params=w.getparams();pcm=w.readframes(round(cut*w.getframerate()))
  with wave.open(str(audio.with_suffix('.pending.wav')),'wb') as w:w.setparams(params);w.writeframes(pcm)
  audio.with_suffix('.pending.wav').replace(audio)
 entry=data['merges']['目前完整成片'];entry.update(m.info(dest),segments=sorted(data['segments']),decode='PASS',scope='完整课程：原第十段中国影响与石河子案例替换为新版45秒中国影响；保留适应与减缓、总结与检测',shihezi_case_included=False,shihezi_quiz_retained=True,meets_duration_limit=report['seconds']<=600)
 m.write_manifest(data)
 old10=m.ROOT/old['segments'][k10]['path']
 if old10.resolve()!=dest10.resolve():
  assert old10.resolve().is_relative_to((m.ROOT/'独立片段').resolve());old10.unlink()
  attribution=old10.parent/'素材署名与来源.txt'
  if attribution.exists():shutil.move(str(attribution),str(project/'第十段_石河子乡土/历史交付素材署名与来源.txt'))
  if not any(old10.parent.iterdir()):old10.parent.rmdir()
 (dest10.parent/'素材署名与来源.txt').write_text('第十段：中国影响，45秒。\n最新来源与制作说明见：'+str(src/'制作说明与来源.md')+'\n纸本水彩说明：'+str(src/'纸本水彩重绘说明.md')+'\n最新标注、附图和轨迹说明：'+str(src/'指向线与附图清晰度修改说明.md')+'\n本段取代原中国影响简述与石河子案例。保留总结中的独立假设检测题。\n',encoding='utf-8')
 report.update(formal_segment9=m.info(old9),formal_segment10=m.info(dest10),removed_old_segment10=str(old10),other_independent_segments_unchanged=True,visual_review='pending actual encoded review')
 (dest.parent/'检查/合成验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 (dest.parent/'内容范围.txt').write_text('完整课程预览：开场至总结与检测。原第十段中国影响简述及石河子案例已整体换成最新45秒中国影响，前段旧石河子引入句删除。其余章节保留，包括结尾独立教学假设题。\n共13段，时长以检查/合成验证.json为准。独立片段10_中国影响已保存，旧石河子交付MP4已删除，原源工程保留。\n',encoding='utf-8')
 index=dest.parent/'素材与评价资料索引.txt';s=index.read_text(encoding='utf-8').replace('10_石河子乡土','10_中国影响');index.write_text(s,encoding='utf-8')
 print('DELIVERED',dest,json.dumps(report,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
