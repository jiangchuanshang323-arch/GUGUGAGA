from pathlib import Path
import sys, math, subprocess, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'runtime'))
import imageio_ffmpeg
W,H,FPS,DURATION = 1280,720,24,44
FONT = 'C:/Windows/Fonts/msyh.ttc'
fonts = {s:ImageFont.truetype(FONT,s) for s in [16,18,20,22,24,28,32,40,46]}
BG=(8,22,40); WHITE=(235,244,252); MUTED=(154,181,204)
TEAL=(85,216,221); HOT=(255,137,89); BLUE=(77,151,239)

def smooth(a,b,t):
    q=max(0,min(1,(t-a)/(b-a))); return q*q*(3-2*q)

def txt(d, xy, s, size=22, color=WHITE, anchor=None):
    d.text(xy,s,font=fonts[size],fill=color,anchor=anchor)

def arrow(d, pts, color, width=4, head=13):
    d.line(pts,fill=color,width=width,joint='curve')
    x,y=pts[-1]; x0,y0=pts[-2]; ang=math.atan2(y-y0,x-x0)
    d.polygon([(x,y),(x-head*math.cos(ang-.5),y-head*math.sin(ang-.5)),
               (x-head*math.cos(ang+.5),y-head*math.sin(ang+.5))],fill=color)

def cloud(d,x,y,k=1):
    col=(188,222,236)
    for dx,dy,r in [(-29,3,18),(-10,-9,23),(15,-6,25),(37,5,17)]:
        d.ellipse((x+(dx-r)*k,y+(dy-r)*k,x+(dx+r)*k,y+(dy+r)*k),fill=col)
    d.rounded_rectangle((x-43*k,y,x+48*k,y+20*k),radius=10*k,fill=col)

def point_on_path(points,q):
    lens=[math.dist(a,b) for a,b in zip(points,points[1:])]; total=sum(lens)
    v=(q%1)*total
    for i,l in enumerate(lens):
        if v<=l:
            f=v/l; return (points[i][0]*(1-f)+points[i+1][0]*f,points[i][1]*(1-f)+points[i+1][1]*f)
        v-=l
    return points[-1]

