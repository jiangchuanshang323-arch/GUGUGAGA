from pathlib import Path
import sys, json, math, wave, subprocess, importlib.util, hashlib
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
for name in ('交付','检查','配音'):(ROOT/name).mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('lesson37',PROJECT/'环境多米诺_水_v37'/'build_part.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.load_audio()
EXE=m.EXE
ROWS={r['mode']:r for r in m.DATA};START=ROWS['西侧']['start'];END=ROWS['东侧']['end'];DURATION=END-START
ORIGINAL=m.reveal
CLOUD=m.p.native.v.CLOUD.copy().convert('RGBA').resize((260,156),Image.Resampling.LANCZOS)

def rain_cloud(layer,cx,cy,t,strength,opacity):
 if opacity<.005:return []
 # The icon is a moving convection/rain belt, not a redrawn SST field.
 a=Image.new('RGBA',layer.size);cloud=CLOUD.copy()
 cloud.putalpha(cloud.getchannel('A').point(lambda v:round(v*opacity)))
 top=round(cy-78);left=round(cx-130);a.alpha_composite(cloud,(left,top))
 d=ImageDraw.Draw(a);n=18
 for i in range(n):
  if (i*.61803398875)%1>strength:continue
  phase=(t*1.24+i*.381966)%1
  x=cx-85+(i%7)*27+3*math.sin(i*1.7)
  y=cy+30+phase*74
  alpha=round(205*opacity*math.sin(math.pi*phase))
  d.line((x,y,x-5,y+13),fill=(135,198,220,alpha),width=3)
  if phase>.88:
   d.arc((x-11,cy+109,x+8,cy+114),0,180,fill=(160,207,221,round(alpha*.6)),width=2)
 layer.alpha_composite(a)
 bounds=[left,top,left+260,cy+115]
 assert 65<=bounds[0]<bounds[2]<=1855 and 515<=bounds[1]<bounds[3]<=728,bounds
 return bounds

def reveal(mode,t,records):
 im=ORIGINAL(mode,t,records)
 if mode not in ('西侧','东侧'):return im
 west_age=max(0,t-ROWS['西侧']['start'])
 shift=m.ease((t-ROWS['东侧']['start'])/3.8)
 layer=Image.new('RGBA',im.size)
 # Western convection gradually thins; the rain belt reforms farther east.
 west_strength=(1-.70*m.ease(west_age/2.5))*(1-shift)
 rain_cloud(layer,550,600,t,west_strength,.93*(1-shift*.86))
 if shift>0:
  rain_cloud(layer,550+650*shift,600-4*math.sin(math.pi*shift),t,.35+.65*shift,shift)
 im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
 return im

m.reveal=reveal

def main():
 audio=ROOT/'配音'/'复用晓伊_西侧偏干与降雨东移.wav'
 pcm=m.PCM[round(START*24000):round(END*24000)]
 with wave.open(str(audio),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm.tobytes())
 out=ROOT/'交付'/'太平洋地图_云雨东移动效_demo_v38.mp4'
 args=[EXE,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(audio),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)]
 proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=subprocess.PIPE);audit=[];count=math.ceil(DURATION*24)
 for i in range(count):
  t=START+i/24;im,meta=m.render(t);audit.append(meta);proc.stdin.write(im.tobytes())
 proc.stdin.close();error=proc.stderr.read();assert proc.wait()==0,error
 check=subprocess.run([EXE,'-v','error','-i',str(out),'-f','null','-'],capture_output=True);assert check.returncode==0 and not check.stderr,check.stderr
 contact=Image.new('RGB',(1920,600),'#e4eded');d=ImageDraw.Draw(contact)
 for i,t in enumerate([.3,2.0,3.4,5.0,7.0,10.0]):
  t=min(t,DURATION-.1);im,_=m.render(START+t);im.save(ROOT/'检查'/f'节点_{i}.png');x=i%3*640;y=i//3*300
  contact.paste(im.resize((533,300),Image.Resampling.LANCZOS),(x,y));d.text((x+545,y+10),str(t),fill=m.INK)
 contact.save(ROOT/'检查'/'云雨连续运动.jpg',quality=95)
 (ROOT/'检查'/'逐帧文字边界.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 report=dict(output=str(out),seconds=DURATION,resolution=[1920,1080],fps=24,frames_checked=count,decode='PASS',visual_review='待抽帧复核',audio='复用v37两句晓伊，无新语音请求',source_times=[START,END],original_v37_unchanged=True,camera_fixed=True,cloud_safe_vertical_range=[515,728],sha256=hashlib.sha256(out.read_bytes()).hexdigest())
 (ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
