from pathlib import Path
import sys,json,math,re,wave,subprocess,hashlib,shutil
from functools import lru_cache
from PIL import Image,ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parent;V3=ROOT.parent/'正文晓伊_口型与大画面_v3'
sys.path.insert(0,str(V3))
import build_lesson as b
INFO=json.loads((ROOT/'衔接时间轴.json').read_text(encoding='utf-8'))
BRIDGE=INFO['bridge_duration'];DURATION=INFO['total_duration'];W,H,FPS=b.W,b.H,b.FPS
with wave.open(str(ROOT/'配音'/'衔接与正文.wav'),'rb') as w:
    RATE=w.getframerate();PCM=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
def speaking(t):
    a=max(0,int((t-.02)*RATE));z=min(len(PCM),int((t+.025)*RATE));v=PCM[a:z]
    rms=float(np.sqrt(np.mean(v*v))) if len(v) else 0
    return 0 if rms<.011 else 1 if rms<.055 else 2 if rms<.13 else 3
@lru_cache(None)
def bubble_layout(message):
    # Preserve every character, reflow into one Chinese paragraph.
    text=message.replace('\n','')
    for size in range(50,41,-1):
        lines=b.balanced_lines(text,size);height=len(lines)*round(size*1.26)+48
        if height<=282:break
    assert ''.join(lines)==text and height<=282
    width=min(465,max(320,math.ceil(max(b.F[size].getlength(s) for s in lines))+48))
    return size,lines,width,height
def bubble(s,message,tip):
    size,lines,width,height=bubble_layout(message);x=35+(465-width)/2;y=168
    center=x+width*.52;bottom=y+height
    # A solid, outlined tail points directly toward the presenter's hood.
    tipx,tipy=tip;tipy=max(tipy,bottom+28)
    points=[(center-20,bottom-4),(tipx,tipy),(center+20,bottom-4)]
    s.items.append({'kind':'polygon','points':[(a+6,c+8) for a,c in points],'fill':'#9fbec0','stroke':None,'width':0})
    s.rect(x+6,y+8,width,height,fill='#9fbec0',stroke=None,r=27)
    s.items.append({'kind':'polygon','points':points,'fill':b.CREAM,'stroke':'#96bdc7','width':3})
    s.rect(x,y,width,height,fill=b.CREAM,stroke='#96bdc7',width=3,r=27)
    # Hide the tail's base line to form a single connected bubble silhouette.
    s.rect(center-17,bottom-6,34,8,fill=b.CREAM,stroke=None,r=0)
    for j,line in enumerate(lines):
        s.text(line,x+24,y+24+j*round(size*1.26),size,b.INK,'justify' if j<len(lines)-1 else 'left',width-48)
def strip_old_presenter_and_bubble(s,remove_presenter=False):
    kept=[]
    for a in s.items:
        if a['kind']=='rect' and a.get('y') in (168,176):continue
        if a['kind']=='line' and all(x<520 and 300<y<510 for x,y in a['points']):continue
        if a['kind']=='text' and a['x']<520 and 185<a['y']<475:continue
        if remove_presenter:
            if a['kind']=='image' and ('独立动作PNG' in a['path'] or '口型_' in a['path']):continue
            if a['kind']=='ellipse' and a.get('y')==970:continue
        kept.append(a)
    s.items=kept
def scene(t):
    if t>=BRIDGE:
        u=t-BRIDGE;s=b.scene(u);strip_old_presenter_and_bubble(s)
        row=next((r for r in b.DATA if r['start']<=u<r['end']),b.DATA[-1])
        bubble(s,row['bubble'],(267,480));return s
    s=b.scene(0,index=0,static=True);strip_old_presenter_and_bubble(s,True)
    # Enter from left with alternating foot poses, followed by a speaking pose.
    progress=b.ease((t-.45)/1.32);px=-505+(517*progress);py=475
    if t<1.9:
        pose=13 if int(max(0,t-.45)/.15)%2==0 else 14
        py+=math.sin(max(0,t-.45)*math.pi/.15)*4
    else:pose=3
    s.ellipse(px+80,970,310,20,'#c7c8be');s.image(b.SPRITES[pose],px,py,500,500)
    if t>=1.9:
        mx,my,mw,mh=b.MOUTH_CENTERS[pose];scale=500/512;state=speaking(t)
        s.image(str(V3/'素材'/f'口型_{pose:02d}_{state}.png'),px+(mx-mw/2)*scale,py+(my-mh/2)*scale,mw*scale,mh*scale)
        bubble(s,INFO['bridge_speech'][0]['text'],(267,480))
    return s
@lru_cache(None)
def justified_positions(text,size,width):
    # Keep Latin scientific names intact while spacing Chinese glyphs.
    tokens=re.findall(r'[A-Za-zÀ-ÿ0-9]+(?:\.[0-9]+)*|.',text)
    lengths=[b.F[size].getlength(token) for token in tokens]
    gap=(width-sum(lengths))/(len(tokens)-1) if len(tokens)>1 else 0
    x=0;out=[]
    for token,length in zip(tokens,lengths):out.append((token,x));x+=length+gap
    return out
