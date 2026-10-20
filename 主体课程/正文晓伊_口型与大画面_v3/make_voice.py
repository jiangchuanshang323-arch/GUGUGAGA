from pathlib import Path
import sys, json, asyncio, subprocess, wave
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'正文日系2D_配音_v2'/'runtime'))
sys.path.insert(0,str(ROOT.parents[1]/'ocean_animation_demo_20261011'/'runtime'))
import edge_tts, imageio_ffmpeg
DATA=json.loads((ROOT.parent/'正文首60秒_v1'/'字幕与内容对应.json').read_text(encoding='utf-8'))
OUT=ROOT/'配音';OUT.mkdir(exist_ok=True)
async def main():
    cursor=0;allpcm=b'';exe=imageio_ffmpeg.get_ffmpeg_exe()
    for i,row in enumerate(DATA):
        spoken=row['bubble'].replace('\n','').replace('Niño3.4','尼诺三点四')
        mp3=OUT/f'{i+1:02d}.mp3'
        if not mp3.exists() or mp3.stat().st_size<1000:
            for attempt in range(3):
                try:
                    await edge_tts.Communicate(spoken,'zh-CN-XiaoyiNeural',rate='+5%',pitch='+0Hz',connect_timeout=15,receive_timeout=30).save(str(mp3))
                    break
                except Exception:
                    if attempt==2:raise
                    await asyncio.sleep(2)
            await asyncio.sleep(.8)
        pcm=subprocess.check_output([exe,'-v','error','-i',str(mp3),'-f','s16le','-ac','1','-ar','24000','-'])
        # Short natural gaps; give the question a longer thinking pause.
        tail=.9 if i==4 else .28
        pcm+=bytes(round(24000*tail)*2)
        duration=len(pcm)/48000
        row['original_start']=row['start'];row['original_end']=row['end']
        row['start']=round(cursor,4);row['end']=round(cursor+duration,4);row['spoken']=spoken
        allpcm+=pcm;cursor+=duration
        print(f'{i+1}/10: {duration:.2f}s',flush=True)
    with wave.open(str(OUT/'完整配音.wav'),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(allpcm)
    (ROOT/'配音时间轴.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'TOTAL {cursor:.3f}s',flush=True)
asyncio.run(main())
