from pathlib import Path
import sys,json,subprocess,hashlib,shutil,re,argparse

ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
sys.path.insert(0,str(PROJECT/'ocean_animation_demo_20261011'/'runtime'))
import imageio_ffmpeg
EXE=imageio_ffmpeg.get_ffmpeg_exe()
MANIFEST=ROOT/'视频清单.json'

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):
 r=subprocess.run([EXE,'-hide_banner','-i',str(p)],capture_output=True)
 s=r.stderr.decode('utf-8','replace');m=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',s)
 assert m,s
 h,mi,sec=map(float,m.groups())
 return {'seconds':h*3600+mi*60+sec,'sha256':digest(p),'bytes':Path(p).stat().st_size}
def decode(p):
 r=subprocess.run([EXE,'-v','error','-i',str(p),'-f','null','-'],capture_output=True)
 assert r.returncode==0 and not r.stderr,r.stderr
def commit(tmp,dest):
 assert tmp.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve())
 decode(tmp);tmp.replace(dest)
def copy_exact(src,dest):
 dest.parent.mkdir(parents=True,exist_ok=True);tmp=dest.with_name('.'+dest.stem+'.pending.mp4')
 shutil.copy2(src,tmp);assert digest(src)==digest(tmp);commit(tmp,dest)
def merge(inputs,dest,trim_start_seconds=0):
 assert 0<=float(trim_start_seconds)<86400
 dest.parent.mkdir(parents=True,exist_ok=True);tmp=dest.with_name('.'+dest.stem+'.pending.mp4')
 args=[EXE,'-v','error','-y'];graph=[]
 for i,path in enumerate(inputs):
  args+=['-i',str(path)]
  graph.extend([f'[{i}:v]fps=24,setsar=1,setpts=PTS-STARTPTS[v{i}]',f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a{i}]'])
 graph.append(''.join(f'[v{i}][a{i}]' for i in range(len(inputs)))+f'concat=n={len(inputs)}:v=1:a=1[joined][acat]')
 graph.append(f'[joined]trim=start={float(trim_start_seconds)},setpts=PTS-STARTPTS,fps=24,setpts=N/(24*TB)[v]')
 graph.append(f'[acat]atrim=start={float(trim_start_seconds)},asetpts=PTS-STARTPTS[a]')
 args+=['-filter_complex',';'.join(graph),'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(tmp)]
 subprocess.run(args,check=True);commit(tmp,dest)
def write_manifest(data):MANIFEST.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def initialize():
 raise RuntimeError('交付清单已存在；请按内容本名使用 update / update_many。')

def update(key,src):
 data=json.loads(MANIFEST.read_text(encoding='utf-8'));assert key in data['segments'],list(data['segments'])
 src=Path(src).resolve();dest=ROOT/data['segments'][key]['path'];assert src!=dest.resolve()
 # Prepare the replacement and every affected merge before publishing any file.
 replacement=dest.with_name('.'+dest.stem+'.replacement.mp4');copy_exact(src,replacement)
 affected=[]
 for merge_key,entry in data['merges'].items():
  if key in entry['segments']:
   target=ROOT/entry['path'];pending=target.with_name('.'+target.stem+'.replacement.mp4')
   merge([replacement if k==key else ROOT/data['segments'][k]['path'] for k in entry['segments']],pending,entry.get('trim_start_seconds',0))
   affected.append((merge_key,pending,target))
 commit(replacement,dest);data['segments'][key].update(info(dest))
 for merge_key,pending,target in affected:commit(pending,target);data['merges'][merge_key].update(info(target))
 # Newly rendered handoff files are temporary once the fixed delivery is verified.
 if src.is_relative_to(PROJECT.resolve()) and not src.is_relative_to(ROOT.resolve()) and src.parent.name=='交付':
  assert digest(src)==digest(dest)
  data.setdefault('replaced_render_copies_removed',[]).append({'path':str(src),'sha256':digest(src)})
  src.unlink()
 write_manifest(data)
 print('Replaced',key,'and merges',[k for k,_,_ in affected],flush=True)

def update_many(pairs):
 data=json.loads(MANIFEST.read_text(encoding='utf-8'));staged={};sources={}
 for key,source in pairs:
  assert key in data['segments'] and key not in staged,key
  source=Path(source).resolve();dest=ROOT/data['segments'][key]['path'];assert source!=dest.resolve()
  replacement=dest.with_name('.'+dest.stem+'.replacement.mp4');copy_exact(source,replacement);staged[key]=replacement;sources[key]=source
 affected=[]
 for name,entry in data['merges'].items():
  if any(key in staged for key in entry['segments']):
   target=ROOT/entry['path'];replacement=target.with_name('.'+target.stem+'.replacement.mp4')
   merge([staged.get(key,ROOT/data['segments'][key]['path']) for key in entry['segments']],replacement,entry.get('trim_start_seconds',0));affected.append((name,replacement,target))
 for key,replacement in staged.items():
  dest=ROOT/data['segments'][key]['path'];commit(replacement,dest);data['segments'][key].update(info(dest))
 for name,replacement,target in affected:commit(replacement,target);data['merges'][name].update(info(target))
 for key,source in sources.items():
  if source.is_relative_to(PROJECT.resolve()) and not source.is_relative_to(ROOT.resolve()) and source.parent.name=='交付':
   assert digest(source)==digest(ROOT/data['segments'][key]['path']);source.unlink()
 write_manifest(data);print('Replaced segments',list(staged),'and merges',[a[0] for a in affected],flush=True)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--init',action='store_true');parser.add_argument('--update',nargs=2,metavar=('SEGMENT_KEY','NEW_MP4'));parser.add_argument('--update-many',nargs='+');args=parser.parse_args()
 if args.init:initialize()
 elif args.update:update(*args.update)
 elif args.update_many:
  assert len(args.update_many)%2==0
  update_many(list(zip(args.update_many[::2],args.update_many[1::2])))
 else:parser.print_help()
