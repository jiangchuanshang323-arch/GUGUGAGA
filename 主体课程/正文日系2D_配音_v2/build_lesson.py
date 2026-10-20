from pathlib import Path
import sys,json,math,subprocess
from PIL import Image,ImageDraw,ImageFont
import numpy as np
ROOT=Path(__file__).resolve().parent; PROJECT=ROOT.parents[1]
sys.path.insert(0,str(PROJECT/'ocean_animation_demo_20261011'/'runtime'))
import imageio_ffmpeg
W,H,FPS=1920,1080,24
DATA=json.loads((ROOT/'配音时间轴.json').read_text(encoding='utf-8'))
OLD=json.loads((ROOT.parent/'正文首60秒_v1'/'字幕与内容对应.json').read_text(encoding='utf-8'))
assert [r['bubble'] for r in DATA]==[r['bubble'] for r in OLD]
DURATION=DATA[-1]['end'];FONT=ROOT/'素材'/'LXGWWenKai-Regular.ttf'
F={s:ImageFont.truetype(str(FONT),s) for s in range(18,65)}
INK='#36566b';SOFT='#627f8c';BLUE='#5599b5';CORAL='#c7765e';CREAM='#fffaf0';EDGE='#9ac3ce';YELLOW='#ffe2a1'
BG=ROOT/'素材'/'日系2D水下课堂.png'
SPRITES={int(p.name[:2]):str(p) for p in (PROJECT/'企鹅小老师_教学动作素材_20261012'/'独立动作PNG').glob('*.png')}
PHOTO_NAMES=['秘鲁渔港_20191017.jpg','印尼烟霾_NASA_20150924_高清.jpg','铜陵大通洪水_20200714.jpg']
PHOTOS=[str(ROOT/'素材'/n) for n in PHOTO_NAMES]
IMAGES={}
def img(path,w,h):
    key=(path,round(w),round(h))
    if key not in IMAGES:IMAGES[key]=Image.open(path).convert('RGBA').resize((round(w),round(h)),Image.Resampling.LANCZOS)
    return IMAGES[key]
