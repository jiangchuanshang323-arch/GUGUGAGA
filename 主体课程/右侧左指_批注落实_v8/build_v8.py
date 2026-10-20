from pathlib import Path
import sys,json,wave,math,re,inspect,subprocess,shutil,hashlib
import numpy as np
from PIL import Image,ImageEnhance
ROOT=Path(__file__).resolve().parent
for name in ('素材','.build','配音','交付'):(ROOT/name).mkdir(exist_ok=True)
V7=ROOT.parent/'权威地图_生动台词_v7'
sys.path.insert(0,str(V7));import build_v7 as old
b=old.b;v=old.v;EXE=old.EXE
TITLE=1.6;TRIM=.8;SHIFT=TITLE-TRIM
DATA=json.loads((V7/'台词与时间轴.json').read_text(encoding='utf-8'))
for r in DATA:r['start']+=SHIFT;r['end']+=SHIFT
with wave.open(str(V7/'配音'/'新版讲解.wav'),'rb') as w:original=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
samples=np.concatenate([np.zeros(round(TITLE*24000),dtype='<i2'),original[round(TRIM*24000):]])
PCM=samples.astype(np.float32)/32768;DURATION=len(samples)/24000
with wave.open(str(ROOT/'配音'/'复用台词_标题衔接.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(samples.tobytes())
MAP=ROOT/'素材'/'NOAA_PSL_ENSO区域图.png'
RIGHT=ROOT/'素材'/'19_右侧向左指_原图.png'
MW,MH=Image.open(MAP).size;PW,PH=Image.open(RIGHT).size
IMAGES=[]
for i,path in enumerate(b.PHOTOS):
    original_img=Image.open(path).convert('RGB')
    shaded=ImageEnhance.Brightness(ImageEnhance.Color(original_img).enhance(.13)).enhance(.50)
    p=ROOT/'素材'/f'案例{i+1}_未讲暗场.png';shaded.save(p);IMAGES.append(str(p))
def mouth(t):
    part=PCM[max(0,int((t-.02)*24000)):int((t+.025)*24000)];r=float(np.sqrt(np.mean(part*part))) if len(part) else 0
    return 0 if r<.011 else 1 if r<.055 else 2 if r<.13 else 3
def wrap(text,size,width):
    toks=re.findall(r'[A-Za-zÀ-ÿ0-9]+(?:\.[0-9]+)*|.',text);lines=[];line=''
    for token in toks:
        if line and b.F[size].getlength(line+token)>width:
            if token in '，。？！：；”）':last=line[-1];line=line[:-1];lines.append(line);line=last+token
            else:lines.append(line);line=token
        else:line+=token
    if line:lines.append(line)
    return lines
def bubble(s,text,right=False):
    x,y,width=(1498,70,400) if right else (18,165,365);size=40 if right else 41
    lines=wrap(text.replace('尼诺三点四','Niño3.4'),size,width-40);height=len(lines)*round(size*1.26)+40
    tip=(1640,512) if right else (200,599);mid=x+width*.49
    s.items.append(dict(kind='polygon',points=[(mid-18,y+height-2),tip,(mid+18,y+height-2)],fill=b.CREAM,stroke='#98bcc8',width=3))
    s.rect(x,y,width,height,fill=b.CREAM,stroke='#98bcc8',width=3,r=25);s.rect(mid-15,y+height-5,30,8,fill=b.CREAM,stroke=None,r=0)
    for j,line in enumerate(lines):s.text(line,x+20,y+20+j*round(size*1.26),size,b.INK,'justify' if j<len(lines)-1 else 'left',width-40)
def presenter(s,pose,px,py,size,t,custom=False):
    s.ellipse(px+size*.20,py+size*.94,size*.63,14,'#bdc9c2')
    path=str(RIGHT) if custom else b.SPRITES[pose];s.image(path,px,py,size,size)
    if custom:mx,my,mw,mh=796,536,70,59;den=PW;mouth_pose=3
    elif pose in (13,14):
        mx,my,mw,mh=(314,239,39,34) if pose==13 else (295,243,39,34);den=512;mouth_pose=3
    elif pose in b.MOUTH_CENTERS:mx,my,mw,mh=b.MOUTH_CENTERS[pose];den=512;mouth_pose=pose
    else:return
    scale=size/den;s.image(str(v.V3/'素材'/f'口型_{mouth_pose:02d}_{mouth(t)}.png'),px+(mx-mw/2)*scale,py+(my-mh/2)*scale,mw*scale,mh*scale)
def scene(t):
    s=b.Scene()
    if t<TITLE:
        s.image(str(b.BG),0,0,1920,1080);s.rect(185,270,1550,525,fill=b.CREAM,stroke='#9ac2cb',r=42)
        s.text('海洋“发烧”了',290,340,78,b.INK,'center',1330)
        s.text('追踪厄尔尼诺的环境多米诺',275,505,61,b.BLUE,'center',1360)
        s.text('给地球看病 · 四步会诊',350,650,43,b.CORAL,'center',1220)
        return s
    row=next((r for r in DATA if r['start']<=t<r['end']),DATA[0] if t<DATA[0]['start'] else DATA[-1]);mode=row['mode'];age=max(0,t-row['start'])
    mapstart=next(r['start'] for r in DATA if r['mode']=='线索')
    CASES=('欢迎','观察','秘鲁','印尼','江南','思考','联系')
    iscase=mode in CASES
    ismap=mode not in CASES and mode not in ('会诊','四步')
    s.image(str(b.BG),0,0,1920,1080)
    if iscase:
        s.text('海洋“发烧”了',36,30,57,b.INK,w=1000);s.text('厄尔尼诺 · 从三地情境开始',38,101,30,b.SOFT,w=1000)
        s.rect(398,155,1500,875,fill=b.CREAM,stroke='#98bcc6',width=3,r=27)
        s.text('相隔万里的三幅画面，有什么联系？',438,191,51,b.INK,w=1410)
        labels=['图一：秘鲁渔港（情境资料图）','图二：印度尼西亚烟霾','图三：江南洪水与积水']
        active=['秘鲁','印尼','江南'].index(mode) if mode in ('秘鲁','印尼','江南') else -1
        for j in range(3):
            x=430+j*486;sel=active==j;dim=active>=0 and not sel
            s.rect(x-5,290,473,626,fill='#fff2cd' if sel else '#eaf0ed',stroke=b.CORAL if sel else '#bdd0d3',width=4 if sel else 1,r=17)
            s.image(IMAGES[j] if dim else b.PHOTOS[j],x+7,305,449,500,fit='cover',cropFocusY=.62 if j==0 else .5)
            lines=wrap(labels[j],32,449)
            for k,line in enumerate(lines):s.text(line,x+6,837+k*42,32,b.INK,'center',449)
            if sel:
                # Warm light bulbs around the currently discussed photo, with a slow pulse.
                pulse=.5+.5*math.sin(age*4)
                for k in range(7):
                    lx=x+18+k*71
                    for ly in (291,815):
                        s.ellipse(lx-9,ly-9,18,18,'#ffe8ab',None)
                        s.ellipse(lx-4,ly-4,8,8,'#fff7d6' if pulse>.5 else '#f4c258',None)
        s.text('历史资料照片，非同年同一次事件证据 · 详细出处见素材说明',425,967,24,b.SOFT,'center',1440)
    elif mode in ('会诊','四步'):
        s.rect(25,155,1460,875,fill=b.CREAM,stroke='#98bcc6',r=28)
        s.text('跟我当一回“地球医生”',80,230,57,b.INK,w=1330)
        s.text('四步会诊',75,350,48,b.BLUE,'center',1340)
        phase=min(3,int(age/(max(.1,row['end']-row['start'])/4)))
        for j,label in enumerate(['测体征','查病因','追并发症','开处方']):
            x=70+j*350;sel=mode=='四步' and j==phase
            s.rect(x,485,323,230,fill='#ffedc8' if sel else '#e4f1ef',stroke=b.CORAL if sel else '#9cbfc1',width=4 if sel else 2,r=25)
            s.text(str(j+1),x,510,62,b.CORAL,'center',323);s.text(label,x,615,45,b.INK,'center',323)
        s.text('从海温读数出发，找机制、看影响、想应对',75,870,40,b.BLUE,'center',1340)
    else:
        # NOAA's original official map is the main background, not a small inset panel.
        s.rect(0,0,1920,1080,fill='#eef9fa',stroke=None,r=0)
        s.text('定位Niño3.4区' if mode in ('测量','定位','结束') else '线索藏在赤道中东太平洋',40,38,55,b.INK,w=1390)
        s.text('官方原图 · NOAA Physical Sciences Laboratory',42,117,26,b.SOFT,w=1350)
        scale=1850/MW;target=(35+458*scale,245+113*scale)
        zoom=1+.08*b.ease(age/1.2) if mode=='定位' else 1.08 if mode=='结束' else 1
        mx=target[0]-458*scale*zoom;my=target[1]-113*scale*zoom
        s.image(str(MAP),mx,my,MW*scale*zoom,MH*scale*zoom)
        # Separate annotations never redraw boundaries or replace the official labels.
        rx=mx+280*scale*zoom;ry=my+95*scale*zoom;rw=178*scale*zoom;rh=37*scale*zoom
        thick=5+round((1+math.sin(t*4))*2)
        s.rect(rx,ry,rw,rh,fill=None,stroke=b.CORAL,width=thick,r=2)
        rad=12+6*(.5+.5*math.sin(t*3));s.ellipse(target[0]-rad,target[1]-rad,rad*2,rad*2,None,b.CORAL,4)
        s.text('170°W—120°W  ·  5°N—5°S',40,939,44,b.INK,'center',1410)
        s.text('官方图保持比例；定位段围绕Niño3.4做局部推近',45,1010,23,b.SOFT,w=1400)
    # Change sides along the bottom edge BEFORE the map appears.
    walkstart=mapstart-1.45;right=t>=mapstart
    if t<DATA[0]['start']:
        q=b.ease((t-TITLE)/.70);px=-390+390*q;py=605;size=400;pose=13 if int(t/.18)%2==0 else 14
        presenter(s,pose,px,py,size,t)
    elif walkstart<=t<mapstart:
        q=b.ease((t-walkstart)/1.45);presenter(s,13 if int((t-walkstart)/.17)%2==0 else 14,20+1560*q,775,300,t)
    elif ismap:
        scale=1850/MW;tx=35+458*scale;ty=245+113*scale;size=500
        px=tx-55/PW*size;py=ty-100/PH*size
        presenter(s,19,px,py,size,t,True)
    elif right:
        presenter(s,8 if mode=='四步' else 3,1510,650,410,t)
    else:presenter(s,row['pose'],0+math.sin(t*.8)*2,600+math.sin(t*1.5)*2,410,t)
    if t>=DATA[0]['start']:bubble(s,row['text'],right)
    s.rect(0,1075,1920,5,fill='#d6e7e5',stroke=None,r=0);s.rect(0,1075,1920*t/DURATION,5,fill=b.BLUE,stroke=None,r=0)
    return s
source=inspect.getsource(v.render).replace("fw=b.F[a['size']].getlength(line)","fw=b.F[a['size']].getlength(line);y+=b.F[a['size']].getmetrics()[0]").replace("anchor='lt'","anchor='ls'")
env=dict(v.__dict__);env['scene']=scene;exec(source,env);render=env['render']
def main():
    (ROOT/'台词与时间轴.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2),encoding='utf-8')
    for label,mode in [('图片强调','秘鲁'),('官方地图','定位'),('新动作','线索')]:
        t=next(r['start'] for r in DATA if r['mode']==mode)+.6;render(t).save(ROOT/f'预览_{label}.png')
    middle=ROOT/'交付'/'海洋发烧了_正文第一部分_右侧左指_v8.mp4'
    cmd=[EXE,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(ROOT/'配音'/'复用台词_标题衔接.wav'),'-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(middle)]
    with open(ROOT/'.build'/'render.log','w') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        for n in range(math.ceil(DURATION*24)):
            p.stdin.write(render(n/24).tobytes())
            if n%240==0:print(f'Render {n/24:.0f}/{DURATION:.2f}',flush=True)
        p.stdin.close();assert p.wait()==0
    opening=ROOT.parent/'得意黑_大字无水印_v6'/'.build'/'开场_双水印处理.mp4'
    final=ROOT/'交付'/'海洋发烧了_最新批注落实_右侧左指_v8.mp4'
    graph='[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24,setpts=PTS-STARTPTS[v0];[1:v]setsar=1,fps=24,setpts=PTS-STARTPTS[v1];[0:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a0];[1:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]'
    with open(ROOT/'.build'/'join.log','w') as log:subprocess.run([EXE,'-y','-i',str(opening),'-i',str(middle),'-filter_complex',graph,'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','19','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)],stdout=log,stderr=log,check=True)
    result=subprocess.run([EXE,'-v','error','-i',str(final),'-f','null','-'],capture_output=True);assert result.returncode==0,result.stderr
    report={'decode':'PASS','body_seconds':DURATION,'voice':'reused v7 Xiaoyi audio; no new synthesis','new_pose':'19 generated right-side left-facing teaching pose; original hairclip side preserved','pointer_anchor':'ruler tip aligns with official Niño3.4 east boundary at 120W','map_original_dimensions':[MW,MH],'map_origin':'NOAA PSL official GIF converted to PNG; no redraw; 8% focused zoom','caption':'date/location line removed from screen, sources preserved separately; Peru is explicitly marked illustrative historical photo','inactive_photos':'grayscale and darkened','active_photo':'pulsing warm light bulbs','walk':'along lower edge before map appears, includes audio-driven mouth overlays','output':str(final)}
    (ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'素材说明.md').write_text('v8沿用v7的晓伊生动化台词音频，补短标题和转换。新增19号右侧向左上指教学姿势，PNG保留透明度；海图直接使用NOAA PSL原图，原始分辨率685×244，非重新绘制，局部放大不增加原图细节。秘鲁渔港属于情境资料图，不作为空舱而归的实拍证据。\n三张案例图片的完整作者、日期、许可与原始链接见此前正文日系2D_配音_v2/素材来源与使用说明.md；原日期保留在来源记录，不在图下注记占空间。\nNOAA来源：https://psl.noaa.gov/data/timeseries/month/Nino34_CPC/\n',encoding='utf-8')
    print(final,flush=True)
if __name__=='__main__':main()
