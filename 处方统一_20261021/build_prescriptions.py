"""Unify the prescription chapter and replace its exact frame interval in the master.

Original narration and the master AAC stream are retained. Artwork repairs are
image_gen outputs; type, highlights, countdown and mouth shapes are animation layers.
"""
from pathlib import Path
from functools import lru_cache
from array import array
import argparse, hashlib, io, json, math, shutil, subprocess, wave
from PIL import Image, ImageDraw, ImageFont, ImageOps

R = Path(__file__).resolve().parent
P = R.parent
ASSETS = R / '素材'
CHECK = R / '检查'
PLATES = R / '处方画面'
CHECK.mkdir(exist_ok=True)
PLATES.mkdir(exist_ok=True)
MASTER = P / 'demooo/合成版本/目前完整成片/海洋发烧了_目前完整成片.mp4'
ORIGINAL = R / '原始完整成片.mp4'
SEGMENT = P / 'demooo/独立片段/11_适应与减缓/海洋发烧了_第十一段_适应与减缓.mp4'
SOURCE = P / '第十一段_适应与减缓'
META = json.loads((SOURCE / '台词与时间轴.json').read_text())
ROWS = META['lines']
FPS, FRAMES, START, END, TOTAL = 24, 1175, 14328, 15503, 17028
INK, BLUE, OCHRE = '#193f53', '#317f83', '#ad6d48'
CREAM = '#fffaf0'
AUDIT = []

@lru_cache(None)
def font(n, hand=False):
    name = '主体课程/正文日系2D_配音_v2/素材/LXGWWenKai-Regular.ttf' if hand else '主体课程/得意黑_大字无水印_v6/素材/SmileySans-Oblique.ttf'
    return ImageFont.truetype(str(P / name), n)

def text(im, s, x, y, n=36, color=INK, center=False, hand=False):
    f = font(n, hand)
    w = f.getlength(s)
    if center:
        x -= w / 2
    baseline = y + n
    bb = ImageDraw.Draw(im).textbbox((x, baseline), s, font=f, anchor='ls')
    assert 18 <= bb[0] and bb[2] <= 1902 and 10 <= bb[1] and bb[3] <= 1068, (s, bb)
    ImageDraw.Draw(im).text((x, baseline), s, font=f, anchor='ls', fill=color)
    AUDIT.append({'text': s, 'box': list(bb), 'size': n})

def row(mode):
    return next(x for x in ROWS if x['mode'] == mode)

def ease(t):
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)

def base(kind, title, info, footer_type):
    file = P / '修改方案_三画面/处方笺_插画原图.png' if kind == 'adapt' else ASSETS / '同款空白处方纸.png'
    im = Image.open(file).convert('RGB').resize((1920, 1080), Image.Resampling.LANCZOS)
    text(im, '开处方', 70, 82, 68, hand=True)
    text(im, '海 洋 会 诊 室', 1253, 76, 33, '#fff8e7', True)
    text(im, title, 1250, 139, 59, center=True)
    for s, x, y in [('姓名：海洋', 662, 212), ('类型：' + footer_type, 1030, 212),
                    ('目标：' + info[0], 1418, 212), ('关注：' + info[1], 662, 263),
                    ('依据：' + info[2], 1030, 263), ('应对：' + info[3], 1420, 263)]:
        text(im, s, x, y, 29)
    for s, x in [('签名：咕咕嘎嘎', 650), ('会诊主题：海洋升温', 1090), ('分类：' + footer_type, 1575)]:
        text(im, s, x, 922, 29)
    return im

def list_item(im, title, sub, y):
    ImageDraw.Draw(im).rectangle((665, y + 12, 683, y + 30), outline=INK, width=2)
    text(im, title, 701, y - 8, 36)
    text(im, sub, 702, y + 37, 30, '#3e626b')

