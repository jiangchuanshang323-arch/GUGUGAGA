from pathlib import Path
import sys,asyncio,wave,json,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parent;P=ROOT.parent
for n in ('配音','检查','.build','交付'):(ROOT/n).mkdir(exist_ok=True)
sys.path.insert(0,str(P/'ocean_animation_demo_20261011/runtime'));sys.path.insert(0,str(P/'正常异常对照_区域预测_v36/.runtime'))
import edge_tts,imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe()
LINES=[('水','同学们，先看第一张多米诺牌。'),('气','接着，来看看下一张牌。'),('生','同学们，再翻到下一张牌。'),('土','下面，看看土壤这张牌。'),('地形','最后一张多米诺，轮到地形啦。'),('回场','五张牌看完了。回想刚才的例子，试着把它们配起来。')]
async def main():
 meta={}
 for mode,text in LINES:
  out=ROOT/'配音'/f'{mode}.mp3'
  if not out.exists():await edge_tts.Communicate(text,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=45).save(str(out))
  a=np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(out),'-ar','24000','-ac','1','-f','s16le','-']),dtype='<i2');nz=np.flatnonzero(np.abs(a.astype(np.int32))>220)
  if len(nz):a=a[max(0,nz[0]-480):min(len(a),nz[-1]+600)]
  lead=.65;tail=.9 if mode!='回场' else .35
  pcm=np.concatenate([np.zeros(round(lead*24000),dtype='<i2'),a,np.zeros(round(tail*24000),dtype='<i2')])
  dest=ROOT/'配音'/f'{mode}.wav'
  with wave.open(str(dest),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm.tobytes())
  meta[mode]=dict(text=text,lead=lead,speech_end=lead+len(a)/24000,duration=len(pcm)/24000,path=str(dest));print(mode,meta[mode]['duration'],flush=True)
 (ROOT/'串讲配音.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':asyncio.run(main())
