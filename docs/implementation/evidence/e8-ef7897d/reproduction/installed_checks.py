import json,os,hashlib,re,subprocess,sys
from pathlib import Path
c=json.loads(Path(sys.argv[1]).read_text());E=Path(c['evidence']);installed=json.loads((E/'installed-package.json').read_text());P=Path(installed['path']);mode=sys.argv[2]
folder,count=('tests',127) if mode=='runtime' else ('hooks',9)
argv=[sys.executable,'-B','-m','unittest','discover','-s',str(P/folder),'-p','test_*.py','-v'];env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(P)+os.pathsep+str(P/'tests')}
p=subprocess.run(argv,text=True,capture_output=True,env=env);out=p.stdout+p.stderr;(E/('installed-'+mode+'.txt')).write_text(out);assert p.returncode==0,out[-3000:];actual=int(re.search(r'Ran (\d+) tests',out).group(1));assert actual==count
now={p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in P.rglob('*') if p.is_file()};assert now==installed['files']
(E/('installed-'+mode+'.json')).write_text(json.dumps({'argv':argv,'exit':p.returncode,'tests':actual,'package_unchanged':True,'output_sha256':hashlib.sha256(out.encode()).hexdigest()},indent=2)+'\n');print(json.dumps({'suite':mode,'tests':actual,'exit':0,'installed_package_unchanged':True}))
