"""Preview only: enlarge chapter seal, then dock it without retiming the scene."""
from pathlib import Path
import importlib.util,sys,math,subprocess,wave,json,hashlib
from PIL import Image,ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('lesson_preview',ROOT/'update_parts.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
from refine_components import install
install(o)
TITLE='追并发症·环境多米诺';o.HIDE_CHAPTER=TITLE
START=o.CUT+1+1.3;BEGIN=START-1.15;DURATION=8
ART=o.p.header(TITLE,'自然环境具有整体性')
def render(t):
 absolute=BEGIN+t;im=o.render5(absolute)
 if absolute<START:return im
 age=absolute-START
 if age<.18:
  q=o.m.ease(age/.18);scale=1.98+.17*q;cx,cy=960,540;alpha=q
 elif age<1.0:scale=2.15;cx,cy=960,540;alpha=1
 elif age<2.0:
  q=o.m.ease(age-1);scale=2.15-1.15*q
  cx=960*(1-q)+(16+ART.width/2)*q;cy=540*(1-q)+(14+ART.height/2)*q;alpha=1
 else:scale=1;cx=16+ART.width/2;cy=14+ART.height/2;alpha=1
 art=ART.resize((round(ART.width*scale),round(ART.height*scale)),Image.Resampling.LANCZOS)
 if alpha<1:art.putalpha(art.getchannel('A').point(lambda x:round(x*alpha)))
 x=round(cx-art.width/2);y=round(cy-art.height/2)
 assert 0<=x and x+art.width<=1920 and 0<=y and y+art.height<=1080
 im.paste(art,(x,y),art);return im

def main():
 dest=o.PROJECT/'demooo'/'预览'/'章节标题入场'/'海洋发烧了_章节标题入场.mp4';dest.parent.mkdir(parents=True,exist_ok=True)
 # Existing narration and push Foley continue unchanged. The 2s title beat fits
 # entirely inside the original silent 2.5s board entry.
 with wave.open(str(ROOT/'part5.wav'),'rb') as w:
  rate=w.getframerate();w.setpos(round(BEGIN*rate));pcm=w.readframes(round(DURATION*rate))
 audio=ROOT/'章节标题样片.wav'
 with wave.open(str(audio),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(pcm)
 assert START+2<=o.STOP
 contact=Image.new('RGB',(1920,580),'#e6eeee');d=ImageDraw.Draw(contact)
 for i,age in enumerate([0.15,.65,1.15,1.5,1.85,2.05,2.8,4.8]):
  t=START-BEGIN+age;im=render(t);im.save(ROOT/'检查'/f'标题入场_{age}.png');x=i%4*480;y=i//4*290;contact.paste(im.resize((480,270)),(x,y));d.text((x+6,y+272),str(age)+'s',fill='black')
 contact.save(ROOT/'检查'/'标题入场_节点.jpg')
 pending=dest.with_name('.'+dest.stem+'.pending.mp4')
 proc=subprocess.Popen([o.EXE,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(audio),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(pending)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 for i in range(round(DURATION*24)):proc.stdin.write(render(i/24).tobytes())
 proc.stdin.close();error=proc.stderr.read();assert proc.wait()==0,error
 test=subprocess.run([o.EXE,'-v','error','-i',str(pending),'-f','null','-'],capture_output=True);assert test.returncode==0 and not test.stderr,test.stderr
 pending.replace(dest)
 report=dict(path=str(dest),seconds=DURATION,title_hold_seconds=1,title_dock_seconds=1,title_lands_before_speech=True,existing_animation_unchanged=True,full_video_unchanged=True,decode='PASS',sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
 (ROOT/'章节标题样片_验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()

