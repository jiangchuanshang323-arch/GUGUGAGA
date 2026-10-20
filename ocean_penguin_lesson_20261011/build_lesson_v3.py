from pathlib import Path
import importlib.util, subprocess, json
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gestures',ROOT/'build_lesson_v2.py')
v2=importlib.util.module_from_spec(spec);spec.loader.exec_module(v2)
L=v2.lesson
for p in range(6):
    v2.cache[(p,245)]=v2.poses[p].resize((245,245),Image.Resampling.LANCZOS)

def wrap(s,font,width):
    lines=[];line=''
    for c in s:
        if c=='\n':
            if line:lines.append(line)
            line=''
            continue
        if font.getlength(line+c)>width and line:
            if c in '，。？！：；”）':
                lines.append(line[:-1]);line=line[-1]+c
                continue
            lines.append(line);line=c
        else:line+=c
    if line:lines.append(line)
    return lines

def bubble(im,box,message,tip,age,size=28):
    x,y,w,h=box
    layer=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(layer)
    fill=(239,249,252,255);ink=(16,49,69,255);edge=(95,221,220,255)
    d.rounded_rectangle((x+4,y+6,x+w+4,y+h+6),radius=24,fill=(0,0,0,80))
    # The tail connects the speech panel to the presenter's head.
    if tip[0]<x:
        tri=[(x+3,y+h*.52),(x+3,y+h*.74),tip]
    else:
        tri=[(x+w*.48,y+h-3),(x+w*.66,y+h-3),tip]
    d.polygon(tri,fill=fill)
    d.rounded_rectangle((x,y,x+w,y+h),radius=24,fill=fill,outline=edge,width=2)
    font=L.fonts[size]
    lines=wrap(message,font,w-52)
    height=len(lines)*(size+13)
    yy=y+(h-height)/2-2
    for line in lines:
        d.text((x+26,yy),line,font=font,fill=ink);yy+=size+13
    alpha=L.ease(age,0,.3)
    if alpha<1:
        layer.putalpha(layer.getchannel('A').point(lambda a:round(a*alpha)))
    im.paste(layer,(0,0),layer)

def header(im,label):
    d=ImageDraw.Draw(im)
    L.text(d,(55,29),'海洋“发烧”了',40)
    L.text(d,(1224,50),label,18,L.TEAL,'ra')

def intro(t):
    im=L.background(t);header(im,'角色气泡字幕版 · 无配音')
    v2.character(im,65,190,395,t)
    d=ImageDraw.Draw(im)
    L.text(d,(500,158),'跟我一起，给海洋做个检查',32,L.TEAL)
    if t<4:
        msg='你好！今天我们来解释：\n海洋为什么会“发烧”？';start=0
    elif t<8:
        msg='为什么一片海域的变化，能影响远方的天气？';start=4
    else:
        msg='今天先看：信风与海水如何相互影响。';start=8
    bubble(im,(495,230,720,180),msg,(380,325),t-start,32)
    d=ImageDraw.Draw(im)
    for i,s in enumerate(['测体征','查病因','追影响','谈应对']):
        L.text(d,(505+i*175,478),s,24,L.GOLD if i==1 else L.MUTED)
    L.text(d,(505,552),'角色引导 → 机制动画 → 思考与总结',20,L.MUTED)
    return im

def chapter(t):
    im=L.background(t+12);header(im,'第一站 · 查病因')
    v2.character(im,65,190,395,t+12,False)
    d=ImageDraw.Draw(im);L.text(d,(500,176),'查病因',52,L.GOLD)
    bubble(im,(495,278,720,180),'把镜头移到赤道太平洋。\n注意箭头：空气和海水都在运动。',(380,353),t,28)
    d=ImageDraw.Draw(im);L.text(d,(505,524),'橙红表示暖水；蓝色表示冷水。',22,L.MUTED)
    return im

