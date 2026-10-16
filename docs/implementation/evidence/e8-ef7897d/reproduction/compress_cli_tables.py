"""Losslessly preserve raw padded CLI tables without text-format alterations."""
import gzip,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];records=[]
for name in ('installed-list','plugins-before','plugins-after'):
    p=E/(name+'.txt');raw=p.read_bytes();target=E/(name+'.txt.gz');target.write_bytes(gzip.compress(raw,mtime=0));assert gzip.decompress(target.read_bytes())==raw
    records.append({'file':target.name,'uncompressed_original_name':p.name,'uncompressed_bytes':len(raw),'uncompressed_sha256':hashlib.sha256(raw).hexdigest(),'compressed_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'exact_roundtrip':True});p.unlink()
(E/'cli-output-preservation.json').write_text(json.dumps({'reason':'Raw CLI tables include trailing alignment padding. Lossless gzip preserves original bytes without editing the output.','records':records},indent=2)+'\n');print('Preserved three raw CLI tables byte-exactly in gzip archives')
