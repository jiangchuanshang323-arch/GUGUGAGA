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
 ('引入','第三张，生。回到秘鲁近海，鱼群的饭桌，就藏在上升流里。'),
 ('正常','正常时，深层冷水把营养盐送上来，浮游植物生长，支撑鱼类的食物来源。'),
 ('异常','厄尔尼诺时，上升流受抑制，营养盐补给减少，渔业随之受到影响。'),
 ('珊瑚','持续偏暖还可能让珊瑚排出共生藻，发生白化。污染也会加重压力，但白化不等于已经死亡。'),
 ('土','第四张，土。别只盯着树着火，脚下的泥炭也会燃烧。'),
 ('干旱','印尼干旱使土壤和植被变干，加上人为点火和排水等因素，更容易出现严重火灾。'),
 ('泥炭','泥炭燃烧释放碳和烟尘；植被与枯落物受损后，土壤失去保护。'),
 ('侵蚀','接下来若遇强降雨，地表径流和侵蚀风险可能增加。土的变化，又连向了地形。')]
async def main():
 parts=[];cursor=0;rows=[];intros=[]
 for i,(mode,text) in enumerate(LINES):
  if mode in ('引入','土'):
   intros.append(dict(start=cursor,title='第三张·生' if mode=='引入' else '第四张·土'))
   parts.append(np.zeros(48000,dtype='<i2'));cursor+=2
  out=ROOT/'配音'/f'{i:02d}_{mode}.mp3'
  if not out.exists():
   await edge_tts.Communicate(text,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=45).save(str(out))
  a=np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(out),'-ar','24000','-ac','1','-f','s16le','-']),dtype='<i2')
  nz=np.flatnonzero(np.abs(a.astype(np.int32))>220)
  if len(nz):a=a[max(0,nz[0]-480):min(len(a),nz[-1]+600)]
  gap=.12 if i<7 else .45
  rows.append(dict(mode=mode,text=text,start=cursor,speech_end=cursor+len(a)/24000,end=cursor+len(a)/24000+gap))
  parts.extend([a,np.zeros(round(gap*24000),dtype='<i2')]);cursor=rows[-1]['end'];print(mode,round(cursor,2),flush=True)
 pcm=np.concatenate(parts)
 with wave.open(str(ROOT/'配音/第七段_晓伊.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm.tobytes())
 (ROOT/'台词与时间轴.json').write_text(json.dumps(dict(lines=rows,intros=intros,duration=len(pcm)/24000),ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':asyncio.run(main())
