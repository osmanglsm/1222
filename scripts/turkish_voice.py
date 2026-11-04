#!/usr/bin/env python3
"""EMA Lightning Turkish TTS. Generates WAV and word-timing metadata."""
import argparse,json
from pathlib import Path
def generate(script_path,output_dir,speed=0.96):
    from ema_lightning import EMA
    if not 0.75 <= speed <= 1.25: raise ValueError("Invalid speech speed")
    lines=json.loads(Path(script_path).read_text(encoding="utf8"))["lines"]
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    tts=EMA()
    manifest=[]
    for i,line in enumerate(lines):
        path=out/f"{i:02d}_{line['speaker']}.wav"
        speech=tts.say(line["text"],path=str(path),speed=speed,seed=1300+i)
        if speech.duration<=0 or not path.exists():raise RuntimeError(f"Missing speech for line {i}")
        manifest.append({"speaker":line["speaker"],"text":line["text"],"file":path.name,
          "duration":round(float(speech.duration),3),"sample_rate":int(speech.sample_rate),
          "words":[{"text":w.text,"start":round(float(w.start),3),"end":round(float(w.end),3)} for w in speech.words]})
        print(f"{path}: {speech.duration:.2f}s")
    (out/"manifest.json").write_text(json.dumps({"engine":"EMA Lightning","lines":manifest},ensure_ascii=False,indent=2),encoding="utf8")
    return manifest
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--script",default="content/13kat_episode01.json")
    p.add_argument("--output",default="output/13kat_voice")
    p.add_argument("--speed",type=float,default=0.96)
    a=p.parse_args();generate(a.script,a.output,a.speed)
if __name__=="__main__":main()