def adaptation():
    im = base('adapt', '海洋会诊 · 适应处方笺', ['减少暴露与损失', '当地天气风险', '监测与预警', '因地因时'], '适应')
    text(im, 'R：主要诉求', 661, 365, 52)
    text(im, '减少天气灾害带来的损失', 667, 438, 40)
    text(im, '建议执行', 666, 517, 40)
    for j, (title, sub) in enumerate([('早发现｜关注官方监测', '先了解气候背景。'),
                                    ('早预警｜核对本地预警', '看清地区与有效时间。'),
                                    ('早行动｜按指引做好准备', '调整出行和用水安排。')]):
        list_item(im, title, sub, 594 + j * 88)
    text(im, '医嘱：减少损失，不是消灭厄尔尼诺。', 665, 856, 33)
    ImageDraw.Draw(im).ellipse((1610, 360, 1802, 422), outline='#ba7353', width=3)
    text(im, '适应', 1706, 362, 38, '#a9674c', True)
    return im

def monitor():
    im = base('blank', '海洋会诊 · 监测预警单', ['争取准备时间', '地区与有效期', '官方信息', '按指引行动'], '适应')
    text(im, 'R：先监测，再查本地预警', 661, 365, 47)
    text(im, '监测提供气候背景', 667, 438, 40)
    for j, (title, sub) in enumerate([('看机构｜选择官方渠道', '关注权威气候监测。'),
                                    ('看地区｜核对影响范围', '查清本地预警的地区。'),
                                    ('看时间｜确认当前有效', '按有效预警做好准备。')]):
        list_item(im, title, sub, 556 + j * 94)
    art = Image.open(SOURCE / '素材/NOAA_CPC官方页面原始截图.png').convert('RGB').crop((0, 0, 1600, 355))
    art = art.resize((530, 118), Image.Resampling.LANCZOS)
    im.paste(art, (1310, 452))
    ImageDraw.Draw(im).rectangle((1305, 447, 1844, 574), outline='#c5a46e', width=2)
    text(im, 'NOAA CPC 官方通报', 1575, 595, 31, center=True)
    text(im, '通报：2026-10-08', 1575, 642, 28, center=True)
    text(im, '截取：2026-10-16', 1575, 684, 28, center=True)
    text(im, '本地风险，看本地预警。', 1575, 767, 33, OCHRE, True)
    text(im, '医嘱：留意地区、有效时间和行动指引。', 665, 856, 33)
    return im

def photo(im, name, y, label, location):
    art = ImageOps.fit(Image.open(SOURCE / ('素材/' + name)).convert('RGB'), (490, 195), Image.Resampling.LANCZOS)
    im.paste(art, (1335, y))
    ImageDraw.Draw(im).rectangle((1330, y - 5, 1830, y + 200), outline='#bfa16c', width=2)
    text(im, label, 1580, y + 202, 29, BLUE, True)
    text(im, location, 1580, y + 239, 24, center=True)

def mitigation():
    im = base('blank', '海洋会诊 · 减缓处方笺', ['限制长期增暖', '温室气体排放', '节能与清洁能源', '从身边做起'], '减缓')
    text(im, 'R：主要诉求', 661, 365, 52)
    text(im, '减少温室气体排放', 667, 438, 40)
    text(im, '建议执行', 666, 517, 40)
    for j, (title, sub) in enumerate([('节约能源｜减少浪费', '关掉不用的灯，节约用电。'),
                                    ('清洁能源｜风电光伏', '减少对高排放能源的依赖。'),
                                    ('长期目标｜限制增暖', '降低长期风险背景。')]):
        list_item(im, title, sub, 594 + j * 88)
    photo(im, '光伏原图.jpg', 351, '光伏发电', '新疆巴州 · 乌若高速附近')
    photo(im, '风电原图.jpg', 630, '风力发电', '新疆巴里坤 · 三塘湖风电场')
    text(im, '医嘱：不能阻止自然发生的厄尔尼诺。', 665, 856, 32)
    return im

