from pathlib import Path
import sys,asyncio,subprocess,wave,json
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent
sys.path.insert(0,str(P/'ocean_animation_demo_20261011/runtime'));sys.path.insert(0,str(P/'正常异常对照_区域预测_v36/.runtime'))
import edge_tts,imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe();(R/'配音').mkdir(exist_ok=True)
LINES=[('适应','第一张处方叫适应：早发现、早预警、早行动。'),('监测','先看官方监测，再查本地预警的地区和有效时间。'),('行动','最后按指引准备应急物品，调整出行和用水安排。'),('损失','这是在减少暴露与损失，不是在消灭厄尔尼诺。'),('减缓','第二张处方叫减缓：通过节能和清洁能源，减少温室气体排放，限制长期人为增暖。'),('自然','它不能阻止自然发生的厄尔尼诺。'),('区分','注意：备应急包属于适应，关掉不用的灯属于减缓，别混成一类。'),('选择','今天选一件事：和家人检查应急包，或者完成一次节能行动。你选哪一项？'),('记录','把选择写下来，再说说它属于哪一类。')]
async def main():
 arrays=[np.zeros(48000,dtype='<i2')];clock=2.;rows=[];chapter=None;pause=None
 for i,(mode,words) in enumerate(LINES):
  if mode=='减缓':chapter=clock;arrays.append(np.zeros(48000,dtype='<i2'));clock+=2
  if mode=='记录':pause=[clock,clock+3];arrays.append(np.zeros(72000,dtype='<i2'));clock+=3
  f=R/'配音'/f'{i:02d}_{mode}.mp3'
  if not f.exists():await edge_tts.Communicate(words,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=45).save(str(f))
  raw=subprocess.run([FF,'-v','error','-i',str(f),'-f','s16le','-ac','1','-ar','24000','-'],capture_output=True,check=True).stdout
  pcm=np.frombuffer(raw,dtype='<i2').copy();idx=np.flatnonzero(abs(pcm.astype(np.int32))>220)
  if len(idx):pcm=pcm[max(0,idx[0]-480):min(len(pcm),idx[-1]+600)]
  dur=len(pcm)/24000;gap=.13 if i<len(LINES)-1 else .45;rows.append(dict(mode=mode,text=words,start=clock,speech_end=clock+dur,end=clock+dur+gap));arrays.extend([pcm,np.zeros(round(gap*24000),dtype='<i2')]);clock+=dur+gap
 pcm=np.concatenate(arrays)
 with wave.open(str(R/'配音/第十一段.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm.tobytes())
 meta=dict(lines=rows,duration=clock,chapter2=chapter,thinking=pause,voice='zh-CN-XiaoyiNeural +5%',word_shots=[24,25],comment_ids=[20]);(R/'台词与时间轴.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(meta,ensure_ascii=False),flush=True)
asyncio.run(main())
