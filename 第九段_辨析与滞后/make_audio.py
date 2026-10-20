from pathlib import Path
import sys,asyncio,subprocess,wave,json
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent
sys.path.insert(0,str(P/'ocean_animation_demo_20261011/runtime'))
sys.path.insert(0,str(P/'正常异常对照_区域预测_v36/.runtime'))
import edge_tts,imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe();(R/'配音').mkdir(exist_ok=True)
LINES=[
('开题','五张牌串起来了，还要分清两个概念。'),
('自然','厄尔尼诺，是海气系统中的自然波动。'),
('增暖','人为全球增暖，则是温室气体增加推动的长期趋势。'),
('风险','两者不是同一个概念，却可能共同抬高某些地区的高温等风险。'),
('责任','减少温室气体排放，是我们应对长期增暖的责任。'),
('提问','所以，一次高温，能全算在厄尔尼诺头上吗？'),
('回答','不能，还要看长期背景和其他因素。'),
('储热','再看滞后。海洋像个大热库，水的比热容大，储热和释放热量都需要时间。'),
('调整','海气交换和大气环流的调整，也会让不同地区的响应错开。'),
('错峰','所以，海温峰值和影响峰值不必同步。'),
('条件','具体晚多久，要看地区、季节和影响类型。')]
async def main():
 a=[np.zeros(48000,dtype='<i2')];clock=2.;rows=[];pause=None;chapter=None
 for i,(mode,words) in enumerate(LINES):
  if mode=='回答':pause=[clock,clock+3];a.append(np.zeros(72000,dtype='<i2'));clock+=3
  if mode=='储热':chapter=clock;a.append(np.zeros(48000,dtype='<i2'));clock+=2
  f=R/'配音'/f'{i:02d}_{mode}.mp3'
  if not f.exists():await edge_tts.Communicate(words,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=45).save(str(f))
  raw=subprocess.run([FF,'-v','error','-i',str(f),'-f','s16le','-ac','1','-ar','24000','-'],capture_output=True,check=True).stdout
  pcm=np.frombuffer(raw,dtype='<i2').copy();idx=np.flatnonzero(np.abs(pcm.astype(np.int32))>220)
  if len(idx):pcm=pcm[max(0,idx[0]-480):min(len(pcm),idx[-1]+600)]
  dur=len(pcm)/24000;gap=.13 if mode!='衔接' else .4
  rows.append(dict(mode=mode,text=words,start=clock,speech_end=clock+dur,end=clock+dur+gap));a+=[pcm,np.zeros(round(gap*24000),dtype='<i2')];clock+=dur+gap
 pcm=np.concatenate(a)
 with wave.open(str(R/'配音/第九段.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm.tobytes())
 meta=dict(lines=rows,duration=clock,thinking=pause,chapter2=chapter,voice='zh-CN-XiaoyiNeural +5%',word_shots=[21,22])
 (R/'台词与时间轴.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(meta,ensure_ascii=False),flush=True)
asyncio.run(main())
