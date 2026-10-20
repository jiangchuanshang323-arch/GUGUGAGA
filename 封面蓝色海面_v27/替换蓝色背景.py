from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'封面重绘_渐变右举_v26'
src=(BASE/'合成封面.py').read_text(encoding='utf-8')
src=src.replace("FONT=ROOT.parent", "BASE=ROOT.parent/'封面重绘_渐变右举_v26'\nFONT=ROOT.parent")
src=src.replace("photo=ROOT/'素材'/'太平洋海浪_4941原图.jpg'", "photo=ROOT/'素材'/'蓝海蓝天_备选9386888.jpg'")
src=src.replace('centering=(.5,.48)','centering=(.5,.57)')
src=src.replace("ROOT/'素材'/'艺术字_蓝绿金橙渐变.png'", "BASE/'素材'/'艺术字_蓝绿金橙渐变.png'")
src=src.replace("ROOT/'素材'/'31_企鹅向右上举板.png'", "BASE/'素材'/'31_企鹅向右上举板.png'")
src=src.replace('海洋发烧了_渐变右举封面_v26.png','海洋发烧了_蓝色海面封面_v27.png').replace('封面_手机预览_v26.png','封面_手机预览_v27.png')
src=src.replace("'photo_author':'Andywallxyz'","'photo_author':'Last Stop Okinawa'").replace("'photo_date':'2017-05-22'","'photo_date':'not verified'")
src=src.replace('https://commons.wikimedia.org/wiki/File:Waves_in_the_Pacific_Ocean.jpg','https://www.pexels.com/photo/a-blue-ocean-and-sky-9386888/')
src=src.replace('https://upload.wikimedia.org/wikipedia/commons/4/45/Waves_in_the_Pacific_Ocean.jpg','https://images.pexels.com/photos/9386888/pexels-photo-9386888.jpeg')
src=src.replace("'license':'CC BY 4.0'","'license':'Pexels license'").replace('https://creativecommons.org/licenses/by/4.0/','https://www.pexels.com/license/')
exec(compile(src,str(ROOT/'替换蓝色背景.py'),'exec'),{'__file__':str(ROOT/'替换蓝色背景.py'),'__name__':'__main__'})
