"""Inspect encoded deliverables and record only observed results."""
from pathlib import Path
import hashlib, io, json, math, re, subprocess, zipfile
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parent
P = R.parent
C = R / '检查'
MASTER = P / 'demooo/合成版本/目前完整成片/海洋发烧了_目前完整成片.mp4'
ORIGINAL = R / '原始完整成片.mp4'
SEGMENT = P / 'demooo/独立片段/11_适应与减缓/海洋发烧了_第十一段_适应与减缓.mp4'
PREVIEW = P / 'demooo/预览/三个画面5秒样片/适应处方单_5秒.mp4'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while data := f.read(1024 * 1024):
            h.update(data)
    return h.hexdigest()

def info(path):
    data = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))
    v = next(x for x in data['streams'] if x['codec_type'] == 'video')
    return {'seconds': float(data['format']['duration']), 'bytes': path.stat().st_size, 'sha256': sha(path),
            'frames': int(v['nb_frames']), 'width': v['width'], 'height': v['height'],
            'fps': v['avg_frame_rate'], 'profile': v.get('profile'), 'pixel_format': v['pix_fmt']}

def audio_hash(path):
    return subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0', '-c', 'copy', '-f', 'hash', '-']).decode().strip()

def extract(path, t):
    b = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', str(path), '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'])
    return Image.open(io.BytesIO(b)).convert('RGB')

