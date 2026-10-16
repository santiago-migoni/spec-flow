import hashlib,json,os,re,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parents[1];c=json.loads((E/'package-comparison.json').read_text());P=Path(c['frozen_test_package']);mode=sys.argv[1];folder,count=('tests',127) if mode=='runtime' else ('hooks',9)
argv=[sys.executable,'-B','-m','unittest','discover','-s',str(P/folder),'-p','test_*.py','-v'];p=subprocess.run(argv,text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(P)+os.pathsep+str(P/'tests')});output=p.stdout+p.stderr;(E/(mode+'.txt')).write_text(output)
assert p.returncode==0,output[-3000:];assert int(re.search(r'Ran (\d+) tests',output).group(1))==count
assert {x.relative_to(P).as_posix():hashlib.sha256(x.read_bytes()).hexdigest() for x in P.rglob('*') if x.is_file()}==c['package_files']
(E/(mode+'.json')).write_text(json.dumps({'argv':argv,'version':'3.0.0','tests':count,'exit':p.returncode,'output_sha256':hashlib.sha256(output.encode()).hexdigest(),'frozen_package_unchanged':True,'result':'PASS'},indent=2)+'\n');print(json.dumps({'suite':mode,'tests':count,'version':'3.0.0','exit':p.returncode,'package_unchanged':True}))
