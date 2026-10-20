from pathlib import Path
import sys,asyncio,subprocess,wave,json,hashlib
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent
sys.path[:0]=[str(P/'ocean_animation_demo_20261011/runtime'),str(P/'正常异常对照_区域预测_v36/.runtime')]
import edge_tts,imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe()
LINES=[
 ('引入',.25,2.72,'厄尔尼诺，会怎样影响中国？'),
 ('降水',3.95,5.30,'先看降水。'),
 ('南方',5.35,9.65,'部分厄尔尼诺事件的次年夏季，长江中下游更容易多雨。'),
 ('北方',9.80,11.85,'北方一些地区则可能偏旱。'),
 ('洪水风险',11.95,15.55,'雨下得多、持续得久，洪水风险也会增加。'),
 ('案例',15.70,19.85,'1998年长江大洪水背后，就有厄尔尼诺的影响。'),
 ('台风',20.30,24.72,'再看台风。发展期，生成区往往偏东、偏南，'),
 ('增强',24.90,27.45,'部分台风有更长时间增强。'),
 ('风险',27.63,30.50,'但强度和登陆地点，还要看具体环境。'),
 ('暖冬',31.30,35.40,'冬季，我国大部常接近常年到偏暖，地区差异明显。'),
 ('寒潮',35.62,40.50,'暖冬不等于一直暖。冷空气仍会南下，带来冷暖交替。'),
 ('收束',41.20,44.65,'这是气候倾向，具体天气还要看预报。')]
async def main():
 out=np.zeros(45*24000,dtype='<i2');rows=[]
 for i,(mode,start,limit,words) in enumerate(LINES):
  f=R/'配音'/f'{i:02d}_{mode}_{hashlib.sha256(words.encode()).hexdigest()[:8]}.mp3'
  same=list((R/'配音').glob(f'*_{mode}_{hashlib.sha256(words.encode()).hexdigest()[:8]}.mp3'))
  if same and not f.exists():
   import shutil
   shutil.copy2(same[0],f)
  old=R/'配音'/f'{i:02d}_{mode}.mp3'
  if old.exists() and not f.exists():
   previous=json.loads((R/'台词与时间轴.json').read_text(encoding='utf-8')) if (R/'台词与时间轴.json').exists() else {}
   if any(r.get('mode')==mode and r.get('text')==words for r in previous.get('lines',[])):
    import shutil
    shutil.copy2(old,f)
  if not f.exists():
   for attempt in range(2):
    try:
     await edge_tts.Communicate(words,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=45).save(str(f));break
    except Exception:
     if attempt:raise
  raw=subprocess.run([FF,'-v','error','-i',str(f),'-f','s16le','-ac','1','-ar','24000','-'],capture_output=True,check=True).stdout
  p=np.frombuffer(raw,dtype='<i2').copy();idx=np.flatnonzero(abs(p.astype(np.int32))>220)
  if len(idx):p=p[max(0,idx[0]-480):min(len(p),idx[-1]+600)]
  natural=len(p)/24000;target=limit-start;factor=max(1,natural/target)
  if factor>1:
   raw=subprocess.run([FF,'-v','error','-f','s16le','-ar','24000','-ac','1','-i','-','-af',f'atempo={factor:.8f}','-f','s16le','-'],input=p.tobytes(),capture_output=True,check=True).stdout;p=np.frombuffer(raw,dtype='<i2').copy()
  p=p[:round(target*24000)];k=round(start*24000);out[k:k+len(p)]=p
  rows.append(dict(mode=mode,text=words,start=start,speech_end=start+len(p)/24000,end=limit,natural_duration=natural,tempo=factor));print(mode,round(natural,2),'tempo',round(factor,3),flush=True)
 with wave.open(str(R/'配音/中国影响45秒.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(out.tobytes())
 (R/'台词与时间轴.json').write_text(json.dumps(dict(duration=45,fps=24,voice='zh-CN-XiaoyiNeural +5%; limited local time fitting',lines=rows),ensure_ascii=False,indent=2),encoding='utf-8')
asyncio.run(main())
