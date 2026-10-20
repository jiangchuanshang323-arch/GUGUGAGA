from pathlib import Path
import sys,asyncio,subprocess,wave,json
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent
sys.path.insert(0,str(P/'ocean_animation_demo_20261011/runtime'));sys.path.insert(0,str(P/'正常异常对照_区域预测_v36/.runtime'))
import edge_tts,imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe();(R/'配音').mkdir(exist_ok=True)
LINES=[
('中国','先把视线移回中国。厄尔尼诺可以通过大气环流，影响我国的水热分布。'),
('差异','不同地区、不同季节，表现并不一样。'),
('新疆','再往西北，找到我国的新疆维吾尔自治区。'),
('石河子','最后，落到天山北麓的石河子。'),
('绿洲','这里的绿洲农业离不开水。'),
('水源','我们关心的，不只是下不下雨，还有山地降水、冰雪融水、河流来水，以及棉田什么时候需要灌溉。'),
('遥相关','太平洋的海水可没有一路流到新疆！遥相关，说的是远距离气候变化之间的统计联系，中间联系着大气环流。'),
('判断','所以，不能看见厄尔尼诺，就给石河子贴上一定涝、或者一定旱的标签。'),
('预报','要结合本地监测和最新预报，再判断供水与农业风险。'),
('衔接','接下来，我们开两类处方。')]
async def main():
 arrays=[np.zeros(48000,dtype='<i2')];clock=2.;rows=[]
 for i,(mode,words) in enumerate(LINES):
  if mode=='判断':arrays.append(np.zeros(16800,dtype='<i2'));clock+=.7
  f=R/'配音'/f'{i:02d}_{mode}.mp3'
  if not f.exists():await edge_tts.Communicate(words,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=45).save(str(f))
  raw=subprocess.run([FF,'-v','error','-i',str(f),'-f','s16le','-ac','1','-ar','24000','-'],capture_output=True,check=True).stdout
  pcm=np.frombuffer(raw,dtype='<i2').copy();idx=np.flatnonzero(abs(pcm.astype(np.int32))>220)
  if len(idx):pcm=pcm[max(0,idx[0]-480):min(len(pcm),idx[-1]+600)]
  dur=len(pcm)/24000;gap=.14 if i<len(LINES)-1 else .5;rows.append(dict(mode=mode,text=words,start=clock,speech_end=clock+dur,end=clock+dur+gap));arrays.extend([pcm,np.zeros(round(gap*24000),dtype='<i2')]);clock+=dur+gap
 pcm=np.concatenate(arrays)
 with wave.open(str(R/'配音/第十段.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm.tobytes())
 meta=dict(lines=rows,duration=clock,voice='zh-CN-XiaoyiNeural +5%',word_shots=[23],comment_ids=[19]);(R/'台词与时间轴.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(meta,ensure_ascii=False),flush=True)
asyncio.run(main())
