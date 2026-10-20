from pathlib import Path
import urllib.request, urllib.parse, re, html, hashlib, json
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent
UA={'User-Agent':'EducationalLessonAsset/1.0 (personal educational preview)'}
def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=90).read()
def commons(name,out):
    page='https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(name)
    filename=name.replace(' ','_');digest=hashlib.md5(filename.encode()).hexdigest()
    url=f'https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/'+urllib.parse.quote(filename)
    data=fetch(html.unescape(url)); (ROOT/'素材'/out).write_bytes(data)
    return {'file':out,'page':page,'url':url,'sha256':hashlib.sha256(data).hexdigest()}
def nasa():
    page='https://science.nasa.gov/earth/earth-observatory/smoke-blankets-indonesia-86681/'
    doc=fetch(page).decode()
    urls=re.findall(r'https://assets.science.nasa.gov/[^\s"<>]+',doc)
    urls=[html.unescape(u) for u in urls if '.jpg' in u.lower()]
    url=next((u.split('?')[0] for u in urls if '_lrg' in u or '_large' in u),urls[0])
    data=fetch(url); (ROOT/'素材'/'印尼烟霾_NASA_20150924.jpg').write_bytes(data)
    return {'file':'印尼烟霾_NASA_20150924.jpg','page':page,'url':url,'sha256':hashlib.sha256(data).hexdigest()}
def font():
    url='https://raw.githubusercontent.com/lxgw/LxgwWenKai/main/fonts/TTF/LXGWWenKai-Regular.ttf'
    data=fetch(url);(ROOT/'素材'/'LXGWWenKai-Regular.ttf').write_bytes(data)
    return {'file':'LXGWWenKai-Regular.ttf','url':url,'sha256':hashlib.sha256(data).hexdigest()}
with ThreadPoolExecutor(max_workers=4) as ex:
    fs=[ex.submit(commons,'Puerto de Paracas, Perú, 2019-10-17.jpg','秘鲁渔港_20191017.jpg'),ex.submit(commons,'Flooded Datong Town, Tongling (2020).jpg','铜陵大通洪水_20200714.jpg'),ex.submit(nasa),ex.submit(font)]
    results=[]
    for f in fs:
        try:results.append(f.result());print(results[-1],flush=True)
        except Exception as e:print(type(e).__name__,str(e),flush=True)
    (ROOT/'素材'/'下载清单.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