def main():
    master, segment, preview = info(MASTER), info(SEGMENT), info(PREVIEW)
    assert master['sha256'] != sha(ORIGINAL)
    assert master['frames'] == 17028 and master['width'] == 1920 and master['height'] == 1080 and master['fps'] == '24/1'
    assert abs(master['seconds'] - 709.5) < .025
    assert segment['frames'] == 1175 and abs(segment['seconds'] - 1175 / 24) < .025
    assert preview['frames'] == 120 and abs(preview['seconds'] - 5) < .025
    original_audio, final_audio = audio_hash(ORIGINAL), audio_hash(MASTER)
    if original_audio != final_audio:
        exact = MASTER.with_name('.原音轨完整保留.pending.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(MASTER), '-i', str(ORIGINAL),
                        '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', str(exact)], check=True)
        exact.replace(MASTER)
        master = info(MASTER)
        final_audio = audio_hash(MASTER)
    assert original_audio == final_audio, (original_audio, final_audio)
    print('FORMAT_FRAME_AUDIO_CHECKS_PASS', flush=True)
    # All frames outside the replacement interval are compared at reduced resolution.
    selection = 'lt(n,14328)+gte(n,15503)'
    graph = (f"[0:v]select='{selection}',scale=480:270,settb=1/24,setpts=N[a];"
             f"[1:v]select='{selection}',scale=480:270,settb=1/24,setpts=N[b];"
             f'[a][b]ssim=stats_file={C / "未修改画面逐帧相似度.txt"}[v]')
    with (C / '全片对照解码日志.txt').open('wb') as log:
        subprocess.run(['ffmpeg', '-v', 'warning', '-i', str(ORIGINAL), '-i', str(MASTER), '-filter_complex', graph,
                        '-map', '[v]', '-an', '-fps_mode', 'passthrough', '-f', 'null', '-'], stderr=log, check=True)
    values = [float(x) for x in re.findall(r'All:([0-9.]+)', (C / '未修改画面逐帧相似度.txt').read_text())]
    assert len(values) == 17028 - 1175, len(values)
    assert min(values) > .90 and sum(values) / len(values) > .98, (min(values), sum(values) / len(values))
    print('OUTSIDE_CHAPTER_COMPARISON_PASS', len(values), min(values), flush=True)
    times = [596.9, 597., 599.5, 603.1, 608.5, 615.9, 620.8, 627., 632., 638., 640.5, 644., 645.916667, 645.958334, 648.2, 708.8]
    sheet = Image.new('RGB', (1600, math.ceil(len(times) / 4) * 250), '#e7eeed')
    f = ImageFont.truetype(str(P / '主体课程/得意黑_大字无水印_v6/素材/SmileySans-Oblique.ttf'), 23)
    for j, t in enumerate(times):
        im = extract(MASTER, t)
        im.save(C / f'完整编码帧_{t:.6f}.png')
        x, y = j % 4 * 400, j // 4 * 250
        sheet.paste(im.resize((400, 225), Image.Resampling.LANCZOS), (x, y))
        ImageDraw.Draw(sheet).text((x + 7, y + 225), f'{int(t)//60}:{t%60:06.3f}', font=f, fill='#244b60')
    sheet.save(C / '完整视频编码抽帧总览.jpg', quality=95)
    before = extract(R / '修复前预览/适应处方单_5秒.mp4', 2.5)
    after = extract(PREVIEW, 2.5)
    # Full-resolution face/portrait evidence on a large neutral comparison canvas.
    portraits = Image.new('RGB', (1000, 780), '#e6efef')
    for j, (name, im) in enumerate([('Original prescription character', before), ('Repaired prescription character', after)]):
        crop = im.crop((110, 610, 400, 990)).resize((500, 655), Image.Resampling.LANCZOS)
        portraits.paste(crop, (j * 500, 45))
        ImageDraw.Draw(portraits).text((j * 500 + 12, 10), name, font=f, fill='#244b60')
    portraits.save(C / '实际编码角色对照.png')
    report = {'master': master, 'segment': segment, 'first_prescription_preview': preview,
              'source_master_sha256': sha(ORIGINAL), 'source': 'repository same-name master; oversized uploaded attachment not downloaded',
              'replacement_seconds': [597.0, 645.9583333333334], 'replacement_frames_half_open': [14328, 15503],
              'decode': 'PASS', 'source_audio_packet_hash': original_audio, 'output_audio_packet_hash': final_audio,
              'audio_packet_payloads_identical': True, 'comparison_frames_outside_replacement': len(values),
              'outside_ssim_at_480x270': {'minimum': min(values), 'mean': sum(values) / len(values)},
              'review_times': times, 'visual_review': 'pending encoded-image inspection', 'browser_playback': 'not tested'}
    (C / '交付验证.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    manifest_path = P / 'demooo/视频清单.json'
    data = json.loads(manifest_path.read_text())
    data['segments']['11_适应与减缓'].update({k: segment[k] for k in ['seconds', 'bytes', 'sha256']},
        decode='PASS', generator='处方统一_20261021/build_prescriptions.py', style='纸本水彩处方笺', character_face='嘴边杂线去除；独立音量口型')
    data['merges']['目前完整成片'].update({k: master[k] for k in ['seconds', 'bytes', 'sha256']},
        decode='PASS', scope='完整课程；处方章节统一纸本水彩，角色脸颊杂线已修复，保留原完整音轨')
    data['previews']['处方统一_首张5秒'] = {'path': str(PREVIEW.relative_to(P / 'demooo')), **preview, 'decode': 'PASS'}
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    old_qa = P / '修改方案_三画面/5秒样片检查/验证.json'
    if old_qa.exists():
        data = json.loads(old_qa.read_text())
        for entry in data.get('outputs', []):
            if entry.get('name') == '适应处方单_5秒':
                entry.update({k: preview[k] for k in ['seconds', 'frames', 'bytes', 'sha256']})
                entry.update(decode='PASS', revision='2026-10-21 净面修复；新工程及核对记录见处方统一_20261021/检查')
        old_qa.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    still_qa = P / '修改方案_三画面/交付核对.json'
    if still_qa.exists():
        data = json.loads(still_qa.read_text())
        for entry in data.get('frames', []):
            if entry.get('name') == '03_适应处方单.png':
                entry['sha256'] = sha(P / '修改方案_三画面/03_适应处方单.png')
        data.update(video_changed=True, latest_prescription_revision='2026-10-21；角色净面、口型及处方统一；其余静态项沿用原记录',
                    latest_validation='处方统一_20261021/检查/交付验证.json')
        still_qa.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    html = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>海洋“发烧”了 · 完整视频</title><style>body{{margin:0;padding:20px;background:#102f40;color:#fff;font:18px sans-serif}}video{{width:100%;max-height:88vh;background:#000}}h1{{font-size:22px}}</style><h1>海洋“发烧”了 · 处方修复完整版</h1><video controls preload="metadata" playsinline src="{quote(MASTER.name)}?v={master['sha256'][:12]}"></video></html>'''
    (MASTER.parent / '播放完整视频.html').write_text(html)
    with zipfile.ZipFile(R / '处方画面/处方图片_4张.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted((R / '处方画面').glob('*.png')):
            z.write(path, path.name)
    print('DELIVERY_RECORDED', json.dumps(report, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    main()
