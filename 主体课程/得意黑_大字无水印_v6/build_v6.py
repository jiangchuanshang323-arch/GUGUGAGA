from pathlib import Path
import sys,json,wave,math,inspect,subprocess,ast
import numpy as np
from PIL import Image,ImageFont
ROOT=Path(__file__).resolve().parent
V5=ROOT.parent/'去水印_紧凑配音_v5'
V4=ROOT.parent/'开场衔接_两端对齐_v4'
sys.path.insert(0,str(V4))
import build_joined_video as v
sys.path.insert(0,str(V5/'runtime'))
import cv2
b=v.b
stats=json.loads((V5/'停顿调整.json').read_text(encoding='utf-8'))
b.DATA=json.loads((V5/'配音时间轴.json').read_text(encoding='utf-8'))
def pcm(path):
    with wave.open(str(path),'rb') as w:return w.getframerate(),np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
b.RATE,b.PCM=pcm(V5/'配音'/'正文紧凑.wav')
v.RATE,v.PCM=pcm(V5/'配音'/'衔接与正文紧凑.wav')
v.BRIDGE=stats['bridge_seconds'];v.DURATION=stats['middle_seconds'];b.DURATION=stats['body_seconds']
v.INFO={'bridge_speech':[{'text':'咕咕嘎嘎！欢迎来到水下课堂。'}]}
b.F={s:ImageFont.truetype(str(ROOT/'素材'/'SmileySans-Oblique.ttf'),s) for s in range(18,97)}
b.balanced_lines.cache_clear();v.justified_positions.cache_clear();v.bubble_layout.cache_clear()
old_bubble=v.bubble
def bubble(s,message,tip):
    start=len(s.items);old_bubble(s,message,tip)
    for a in s.items[start:]:
        if a['kind']=='text':a['bubble']=True
v.bubble=bubble
old_scene=v.scene
sizes={52:64,46:56,42:56,40:46,38:48,36:44,34:44,32:42,31:38,29:40,28:34,26:32,25:29,24:30,22:28}
def scene(t):
    s=old_scene(t)
    for a in s.items:
        if a['kind']!='text' or a.get('bubble'):continue
        size=sizes.get(a['size'],a['size'])
        # Preserve existing information and geometry; choose the largest size that fits.
        while max(b.F[size].getlength(line) for line in a['text'].split('\n'))>a['w']+2:size-=1
        a['size']=size;a['lineHeight']=round(size*1.35);a['h']=a['lineHeight']*len(a['text'].split('\n'))+8
    return s
# Retain the established renderer, replacing glyph-top alignment by a shared baseline.
source=inspect.getsource(v.render).replace('s=scene(t);','s=scene(t);')
source=source.replace("fw=b.F[a['size']].getlength(line)","fw=b.F[a['size']].getlength(line);y+=b.F[a['size']].getmetrics()[0]")
source=source.replace("anchor='lt'","anchor='ls'")
env=dict(v.__dict__);env['scene']=scene
exec(source,env);render=env['render']
EXE=b.imageio_ffmpeg.get_ffmpeg_exe()
def preview():
    for i,t in enumerate((v.BRIDGE+1,v.BRIDGE+b.DATA[-1]['start']+.3,3)):
        render(t).save(ROOT/'.build'/f'预览_{i}.png')
    print('Previews ready',flush=True)
def main():
    preview()
    src=V5/'.build'/'开场_字形修补.mp4';clean=ROOT/'.build'/'开场_双水印处理.mp4'
    cap=cv2.VideoCapture(str(src));fps=cap.get(cv2.CAP_PROP_FPS);width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    mask=np.zeros((height,width),dtype=np.uint8);mask[19:65,20:108]=255
    cmd=[EXE,'-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{width}x{height}','-r',str(fps),'-i','-','-i',str(src),'-map','0:v','-map','1:a','-c:v','libx264','-crf','18','-preset','fast','-c:a','copy','-shortest',str(clean)]
    with open(ROOT/'.build'/'opening.log','w') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        while True:
            ok,frame=cap.read()
            if not ok:break
            frame=cv2.inpaint(frame,mask,3,cv2.INPAINT_TELEA);p.stdin.write(frame.tobytes())
        cap.release();p.stdin.close();assert p.wait()==0
    middle=ROOT/'.build'/'正文_得意黑.mp4'
    cmd=[EXE,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(V5/'配音'/'衔接与正文紧凑.wav'),'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(middle)]
    with open(ROOT/'.build'/'body.log','w') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        for n in range(math.ceil(v.DURATION*24)):
            p.stdin.write(render(n/24).tobytes())
            if n%240==0:print(f'Render {n/24:.0f}/{v.DURATION:.1f}s',flush=True)
        p.stdin.close();assert p.wait()==0
    tree=ast.parse((V5/'build_v5.py').read_text(encoding='utf-8'))
    graph=next(ast.literal_eval(a.value) for a in ast.walk(tree) if isinstance(a,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='graph' for x in a.targets))
    final=ROOT/'交付'/'海洋发烧了_得意黑_大字无水印_v6.mp4'
    cmd=[EXE,'-y','-i',str(clean),'-i',str(middle),'-filter_complex',graph,'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)]
    with open(ROOT/'.build'/'join.log','w') as log:subprocess.run(cmd,stderr=log,stdout=log,check=True)
    check=subprocess.run([EXE,'-v','error','-i',str(final),'-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace');assert check.returncode==0,check.stderr
    for t in (1,6):subprocess.run([EXE,'-v','error','-ss',str(t),'-i',str(clean),'-frames:v','1','-y',str(ROOT/'.build'/f'开场检查_{t}.png')],check=True)
    report={'font':'Smiley Sans / 得意黑','text_alignment':'shared baseline, justified bubble, last line left','original_text_preserved':True,'audio_reused':True,'watermarks_processed':['小云雀','AI生成'],'full_decode':'PASS','output':str(final),'bytes':final.stat().st_size}
    (ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(str(final),flush=True)
if __name__=='__main__':
    if '--preview' in sys.argv:preview()
    else:main()
