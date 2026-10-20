from pathlib import Path
import sys,asyncio,subprocess,wave,json
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent
sys.path.insert(0,str(P/'ocean_animation_demo_20261011/runtime'));sys.path.insert(0,str(P/'正常异常对照_区域预测_v36/.runtime'))
import edge_tts,imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe();(R/'配音').mkdir(exist_ok=True)
LINES=[('会诊','最后，把四步会诊串起来：测体征、查病因、追并发症、开处方。'),('机制','信风减弱，暖水东移，东部冷水上涌减弱，沃克环流也随之减弱或错位，水热格局因此改变。'),('辨析','还要记住：影响有遥相关和滞后，厄尔尼诺也不等于全球变暖。'),('情境','现在试一道题。以下是教学假设，不是真实预报。'),('材料','Niño三点四区持续异常偏暖，信风减弱。石河子某校收到当地强降雨预警。'),('问题','判断海温距平正负，解释东部上升流变化；能据此断定石河子暴雨吗？学校怎样应对？'),('答案','参考答案：距平为正，上升流减弱。'),('迁移','但不能仅凭厄尔尼诺断定石河子暴雨。按本地预警调整户外活动，属于适应。'),('评分','四项各一分。'),('告别','下期会诊，我们再认识拉尼娜。咕咕嘎嘎，下课啦！')]
async def main():
 a=[np.zeros(48000,dtype='<i2')];clock=2.;rows=[];chapter=None;pause=None
 for i,(mode,words) in enumerate(LINES):
  if mode=='情境':chapter=clock;a.append(np.zeros(48000,dtype='<i2'));clock+=2
  if mode=='答案':pause=[clock,clock+3];a.append(np.zeros(72000,dtype='<i2'));clock+=3
  f=R/'配音'/f'{i:02d}_{mode}.mp3'
  if not f.exists():await edge_tts.Communicate(words,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=45).save(str(f))
  raw=subprocess.run([FF,'-v','error','-i',str(f),'-f','s16le','-ac','1','-ar','24000','-'],capture_output=True,check=True).stdout;p=np.frombuffer(raw,dtype='<i2').copy();idx=np.flatnonzero(abs(p.astype(np.int32))>220)
  if len(idx):p=p[max(0,idx[0]-480):min(len(p),idx[-1]+600)]
  dur=len(p)/24000;gap=.14 if i<len(LINES)-1 else 2.2;rows.append(dict(mode=mode,text=words,start=clock,speech_end=clock+dur,end=clock+dur+gap));a.extend([p,np.zeros(round(gap*24000),dtype='<i2')]);clock+=dur+gap
 p=np.concatenate(a)
 with wave.open(str(R/'配音/第十二段.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(p.tobytes())
 meta=dict(lines=rows,duration=clock,chapter2=chapter,thinking=pause,voice='zh-CN-XiaoyiNeural +5%',word_shots=[26,27],comment_ids=[20]);(R/'台词与时间轴.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(meta,ensure_ascii=False),flush=True)
asyncio.run(main())
