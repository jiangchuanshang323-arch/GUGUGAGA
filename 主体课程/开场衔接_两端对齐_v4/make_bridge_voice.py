from pathlib import Path
import sys,asyncio,subprocess,wave,json
ROOT=Path(__file__).resolve().parent;V2=ROOT.parent/'正文日系2D_配音_v2';V3=ROOT.parent/'正文晓伊_口型与大画面_v3'
sys.path.insert(0,str(V2/'runtime'));sys.path.insert(0,str(ROOT.parents[1]/'ocean_animation_demo_20261011'/'runtime'))
import edge_tts,imageio_ffmpeg
TEXTS=['咕咕嘎嘎！欢迎来到水下课堂。']
async def main():
    cursor=1.9;pcm=bytes(round(cursor*24000)*2);timeline=[];exe=imageio_ffmpeg.get_ffmpeg_exe()
    for i,text in enumerate(TEXTS):
        p=ROOT/'配音'/f'衔接_{i+1}.mp3'
        if not p.exists() or p.stat().st_size<1000:
            for attempt in range(3):
                try:
                    await edge_tts.Communicate(text,'zh-CN-XiaoyiNeural',rate='+5%',connect_timeout=15,receive_timeout=30).save(str(p));break
                except Exception:
                    if attempt==2:raise
                    await asyncio.sleep(2)
        chunk=subprocess.check_output([exe,'-v','error','-i',str(p),'-f','s16le','-ac','1','-ar','24000','-'])
        chunk+=bytes(round(.28*24000)*2);duration=len(chunk)/48000
        timeline.append({'start':cursor,'end':cursor+duration,'text':text});cursor+=duration;pcm+=chunk
        print(i+1,duration,flush=True);await asyncio.sleep(1)
    with wave.open(str(V3/'配音'/'完整配音.wav'),'rb') as w:
        assert w.getframerate()==24000 and w.getnchannels()==1
        pcm+=w.readframes(w.getnframes())
    with wave.open(str(ROOT/'配音'/'衔接与正文.wav'),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm)
    info={'bridge_duration':cursor,'total_duration':len(pcm)/48000,'walk_duration':1.9,'bridge_speech':timeline}
    (ROOT/'衔接时间轴.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8');print(info,flush=True)
asyncio.run(main())