def icon(im, kind, cx, cy):
    d = ImageDraw.Draw(im)
    if kind == 'bag':
        d.arc((cx - 35, cy - 94, cx + 35, cy - 14), 180, 360, fill=INK, width=5)
        d.rounded_rectangle((cx - 72, cy - 45, cx + 72, cy + 64), 18, fill='#e3b48a', outline=OCHRE, width=4)
        d.rounded_rectangle((cx - 10, cy - 24, cx + 10, cy + 43), 3, fill=CREAM)
        d.rounded_rectangle((cx - 34, cy, cx + 34, cy + 20), 3, fill=CREAM)
    else:
        d.ellipse((cx - 51, cy - 79, cx + 51, cy + 23), fill='#eed19a', outline=OCHRE, width=4)
        d.line((cx - 16, cy - 21, cx, cy + 20, cx + 16, cy - 21), fill=OCHRE, width=4)
        d.rounded_rectangle((cx - 24, cy + 18, cx + 24, cy + 62), 7, fill='#91adb6', outline=INK, width=3)
        for a in [-2.7, -1.6, -.5]:
            d.line((cx + 73 * math.cos(a), cy - 25 + 73 * math.sin(a), cx + 91 * math.cos(a), cy - 25 + 91 * math.sin(a)), fill=OCHRE, width=4)

def choices():
    im = base('blank', '海洋会诊 · 我的行动单', ['判断并落实行动', '家庭与日常生活', '适应和减缓', '自选一项'], '行动')
    text(im, 'R：今天，选一项并写下分类', 661, 351, 47)
    ImageDraw.Draw(im).line((1240, 442, 1240, 834), fill='#c3b58f', width=2)
    for cx, title, kind, action, sub, color in [(938, '适应', 'bag', '和家人检查应急包', '降低暴露与损失', BLUE),
                                                (1547, '减缓', 'lamp', '完成一次节能行动', '减少温室气体排放', OCHRE)]:
        text(im, title, cx, 423, 61, color, True)
        icon(im, kind, cx, 607)
        text(im, action, cx, 724, 42, center=True)
        text(im, sub, cx, 787, 34, color, True)
    text(im, '把选择写下来，再说说它属于哪一类。', 665, 856, 35)
    return im

BUILDERS = {'adapt': adaptation, 'monitor': monitor, 'mitigate': mitigation, 'choice': choices}
PLATE_NAMES = {'adapt': '01_适应处方', 'monitor': '02_监测预警', 'mitigate': '03_减缓处方', 'choice': '04_行动选择'}
PLATE_IMAGES, PLATE_AUDIT = {}, {}
for k, fn in BUILDERS.items():
    AUDIT.clear()
    PLATE_IMAGES[k] = fn()
    PLATE_AUDIT[k] = list(AUDIT)

with wave.open(str(SOURCE / '配音/第十一段.wav'), 'rb') as wav:
    RATE = wav.getframerate()
    assert RATE == 24000 and wav.getnchannels() == 1 and wav.getsampwidth() == 2
    PCM = array('h', wav.readframes(wav.getnframes()))

SPRITE = Image.open(ASSETS / '企鹅_净面动画底图.png').convert('RGBA')
BBOX = SPRITE.getchannel('A').point(lambda x: 255 if x >= 128 else 0).getbbox()
SCALE = 368.671875 / (BBOX[3] - BBOX[1])
ACTORS = []
for state in range(4):
    art = SPRITE.copy()
    d = ImageDraw.Draw(art)
    if state == 0:
        d.arc((627, 485, 677, 510), 5, 170, fill='#8b4951', width=3)
    else:
        hh, ww = [(0, 0), (20, 43), (37, 57), (51, 63)][state]
        x, y = 651, 499
        d.ellipse((x - ww / 2, y - hh / 2, x + ww / 2, y + hh / 2), fill='#963d4b', outline='#78343e', width=3)
        if state >= 2:
            d.ellipse((x - ww / 2 + 9, y + 2, x + ww / 2 - 8, y + hh / 2 - 4), fill='#eb929a')
    if state == 0:
        art.save(ASSETS / '企鹅_净面闭口原料.png')
    d.text((742, 778), '处方单', font=font(82), anchor='mt', fill=INK)
    for j in range(3):
        d.line((642, 892 + j * 52, 840, 892 + j * 52), fill='#89aeb4', width=4)
    art.save(ASSETS / f'企鹅_净面口型_{state}.png')
    ACTORS.append(art.resize((round(art.width * SCALE), round(art.height * SCALE)), Image.Resampling.LANCZOS))

