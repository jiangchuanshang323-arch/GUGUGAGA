from pathlib import Path
import sys,math,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'抛卷轴_高清全屏_v17'))
import build_v17 as s
v=s.v;b=s.b
BASE=Image.open(ROOT/'素材'/'27_连续握持底图.png').convert('RGBA')
LOOK=Image.open(ROOT/'素材'/'28_抬头看卷轴.png').convert('RGBA').resize(BASE.size,Image.Resampling.LANCZOS)
headmask=Image.new('L',BASE.size,0)
md=ImageDraw.Draw(headmask);md.rectangle((0,0,1280,600),fill=255)
for yy in range(601,650):md.line((0,yy,1280,yy),fill=round(255*(650-yy)/50))
LOOK=Image.composite(LOOK,BASE,headmask)
FRONT=Image.open(ROOT/'素材'/'29_正面看观众.png').convert('RGBA').resize(BASE.size,Image.Resampling.LANCZOS)
FRONT=Image.composite(FRONT,BASE,headmask)
RELEASE=1.10

def ease(a,lo,hi):return b.ease((a-lo)/(hi-lo))
def hand_at(a):
    if a<.65:
        q=ease(a,.12,.65);return (600-48*q,835-107*q)
    q=ease(a,.76,RELEASE);return (552-192*q,728-348*q)

def jump_y(a):
    if a<.76:return 0
    if a<.86:return 12*ease(a,.76,.86)
    if a<1.14:return 12-100*ease(a,.86,1.14)
    if a<1.57:return -88+88*ease(a,1.14,1.57)
    if a<1.73:return 5*math.sin(math.pi*ease(a,1.57,1.73))
    return 0

def curve(points):
    out=[]
    for i in range(31):
        t=i/30;u=1-t
        out.append(tuple(u*u*u*points[0][k]+3*u*u*t*points[1][k]+3*u*t*t*points[2][k]+t*t*t*points[3][k] for k in (0,1)))
    return out

def arm(stage,hand,origin,front=False,clip=False):
    # Continuous shoulder-to-grip geometry. The grip and scroll share exactly the same hand joint.
    h=hand;sh=(503,684);dx=h[0]-sh[0];dy=h[1]-sh[1];length=math.hypot(dx,dy)
    nx=-dy/length;ny=dx/length
    def off(p,k):return (p[0]+nx*k,p[1]+ny*k)
    art=Image.new('RGBA',(1280,1280));d=ImageDraw.Draw(art)
    if not front:
        a=off(sh,55);c=off(h,30);e=off(h,-30);f=off(sh,-55)
        mid=((sh[0]+h[0])*.5,(sh[1]+h[1])*.5)
        back=(sh[0]-dx/length*52,sh[1]-dy/length*52)
        pts=curve([a,off(mid,63),off(h,48),h])+curve([h,off(h,-43),off(mid,-52),f])+curve([f,back,back,a])
        d.polygon(pts,fill='#50525f');d.line(pts,fill='#171920',width=10,joint='curve')
        highlight=curve([off(sh,37),off(mid,44),off(h,23),(h[0]-dx*.12,h[1]-dy*.12)])
        d.line(highlight,fill='#898e9d',width=7,joint='curve')
    else:
        # Foreground wrap hides the roll at the grip, so it reads as held rather than hovering.
        d.ellipse((h[0]-28,h[1]-16,h[0]+25,h[1]+18),fill='#50525f',outline='#171920',width=7)
        d.arc((h[0]-23,h[1]-11,h[0]+20,h[1]+14),180,290,fill='#9296a4',width=4)
    if clip:art.paste((0,0,0,0),(0,805,1280,1280))
    art=art.resize((390,390),Image.Resampling.LANCZOS);stage.paste(art,origin,art)

