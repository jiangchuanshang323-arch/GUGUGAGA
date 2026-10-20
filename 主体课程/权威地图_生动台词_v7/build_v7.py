from pathlib import Path
import sys,json,asyncio,subprocess,wave,math,inspect,urllib.request,hashlib
import numpy as np
from PIL import Image,ImageFont
ROOT=Path(__file__).resolve().parent
for name in ('素材','配音','.build','交付'):(ROOT/name).mkdir(parents=True,exist_ok=True)
PROJECT=ROOT.parents[1]
sys.path.insert(0,str(ROOT.parent/'开场衔接_两端对齐_v4'))
import build_joined_video as v
b=v.b
sys.path.insert(0,str(ROOT.parent/'正文日系2D_配音_v2'/'runtime'))
import edge_tts
EXE=b.imageio_ffmpeg.get_ffmpeg_exe()
FONT=ROOT.parent/'得意黑_大字无水印_v6'/'素材'/'SmileySans-Oblique.ttf'
b.F={s:ImageFont.truetype(str(FONT),s) for s in range(18,97)}
b.balanced_lines.cache_clear();v.justified_positions.cache_clear()
MAPURL='https://cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ninoareas_c.jpg'
MAP=ROOT/'素材'/'NOAA_CPC_四个Niño区域_原图.jpg'
if not MAP.exists():
    req=urllib.request.Request(MAPURL,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=40) as response:MAP.write_bytes(response.read())
