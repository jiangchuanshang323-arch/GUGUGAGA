from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import json
root=Path(__file__).resolve().parents[1]
path=next((root/'00_原始资料').glob('*最新批注版*.docx'))
with ZipFile(path) as z:
    tree=etree.fromstring(z.read('word/document.xml'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
active=False
for node in tree.find('w:body',ns):
    text=''.join(node.xpath('.//w:t/text()',namespaces=ns))
    if '镜头 11' in text:active=True
    if '镜头 14' in text:active=False
    if active:print(text)
comments=json.loads((root/'主体课程'/'权威地图_生动台词_v7'/'.build'/'最新批注提取.json').read_text(encoding='utf-8'))
for c in comments:
    if any(x in str(c) for x in ('镜头 11','镜头 12','镜头 13','镜头 10')):print(json.dumps(c,ensure_ascii=False))