def voice(t):
    active = next((r for r in ROWS if r['start'] <= t < r['speech_end']), None)
    a = PCM[max(0, round(t * RATE)):max(0, round(t * RATE)) + 960]
    rms = math.sqrt(sum(x * x for x in a) / len(a)) / 32768 if a else 0
    return rms, 0 if not active or rms < .011 else 1 if rms < .055 else 2 if rms < .13 else 3

@lru_cache(None)
def wrapped(words, width, n):
    lines, line = [], ''
    punctuation = set('，。！？、：；）》」')
    for char in words:
        if font(n).getlength(line + char) > width and line:
            if char in punctuation:
                tail = line[-1]
                line = line[:-1]
                lines.append(line)
                line = tail + char
            else:
                lines.append(line)
                line = char
        else:
            line += char
    if line:
        lines.append(line)
    if len(lines) == 1:
        return lines
    # Balance all lines together, favoring clause boundaries and avoiding orphan
    # tails, without stretching one unusually short non-final line.
    count = len(lines)
    target = font(n).getlength(words) / count
    @lru_cache(None)
    def solve(start, remaining):
        if remaining == 0:
            return (0, ()) if start == len(words) else (float('inf'), ())
        best = (float('inf'), ())
        for stop in range(start + 1, len(words) + 1):
            part = words[start:stop]
            w = font(n).getlength(part)
            if w > width:
                break
            if stop < len(words) and words[stop] in punctuation:
                continue
            if remaining == 1 and stop != len(words):
                continue
            if remaining > 1 and stop == len(words):
                continue
            cost, rest = solve(stop, remaining - 1)
            cost += (w - target) ** 2
            if part[-1] in punctuation:
                cost -= (target * .25) ** 2
            if remaining == 1 and len(part) <= 3:
                cost += 1e9
            if cost < best[0]:
                best = (cost, (part,) + rest)
        return best
    result = list(solve(0, count)[1])
    assert ''.join(result) == words and len(result) == count
    return result

def bubble(im, words):
    n, x, right = 46, 35, 548
    lines = wrapped(words, right - x - 48, n)
    height = len(lines) * 62 + 38
    y, bottom = 570 - height, 570
    assert y > 190
    d = ImageDraw.Draw(im)
    d.polygon([(x + 180, bottom - 3), (x + 245, bottom - 3), (220, 650)], fill=CREAM)
    d.line([(x + 180, bottom - 3), (220, 650), (x + 245, bottom - 3)], fill='#bdd1d3', width=2)
    d.rounded_rectangle((x, y, right, bottom), 22, fill=CREAM, outline='#bdd1d3', width=2)
    for j, line in enumerate(lines):
        baseline = y + 24 + n + j * 62
        width = font(n).getlength(line)
        extra = (right - x - 48 - width) / (len(line) - 1) if j < len(lines) - 1 and len(line) > 1 else 0
        xx = x + 24
        for ch in line:
            d.text((xx, baseline), ch, font=font(n), fill=INK, anchor='ls')
            xx += font(n).getlength(ch) + extra
        AUDIT.append({'text': line, 'box': [x + 24, baseline - n, xx, baseline + 10], 'baseline': baseline, 'size': n})
    return [x, y, right, bottom]

