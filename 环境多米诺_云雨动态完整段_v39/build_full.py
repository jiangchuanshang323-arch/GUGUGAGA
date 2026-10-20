from pathlib import Path
import importlib.util,shutil,json,hashlib

ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
for folder in ('交付','检查','配音','.build'):(ROOT/folder).mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('approved38',PROJECT/'太平洋云雨动效_v38'/'build_demo.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
m=v.m
SOURCE=PROJECT/'环境多米诺_水_v37'
for rel in ['配音/环境多米诺_水_晓伊.wav','台词与时间轴.json']:
 shutil.copy2(SOURCE/rel,ROOT/rel)
m.ROOT=ROOT
m.load_audio=lambda:None # The exact original PCM and timeline were loaded by the approved demo.

def main():
 m.main()
 old=ROOT/'交付'/'海洋发烧了_第五段_环境多米诺水_v37.mp4'
 target=ROOT/'交付'/'海洋发烧了_第五段_云雨动态版_v39.mp4'
 assert old.resolve().is_relative_to(ROOT.resolve()) and target.resolve().is_relative_to(ROOT.resolve())
 old.replace(target)
 report=json.loads((ROOT/'验证.json').read_text(encoding='utf-8'))
 report.update(output=str(target),approved_animation='v38太平洋云雨动效',audio='完整复用v37晓伊与时间轴，无新语音请求',original_v37_unchanged=True,visual_review='待最终抽帧复核',sha256=hashlib.sha256(target.read_bytes()).hexdigest())
 (ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
