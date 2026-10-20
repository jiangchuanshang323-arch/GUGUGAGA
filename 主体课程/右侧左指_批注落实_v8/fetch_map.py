from pathlib import Path
import urllib.request,json
from PIL import Image
ROOT=Path(__file__).resolve().parent
url='https://psl.noaa.gov/enso/img/oceanic-indices-map.gif'
req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
with urllib.request.urlopen(req,timeout=40) as r:data=r.read()
p=ROOT/'素材'/'NOAA_PSL_ENSO区域图_原始.gif';p.write_bytes(data)
im=Image.open(p);im.convert('RGB').save(ROOT/'素材'/'NOAA_PSL_ENSO区域图.png')
print(im.size)
(ROOT/'地图来源.json').write_text(json.dumps({'institution':'NOAA Physical Sciences Laboratory','page':'https://psl.noaa.gov/data/timeseries/month/Nino34_CPC/','image':url,'original_dimensions':im.size,'transform':'GIF converted losslessly to PNG; original retained; resizing and zooming only'},ensure_ascii=False,indent=2),encoding='utf-8')
