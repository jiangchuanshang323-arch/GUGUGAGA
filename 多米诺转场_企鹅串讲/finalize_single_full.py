from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent;P=ROOT.parent;D=P/'demooo'
mf=D/'视频清单.json';data=json.loads(mf.read_text(encoding='utf-8'));key='环境多米诺_水气生土地形';entry=data['merges'][key];video=D/entry['path']
assert video.is_file() and hashlib.sha256(video.read_bytes()).hexdigest()==entry['sha256']
report=json.loads((ROOT/'单牌整段_验证.json').read_text(encoding='utf-8'));report.update(visual_review='PASS：五种单牌15个实际编码节点及整段12节点复核；逐帧对象记录确认最多一张牌、无强制人物和气泡公共基线；非逐帧人工观看',actual_encoded_nodes=27)
(ROOT/'单牌整段_验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for k in ('单张多米诺牌','单张多米诺牌_气'):
 data['previews'][k]['description']='单牌局部样片；气泡公共基线与前镜角色规则已应用于正式独立小段及环境多米诺完整段'
# Retire the superseded five-card preview only; retain original engineering inputs.
old=data.get('previews',{}).pop('多米诺转场与企鹅回场',None)
if old:
 f=D/old['path'];assert f.resolve().is_relative_to(D.resolve())
 if f.exists():
  h=hashlib.sha256(f.read_bytes()).hexdigest();assert h==old['sha256'];f.unlink()
  data.setdefault('retired_previews',[]).append(dict(path=old['path'],sha256=h,reason='五牌总览转场已被用户否定，改为当前单张牌'))
  if not any(f.parent.iterdir()):f.parent.rmdir()
data['visual_review']='单牌正式改版：详见多米诺转场_企鹅串讲/单牌整段_验证.json。旧版标题与五牌总览预览不作为当前交付。'
mf.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
credits='''环境多米诺完整段：素材来源与署名

NOAA：厄尔尼诺冬季典型全球影响图，原始机构图像裁切；海岸线、投影及色区保留。原项目素材及来源清单：环境多米诺_水_v37/素材/来源.json。
中国气象局：《2024年中国气候公报》图2.11。https://www.cma.gov.cn/zfxxgk/gknr/qxbg/202503/W020250302606211127018.pdf 。原图与夏季雨带局部展示。
阿塔卡马开花照片：ESO，图像poposo-flor_9742。https://www.eso.org/public/images/poposo-flor_9742/ 。仅作开花现象，不作为某次厄尔尼诺归因证明；图像裁切。ESO使用条款：https://www.eso.org/public/outreach/copyright/ 。
温度数据：Met Office HadCRUT.5.1.0.0，1980—2024年全球年平均温度距平，1961—1990参照期及原数据95%不确定性范围。https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.5.1.0.0/download.html 。使用原始数据绘图，按机构Open Government Licence说明。
珊瑚照片：NOAA Fisheries，Jarvis Island bleached coral。https://www.fisheries.noaa.gov/feature-story/coral-recovery-after-bleaching-event-central-pacific 。照片裁切；未拼作同地前后对照。
印尼2015烟霾影像：NASA Earth Observatory。https://science.nasa.gov/earth/earth-observatory/el-nino-brought-drought-and-fire-to-indonesia-87204/ 。原项目保存7200×4800图像borneo_2015267_lrg.jpg，裁切用于讲解。
'''
credits+=(D/'独立片段/08_地形与配对/素材署名与来源.txt').read_text(encoding='utf-8')
(video.parent/'素材来源与署名.txt').write_text(credits,encoding='utf-8')
total=sum(v['seconds'] for v in data['segments'].values())
note=f'\n\n2026-10-16 单张多米诺正式整段完成：用户明确要求整段，已将单牌/基线/前镜人物规则应用05—08，并合成demooo/合成版本/环境多米诺_水气生土地形/海洋发烧了_环境多米诺完整段.mp4，{entry["seconds"]:.2f}秒（约3分26秒），1920×1080、24fps。整段只从第一张水牌开始，至地形后的企鹅配对反馈结束，不含前面的预测和推板；清单trim_start_seconds记录第一段前缀裁切，manage_videos.merge及update/update_many均保留该裁切，后续修改会同步重建且不改变范围。\n正式独立05—08本名覆盖，旧第四第五段及开场至第五段合成同步更新、成员不扩展。原始首句配音复用，不再另加重复串讲；在首句科学讲解开始后0.75秒淡去卡牌，左上标题一直固定。水前企鹅已在场则保留，气/生/土/地形前无人就只出牌居中，角色完全消失后才恢复底部字幕；气泡公共ls基线，不能再按逐字bbox顶部对齐。地形收束1.1秒停顿后企鹅回场，直接配对板，不再重复五牌总览。原始科学内容/原图/其余配音保留，无新语音请求。\n当前正式入口为多米诺转场_企鹅串讲/apply_single_cards.py；单牌正式_制作清单.json保存替换时轴，原片_*.mp4仅为未加新转场工程基片。旧五牌build_transitions.py和repair_and_publish.py的直接发布入口已停用。五个单牌15节点及整段12节点、解码与逐帧对象/气泡记录复核通过；原先旧五牌14.54秒预览已按哈希校验退休删除，仅保留两支仍适用的水/气单牌样片，原工程不删。素材署名另附整段旁。累计全课程小段约{total:.2f}秒，未把00—08另拼成全课程；现有目前完整成片仍按已确认开场至第五段范围。\n'
for f in [P/'AGENTS.md',P/'制作进度与接续.md']:
 with f.open('a',encoding='utf-8') as out:out.write(note)
print('FINAL',str(video),entry['seconds'],'all-segment-seconds',total)