SPEECH=[
 (0,'正常年份，信风推动\n表层暖水向西堆积。'),
 (5.5,'西侧暖水较厚，\n东侧冷水上涌较强。'),
 (11,'当信风减弱，\n暖水开始向东扩展。'),
 (16,'海洋变化与大气变化\n彼此作用。'),
 (21,'中东太平洋增暖，\n东侧上升流受到抑制。'),
 (26.5,'对流与降水分布调整，\n沃克环流减弱并位移。'),
 (32,'海—气耦合变化，\n还能影响远方的\n天气与生态。'),
 (38,'实际影响随地区、季节\n及其他气候因素变化。')]

def mechanism(t):
    im=L.background(t+16);header(im,'机制讲解 · 一起观察')
    d=ImageDraw.Draw(im)
    stages=['正常状态','信风减弱','暖水向东扩展','海气相互响应']
    stage=0 if t<11 else 1 if t<21 else 2 if t<32 else 3
    for i,s in enumerate(stages):
        L.text(d,(40+i*225,116),f'{i+1}  {s}',20,L.TEAL if i==stage else L.MUTED)
    # Give the diagram and speaker separate regions; speech never covers arrows.
    panel=L.demo.frame(min(t,43.99)).crop((120,170,1185,610)).resize((860,355),Image.Resampling.LANCZOS)
    im.paste(panel,(35,224))
    v2.character(im,970,430,245,t+16,False)
    start,msg=next((a,s) for a,s in reversed(SPEECH) if t>=a)
    bubble(im,(924,194,320,204),msg,(1090,450),t-start,24)
    d=ImageDraw.Draw(im)
    L.text(d,(40,620),'信风 · 海水分布 · 大气环流',28,L.TEAL)
    L.text(d,(40,670),'赤道太平洋剖面示意 · 非按比例',18,L.MUTED)
    return im

def outro(t):
    im=L.background(t+60);header(im,'思考与总结')
    v2.character(im,65,190,395,t+60,False)
    if t<3:
        msg='轮到你来解释：信风减弱后，海水和降水会怎样变化？';start=0
    else:
        msg='从海洋到大气，这就是海—气相互作用。';start=3
    bubble(im,(495,215,720,170),msg,(380,322),t-start,28)
    d=ImageDraw.Draw(im)
    if t>=3:
        for i,s in enumerate(['① 暖水向东扩展','② 东侧上升流减弱','③ 对流与降水分布调整']):
            if t>=3+i*.65:L.text(d,(520,432+i*52),s,24,L.WHITE)
    else:L.text(d,(520,467),'想一想，也可以暂停视频。',24,L.GOLD)
    return im

def frame(t):
    for b,left,right in [(12,intro,chapter),(16,chapter,mechanism),(60,mechanism,outro)]:
        if b-.35<=t<b+.35:
            lt=t if b==12 else t-12 if b==16 else t-16
            im=Image.blend(left(lt),right(max(0,t-b)),L.ease(t,b-.35,b+.35))
            break
    else:
        im=intro(t) if t<12 else chapter(t-12) if t<16 else mechanism(t-16) if t<60 else outro(t-60)
    d=ImageDraw.Draw(im);d.rectangle((0,717,round(1280*t/68),720),fill=L.TEAL)
    return im

def main():
    out=ROOT/'企鹅主角_气泡字幕版_v3.mp4'
    exe=L.imageio_ffmpeg.get_ffmpeg_exe()
    cmd=[exe,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','24','-i','-',
      '-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
    with open(ROOT/'encode_v3.log','w',encoding='utf-8') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        for i in range(24*68):
            im=frame(i/24)
            if i in [2*24,6*24,14*24,24*24,44*24,55*24,61*24,66*24]:im.save(ROOT/f'v3_check_{i//24:02d}.png')
            p.stdin.write(im.tobytes())
            if i%240==0:print(f'rendered {i//24}/68s',flush=True)
        p.stdin.close()
        if p.wait():raise RuntimeError('encoding failed')
    check=subprocess.run([exe,'-v','error','-i',str(out),'-f','null','-'],capture_output=True,text=True)
    if check.returncode:raise RuntimeError(check.stderr)
    frame(24).save(ROOT/'气泡字幕版预览.png')
    print(json.dumps({'output':str(out),'seconds':68,'bytes':out.stat().st_size,'decode':'PASS'},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
