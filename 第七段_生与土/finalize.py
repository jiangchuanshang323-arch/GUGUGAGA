from pathlib import Path
import sys,json,hashlib,subprocess,importlib.util,io,math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent;D=PROJECT/'demooo'
s=importlib.util.spec_from_file_location('delivery',D/'manage_videos.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
report=json.loads((ROOT/'验证.json').read_text(encoding='utf-8'));p=Path(report['output']);m.decode(p)
meta=json.loads((ROOT/'台词与时间轴.json').read_text(encoding='utf-8'))
times=[.6,1.7,4.5,10,16,22,27,meta['intros'][1]['start']+.6,35,41,46,52]
contact=Image.new('RGB',(1920,870),'#e5eeee');draw=ImageDraw.Draw(contact)
for i,t in enumerate(times):
 b=subprocess.check_output([m.EXE,'-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-f','image2pipe','-vcodec','png','-'])
 im=Image.open(io.BytesIO(b)).convert('RGB');assert im.size==(1920,1080)
 im.save(ROOT/'检查'/f'实际编码_{t:.2f}.png');x=i%4*480;y=i//4*290
 contact.paste(im.resize((480,270)),(x,y));draw.text((x+8,y+273),f'{t:.2f}s',fill='#244b60')
contact.save(ROOT/'检查/实际编码_十二节点.jpg')
audit=json.loads((ROOT/'检查/逐帧文字边界.json').read_text(encoding='utf-8'));assert len(audit)==math.ceil(meta['duration']*24)
manifest=json.loads(m.MANIFEST.read_text(encoding='utf-8'))
manifest['segments']['07_生与土']={'path':str(p.relative_to(D)),**m.info(p),'decode':'PASS','word_shots':[17,18],'new_segment_only':True}
for group in ['segments','merges','previews']:
 for key,item in manifest[group].items():
  f=D/item['path'];assert f.is_file() and m.digest(f)==item['sha256'],key
m.write_manifest(manifest)
report.update(encoded_frames_verified=12,all_frame_text_bounds='PASS',actual_fps='24',visual_review='待实际编码节点人工复核',previous_master_unchanged=True)
(ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
photos=[ROOT/'素材/NOAA_Jarvis珊瑚白化.jpg',PROJECT/'环境多米诺_水_v37/素材/NASA_2015印尼烟霾.jpg']
(ROOT/'素材/素材校验.json').write_text(json.dumps([dict(path=str(f),size=Image.open(f).size,sha256=m.digest(f)) for f in photos],ensure_ascii=False,indent=2),encoding='utf-8')
note='\n\n2026-10-16 用户更正命名：demooo是交付总文件夹名，不是视频文件名。已将原视频交付目录迁移为demooo，13项旧视频全部按内容本名重命名，SHA256一致，清单/管理器/活跃工程引用同步更新；历史记录原路径仅为历史。今后使用demooo/独立片段、demooo/合成版本、demooo/预览，每项固定语义文件名，修改覆盖。新增第七段生与土，54.75秒，镜17—18及批注16—17；上升流/营养盐/鱼群连续动效，NOAA贾维斯岛白化照片，NASA2015印尼烟霾照片与土壤泥炭剖面，结尾降雨—径流—侵蚀衔接地形。沿用晓伊+5%、57号章节与46号底部字幕，两章各2秒无旁白中央标题入场，不加人物。独立新文件为demooo/独立片段/07_生与土/海洋发烧了_第七段_生与土.mp4，不自动拼总片。开场至第七段时长相加约7分34秒，现有总片仍5分36秒含开场至第五段。目标9分55秒剩余约141秒，预算见本工程制作依据；不可按每章一分钟扩张。\n'
for f in [PROJECT/'AGENTS.md',PROJECT/'制作进度与接续.md']:
 with f.open('a',encoding='utf-8') as out:out.write(note)
print(json.dumps(report,ensure_ascii=False,indent=2))
