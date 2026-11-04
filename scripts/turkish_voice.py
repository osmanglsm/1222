#!/usr/bin/env python3
"""Open-source Turkish TTS for 13. Kat using EMA Lightning (Apache-2.0).
Generates one WAV per line and a timing manifest; no silent fallback to robotic speech.
Usage: python scripts/turkish_voice.py --script content/13kat_episode01.json --output output/voice
"""
import argparse
import json
import wave
from pathlib import Path

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--script",default="content/13kat_episode01.json")
    parser.add_argument("--output",default="output/voice")
    parser.add_argument("--speed",type=float,default=0.94)
    args=parser.parse_args()
    if not 0.75 <= args.speed <= 1.25:
        parser.error("speed must be between 0.75 and 1.25 for intelligibility")
    from ema_lightning import EMA
    lines=json.loads(Path(args.script).read_text(encoding="utf-8"))["lines"]
    out=Path(args.output)
    out.mkdir(parents=True,exist_ok=True)
    tts=EMA(device="cpu")
    manifest=[]
    for index,line in enumerate(lines):
        text=line["text"].strip()
        if not text:
            continue
        path=out/f"{index:02d}_{line['speaker']}.wav"
        speech=tts.say(text,path=str(path),speed=args.speed,seed=1300+index)
        if speech.duration <= 0:
            raise RuntimeError(f"Empty audio for line {index}")
        manifest.append({"speaker":line["speaker"],"text":text,"file":path.name,"duration":round(speech.duration,3),"sample_rate":speech.sample_rate})
        print(f"{path}: {speech.duration:.2f}s")
    (out/"manifest.json").write_text(json.dumps({"engine":"EMA Lightning","license":"Apache-2.0","lines":manifest},ensure_ascii=False,indent=2),encoding="utf-8")
    print("Created",len(manifest),"speech files; verify pronunciation before publishing.")

if __name__=="__main__":
    main()
