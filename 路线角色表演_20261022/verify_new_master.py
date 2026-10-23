"""Decode and inspect the four splice edges in the 2026-10-23 master."""
import io
import json
import re
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "demooo"))
import manage_videos as m

q = HERE / "新版合入_20261023"
report_path = q / "新版合成验证.json"
report = json.loads(report_path.read_text("utf-8"))
path = Path(report["path"])
assert path.exists()
probe = subprocess.run(
    [m.EXE, "-hide_banner", "-i", str(path), "-map", "0:v:0",
     "-c", "copy", "-f", "null", "-"], capture_output=True, check=True,
)
frame_count = int(re.findall(r"frame=\s*(\d+)",
                             probe.stderr.decode("utf-8", "replace"))[-1])
assert frame_count == report["frames"] == 17718
assert report["decode"] == "PASS"
times = []
for row in report["route_seams"]:
    for where, frame in [
        ("before", row["new_start_frame"]-3),
        ("enter", row["new_start_frame"]+3),
        ("station", (row["new_start_frame"]+row["new_end_frame"])//2),
        ("leave", row["new_end_frame"]-3),
        ("after", row["new_end_frame"]+3),
    ]:
        times.append((row["station"], where, frame / 24))
sheet = Image.new("RGB", (1600, len(times)//5*270), "#e7eeeb")
d = ImageDraw.Draw(sheet)
for i, (station, where, t) in enumerate(times):
    raw = subprocess.run(
        [m.EXE, "-v", "error", "-ss", f"{t:.9f}", "-i", str(path),
         "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
        capture_output=True, check=True,
    ).stdout
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    assert image.size == (1920, 1080)
    image = image.resize((320, 180), Image.Resampling.LANCZOS)
    x, y = (i%5)*320, (i//5)*270
    sheet.paste(image, (x,y))
    d.text((x+10,y+190), f"station {station} {where} {t:.3f}s", fill="#234657")
sheet.save(q / "四站新版_实际编码接缝总览.jpg", quality=92)
report.update(encoded_frame_count=frame_count, seam_review_sheet=str(q / "四站新版_实际编码接缝总览.jpg"))
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print("PASS", frame_count, path)
