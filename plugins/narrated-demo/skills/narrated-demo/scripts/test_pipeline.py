"""Small deterministic contract tests; optional external tools set by TEST_CONFIG."""
import copy, json, os, tempfile, unittest
from pathlib import Path
import pipeline as p

class Contracts(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="narrated-demo espaços ação ",dir=os.environ.get("NARRATED_DEMO_TEST_ROOT"))
        self.root=Path(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()
    def config(self):
        c={"schema_version":1,"mode":"tutorial","project":"Other project","module":"Orders","output_dir":"run ação","ffmpeg":"ffmpeg","ffprobe":"ffprobe","voice":"Dora"}
        path=self.root/"config.json"; p.write(path,c); return path
    def test_unicode_json(self):
        c=p.load_config(self.config()); self.assertIn("ação",c["output_dir"])
        bad=self.root/"bad.json"; bad.write_text("{",encoding="utf8")
        with self.assertRaises(ValueError): p.read(bad)
    def test_temporal_precision(self):
        self.assertAlmostEqual(p.mapped(1.237,[{"start":.137,"end":1.237,"factor":4}]),.412)
        self.assertEqual(p.stamp(1.237),"00:00:01,237")
    def test_cursor_transform(self):
        c={"width":1920,"height":1080}; w,h,x,y=p.fit(1440,810,c)
        self.assertEqual(p.pointer_xy(0,0,1440,810,c),(x,y))
        a,b=p.pointer_xy(1439,809,1440,810,c); self.assertLess(a,x+w); self.assertLess(b,y+h)
    def test_resume_corruption_invalidation(self):
        f=self.root/"clip"; f.write_bytes(b"valid"); s=p.signature({"voice":"Dora","text":"a"})
        p.mark(f,s); self.assertTrue(p.cached(f,s))
        self.assertFalse(p.cached(f,p.signature({"voice":"Alex","text":"a"})))
        self.assertFalse(p.cached(f,p.signature({"voice":"Dora","text":"b"})))
        f.write_bytes(b"corrupted"); self.assertFalse(p.cached(f,s))
    def test_missing_tools(self):
        c=p.load_config(self.config()); c["ffmpeg"]="not-an-installed-tool-abc123"
        with self.assertRaises(FileNotFoundError): p.require_tools(c)
    def test_voice_preferences(self):
        c=p.load_config(self.config()); self.assertEqual(p.profile(c)["speaker"],"pf_dora")
        c["voice"]="Alex"; self.assertEqual(p.profile(c)["speaker"],"pm_alex")
        c["voice"]="Faber"
        with self.assertRaises(ValueError): p.profile(c)
    def test_schedule_and_subtitle_change(self):
        original=p.synthesize
        p.synthesize=lambda c,prof,text,out: {"audio":"fictional.wav","duration":.717,"text_tts":text,"sha256":"fixture"}
        try:
            c=p.load_config(self.config()); out=self.root; t={"steps":[{"start":.137,"expectationEnd":2.237}]}
            u={"id":"other-order","chapter":"Example","title":"Save","steps":[0],"grounding":[{"claim":"Fixture saved","status":"confirmed","evidence":"fixture assertion"}]}
            for phase in ("before","during","after"): u[phase]={"text_display":"Texto fictício.","text_tts":"Texto fictício."}
            tl=p.schedule(c,t,[u],out,p.profile(c)); part=tl["parts"][0]
            self.assertGreaterEqual(part["lead"],part["utterances"][0]["end"])
            self.assertEqual(part["source_span"],[.137,2.237])
            old=p.digest(out/"captions.srt"); u["after"]["text_display"]="Resultado fictício alterado."
            p.schedule(c,t,[u],out,p.profile(c)); self.assertNotEqual(old,p.digest(out/"captions.srt"))
            self.assertTrue((out/"captions.vtt").read_text().startswith("WEBVTT"))
        finally: p.synthesize=original
    def test_demo_tutorial_contract(self):
        c=p.load_config(self.config()); c["units"]=str(self.root/"units.json")
        u=p.read(p.ROOT/"assets/units.example.json"); u["units"][0]["before"]={"text_display":"","text_tts":""}; p.write(c["units"],u)
        with self.assertRaises(ValueError): p.units(c,{"steps":[{}]})
        c["mode"]="demo"; self.assertEqual(len(p.units(c,{"steps":[{}]})),1)

if __name__=="__main__": unittest.main()
