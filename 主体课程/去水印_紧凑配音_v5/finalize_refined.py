from pathlib import Path
import sys,ast,subprocess,json
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'ocean_animation_demo_20261011'/'runtime'))
import imageio_ffmpeg
exe=imageio_ffmpeg.get_ffmpeg_exe()
tree=ast.parse((ROOT/'build_v5.py').read_text(encoding='utf-8'))
graph=next(n.value.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='graph' for t in n.targets))
final=ROOT/'交付'/'海洋发烧了_去小云雀水印_紧凑配音_v5.1.mp4'
with open(ROOT/'.build'/'final_join.log','w') as log:
    subprocess.run([exe,'-y','-i',str(ROOT/'.build'/'开场_字形修补.mp4'),'-i',str(ROOT/'.build'/'紧凑正文.mp4'),'-filter_complex',graph,'-map','[v]','-map','[a]','-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)],stdout=log,stderr=log,check=True)
check=subprocess.run([exe,'-v','error','-i',str(final),'-f','null','-'],capture_output=True);assert check.returncode==0,check.stderr
meta=subprocess.run([exe,'-hide_banner','-i',str(final)],capture_output=True,text=True,encoding='utf-8',errors='replace')
print('\n'.join(line for line in meta.stderr.splitlines() if 'Duration:' in line or 'Stream #' in line),flush=True)
report={'output':str(final),'decode':'PASS','voice':'晓伊，复用原配音，仅剪辑停顿','question_added_pause_seconds':.22,'normal_added_pause_seconds':.14,'original_text_preserved':True,'watermark':'小云雀字形局部修补；保留AI生成标识','bytes':final.stat().st_size}
(ROOT/'最终验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('FINAL PASS',flush=True)