def frame(t):
    change=smooth(12,29,t)
    stage=0 if t<11 else 1 if t<21 else 2 if t<32 else 3
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    # restrained header, sequence and timeline
    txt(d,(55,29),'海洋“发烧”了',40)
    txt(d,(56,83),'海—气相互作用  /  动画样片',18,MUTED)
    txt(d,(1225,46),'01  机制演示',18,TEAL,'ra')
    titles=['正常状态','信风减弱','暖水向东扩展','海洋与大气相互响应']
    for i,title in enumerate(titles):
        x=56+i*302
        col=TEAL if i==stage else MUTED if i<stage else (80,111,139)
        d.ellipse((x,119,x+25,144),fill=col if i==stage else (22,47,69),outline=col,width=1)
        txt(d,(x+12,131),str(i+1),16,BG if i==stage else col,'mm')
        txt(d,(x+36,131),title,20,col,'lm')
    d.line((56,160,1224,160),fill=(33,59,80),width=1)
    # Basin, explicitly a section rather than a geographic map.
    xL,xR,surface,bottom=170,1110,385,574
    txt(d,(177,184),'西太平洋',24,WHITE)
    txt(d,(1102,184),'东太平洋',24,WHITE,'ra')
    txt(d,(640,191),'赤道太平洋剖面示意 · 非按比例',16,MUTED,'ma')
    # Atmosphere particle circuit. Circulation weakens and rising branch moves east.
    riseX=300+change*420; sinkX=1010
    aircol=tuple(int(a*(1-change*.35)) for a in TEAL)
    path=[(riseX,350),(riseX,250),(sinkX,250),(sinkX,350)]
    arrow(d,path,aircol,3,12)
    for i in range(12):
        px,py=point_on_path(path,t*.07+i/12)
        d.ellipse((px-3,py-3,px+3,py+3),fill=aircol)
    txt(d,(640,226),'沃克环流：上升与下沉位置随海温分布变化',18,MUTED,'ma')
    # Moving convection and rainfall.
    cloud(d,riseX,285,.86)
    for i in range(9):
        rx=riseX-38+i*9; ry=322+((t*27+i*7)%46)
        d.line((rx,ry,rx-3,ry+9),fill=(119,211,245),width=2)
    txt(d,(riseX,377),'对流与降水',16,TEAL,'mb')
    # Trade wind: east to west, thinning and slowing without reversing.
    windY=352
    arrow(d,[(980,windY),(450,windY)],(187,214,228),max(2,int(6-3*change)),15)
    txt(d,(930,316),'近地面信风  '+('较强' if change<.2 else '减弱'),20,WHITE,'ma')
    for i in range(7):
        xx=980-((t*(70-45*change)+i*85)%530)
        d.line((xx,windY-1,xx+15,windY-1),fill=WHITE,width=2)
    # Ocean pixel gradient, warm surface layer grows toward east.
    ww,hh=xR-xL,bottom-surface
    xs=np.linspace(0,1,ww)[None,:]; ys=np.arange(hh)[:,None]
    depth=(126-95*xs)*(1-change)+(113-31*xs)*change
    warm=np.clip((depth-ys)/29,0,1)
    eastWarm=(1-xs)*(1-change)+change*.86
    top=np.zeros((hh,ww,3),dtype=np.float32)
    for c,(cold,red) in enumerate(zip((25,66,107),(242,100,59))):
        top[:,:,c]=cold+(red-cold)*warm*(.35+.65*eastWarm)
    ocean=Image.fromarray(top.astype('uint8'),'RGB'); im.paste(ocean,(xL,surface)); d=ImageDraw.Draw(im)
    d.line((xL,surface,xR,surface),fill=(155,222,236),width=3)
    # Thermocline curve, west deep / east shallow, increasingly flatter.
    pts=[]
    for xx in range(xL,xR+1,8):
        u=(xx-xL)/(xR-xL)
        dep=(126-95*u)*(1-change)+(113-31*u)*change
        pts.append((xx,surface+dep))
    for i in range(0,len(pts)-1,3):d.line(pts[i:i+2],fill=(240,218,169),width=2)
    txt(d,(470,532),'温跃层（示意）',18,(234,217,188))
    txt(d,(245,414),'表层暖水',22,(255,234,215))
    txt(d,(850,549),'深层冷水',20,(138,202,245))
    # Water particles and eastward expansion, not an all-water reversal.
    if t<12:
        arrow(d,[(720,441),(300,441)],(255,200,159),3,12)
        for i in range(9):
            px=720-((t*32+i*52)%420);d.ellipse((px-3,437,px+3,443),fill=(255,220,175))
    else:
        extent=490+smooth(12,28,t)*500
        arrow(d,[(290,440),(extent,440)],(255,217,162),4,14)
        for i in range(12):
            px=290+((max(0,t-12)*44+i*67)%max(1,extent-290))
            d.ellipse((px-3,437,px+3,443),fill=(255,220,175))
    # Coastal upwelling weakens, stays explicit.
    upcol=(114,209,255)
    arrow(d,[(1035,555),(1035,410)],upcol,max(2,int(6-change*4)),13)
    for i in range(5):
        py=555-((t*(35-change*22)+i*30)%145)
        d.ellipse((1032,py-3,1038,py+3),fill=upcol)
    txt(d,(1092,484),'上升流',18,upcol,'ra')
    txt(d,(1092,510),'较强' if change<.2 else '减弱',18,upcol,'ra')
    # West/east land as small schematic section ends.
    d.polygon([(120,575),(120,447),(151,422),(170,450),(170,575)],fill=(60,96,94))
    d.polygon([(1110,575),(1110,449),(1147,426),(1180,465),(1180,575)],fill=(76,93,91))
    # Warm/cool legend.
    d.ellipse((179,591,190,602),fill=HOT); txt(d,(199,586),'暖水',16,MUTED)
    d.ellipse((281,591,292,602),fill=BLUE);txt(d,(301,586),'冷水',16,MUTED)
    txt(d,(1104,590),'教学示意，不代表实时监测或区域预报',16,MUTED,'ra')
    # One idea per subtitle, explicitly limits typical effects.
    captions=[
      ('正常年份，信风推动表层暖水向西堆积。','西侧暖水较厚；东侧温跃层较浅，冷水上涌较强。'),
      ('当信风减弱，暖水开始向东扩展。','海洋变化与大气变化彼此作用，并非一个因素单向决定。'),
      ('中东太平洋增暖，东侧上升流受到抑制。','对流和降水分布随之调整，沃克环流减弱并发生位移。'),
      ('海—气耦合变化，能影响远方的天气与生态。','实际影响随地区、季节及其他气候因素变化。')]
    a,b=captions[stage]
    txt(d,(640,630),a,28,WHITE,'ma');txt(d,(640,674),b,20,MUTED,'ma')
    d.rectangle((0,H-4,W,H),fill=(25,49,68));d.rectangle((0,H-4,int(W*t/DURATION),H),fill=TEAL)
    return im

def main():
    exe=imageio_ffmpeg.get_ffmpeg_exe()
    out=ROOT/'海洋发烧了_机制动画样片.mp4'
    cmd=[exe,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}',
         '-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=open(ROOT/'encode.log','w',encoding='utf-8'))
    for i in range(FPS*DURATION):
        im=frame(i/FPS)
        if i in [5*FPS,17*FPS,27*FPS,38*FPS]: im.save(ROOT/f'check_{i//FPS:02d}.png')
        p.stdin.write(im.tobytes())
        if i%(FPS*10)==0:print(f'rendered {i//FPS}/{DURATION}s',flush=True)
    p.stdin.close(); rc=p.wait()
    if rc:raise RuntimeError(f'ffmpeg error {rc}')
    frame(27).save(ROOT/'预览.png')
    print(json.dumps({'output':str(out),'bytes':out.stat().st_size,'seconds':DURATION,'fps':FPS,'size':[W,H]},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
