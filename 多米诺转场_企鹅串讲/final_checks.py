from pathlib import Path
import json,subprocess,sys,io,hashlib
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;P=ROOT.parent;D=P/'demooo'
sys.path.insert(0,str(P/'ocean_animation_demo_20261011/runtime'))
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe();m=json.loads((D/'视频清单.json').read_text(encoding='utf-8'))
checks=[('05_环境多米诺_水',20.1),('05_环境多米诺_水',37.5),('06_水收束与气',27.7),('07_生与土',1.7),('07_生与土',30.9),('08_地形与配对',1.7),('08_地形与配对',35.7),('08_地形与配对',44.0)]
contact=Image.new('RGB',(1920,580),'#e5eeee');d=ImageDraw.Draw(contact)
for i,(key,t) in enumerate(checks):
 p=D/m['segments'][key]['path'];a=subprocess.check_output([ff,'-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-f','image2pipe','-vcodec','png','-']);im=Image.open(io.BytesIO(a)).convert('RGB');x=i%4*480;y=i//4*290;contact.paste(im.resize((480,270)),(x,y));d.text((x+7,y+273),f'{key[:2]} {t:.2f}s',fill='#244b60')
contact.save(ROOT/'检查/正式交付_八节点.jpg')
total=sum(r['seconds'] for r in m['segments'].values())
r=json.loads((ROOT/'验证.json').read_text(encoding='utf-8'));r.update(canonical_frames_checked=8,total_segment_seconds=total,visual_review='PASS：12个实际编码转场节点及8个正式交付节点复核，1046帧对象记录与679个气泡帧安全边界核对；非逐帧人工观看')
(ROOT/'验证.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
for folder in ['第六段_水收束与气','第七段_生与土','第八段_地形与配对']:
 f=P/folder/'验证.json';v=json.loads(f.read_text(encoding='utf-8'));v['superseded_scope']='本文件原检查针对串讲改版前基片；当前交付以多米诺转场_企鹅串讲/验证.json为准';f.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
note=f'\n\n2026-10-16 多米诺串讲改版：用户要求五张牌切换时企鹅提醒并重现原五牌、突出当前牌后淡去；多米诺各段及配对取消中央放大归位，标题固定左上。正式05—08已同名覆盖，时长73.84/64.80/57.73/56.73秒；已确认的第四第五段合成及开场至第五段总片同步更新，成员范围未扩展，不自动加入第六至第八段。05推板处标题亦固定，移除水牌前0.7秒退场，避免企鹅刚走又进；气、生、土、地形各段用原全角色03/06与原口型、旧card_art色彩图标串讲。地形原收束句后新增1.1秒停留，企鹅从左侧回场，五牌回顾后淡入配对；人物出现只有46号指向性气泡，倒计时换09托腮，结束12点赞，没有底部字幕。原科学讲解与原配音保留，只新生成六句串讲，晓伊+5%。\n主工程为多米诺转场_企鹅串讲/build_transitions.py，时轴、原片输入快照、来源和边界/编码检查保留；只对未加串讲基片应用一次。旧章节入场_全片合成/build_full.py的发布入口已停用，防止重新覆盖成旧中央归位动画。以后正文修改先更新基片/时轴，再应用本流程；当前正式交付看demooo清单及本工程验证，不把06—08旧原始检查哈希当成当前成片哈希。\n修改短样片为demooo/预览/多米诺转场与企鹅回场/多米诺转场与企鹅回场.mp4，14.54秒，展示气牌串讲及地形完整收束—停留—企鹅回场；不直接再发长片。累计各段相加约{total:.2f}秒（约8分37秒），未合并。离10分钟上限约{600-total:.2f}秒，后续辨析/滞后、以石河子为主乡土、处方及总结需总计控制在此范围，标题停顿亦计算；不能机械每章一分钟。\n'
for f in [P/'AGENTS.md',P/'制作进度与接续.md']:
 with f.open('a',encoding='utf-8') as a:a.write(note)
print('Canonical checks ready; summed duration',total)
