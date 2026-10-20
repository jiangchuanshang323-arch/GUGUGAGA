from pathlib import Path
import urllib.request,hashlib,json
from PIL import Image
root=Path(__file__).resolve().parent/'异常环流_对照预测_v24'
for x in ('素材','配音','.build','交付'):(root/x).mkdir(parents=True,exist_ok=True)
url='https://content-drupal.climate.gov/sites/default/files/2021-10/ENSO_blog_Bjerknes-feedback-ElNino_large.jpg'
p=root/'素材'/'NOAA_厄尔尼诺_1860原图.jpg'
if not p.exists():
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40) as r:p.write_bytes(r.read())
print(Image.open(p).size)
(root/'素材'/'来源.json').write_text(json.dumps({'publisher':'NOAA Climate.gov','media':'https://content-drupal.climate.gov/media/13534','image':url,'size':Image.open(p).size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'science':'https://content-drupal.climate.gov/news-features/blogs/enso/rise-el-ni%C3%B1o-and-la-ni%C3%B1a','AI_redraw':False},ensure_ascii=False,indent=2),encoding='utf-8')
