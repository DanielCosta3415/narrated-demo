"""Short local E2E + actual resume; no product services are started."""
import argparse, copy
from pathlib import Path
import pipeline as p
ap=argparse.ArgumentParser(); ap.add_argument("config"); a=ap.parse_args()
c=p.load_config(a.config); out=Path(c["output_dir"])
cmd=[__import__("sys").executable,str(Path(__file__).with_name("pipeline.py")),"build",str(Path(a.config).resolve())]
p.execute(cmd)
files=[out/"source.mp4",*out.glob("clip-*.mp4"),*out.glob("audio/*.wav")]
before={str(z):(p.digest(z),z.stat().st_mtime_ns) for z in files}
p.execute(cmd)
after={str(z):(p.digest(z),z.stat().st_mtime_ns) for z in files}
assert before==after,"Valid stage outputs not reused"
qa=p.read(out/"qa.json"); assert qa["sha256"]==p.digest(out/"final.mp4")
assert qa["config_sha256"]==p.signature(c)
assert qa["perceptual_listening"]["status"]=="not_verified"
assert qa["user_approval"]["status"]=="not_verified"
missing=copy.deepcopy(c); missing["model"]=str(out/"missing-model.onnx")
try: p.require_tools(missing,True)
except FileNotFoundError: pass
else: raise AssertionError("Missing model must fail")
wrong=copy.deepcopy(p.read(out/"timeline.json")); wrong["speech"][0]["end"]=wrong["duration"]+10
try: p.validate(c,out/"final.mp4",wrong,out/"invalid-qa.json")
except ValueError: pass
else: raise AssertionError("Invalid timing accepted")
changed=p.signature({"voice":"Alex","text":"new"}); assert not p.cached(files[0],changed)
p.write(out/"integration-tests.json",{"schema_version":1,"status":"pass","resume_preserved_stage_hashes_and_mtimes":True,"missing_model":"pass","invalid_timing":"pass","qa_exact_final_hash":"pass","unavailable_reviews_remain_not_verified":True,"output_sha256":p.digest(out/"final.mp4")})
print("Short E2E and resume passed")
