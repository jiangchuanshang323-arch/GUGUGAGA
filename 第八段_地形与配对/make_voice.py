from pathlib import Path
import sys,asyncio,wave,json,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
for n in ('配音','素材','检查','.build'):(ROOT/n).mkdir(exist_ok=True)
sys.path.insert(0,str(PROJECT/'ocean_animation_demo_20261011/runtime'))
sys.path.insert(0,str(PROJECT/'正常异常对照_区域预测_v36/.runtime'))
import edge_tts,imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe()
LINES=[
 ('机制','第五张，地形。厄尔尼诺不直接推动地壳，而是通过降水、海浪等变化，改变侵蚀和堆积。'),
 ('河口','秘鲁卡亚俄湾就有反直觉的例子：部分强事件后，里马克河带来的泥沙形成三角洲，随后让北侧海滩变宽。'),
 ('漫滩','拉尼娜也会塑造地表。研究发现，亚马孙流域部分漫滩的集中堆积，与拉尼娜洪水相联系。'),
 ('收束','所以，别只盯着灾害，还要追踪水和泥沙的重新分配。'),
 ('提问','按本课重点配对：降水、热交换、白化、泥炭燃烧、河口堆积，分别对应哪张牌？'),
 ('揭晓','依次是水、气、生、土、地形。通过过程，它们相互联系。')]
async def main():
 parts=[];cursor=0;rows=[];intros=[];pause=None
 for i,(mode,text) in enumerate(LINES):
  if mode in ('机制','提问'):
   intros.append(dict(start=cursor,title='第五张·地形' if mode=='机制' else '互动·要素配对'))
   parts.append(np.zeros(48000,dtype='<i2'));cursor+=2
  if mode=='揭晓':pause=cursor;parts.append(np.zeros(72000,dtype='<i2'));cursor+=3
  out=ROOT/'配音'/f'{i:02d}_{mode}.mp3'
  if not out.exists():await edge_tts.Communicate(text,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=45).save(str(out))
  a=np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(out),'-ar','24000','-ac','1','-f','s16le','-']),dtype='<i2')
  nz=np.flatnonzero(np.abs(a.astype(np.int32))>220)
  if len(nz):a=a[max(0,nz[0]-480):min(len(a),nz[-1]+600)]
  gap=.1 if i<5 else .4
  rows.append(dict(mode=mode,text=text,start=cursor,speech_end=cursor+len(a)/24000,end=cursor+len(a)/24000+gap))
  parts.extend([a,np.zeros(round(gap*24000),dtype='<i2')]);cursor=rows[-1]['end'];print(mode,round(cursor,2),flush=True)
 pcm=np.concatenate(parts)
 with wave.open(str(ROOT/'配音/第八段_晓伊.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm.tobytes())
 (ROOT/'台词与时间轴.json').write_text(json.dumps(dict(lines=rows,intros=intros,pause_start=pause,duration=len(pcm)/24000),ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':asyncio.run(main())
