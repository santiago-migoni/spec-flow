"""Run only deterministic suites; synthetic adapter fixtures do not prove native identity."""
import json,os,pathlib,subprocess,sys,time
c=json.loads(pathlib.Path(sys.argv[1]).read_text());pkg=pathlib.Path(c['source_package_root']);out=pathlib.Path(c['evidence_directory'])/'deterministic';out.mkdir(exist_ok=True)
for name,folder in [('controller','tests'),('hooks','hooks')]:
    cmd=[sys.executable,'-B','-m','unittest','discover','-s',str(pkg/folder),'-p','test_*.py']
    env={**os.environ,'PYTHONPATH':str(pkg),'PYTHONDONTWRITEBYTECODE':'1'}
    start=time.monotonic();p=subprocess.run(cmd,env=env,text=True,capture_output=True)
    (out/(name+'.log')).write_text(p.stdout+p.stderr)
    result={'command':cmd,'PYTHONPATH':str(pkg),'PYTHONDONTWRITEBYTECODE':'1','exit_code':p.returncode,'duration_seconds':time.monotonic()-start}
    (out/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(name,result)
    if p.returncode:sys.exit(p.returncode)
