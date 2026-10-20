from pathlib import Path
import sys,json,math,subprocess,wave
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from functools import lru_cache
ROOT=Path(__file__).resolve().parent; PROJECT=ROOT.parents[1]
sys.path.insert(0,str(PROJECT/'ocean_animation_demo_20261011'/'runtime'))
import imageio_ffmpeg
W,H,FPS=1920,1080,24
DATA=json.loads((ROOT/'配音时间轴.json').read_text(encoding='utf-8'))
OLD=json.loads((ROOT.parent/'正文首60秒_v1'/'字幕与内容对应.json').read_text(encoding='utf-8'))
assert [r['bubble'] for r in DATA]==[r['bubble'] for r in OLD]
DURATION=DATA[-1]['end'];ASSETS=ROOT.parent/'正文日系2D_配音_v2'/'素材';FONT=ASSETS/'LXGWWenKai-Regular.ttf'
F={s:ImageFont.truetype(str(FONT),s) for s in range(18,65)}
INK='#36566b';SOFT='#627f8c';BLUE='#5599b5';CORAL='#c7765e';CREAM='#fffaf0';EDGE='#9ac3ce';YELLOW='#ffe2a1'
BG=ASSETS/'日系2D水下课堂.png'
SPRITES={int(p.name[:2]):str(p) for p in (PROJECT/'企鹅小老师_教学动作素材_20261012'/'独立动作PNG').glob('*.png')}
PHOTO_NAMES=['秘鲁渔港_20191017.jpg','印尼烟霾_NASA_20150924_高清.jpg','铜陵大通洪水_20200714.jpg']
PHOTOS=[str(ASSETS/n) for n in PHOTO_NAMES]
IMAGES={}
with wave.open(str(ROOT/'配音'/'完整配音.wav'),'rb') as wav:
    RATE=wav.getframerate();PCM=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').astype(np.float32)/32768
MOUTH_CENTERS={3:(266,229,43,37),4:(306,220,35,29),5:(274,218,35,29),6:(227,218,50,44),7:(288,235,50,44),8:(274,240,31,26),9:(277,234,30,27)}
MOUTH_LOG=[]
def mouth_state(t):
    lo=max(0,int((t-.02)*RATE));hi=min(len(PCM),int((t+.025)*RATE));sample=PCM[lo:hi]
    rms=float(np.sqrt(np.mean(sample*sample))) if len(sample) else 0
    if rms<.011:return 0
    if rms<.055:return 1
    if rms<.13:return 2
    return 3

@lru_cache(None)
def balanced_lines(paragraph,fs):
    font=F[fs];maxwidth=409
    protected=['山火','城市','气候','体温计','赤道','太平洋','海温','异常','增暖','空舱','而归','不同','地方','会诊','地球','医生','相隔','公里','可能','什么','联系','印度尼西亚','秘鲁','渔港','暴雨','警报','体征','病因','并发症','处方']
    forbidden=set()
    for word in protected:
        begin=paragraph.find(word)
        while begin>=0:
            forbidden.update(range(begin+1,begin+len(word)));begin=paragraph.find(word,begin+1)
    if font.getlength(paragraph)<=maxwidth:return [paragraph]
    for rows in range(math.ceil(font.getlength(paragraph)/maxwidth),len(paragraph)):
        target=font.getlength(paragraph)/rows
        @lru_cache(None)
        def solve(start,left):
            if left==0:return (0,[]) if start==len(paragraph) else (float('inf'),[])
            best=(float('inf'),[])
            for end in range(start+1,len(paragraph)+1):
                part=paragraph[start:end];width=font.getlength(part)
                if width>maxwidth:break
                if len(part)<3 and rows>1:continue
                if end<len(paragraph):
                    if end in forbidden:continue
                    if paragraph[end] in '，。？！：；”）' or part[-1] in '“（':continue
                    if part[-1].isascii() and part[-1].isalnum() and paragraph[end].isascii() and paragraph[end].isalnum():continue
                score,tail=solve(end,left-1)
                score+=(width-target)**2
                if paragraph[:end].count('“')!=paragraph[:end].count('”'):score+=50000
                if score<best[0]:best=(score,[part]+tail)
            return best
        score,lines=solve(0,rows)
        if math.isfinite(score):return lines
    raise ValueError(paragraph)
def img(path,w,h):
    key=(path,round(w),round(h))
    if key not in IMAGES:IMAGES[key]=Image.open(path).convert('RGBA').resize((round(w),round(h)),Image.Resampling.LANCZOS)
    return IMAGES[key]
