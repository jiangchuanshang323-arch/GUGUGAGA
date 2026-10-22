"""Prepare version labels and delivery files after visual review."""
from pathlib import Path
import json,os,subprocess,shutil
from build_full import P,R,C,B,OUT,BASE,FF,VERSION,digest,NEW_TOTAL,DELTA

def main():
    record=json.loads((C/'交付记录.json').read_text())
    assert digest(OUT)==record['output_sha256'] and record['complete_decode']=='PASS'
    record['visual_review']='实际编码23节点总览，以及入场、抽选转接、回到定位与字幕全尺寸抽查完成；非逐帧人工观看，未声称用户应用内实播。'
    record['subtitle_font_pixels']=46
    (C/'交付记录.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
    preview=P/'downloads/preview_route_V20261023_02.mp4'
    subprocess.run([FF,'-v','error','-y','-ss','49.5','-i',str(OUT),'-t','18','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-profile:v','baseline','-level:v','4.0','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(preview)],check=True)
    alias=P/'downloads/ocean_beautified_full.mp4';temp=alias.with_name('.latest_swap.mp4')
    if temp.exists():temp.unlink()
    os.link(OUT,temp);os.replace(temp,alias)
    delivery=P/'demooo/合成版本/四步会诊融入';delivery.mkdir(parents=True,exist_ok=True)
    human=delivery/'海洋发烧了_完整版_V20261023.02.mp4'
    if human.exists():human.unlink()
    os.link(OUT,human)
    shutil.copy2(C/'前后过渡与抽选衔接总览.jpg',delivery/'四步会诊_前后衔接预览_V20261023.02.jpg')
    (delivery/'当前版本.txt').write_text('当前版本：V20261023.02（8秒小样融入版）\n时长：11分51.958秒，1920×1080，24fps，17087帧。\n原教学台词与知识顺序保留；加入已确认小样及三处纸页衔接。\n前一版本V20261023.01已在downloads/archive归档。\n完整工程：四步会诊融入_20261023\n')
    latest={k:record[k] for k in ['version','output_sha256','bytes','seconds','frames','resolution','fps','source_version','source_sha256','duration_increase_seconds']}
    latest.update(status='current',label='8秒小样融入完整版',download='downloads/ocean_full_V20261023_02.mp4',preview='downloads/preview_route_V20261023_02.mp4',archive='downloads/archive/ocean_full_V20261023_01.mp4',project='四步会诊融入_20261023',sample_scope='本版使用用户已确认的8秒抽选小样，不是36秒连续四站动作。')
    (P/'downloads/CURRENT_VERSION.json').write_text(json.dumps(latest,ensure_ascii=False,indent=2)+'\n')
    text=f'''# 《海洋“发烧”了》\n\n## 当前版本：{VERSION} · 8秒小样融入完整版\n\n**11分51.958秒 · 1920×1080 · 24fps**\n\n- **[下载当前完整视频](downloads/ocean_full_V20261023_02.mp4)**\n- [先看18秒前后衔接预览](downloads/preview_route_V20261023_02.mp4)\n- [当前版本与文件校验信息](downloads/CURRENT_VERSION.json)\n- [本次完整工程与说明](四步会诊融入_20261023/README.md)\n\n使用Edge或Chrome登录有仓库访问权限的GitHub账号，进入视频文件页面后，点击右上角 **Download raw file（下载原始文件）**。选择保存到桌面，或从下载文件夹移动到桌面。\n\n### 本次更新\n\n保留已确认的8秒“原翅膀与帽子贴合”动作画面，在入场、原小样抽选点、回到Niño3.4定位处加入纸页转场；字幕沿用原讲解。原教学内容、顺序、其余美化画面、中国影响与处方保留。为动作增加2.458秒静音停顿，没有新配音、没有加速原台词。\n\n### 版本记录\n\n| 版本 | 状态 | 完整视频 | 时长 |\n|---|---|---|---|\n| **{VERSION}** | **当前推荐** | [8秒小样融入版](downloads/ocean_full_V20261023_02.mp4) | 11:51.958 |\n| V20261023.01 | 已归档 | [原整体美化版](downloads/archive/ocean_full_V20261023_01.mp4) | 11:49.500 |\n\n原通用地址 `downloads/ocean_beautified_full.mp4` 也已更新为当前版本。文件名带明确版本号的链接用于固定版本下载。\n'''
    (P/'README.md').write_text(text)
    (P/'downloads/README.md').write_text(text.replace('(downloads/','(').replace('(四步会诊融入_20261023/','(../四步会诊融入_20261023/'))
    (P/'CURRENT_VERSION.md').write_text(f'# 当前视频版本：{VERSION}\n\n**8秒小样融入完整版**，11分51.958秒，1080p / 24fps。\n\n[下载当前完整版](downloads/ocean_full_V20261023_02.mp4) · [18秒衔接预览](downloads/preview_route_V20261023_02.mp4)\n\n本版替代V20261023.01作为推荐观看版，上一版本保留在downloads/archive。\n\nSHA256：`{record["output_sha256"]}`\n')
    manifest=P/'demooo/视频清单.json';data=json.loads(manifest.read_text())
    rel=str(human.relative_to(P/'demooo'))
    entry={**latest,'path':rel,'engine':'四步会诊融入_20261023/build_full.py','video_outside_interval_stream_copied':True,'audio_note':'原PCM片段不变速，插入静音后重编码AAC，不能称整轨AAC字节一致。'}
    data.setdefault('presentation_deliveries',{})['四步会诊融入']=entry;data['latest_viewing_delivery']=rel;data['current_version']=VERSION
    if '整体美化' in data['presentation_deliveries']:
        data['presentation_deliveries']['整体美化'].update(version='V20261023.01',status='archived',download='downloads/archive/ocean_full_V20261023_01.mp4')
    manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    note=f'''\n\n2026-10-23 发布{VERSION}（8秒小样融入完整版）：用户本轮要求将GitHub新上传的四步会诊动作及设计融入全片、完成前后过渡并推送。已读取66a7569的v3源码与说明，确认8秒小样为行走段＋第四站动作抽选，原始192帧全部使用。远端缺rig_reference_v1.py，已异步请求补充；本版按用户明确提供的8秒素材制作，不冒充36秒连续四站动画。\n当前主下载downloads/ocean_full_V20261023_02.mp4；中文交付{rel}；通用旧下载地址已指向此版；旧V01归档downloads/archive/ocean_full_V20261023_01.mp4。根README.md、CURRENT_VERSION.md和downloads/CURRENT_VERSION.json明确当前版本。新片711.958333秒、17087帧、1920×1080/24fps，SHA256 {record['output_sha256']}。\n以43eb4f11的整体美化片为母片；原53—61秒的192帧替换为251帧，增加59帧（2.458333秒）。原概念镜头用0.75秒纸页入场，小样3.5秒抽选处用0.5秒无空白纸页切换，最后0.75秒回到原Niño3.4定位；字幕46号得意黑。前后视频包直接复制；原配音不变速、不新合成，在原59.791667秒静音处加入2.458333秒停顿，PCM前后片段逐样相同，最后AAC重新编码，不能沿用旧“整AAC包一致”说法。其余内容、旧美化、中国水彩、处方和检测均保留，仅全片时码从插入点后顺延。\n工程四步会诊融入_20261023/build_full.py，发布准备prepare_release.py；完整解码、24fps连续PTS、23实际编码节点及转场/字幕全尺寸抽查完成，不是逐帧人工观看或用户应用内实播。18秒预览downloads/preview_route_V20261023_02.mp4。用户本轮已明确授权上传GitHub，待本次发布命令确认后以远端main提交为准。\n'''
    for name in ['AGENTS.md','制作进度与接续.md']:
        with (P/name).open('a') as f:f.write(note)
    # Only superseded inspection copies created in this task are removed.
    stale=C/'过渡关键全尺寸'
    if stale.exists():shutil.rmtree(stale)
    print(json.dumps(latest,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
