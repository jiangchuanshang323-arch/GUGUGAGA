from pathlib import Path
import asyncio,sys,subprocess
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'runtime'))
sys.path.insert(0,str(ROOT.parents[1]/'ocean_animation_demo_20261011'/'runtime'))
import edge_tts,imageio_ffmpeg
OUT=ROOT/'音色试听'/'咕咕嘎嘎';OUT.mkdir(exist_ok=True)
async def main():
    for voice,label in [('zh-CN-XiaoyiNeural','01_晓伊'),('zh-TW-HsiaoChenNeural','02_晓臻'),('zh-TW-HsiaoYuNeural','03_晓雨')]:
        p=OUT/(label+'.mp3')
        for attempt in range(3):
            try:
                await edge_tts.Communicate('咕咕嘎嘎！',voice,rate='+5%',connect_timeout=15,receive_timeout=30).save(str(p))
                r=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(p),'-f','null','-'],capture_output=True)
                assert r.returncode==0 and p.stat().st_size>1000
                print(label+' PASS',flush=True);break
            except Exception as e:
                if attempt==2:raise
                await asyncio.sleep(2)
        await asyncio.sleep(1)
asyncio.run(main())