def page_at(t):
    if t < row('监测')['start']:
        return 'adapt', 0
    if t < row('行动')['start']:
        return 'monitor', row('监测')['start']
    if t < META['chapter2']:
        return 'adapt', row('行动')['start']
    if t < row('区分')['start']:
        return 'mitigate', META['chapter2']
    return 'choice', row('区分')['start']

def tick(im, x, y, q=1, color=BLUE):
    q = ease(q)
    pts = [(x, y + 7), (x + 7, y + 15), (x + 23, y - 7)]
    if q < .35:
        end = (x + 7 * q / .35, y + 7 + 8 * q / .35)
        ImageDraw.Draw(im).line([pts[0], end], fill=color, width=4)
    else:
        u = (q - .35) / .65
        end = (x + 7 + 16 * u, y + 15 - 22 * u)
        ImageDraw.Draw(im).line([pts[0], pts[1], end], fill=color, width=4, joint='curve')

def frame(t):
    AUDIT.clear()
    key, since = page_at(t)
    im = PLATE_IMAGES[key].copy()
    if since > 0 and t < since + .28:
        previous = page_at(since - .001)[0]
        im = Image.blend(PLATE_IMAGES[previous], im, ease((t - since) / .28))
    if key == 'adapt':
        times = [3.35, 4.15, 5.00] if t < row('行动')['start'] else [10.65, 11.80, 13.15]
        for j, at in enumerate(times):
            if t > at:
                tick(im, 666, 606 + j * 88, (t - at) / .25)
    elif key == 'monitor':
        for j, at in enumerate([6.2, 7.5, 8.8]):
            if t > at:
                tick(im, 666, 568 + j * 94, (t - at) / .25)
    elif key == 'mitigate':
        for j, at in enumerate([21.1, 23.0, 25.8]):
            if t > at:
                tick(im, 666, 606 + j * 88, (t - at) / .25, OCHRE)
    elif t < row('选择')['start']:
        for j, at in enumerate([row('区分')['start'] + 1.5, row('区分')['start'] + 3]):
            if t > at:
                tick(im, [733, 1345][j], 752, (t - at) / .25, [BLUE, OCHRE][j])
    thinking = META['thinking'][0] <= t < META['thinking'][1]
    if thinking:
        shade = Image.new('RGBA', im.size)
        ImageDraw.Draw(shade).rectangle((615, 330, 1880, 905), fill=(20, 43, 58, 135))
        im = Image.alpha_composite(im.convert('RGBA'), shade).convert('RGB')
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((1077, 451, 1422, 790), 22, fill=CREAM, outline='#c2a36e', width=3)
        text(im, '轮到你了', 1250, 477, 42, center=True)
        text(im, str(3 - int(t - META['thinking'][0])), 1250, 551, 146, center=True)
    rms, state = voice(t)
    actor = ACTORS[state]
    px = round(253 - (BBOX[0] + BBOX[2]) / 2 * SCALE)
    py = round(985 + 1.2 * math.sin(t * 2) - BBOX[3] * SCALE)
    speaking = next((r for r in ROWS if r['start'] <= t < r['end']), None)
    box = None
    if speaking:
        box = bubble(im, speaking['text'])
    elif thinking:
        box = bubble(im, '你选哪一项？')
    im.paste(actor, (px, py), actor)
    alpha_box = actor.getchannel('A').point(lambda x: 255 if x >= 128 else 0).getbbox()
    body = [px + alpha_box[0], py + alpha_box[1], px + alpha_box[2], py + alpha_box[3]]
    assert 366 <= body[3] - body[1] <= 371
    return im, {'time': t, 'page': key, 'mouth': state, 'rms': rms, 'thinking': thinking, 'body_box': body,
                'bubble_box': box, 'text': list(AUDIT)}

