from pathlib import Path
import sys,asyncio,json
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'runtime'))
import edge_tts
OUT=ROOT/'音色试听';OUT.mkdir(exist_ok=True)
TEXT='相隔上万公里，它们可能有什么联系？今天，我们当一回地球医生，完成一次全球会诊。医生看病，先测体温。'
async def main():
    voices=await edge_tts.list_voices()
    zh=[{'name':v['ShortName'],'gender':v['Gender']} for v in voices if v['Locale'].startswith('zh')]
    print(json.dumps(zh,ensure_ascii=False),flush=True)
    names={v['ShortName'] for v in voices}
    for voice,label in [('zh-CN-XiaoyiNeural','01_晓伊_普通话女声'),('zh-TW-HsiaoChenNeural','02_晓臻_台湾国语女声'),('zh-TW-HsiaoYuNeural','03_晓雨_台湾国语女声')]:
        if voice not in names:continue
        existing=OUT/(label+'.mp3')
        if existing.exists() and existing.stat().st_size>1000:continue
        for attempt in range(3):
            try:
                await edge_tts.Communicate(TEXT,voice,rate='+5%',connect_timeout=15,receive_timeout=30).save(str(OUT/(label+'.mp3')))
                print('Saved '+label,flush=True);break
            except Exception as e:
                if attempt==2:print('Failed '+voice+': '+type(e).__name__,flush=True)
                else:await asyncio.sleep(2)
        await asyncio.sleep(1)
    (OUT/'试听说明.json').write_text(json.dumps({'text':TEXT,'rate':'+5%','source':'Microsoft Edge TTS','voices':zh},ensure_ascii=False,indent=2),encoding='utf-8')
asyncio.run(main())
