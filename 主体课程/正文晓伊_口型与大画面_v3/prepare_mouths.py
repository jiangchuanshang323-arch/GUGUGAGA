from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json
ROOT=Path(__file__).resolve().parent
im=Image.open(ROOT/'素材'/'嘴型图集.png').convert('RGBA'); w=im.width//4
out=[]
for i in range(4):
    cell=im.crop((i*w,0,(i+1)*w,im.height));a=np.asarray(cell)
    mask=(a[:,:,3]>240)&(a[:,:,0]<205)&(a[:,:,1]<140)&(a[:,:,2]<140)&(a[:,:,0]>a[:,:,1]*1.2)
    mask[:im.height//3]=False;mask[im.height*3//4:]=False
    mask[:,:w//4]=False;mask[:,w*3//4:]=False
    yy,xx=np.where(mask);cx=(xx.min()+xx.max())/2;cy=(yy.min()+yy.max())/2
    # Sprite extraction and masks only: all mouth artwork came from imagegen.
    tile=cell.crop((round(cx-110),round(cy-90),round(cx+110),round(cy+90)))
    alpha=Image.new('L',tile.size,0);d=ImageDraw.Draw(alpha)
    for n in range(10):d.rounded_rectangle((n,n,tile.width-1-n,tile.height-1-n),radius=15,fill=round(255*(n+1)/10))
    tile.putalpha(alpha)
    p=ROOT/'素材'/f'嘴型_{i}.png';tile.save(p);out.append({'state':i,'mouth_box':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())],'path':str(p)})
(ROOT/'素材'/'嘴型提取说明.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(out)

# Match only the generated skin matte to the existing face; retain drawn lips,
# teeth and tongue. This is mechanical overlay preparation, not new artwork.
poses={int(p.name[:2]):Image.open(p).convert('RGBA') for p in (ROOT.parents[1]/'企鹅小老师_教学动作素材_20261012'/'独立动作PNG').glob('*.png')}
centers={3:(266,229,43,37),4:(306,220,35,29),5:(274,218,35,29),6:(227,218,50,44),7:(288,235,50,44),8:(274,240,31,26),9:(277,234,30,27)}
for pose,(cx,cy,pw,ph) in centers.items():
    source=np.asarray(poses[pose]);x0=round(cx-pw/2);y0=round(cy-ph/2)
    X=[];Y=[]
    for dy in range(-ph//2-3,ph//2+4):
        for dx in range(-pw//2-3,pw//2+4):
            if abs(dx)<pw*.40 and abs(dy)<ph*.40:continue
            rgb=source[cy+dy,cx+dx,:3]
            if rgb[0]>210 and rgb[1]>160 and rgb[2]>135 and int(rgb[0])-int(rgb[1])>6:
                X.append([1,dx,dy]);Y.append(rgb)
    coeff=np.linalg.lstsq(np.array(X),np.array(Y),rcond=None)[0]
    for state in range(4):
        patch=Image.open(ROOT/'素材'/f'嘴型_{state}.png').convert('RGBA').resize((pw,ph),Image.Resampling.LANCZOS)
        arr=np.array(patch);xx,yy=np.meshgrid(np.arange(pw)-pw/2,np.arange(ph)-ph/2)
        plane=np.stack([np.ones_like(xx),xx,yy],axis=2)@coeff
        skin=(arr[:,:,0]>215)&(arr[:,:,1]>155)&(arr[:,:,2]>135)&((arr[:,:,0].astype(int)-arr[:,:,1])>10)
        arr[:,:,:3][skin]=np.clip(plane[skin],0,255).astype(np.uint8)
        # A narrow feather keeps the matte invisible while fully covering old lips.
        alpha=Image.new('L',(pw,ph),0);dd=ImageDraw.Draw(alpha)
        dd.rounded_rectangle((2,2,pw-3,ph-3),radius=5,fill=255)
        arr[:,:,3]=np.asarray(alpha.filter(ImageFilter.GaussianBlur(.7)))
        Image.fromarray(arr).save(ROOT/'素材'/f'口型_{pose:02d}_{state}.png')
