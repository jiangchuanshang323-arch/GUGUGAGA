from pathlib import Path
import hashlib
import json
import subprocess
import time

from PIL import Image
import numpy as np

from build_route_v3 import FF, FPS, OUT, Q, frame


# Keep the four 5-second station performances intact. The four walking
# intervals take half as long, so the penguin steps instead of drifting.
SOURCE_CUTS = np.array([0, 1.5, 6.5, 10.5, 15.5, 19, 24, 29.5, 34.5, 36])
OUTPUT_CUTS = np.array([0, .75, 5.75, 7.75, 12.75, 14.5,
                        19.5, 22.25, 27.25, 28.75])
N = round(OUTPUT_CUTS[-1] * FPS)


def source_time(t):
    return float(np.interp(t, OUTPUT_CUTS, SOURCE_CUTS))


def main():
    dest = OUT / '四步会诊路线_全程动作展示.mp4'
    temp = OUT / '.四步会诊路线_v3_编码中.mp4'
    report_path = Q / '全程_v3_交付验证.json'
    checkpoints = [0.4, 1.7, 4.5, 6.8, 9.5, 11.5, 13.5, 16.5,
                   18.5, 20.4, 21.8, 22.3, 22.5, 23.0, 24.2, 25.5,
                   26.2, 27.5, 28.5]
    checkpoints = {round(t * FPS) for t in checkpoints}
    contact = Image.new('RGB', (480 * 4, 270 * 5))
    started = time.monotonic()
    audit = []
    command = [str(FF), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt',
               'rgb24', '-s', '1920x1080', '-r', str(FPS), '-i', '-',
               '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
               '-frames:v', str(N), '-t', str(N / FPS), '-c:v', 'libx264',
               '-profile:v', 'baseline', '-level', '4.0', '-g', '24', '-bf', '0',
               '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p',
               '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(temp)]
    with (Q / '全程_v3_编码日志.txt').open('wb') as log:
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=log)
        try:
            for i in range(N):
                image, metadata = frame(source_time(i / FPS))
                proc.stdin.write(image.tobytes())
                audit.append(metadata)
                if i in checkpoints:
                    tile = image.resize((480, 270), Image.Resampling.LANCZOS)
                    j = sorted(checkpoints).index(i)
                    contact.paste(tile, ((j % 4) * 480, (j // 4) * 270))
                if i % 96 == 0:
                    print(f'render {i}/{N}', flush=True)
        finally:
            proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError('ffmpeg encoding failed; see encoding log')
    contact.save(Q / '全程_v3_关键帧总览.jpg', quality=90)
    check = subprocess.run([str(FF), '-v', 'error', '-i', str(temp),
                            '-f', 'null', '-'], capture_output=True)
    if check.returncode or check.stderr:
        raise RuntimeError('full decode failed: ' + check.stderr.decode(errors='replace'))
    stations = {1: 0, 2: 0, 3: 0, 4: 0}
    for item in audit:
        if item['station'] in stations:
            stations[item['station']] += 1
    if any(v == 0 for v in stations.values()):
        raise RuntimeError(f'missing station: {stations}')
    temp.replace(dest)
    report = {
        'path': str(dest), 'duration_seconds': N / FPS,
        'resolution': [1920, 1080], 'fps': FPS, 'frames': N,
        'station_frames': stations,
        'source': 'build_route_v3.py:frame',
        'walking_speed': '2x',
        'source_time_cuts': SOURCE_CUTS.tolist(),
        'output_time_cuts': OUTPUT_CUTS.tolist(),
        'sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
        'decode': 'PASS', 'elapsed_seconds': round(time.monotonic() - started, 1),
        'merged_into_full_course': False,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
