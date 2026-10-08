"""Record hashes and comparison of original v5 sources, without modifying them."""
import argparse, hashlib, json
from pathlib import Path
ap=argparse.ArgumentParser()
ap.add_argument("temporary"); ap.add_argument("preserved"); ap.add_argument("destination")
a=ap.parse_args(); result=[]
for name in ("v5_build.py","v5_merge.py","v5_review.py","v5_voice.py","v5_critical.py"):
    temp=Path(a.temporary)/name; other=Path(a.preserved)/name
    h=lambda path:hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    result.append({"file":name,"temporary_sha256":h(temp),"preserved_sha256":h(other),"same":h(temp)==h(other)})
Path(a.destination).write_text(json.dumps(result,indent=2),encoding="utf8")
