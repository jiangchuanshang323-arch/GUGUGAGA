from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
old=P/'视频交付';new=P/'demooo'
assert old.is_dir() and not new.exists()
assert old.resolve().is_relative_to(P.resolve()) and new.resolve().is_relative_to(P.resolve())
m=json.loads((old/'视频清单.json').read_text(encoding='utf-8'))
mapping={};checks=[]
titles=['开场','第一段_三地情境','第二段_测体征','第三段_查病因','第四段_对照与预测','第五段_环境多米诺_水','第六段_水收束与气']
for group in ['segments','merges','previews']:
 for i,(key,item) in enumerate(m.get(group,{}).items()):
  src=old/item['path'];assert src.is_file() and src.resolve().is_relative_to(old.resolve())
  name='海洋发烧了_'+(titles[i] if group=='segments' else key)+'.mp4'
  dst=src.with_name(name);assert not dst.exists()
  h=hashlib.sha256(src.read_bytes()).hexdigest();assert h==item['sha256']
  before=item['path'];src.rename(dst);item['path']=str(dst.relative_to(old));mapping[before]=item['path'];checks.append((item['path'],h))
m.pop('filename',None)
m['folder_name']='demooo'
m['policy']='分段、合成版本、预览均以内容本名命名；每项保持一个固定交付路径，修改时覆盖。demooo仅为总文件夹名称。'
(old/'视频清单.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
old.rename(new)
for rel,h in checks:assert hashlib.sha256((new/rel).read_bytes()).hexdigest()==h
# Correct active code references, including split Path(...) expressions.
for f in P.rglob('*.py'):
 if any(x in f.parts for x in ['runtime','.runtime','.build','__pycache__']):continue
 if f.name==Path(__file__).name:continue
 s=f.read_text(encoding='utf-8-sig');before=s
 s=s.replace('视频交付','demooo')
 for a,b in mapping.items():
  s=s.replace(a.replace('\\','/'),b.replace('\\','/'))
  s=s.replace(a,b)
  parts=Path(a).parts;replacement=Path(b).name
  if len(parts)>=2:s=s.replace("'"+parts[-2]+"'/'demooooo.mp4'","'"+parts[-2]+"'/'"+replacement+"'")
 if f.name=='manage_videos.py':
  start=s.index('def initialize():');end=s.index('\ndef update(',start)
  s=s[:start]+"def initialize():\n raise RuntimeError('交付清单已存在；请按内容本名使用 update / update_many。')\n"+s[end:]
 s=s.replace("dest.with_name('.demooooo.pending.mp4')","dest.with_name('.'+dest.stem+'.pending.mp4')")
 s=s.replace("dest.with_name('.demooooo.replacement.mp4')","dest.with_name('.'+dest.stem+'.replacement.mp4')")
 s=s.replace("target.with_name('.demooooo.replacement.mp4')","target.with_name('.'+target.stem+'.replacement.mp4')")
 # Preview builders store their destination separately from OUTDIR.
 if 'OUTDIR' in s:
  for k,v in m.get('previews',{}).items():
   if "'预览'/'"+k+"'" in s:s=s.replace("OUTDIR/'demooooo.mp4'","OUTDIR/'"+Path(v['path']).name+"'")
 if s!=before:f.write_text(s,encoding='utf-8')
(new/'使用说明.md').write_text('# 视频交付\n\n总文件夹为 demooo。独立片段、合成版本和预览按内容本名命名，不再以 demo 命名视频。每段修改覆盖对应固定文件；合成仅在明确要求后进行。当前完整成片包含开场至第五段，第六段独立保存。\n',encoding='utf-8')
(new/'命名迁移校验.json').write_text(json.dumps(dict(files=[dict(path=p,sha256=h) for p,h in checks],hash_check='PASS',mapping=mapping),ensure_ascii=False,indent=2),encoding='utf-8')
print('Renamed and hash verified',len(checks),'videos',new)
