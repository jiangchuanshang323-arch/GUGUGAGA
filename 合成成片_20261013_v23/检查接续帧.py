from pathlib import Path
import sys,json,subprocess
from PIL import Image
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'主体课程'/'上抛后恢复普通姿势_v23'))
import build_v23 as m
report=json.loads((ROOT/'合成验证.json').read_text(encoding='utf-8'))
movie=Path(report['segments'][-1]['file']);boundary=report['segments'][0]['seconds']
frames=[boundary-.5,boundary+.5,boundary+m.v.BRIDGE_START+1.45,boundary+m.v.BRIDGE_END+20]
sheet=Image.new('RGB',(1280,720))
for i,t in enumerate(frames):
    frame=ROOT/f'接续检查_{i+1}.png'
    subprocess.run([m.v.EXE,'-y','-v','error','-ss',str(t),'-i',str(movie),'-frames:v','1',str(frame)],check=True)
    sheet.paste(Image.open(frame).resize((640,360)),((i%2)*640,(i//2)*360))
sheet.save(ROOT/'接续与最新转场检查.jpg')