(ROOT/'素材来源.json').write_text(json.dumps({'publisher':'NOAA National Weather Service Climate Prediction Center','page':'https://cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/nino_regions.shtml','image':MAPURL,'sha256':hashlib.sha256(MAP.read_bytes()).hexdigest(),'use':'Official image displayed intact, only resized without changing labels or boundaries. Highlight overlay is separate.','dimensions':Image.open(MAP).size},ensure_ascii=False,indent=2),encoding='utf-8')
LINES=[
 ('欢迎','咕咕嘎嘎！欢迎来到水下课堂。',3),
 ('观察','海洋怎么会“发烧”？先跟我看看，地球上发生了哪些怪事。',3),
 ('秘鲁','在秘鲁，渔船出海，却空舱而归。',6),
 ('印尼','在印度尼西亚，干旱和山火拉响警报。',6),
 ('江南','再看中国江南，暴雨来袭，城市出现积水。',6),
 ('思考','一个缺鱼，一个缺水，一个水太多……',9),
 ('联系','相隔上万公里，它们会不会有共同的线索？',9),
 ('线索','把目光移到这里——赤道中东太平洋。',6),
 ('增暖','这里的海水异常变暖了！这场海洋“发烧”，可能牵动远方的天气。',3),
 ('会诊','今天，跟我当一回“地球医生”！',3),
 ('四步','测体征、查病因、追并发症，最后开处方。',8),
 ('测量','看病先测体温，可这么大的海洋，“体温计”放在哪儿？',9),
 ('定位','看这里——赤道太平洋的尼诺三点四区。',6),
 ('结束','我们就从这片海域的海温变化，开始寻找答案！',3),
]
DATA=[];PCM=np.zeros(1,dtype=np.float32);DURATION=1
async def audio():
    global DATA,PCM,DURATION
    cursor=1.55;parts=[np.zeros(round(cursor*24000),dtype='<i2')]
    for i,(mode,text,pose) in enumerate(LINES):
        mp3=ROOT/'配音'/f'{i+1:02d}.mp3'
        if not mp3.exists() or mp3.stat().st_size<1000:
            for attempt in range(4):
                try:
                    await edge_tts.Communicate(text,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=20,receive_timeout=40).save(str(mp3))
                    break
                except Exception:
                    if attempt==3:raise
                    await asyncio.sleep(2+attempt)
        raw=subprocess.check_output([EXE,'-v','error','-i',str(mp3),'-f','s16le','-ac','1','-ar','24000','-'])
        samples=np.frombuffer(raw,dtype='<i2');idx=np.flatnonzero(np.abs(samples.astype(np.int32))>220)
        if len(idx):samples=samples[max(0,idx[0]-1200):min(len(samples),idx[-1]+1500)]
        samples=np.concatenate([samples,np.zeros(round(24000*(.20 if mode in ('联系','测量') else .12)),dtype='<i2')])
        seconds=len(samples)/24000
        DATA.append(dict(mode=mode,text=text,pose=pose,start=cursor,end=cursor+seconds));cursor+=seconds;parts.append(samples)
        print(f'Voice {i+1}/{len(LINES)}',flush=True)
    allsamples=np.concatenate(parts);PCM=allsamples.astype(np.float32)/32768;DURATION=len(allsamples)/24000
    with wave.open(str(ROOT/'配音'/'新版讲解.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(allsamples.tobytes())
    (ROOT/'台词与时间轴.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2),encoding='utf-8')

def mouth(t):
    z=PCM[max(0,int((t-.02)*24000)):int((t+.025)*24000)];r=float(np.sqrt(np.mean(z*z))) if len(z) else 0
    return 0 if r<.011 else 1 if r<.055 else 2 if r<.13 else 3
def bubble(s,text,x,tip):
    # Smaller chunks prevent full lines from crowding the teacher's face.
    for size in range(48,37,-1):
        lines=b.balanced_lines(text,size);height=len(lines)*round(size*1.25)+40
        if height<300:break
    width=450;y=155;center=x+width*.52;bottom=y+height
    pts=[(center-22,bottom-3),tip,(center+22,bottom-3)]
    s.items.append(dict(kind='polygon',points=pts,fill=b.CREAM,stroke='#96bdc7',width=3))
    s.rect(x,y,width,height,fill=b.CREAM,stroke='#96bdc7',width=3,r=25)
    s.rect(center-18,bottom-6,36,10,fill=b.CREAM,stroke=None,r=0)
    for j,line in enumerate(lines):s.text(line,x+22,y+20+j*round(size*1.25),size,b.INK,'justify' if j<len(lines)-1 else 'left',width-44)
def scene(t):
    row=next((r for r in DATA if r['start']<=t<r['end']),DATA[0] if t<DATA[0]['start'] else DATA[-1]);mode=row['mode'];age=t-row['start'];s=b.Scene()
    s.image(str(b.BG),0,0,1920,1080)
    s.text('海洋“发烧”了',40,28,58,b.INK,w=900)
    s.text('水下课堂 · 三地情境与测体征',42,96,29,b.SOFT,w=1050)
    mapstart=next(r['start'] for r in DATA if r['mode']=='测量')
    moving=t>=mapstart
    if moving:
        # Map takes the large left area; presenter moves physically to the right.
        bx=22;bw=1435;by=158;bh=865
    else:bx=530;bw=1362;by=158;bh=865
    s.rect(bx+8,by+10,bw,bh,fill='#95bac1',stroke=None,r=27)
    s.rect(bx,by,bw,bh,fill=b.CREAM,stroke='#9abdc2',width=3,r=27)
    if mode in ('欢迎','观察','秘鲁','印尼','江南','思考','联系'):
        s.text('三地情境：看看地球发生了什么',570,190,51,b.INK,w=1260)
        locations=['秘鲁渔港','印度尼西亚','中国江南'];tags=['渔船空舱而归','干旱 · 山火 · 烟霾','暴雨 · 城市积水'];metadata=['帕拉卡斯 · 2019','NASA卫星实拍 · 2015','铜陵大通 · 2020']
        for j in range(3):
            x=563+j*435;selected=mode==['秘鲁','印尼','江南'][j]
            s.rect(x,280,414,632,fill='#fff0cc' if selected else '#eef4ef',stroke=b.CORAL if selected else '#bad1d4',width=3,r=18)
            s.image(b.PHOTOS[j],x+10,292,394,426,fit='cover',cropFocusY=.62 if j==0 else .5)
            s.text(locations[j],x+8,742,43,b.CORAL if selected else b.INK,'center',398)
            s.text(tags[j],x+8,807,33,b.INK,'center',398)
            s.text(metadata[j],x+8,867,27,b.SOFT,'center',398)
        s.text('历史资料照片，用于观察情境，不作为本次事件的直接证据',555,960,28,b.SOFT,'center',1310)
    elif mode in ('会诊','四步'):
        s.text('跟我当一回“地球医生”',580,220,57,b.INK,w=1200)
        s.text('四步会诊',580,355,48,b.BLUE,'center',1200)
        for j,label in enumerate(['测体征','查病因','追并发症','开处方']):
            x=585+j*310;s.rect(x,490,280,230,fill='#e4f1ef',stroke='#9cbfc1',r=25)
            s.text(str(j+1),x,515,61,b.CORAL,'center',280);s.text(label,x,615,45,b.INK,'center',280)
        s.text('从海温读数出发，一步步找到影响与应对',585,860,38,b.BLUE,'center',1210)
    else:
        # The official NOAA image is placed whole, fitted without distortion.
        x=50 if moving else 550;available=1380 if moving else 1320
        s.text('测体征：找到Niño3.4区' if moving else '把目光移向赤道太平洋',x+10,190,48,b.INK,w=available-20)
        src=Image.open(MAP);scale=min(available/src.width,590/src.height);mw=src.width*scale;mh=src.height*scale;mx=x+(available-mw)/2;my=285+(590-mh)/2
        s.image(str(MAP),mx,my,mw,mh)
        if moving:
            s.text('170°W—120°W  ·  5°N—5°S',x,896,44,b.INK,'center',available)
        else:s.text('赤道中东太平洋：追踪海温异常的线索',x,896,39,b.CORAL,'center',available)
        s.text('原图：NOAA / NWS Climate Prediction Center',x,964,27,b.SOFT,'center',available)
        if mode in ('定位','结束'):
            s.rect(mx+267*scale,my+100*scale,(414-267)*scale,39*scale,fill=None,stroke=b.CORAL,width=4,r=1)
    # Walk during transitions; keep the original asymmetrical hairclip intact.
    px=6;py=500;pose=row['pose'];size=500
    if t<1.55:
        px=-490+496*b.ease(t/1.4);pose=13 if int(t/.18)%2==0 else 14
    elif moving:
        progress=b.ease((t-mapstart)/1.9);px=6+1485*progress
        if progress<1:pose=13 if int((t-mapstart)/.18)%2==0 else 14;py+=math.sin((t-mapstart)*12)*5
        elif pose==6:pose=5
    else:px+=math.sin(t*.7)*3;py+=math.sin(t*1.8)*2
    s.ellipse(px+95,997,290,17,'#c7c8be');s.image(b.SPRITES[pose],px,py,size,size)
    if pose in b.MOUTH_CENTERS:
        mx,my,mw,mh=b.MOUTH_CENTERS[pose];scale=size/512
        s.image(str(v.V3/'素材'/f'口型_{pose:02d}_{mouth(t)}.png'),px+(mx-mw/2)*scale,py+(my-mh/2)*scale,mw*scale,mh*scale)
    if t>=1.55:
        bubble(s,row['text'].replace('尼诺三点四','Niño3.4'),1458 if moving else 35,(1732 if moving else 262,505))
    s.rect(0,1074,1920,6,fill='#d6e7e5',stroke=None,r=0);s.rect(0,1074,1920*t/DURATION,6,fill=b.BLUE,stroke=None,r=0)
    return s
source=inspect.getsource(v.render).replace("fw=b.F[a['size']].getlength(line)","fw=b.F[a['size']].getlength(line);y+=b.F[a['size']].getmetrics()[0]").replace("anchor='lt'","anchor='ls'")
env=dict(v.__dict__);env['scene']=scene;exec(source,env);render=env['render']
def main():
    asyncio.run(audio())
    for name,t in [('三地',DATA[2]['start']+.7),('四步',DATA[10]['start']+.5),('官方地图',DATA[12]['start']+.4)]:render(t).save(ROOT/f'预览_{name}.png')
    middle=ROOT/'交付'/'海洋发烧了_正文第一部分_官方地图_v7.mp4'
    cmd=[EXE,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(ROOT/'配音'/'新版讲解.wav'),'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(middle)]
    with open(ROOT/'.build'/'render.log','w') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        for n in range(math.ceil(DURATION*24)):
            p.stdin.write(render(n/24).tobytes())
            if n%240==0:print(f'Render {n/24:.0f}/{DURATION:.1f}',flush=True)
        p.stdin.close();assert p.wait()==0
    opening=ROOT.parent/'得意黑_大字无水印_v6'/'.build'/'开场_双水印处理.mp4'
    final=ROOT/'交付'/'海洋发烧了_开场与新版第一部分_v7.mp4'
    graph='[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24,setpts=PTS-STARTPTS[v0];[1:v]setsar=1,fps=24,setpts=PTS-STARTPTS[v1];[0:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a0];[1:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]'
    cmd=[EXE,'-y','-i',str(opening),'-i',str(middle),'-filter_complex',graph,'-map','[v]','-map','[a]','-c:v','libx264','-crf','19','-preset','fast','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)]
    with open(ROOT/'.build'/'join.log','w') as log:subprocess.run(cmd,stderr=log,stdout=log,check=True)
    check=subprocess.run([EXE,'-v','error','-i',str(final),'-f','null','-'],capture_output=True);assert check.returncode==0,check.stderr
    (ROOT/'制作说明.md').write_text('第一部分修改：使用NOAA CPC原始Niño区域图；显示官方图整图而非重新绘制。地图保持原始比例，角色向右走位。删除底部重复四步会诊导航，扩大内容区。采用已展示的生动化台词、晓伊配音、得意黑、气泡实心尾尖与统一基线。\n正文时长：'+str(round(DURATION,2))+'秒。\n图源：'+MAPURL+'\n成片全片解码检查通过。',encoding='utf-8')
    print(final,flush=True)
if __name__=='__main__':main()
