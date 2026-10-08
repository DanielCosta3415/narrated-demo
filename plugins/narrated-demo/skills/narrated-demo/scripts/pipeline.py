"""Narrated Demo v1: deterministic local synthesis, timing, composition and QA.
Extracted/generalized from the inspected v5 pipeline; no product commands/APIs.
"""
import argparse, bisect, copy, hashlib, json, math, os, re, shutil
import subprocess, sys, tempfile, textwrap, time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
MODES = {"demo", "tutorial", "revise-narration", "select-voice", "resume", "validate"}
def read(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        raise ValueError(f"Invalid JSON/file {path}: {e}") from e
def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""): h.update(block)
    return h.hexdigest()
def signature(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name+".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)
def execute(args, cwd=None):
    result = subprocess.run(list(map(str,args)), cwd=cwd, capture_output=True, encoding="utf-8", errors="replace")
    if result.returncode: raise RuntimeError(f"Command failed: {Path(args[0]).name}: {result.stderr[-4000:]}")
    return result
def finite(x): return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
def load_config(path):
    path = Path(path).resolve(); c = read(path)
    if c.get("schema_version") != 1 or c.get("mode") not in MODES: raise ValueError("Unsupported schema/mode")
    for k in ("output_dir","project","module","ffmpeg","ffprobe","voice"):
        if not isinstance(c.get(k),str) or not c[k]: raise ValueError(f"Missing config {k}")
    for k,d in (("width",1920),("height",1080),("fps",60)):
        c.setdefault(k,d)
        if type(c[k]) is not int or c[k]<=0: raise ValueError(f"Invalid {k}")
    if c["width"]%2 or c["height"]%2: raise ValueError("H264 dimensions must be even")
    for k in ("output_dir","recording","units","model","voices"):
        if k in c: c[k] = str((path.parent/c[k]).resolve())
    for k in ("ffmpeg","ffprobe"):
        if "/" in c[k] or "\\" in c[k]: c[k] = str((path.parent/c[k]).resolve())
    c.setdefault("subtitle_mode","burned-in")
    if c["subtitle_mode"] not in {"external","selectable","burned-in","both"}: raise ValueError("subtitle mode")
    c.setdefault("font","Segoe UI"); c.setdefault("font_size",30)
    if not re.fullmatch(r"[\w .-]+",c["font"]): raise ValueError("Unsupported font name")
    c.setdefault("lufs",-16); c.setdefault("true_peak",-1); c.setdefault("lexicon",{})
    c.setdefault("crf",18); c.setdefault("preset","veryfast")
    c.setdefault("profile_overrides",{})
    if not finite(c["lufs"]) or not -40<=c["lufs"]<=-5: raise ValueError("lufs")
    if not finite(c["true_peak"]) or not -9<=c["true_peak"]<=0: raise ValueError("true_peak")
    return c
def profile(c):
    p=copy.deepcopy(read(ROOT/"assets/voices.json")["profiles"].get(c["voice"]))
    if not p: raise ValueError("Choose Dora or Alex; no implicit substitute")
    allowed={"speed","trim","sentence_pause","clause_pause","lang"}
    if set(c["profile_overrides"])-allowed: raise ValueError("Unsupported profile override")
    p.update(c["profile_overrides"])
    if not finite(p["speed"]) or not .5<=p["speed"]<=2: raise ValueError("voice speed")
    return p
def require_tools(c, models=False):
    for k in ("ffmpeg","ffprobe"):
        if not shutil.which(c[k]) and not Path(c[k]).is_file(): raise FileNotFoundError(f"{k} missing; set explicit executable")
        execute([c[k],"-version"])
    if models:
        for k in ("model","voices"):
            if not Path(c.get(k,"")).is_file(): raise FileNotFoundError(f"{k} missing; configure external model file")
        expected=read(ROOT/"assets/voices.json")
        for k in ("model","voices"):
            if digest(c[k])!=expected[k+"_sha256"]: raise ValueError(f"{k} hash differs from approved v1.0; review/update profile explicitly")
def mapped(t, slow):
    return t-sum(max(0,min(t,s["end"])-s["start"])*(1-1/s["factor"]) for s in slow)
def capture(c):
    raw=read(c["recording"])
    if raw.get("version")!=1 or raw.get("status")!="complete": raise ValueError("Only completed Cutaway v1 timeline accepted")
    t=copy.deepcopy(raw); slow=t.get("slowMotion",[])
    if not finite(t.get("duration")) or t["duration"]<=0: raise ValueError("capture duration")
    end=-1
    for s in slow:
        if not all(finite(s.get(k)) for k in ("start","end","factor")) or not end<=s["start"]<s["end"]<=t["duration"] or s["factor"]<1: raise ValueError("Invalid slowdown")
        end=s["end"]
    base=Path(c["recording"]).parent
    for key in ("frames","points","clicks","cursors"):
        rows=t.get(key,[]); prev=-1
        for row in rows:
            if not finite(row.get("t")) or not prev<=row["t"]<=t["duration"]: raise ValueError(f"Nonmonotonic {key}")
            prev=row["t"]; row["t"]=mapped(row["t"],slow)
            if key=="frames":
                row["file"]=str((base/row["file"]).resolve())
                if not Path(row["file"]).is_file(): raise FileNotFoundError(row["file"])
    if not t.get("frames") or not t.get("points"): raise ValueError("Frames and pointer trace required")
    vw,vh=t["viewport"]["width"],t["viewport"]["height"]
    for p in t["points"]+t.get("clicks",[]):
        if not all(finite(p.get(k)) for k in ("x","y")) or not 0<=p["x"]<vw or not 0<=p["y"]<vh: raise ValueError("Pointer out of viewport")
    for s in t["steps"]:
        if not all(finite(s.get(k)) for k in ("start","expectationEnd")) or not 0<=s["start"]<=s["expectationEnd"]<=t["duration"]: raise ValueError("Incomplete step")
        s["start"]=mapped(s["start"],slow); s["expectationEnd"]=mapped(s["expectationEnd"],slow)
    t["duration"]=mapped(t["duration"],slow); t["slowMotion"]=[]; return t
def units(c,t):
    doc=read(c["units"])
    if doc.get("schema_version")!=1 or not doc.get("units"): raise ValueError("Units schema")
    ids=set()
    for u in doc["units"]:
        if not isinstance(u.get("id"),str) or u["id"] in ids: raise ValueError("Duplicate/invalid ID")
        ids.add(u["id"])
        if not all(isinstance(u.get(k),str) and u[k] for k in ("chapter","title")): raise ValueError("Unit headings")
        ix=u.get("steps",[])
        if not ix or any(type(i) is not int or not 0<=i<len(t["steps"]) for i in ix) or ix!=sorted(set(ix)): raise ValueError("Step references")
        for phase in ("before","during","after"):
            for key in ("text_display","text_tts"):
                if not isinstance(u.get(phase,{}).get(key),str): raise ValueError("Narration contract")
            if c["mode"]=="tutorial" and phase!="during" and not u[phase]["text_display"]: raise ValueError("Tutorial before/after required")
        if not u.get("grounding"): raise ValueError("Grounding required")
        for g in u["grounding"]:
            if g.get("status") not in {"confirmed","supported_with_limits","unverified"} or not g.get("claim") or not g.get("evidence"): raise ValueError("Grounding contract")
    for item in c.get("coverage",[]):
        if item.get("status") not in {"demonstrated","blocked","not_implemented","out_of_scope","not_applicable"}: raise ValueError("Coverage status")
        if item["status"]=="demonstrated" and (not item.get("evidence") or not set(item["evidence"])<=ids): raise ValueError("Coverage references")
    return doc["units"]
def cached(path,sig):
    side=Path(str(path)+".cache.json")
    if not Path(path).is_file() or not side.is_file(): return False
    data=read(side); return data.get("signature")==sig and data.get("sha256")==digest(path)
def mark(path,sig): write(str(path)+".cache.json",{"signature":sig,"sha256":digest(path)})
def synthesize(c,p,text,out):
    import importlib.metadata as md
    import soundfile as sf
    from kokoro_onnx import Kokoro
    if md.version("kokoro-onnx") != p["engine_version"]:
        raise ValueError("Kokoro runtime differs from approved profile; review profile before synthesis")
    spoken=text
    for a,b in c["lexicon"].items(): spoken=spoken.replace(a,b)
    sig=signature({"profile":p,"model":digest(c["model"]),"voices":digest(c["voices"]),"text":spoken})
    target=out/"audio"/(sig+".wav"); target.parent.mkdir(exist_ok=True)
    if not cached(target,sig):
        if not hasattr(synthesize,"engines"): synthesize.engines={}
        key=(c["model"],c["voices"])
        if key not in synthesize.engines: synthesize.engines[key]=Kokoro(*key)
        audio,sr=synthesize.engines[key].create(spoken,p["speaker"],speed=p["speed"],lang=p["lang"],trim=p["trim"],sentence_pause=p["sentence_pause"],clause_pause=p["clause_pause"])
        temp=target.with_suffix(".tmp.wav"); sf.write(temp,audio,sr,subtype="FLOAT"); temp.replace(target); mark(target,sig)
    audio,sr=sf.read(target)
    return {"audio":str(target),"duration":len(audio)/sr,"text_tts":spoken,"sha256":digest(target)}
def stamp(t,vtt=False):
    n=round(t*1000); return f"{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02}{'.' if vtt else ','}{n%1000:03}"
def ast(t):
    n=round(t*100); return f"{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}"
def ass_header(c):
    return ["[Script Info]","ScriptType: v4.00+","PlayResX: "+str(c["width"]),"PlayResY: "+str(c["height"]),"[V4+ Styles]","Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",f"Style: Default,{c['font']},{c['font_size']},&H00FFFFFF,&H00FFFFFF,&H00111111,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,80,80,12,1","[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
def fit(vw,vh,c):
    # Full viewport aspect fit; room reserved for header/captions.
    top=round(c["height"]*60/1080); bottom=round(c["height"]*84/1080)
    s=min(c["width"]/vw,(c["height"]-top-bottom)/vh)
    w=int(vw*s)//2*2; h=int(vh*s)//2*2
    return w,h,(c["width"]-w)//2,top+(c["height"]-top-bottom-h)//2
def pointer_xy(x,y,vw,vh,c):
    w,h,px,py=fit(vw,vh,c); return px+x*w/vw,py+y*h/vh
def schedule(c,t,us,out,p):
    parts=[]; speech=[]; captions=[]; clock=0
    q=lambda x: math.ceil(x*c["fps"])/c["fps"]
    for u in us:
        begin=t["steps"][u["steps"][0]]["start"]; end=t["steps"][u["steps"][-1]]["expectationEnd"]
        visual=q(max(1/c["fps"],end-begin))
        voices={}
        for phase in ("before","during","after"):
            d=u[phase]
            if d["text_tts"]:
                a=synthesize(c,p,d["text_tts"],out); a.update(text=d["text_display"],window=max(a["duration"],len(d["text_display"])/17,1.3)); voices[phase]=a
        if not voices: raise ValueError("Empty narration")
        bw=voices.get("before",{}).get("window",0); dw=voices.get("during",{}).get("window",0)
        lead=q(.15+bw+.15)
        during=lead+q((visual-dw)/2) if visual-dw>4 else lead+.1
        after=max(lead+visual+.18,during+dw+.18 if dw else 0)
        offsets={"before":.15,"during":during,"after":after}
        duration=q(max(offsets[k]+a["window"] for k,a in voices.items())+.25)
        part={"id":u["id"],"chapter":u["chapter"],"title":u["title"],"start":clock,"duration":duration,"source_span":[begin,end],"lead":lead,"visual_duration":visual,"utterances":[],"grounding":u["grounding"]}
        for k,a in voices.items():
            a=dict(a,phase=k,start=clock+offsets[k],end=clock+offsets[k]+a["duration"])
            part["utterances"].append(a); speech.append(a)
            lines=textwrap.wrap(a["text"],width=43,break_long_words=False)
            if any(len(l)>43 for l in lines): raise ValueError("Caption word too long; rewrite")
            chunks=["\n".join(lines[i:i+2]) for i in range(0,len(lines),2)]
            pos=a["start"]; weight=sum(map(len,chunks))
            for ch in chunks:
                delta=a["window"]*len(ch)/weight; captions.append({"start":pos,"end":pos+delta,"text":ch}); pos+=delta
        parts.append(part); clock+=duration
    for rows in (speech,captions):
        if any(rows[i]["end"]>rows[i+1]["start"]+.001 for i in range(len(rows)-1)): raise ValueError("Speech/caption overlap")
    timeline={"schema_version":1,"duration":clock,"parts":parts,"speech":speech,"captions":captions}
    write(out/"timeline.json",timeline)
    for ext in ("srt","vtt"):
        blocks=[f"{i+1}\n{stamp(z['start'],ext=='vtt')} --> {stamp(z['end'],ext=='vtt')}\n{z['text']}" for i,z in enumerate(captions)]
        (out/f"captions.{ext}").write_text(("WEBVTT\n\n" if ext=="vtt" else "")+"\n\n".join(blocks),encoding="utf-8")
    return timeline
def ff(c,args,out): return execute([c["ffmpeg"],"-y","-hide_banner","-loglevel","error",*args],out)
def encode_opts(c): return ["-c:v","libx264","-preset",c["preset"],"-crf",c["crf"],"-pix_fmt","yuv420p","-threads","2"]
def concat_line(path):
    p=str(path).replace("\\","/")
    if "\n" in p or "\r" in p: raise ValueError("Concat path newline unsupported")
    return "file '"+p.replace("'", "'\\''")+"'"
def source(c,t,out):
    from PIL import Image
    frames=t["frames"]; vw,vh=t["viewport"]["width"],t["viewport"]["height"]
    actual=Image.open(frames[0]["file"]).size
    expected=(round(vw*t["capture"]["scale"]),round(vh*t["capture"]["scale"]))
    if actual!=expected: raise ValueError("Capture scale does not match PNG dimensions")
    sig=signature({"capture":digest(c["recording"]),"frames":[digest(f["file"]) for f in frames],"geometry":fit(vw,vh,c),"fps":c["fps"],"codec":encode_opts(c),"renderer":digest(__file__)})
    target=out/"source.mp4"
    if cached(target,sig): return target
    lines=[]
    for i,fr in enumerate(frames):
        end=frames[i+1]["t"] if i+1<len(frames) else t["duration"]
        if end>fr["t"]: lines += [concat_line(fr["file"]),"option framerate 1000",f"duration {end-fr['t']:.9f}"]
    lines += [concat_line(frames[-1]["file"]),"option framerate 1000"]
    (out/"frames.txt").write_text("\n".join(lines),encoding="utf-8")
    w,h,x,y=fit(vw,vh,c); ass=ass_header(c); pts=t["points"]; times=[z["t"] for z in pts]; kinds=t.get("cursors",[]); kt=[z["t"] for z in kinds]
    for n in range(math.ceil(t["duration"]*c["fps"])):
        a=n/c["fps"]; b=min(t["duration"],(n+1)/c["fps"]); ix=max(0,bisect.bisect_right(times,a)-1); z=pts[ix]; px,py=z["x"],z["y"]
        if ix+1<len(pts) and times[ix+1]>times[ix]:
            ratio=min(1,max(0,(a-times[ix])/(times[ix+1]-times[ix]))); px+=(pts[ix+1]["x"]-px)*ratio; py+=(pts[ix+1]["y"]-py)*ratio
        px,py=pointer_xy(px,py,vw,vh,c); ci=bisect.bisect_right(kt,a)-1
        drawing="m 0 0 l 0 25 7 19 13 31 18 28 12 17 23 17 0 0"
        if ci>=0 and kinds[ci]["type"]=="text": drawing="m 0 0 l 12 0 12 3 8 3 8 24 12 24 12 27 0 27 0 24 4 24 4 3 0 3 0 0"
        ass.append(f"Dialogue: 2,{ast(a)},{ast(b)},Default,,0,0,0,,{{\\an7\\pos({px:.2f},{py:.2f})\\p1}}"+drawing)
    for z in t.get("clicks",[]):
        x1,y1=pointer_xy(z["x"],z["y"],vw,vh,c); a=z["t"]
        ass.append(f"Dialogue: 1,{ast(a)},{ast(min(t['duration'],a+.3))},Default,,0,0,0,,{{\\an7\\pos({x1-16:.2f},{y1-16:.2f})\\1c&HFFAA33&\\1a&HBB&\\p1\\fad(0,250)}}m 16 0 b 25 0 32 7 32 16 b 32 25 25 32 16 32 b 7 32 0 25 0 16 b 0 7 7 0 16 0")
    (out/"pointer.ass").write_text("\n".join(ass),encoding="utf-8")
    temp=out/"source.new.mp4"
    ff(c,["-f","concat","-safe","0","-i","frames.txt","-vf",f"scale={w}:{h},pad={c['width']}:{c['height']}:{x}:{y}:color=0x122b49,fps={c['fps']},ass=pointer.ass","-t",t["duration"],*encode_opts(c),temp],out)
    temp.replace(target); mark(target,sig); return target
def measure(c,path):
    result=execute([c["ffmpeg"],"-hide_banner","-i",path,"-vn","-af",f"loudnorm=I={c['lufs']}:TP={c['true_peak']}:LRA=11:print_format=json","-f","null","-"])
    text=result.stderr; return json.loads(text[text.rfind("{"):text.rfind("}")+1])
def render(c,t,tl,out):
    import numpy as np
    import soundfile as sf
    master=source(c,t,out); clips=[]
    for i,p in enumerate(tl["parts"]):
        clip=out/f"clip-{i:03}.mp4"; sig=signature({"source":digest(master),"part":{k:p[k] for k in ("source_span","lead","duration")},"codec":encode_opts(c)})
        if not cached(clip,sig):
            a,b=p["source_span"]
            vf=f"trim=duration={max(1/c['fps'],b-a)},setpts=PTS-STARTPTS,fps={c['fps']},tpad=start_mode=clone:start_duration={p['lead']}:stop_mode=clone:stop_duration={p['duration']},trim=duration={p['duration']}"
            temp=clip.with_suffix(".new.mp4"); ff(c,["-ss",a,"-i",master,"-vf",vf,"-an","-frames:v",round(p["duration"]*c["fps"]),*encode_opts(c),temp],out); temp.replace(clip); mark(clip,sig)
        clips.append(clip)
    (out/"clips.txt").write_text("\n".join(concat_line(z) for z in clips),encoding="utf-8")
    ff(c,["-f","concat","-safe","0","-i","clips.txt","-c","copy","master.new.mp4"],out)
    (out/"master.new.mp4").replace(out/"master.mp4")
    mix=np.zeros(round(tl["duration"]*48000),dtype=np.float32)
    for s in tl["speech"]:
        target=Path(s["audio"]).with_suffix(".48k.wav")
        sig=signature({"audio":s["sha256"],"sr":48000})
        if not cached(target,sig): ff(c,["-i",s["audio"],"-ar","48000","-ac","1","-c:a","pcm_f32le",target],out); mark(target,sig)
        data,_=sf.read(target); at=round(s["start"]*48000)
        if at+len(data)>len(mix): raise ValueError("Audio would truncate")
        mix[at:at+len(data)]=data
    sf.write(out/"native.wav",mix,48000,subtype="FLOAT"); m=measure(c,out/"native.wav")
    # Leave codec headroom, then enforce requested ceiling on decoded AAC.
    filt=f"loudnorm=I={c['lufs']}:TP={c['true_peak']-.5}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=false"
    ff(c,["-i","native.wav","-af",filt,"-ar","48000","-c:a","pcm_s16le","narration.wav"],out)
    ass=ass_header(c)
    for z in tl["captions"]:
        text=z["text"].replace("{","").replace("}","").replace("\\","").replace("\n","\\N")
        ass.append(f"Dialogue: 0,{ast(z['start'])},{ast(z['end'])},Default,,0,0,0,,"+text)
    (out/"captions.ass").write_text("\n".join(ass),encoding="utf-8")
    args=["-i","master.mp4","-i","narration.wav"]
    selectable=c["subtitle_mode"] in {"selectable","both"}
    if selectable: args+=["-i","captions.srt"]
    args+=["-map","0:v","-map","1:a"]
    if selectable: args+=["-map","2:0","-c:s","mov_text"]
    if c["subtitle_mode"] in {"burned-in","both"}: args+=["-vf","ass=captions.ass",*encode_opts(c)]
    else: args+=["-c:v","copy"]
    ff(c,[*args,"-c:a","aac","-b:a","192k","final.new.mp4"],out)
    # QA before replacing last valid final.
    validate(c,out/"final.new.mp4",tl,out/"qa.new.json")
    (out/"final.new.mp4").replace(out/"final.mp4"); qa=read(out/"qa.new.json"); qa["output"]=str(out/"final.mp4"); write(out/"qa.json",qa)
    return out/"final.mp4"
def validate(c,path,tl,target):
    for part in tl["parts"]:
        preparatory=[u for u in part["utterances"] if u["phase"]=="before"]
        if preparatory and preparatory[0]["end"] > part["start"]+part["lead"]+.001:
            raise ValueError("Action precedes preparatory narration")
    require_tools(c); ff(c,["-threads","2","-i",path,"-map","0:v","-map","0:a","-f","null","-"],Path(path).parent)
    info=json.loads(execute([c["ffprobe"],"-v","error","-show_streams","-show_format","-of","json",path]).stdout)
    v=next(z for z in info["streams"] if z["codec_type"]=="video")
    if (v["width"],v["height"])!=(c["width"],c["height"]): raise ValueError("Resolution mismatch")
    if abs(float(info["format"]["duration"])-tl["duration"])>.2: raise ValueError("Duration mismatch")
    frames=json.loads(execute([c["ffprobe"],"-v","error","-select_streams","v:0","-show_frames","-show_entries","frame=best_effort_timestamp_time","-of","json",path]).stdout)["frames"]
    pts=[float(z["best_effort_timestamp_time"]) for z in frames]
    if len(pts)<2 or any(abs(b-a-1/c["fps"])>1e-5 for a,b in zip(pts,pts[1:])): raise ValueError("Decoded cadence mismatch")
    for key in ("speech","captions"):
        rows=tl[key]
        if any(z["start"]<0 or z["end"]<=z["start"] or z["end"]>tl["duration"]+.001 for z in rows): raise ValueError("Invalid windows")
        if any(a["end"]>b["start"]+.001 for a,b in zip(rows,rows[1:])): raise ValueError("Overlap")
    m=measure(c,path)
    if abs(float(m["input_i"])-c["lufs"])>1 or float(m["input_tp"])>c["true_peak"]: raise ValueError("Loudness mismatch")
    qa={"schema_version":1,"output":str(path),"sha256":digest(path),"config_sha256":signature(c),"timeline_sha256":signature(tl),"verified_at":datetime.now(timezone.utc).isoformat(),"technical":{"status":"pass","decode":"pass","decoded_frames":len(pts),"cadence":"pass","metadata":info,"loudness":m},"visual_sampling":{"status":"not_verified"},"continuous_audiovisual":{"status":"not_verified"},"perceptual_listening":{"status":"not_verified"},"user_approval":{"status":"not_verified"}}
    write(target,qa); return qa
def environment(c):
    import importlib.metadata as md
    versions={k:execute([c[k],"-version"]).stdout.splitlines()[0] for k in ("ffmpeg","ffprobe")}
    for name in ("kokoro-onnx","soundfile","numpy","Pillow","onnxruntime"):
        try: versions[name]=md.version(name)
        except md.PackageNotFoundError: versions[name]="missing"
    return {"python":sys.version,"executables":{k:c[k] for k in ("ffmpeg","ffprobe")},"versions":versions}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("command",choices=["build","validate","sample","doctor"]); ap.add_argument("config"); a=ap.parse_args()
    c=load_config(a.config); require_tools(c,a.command in {"build","sample"}); out=Path(c["output_dir"]); out.mkdir(parents=True,exist_ok=True)
    if a.command=="doctor": print(json.dumps(environment(c),indent=2)); return
    if a.command=="validate": validate(c,out/"final.mp4",read(out/"timeline.json"),out/"qa.json"); return
    if a.command=="build" and c["mode"] in {"validate","select-voice"}:
        raise ValueError("Use validate/sample command for the chosen non-build mode")
    p=profile(c); write(out/"resolved-config.json",dict(c,resolved_profile=p))
    if a.command=="sample":
        text=c.get("sample_text",f"Olá, o meu nome é {p['display_name']}. Neste vídeo apresentarei um sistema de exemplo.")
        print(json.dumps(synthesize(c,p,text,out),ensure_ascii=False)); return
    t=capture(c); us=units(c,t); tl=schedule(c,t,us,out,p); final=render(c,t,tl,out)
    manifest={"schema_version":1,"stage":"complete","status":"pass","environment":environment(c),"config":c,"resolved_profile":p,"inputs":{k:digest(c[k]) for k in ("recording","units","model","voices")},"script_sha256":digest(__file__),"output":str(final),"output_sha256":digest(final),"capture_origin":"CDP variable cadence, pointer reconstructed at output cadence","coverage":c.get("coverage",[]),"command":["python","pipeline.py","build",str(Path(a.config).resolve())]}
    write(out/"manifest.json",manifest); print(str(final))
if __name__=="__main__":
    try: main()
    except Exception as e: print(f"{type(e).__name__}: {e}",file=sys.stderr); sys.exit(1)