def make_map():
    w,h=1224,432;m=Image.new('RGB',(w,h),'#dceff0');d=ImageDraw.Draw(m)
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
def xy(lon,lat):return (590+((lon+360)%360)/360*1224,273+(82-lat)/152*432)
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
    s.rect(554,170,1340,774,fill='#95bac1',stroke=None,r=30)
    s.rect(545,158,1340,774,fill='#f0e5cd',stroke='#91b7bc',width=3,r=30)
    s.rect(560,173,1310,744,fill=CREAM,stroke=None,r=20)
    s.text('海洋“发烧”了',49,42,52,INK,w=580)
    s.text('水下课堂 · 正文第一段',50,108,26,SOFT,w=570)
    s.text('01 / 从三地情境开始',1470,113,25,INK,w=390,align='right')
    if i<5:
        title='三地情境：先观察，再追问' if i<4 else '相隔上万公里，可能有什么联系？'
        s.text(title,590,195,46,INK,w=1230)
        locations=['秘鲁渔港','印度尼西亚','中国江南'];tags=['渔船空舱而归','干旱 · 山火 · 烟霾','暴雨 · 城市积水']
        metadata=['帕拉卡斯 · 2019','卫星实拍 · 2015','铜陵大通 · 2020']
        for j in range(3):
            x=590+j*414;selected=i==j+1
            s.rect(x-9,264,407,550,fill='#fff0cc' if selected else '#f2f4ed',stroke=CORAL if selected else '#b9d1d3',width=3 if selected else 1,r=15)
            s.image(PHOTOS[j],x,276,389,350,fit='cover',cropFocusY=.62 if j==0 else .5)
            s.text(locations[j],x,649,40,CORAL if selected else INK,'center',389)
            s.text(tags[j],x,713,31,INK,'center',389)
            s.text(metadata[j],x,767,26,SOFT,'center',389)
        s.text('历史资料照片 · Wikimedia Commons / NASA',590,856,25,SOFT,w=1230,align='center')
    else:
        s.text('把视线移向赤道太平洋' if i<8 else '测体征：定位Niño3.4区',590,195,46,INK,w=1230)
        s.image(MAP,590,273,1224,432)
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
            s.text('赤道中东太平洋异常增暖',590,810,42,CORAL,'center',1224)
        elif i in (6,7):
            s.text('四步会诊',590,749,36,BLUE,'center',1224)
            for j,label in enumerate(['测体征','查病因','追并发症','开处方']):
                x=602+j*305;s.rect(x,811,278,72,fill='#e4f1ef',stroke='#99bfbc',width=2,r=17)
                s.text(label,x,824,34,INK,'center',278)
        else:
            x1,y1=xy(-170,5);x2,y2=xy(-120,-5)
            s.rect(x1,y1,x2-x1,y2-y1,fill=None,stroke=CORAL,width=4,r=4)
            s.text('Niño3.4',cx-90,cy+35,29,CORAL,'center',180)
            s.text('170°W—120°W · 5°N—5°S',590,803,38,INK,'center',1224)
            s.text('像“体温计”一样，追踪海温异常',590,863,32,BLUE,'center',1224)
        s.text('陆地轮廓：Natural Earth',1500,709,22,SOFT,'right',300)
    pose=row['pose']
    if not static:
        if pose==3 and age%4.5>4.35:pose=4
        if pose==6 and age<.25:pose=5
        if pose==6 and 1.7<age<1.88:pose=7
    s.ellipse(90,970,310,20,'#c7c8be')
    px=12+(0 if static else math.sin(t*.7)*2);py=475+(0 if static else math.sin(t*1.9)*3)
    s.image(SPRITES[pose],px,py,500,500)
    state=2 if static else mouth_state(t)
    mx,my,mw,mh=MOUTH_CENTERS[pose];scale=500/512
    s.image(str(ROOT/'素材'/f'口型_{pose:02d}_{state}.png'),px+(mx-mw/2)*scale,py+(my-mh/2)*scale,mw*scale,mh*scale)
    # Speech bubbles retain exact original wording and line breaks.
    # Larger text, height fitted to content instead of a fixed oversized bubble.
    for fs in range(52,41,-1):
        lines=[]
        for paragraph in row['bubble'].split('\n'):lines.extend(balanced_lines(paragraph,fs))
        bh=len(lines)*round(fs*1.26)+48
        if bh<=282:break
    assert bh<=282
    assert ''.join(lines)==row['bubble'].replace('\n','')
    bw=min(465,max(300,math.ceil(max(F[fs].getlength(line) for line in lines))+48));bx=35+(465-bw)/2
    s.rect(bx+6,176,bw,bh,fill='#9fbec0',stroke=None,r=27)
    s.rect(bx,168,bw,bh,fill=CREAM,stroke='#96bdc7',width=3,r=27)
    tail=bx+bw*.53;s.line([(tail-13,168+bh),(tail-8,192+bh),(tail+18,168+bh)],'#96bdc7',3)
    for j,line in enumerate(lines):s.text(line,bx+24,192+j*round(fs*1.26),fs,INK,'center',bw-48)
    s.rect(545,971,1340,73,fill=CREAM,stroke='#97bcc4',width=2,r=30)
    for j,label in enumerate(['测体征','查病因','追并发症','开处方']):
        x=585+j*326
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
    exe=imageio_ffmpeg.get_ffmpeg_exe();out=ROOT/'海洋发烧了_晓伊配音_口型与大画面_v3.mp4'
    cmd=[exe,'-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(ROOT/'配音'/'完整配音.wav'),'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)]
    with open(ROOT/'.build'/'encode.log','w') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        for n in range(math.ceil(DURATION*FPS)):
            p.stdin.write(render(scene(n/FPS)).tobytes())
            MOUTH_LOG.append(mouth_state(n/FPS))
            if n%(FPS*5)==0:print(f'{n/FPS:.0f}/{DURATION:.1f}s',flush=True)
        p.stdin.close()
        if p.wait():raise RuntimeError('encoding failed')
    r=subprocess.run([exe,'-v','error','-i',str(out),'-f','null','-'],capture_output=True,text=True)
    assert r.returncode==0,r.stderr
    changes=sum(a!=b for a,b in zip(MOUTH_LOG,MOUTH_LOG[1:]));assert changes>80
    (ROOT/'验证结果.json').write_text(json.dumps({'duration':DURATION,'resolution':[W,H],'fps':FPS,'audio':'AAC Chinese TTS zh-CN-XiaoyiNeural +5%','subtitle_text_unchanged':True,'mouth_state_counts':{str(k):MOUTH_LOG.count(k) for k in range(4)},'mouth_state_changes':changes,'board_area_increase_percent':round((1340*774/(1184*628)-1)*100,1),'decode':'PASS','bytes':out.stat().st_size},ensure_ascii=False,indent=2),encoding='utf-8')
    print('VIDEO PASS',flush=True)
if __name__=='__main__':
    prepare()
    if '--prepare-only' not in sys.argv:encode()
