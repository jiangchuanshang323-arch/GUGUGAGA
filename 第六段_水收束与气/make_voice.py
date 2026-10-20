from pathlib import Path
import sys,asyncio,wave,json,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
for name in ('配音','检查','素材','.build'):(ROOT/name).mkdir(exist_ok=True)
sys.path.insert(0,str(PROJECT/'ocean_animation_demo_20261011/runtime'))
sys.path.insert(0,str(PROJECT/'正常异常对照_区域预测_v36/.runtime'))
import edge_tts,imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe()
LINES=[
 ('中国','先看我国东部。这张雨带图，横轴是时间，纵轴是纬度；蓝色越深，降水越多。'),
 ('雨带','厄尔尼诺通过环流影响雨带。次年夏季，长江流域持续降水可能增多，但每次情况不同。'),
 ('花海','换到阿塔卡马沙漠，适量降雨能唤醒休眠的种子，让荒漠开花。'),
 ('限定','花海说明水分条件改变，不能单凭一张照片，就认定是厄尔尼诺造成的。'),
 ('气','第二张，气。海洋不只输送水汽，也在储存和传递热量。'),
 ('交换','海面偏暖，海气之间的热交换随之改变。蒸发带走海水的热量；水汽凝结时，再向大气释放潜热。'),
 ('分配','厄尔尼诺会重新分配海洋与大气之间的热量，因而可能在短期内，推高全球平均地表温度。'),
 ('曲线','看这条真实观测曲线：年际之间有起伏，长期背景却在上升。短期波动，不等于长期变暖的全部原因。'),
 ('承下','热量和水汽改变了，生物会怎样回应？下一张，生。')]
async def main():
 parts=[np.zeros(4800,dtype='<i2')];cursor=.2;rows=[];intro=None
 for i,(mode,text) in enumerate(LINES):
  if mode=='气':intro=cursor;parts.append(np.zeros(48000,dtype='<i2'));cursor+=2
  out=ROOT/'配音'/f'{i:02d}_{mode}.mp3'
  if not out.exists():
   # User's standing project authorization covers new Xiaoyi narration scripts.
   await edge_tts.Communicate(text,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=45).save(str(out))
  raw=subprocess.check_output([FF,'-v','error','-i',str(out),'-ar','24000','-ac','1','-f','s16le','-'])
  a=np.frombuffer(raw,dtype='<i2');nz=np.flatnonzero(np.abs(a.astype(np.int32))>220)
  if len(nz):a=a[max(0,nz[0]-480):min(len(a),nz[-1]+600)]
  gap=.1 if i<len(LINES)-1 else .35
  rows.append(dict(mode=mode,text=text,start=cursor,speech_end=cursor+len(a)/24000,end=cursor+len(a)/24000+gap))
  parts.extend([a,np.zeros(round(gap*24000),dtype='<i2')]);cursor=rows[-1]['end'];print(mode,round(cursor,2),flush=True)
 pcm=np.concatenate(parts)
 with wave.open(str(ROOT/'配音/第六段_晓伊.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm.tobytes())
 (ROOT/'台词与时间轴.json').write_text(json.dumps(dict(lines=rows,title_intro_start=intro,duration=len(pcm)/24000),ensure_ascii=False,indent=2),encoding='utf-8')
 print('Total',len(pcm)/24000,flush=True)
if __name__=='__main__':asyncio.run(main())
