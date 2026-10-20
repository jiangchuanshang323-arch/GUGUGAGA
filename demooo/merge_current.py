from pathlib import Path
import json,math,io,subprocess
from PIL import Image,ImageDraw
import manage_videos as m

def main():
 data=json.loads(m.MANIFEST.read_text(encoding='utf-8'))
 keys=sorted(data['segments']);assert [int(k.split('_')[0]) for k in keys]==list(range(13)),keys
 paths=[m.ROOT/data['segments'][k]['path'] for k in keys]
 for k,p in zip(keys,paths):assert m.digest(p)==data['segments'][k]['sha256'],k
 entry=data['merges']['目前完整成片'];dest=m.ROOT/entry['path']
 print('Merging',keys,'total',sum(data['segments'][k]['seconds'] for k in keys),flush=True)
 from replace_china_full import compose
 pending,dest,detail=compose(data);pending.replace(dest)
 info=m.info(dest);entry.update(info);entry.update(segments=keys,scope='完整课程：新版45秒中国影响取代旧第十段及石河子案例；其余现有章节保留',opening_count=1,decode='PASS',word_duration_limit_seconds=600,meets_duration_limit=info['seconds']<=600)
 m.write_manifest(data)
 check=dest.parent/'检查';check.mkdir(exist_ok=True)
 times=[1.0];elapsed=0
 for k in keys:
  seconds=data['segments'][k]['seconds'];times.extend([elapsed+min(3.,seconds/2),elapsed+seconds-.3]);elapsed+=seconds
 sheet=Image.new('RGB',(1600,math.ceil(len(times)/4)*250),'#dfe9eb');records=[]
 for j,t in enumerate(times):
  raw=subprocess.run([m.EXE,'-v','error','-ss',str(t),'-i',str(dest),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True,check=True).stdout
  im=Image.open(io.BytesIO(raw)).convert('RGB');assert im.size==(1920,1080)
  sheet.paste(im.resize((400,225),Image.Resampling.LANCZOS),((j%4)*400,(j//4)*250));ImageDraw.Draw(sheet).text(((j%4)*400+5,(j//4)*250+229),f'{t:.2f}s',fill='#254f61')
  records.append(dict(seconds=t,resolution=list(im.size)))
 sheet.save(check/'全阶段编码抽帧.jpg')
 detail.update(independent_hashes_unchanged=True,review_nodes=records)
 (check/'合成验证.json').write_text(json.dumps(detail,ensure_ascii=False,indent=2),encoding='utf-8')
 (dest.parent/'内容范围.txt').write_text('完整课程预览：开场至第十二段《总结与检测》，共13个独立视频。\n新版45秒中国影响已替代原第十段中国影响简述及石河子案例，前段旧石河子引入句已删除；适应与减缓和结尾独立假设题保留。\n独立片段保留，后续修改按清单同名覆盖。\n原创题目、参考答案和评分标准见独立片段/12_总结与检测/03_评价附件_结尾情境题.docx。\n',encoding='utf-8')
 print(str(dest),info,flush=True)

if __name__=='__main__':main()
