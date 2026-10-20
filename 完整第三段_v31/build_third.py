from pathlib import Path
import sys,importlib.util,subprocess,json,re,hashlib,math
from PIL import ImageDraw,Image
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
for f in ('交付','.build','检查'):(ROOT/f).mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(PROJECT/'主体课程'/'上抛后恢复普通姿势_v23'))
import build_v23 as actor
spec=importlib.util.spec_from_file_location('diagram30',PROJECT/'固定剖面_局部强调_v30'/'build_demo.py')
diagram=importlib.util.module_from_spec(spec);spec.loader.exec_module(diagram)
EXE=diagram.v.EXE
OLD=PROJECT/'合成成片_20261013_v23'/'海洋发烧了_第三段_普通姿势卷轴_v23.mp4'
NEW=PROJECT/'固定剖面_局部强调_v30'/'交付'/'厄尔尼诺_固定剖面逐句讲解_v30.mp4'
FPS=24;PREFIX_FRAMES=math.ceil(actor.v.BRIDGE_START*FPS);PREFIX_END=PREFIX_FRAMES/FPS
BRIDGE_FRAMES=math.ceil((actor.v.BRIDGE_END-actor.v.BRIDGE_START)*FPS);BRIDGE_LEN=BRIDGE_FRAMES/FPS
BRIDGE=ROOT/'.build'/'卷轴转场_新剖面.mp4'
OUT=ROOT/'交付'/'海洋发烧了_完整第三段_v31.mp4'
poster,_=diagram.render(0)
ImageDraw.Draw(poster).rectangle((0,958,1920,1080),fill='#244b60')
actor.s.POSTER=poster

def info(path):
 data=subprocess.run([EXE,'-hide_banner','-i',str(path)],capture_output=True).stderr.decode('utf-8','replace')
 match=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',data)
 h,m,s=map(float,match.groups())
 return {'file':str(path),'seconds':h*3600+m*60+s,'streams':[line.strip() for line in data.splitlines() if 'Stream #' in line]}

def main():
 print('Render approved penguin action with v30 scroll artwork',flush=True)
 process=subprocess.Popen([EXE,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-',
 '-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-vf','setsar=1',
 '-c:a','aac','-t',str(BRIDGE_LEN),'-movflags','+faststart',str(BRIDGE)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 for n in range(BRIDGE_FRAMES):
  age=2.8*n/(BRIDGE_FRAMES-1)
  process.stdin.write(actor.transition(age).tobytes())
 process.stdin.close();err=process.stderr.read();assert process.wait()==0,err
 print('Join energy explanation, scroll, and v30 narration',flush=True)
 filters=(f'[0:v]trim=end_frame={PREFIX_FRAMES},setpts=PTS-STARTPTS,setsar=1,fps=24[v0];'
 f'[0:a]atrim=end={PREFIX_END},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a0];'
 f'[1:v]setpts=PTS-STARTPTS,setsar=1,fps=24[v1];[1:a]atrim=end={BRIDGE_LEN},asetpts=PTS-STARTPTS[a1];'
 '[2:v]setpts=PTS-STARTPTS,setsar=1,fps=24[v2];[2:a]asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a2];'
 '[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]')
 subprocess.run([EXE,'-y','-v','error','-i',str(OLD),'-i',str(BRIDGE),'-i',str(NEW),'-filter_complex',filters,
 '-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-r','24','-c:a','aac','-b:a','160k','-movflags','+faststart',str(OUT)],check=True)
 check=subprocess.run([EXE,'-v','error','-i',str(OUT),'-f','null','-'],capture_output=True)
 assert check.returncode==0 and not check.stderr,check.stderr
 diagram_start=PREFIX_END+BRIDGE_LEN
 times=[PREFIX_END-.15,PREFIX_END+.6,PREFIX_END+1.12,PREFIX_END+1.4,PREFIX_END+2.4,diagram_start-.04,diagram_start+.25,diagram_start+20.1]
 sheet=Image.new('RGB',(1920,580),'#e5ecee');sd=ImageDraw.Draw(sheet)
 for n,t in enumerate(times):
  p=ROOT/'检查'/f'接续_{n+1}.png'
  subprocess.run([EXE,'-y','-v','error','-ss',str(t),'-i',str(OUT),'-frames:v','1',str(p)],check=True)
  image=Image.open(p).convert('RGB');x=n%4*480;y=n//4*290
  sheet.paste(image.resize((480,270),Image.Resampling.LANCZOS),(x,y));sd.text((x+8,y+273),f'{t:.3f}s',fill='#274e61')
 sheet.save(ROOT/'检查'/'卷轴接续检查.jpg',quality=94)
 report={'output':info(OUT),'decode':'PASS','new_voice_synthesis':False,'old_diagram_replaced_not_repeated':True,'scroll_contains_v30_art':True,
 'energy_prefix_end':PREFIX_END,'bridge_seconds':BRIDGE_LEN,'v30_start':diagram_start,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
 'inputs':[info(OLD),info(NEW)],'visual_review':'待检查卷轴及新图解接续联系表'}
 assert abs(report['output']['seconds']-(diagram_start+37.69))<.15
 (ROOT/'合成验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report['output'],ensure_ascii=False),flush=True)

if __name__=='__main__':main()
