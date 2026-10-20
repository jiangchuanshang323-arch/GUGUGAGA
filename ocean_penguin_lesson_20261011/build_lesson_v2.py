from pathlib import Path
import sys, importlib.util, math, subprocess, json
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('lesson_v1',ROOT/'build_lesson.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)
atlas=Image.open(ROOT/'角色动作图集_v2.png').convert('RGBA')
cw,ch=atlas.width//3,atlas.height//2
poses=[]
for j in range(2):
    for i in range(3):
        poses.append(atlas.crop((i*cw,j*ch,(i+1)*cw,(j+1)*ch)))
cache={(p,h):poses[p].resize((round(cw*h/ch),h),Image.Resampling.LANCZOS)
       for p in range(6) for h in (190,395,425)}

def pose_at(t):
    # Gestures follow teaching intent rather than loop randomly.
    if t<2.4:return 1 # greeting
    if t<5:return 5 # explain
    if t<8:return 2 # point
    if t<11:return 3 # think
    if t<16:return 2 # introduce mechanism
    if t<27:return 5 if (t-16)%6<3 else 0
    if t<37:return 2
    if t<48:return 5 if (t-37)%6<3 else 2
    if t<60:return 5 if (t-48)%6<3 else 0
    if t<63:return 3
    if t<65:return 2
    return 5

def character(im,x,y,h,t,enter=True):
    pose=pose_at(t)
    # Brief closed-eye expression on neutral pauses, not a permanent smile.
    if pose==0 and 2.65<t%3.7<2.84:pose=4
    src=cache[(pose,h)]
    # Inset presenter faces the diagram to its left.
    if h==190:
        src=src.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        x=1078
    rot=src.rotate(math.sin(t*1.8)*.55,resample=Image.Resampling.BICUBIC,expand=False)
    dx=round(math.sin(t*.9)*2);dy=round(math.sin(t*2)*2)
    if enter:dx-=round(100*(1-lesson.ease(t,0,1.2)))
    im.paste(rot,(round(x+dx),round(y+dy)),rot)

lesson.character=character

def main():
    out=ROOT/'企鹅主角_动作升级版_v2.mp4'
    exe=lesson.imageio_ffmpeg.get_ffmpeg_exe()
    cmd=[exe,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','24',
      '-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
    with open(ROOT/'encode_v2.log','w',encoding='utf-8') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        for i in range(24*68):
            im=lesson.frame(i/24)
            if i in [24,6*24,9*24,29*24,50*24,61*24,66*24]:im.save(ROOT/f'v2_check_{i//24:02d}.png')
            p.stdin.write(im.tobytes())
            if i%240==0:print(f'rendered {i//24}/68s',flush=True)
        p.stdin.close()
        if p.wait():raise RuntimeError('encoding failed')
    r=subprocess.run([exe,'-v','error','-i',str(out),'-f','null','-'],capture_output=True,text=True)
    if r.returncode:raise RuntimeError(r.stderr)
    lesson.frame(6).save(ROOT/'动作升级版预览.png')
    (ROOT/'动作升级版说明.txt').write_text('68秒，无音轨。六姿势：放下鳍肢、招手、指向图表、托腮思考、闭眼微笑、展开鳍肢讲解。根据教学内容切换姿势，加入短暂眨眼；采用多姿势二维动画，不是骨骼动画或口型同步。素材由内置imagegen工具根据原角色生成，提示词要求3列2行透明图集，保持企鹅服装、脸、发型和配饰一致。',encoding='utf-8')
    print(json.dumps({'output':str(out),'duration':68,'bytes':out.stat().st_size,'decode':'PASS'},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