def render(t):
    s=scene(t);im=Image.new('RGB',(W,H),b.CREAM);d=ImageDraw.Draw(im)
    for a in s.items:
        kind=a['kind']
        if kind=='image':
            x,y,w,h=[round(a[v]) for v in ('x','y','w','h')]
            if a.get('fit')=='cover':
                key=(a['path'],w,h,'v4_cover');art=b.IMAGES.get(key)
                if art is None:
                    src=Image.open(a['path']).convert('RGBA');scale=max(w/src.width,h/src.height)
                    nw,nh=round(src.width*scale),round(src.height*scale);src=src.resize((nw,nh),Image.Resampling.LANCZOS)
                    left=(nw-w)//2;top=round((nh-h)*a.get('cropFocusY',.5));art=src.crop((left,top,left+w,top+h));b.IMAGES[key]=art
            else:art=b.img(a['path'],w,h)
            im.paste(art,(x,y),art);d=ImageDraw.Draw(im)
        elif kind=='rect':d.rounded_rectangle((a['x'],a['y'],a['x']+a['w'],a['y']+a['h']),radius=a['r'],fill=a['fill'],outline=a['stroke'],width=a['width'])
        elif kind=='ellipse':d.ellipse((a['x'],a['y'],a['x']+a['w'],a['y']+a['h']),fill=a['fill'],outline=a['stroke'],width=a['width'])
        elif kind=='line':d.line(a['points'],fill=a['color'],width=a['width'],joint='curve')
        elif kind=='polygon':
            d.polygon(a['points'],fill=a['fill'])
            if a['stroke']:d.line(a['points']+[a['points'][0]],fill=a['stroke'],width=a['width'],joint='curve')
        elif kind=='text':
            for j,line in enumerate(a['text'].split('\n')):
                x,y=a['x'],a['y']+j*a['lineHeight'];fw=b.F[a['size']].getlength(line)
                assert fw<=a['w']+3,(line,fw,a['w'])
                if a['align']=='justify':
                    for token,offset in justified_positions(line,a['size'],a['w']):d.text((x+offset,y),token,font=b.F[a['size']],fill=a['color'],anchor='lt')
                else:
                    if a['align']=='center':x+=(a['w']-fw)/2
                    elif a['align']=='right':x+=a['w']-fw
                    d.text((x,y),line,font=b.F[a['size']],fill=a['color'],anchor='lt')
    if t<.18:return Image.new('RGB',(W,H),'black')
    if t<.53:im=Image.blend(Image.new('RGB',(W,H),'black'),im,b.ease((t-.18)/.35))
    return im
def main():
    exe=b.imageio_ffmpeg.get_ffmpeg_exe();middle=ROOT/'.build'/'衔接正文_v4.mp4'
    for t in (.8,1.5,3.3,BRIDGE+1,BRIDGE+b.DATA[-1]['start']+1):render(t).save(ROOT/'.build'/f'画面_{t:.1f}.png')
    render(BRIDGE+1).save(ROOT/'气泡修订预览.png')
    cmd=[exe,'-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(ROOT/'配音'/'衔接与正文.wav'),'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(middle)]
    with open(ROOT/'.build'/'encode.log','w') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        for n in range(math.ceil(DURATION*FPS)):
            p.stdin.write(render(n/FPS).tobytes())
            if n%(FPS*10)==0:print(f'{n/FPS:.0f}/{DURATION:.1f}s',flush=True)
        p.stdin.close();assert p.wait()==0
    source=Path('G:/shot_01.mp4');archive=ROOT.parents[1]/'外部生成视频';archive.mkdir(exist_ok=True)
    archived=archive/'shot_01_用户开场_20261012.mp4'
    if not archived.exists():shutil.copy2(source,archived)
    assert hashlib.sha256(source.read_bytes()).digest()==hashlib.sha256(archived.read_bytes()).digest()
    final=ROOT/'交付'/'海洋发烧了_开场衔接与正文_v4.mp4'
    # Preserve the opening's full duration and audio, normalize canvas and loudness.
    graph='[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24,fade=t=out:st=9.963333:d=0.12,setpts=PTS-STARTPTS[v0];[1:v]setsar=1,fps=24,setpts=PTS-STARTPTS[v1];[0:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-18:TP=-1.5:LRA=9,aresample=48000,asetpts=PTS-STARTPTS[a0];[1:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-18:TP=-1.5:LRA=9,aresample=48000,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]'
    cmd=[exe,'-y','-i',str(archived),'-i',str(middle),'-filter_complex',graph,'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)]
    with open(ROOT/'.build'/'join.log','w') as log:subprocess.run(cmd,stderr=log,stdout=log,check=True)
    result=subprocess.run([exe,'-v','error','-i',str(final),'-f','null','-'],capture_output=True,text=True);assert result.returncode==0,result.stderr
    report={'opening_source':str(archived),'opening_unchanged_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'opening_seconds':10.083333,'bridge_seconds':BRIDGE,'body_seconds':b.DURATION,'expected_total_seconds':10.083333+DURATION,'resolution':[W,H],'fps':FPS,'bubble':'solid tail points to character; Chinese justified lines and left-aligned last line','original_body_text_preserved':True,'full_decode':'PASS','output':str(final),'bytes':final.stat().st_size}
    (ROOT/'合成验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
