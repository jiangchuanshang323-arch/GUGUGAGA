from pathlib import Path
import sys,math,json,wave,subprocess,hashlib,re
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
for folder in ('交付','.build','检查','配音'):(ROOT/folder).mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(PROJECT/'主体课程'/'出入场_无制作提示_v9'))
import build_v9 as c
EXE=c.EXE
OLD_ROWS=json.loads(json.dumps(c.DATA,ensure_ascii=False))
INSERT=next(r['end'] for r in OLD_ROWS if r['mode']=='增暖')
DEFROW=json.loads((PROJECT/'固定剖面_局部强调_v30'/'保留的逐句时间轴.json').read_text(encoding='utf-8'))[10]
with wave.open(str(PROJECT/'精绘厄尔尼诺_讲解演示_v28'/'配音'/'精绘演示_晓伊.wav'),'rb') as w:
 raw=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
 definition=raw[round(DEFROW['start']*24000):round(DEFROW['end']*24000)]
with wave.open(str(PROJECT/'主体课程'/'出入场_无制作提示_v9'/'配音'/'复用台词_标题衔接.wav'),'rb') as w:
 old=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
DELTA=len(definition)/24000;cut=round(INSERT*24000)
pcm=np.concatenate([old[:cut],definition,old[cut:]])
AUDIO=ROOT/'配音'/'第一段_原配音加概念说明.wav'
with wave.open(str(AUDIO),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm.tobytes())
c.PCM=pcm.astype(np.float32)/32768;c.DURATION=len(pcm)/24000
for row in c.DATA:
 if row['start']>=INSERT-1e-8:row['start']+=DELTA;row['end']+=DELTA
c.DATA.append({'mode':'增暖','pose':3,'text':DEFROW['text'],'start':INSERT,'end':INSERT+DELTA})
c.DATA.sort(key=lambda r:r['start'])
source=(PROJECT/'标题页与自绘图解_v25'/'正文样式替换.patch.txt').read_text(encoding='utf-8')
exec(source,c.__dict__)
base_scene=c.scene
COVER=PROJECT/'封面蓝色海面_v27'/'交付'/'海洋发烧了_蓝色海面封面_v27.png'
def scene(t):
 if t<c.TITLE:
  s=c.b.Scene();s.image(str(COVER),0,0,1920,1080);return s
 return base_scene(t)
c.env['scene']=scene
BODY=ROOT/'.build'/'第一段_封面字级概念修订.mp4'
OPENING=PROJECT/'主体课程'/'得意黑_大字无水印_v6'/'.build'/'开场_双水印处理.mp4'
SECOND=PROJECT/'主体课程'/'横梁起卷_双手下拉_v14'/'交付'/'海洋发烧了_第二分钟_双手卷板_v14.mp4'
THIRD=PROJECT/'完整第三段_v31'/'交付'/'海洋发烧了_完整第三段_v31.mp4'
OUT=ROOT/'交付'/'海洋发烧了_目前阶段新版_v32.mp4'

def media_info(path):
 data=subprocess.run([EXE,'-hide_banner','-i',str(path)],capture_output=True).stderr.decode('utf-8','replace')
 m=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',data);h,mi,s=map(float,m.groups())
 return {'file':str(path),'seconds':h*3600+mi*60+s,'streams':[line.strip() for line in data.splitlines() if 'Stream #' in line]}

def main():
 for t,name in [(.8,'新封面'),(next(r['start'] for r in c.DATA if r['mode']=='观察')+.5,'案例大字'),(INSERT+.5,'概念补充')]:
  c.render(t).save(ROOT/'检查'/(name+'.png'))
 if '--preview' in sys.argv:return
 count=math.ceil(c.DURATION*24)
 cmd=[EXE,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(AUDIO),
 '-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p','-vf','setsar=1','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(BODY)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 for n in range(count):
  proc.stdin.write(c.render(n/24).tobytes())
  if n%120==0:print(f'First segment {n}/{count}',flush=True)
 proc.stdin.close();err=proc.stderr.read();assert proc.wait()==0,err
 print('Join opening and all three latest segments',flush=True)
 parts=[OPENING,BODY,SECOND,THIRD]
 graph=[]
 for i in range(4):
  graph.append(f'[{i}:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24,setpts=PTS-STARTPTS[v{i}]')
  graph.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a{i}]')
 graph.append(''.join(f'[v{i}][a{i}]' for i in range(4))+'concat=n=4:v=1:a=1[v][a]')
 args=[EXE,'-y','-v','error']
 for part in parts:args+=['-i',str(part)]
 args+=['-filter_complex',';'.join(graph),'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-r','24','-c:a','aac','-b:a','160k','-movflags','+faststart',str(OUT)]
 subprocess.run(args,check=True)
 check=subprocess.run([EXE,'-v','error','-i',str(OUT),'-f','null','-'],capture_output=True)
 assert check.returncode==0 and not check.stderr,check.stderr
 info=[media_info(p) for p in parts];output=media_info(OUT)
 assert abs(output['seconds']-sum(p['seconds'] for p in info))<.3
 starts=[0]
 for p in info[:-1]:starts.append(starts[-1]+p['seconds'])
 times=[starts[1]+.5,starts[1]+10,starts[1]+INSERT+.7,starts[2]-.2,starts[2]+.3,starts[3]-.3,starts[3]+.3,starts[3]+19.2]
 sheet=Image.new('RGB',(1920,580),'#e6eded');d=ImageDraw.Draw(sheet)
 for i,t in enumerate(times):
  p=ROOT/'检查'/f'成片检查_{i+1}.png'
  subprocess.run([EXE,'-y','-v','error','-ss',str(t),'-i',str(OUT),'-frames:v','1',str(p)],check=True)
  image=Image.open(p).convert('RGB');x=i%4*480;y=i//4*290
  sheet.paste(image.resize((480,270),Image.Resampling.LANCZOS),(x,y));d.text((x+8,y+273),f'{t:.2f}s',fill='#274e61')
 sheet.save(ROOT/'检查'/'阶段成片接续检查.jpg',quality=94)
 report={'output':output,'inputs':info,'segment_start_seconds':starts,'decode':'PASS','opening_count':1,'old_third_included':False,
 'cover':'v27 blue-ocean photograph and gradient lettering','case_header':63,'case_caption':52,'definition_added_in_first_segment':DEFROW['text'],
 'new_voice_synthesis':False,'definition_reused_from_v30_seconds':[DEFROW['start'],DEFROW['end']],
 'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'visual_review':'待抽帧复核','scope':'已完成开场与前三段，尚未完成整课'}
 (ROOT/'合成验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'第一段修订时间轴.json').write_text(json.dumps(c.DATA,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(output,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