def make_map():
    w,h=1080,336;m=Image.new('RGB',(w,h),'#dceff0');d=ImageDraw.Draw(m)
    def xy(lon,lat):return ((lon+180)/360*w,(82-lat)/152*h)
    for lon in range(-180,181,30):
        x=xy(lon,0)[0];d.line((x,0,x,h),fill='#c0dadd',width=1)
    for lat in (-60,-30,0,30,60):
        y=xy(0,lat)[1];d.line((0,y,w,y),fill='#8fb6c2' if lat==0 else '#c0dadd',width=2 if lat==0 else 1)
    geo=json.loads((ROOT.parent/'正文首60秒_v1'/'ne_110m_land.geojson').read_text())
    for f in geo['features']:
        g=f['geometry'];ps=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
        for p in ps:d.polygon([xy(a,b) for a,b,*_ in p[0]],fill='#a7c5b3',outline='#81a99e')
    Image.fromarray(np.roll(np.asarray(m),w//2,axis=1)).save(ROOT/'素材'/'太平洋居中地图.png')
make_map(); MAP=str(ROOT/'素材'/'太平洋居中地图.png')
def xy(lon,lat):return (735+((lon+360)%360)/360*1080,301+(82-lat)/152*336)
def ease(q):q=max(0,min(1,q));return q*q*(3-2*q)
class Scene:
    def __init__(self):self.items=[]
    def image(self,p,x,y,w,h,**kwargs):self.items.append(dict(kind='image',path=p,x=x,y=y,w=w,h=h,**kwargs))
    def rect(self,x,y,w,h,fill=CREAM,stroke=EDGE,width=2,r=24):self.items.append(dict(kind='rect',x=x,y=y,w=w,h=h,fill=fill,stroke=stroke,width=width,r=r))
    def text(self,s,x,y,size=32,color=INK,align='left',w=1100):
        lines=s.split('\n');lh=round(size*1.35)
        self.items.append(dict(kind='text',text=s,x=x,y=y,w=w,h=lh*len(lines)+8,size=size,color=color,align=align,lineHeight=lh))
    def line(self,points,color=BLUE,width=3):self.items.append(dict(kind='line',points=points,color=color,width=width))
    def ellipse(self,x,y,w,h,fill,stroke=None,width=2):self.items.append(dict(kind='ellipse',x=x,y=y,w=w,h=h,fill=fill,stroke=stroke,width=width))
    def arrow(self,points,color=CORAL,width=3):
        self.line(points,color,width);x,y=points[-1];a,b=points[-2];angle=math.atan2(y-b,x-a)
        self.line([(x-11*math.cos(angle-.45),y-11*math.sin(angle-.45)),(x,y),(x-11*math.cos(angle+.45),y-11*math.sin(angle+.45))],color,width)
def scene(t,index=None,static=False):
    i=next((i for i,r in enumerate(DATA) if r['start']<=t<r['end']),len(DATA)-1) if index is None else index
    row=DATA[i];age=max(0,t-row['start']);s=Scene()
    s.image(str(BG),0,0,W,H)
    # Readable editable classroom board with soft two-tone frame.
    s.rect(701,206,1184,628,fill='#95bac1',stroke=None,r=30)
    s.rect(690,194,1184,628,fill='#f0e5cd',stroke='#91b7bc',width=3,r=30)
    s.rect(705,209,1154,598,fill=CREAM,stroke=None,r=20)
    s.text('海洋“发烧”了',49,42,52,INK,w=580)
    s.text('水下课堂 · 正文第一段',50,108,26,SOFT,w=570)
    s.text('01 / 从三地情境开始',1470,143,25,INK,w=390,align='right')
    if i<5:
        title='三地情境：先观察，再追问' if i<4 else '相隔上万公里，可能有什么联系？'
        s.text(title,740,231,39,INK,w=1100)
        locations=['秘鲁渔港','印度尼西亚','中国江南'];tags=['渔船空舱而归','干旱 · 山火 · 烟霾','暴雨 · 城市积水']
        metadata=['帕拉卡斯 · 2019','卫星实拍 · 2015','铜陵大通 · 2020']
        for j in range(3):
            x=738+j*366;selected=i==j+1
            s.rect(x-9,298,356,439,fill='#fff0cc' if selected else '#f2f4ed',stroke=CORAL if selected else '#b9d1d3',width=3 if selected else 1,r=15)
            s.image(PHOTOS[j],x,309,338,280,fit='cover',cropFocusY=.62 if j==0 else .5)
            s.text(locations[j],x,608,32,CORAL if selected else INK,'center',338)
            s.text(tags[j],x,656,26,INK,'center',338)
            s.text(metadata[j],x,702,22,SOFT,'center',338)
        s.text('历史资料照片 · Wikimedia Commons / NASA',744,766,21,SOFT,w=1080,align='center')
    else:
        s.text('把视线移向赤道太平洋' if i<8 else '测体征：定位Niño3.4区',740,231,42,INK,w=1100)
        s.image(MAP,735,301,1080,336)
        for lon,lat,label,size in [(-160,22,'太平洋',28),(65,-15,'印度洋',22),(-30,15,'大西洋',22)]:
            x,y=xy(lon,lat);s.text(label,x-72,y-18,size,SOFT,'center',144)
        for lon,lat,label in [(-78,-12,'秘鲁'),(118,-2,'印尼'),(112,28,'江南')]:
            x,y=xy(lon,lat);s.ellipse(x-6,y-6,12,12,CORAL);s.text(label,x+11,y-33,24,INK,w=80)
        cx,cy=xy(-145,0)
        if i==5:
            q=1 if static else ease(age/1.1)
            for lon,lat in [(-78,-12),(118,-2),(112,28)]:
                x,y=xy(lon,lat);s.arrow([(x,y),(x+(cx-x)*q,y+(cy-y)*q)])
            s.ellipse(cx-44,cy-22,88,44,None,CORAL,3)
            s.text('赤道中东太平洋异常增暖',744,690,38,CORAL,'center',1080)
        elif i in (6,7):
            s.text('四步会诊',744,659,32,BLUE,'center',1080)
            for j,label in enumerate(['测体征','查病因','追并发症','开处方']):
                x=753+j*266;s.rect(x,711,245,62,fill='#e4f1ef',stroke='#99bfbc',width=2,r=17)
                s.text(label,x,722,30,INK,'center',245)
        else:
            x1,y1=xy(-170,5);x2,y2=xy(-120,-5)
            s.rect(x1,y1,x2-x1,y2-y1,fill=None,stroke=CORAL,width=4,r=4)
            s.text('Niño3.4',cx-90,cy+35,29,CORAL,'center',180)
            s.text('170°W—120°W · 5°N—5°S',744,688,34,INK,'center',1080)
            s.text('像“体温计”一样，追踪海温异常',744,743,30,BLUE,'center',1080)
        s.text('陆地轮廓：Natural Earth',1510,638,20,SOFT,'right',288)
    pose=row['pose']
    if not static:
        if pose==3 and age%4.5>4.35:pose=4
        if pose==6 and age<.25:pose=5
        if pose==6 and 1.7<age<1.88:pose=7
    s.ellipse(159,977,360,22,'#c7c8be')
    s.image(SPRITES[pose],20+(0 if static else math.sin(t*.7)*2),395+(0 if static else math.sin(t*1.9)*3),620,620)
    # Speech bubbles retain exact original wording and line breaks.
    s.rect(46,162,560,228,fill='#9fbec0',stroke=None,r=27)
    s.rect(40,153,560,228,fill=CREAM,stroke='#96bdc7',width=3,r=27)
    s.line([(343,381),(350,409),(381,381)],'#96bdc7',3)
    n=len(row['bubble'].split('\n'));s.text(row['bubble'],68,153+(228-n*48)/2-4,36,INK,w=507)
    s.rect(716,971,1142,73,fill=CREAM,stroke='#97bcc4',width=2,r=30)
    for j,label in enumerate(['测体征','查病因','追并发症','开处方']):
        x=756+j*280
        if j==0 and i>=8:s.rect(x,985,216,44,fill=YELLOW,stroke=None,r=18)
        s.text(label,x,988,29,INK,'center',216)
    s.rect(0,1075,W,5,fill='#d6e7e5',stroke=None,r=0)
    if not static:s.rect(0,1075,W*t/DURATION,5,fill=BLUE,stroke=None,r=0)
    return s
def render(s):
    im=Image.new('RGB',(W,H),CREAM);d=ImageDraw.Draw(im)
    for a in s.items:
        k=a['kind']
        if k=='image':
            x,y,w,h=[round(a[v]) for v in ('x','y','w','h')]
            if a.get('fit')=='cover':
                key=(a['path'],w,h,'cover'); art=IMAGES.get(key)
                if art is None:
                    src=Image.open(a['path']).convert('RGBA');sc=max(w/src.width,h/src.height);nw,nh=round(src.width*sc),round(src.height*sc);src=src.resize((nw,nh),Image.Resampling.LANCZOS)
                    left=(nw-w)//2;top=round((nh-h)*a.get('cropFocusY',.5));art=src.crop((left,top,left+w,top+h));IMAGES[key]=art
                im.paste(art,(x,y),art)
            else:
                art=img(a['path'],w,h);im.paste(art,(x,y),art)
            d=ImageDraw.Draw(im)
        elif k=='rect':
            d.rounded_rectangle((a['x'],a['y'],a['x']+a['w'],a['y']+a['h']),radius=a['r'],fill=a['fill'],outline=a['stroke'],width=a['width'])
        elif k=='ellipse':d.ellipse((a['x'],a['y'],a['x']+a['w'],a['y']+a['h']),fill=a['fill'],outline=a['stroke'],width=a['width'])
        elif k=='line':d.line(a['points'],fill=a['color'],width=a['width'],joint='curve')
        elif k=='text':
            for j,line in enumerate(a['text'].split('\n')):
                x=a['x'];y=a['y']+j*a['lineHeight'];fw=F[a['size']].getlength(line)
                if a['align']=='center':x+=(a['w']-fw)/2
                elif a['align']=='right':x+=a['w']-fw
                assert fw<=a['w']+3,(line,fw,a['w'])
                d.text((x,y),line,font=F[a['size']],fill=a['color'],anchor='lt')
    return im
def prepare():
    slides=[]
    for i,row in enumerate(DATA):
        sc=scene((row['start']+row['end'])/2,i,True);slides.append(sc.items)
        render(sc).save(ROOT/'.build'/f'video_slide_{i+1:02d}.png')
    (ROOT/'.build'/'slides.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2),encoding='utf-8')
    render(scene(DATA[1]['start']+1,1,True)).save(ROOT/'新版画面预览.png')
def encode():
    exe=imageio_ffmpeg.get_ffmpeg_exe();out=ROOT/'海洋发烧了_正文日系2D_中文配音_v2.mp4'
    cmd=[exe,'-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(ROOT/'配音'/'完整配音.wav'),'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)]
    with open(ROOT/'.build'/'encode.log','w') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        for n in range(math.ceil(DURATION*FPS)):
            p.stdin.write(render(scene(n/FPS)).tobytes())
            if n%(FPS*5)==0:print(f'{n/FPS:.0f}/{DURATION:.1f}s',flush=True)
        p.stdin.close()
        if p.wait():raise RuntimeError('encoding failed')
    r=subprocess.run([exe,'-v','error','-i',str(out),'-f','null','-'],capture_output=True,text=True)
    assert r.returncode==0,r.stderr
    (ROOT/'验证结果.json').write_text(json.dumps({'duration':DURATION,'resolution':[W,H],'fps':FPS,'audio':'AAC Chinese TTS zh-CN-XiaoxiaoNeural +12%','subtitle_text_unchanged':True,'decode':'PASS','bytes':out.stat().st_size},ensure_ascii=False,indent=2),encoding='utf-8')
    print('VIDEO PASS',flush=True)
if __name__=='__main__':
    prepare()
    if '--prepare-only' not in sys.argv:encode()
