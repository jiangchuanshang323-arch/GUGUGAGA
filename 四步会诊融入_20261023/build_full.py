"""Integrate the approved 8 s excerpt into the reviewed full course.

Keep every source excerpt frame. Add a paper transition at its editorial cut,
plus page-opening/closing transitions against live neighbouring course frames.
All other video frames are stream-copied. Original speech is reused unchanged;
an exact 59-frame silent action pause is inserted after the existing four-step
line. This is an excerpt integration, not an unprovided 36 s continuous rig.
"""
from pathlib import Path
from functools import lru_cache
import hashlib, io, json, math, os, subprocess, wave
import numpy as np
from PIL import Image,ImageDraw,ImageFont

R=Path(__file__).resolve().parent;P=R.parent;B=R/'.build';C=R/'检查'
for f in [B,C,P/'downloads/archive']:f.mkdir(parents=True,exist_ok=True)
FF='ffmpeg';VERSION='V20261023.02';FPS=24;W,H=1920,1080
OLD=P/'downloads/ocean_beautified_full.mp4'
BASE=P/'downloads/archive/ocean_full_V20261023_01.mp4'
if not BASE.exists():os.link(OLD,BASE)
SOURCE=P/'demooo/预览/四步会诊路线全程/四步会诊路线_原翅膀与帽子贴合_8秒小样.mp4'
OUT=P/'downloads/ocean_full_V20261023_02.mp4'
FONT=P/'主体课程/得意黑_大字无水印_v6/素材/SmileySans-Oblique.ttf'
START,ROUTE_START,ROUTE_END,END=1272,1290,1435,1464
FRONT,CUT,LIVE_BACK=18,12,18
OLD_TOTAL=17028;DELTA=59;NEW_TOTAL=OLD_TOTAL+DELTA;PATCH_TOTAL=251
ORIGINAL_SHA='43eb4f11d6e2c716271d61343717138f504d36d8624c92e01f8d56b702c344dc'
SAMPLE_SHA='f09ce5e1f065ae65336df485b90949ffe45cb27605b50720326f3f002c9430c7'

def digest(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for z in iter(lambda:f.read(1024*1024),b''):h.update(z)
    return h.hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def frames(p,start=0,count=None):
    cmd=[FF,'-v','error','-threads','1','-ss',f'{start/24:.12f}','-i',str(p)]
    if count is not None:cmd+=['-frames:v',str(count)]
    cmd+=['-map','0:v:0','-f','rawvideo','-pix_fmt','rgb24','-']
    q=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);out=[]
    while True:
        z=q.stdout.read(W*H*3)
        if not z:break
        assert len(z)==W*H*3
        out.append(Image.frombytes('RGB',(W,H),z))
    assert q.wait()==0,q.stderr.read();return out
def ease(q):q=max(0,min(1,q));return q*q*(3-2*q)

def wipe(a,b,q,reverse=False):
    """Paper edge travels across the frame; no double-exposed characters."""
    q=ease(q)
    if q<=0:return a.copy()
    if q>=1:return b.copy()
    im=a.copy();edge=round(W*q);x=W-edge if reverse else edge
    if reverse:im.paste(b.crop((x,0,W,H)),(x,0))
    else:im.paste(b.crop((0,0,x,H)),(0,0))
    layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
    for k in range(30,0,-1):
        xx=x-k if reverse else x+k
        if 0<=xx<W:d.line((xx,0,xx,H),fill=(33,57,68,round(22*(1-k/31))),width=1)
    for k in range(-6,7):
        xx=x+k
        if 0<=xx<W:
            f=1-abs(k)/8;col=(255-round(26*(1-f)),250-round(28*(1-f)),235-round(25*(1-f)),255)
            d.line((xx,0,xx,H),fill=col,width=1)
    im.paste(layer,(0,0),layer);return im

def exchange(a,b,q):
    # Reveal the common route background first, then the later actor position.
    # The earlier left actor disappears before the right actor is revealed.
    # A direct paper edge avoids a blank-paper flash or a double exposure.
    return wipe(a,b,q)

@lru_cache(None)
def font(n):return ImageFont.truetype(str(FONT),n)
def subtitle(im,t):
    if t<0 or t>=6.041666667:return im
    words='今天，跟我当一回“地球医生”！' if t<2.2363 else '测体征、查病因、追并发症，最后开处方。'
    layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
    d.rectangle((0,1018,W,H),fill=(36,75,96,243))
    f=font(46);width=f.getlength(words);x=(W-width)/2
    d.text((x,1065),words,font=f,anchor='ls',fill='#fffaf0')
    im.paste(layer,(0,0),layer);return im

