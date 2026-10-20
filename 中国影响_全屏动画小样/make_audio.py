from pathlib import Path
import sys,asyncio,subprocess,wave,json
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent
sys.path.insert(0,str(P/'ocean_animation_demo_20261011/runtime'));sys.path.insert(0,str(P/'正常异常对照_区域预测_v36/.runtime'))
import edge_tts,imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe();(R/'配音').mkdir(exist_ok=True)
LINES=[('范围','把视线移回中国。以厄尔尼诺次年夏季为例，'),('水汽','偏南风可能把更多水汽输送到长江流域，'),('降水','增加降水偏多的可能。'),('差异','不同事件，雨带的位置和强度仍会变化。')]
async def main():
 arrays=[np.zeros(9600,dtype='<i2')];clock=.4;rows=[]
 for i,(mode,words) in enumerate(LINES):
  f=R/'配音'/f'{i:02d}_{mode}.mp3'
  if not f.exists():await edge_tts.Communicate(words,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=45).save(str(f))
  raw=subprocess.run([FF,'-v','error','-i',str(f),'-f','s16le','-ac','1','-ar','24000','-'],capture_output=True,check=True).stdout;p=np.frombuffer(raw,dtype='<i2').copy();idx=np.flatnonzero(abs(p.astype(np.int32))>220)
  if len(idx):p=p[max(0,idx[0]-480):min(len(p),idx[-1]+600)]
  dur=len(p)/24000;gap=.12 if i<len(LINES)-1 else .6;rows.append(dict(mode=mode,text=words,start=clock,speech_end=clock+dur,end=clock+dur+gap));arrays.extend([p,np.zeros(round(gap*24000),dtype='<i2')]);clock+=dur+gap
 pcm=np.concatenate(arrays)
 with wave.open(str(R/'配音/中国影响.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm.tobytes())
 meta=dict(lines=rows,duration=clock,voice='zh-CN-XiaoyiNeural +5%',scope='全屏自绘中国影响短样片，不含石河子，不替换正式小段或合成片');(R/'台词与时间轴.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(meta,ensure_ascii=False),flush=True)
asyncio.run(main())