def preview():
    samples = [('adapt', 4.8), ('monitor', 8.8), ('mitigate', 25.2), ('choice', 39.2)]
    for j, (key, t) in enumerate(samples):
        im, _ = frame(t)
        im.save(PLATES / (PLATE_NAMES[key] + '.png'))
    # A compact 2-by-2 overview without excess white space.
    compact = Image.new('RGB', (1440, 880), '#e9eee9')
    for j, (key, t) in enumerate(samples):
        im, _ = frame(t)
        compact.paste(im.resize((720, 405), Image.Resampling.LANCZOS), ((j % 2) * 720, (j // 2) * 440))
        ImageDraw.Draw(compact).text(((j % 2) * 720 + 12, (j // 2) * 440 + 410), PLATE_NAMES[key], font=font(24), fill=INK)
    compact.save(PLATES / '四页总览.jpg', quality=95)
    # Inspect repaired facial skin at native sprite resolution, across all mouth states.
    close = Image.new('RGB', (1200, 300), '#d5ebef')
    for j in range(4):
        a = Image.open(ASSETS / f'企鹅_净面口型_{j}.png').convert('RGBA').crop((430, 350, 850, 590))
        a.thumbnail((300, 300), Image.Resampling.LANCZOS)
        close.paste(a, (j * 300, 0), a)
    close.save(CHECK / '净面四口型放大.png')
    (CHECK / '静态文字边界.json').write_text(json.dumps(PLATE_AUDIT, ensure_ascii=False, indent=2))
    print('PREVIEW_READY', flush=True)

def encode_segment():
    if not ORIGINAL.exists():
        assert hashlib.sha256(MASTER.read_bytes()).hexdigest() == '9fbf054f8d79c58e81fc67633049fd787911f00d664fe46683041bee56d31a77'
        shutil.copy2(MASTER, ORIGINAL)
    pending = R / '处方段.pending.mp4'
    args = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', '24', '-i', '-',
            '-i', str(SOURCE / '配音/第十一段.wav'), '-frames:v', str(FRAMES), '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
            '-profile:v', 'baseline', '-level:v', '4.0', '-g', '24', '-bf', '0', '-refs', '1', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-ar', '48000', '-ac', '2', '-b:a', '160k', '-af', 'apad', '-t', str(FRAMES / FPS),
            '-movflags', '+faststart', str(pending)]
    audits = []
    with (CHECK / '处方段编码日志.txt').open('wb') as log:
        proc = subprocess.Popen(args, stdin=subprocess.PIPE, stderr=log)
        for i in range(FRAMES):
            im, audit = frame(i / FPS)
            proc.stdin.write(im.tobytes())
            audits.append(audit)
            if i % 240 == 0:
                print('PRESCRIPTION_FRAMES', i, '/', FRAMES, flush=True)
        proc.stdin.close()
        assert proc.wait() == 0
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(pending), '-f', 'null', '-'], check=True)
    SEGMENT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pending, SEGMENT)
    pending.replace(R / '处方段_完整48秒.mp4')
    (CHECK / '逐帧动画记录.json').write_text(json.dumps(audits, ensure_ascii=False))
    print('PRESCRIPTION_ENCODED', flush=True)

def encode_master():
    output = MASTER.with_name('.处方修正.pending.mp4')
    graph = (f'[0:v]setpts=N/(24*TB)[main];'
             f'[1:v]setpts=(N+{START})/(24*TB)[rx];'
             f"[main][rx]overlay=eof_action=pass:repeatlast=0:enable='gte(t,{START/FPS})*lt(t,{END/FPS:.12f})'[v]")
    args = ['ffmpeg', '-v', 'error', '-y', '-i', str(ORIGINAL), '-i', str(R / '处方段_完整48秒.mp4'),
            '-filter_complex', graph, '-map', '[v]', '-map', '0:a:0', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
            '-profile:v', 'baseline', '-level:v', '4.0', '-g', '24', '-bf', '0', '-refs', '1', '-pix_fmt', 'yuv420p',
            '-r', '24', '-frames:v', str(TOTAL), '-c:a', 'copy', '-movflags', '+faststart',
            '-progress', str(CHECK / '全片编码进度.txt'), str(output)]
    print('MASTER_ENCODING', flush=True)
    with (CHECK / '全片编码日志.txt').open('wb') as log:
        subprocess.run(args, stderr=log, check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(output), '-f', 'null', '-'], check=True)
    output.replace(MASTER)
    print('MASTER_ENCODED', MASTER, flush=True)

def refresh_original_preview():
    """Refresh the original prescription still, sprite and five-second preview."""
    for relative in ['修改方案_三画面/03_适应处方单.png', '修改方案_三画面/三个画面总览.jpg',
                     'demooo/预览/三个画面5秒样片/适应处方单_5秒.mp4']:
        source = P / relative
        saved = R / '修复前预览' / source.name
        saved.parent.mkdir(exist_ok=True)
        if not saved.exists():
            shutil.copy2(source, saved)
    old_sprite = P / '修改方案_三画面/企鹅_拿处方单.png'
    backup = ASSETS / '企鹅_修复前.png'
    if not backup.exists():
        shutil.copy2(old_sprite, backup)
    shutil.copy2(ASSETS / '企鹅_净面闭口原料.png', old_sprite)
    shutil.copy2(PLATES / '01_适应处方.png', P / '修改方案_三画面/03_适应处方单.png')
    overview = Image.new('RGB', (1440, 2544), '#e6eeec')
    for i, (name, path) in enumerate([
        ('01 Illustrated route', P / '修改方案_三画面/01_四步会诊路线.png'),
        ('02 Concept comparison', P / '修改方案_三画面/02_厄尔尼诺与人为增暖.png'),
        ('03 Prescription - repaired', PLATES / '01_适应处方.png')]):
        art = Image.open(path).convert('RGB').resize((1440, 810), Image.Resampling.LANCZOS)
        overview.paste(art, (0, i * 848))
        ImageDraw.Draw(overview).text((24, i * 848 + 818), name, font=font(24), fill=INK)
    overview.save(P / '修改方案_三画面/三个画面总览.jpg', quality=95)
    audio = array('h', [0]) * 120000
    first = ROWS[0]
    take = PCM[round(first['start'] * RATE):round(first['speech_end'] * RATE)]
    offset = round(.35 * RATE)
    audio[offset:offset + len(take)] = take
    wav_path = R / '首张处方5秒.wav'
    with wave.open(str(wav_path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(audio.tobytes())
    output = P / 'demooo/预览/三个画面5秒样片/适应处方单_5秒.mp4'
    args = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', '24', '-i', '-',
            '-i', str(wav_path), '-frames:v', '120', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
            '-profile:v', 'baseline', '-level:v', '4.0', '-g', '24', '-bf', '0', '-refs', '1', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-ar', '48000', '-ac', '2', '-b:a', '128k', '-movflags', '+faststart', str(output)]
    output.parent.mkdir(parents=True, exist_ok=True)
    with (CHECK / '首张处方样片日志.txt').open('wb') as log:
        proc = subprocess.Popen(args, stdin=subprocess.PIPE, stderr=log)
        for i in range(120):
            local = i / 24
            t = min(5.95, max(2.0, local + 1.65))
            im, _ = frame(t)
            if local < .35:
                # Rebuild from the same plate so the silent lead has a closed mouth.
                im = PLATE_IMAGES['adapt'].copy()
                bubble(im, first['text'])
                actor = ACTORS[0]
                px = round(253 - (BBOX[0] + BBOX[2]) / 2 * SCALE)
                py = round(985 - BBOX[3] * SCALE)
                im.paste(actor, (px, py), actor)
            proc.stdin.write(im.tobytes())
        proc.stdin.close()
        assert proc.wait() == 0
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(output), '-f', 'null', '-'], check=True)
    print('ORIGINAL_PREVIEW_REPAIRED', output, flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--master', action='store_true')
    parser.add_argument('--refresh-preview', action='store_true')
    args = parser.parse_args()
    preview()
    if args.render:
        encode_segment()
    if args.master:
        encode_master()
    if args.refresh_preview:
        refresh_original_preview()
