from pathlib import Path
import urllib.request
from pypdf import PdfReader
import pypdfium2 as pdfium
ROOT=Path(__file__).resolve().parent
url='https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/lanina/enso_evolution-status-fcsts-web.pdf'
p=ROOT/'素材'/'NOAA_CPC_ENSO官方周报.pdf'
if not p.exists():
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=45) as r:p.write_bytes(r.read())
d=PdfReader(p);render=pdfium.PdfDocument(str(p))
for i,page in enumerate(d.pages):
    text=page.extract_text()
    if ('Niño Regions' in text or 'Nino regions' in text or 'Map of' in text):
        print(i,text[:550].replace('\n',' / '),[(x.image.size) for x in page.images])
        render[i].render(scale=2).to_pil().save(ROOT/'素材'/f'官方周报_第{i+1}页.png')
        for j,img in enumerate(page.images):img.image.save(ROOT/'素材'/f'周报原图_{i+1}_{j}.png')
