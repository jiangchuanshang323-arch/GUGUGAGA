"""Review-only edit montage. Does not replace the existing 45-second deliverable."""
from pathlib import Path
import json,subprocess,wave,hashlib,io
import numpy as np
from PIL import Image,ImageDraw
import build_video as v
from refine_scene import install

install(v)
R=v.R;Q=R/'检查/本轮地图改版';Q.mkdir(parents=True,exist_ok=True)
OUT=v.OUT.parent/'中国影响_地图与情境动作修改示例.mp4'
WINDOWS=[(6,8.75),(14.35,17.35),(26.5,29),(32,34),(36.25,38.5)]
TIMES=[a+i/24 for a,b in WINDOWS for i in range(round((b-a)*24))]
old_hash=hashlib.sha256(v.OUT.read_bytes()).hexdigest()
audio=np.concatenate([v.PCM[round(a*24000):round(b*24000)] for a,b in WINDOWS])
with wave.open(str(Q/'示例配音.wav'),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(audio.astype('<i2').tobytes())
log=(Q/'编码日志.txt').open('wb')
tmp=OUT.with_name('.地图修改示例.pending.mp4')
proc=subprocess.Popen([v.b.FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-i',str(Q/'示例配音.wav'),'-t',str(len(TIMES)/24),'-c:v','libx264','-profile:v','baseline','-level:v','4.0','-g','24','-bf','0','-refs','1','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-ac','2','-b:a','128k','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE,stderr=log)
audit=[]
for i,t in enumerate(TIMES):
 im=v.frame(t);proc.stdin.write(im.convert('RGB').tobytes())
 assert not any(o['kind'] in ['character','bubble'] for o in v.AUDIT)
 audit.append(dict(frame=i,source_time=t,objects=v.AUDIT))
 if i%72==0:print('frames',i,'/',len(TIMES),flush=True)
proc.stdin.close();assert proc.wait()==0;log.close()
v.b.manager.decode(tmp);info=v.b.manager.info(tmp)
assert abs(info['seconds']-len(TIMES)/24)<.03,info
storms=[o for r in audit for o in r['objects'] if o['kind']=='typhoon']
assert all(b['center'][0]<=a['center'][0]+1e-8 and b['center'][1]<=a['center'][1]+1e-8 for a,b in zip(storms,storms[1:]))
assert max(o['map_scale'] for o in storms)==2
assert all(o['box'][0]>1600 for r in audit for o in r['objects'] if o['kind']=='south_china_sea_inset')
assert {o['pose'] for r in audit for o in r['objects'] if o['kind']=='weather_character'}=={'rain','fan','cold'}
assert hashlib.sha256(v.OUT.read_bytes()).hexdigest()==old_hash
tmp.replace(OUT)
sheet=Image.new('RGB',(1920,620),'#e7eef0')
for j,t in enumerate([.8,2.5,4.5,6.5,8.0,10.0,11.0,12.2]):
 raw=subprocess.run([v.b.FF,'-v','error','-ss',str(t),'-i',str(OUT),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True,check=True).stdout
 im=Image.open(io.BytesIO(raw));im.save(Q/f'实际编码_{t:.1f}.png')
 x=j%4*480;y=j//4*310;sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),(x,y))
 ImageDraw.Draw(sheet).text((x+10,y+272),f'{t:.1f}s',font=v.F(23),fill=v.INK)
sheet.save(Q/'实际编码总览.jpg')
(Q/'逐帧对象.json').write_text(json.dumps(audit,ensure_ascii=False),encoding='utf-8')
s=v.REFINED;assert s.in_mainland(*s.shore_clip['render_end']);assert not s.in_mainland(*s.shore_clip['removed_next_point'])
assert all(s.in_mainland(*p) for coords,_ in s.yangtze for p in coords if p[0]>121)
main=[s.point(lon,lat) for poly in v.G for lon,lat in poly[0] if lat>=18]
box=[min(p[0] for p in main),min(p[1] for p in main),max(p[0] for p in main),max(p[1] for p in main)]
(Q/'验证.json').write_text(json.dumps(dict(**info,resolution='1920x1080',fps=24,frames=len(TIMES),decode='PASS',northwest_track='PASS',max_map_scale=2,map_projection='equirectangular, standard parallel 35N',main_country_bounds=box,shore_clip=s.shore_clip,no_offshore_yangtze_tail='PASS',right_period_font_sizes=[60],weather_poses=['rain','fan','cold'],penguin_screen_scale_unchanged=.52,subtitles_only=True,province_source='https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json',rivers_source=['https://www.openstreetmap.org/relation/9392345','https://github.com/nvkelso/natural-earth-vector'],river_line_count=len(s.rivers),source_windows=WINDOWS,original45_unchanged_sha256=old_hash),ensure_ascii=False,indent=2),encoding='utf-8')
(R/'素材/长江显示河道_海岸收束.geojson').write_text(json.dumps({'type':'FeatureCollection','source':'https://www.openstreetmap.org/relation/9392345','rendering':'clipped at displayed mainland coastline; offshore extension omitted','features':[{'type':'Feature','properties':{'name':'长江'},'geometry':{'type':'LineString','coordinates':c}} for c,_ in s.yangtze]},ensure_ascii=False),encoding='utf-8')
print('DELIVERED',OUT,info,flush=True)
