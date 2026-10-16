from pathlib import Path
import re,json,sys
root=Path(sys.argv[1]);pkg=Path(sys.argv[2]);result=[]
lookup={"constitution":("constitution","constitution-template.md"),"architecture":("design","architecture-template.md"),"infrastructure":("design","infrastructure-template.md"),"structure":("design","structure-template.md"),"roadmap":("roadmap","roadmap-template.md"),"spec":("specify","spec-template.md"),"plan":("plan","plan-template.md"),"tasks":("tasks","tasks-template.md")}
for doc in sorted((root/".specs").rglob("*.md")):
 text=doc.read_text();m=re.search(r"^```spec-flow\s*\n(.*?)^```",text,re.M|re.S)
 if not m:continue
 c=json.loads(m.group(1));kind=c["kind"]
 if kind not in lookup:continue
 skill,name=lookup[kind];template=(pkg/"skills"/skill/"assets"/name).read_text()
 required=re.findall(r"^## (.+)$",template,re.M);actual=re.findall(r"^## (.+)$",text,re.M)
 missing=[h for h in required if h not in actual]
 result.append({"document":str(doc.relative_to(root)),"kind":kind,"required_count":len(required),"observed_count":len(actual),"missing_sections":missing})
print(json.dumps({"fixture":str(root),"checks":result,"all_sections_present":all(not r["missing_sections"] for r in result)},indent=2))
sys.exit(0 if all(not r["missing_sections"] for r in result) else 1)
