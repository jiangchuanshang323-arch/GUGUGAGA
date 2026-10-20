from pathlib import Path
import sys,json,wave,subprocess,math
import numpy as np
ROOT=Path(__file__).resolve().parent;V3=ROOT.parent/'正文晓伊_口型与大画面_v3';V4=ROOT.parent/'开场衔接_两端对齐_v4'
sys.path.insert(0,str(V4))
import build_joined_video as v
EXE=v.b.imageio_ffmpeg.get_ffmpeg_exe();RATE=24000
def decode(p):
    raw=subprocess.check_output([EXE,'-v','error','-i',str(p),'-f','s16le','-ac','1','-ar',str(RATE),'-'])
    return np.frombuffer(raw,dtype='<i2').copy()
def compact(p):
    pcm=decode(p);step=240;n=len(pcm)//step
    rms=np.sqrt(np.mean((pcm[:n*step].reshape(n,step).astype(float)/32768)**2,axis=1))
    active=np.where(rms>.005)[0];assert len(active)>0
    lo=max(0,active[0]*step-960);hi=min(len(pcm),(active[-1]+1)*step+1320)
    # Trim boundary silence only around detected speech with consonant margins.
    voiced=pcm[lo:hi];cuts=[];inside=rms<.0045
    start=None
    for i,silent in enumerate(list(inside)+[False]):
        if silent and start is None:start=i
        if not silent and start is not None:
            a,z=start*step,i*step
            if a>lo+960 and z<hi-1320 and z-a>8400:
                # Retain 0.22 s of any internal silence longer than 0.35 s.
                left=a+2640;right=z-2640
                if right>left:cuts.append((left-lo,right-lo))
            start=None
    parts=[];cursor=0
    for a,z in cuts:parts.append(voiced[cursor:a]);cursor=z
    parts.append(voiced[cursor:]);result=np.concatenate(parts)
    return result,{'original_seconds':len(pcm)/RATE,'trimmed_seconds':len(result)/RATE,'internal_silences_shortened':len(cuts),'boundary_seconds_removed':(len(pcm)-(hi-lo))/RATE}
def save_wav(p,pcm):
    with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm.astype('<i2').tobytes())
def main():
    original=json.loads((V3/'配音时间轴.json').read_text(encoding='utf-8'));data=[];chunks=[];cursor=0;stats=[]
    for i,row in enumerate(original):
        pcm,stat=compact(V3/'配音'/f'{i+1:02d}.mp3');gap=.22 if i==4 else .14
        pcm=np.concatenate([pcm,np.zeros(round(gap*RATE),dtype='<i2')]);duration=len(pcm)/RATE
        item=dict(row,start=cursor,end=cursor+duration);data.append(item);cursor+=duration;chunks.append(pcm)
        stats.append(dict(stat,segment=i+1,added_pause=gap))
    body=np.concatenate(chunks);save_wav(ROOT/'配音'/'正文紧凑.wav',body)
    bridge,bridge_stats=compact(V4/'配音'/'衔接_1.mp3')
    bridge=np.concatenate([np.zeros(round(1.9*RATE),dtype='<i2'),bridge,np.zeros(round(.12*RATE),dtype='<i2')])
    lead=len(bridge)/RATE;full=np.concatenate([bridge,body]);duration=len(full)/RATE
    save_wav(ROOT/'配音'/'衔接与正文紧凑.wav',full)
    v.b.DATA=data;v.b.DURATION=len(body)/RATE;v.b.PCM=body.astype(np.float32)/32768;v.b.RATE=RATE
    v.INFO={'bridge_duration':lead,'total_duration':duration,'walk_duration':1.9,'bridge_speech':[{'start':1.9,'end':lead,'text':'咕咕嘎嘎！欢迎来到水下课堂。'}]}
    v.BRIDGE=lead;v.DURATION=duration;v.PCM=full.astype(np.float32)/32768;v.RATE=RATE
    assert [d['bubble'] for d in data]==[d['bubble'] for d in original]
    (ROOT/'配音时间轴.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'停顿调整.json').write_text(json.dumps({'segments':stats,'bridge':bridge_stats,'question_added_pause_seconds':.22,'body_seconds':len(body)/RATE,'bridge_seconds':lead,'middle_seconds':duration},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Body {len(body)/RATE:.2f}s; bridge {lead:.2f}s; saved {43.428-len(body)/RATE:.2f}s',flush=True)
    # The watermark alternates between two small regions in the opening.
    clean=ROOT/'.build'/'开场_去小云雀水印.mp4'
    filt="delogo=x=1066:y=581:w=134:h=44:show=0:enable='lt(t,4.35)+gt(t,7.55)',delogo=x=14:y=174:w=134:h=47:show=0:enable='between(t,4.0,8.15)'"
    subprocess.run([EXE,'-y','-v','error','-i',str(ROOT.parents[1]/'外部生成视频'/'shot_01_用户开场_20261012.mp4'),'-vf',filt,'-c:v','libx264','-crf','18','-preset','fast','-c:a','copy',str(clean)],check=True)
    for t in (2,6,9.8):subprocess.run([EXE,'-v','error','-ss',str(t),'-i',str(clean),'-frames:v','1','-vf','scale=960:-1','-y',str(ROOT/'.build'/f'去水印_{t}.png')],check=True)
    middle=ROOT/'.build'/'紧凑正文.mp4'
    cmd=[EXE,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(ROOT/'配音'/'衔接与正文紧凑.wav'),'-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest',str(middle)]
    with open(ROOT/'.build'/'encode.log','w') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        for frame in range(math.ceil(duration*24)):
            p.stdin.write(v.render(frame/24).tobytes())
            if frame%240==0:print(f'{frame/24:.0f}/{duration:.1f}s',flush=True)
        p.stdin.close();assert p.wait()==0
    final=ROOT/'交付'/'海洋发烧了_去小云雀水印_紧凑配音_v5.mp4'
    graph='[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24,fade=t=out:st=9.963333:d=0.12,setpts=PTS-STARTPTS[v0];[1:v]setsar=1,fps=24,setpts=PTS-STARTPTS[v1];[0:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-18:TP=-1.5:LRA=9,aresample=48000,asetpts=PTS-STARTPTS[a0];[1:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-18:TP=-1.5:LRA=9,aresample=48000,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]'
    with open(ROOT/'.build'/'join.log','w') as log:subprocess.run([EXE,'-y','-i',str(clean),'-i',str(middle),'-filter_complex',graph,'-map','[v]','-map','[a]','-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)],stdout=log,stderr=log,check=True)
    check=subprocess.run([EXE,'-v','error','-i',str(final),'-f','null','-'],capture_output=True);assert check.returncode==0,check.stderr
    (ROOT/'验证结果.json').write_text(json.dumps({'output':str(final),'expected_duration':10.083333+duration,'full_decode':'PASS','original_text_preserved':True,'question_added_pause':.22,'audio_resynthesized':False,'watermark_method':'localized FFmpeg delogo; original retained; AI label retained','bytes':final.stat().st_size},ensure_ascii=False,indent=2),encoding='utf-8')
    print('FINAL PASS '+str(final),flush=True)
if __name__=='__main__':main()
