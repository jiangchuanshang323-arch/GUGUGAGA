from pathlib import Path
import json,subprocess,importlib.util,io,math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent;D=PROJECT/'demooo'
s=importlib.util.spec_from_file_location('delivery8',D/'manage_videos.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
r=json.loads((ROOT/'验证.json').read_text(encoding='utf-8'));p=Path(r['output']);m.decode(p)
meta=json.loads((ROOT/'台词与时间轴.json').read_text(encoding='utf-8'))
times=[.6,1.7,5.7,9,13,16.2,18.1,22.8,25.5,meta['intros'][1]['start']+.5,meta['pause_start']+1.5,meta['duration']-1]
contact=Image.new('RGB',(1920,870),'#e5eeee');draw=ImageDraw.Draw(contact)
for i,t in enumerate(times):
 b=subprocess.check_output([m.EXE,'-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-f','image2pipe','-vcodec','png','-']);im=Image.open(io.BytesIO(b)).convert('RGB');assert im.size==(1920,1080)
 im.save(ROOT/'检查'/f'实际编码_{t:.2f}.png');x=i%4*480;y=i//4*290;contact.paste(im.resize((480,270)),(x,y));draw.text((x+8,y+273),f'{t:.2f}s',fill='#244b60')
contact.save(ROOT/'检查/实际编码_十二节点.jpg')
audit=json.loads((ROOT/'检查/逐帧文字边界.json').read_text(encoding='utf-8'));assert len(audit)==math.ceil(meta['duration']*24)
assert all(a['silent'] for a in audit if meta['pause_start']<=a['t']<meta['pause_start']+3)
data=json.loads(m.MANIFEST.read_text(encoding='utf-8'));data['segments']['08_地形与配对']={'path':str(p.relative_to(D)),**m.info(p),'decode':'PASS','word_shots':[19,20],'new_segment_only':True}
for group in ('segments','merges','previews'):
 for key,item in data[group].items():assert m.digest(D/item['path'])==item['sha256'],key
m.write_manifest(data)
r.update(encoded_frames_checked=12,all_frame_text_bounds='PASS',countdown_silence='PASS',visual_review='待实际编码节点人工复核',previous_master_unchanged=True)
(ROOT/'验证.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
credit='图七原图作者：Emanuel Guzman、Carmela Ramos、Ali Dastgheib，2020。Influence of the El Niño Phenomenon on Shoreline Evolution. Case Study: Callao Bay, Perú. Journal of Marine Science and Engineering 8(2),90. https://doi.org/10.3390/jmse8020090 。原作CC BY 4.0：https://creativecommons.org/licenses/by/4.0/ 。本视频对图7进行同范围裁切、等比缩放并添加中文日期及动态定性标注；未改变岸线或原图比例尺。公开馆藏PDF：https://app.ingemmet.gob.pe/biblioteca/pdf/Amb-257.pdf 。\n\n漫滩动画据Aalto等，Nature 425,493–497(2003)，https://doi.org/10.1038/nature02002 的过程结论自绘，不复制其图版。\n'
(p.parent/'素材署名与来源.txt').write_text(credit,encoding='utf-8')
inputs=[ROOT/'素材/Callao论文_INGEMMET馆藏.pdf',ROOT/'素材/论文页8_图0_Im13.png',ROOT/'素材/论文页8_图1_Im14.png']
(ROOT/'素材/素材校验.json').write_text(json.dumps([dict(path=str(f),sha256=m.digest(f),bytes=f.stat().st_size) for f in inputs],ensure_ascii=False,indent=2),encoding='utf-8')
note='\n\n2026-10-16 第八段地形与配对完成：demooo/独立片段/08_地形与配对/海洋发烧了_第八段_地形与配对.mp4，约50.11秒，1920×1080、24fps。按批注18以地表侵蚀/堆积替换旧正文候选碳汇镜头；秘鲁Callao湾论文原图7（2017年4月/2018年1月，同范围裁切保留尺度与坐标），河口圈选后才出现沿岸北向输沙箭头，保留1.7—1.8km长度及最远约7km邻近海滩信息，2017注明沿岸厄尔尼诺；Aalto等Nature2003部分亚马孙漫滩—拉尼娜洪水关联，用概念剖面表现漫滩退水堆积，不伪造地理底图。五要素配对覆盖水/气/生/土/地形，按本课重点，3秒无旁白倒计时变暗后逐条连线；不暗示互斥分类或固定因果顺序。两个标题各2秒展示归位，晓伊+5%，无角色故46号底部字幕，57号标题。只新增独立片段，不合并；原总片及其他小段哈希复核未变。累计时长相加约8分24秒，离10分钟上限约96秒，后续辨析/滞后22秒、石河子为主乡土28秒、处方25秒、检测17秒，含标题与停顿；按真实配音重新核算。来源/署名/时轴/检查在第八段_地形与配对。原图为CC BY4.0，交付视频旁保存素材署名与来源.txt。\n'
for f in [PROJECT/'AGENTS.md',PROJECT/'制作进度与接续.md']:
 with f.open('a',encoding='utf-8') as out:out.write(note)
print(json.dumps(r,ensure_ascii=False,indent=2))
