from pathlib import Path
import subprocess,io,json,hashlib,re
from PIL import Image,ImageDraw
p=Path(r'D:\Arthur\数字微课');q=p/'路线角色表演_20261022/检查/原翅膀与帽子贴合';r=json.loads((q/'交付验证.json').read_text(encoding='utf-8'));v=Path(r['path']);ff=p/'ocean_animation_demo_20261011/runtime/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe';ts=[.35,1.15,2.0,3.0,3.8,4.35,4.9,5.6,6.25,6.9,7.4,7.9];sheet=Image.new('RGB',(1600,1350))
for i,t in enumerate(ts):
 raw=subprocess.run([str(ff),'-v','error','-ss',str(t),'-i',str(v),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True,check=True).stdout;im=Image.open(io.BytesIO(raw)).convert('RGB');source=6.75+t if t<3.5 else 31.5+t-3.5
 import sys;sys.path.insert(0,str(p/'路线角色表演_20261022'));import build_route_v3 as b
 x,y,*_=b.travel(source);tile=im.crop((round(x-200),round(y-430),round(x+200),round(y+20)));ImageDraw.Draw(tile).text((5,5),f'{t:.2f}s',fill='white',stroke_fill='#153e50',stroke_width=2);sheet.paste(tile,((i%4)*400,(i//4)*450))
sheet.save(q/'编码后手部与帽子检查.jpg');info=subprocess.run([str(ff),'-hide_banner','-i',str(v),'-map','0:v:0','-c','copy','-f','null','-'],capture_output=True,check=True).stderr.decode('utf-8','replace');assert '00:00:08.00' in info and int(re.findall(r'frame=\s*(\d+)',info)[-1])==192
route=p/'demooo/预览/四步会诊路线全程/四步会诊路线_全程动作展示.mp4';r['existing_36s_route_unchanged']=hashlib.file_digest(route.open('rb'),'sha256').hexdigest()=='922e53b614845675c059ceead497185358d79b5ed3927ad7c5e901bb0551e08d';assert r['existing_36s_route_unchanged'];r['sha256']=hashlib.file_digest(v.open('rb'),'sha256').hexdigest();r['encoded_visual_samples']=12;(q/'交付验证.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(r,ensure_ascii=True))
