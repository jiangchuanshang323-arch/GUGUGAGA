from pathlib import Path
import sys, importlib.util, math, subprocess, json
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'ocean_animation_demo_20261011'
sys.path.insert(0,str(BASE/'runtime'))
import imageio_ffmpeg
spec=importlib.util.spec_from_file_location('ocean_demo',BASE/'build_demo.py')
demo=importlib.util.module_from_spec(spec);spec.loader.exec_module(demo)
W,H,FPS,DURATION=1280,720,24,68
FONT='C:/Windows/Fonts/msyh.ttc'
fonts={s:ImageFont.truetype(FONT,s) for s in (16,18,20,22,24,28,32,40,46,52,60)}
WHITE=(237,247,255); MUTED=(166,191,211); TEAL=(83,220,222); GOLD=(255,204,95)
actor=Image.open(ROOT/'角色透明素材.png').convert('RGBA')
actor=actor.crop(actor.getbbox())
sprites={h:actor.resize((round(actor.width*h/actor.height),h),Image.Resampling.LANCZOS) for h in (190,395,425)}

def ease(t,a,b):
    q=max(0,min(1,(t-a)/(b-a)));return q*q*(3-2*q)

def text(d,xy,s,size=24,color=WHITE,anchor=None):
    d.text(xy,s,font=fonts[size],fill=color,anchor=anchor)

def background(t):
    im=Image.new('RGB',(W,H),(8,23,42));d=ImageDraw.Draw(im)
    for y in range(H):
        q=y/H;d.line((0,y,W,y),fill=(int(8+q*5),int(23+q*12),int(42+q*18)))
    for k in range(4):
        pts=[(x,480+k*48+int(13*math.sin(x/130+t*.45+k))) for x in range(-10,W+20,10)]
        d.line(pts,fill=(23+k*2,55+k*4,75+k*4),width=2)
    for i in range(19):
        x=(i*137+41)%W;y=180+(i*91+int(t*10))%340
        d.ellipse((x,y,x+3,y+3),fill=(35,84,103))
    return im

def character(im,x,y,h,t,enter=True):
    # Cutout animation: whole-body sway and breathing, not generated lip sync.
    src=sprites[h]
    rot=src.rotate(math.sin(t*1.5)*1.15,resample=Image.Resampling.BICUBIC,expand=True)
    dx=round(math.sin(t*.95)*3);dy=round(math.sin(t*2)*4)
    if enter:dx-=round(100*(1-ease(t,0,1.2)))
    im.paste(rot,(int(x+dx),int(y+dy)),rot)

def footer(im,line,secondary=None):
    d=ImageDraw.Draw(im);d.rectangle((0,614,W,H),fill=(6,19,35))
    text(d,(640,632),line,28,WHITE,'ma')
    if secondary:text(d,(640,677),secondary,18,MUTED,'ma')

def intro(t):
    im=background(t);d=ImageDraw.Draw(im)
    text(d,(55,34),'海洋“发烧”了',46)
    text(d,(1220,53),'角色讲课样片  ·  无配音',18,TEAL,'ra')
    d.ellipse((67,494,438,533),fill=(11,24,38))
    character(im,80,169,425,t)
    d=ImageDraw.Draw(im)
    text(d,(525,202),'跟我一起，给海洋做个检查。',32)
    text(d,(525,263),'为什么一片海域的变化',40)
    text(d,(525,322),'能影响远方的天气？',40,TEAL)
    # Thermometer and subtle pulse, clearly a narrative metaphor.
    d.rounded_rectangle((1011,420,1041,528),radius=15,outline=MUTED,width=3)
    d.ellipse((1006,510,1046,550),fill=(255,128,88))
    hh=25+ease(t,1,9)*60
    d.rounded_rectangle((1021,520-hh,1031,532),radius=4,fill=(255,128,88))
    for i,s in enumerate(['测体征','查病因','追影响','谈应对']):
        x=525+i*117;text(d,(x,466),s,22,TEAL if t>=2+i*1.5 else MUTED)
    text(d,(525,518),'今天先看：信风与海水如何相互影响',22,MUTED)
    footer(im,'你好！今天我们来解释，海洋为什么会“发烧”。','角色引导  →  机制动画  →  思考与总结')
    return im

