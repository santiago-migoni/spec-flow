import json,re,sys,hashlib
from pathlib import Path
c=json.loads(Path(sys.argv[1]).read_text());P=Path(c['source_package_root']);B=Path(c['disposable_base']);E=Path(c['evidence_directory']);sys.path.insert(0,str(P))
from harness.runtime.contracts import read_document,validate_release
mapping={'constitution':('constitution','constitution-template.md'),'architecture':('design','architecture-template.md'),'structure':('design','structure-template.md'),'roadmap':('roadmap','roadmap-template.md'),'spec':('specify','spec-template.md'),'plan':('plan','plan-template.md'),'tasks':('tasks','tasks-template.md')}
res={}
for label,root in [('fresh',B/'fresh-main'),('negative',B/'negative-main'),('legacy-candidates',B/'legacy-candidates')]:
    docs=[]
    for kind,(skill,name) in mapping.items():
        path=root/('.specs/'+kind+'.md' if kind not in ('spec','plan','tasks') else '.specs/release-v1.2.3/'+kind+'.md')
        actual=path.read_text();template=(P/'skills'/skill/'assets'/name).read_text();read_document(path)
        headings=lambda s:re.findall(r'^## (.+)$',s,re.M)
        tables=lambda s:len(re.findall(r'^\|\s*-{3}',s,re.M))
        assert headings(actual)==headings(template),(kind,headings(actual),headings(template))
        assert tables(actual)==tables(template),(kind,tables(actual),tables(template))
        if kind=='structure':assert 'release.py' in actual and 'test_release.py' in actual and '├──' in actual
        docs.append({'path':str(path.relative_to(root)),'kind':kind,'sections':len(headings(actual)),'tables':tables(actual),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    assert not (root/'.spec-flow').exists()
    checked=validate_release(root,'v1.2.3');assert checked['release']=='v1.2.3',checked
    res[label]={'documents':docs,'valid':True,'no_approvals_or_run':True}
(E/'fixture-shape-independent-check.json').write_text(json.dumps({'fixtures':res,'result':'PASS'},indent=2)+'\n');print('PASS: 21 documents, headings, tables, tree and release contracts before approvals')
