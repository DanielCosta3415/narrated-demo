"""Sample final-file frames; image extraction is not perceptual approval."""
import argparse, json
from pathlib import Path
import pipeline as p
ap=argparse.ArgumentParser(); ap.add_argument("config"); a=ap.parse_args()
c=p.load_config(a.config); out=Path(c["output_dir"]); video=out/"final.mp4"; timeline=p.read(out/"timeline.json")
root=out/"review"; root.mkdir(exist_ok=True); samples=[]
for i,part in enumerate(timeline["parts"]):
    for label,at in (("before",part["start"]+.2),("result",min(part["start"]+part["lead"]+part["visual_duration"]+.1,part["start"]+part["duration"]-.1))):
        target=root/f"{i:03}-{label}.png"
        p.ff(c,["-ss",at,"-i",video,"-frames:v","1",target],out)
        samples.append({"unit":part["id"],"at":at,"file":str(target),"sha256":p.digest(target)})
p.write(root/"samples.json",{"schema_version":1,"video_sha256":p.digest(video),"config_sha256":p.signature(c),"samples":samples,"status":"not_verified","reason":"Frames extracted; Codex/user must inspect before recording sampled visual review"})
print(root)
