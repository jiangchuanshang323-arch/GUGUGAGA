from pathlib import Path
import sys,subprocess,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'runtime'))
import cv2
sys.path.insert(0,str(ROOT.parents[1]/'ocean_animation_demo_20261011'/'runtime'))
import imageio_ffmpeg
EXE=imageio_ffmpeg.get_ffmpeg_exe();SRC=ROOT.parents[1]/'外部生成视频'/'shot_01_用户开场_20261012.mp4'
cap=cv2.VideoCapture(str(SRC));fps=cap.get(cv2.CAP_PROP_FPS);W=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));H=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cap.set(cv2.CAP_PROP_POS_MSEC,2000);ok,reference=cap.read();assert ok
# Derive a fixed glyph mask on a dark ocean background, retaining scenery.
rx,ry,rw,rh=1066,581,134,44
roi=reference[ry:ry+rh,rx:rx+rw];minimum=np.min(roi,axis=2)
mask=(minimum>130).astype(np.uint8)*255
mask=cv2.dilate(mask,np.ones((3,3),np.uint8),iterations=1)
Image.fromarray(mask).save(ROOT/'.build'/'水印字形遮罩.png')
yy,xx=np.where(mask>0);mx0,mx1,my0,my1=xx.min(),xx.max()+1,yy.min(),yy.max()+1
glyph_mask=mask[my0:my1,mx0:mx1]
glyph_edges=cv2.Laplacian(cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY),cv2.CV_32F)[my0:my1,mx0:mx1]
cap.set(cv2.CAP_PROP_POS_FRAMES,0)
clean=ROOT/'.build'/'开场_字形修补.mp4'
cmd=[EXE,'-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-i',str(SRC),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-crf','18','-preset','fast','-c:a','copy','-shortest',str(clean)]
with open(ROOT/'.build'/'inpaint.log','w') as log:
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log);n=0
    while True:
        ok,frame=cap.read()
        if not ok:break
        t=n/fps
        if t<4.35 or t>7.55:
            area=frame[ry:ry+rh,rx:rx+rw];frame[ry:ry+rh,rx:rx+rw]=cv2.inpaint(area,mask,3,cv2.INPAINT_TELEA)
        if 4<=t<=8.15:
            # The alternate logo position is exactly 1056px left and 398px up.
            lx,ly=14,174
            shifted=np.zeros((47,134),dtype=np.uint8)
            # Match the same logo's letter edges instead of masking bright clouds.
            patch=frame[ly:ly+47,lx:lx+134]
            edge=cv2.Laplacian(cv2.cvtColor(patch,cv2.COLOR_BGR2GRAY),cv2.CV_32F)
            match=cv2.matchTemplate(edge,glyph_edges,cv2.TM_CCOEFF_NORMED)
            _,confidence,_,(gx,gy)=cv2.minMaxLoc(match)
            if confidence>.20:
                shifted[gy:gy+glyph_mask.shape[0],gx:gx+glyph_mask.shape[1]]=glyph_mask
                frame[ly:ly+47,lx:lx+134]=cv2.inpaint(patch,shifted,3,cv2.INPAINT_TELEA)
        p.stdin.write(frame.tobytes());n+=1
    cap.release();p.stdin.close();assert p.wait()==0
for t in (2,6,9.8):subprocess.run([EXE,'-v','error','-ss',str(t),'-i',str(clean),'-frames:v','1','-vf','scale=960:-1','-y',str(ROOT/'.build'/f'字形修补_{t}.png')],check=True)
print('Refined opening '+str(n)+' frames',flush=True)
