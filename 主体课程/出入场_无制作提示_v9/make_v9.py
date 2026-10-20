from pathlib import Path
import runpy
ROOT=Path(__file__).resolve().parent
V8=ROOT.parent/'右侧左指_批注落实_v8'
src=(V8/'build_v8.py').read_text(encoding='utf-8')
src=src.replace("MAP=ROOT/'素材'/'NOAA_PSL_ENSO区域图.png'","V8=ROOT.parent/'右侧左指_批注落实_v8'\nMAP=V8/'素材'/'NOAA_PSL_ENSO区域图.png'")
src=src.replace("RIGHT=ROOT/'素材'/'19_右侧向左指_原图.png'","RIGHT=V8/'素材'/'19_右侧向左指_原图.png'")
a=src.index('IMAGES=[]');z=src.index('def mouth(t):',a)
src=src[:a]+"IMAGES=[str(V8/'素材'/f'案例{i+1}_未讲暗场.png') for i in range(3)]\n"+src[z:]
for line in [
 "        s.text('历史资料照片，非同年同一次事件证据 · 详细出处见素材说明',425,967,24,b.SOFT,'center',1440)\n",
 "        s.text('官方原图 · NOAA Physical Sciences Laboratory',42,117,26,b.SOFT,w=1350)\n",
 "        s.text('官方图保持比例；定位段围绕Niño3.4做局部推近',45,1010,23,b.SOFT,w=1400)\n",
]:
    assert line in src;src=src.replace(line,'')
src=src.replace('图一：秘鲁渔港（情境资料图）','图一：秘鲁渔港')
src=src.replace('473,626,fill=', '473,666,fill=').replace('449,500,fit=', '449,540,fit=').replace('837+k*42','877+k*42').replace('(291,815)','(291,855)')
src=src.replace('walkstart=mapstart-1.45;right=t>=mapstart','walkstart=mapstart-1.0;enterend=mapstart+.70;right=t>=mapstart\n    intransit=walkstart<=t<enterend')
old="""    elif walkstart<=t<mapstart:
        q=b.ease((t-walkstart)/1.45);presenter(s,13 if int((t-walkstart)/.17)%2==0 else 14,20+1560*q,775,300,t)
"""
new="""    elif walkstart<=t<mapstart:
        q=b.ease((t-walkstart)/1.0)
        presenter(s,13 if int((t-walkstart)/.17)%2==0 else 14,-500*q,600,410,t)
    elif mapstart<=t<enterend:
        q=b.ease((t-mapstart)/.70)
        presenter(s,13 if int((t-mapstart)/.17)%2==0 else 14,1920-(1920-1330)*q,600,410,t)
"""
assert old in src;src=src.replace(old,new)
src=src.replace("if t>=DATA[0]['start']:bubble(s,row['text'],right)","if t>=DATA[0]['start'] and not intransit:bubble(s,row['text'],right)")
src=src.replace('_右侧左指_v8.mp4','_出入场_v9.mp4')
src=src.replace("'walk':'along lower edge before map appears, includes audio-driven mouth overlays'","'walk':'exit left, enter from right; bubble hidden immediately when movement begins and reappears only after arrival'")
src=src.replace("'caption':'date/location line removed from screen, sources preserved separately; Peru is explicitly marked illustrative historical photo'","'caption':'simple figure labels only; production notes and evidence/source explanations kept in external documentation'")
src=src.replace("    for label,mode in [('图片强调','秘鲁'),('官方地图','定位'),('新动作','线索')]:", "    mapstart=next(r['start'] for r in DATA if r['mode']=='线索')\n    for offset in (-.45,.35,.9):\n        t=mapstart+offset;sc=scene(t)\n        if offset<.7:assert not any(a['kind']=='polygon' for a in sc.items), 'Bubble remained during movement'\n        else:assert any(a['kind']=='polygon' for a in sc.items), 'Bubble did not return after arrival'\n        render(t).save(ROOT/f'转场检查_{offset}.png')\n    for label,mode in [('图片强调','秘鲁'),('官方地图','定位'),('新动作','线索')]:")
src=src.replace('v8沿用v7的晓伊生动化台词音频，补短标题和转换。','v9复用已确认的晓伊配音。去除视频中的制作提示；讲解开始移动时隐藏气泡，从左边退出、从右边进入，站稳后恢复气泡。')
(ROOT/'build_v9.py').write_text(src,encoding='utf-8')
runpy.run_path(str(ROOT/'build_v9.py'),run_name='__main__')