def chapter(t):
    im=background(t+12);d=ImageDraw.Draw(im)
    character(im,100,185,395,t+12,False)
    d=ImageDraw.Draw(im)
    text(d,(525,211),'第一站',28,GOLD)
    text(d,(525,272),'查病因',60)
    text(d,(525,362),'把镜头移到赤道太平洋。',28,TEAL)
    text(d,(525,422),'先看正常状态，再看它怎样变化。',24,MUTED)
    footer(im,'注意箭头：空气和海水都在运动。','橙红表示暖水，蓝色表示冷水；剖面为教学示意。')
    return im

def mechanism(t):
    im=demo.frame(min(t,43.99))
    # Margin inset stays out of the basin, labels, and caption area.
    character(im,1100,218,190,t+16,False)
    d=ImageDraw.Draw(im);text(d,(1190,426),'一起观察',16,GOLD,'ma')
    return im

def outro(t):
    im=background(t+60);character(im,90,173,425,t+60,False)
    d=ImageDraw.Draw(im)
    text(d,(525,202),'现在，轮到你来解释。',32,GOLD)
    text(d,(525,271),'信风减弱后，',40)
    text(d,(525,328),'海水和降水会怎样变化？',40,TEAL)
    lines=['① 暖水向东扩展','② 东侧上升流减弱','③ 对流与降水分布调整']
    if t>3:
        for i,s in enumerate(lines):
            if t>=3+i*.65:text(d,(525,409+i*47),s,24,WHITE)
    else:
        text(d,(525,438),'想一想，也可以暂停画面。',24,MUTED)
    footer(im,'从海洋到大气，这就是海—气相互作用。','实际影响随地区、季节及其他气候因素变化。')
    return im

def cut(t):
    if t<12:return intro(t)
    if t<16:return chapter(t-12)
    if t<60:return mechanism(t-16)
    return outro(t-60)

def frame(t):
    # Three 0.7-second crossfades, smooth but restrained.
    for b,left,right in [(12,intro,chapter),(16,chapter,mechanism),(60,mechanism,outro)]:
        if b-.35<=t<b+.35:
            lt=t if b==12 else t-12 if b==16 else t-16
            rt=max(0,t-b)
            return Image.blend(left(lt),right(rt),ease(t,b-.35,b+.35))
    im=cut(t)
    d=ImageDraw.Draw(im)
    d.rectangle((0,H-3,round(W*t/DURATION),H),fill=TEAL)
    return im

def main():
    out=ROOT/'企鹅主角_海洋发烧了_无配音样片.mp4'
    exe=imageio_ffmpeg.get_ffmpeg_exe()
    cmd=[exe,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),
      '-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=open(ROOT/'encode.log','w',encoding='utf-8'))
    for i in range(FPS*DURATION):
        im=frame(i/FPS)
        if i in [5*FPS,14*FPS,24*FPS,43*FPS,64*FPS,67*FPS]:im.save(ROOT/f'check_{i//FPS:02d}.png')
        p.stdin.write(im.tobytes())
        if i%(FPS*10)==0:print(f'rendered {i//FPS}/{DURATION}s',flush=True)
    p.stdin.close()
    if p.wait():raise RuntimeError('encoding failed')
    check=subprocess.run([exe,'-v','error','-i',str(out),'-f','null','-'],capture_output=True,text=True)
    if check.returncode:raise RuntimeError(check.stderr)
    frame(5).save(ROOT/'封面预览.png')
    (ROOT/'制作说明.txt').write_text('68秒，1280×720，24fps，无音轨。角色采用内置imagegen工具制作透明素材，提示词要点：保持原角色身份、企鹅服装、表情与举起鳍肢的姿态，移除白色背景、装饰线和旁边文字。角色动作是透明立绘的摆动、呼吸起伏和进出场，不是逐帧角色表演或口型同步。科学机制由本地程序绘制，成片含三处交叉淡化转场。',encoding='utf-8')
    print(json.dumps({'output':str(out),'bytes':out.stat().st_size,'duration':DURATION,'decode':'PASS'},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
