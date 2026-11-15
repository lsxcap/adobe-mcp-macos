#!/usr/bin/env python3
"""Install upstream Adobe MCP servers and a local macOS Illustrator adapter."""
import argparse, hashlib, json, os, pathlib, platform, shutil, subprocess, tempfile, urllib.request, zipfile
ROOT=pathlib.Path.home()/'.local/share/adobe-mcp-macos'
URL='https://github.com/changhaozhang663-shaxia/codex-science-figure-mcp/releases/download/v2026.10.02/Illustrator-MCP-0.2.0-Windows-x64-20261002.zip'
SHA='3f7d0110c0e67c3f155d127eb48fcd25ddbd876b9259072f614fb2904861a82b'
def run(*args): subprocess.run(args,check=True)
def app_path(kind, explicit):
 if explicit:
  p=pathlib.Path(explicit).expanduser()
  if not p.is_dir() or p.suffix!='.app': raise SystemExit('Invalid app bundle')
  return p
 name='Photoshop' if kind=='ps' else 'Illustrator'
 candidates=[p for base in [pathlib.Path('/Applications'),pathlib.Path.home()/'Applications'] for p in base.glob('Adobe '+name+'*/*.app') if 'beta' not in str(p).lower()]
 if len(candidates)!=1: raise SystemExit('Specify --app with the desired Adobe .app path; found: '+str(candidates))
 return candidates[0]
def adapt(root):
 p=root/'src/bridge.mjs';s=p.read_text();a=s.index('    const exe =');b=s.index('    const worker =',a)
 s=s[:a]+"    this.worker = spawn(process.execPath, [fileURLToPath(new URL('./worker-mac.mjs', import.meta.url))], { stdio: ['pipe', 'pipe', 'pipe'] });\n"+s[b:];p.write_text(s)
 shutil.copyfile(pathlib.Path(__file__).with_name('worker-mac.mjs'),root/'src/worker-mac.mjs')
 p=root/'src/tools.mjs';lines=p.read_text().splitlines();p.write_text('\n'.join("export const absolutePath = z.string().min(1).max(32000).refine(p => path.posix.isAbsolute(p) && !/[\\0\\r\\n]/.test(p), 'Use an absolute macOS file path.');" if l.startswith('export const absolutePath =') else l for l in lines)+'\n')
 for p in (root/'src').rglob('*.jsx'): p.write_text(p.read_text().replace('COM / ExtendScript','AppleScript / ExtendScript'))
def main():
 parser=argparse.ArgumentParser();parser.add_argument('product',choices=['ps','ai']);parser.add_argument('--app');parser.add_argument('--check',action='store_true');args=parser.parse_args()
 if platform.system()!='Darwin': raise SystemExit('This installer supports macOS only.')
 node=shutil.which('node');npm=shutil.which('npm');codex=shutil.which('codex')
 if not codex:
  for p in ['/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex','/Applications/Codex.app/Contents/Resources/codex']:
   if pathlib.Path(p).is_file():codex=p;break
 if not all([node,npm,codex]):raise SystemExit('Install Node.js 22+ and Codex first; ensure node/npm are on PATH.')
 if int(subprocess.check_output([node,'--version'],text=True).strip().lstrip('v').split('.')[0])<22:raise SystemExit('Node.js 22+ required')
 app=app_path(args.product,args.app);name='photoshop' if args.product=='ps' else 'illustrator-local'
 print(json.dumps({'product':args.product,'app':str(app),'node':node,'codex':codex},ensure_ascii=False))
 if args.check:return
 existing=subprocess.run([codex,'mcp','get',name],capture_output=True)
 if existing.returncode==0:raise SystemExit('MCP already exists. Existing configuration preserved; inspect it before updating.')
 ROOT.mkdir(parents=True,exist_ok=True);dest=ROOT/args.product
 if dest.exists():raise SystemExit('Install directory exists; inspect before replacing: '+str(dest))
 with tempfile.TemporaryDirectory(prefix='adobe-mcp-') as temp:
  temp=pathlib.Path(temp)
  if args.product=='ps':
   stage=temp/'ps';run(npm,'install','--prefix',str(stage),'@alisaitteke/photoshop-mcp@1.7.38');shutil.move(str(stage),dest)
   entry=dest/'node_modules/@alisaitteke/photoshop-mcp/dist/index.js';env=['--env','PHOTOSHOP_PATH='+str(app),'--env','ANALYTICS_DISABLED=1']
  else:
   archive=temp/'upstream.zip';urllib.request.urlretrieve(URL,archive)
   if hashlib.sha256(archive.read_bytes()).hexdigest()!=SHA:raise SystemExit('Checksum mismatch; stopped')
   with zipfile.ZipFile(archive) as z:
    for member in z.infolist():
     parts=pathlib.PurePosixPath(member.filename).parts
     if '..' in parts or member.filename.startswith('/'):raise SystemExit('Unsafe archive path')
     if 'node_modules' not in parts:z.extract(member,temp)
   stage=temp/'Illustrator-MCP';adapt(stage)
   run(npm,'install','--prefix',str(stage),'--ignore-scripts');shutil.move(str(stage),dest)
   entry=dest/'src/server.mjs';env=['--env','ILLUSTRATOR_APP_PATH='+str(app)]
 run(codex,'mcp','add',name,*env,'--',node,str(entry))
 print('Installed. Restart Codex, start a new conversation, then request a read-only connection check. No documents were edited.')
if __name__=='__main__':main()