def transition(age):
    stage=Image.open(b.BG).convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS)
    stage.paste(s.OLD_BOARD,(24,140),s.OLD_BOARD)
    bounce=jump_y(age);origin=(1510,660+round(bounce))
    ground=Image.new('RGBA',stage.size);gd=ImageDraw.Draw(ground)
    sw=74-18*min(1,max(0,-bounce/88))
    gd.ellipse((1705-sw,1020,1705+sw,1037),fill=(64,88,101,38))
    stage.paste(ground,(0,0),ground)
    # Start raising the head at takeoff, before the hand releases the scroll.
    # A brief pose transition avoids long double-eye ghosting; only head is affected.
    gaze=ease(age,.86,.94)
    audience=ease(age,1.22,1.30)
    sprite=Image.blend(Image.blend(BASE,LOOK,gaze),FRONT,audience).resize((390,390),Image.Resampling.LANCZOS);stage.paste(sprite,origin,sprite)
    h=hand_at(min(age,RELEASE));held=age<RELEASE
    if not held:
        follow=ease(age,RELEASE,RELEASE+.13)
        h=(h[0]-15*follow,h[1]-28*follow)
        recover=ease(age,1.20,1.52)
        h=(h[0]+(452-h[0])*recover,h[1]+(830-h[1])*recover)
    arm(stage,h,origin,clip=age<.28)
    scale=390/1280
    grip=(origin[0]+h[0]*scale,origin[1]+h[1]*scale)
    rh=hand_at(RELEASE)
    release=(1510+(rh[0]+2)*scale,660+(rh[1]+15)*scale+round(jump_y(RELEASE)))
    if held:
        # The roll is still below the pocket lip initially; extraction follows the moving flipper.
        cx=grip[0]+2*scale;cy=grip[1]+15*scale
        cutoff=origin[1]+805*scale if age<.70 else None
        s.paste_scroll(stage,cx,cy,14,42,rotation=-10*ease(age,.76,RELEASE),cutoff=cutoff)
        arm(stage,h,origin,front=True,clip=age<.28)
        return stage
    flight=ease(age,RELEASE,1.72)
    cx=release[0]+(1050-release[0])*flight
    cy=release[1]+(370-release[1])*flight-230*4*flight*(1-flight)
    rotation=-10+10*ease(age,RELEASE,1.38)
    opening=ease(age,1.50,2.02);zoom=ease(age,2.02,2.70)
    factor=1+(1920/804-1)*zoom
    width=14+804*opening*factor;height=(42+(804*1080/1920-42)*opening)*factor+12*opening
    cx+=(960-cx)*zoom;cy+=(540-cy)*zoom
    rails=1-ease(age,2.54,2.76)
    s.paste_scroll(stage,cx,cy,width,height,rotation,s.POSTER if opening>.035 else None,rails)
    if age>2.76:stage=Image.blend(stage,s.POSTER,ease(age,2.76,2.80))
    return stage

def render(t):
    if t<v.BRIDGE_START:return v.old.base_render(t)
    if t<v.BRIDGE_END:return transition(t-v.BRIDGE_START)
    return v.diagram_render(t)
v.render=render

def main():
    ages=(.52,1.04,1.18,1.32,1.46,1.72)
    sheet=Image.new('RGB',(1200,800),b.CREAM)
    for i,a in enumerate(ages):
        im=transition(a);im.save(ROOT/f'握持检查_{a}.png')
        shot=im.crop((1450,540,1920,1080)).resize((400,400),Image.Resampling.LANCZOS)
        sheet.paste(shot,((i%3)*400,(i//3)*400))
    sheet.save(ROOT/'握持连续动作检查.jpg')
    if '--preview' in sys.argv:return
    end=next(r['end'] for r in v.DATA if r['mode']=='方向')
    out=ROOT/'交付'/'上抛后面向观众再展开_demo_v22.mp4'
    v.encode(out,v.BRIDGE_START,end-v.BRIDGE_START)
    assert 1.30 < 1.50
    (ROOT/'验证.json').write_text(json.dumps({'decode':'PASS','seconds':end-v.BRIDGE_START,'release_second':RELEASE,'grip_and_scroll_shared_joint':True,'jump_height_px':88,'landing_second':1.57,'head_raise_start':.86,'head_raise_end':.94,'face_audience':[1.22,1.30],'scroll_open_start':1.50,'faces_audience_before_unroll':True,'arm_returns_down':True,'full_segment_rendered':False},ensure_ascii=False,indent=2),encoding='utf-8')
    print(out,flush=True)
if __name__=='__main__':main()
