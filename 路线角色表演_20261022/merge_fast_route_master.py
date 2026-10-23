"""Replace four old walk inserts in the retained master, preserving course audio."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
sys.path.insert(0, str(PROJECT / "demooo"))
import manage_videos as m

SRC = PROJECT / "demooo/预览/四步会诊路线全程/四步会诊路线_全程动作展示.mp4"
BASE = PROJECT / "demooo/合成版本/目前完整成片/海洋发烧了_目前完整成片.mp4"
OUT = BASE.with_name("海洋发烧了_目前完整成片_新版_四站动作.mp4")
STAGE = HERE / "新版合入_20261023"
STAGE.mkdir(exist_ok=True)
REPORT = json.loads((BASE.parent / "检查/合成验证.json").read_text("utf-8"))
BASE_FRAMES = 17428
SOURCE_FRAMES = 690
STATIONS = [
    ("测体征", 1743, 0, 138),
    ("查病因", 3836, 138, 306),
    ("追并发症", 6930, 306, 468),
    ("开处方", 14628, 468, 690),
]
FPS = 24
FRAME_BYTES = 1920 * 1080 * 3
AUDIO_BYTES_PER_FRAME = 48000 // FPS * 4


def read_frame(proc):
    result = proc.stdout.read(FRAME_BYTES)
    if len(result) != FRAME_BYTES:
        raise RuntimeError(f"short frame {len(result)}")
    return result


def blend(raw_a, raw_b, alpha):
    a = Image.frombytes("RGB", (1920, 1080), raw_a)
    b = Image.frombytes("RGB", (1920, 1080), raw_b)
    return Image.blend(a, b, alpha).tobytes()


def build_audio():
    raw = subprocess.run(
        [m.EXE, "-v", "error", "-i", str(BASE), "-vn", "-f", "s16le",
         "-ar", "48000", "-ac", "2", "-"],
        capture_output=True, check=True,
    ).stdout
    need = BASE_FRAMES * AUDIO_BYTES_PER_FRAME
    raw = (raw + bytes(max(0, need - len(raw))))[:need]
    chunks = []
    at = 0
    for _, start, first, end in STATIONS:
        chunks.append(raw[at * AUDIO_BYTES_PER_FRAME:start * AUDIO_BYTES_PER_FRAME])
        chunks.append(bytes((end - first) * AUDIO_BYTES_PER_FRAME))
        at = start + 100
    chunks.append(raw[at * AUDIO_BYTES_PER_FRAME:])
    joined = b"".join(chunks)
    expected_frames = BASE_FRAMES + sum((end-first)-100 for _,_,first,end in STATIONS)
    assert len(joined) == expected_frames * AUDIO_BYTES_PER_FRAME
    wav = STAGE / ".新版完整成片音轨.wav"
    with wave.open(str(wav), "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(48000)
        out.writeframes(joined)
    return wav, expected_frames


def build_master():
    assert m.digest(BASE) == REPORT["sha256"]
    route_report = json.loads(
        (HERE / "检查/原翅膀与帽子贴合/全程_v3_交付验证.json").read_text("utf-8"))
    assert m.digest(SRC) == route_report["sha256"]
    assert round(REPORT["seconds"] * FPS) == BASE_FRAMES
    assert [round(t * FPS) for t in REPORT["route_starts"]] == [x[1] for x in STATIONS]
    wav, total = build_audio()
    pending = STAGE / ".完整版新版编码中.mp4"
    logs = [(STAGE / name).open("wb") for name in
            ("原版解码日志.txt", "新路线解码日志.txt", "完整版编码日志.txt")]
    old = subprocess.Popen(
        [m.EXE, "-v", "error", "-i", str(BASE), "-map", "0:v:0",
         "-vf", f"fps=24,tpad=stop_mode=clone:stop_duration=0.2,trim=end_frame={BASE_FRAMES}",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE, stderr=logs[0],
    )
    new = subprocess.Popen(
        [m.EXE, "-v", "error", "-i", str(SRC), "-map", "0:v:0",
         "-vf", f"fps=24,trim=end_frame={SOURCE_FRAMES}",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE, stderr=logs[1],
    )
    enc = subprocess.Popen(
        [m.EXE, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", "1920x1080", "-r", "24", "-i", "-", "-i", str(wav),
         "-frames:v", str(total), "-t", str(total / FPS),
         "-c:v", "libx264", "-preset", "fast", "-crf", "18",
         "-profile:v", "baseline", "-level:v", "4.0", "-g", "24", "-bf", "0",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
         "-movflags", "+faststart", str(pending)],
        stdin=subprocess.PIPE, stderr=logs[2],
    )
    count = 0
    old_at = 0
    new_at = 0
    seams = []
    try:
        for number, (label, start, first, end) in enumerate(STATIONS, 1):
            for _ in range(start - old_at):
                enc.stdin.write(read_frame(old))
                count += 1
            old_at = start
            original_first = []
            original_last = []
            for i in range(100):
                raw = read_frame(old)
                if i < 8:
                    original_first.append(raw)
                if i >= 92:
                    original_last.append(raw)
            old_at += 100
            assert new_at == first
            out_start = count
            for j in range(end-first):
                raw = read_frame(new)
                if j < 8:
                    raw = blend(original_first[j], raw, (j+1)/8)
                elif j >= end-first-8:
                    k = j-(end-first-8)
                    raw = blend(raw, original_last[k], (k+1)/8)
                enc.stdin.write(raw)
                count += 1
                new_at += 1
            seams.append(dict(station=number, label=label, original_frame=start,
                              new_start_frame=out_start, new_end_frame=count,
                              demo_source_frames=[first,end], crossfade_frames=8))
            print("STATION_WRITTEN", number, label, count, "/", total, flush=True)
        for _ in range(BASE_FRAMES - old_at):
            enc.stdin.write(read_frame(old))
            count += 1
    finally:
        enc.stdin.close()
        old.stdout.close()
        new.stdout.close()
    codes = (enc.wait(), old.wait(), new.wait())
    for log in logs:
        log.close()
    wav.unlink(missing_ok=True)
    assert codes == (0, 0, 0), codes
    assert count == total and new_at == SOURCE_FRAMES
    m.decode(pending)
    info = m.info(pending)
    assert abs(info["seconds"] - total/FPS) < .03, info
    pending.replace(OUT)
    data = dict(
        path=str(OUT), **m.info(OUT), frames=total, fps=24,
        resolution=[1920,1080], decode="PASS",
        previous_full=str(BASE), previous_sha256=REPORT["sha256"],
        route_source=str(SRC), route_sha256=route_report["sha256"],
        route_seams=seams, stage="new version; not uploaded",
        visual_review="pending encoded seam review",
    )
    (STAGE / "新版合成验证.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("MASTER_READY", OUT, total, info["seconds"], flush=True)


def split_demos():
    names = ["01_测体征", "02_查病因", "03_追并发症", "04_开处方"]
    demo_dir = PROJECT / "demooo/预览/四步会诊路线全程/四站分段新版"
    demo_dir.mkdir(exist_ok=True)
    for name, (_, _, first, end) in zip(names, STATIONS):
        dest = demo_dir / f"四步会诊路线_{name}_新版.mp4"
        subprocess.run(
            [m.EXE, "-v", "error", "-y", "-i", str(SRC),
             "-vf", f"trim=start_frame={first}:end_frame={end},setpts=N/(24*TB)",
             "-an", "-frames:v", str(end-first), "-c:v", "libx264",
             "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", str(dest)],
            check=True,
        )
        m.decode(dest)
        print("DEMO_READY", dest, flush=True)


if __name__ == "__main__":
    if "--demos" in sys.argv:
        split_demos()
    else:
        build_master()
