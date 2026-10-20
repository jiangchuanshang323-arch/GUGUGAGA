from pathlib import Path
import urllib.request,json,zipfile,io,hashlib
ROOT=Path(__file__).resolve().parent
def get(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'DigitalLesson-FontDownload'}),timeout=60).read()
info=json.loads(get('https://api.github.com/repos/atelier-anchor/smiley-sans/releases/latest'))
print([(a['name'],a['size']) for a in info['assets']],flush=True)
asset=next(a for a in info['assets'] if a['name'].lower().endswith('.zip'))
data=get(asset['browser_download_url']);z=zipfile.ZipFile(io.BytesIO(data))
font=next(n for n in z.namelist() if n.endswith('SmileySans-Oblique.ttf'))
fontdata=z.read(font);(ROOT/'素材'/'SmileySans-Oblique.ttf').write_bytes(fontdata)
license_data=get('https://raw.githubusercontent.com/atelier-anchor/smiley-sans/main/LICENSE')
(ROOT/'素材'/'得意黑_LICENSE.txt').write_bytes(license_data)
(ROOT/'素材'/'字体来源.json').write_text(json.dumps({'project':'https://github.com/atelier-anchor/smiley-sans','release':info['tag_name'],'asset':asset['browser_download_url'],'font_sha256':hashlib.sha256(fontdata).hexdigest()},ensure_ascii=False,indent=2),encoding='utf-8')
print('Font saved',len(fontdata),flush=True)
