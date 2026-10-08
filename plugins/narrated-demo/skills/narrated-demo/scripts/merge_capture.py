"""Merge explicit completed capture prefixes without product hooks."""
import argparse, copy
from pathlib import Path
import pipeline as p
ap=argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("output"); a=ap.parse_args()
spec=p.read(a.spec)
if spec.get("schema_version")!=1 or not spec.get("segments"): raise ValueError("Merge spec v1 required")
out=None; clock=0; provenance=[]
for item in spec["segments"]:
    path=(Path(a.spec).resolve().parent/item["timeline"]).resolve(); raw=p.read(path)
    if raw.get("version")!=1: raise ValueError("Cutaway v1 required")
    n=item.get("completed_steps",len(raw["steps"]))
    if type(n) is not int or not 0<n<=len(raw["steps"]): raise ValueError("Invalid completed prefix")
    steps=raw["steps"][:n]
    if any("expectationEnd" not in s for s in steps): raise ValueError("Prefix contains uncompleted step")
    cutoff=raw["steps"][n]["start"] if n<len(raw["steps"]) else raw["duration"]
    if n==len(raw["steps"]) and raw["status"]!="complete": raise ValueError("Failed tail needs explicit completed prefix")
    if out is None: out={k:copy.deepcopy(raw[k]) for k in ("version","viewport","capture")}
    elif any(out[k]!=raw[k] for k in ("viewport","capture")): raise ValueError("Capture geometry seam mismatch")
    slow=raw.get("slowMotion",[])
    def normalize(value):
        if isinstance(value,list): return [normalize(z) for z in value]
        if isinstance(value,dict):
            return {k:(p.mapped(v,slow)+clock if k in {"t","start","end","readyAt","actionStart","interactionEnd","expectationEnd","approachStart","up","typingStart"} and p.finite(v) else normalize(v)) for k,v in value.items()}
        return value
    out.setdefault("steps",[]).extend(normalize(steps))
    for key in ("frames","points","clicks","cursors","focuses","scrolls","keys","validationMessages"):
        rows=copy.deepcopy([z for z in raw.get(key,[]) if z.get("t",z.get("start",0))<cutoff])
        if key=="frames":
            for z in rows: z["file"]=str((path.parent/z["file"]).resolve())
        out.setdefault(key,[]).extend(normalize(rows))
    provenance.append({"timeline_sha256":p.digest(path),"completed_steps":n,"source_cutoff":cutoff,"offset":clock})
    clock+=p.mapped(cutoff,slow)
out.update(status="complete",duration=clock,slowMotion=[],provenance=provenance)
p.write(a.output,out)
