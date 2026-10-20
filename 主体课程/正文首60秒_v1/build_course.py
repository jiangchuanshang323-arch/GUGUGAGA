from pathlib import Path
import sys, json, math, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
sys.path.insert(0,str(PROJECT/'ocean_animation_demo_20261011'/'runtime'))
import imageio_ffmpeg
W,H,FPS,DURATION=1920,1080,24,60
FONT='C:/Windows/Fonts/msyh.ttc'
F={s:ImageFont.truetype(FONT,s) for s in (20,22,24,26,28,30,32,34,36,40,44,48,56)}
WHITE=(239,248,255); MUTED=(169,200,221); TEAL=(95,231,232); GOLD=(255,212,112)
BG=Image.open(ROOT/'水下课堂空背景.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
ILLUSTRATION=Image.open(ROOT/'三地情境示意.png').convert('RGB')
raw_cases=[ILLUSTRATION.crop((i*ILLUSTRATION.width//3,0,(i+1)*ILLUSTRATION.width//3,ILLUSTRATION.height)) for i in range(3)]
SPRITE_ROOT=PROJECT/'企鹅小老师_教学动作素材_20261012'/'独立动作PNG'
POSES={int(p.name[:2]):Image.open(p).convert('RGBA') for p in SPRITE_ROOT.glob('*.png')}
POSES={k:v.resize((620,620),Image.Resampling.LANCZOS) for k,v in POSES.items()}

TIMELINE=[
 (0,5,'先观察三幅画面：\n它们发生在不同的地方。',3,'镜3：三组画面并置'),
 (5,11,'秘鲁渔港：\n渔船空舱而归。',6,'镜3：秘鲁渔港'),
 (11,17,'印度尼西亚：\n干旱与山火警报。',6,'镜3：烟霾与山火'),
 (17,23,'中国江南：\n暴雨与城市积水。',6,'镜3：江南暴雨'),
 (23,30,'相隔上万公里，\n它们可能有什么联系？',9,'镜4：跨区域问题'),
 (30,38,'追踪一条共同线索：\n赤道中东太平洋\n异常增暖。',6,'镜4：海洋发烧'),
 (38,44,'今天，我们当一回\n“地球医生”，\n完成一次全球会诊。',3,'镜4：会诊叙事'),
 (44,50,'测体征，查病因，\n追并发症，开处方。',8,'00总体设计：四步会诊'),
 (50,55,'医生看病，\n先测体温。',5,'镜5：测体征'),
 (55,60,'气候学家的“体温计”，\n是赤道太平洋的\nNiño3.4区。',6,'镜5：区域定位'),
]

def ease(a,b,t):
    q=max(0,min(1,(t-a)/(b-a)));return q*q*(3-2*q)

def text(d,xy,s,size=32,color=WHITE,anchor=None):
    d.text(xy,s,font=F[size],fill=color,anchor=anchor)

def wrapped(s,size,width):
    lines=[]
    for paragraph in s.split('\n'):
        line=''
        for c in paragraph:
            if F[size].getlength(line+c)>width and line:
                if c in '，。？！：；”）':
                    lines.append(line[:-1]);line=line[-1]+c
                else:lines.append(line);line=c
            else:line+=c
        if line:lines.append(line)
    return lines

def speech(im,s,age):
    # Fixed speech area next to presenter, separated from the teaching screen.
    x,y,w,h=40,153,560,228
    layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
    d.rounded_rectangle((x+6,y+8,x+w+6,y+h+8),radius=28,fill=(0,12,32,95))
    d.polygon([(x+300,y+h-3),(x+375,y+h-3),(x+346,y+h+47)],fill=(245,253,253,255))
    d.rounded_rectangle((x,y,x+w,y+h),radius=28,fill=(245,253,253,255),outline=(99,219,222,255),width=3)
    lines=wrapped(s,34,w-58); yy=y+(h-len(lines)*49)/2-4
    for line in lines:
        d.text((x+29,yy),line,font=F[34],fill=(20,53,75,255));yy+=49
    a=ease(0,.3,age)
    if a<1:layer.putalpha(layer.getchannel('A').point(lambda n:round(n*a)))
    im.paste(layer,(0,0),layer)

def presenter(im,pose,t,age):
    # Content-led poses, small breathing motion, occasional short blink on rest.
    if pose==3 and t%4.8>4.63:pose=4
    if pose==6 and age<.4:pose=5
    if pose==6 and 2.5<age<2.78:pose=7
    src=POSES[pose]
    x=20+round(math.sin(t*.7)*2); y=395+round(math.sin(t*1.9)*3)
    im.paste(src,(x,y),src)

def cover(img,w,h,zoom=1):
    scale=max(w/img.width,h/img.height)*zoom
    nw,nh=round(img.width*scale),round(img.height*scale)
    r=img.resize((nw,nh),Image.Resampling.LANCZOS)
    return r.crop(((nw-w)//2,(nh-h)//2,(nw+w)//2,(nh+h)//2))

def arrow(d,pts,color,width=4,head=14):
    d.line(pts,fill=color,width=width,joint='curve')
    x,y=pts[-1];px,py=pts[-2];a=math.atan2(y-py,x-px)
    d.polygon([(x,y),(x-head*math.cos(a-.5),y-head*math.sin(a-.5)),(x-head*math.cos(a+.5),y-head*math.sin(a+.5))],fill=color)

def world_map():
    mw,mh=1080,336
    m=Image.new('RGB',(mw,mh),(13,45,73));d=ImageDraw.Draw(m)
    def xy(lon,lat):return ((lon+180)/360*mw,(82-lat)/152*mh)
    for lon in range(-180,181,30):
        xx=xy(lon,0)[0];d.line((xx,0,xx,mh),fill=(35,71,93),width=1)
    for lat in (-60,-30,0,30,60):
        yy=xy(0,lat)[1];d.line((0,yy,mw,yy),fill=(47,84,107) if lat==0 else (35,71,93),width=2 if lat==0 else 1)
    data=json.loads((ROOT/'ne_110m_land.geojson').read_text(encoding='utf-8'))
    for feature in data['features']:
        g=feature['geometry']; polys=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
        for poly in polys:
            d.polygon([xy(lon,lat) for lon,lat,*_ in poly[0]],fill=(66,113,123),outline=(124,166,166))
    # Roll an ordinary world map by half its width to put Pacific at the center.
    return Image.fromarray(np.roll(np.asarray(m),mw//2,axis=1))

MAP=world_map()
def map_xy(lon,lat):
    return (735+((lon+360)%360)/360*1080,301+(82-lat)/152*336)

def case_panel(im,t):
    d=ImageDraw.Draw(im)
    text(d,(740,223),'三地情境：先观察，再追问' if t<23 else '相隔上万公里，可能有什么联系？',40,GOLD)
    locations=['秘鲁渔港','印度尼西亚','中国江南']
    tags=['渔船空舱而归','干旱 · 山火 · 烟霾','暴雨 · 城市积水']
    selected=0 if 5<=t<11 else 1 if 11<=t<17 else 2 if 17<=t<23 else -1
    for i in range(3):
        x=738+i*366;y=292;w=338;h=354
        art=cover(raw_cases[i],w,h,1+min(t,23)*.00065)
        # Subtle motion layers relate to the scene; artwork remains case illustration.
        ad=ImageDraw.Draw(art)
        if i==2:
            for j in range(30):
                rx=(j*53+int(t*18))%w;ry=(j*83+int(t*200))%h
                ad.line((rx,ry,rx-4,ry+16),fill=(191,219,234),width=1)
        elif i==1:
            smoke=Image.new('RGBA',(w,h));sd=ImageDraw.Draw(smoke)
            for j in range(7):
                sy=int((j*43-t*7)%h);sx=70+j*29
                sd.ellipse((sx-38,sy-25,sx+45,sy+25),fill=(181,188,193,22))
            art.paste(smoke,(0,0),smoke)
        im.paste(art,(x,y));d=ImageDraw.Draw(im)
        d.rounded_rectangle((x-3,y-3,x+w+3,y+h+3),radius=7,outline=GOLD if selected==i else (74,161,180),width=5 if selected==i else 2)
        text(d,(x+w/2,665),locations[i],32,GOLD if selected==i else WHITE,'ma')
        text(d,(x+w/2,713),tags[i],24,MUTED,'ma')
    text(d,(1260,762),'AI情境示意 · 非新闻实拍',22,MUTED,'ma')

def map_panel(im,t):
    d=ImageDraw.Draw(im)
    heading='把视线移向赤道太平洋' if t<50 else '测体征：定位Niño3.4区'
    text(d,(740,223),heading,44,GOLD)
    im.paste(MAP,(735,301));d=ImageDraw.Draw(im)
    text(d,map_xy(-160,22),'太平洋',28,(137,195,217),'mm')
    text(d,map_xy(65,-15),'印度洋',22,MUTED,'mm')
    text(d,map_xy(-30,15),'大西洋',22,MUTED,'mm')
    points=[(-78,-12),(118,-2),(112,28)]
    labels=['秘鲁','印尼','江南']
    for (lon,lat),label in zip(points,labels):
        px,py=map_xy(lon,lat)
        d.ellipse((px-7,py-7,px+7,py+7),fill=GOLD)
        text(d,(px+10,py-30),label,22,WHITE)
    cx,cy=map_xy(-145,0)
    if t<38:
        for lon,lat in points:
            px,py=map_xy(lon,lat)
            q=ease(30,34,t);end=(px+(cx-px)*q,py+(cy-py)*q)
            arrow(d,[(px,py),end],(244,158,108),3,10)
        pulse=20+6*math.sin(t*2)
        d.ellipse((cx-pulse*2,cy-pulse,cx+pulse*2,cy+pulse),outline=(255,148,102),width=3)
        text(d,(1260,694),'赤道中东太平洋异常增暖',34,TEAL,'ma')
    if 38<=t<50:
        text(d,(1260,660),'四步会诊',32,TEAL,'ma')
        for i,s in enumerate(['测体征','查病因','追并发症','开处方']):
            x=763+i*262;w=238
            d.rounded_rectangle((x,712,x+w,772),radius=15,fill=(20,58,85),outline=GOLD if t>=44 else TEAL,width=2)
            text(d,(x+w/2,742),s,28,WHITE,'mm')
    if t>=50:
        x1,y1=map_xy(-170,5);x2,y2=map_xy(-120,-5)
        reveal=ease(50,52,t)
        d.rounded_rectangle((x1,y1,x1+(x2-x1)*reveal,y2),radius=4,outline=GOLD,width=4)
        text(d,(cx,cy+43),'Niño3.4',28,GOLD,'ma')
        text(d,(1260,690),'170°W—120°W · 5°N—5°S',32,WHITE,'ma')
        text(d,(1260,743),'像“体温计”一样，追踪海温异常',28,TEAL,'ma')
    text(d,(1795,638),'陆地轮廓：Natural Earth',20,MUTED,'ra')

def frame(t):
    im=BG.copy();d=ImageDraw.Draw(im)
    # Board interior coordinates remain within the generated cyan frame.
    d.rounded_rectangle((692,196,1885,791),radius=20,fill=(7,30,57))
    text(d,(49,43),'海洋“发烧”了',48,WHITE)
    text(d,(50,105),'水下课堂 · 正文第一段',24,(208,241,250))
    text(d,(1853,145),'01 / 从三地情境开始',24,WHITE,'ra')
    if t<29.7:case_panel(im,t)
    elif t<30.3:
        a=im.copy();case_panel(a,t)
        b=im.copy();map_panel(b,t)
        im=Image.blend(a,b,ease(29.7,30.3,t))
    else:map_panel(im,t)
    start,end,msg,pose,source=next(s for s in TIMELINE if s[0]<=t<s[1])
    shadow=Image.new('RGBA',(W,H));sd=ImageDraw.Draw(shadow)
    sd.ellipse((154,974,514,1006),fill=(4,21,44,75))
    im.paste(shadow,(0,0),shadow)
    presenter(im,pose,t,t-start)
    speech(im,msg,t-start)
    d=ImageDraw.Draw(im)
    # Course navigation, not duplicate narration along the lower edge.
    d.rounded_rectangle((716,971,1858,1044),radius=30,fill=(8,39,65),outline=(93,185,204),width=2)
    for i,label in enumerate(['测体征','查病因','追并发症','开处方']):
        x=864+i*280
        if i==0 and t>=50:d.rounded_rectangle((x-101,986,x+101,1029),radius=18,fill=(84,77,44),outline=GOLD,width=2)
        text(d,(x,1007),label,28,GOLD if i==0 and t>=50 else WHITE,'mm')
    d.rectangle((0,1075,W,1080),fill=(12,55,77));d.rectangle((0,1075,round(W*t/60),1080),fill=TEAL)
    return im

def main():
    out=ROOT/'海洋发烧了_正文首60秒_无配音_v1.mp4'
    exe=imageio_ffmpeg.get_ffmpeg_exe()
    cmd=[exe,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
         '-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
    with open(ROOT/'encode.log','w',encoding='utf-8') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        for i in range(FPS*DURATION):
            im=frame(i/FPS)
            if i in [3*FPS,8*FPS,14*FPS,20*FPS,26*FPS,34*FPS,41*FPS,47*FPS,53*FPS,58*FPS]:im.save(ROOT/f'检查_{i//FPS:02d}.png')
            p.stdin.write(im.tobytes())
            if i%(FPS*10)==0:print(f'rendered {i//FPS}/{DURATION}s',flush=True)
        p.stdin.close()
        if p.wait():raise RuntimeError('encoding failed')
    r=subprocess.run([exe,'-v','error','-i',str(out),'-f','null','-'],capture_output=True,text=True)
    if r.returncode:raise RuntimeError(r.stderr)
    frame(8).save(ROOT/'正文首60秒_封面.png')
    (ROOT/'字幕与内容对应.json').write_text(json.dumps([{'start':a,'end':b,'bubble':c,'pose':p,'source':s} for a,b,c,p,s in TIMELINE],ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(out),'seconds':DURATION,'resolution':[W,H],'fps':FPS,'bytes':out.stat().st_size,'decode':'PASS'},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
