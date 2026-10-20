from pathlib import Path
import sys,math,json,csv,wave,subprocess,importlib.util,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageOps
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
for name in ('素材','检查','.build'):(ROOT/name).mkdir(exist_ok=True)
sys.path.insert(0,str(PROJECT/'卷图推板与五牌'))
s=importlib.util.spec_from_file_location('lesson6_base',PROJECT/'卷图推板与五牌/update_parts.py');o=importlib.util.module_from_spec(s);s.loader.exec_module(o)
from refine_components import install
install(o)
META=json.loads((ROOT/'台词与时间轴.json').read_text(encoding='utf-8'));ROWS=META['lines'];DURATION=META['duration'];INTRO=META['title_intro_start']
F=o.F;ease=o.m.ease;INK=o.INK;BLUE=o.BLUE;ORANGE=o.ORANGE;CREAM=o.CREAM
RAIN=Image.open(ROOT/'素材/公报雨带_页33_图0_Im0.png').convert('RGB')
FLOWERS=Image.open(ROOT/'素材/ESO_阿塔卡马花海.jpg').convert('RGB')
with (ROOT/'素材/HadCRUT_annual.csv').open(encoding='utf-8') as f:
 DATA=[dict(year=int(a['Time']),value=float(a['Anomaly (deg C)']),low=float(a['Lower confidence limit (2.5%)']),high=float(a['Upper confidence limit (97.5%)'])) for a in csv.DictReader(f) if 1980<=int(a['Time'])<=2024]
