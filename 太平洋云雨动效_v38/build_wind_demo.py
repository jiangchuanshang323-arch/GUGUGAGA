from pathlib import Path
import importlib.util,math,json,subprocess,hashlib
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
OUTDIR=PROJECT/'demooo'/'预览'/'太平洋云雨';OUTDIR.mkdir(parents=True,exist_ok=True)
CHECK=ROOT/'检查'/'风线';CHECK.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('cloud38',ROOT/'build_demo.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
m=v.m;BASE=v.ORIGINAL

def wind_scene(mode,t,records):
 im=BASE(mode,t,records)
 if mode not in ('西侧','东侧'):return im
 age=max(0,t-v.START);weak=m.ease(age/7.2)
 # Easterly trades stay east-to-west. Their paths shorten and flow slows.
 layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
 for row in range(3):
  right=1380-row*46;length=690-300*weak-row*45;left=right-length
  yy=456+row*26
  def xy(u):return right-length*u,yy+3*math.sin(u*math.pi*2+row*.7)
  pts=[xy(i/90) for i in range(91)]
  alpha=round(150-47*weak)
  d.line(pts,fill=(177,213,222,alpha),width=3,joint='curve')
  # Each moving breeze is a short curved dash, fading at both ends of its path.
  for j in range(3):
   q=(age*(.28-.07*weak)+j/3+row*.13)%1
   a=max(0,q-.085);b=min(.975,q+.055)
   segment=[xy(a+(b-a)*k/18) for k in range(19)]
   fade=min(1,q/.12,(1-q)/.12)
   d.line(segment,fill=(213,239,240,round((225-35*weak)*max(0,fade))),width=4,joint='curve')
  # A small westward head stays aligned with the shortened shaft.
  x,y=pts[-1];d.polygon([(x,y),(x+11,y-5),(x+10,y+5)],fill=(177,213,222,alpha))
  assert 530<left<right<1430 and 448<min(y for _,y in pts)<max(y for _,y in pts)<520
 im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
 m.text(im,'东风信风减弱',1040,410,29,'#91b9c9',True,records)
 return im

v.ORIGINAL=wind_scene

def main():
 out=OUTDIR/'.太平洋云雨.pending.mp4';audio=ROOT/'配音'/'复用晓伊_西侧偏干与降雨东移.wav'
 args=[v.EXE,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(audio),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)]
 proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=subprocess.PIPE);audit=[];count=math.ceil(v.DURATION*24)
 for i in range(count):
  im,meta=m.render(v.START+i/24);audit.append(meta);proc.stdin.write(im.tobytes())
 proc.stdin.close();err=proc.stderr.read();assert proc.wait()==0,err
 test=subprocess.run([v.EXE,'-v','error','-i',str(out),'-f','null','-'],capture_output=True);assert test.returncode==0 and not test.stderr,test.stderr
 contact=Image.new('RGB',(1920,1120),'#e7efee');d=ImageDraw.Draw(contact)
 for i,t in enumerate([.4,3.0,6.7,10.0]):
  im,_=m.render(v.START+t);im.save(CHECK/f'节点_{t}.png');im=im.resize((960,540),Image.Resampling.LANCZOS);x=i%2*960;y=i//2*560;contact.paste(im,(x,y));d.text((x+8,y+543),str(t),fill=m.INK)
 contact.save(CHECK/'风线与云雨.jpg',quality=95)
 (CHECK/'逐帧检查.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 report={'pending':str(out),'output':str(OUTDIR/'海洋发烧了_太平洋云雨.mp4'),'seconds':v.DURATION,'resolution':[1920,1080],'fps':24,'frames_checked':count,'decode':'PASS','visual_review':'待视觉抽查','wind_direction':'东→西，路径渐短、流速渐缓','full_segment_unchanged':True,'audio':'复用原11秒晓伊，无新语音请求','sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
 (CHECK/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