def render_patch():
    assert digest(BASE)==ORIGINAL_SHA and digest(SOURCE)==SAMPLE_SHA
    route=frames(SOURCE,0,192);before=frames(BASE,START,FRONT)
    after=frames(BASE,ROUTE_END,END-ROUTE_END)
    assert len(route)==192 and len(before)==18 and len(after)==29
    images=[];scenes=[]
    for i,a in enumerate(before):
        images.append(wipe(a,route[0],i/(FRONT-1),True));scenes.append('入场：原概念镜头→路线纸页')
    for i,a in enumerate(route[:84]):
        images.append(subtitle(a.copy(),i/24));scenes.append('原小样前半：行走与查病因')
    for i in range(CUT):
        im=exchange(route[83],route[84],i/(CUT-1))
        images.append(subtitle(im,(84+i)/24));scenes.append('小样抽选处：纸页转接')
    for i,a in enumerate(route[84:]):
        images.append(subtitle(a.copy(),(96+i)/24));scenes.append('原小样后半：帽子贴合与持板动作')
    for i,a in enumerate(after[:LIVE_BACK]):
        images.append(wipe(route[-1],a,i/(LIVE_BACK-1),True));scenes.append('出场：路线纸页→原Niño3.4定位')
    for a in after[LIVE_BACK:]:images.append(a.copy());scenes.append('恢复原定位镜头')
    assert len(images)==PATCH_TOTAL
    target=B/'四步会诊_带前后过渡.mp4'
    q=subprocess.Popen([FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-g','24','-keyint_min','24','-sc_threshold','0','-movflags','+faststart',str(target)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    nodes=[0,8,17,18,42,78,101,107,113,114,130,155,190,215,221,230,239,250]
    sheet=Image.new('RGB',(1600,math.ceil(len(nodes)/4)*249),'#eaf1f2');d=ImageDraw.Draw(sheet)
    for i,im in enumerate(images):
        q.stdin.write(im.tobytes())
        if i in nodes:
            j=nodes.index(i);x=j%4*400;y=j//4*249;sheet.paste(im.resize((400,225),Image.Resampling.LANCZOS),(x,y));d.text((x+5,y+228),f'{i/24:.3f}s / {i}',font=font(16),fill='#244b60')
            im.save(C/f'衔接设计_{i:03d}.png')
    q.stdin.close();err=q.stderr.read();assert q.wait()==0,err
    sheet.save(C/'前后过渡与抽选衔接总览.jpg',quality=94)
    timeline=[{'frame':i,'base_start':START,'new_time':(START+i)/24,'scene':s} for i,s in enumerate(scenes)]
    (R/'局部画面时间轴.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2))
    return target

def audio():
    z=subprocess.check_output([FF,'-v','error','-i',str(BASE),'-map','0:a:0','-ac','2','-ar','48000','-f','s16le','-'])
    a=np.frombuffer(z,dtype='<i2').reshape(-1,2);target=OLD_TOTAL*2000
    if len(a)>target:
        tail=a[target:].astype(float);assert np.sqrt(np.mean(tail*tail))<50,'Only silent codec padding may be trimmed'
        a=a[:target]
    elif len(a)<target:a=np.pad(a,((0,target-len(a)),(0,0)))
    cut=ROUTE_END*2000;silence=np.zeros((DELTA*2000,2),dtype='<i2')
    out=np.concatenate([a[:cut],silence,a[cut:]])
    assert len(out)==NEW_TOTAL*2000 and np.array_equal(out[:cut],a[:cut]) and np.array_equal(out[cut+len(silence):],a[cut:])
    path=B/'原配音_仅插入动作停顿.wav'
    with wave.open(str(path),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(out.tobytes())
    return path,{'new_speech':False,'speech_speed_changed':False,'original_pcm_before_and_after_pause_identical':True,'inserted_silence_samples':len(silence),'inserted_silence_seconds':DELTA/24,'source_audio_padding_trimmed_or_padded_to_video':True}

def assemble(patch,audio_path):
    # Native source has exact one-second closed GOP boundaries at 53 and 61.
    subprocess.run([FF,'-v','error','-y','-i',str(BASE),'-map','0:v:0','-c','copy','-f','segment','-segment_times','53,61','-reset_timestamps','1','-segment_format_options','avoid_negative_ts=disabled',str(B/'原片_%d.mp4')],check=True)
    counts=[int(probe(B/f'原片_{i}.mp4')['streams'][0]['nb_frames']) for i in range(3)]
    assert counts==[1272,192,15564],counts
    lst=B/'全片合成列表.txt';lst.write_text("file '原片_0.mp4'\nduration 53\nfile '四步会诊_带前后过渡.mp4'\nduration 10.458333333333\nfile '原片_2.mp4'\nduration 648.5\n")
    silent=B/'新版完整画面.mp4'
    subprocess.run([FF,'-v','error','-y','-f','concat','-safe','0','-i',str(lst),'-c','copy',str(silent)],check=True)
    pending=OUT.with_name('.ocean_full_V20261023_02.pending.mp4')
    subprocess.run([FF,'-v','error','-y','-i',str(silent),'-i',str(audio_path),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(pending)],check=True)
    meta=probe(pending);v=next(s for s in meta['streams'] if s['codec_type']=='video')
    assert int(v['nb_frames'])==NEW_TOTAL and (v['width'],v['height'])==(W,H)
    assert abs(float(meta['format']['duration'])-NEW_TOTAL/24)<.03
    # Verify the complete packet timeline is uniformly 24 fps, including seams.
    times=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts','-of','json',str(pending)]))
    pts=sorted(int(p['pts']) for p in times['packets']);assert len(pts)==NEW_TOTAL and pts[0]==0 and set(b-a for a,b in zip(pts,pts[1:]))=={512}
    decode=subprocess.run([FF,'-v','error','-threads','2','-i',str(pending),'-f','null','-'],capture_output=True,check=True);assert not decode.stderr,decode.stderr
    pending.replace(OUT)
    return meta

def export_review():
    times=[52.8,53.2,53.6,53.9,55,57.1,57.5,57.9,58.2,59.5,61,62,62.6,63.4,64,74,82,113,270,554.8,607.5,682.5,710]
    sheet=Image.new('RGB',(1600,math.ceil(len(times)/4)*249),'#eaf1f2');d=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        z=subprocess.check_output([FF,'-v','error','-ss',str(t),'-i',str(OUT),'-frames:v','1','-f','image2pipe','-vcodec','png','-'])
        im=Image.open(io.BytesIO(z)).convert('RGB');x=i%4*400;y=i//4*249;sheet.paste(im.resize((400,225),Image.Resampling.LANCZOS),(x,y));d.text((x+5,y+228),f'{int(t)//60:02d}:{t%60:04.1f}',font=font(17),fill='#244b60')
        if t in [53.6,55,57.5,58.2,59.5,62,63.4,607.5,710]:im.save(C/f'最终编码_{t:g}.png')
    sheet.save(C/'完整版实际编码节点总览.jpg',quality=94)
    return times

def main():
    patch=render_patch();print('局部画面与三处转场已编码',flush=True)
    a,adetail=audio();print('原讲解保留，动作停顿安排完成',flush=True)
    meta=assemble(patch,a);print('完整成片合成及解码完成',flush=True)
    times=export_review()
    report={'version':VERSION,'output':str(OUT),'output_sha256':digest(OUT),'bytes':OUT.stat().st_size,'seconds':NEW_TOTAL/24,'frames':NEW_TOTAL,'resolution':[W,H],'fps':24,'source_version':'V20261023.01','source_sha256':ORIGINAL_SHA,'sample_sha256':SAMPLE_SHA,'sample_all_192_frames_used':True,'sample_is_excerpt_not_continuous_four_station_performance':True,'missing_source_dependency':'rig_reference_v1.py','source_interval_reworked':[53,61],'new_interval':[53,53+PATCH_TOTAL/24],'duration_increase_seconds':DELTA/24,'transitions':['0.75秒纸页展开入场','小样3.5秒抽选处0.5秒纸页转接','0.75秒纸页收束回到原定位镜头'],'audio':adetail,'video_outside_interval_stream_copied':True,'complete_decode':'PASS','packet_timeline_24fps':'PASS','review_times':times,'visual_review':'待实际编码抽帧人工复核；不声称用户应用内实播'}
    (C/'交付记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    (R/'README.md').write_text(f'''# 四步会诊小样融入完整版\n\n当前版本：**{VERSION}**。\n\n以V20261023.01整体美化版为底，使用用户确认的8秒“原翅膀与帽子贴合”小样；该小样是行走段和第四站动作的抽选。完整保留192帧，在内部抽选点增加0.5秒纸页转接，前后各用0.75秒纸页效果融入原片概念收束和Niño3.4定位。**本版不是36秒连续四站表演**；远端v3引用的rig_reference_v1.py未提供，不凭缺失源码声称重建了完整动作。\n\n教学台词、知识顺序、其余美化画面、中国水彩与修复后的处方保留。原配音不重新合成、不变速；只在四步会诊讲完后的静音处增加{DELTA/24:.6f}秒动作停顿。原音频解码后的前后PCM片段完全一致，最终AAC因新增停顿重新编码，不能称整条AAC字节相同。\n\n新时长：{NEW_TOTAL/24:.6f}秒（约11分52秒），1920×1080 / 24fps / {NEW_TOTAL}帧。原片53—61秒的局部改为10.458333秒，其余画面压缩包直接复制。\n\n- 当前完整视频：downloads/ocean_full_V20261023_02.mp4\n- 上一版本：downloads/archive/ocean_full_V20261023_01.mp4\n- 工程：四步会诊融入_20261023/build_full.py\n- 前后衔接预览及输出核对：检查/\n\n角色、动作和路线插画均来自本项目及用户本次素材，没有新生成角色或案例图片。完整解码通过；实际画面抽查状态见检查/交付记录.json。\n''',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()