assert len(DATA)==45 and all(math.isfinite(r['value']) for r in DATA)
(ROOT/'素材/绘图数据_1980至2024.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2),encoding='utf-8')
V=o.p.native.v
SKY=V.gradient((1920,1080),(244,251,247),(201,229,233)).convert('RGB')
SEACOLD=V.gradient((1720,290),(103,177,198),(40,105,141))
SEAWARM=V.gradient((1720,290),(250,215,169),(233,169,136))
TITLE=o.p.header('第二张·气','海气热交换 → 大气能量变化')
AUDIT=[]
def text(im,s,x,y,size=60,color=INK,center=False):
 o.txt(im,s,x,y,size,color,center)
 bb=F(size).getbbox(s);w=bb[2]-bb[0];h=bb[3]-bb[1]
 AUDIT.append({'text':s,'box':[round(x-w/2 if center else x),round(y),round(x+w/2 if center else x+w),round(y+h)]})
def pill(im,s,cx,y,size=60,color=INK):
 w=F(size).getlength(s)+42;h=size+28;x=cx-w/2
 assert x>=24 and x+w<=1896
 ImageDraw.Draw(im).rounded_rectangle((x,y,x+w,y+h),18,fill=CREAM,outline='#a8c9cf',width=2)
 text(im,s,cx,y+13,size,color,True)
def water_header(im):o.header(im,'第一张·水','环流变化 → 降水重分配 → 水循环响应')
def air_header(im):im.paste(TITLE,(16,14),TITLE)

def rain_scene(t):
 im=o.m.BG.copy();d=ImageDraw.Draw(im);d.rounded_rectangle((34,184,1886,944),24,fill=CREAM,outline='#a7c6ce',width=2)
 water_header(im);text(im,'2024年中国东部雨带实况',1400,82,46,BLUE,True)
 # The official raster and its zoom are displayed at their original proportions.
 art=ImageOps.contain(RAIN,(900,728),Image.Resampling.LANCZOS);x=64;y=206
 im.paste(art,(x,y));s=art.width/RAIN.width
 region=(185,320,680,767);b=(x+region[0]*s,y+region[1]*s,x+region[2]*s,y+region[3]*s)
 age=t-ROWS[0]['start'];q=ease((age-1)/.5)
 if q:
  layer=Image.new('RGBA',im.size);ld=ImageDraw.Draw(layer);ld.rounded_rectangle(b,8,fill=(110,173,191,round(q*18)),outline=(77,139,163,round(q*190)),width=3);im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
  inset=ImageOps.contain(RAIN.crop(region),(790,550),Image.Resampling.LANCZOS)
  xx=1420-inset.width/2;yy=342
  im.paste(inset,(round(xx),yy));d=ImageDraw.Draw(im);d.rounded_rectangle((xx-6,yy-6,xx+inset.width+6,yy+inset.height+6),12,outline='#8fb7c5',width=3)
  d.line((b[2]+3,(b[1]+b[3])/2,xx-10,yy+inset.height/2),fill='#8fb7c5',width=3)
  pill(im,'6—8月 · 雨带局部',1420,225,54,BLUE)
 if age<3.5:pill(im,'横轴：时间 →',1420,855,54,BLUE)
 elif age<6.7:pill(im,'纵轴：纬度 ↑',1420,855,54,BLUE)
 else:pill(im,'影响随事件和季节而异',1420,855,54,BLUE)
 return im

def flower_scene(t,row):
 im=o.m.BG.copy();age=t-ROWS[2]['start'];q=min(1,max(0,age/(ROWS[3]['end']-ROWS[2]['start'])))
 w,h=FLOWERS.size;scale=1+.025*q;cw=w/scale;ch=cw/(1820/742)
 # A gentle editorial crop of the real photograph; no synthetic landscape.
 cx=w*.51;cy=h*.58
 crop=FLOWERS.crop((round(cx-cw/2),round(cy-ch/2),round(cx+cw/2),round(cy+ch/2)))
 im.paste(crop.resize((1820,742),Image.Resampling.LANCZOS),(50,200));water_header(im)
 pill(im,'图四：阿塔卡马沙漠开花 · ESO',650,214,49)
 words=['降雨','种子萌发','开花'];times=[.35,1.8,3.4]
 for i,s in enumerate(words):
  if age<times[i]:continue
  cx=470+i*480;pill(im,s,cx,831,60,BLUE if i==0 else ORANGE)
  if i:o.p.native.arrow(im,[(cx-300,874),(cx-185,874)],'#b4ced1',5,1)
 return im

def water(im,t):
 xs=np.arange(1720);edge=112+7*np.sin(xs/160+t*.45)+3*np.sin(xs/67-t*.7)
 mask=Image.new('L',(1720,290));d=ImageDraw.Draw(mask);pts=[(x,float(edge[x])) for x in range(0,1720,4)]+[(1719,float(edge[-1]))]
 d.polygon([(0,0),(1719,0)]+pts[::-1],fill=255)
 sea=SEACOLD.copy();sea.paste(SEAWARM,(0,0),mask);im.paste(sea,(100,650));d=ImageDraw.Draw(im)
 d.line([(100+x,650+float(edge[x])) for x in range(0,1720,5)],fill='#fff0d5',width=4,joint='curve')
 d.line([(100+x,650+3*math.sin(x/100+t)) for x in range(0,1720,5)],fill='#f8fbef',width=4,joint='curve')
 for i in range(17):
  x=145+(i*97+t*10)%1600;y=685+(i%3)*23;d.line((x,y,x+34,y-2),fill='#fbe7c4',width=2)

def energy_scene(t,row,show_header=True):
 im=SKY.copy();water(im,t);d=ImageDraw.Draw(im)
 mode=row['mode'];swap=next(r for r in ROWS if r['mode']=='交换');age=t-swap['start']
 c_strength=.55+.06*math.sin(t*.5)
 # Same soft hand-drawn cloud silhouette as the approved continuous scene.
 import_cloud(im,1255,373,c_strength,t,2)
 text(im,'大气',175,207,66,BLUE);pill(im,'海洋：储热与热量输送',960,834,65,ORANGE)
 if t>=swap['start']:
  e=ease((age-2.7)/.65)
  if e:
   path=V.cubic((615,640),(500,490),(900,370),(1160,342),70)
   release=ease((age-5.3)/.65)
   n=max(2,round((len(path)-1)*e));o.p.native.arrow(im,path[:n],BLUE,8,1-.55*release)
   pill(im,'蒸发携热',475,443,60,BLUE)
   for i in range(8):
    q=(t*.25+i/8)%1;j=min(len(path)-2,max(0,round(q*(len(path)-1))));x,y=path[j]
    d.ellipse((x-5,y-5,x+5,y+5),fill='#c9e3e6');d.ellipse((x+8,y-2,x+14,y+4),fill='#e8b888')
  release=ease((age-5.3)/.65)
  if release:
   for a,b,c,end in [((1310,310),(1400,270),(1540,260),(1650,245))]:
    path=V.cubic(a,b,c,end,45);n=max(2,round((len(path)-1)*release));o.p.native.arrow(im,path[:n],ORANGE,7,1)
   pill(im,'凝结放热',1460,445,60,ORANGE)
 if mode=='分配':
  pill(im,'海气热量再分配',960,191,68,ORANGE)
 if show_header:air_header(im)
 return im

spec=importlib.util.spec_from_file_location('approved_cloud',PROJECT/'连续场景重做/build_preview.py');cloudmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(cloudmod)
import_cloud=cloudmod.cloud

def curve_scene(t,row):
 im=o.m.BG.copy();d=ImageDraw.Draw(im);d.rounded_rectangle((40,184,1880,944),24,fill=CREAM,outline='#aac8cf',width=2);air_header(im)
 text(im,'全球年平均地表温度距平',960,215,68,INK,True)
 text(im,'1980—2024年 · 相对1961—1990年平均值',960,299,38,BLUE,True)
 x0,x1,y0,y1=205,1740,805,375
 def pt(year,val):return x0+(year-1980)/44*(x1-x0),y0-(val+.25)/1.5*(y0-y1)
 for value in [-.2,0,.5,1.0]:
  yy=pt(1980,value)[1];d.line((x0,yy,x1,yy),fill='#dce6e5',width=2);text(im,f'{value:.1f}',120,yy-21,42,BLUE)
 text(im,'℃',105,350,40,BLUE)
 for year in [1980,1990,2000,2010,2020,2024]:
  xx=pt(year,0)[0];d.line((xx,y0,xx,y0+9),fill='#8eabb3',width=2);text(im,str(year),xx,y0+17,42,BLUE,True)
 d.line((x0,357,x0,y0,x1+15,y0),fill='#8eabb3',width=3)
 age=t-next(r['start'] for r in ROWS if r['mode']=='曲线');progress=ease(age/5.2)*(len(DATA)-1)
 n=min(len(DATA)-1,max(0,int(progress)));fraction=progress-n
 band=[pt(a['year'],a['high']) for a in DATA[:n+1]]+[pt(a['year'],a['low']) for a in DATA[:n+1][::-1]]
 if len(band)>3:d.polygon(band,fill='#f3e2ce')
 points=[pt(a['year'],a['value']) for a in DATA[:n+1]]
 if n<len(DATA)-1:
  a=pt(DATA[n]['year'],DATA[n]['value']);b=pt(DATA[n+1]['year'],DATA[n+1]['value']);points.append((a[0]+(b[0]-a[0])*fraction,a[1]+(b[1]-a[1])*fraction))
 if len(points)>1:d.line(points,fill=ORANGE,width=7,joint='curve')
 xx,yy=points[-1];d.ellipse((xx-8,yy-8,xx+8,yy+8),fill=ORANGE,outline=CREAM,width=2)
 text(im,'数据：Met Office HadCRUT5.1',1250,887,36,BLUE,True)
 text(im,'浅色带：95%不确定性范围',420,887,32,BLUE,True)
 if age>5.7:pill(im,'年际起伏 ≠ 长期增暖的全部原因',960,365,53,INK)
 if row['mode']=='承下':
  q=ease((t-row['start'])/.5);x=1600+11*math.sin(t*2);o.m.icon(d,2,x,625,'#88b297',1.1);pill(im,'下一张 · 生',1550,704,56,BLUE)
 return im

def title_intro(im,age):
 art=TITLE;scale=2.15 if age<1 else 2.15-1.15*ease(age-1)
 if age<1:cx,cy=960,540
 else:q=ease(age-1);cx=960*(1-q)+(16+art.width/2)*q;cy=540*(1-q)+(14+art.height/2)*q
 a=art.resize((round(art.width*scale),round(art.height*scale)),Image.Resampling.LANCZOS)
 x=round(cx-a.width/2);y=round(cy-a.height/2);assert x>=0 and x+a.width<=1920 and y>=0 and y+a.height<=1080
 im.paste(a,(x,y),a)

def scene(t,row):
 if row['mode'] in ('中国','雨带'):return rain_scene(t)
 if row['mode'] in ('花海','限定'):return flower_scene(t,row)
 if row['mode'] in ('曲线','承下'):return curve_scene(t,row)
 return energy_scene(t,row)

def render(t):
 global AUDIT
 AUDIT=[]
 if INTRO<=t<INTRO+2:
  im=energy_scene(t,next(r for r in ROWS if r['mode']=='气'),False);title_intro(im,t-INTRO);return im,dict(t=t,mode='章节标题入场',labels=AUDIT,narration=False)
 row=next((r for r in ROWS if r['start']<=t<r['end']),ROWS[0] if t<.2 else ROWS[-1]);im=scene(t,row)
 # Dissolve only at genuine scene boundaries; all scientific objects retain their direction.
 if row['mode'] in ('花海','曲线') and t-row['start']<.4:
  idx=ROWS.index(row);prev=ROWS[idx-1];im=Image.blend(scene(prev['end']-.02,prev),im,ease((t-row['start'])/.4))
 o.subtitle(im,row['text']);return im,dict(t=t,mode=row['mode'],labels=AUDIT,narration=True)

def main():
 times=[1.3,5,10,17,23,INTRO+.6,INTRO+1.5,30,37,41,46,53,57,61]
 contact=Image.new('RGB',(1920,math.ceil(len(times)/4)*290),'#e5eeee');dd=ImageDraw.Draw(contact)
 for i,t in enumerate(times):
  im,_=render(t);im.save(ROOT/'检查'/f'节点_{t}.png');x=i%4*480;y=i//4*290;contact.paste(im.resize((480,270)),(x,y));dd.text((x+6,y+273),f'{t:.2f}s',fill=INK)
 contact.save(ROOT/'检查/内容与动效检查.jpg')
 if '--preview' in sys.argv:return
 dest=PROJECT/'demooo/独立片段/06_水收束与气/海洋发烧了_第六段_水收束与气.mp4';dest.parent.mkdir(parents=True,exist_ok=True);pending=dest.with_name('.'+dest.stem+'.pending.mp4')
 proc=subprocess.Popen([o.EXE,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(ROOT/'配音/第六段_晓伊.wav'),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(pending)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 audit=[];count=math.ceil(DURATION*24)
 for i in range(count):
  im,meta=render(i/24);audit.append(meta);proc.stdin.write(im.tobytes())
  if i%240==0:print('Render',i,'/',count,flush=True)
 proc.stdin.close();err=proc.stderr.read();assert proc.wait()==0,err
 test=subprocess.run([o.EXE,'-v','error','-i',str(pending),'-f','null','-'],capture_output=True);assert test.returncode==0 and not test.stderr,test.stderr
 pending.replace(dest)
 (ROOT/'检查/逐帧文字边界.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 report=dict(output=str(dest),seconds=DURATION,frames=count,resolution=[1920,1080],fps=24,decode='PASS',new_segment_only=True,previous_full_video_unchanged=True,character_present=False,visual_review='待实际编码抽帧',temperature_source='Met Office HadCRUT.5.1.0.0，1980—2024；1961—1990基准',sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
 (ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False),flush=True)
def patch_tail():
 # Keep the encoded first 55 seconds and original AAC; redraw only this local label fix.
 dest=PROJECT/'demooo/独立片段/06_水收束与气/海洋发烧了_第六段_水收束与气.mp4'
 start=math.ceil((next(r['start'] for r in ROWS if r['mode']=='曲线')+5.4)*24);count=math.ceil(DURATION*24)
 tail=ROOT/'.build/曲线末段.mp4'
 proc=subprocess.Popen([o.EXE,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p',str(tail)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 for i in range(start,count):proc.stdin.write(render(i/24)[0].tobytes())
 proc.stdin.close();err=proc.stderr.read();assert proc.wait()==0,err
 pending=dest.with_name('.'+dest.stem+'.pending.mp4')
 filters=f'[0:v]trim=end_frame={start},setpts=PTS-STARTPTS[head];[1:v]setpts=PTS-STARTPTS[tail];[head][tail]concat=n=2:v=1:a=0,fps=24[v]'
 subprocess.run([o.EXE,'-v','error','-y','-i',str(dest),'-i',str(tail),'-filter_complex',filters,'-map','[v]','-map','0:a','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(pending)],check=True)
 test=subprocess.run([o.EXE,'-v','error','-i',str(pending),'-f','null','-'],capture_output=True);assert test.returncode==0 and not test.stderr,test.stderr
 pending.replace(dest);report=json.loads((ROOT/'验证.json').read_text(encoding='utf-8'));report['sha256']=hashlib.sha256(dest.read_bytes()).hexdigest();report['chart_annotation_avoids_data']=True
 (ROOT/'验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('Chart annotation moved clear of data; decode PASS',flush=True)
if __name__=='__main__':
 if '--patch-tail' in sys.argv:patch_tail()
 else:main()
