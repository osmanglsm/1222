#!/usr/bin/env python3
"""Compose the 13 Kat episode with EMA Lightning voice clips; no robotic fallback."""
import argparse,json,math,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def wrap(d,text,f,w):
    lines=[];line=""
    for word in text.split():
        new=(line+" "+word).strip()
        if line and d.textbbox((0,0),new,font=f)[2]>w:lines.append(line);line=word
        else:line=new
    if line:lines.append(line)
    return lines
def paint(scene,t,caption=""):
    im=Image.new("RGB",(540,960),(12,27,35));d=ImageDraw.Draw(im)
    d.rectangle((0,100,540,750),fill=(27,61,69))
    drift=int(8*math.sin(t*.65))
    if scene in (0,1):
        d.rectangle((95,150,445,745),fill=(8,24,33),outline=(104,123,117),width=9)
        d.rectangle((118,178,422,715),fill=(32,60,65))
        for x in (132,407):d.line((x,200,x,692),fill=(102,116,108),width=4)
        d.rounded_rectangle((212,210,329,296),radius=9,fill=(5,15,23))
        d.text((270,223),"12" if scene==0 and t<1.8 else "13",font=font(54,True),fill=(229,75,64),anchor="mt")
        if scene==1:
            d.ellipse((220,348+drift,320,458+drift),fill=(215,178,144))
            d.polygon([(223,365+drift),(247,335+drift),(310,354+drift),(321,382+drift)],fill=(32,31,37))
            d.polygon([(181,486+drift),(354,486+drift),(380,704),(166,704)],fill=(41,58,67))
            for x in (246,293):d.ellipse((x,403+drift,x+6,410+drift),fill=(29,28,33))
    elif scene==2:
        d.polygon([(0,170),(540,170),(370,660),(170,660)],fill=(44,72,76))
        d.polygon([(0,750),(540,750),(370,660),(170,660)],fill=(32,43,46))
        for i in range(5):
            x=55+i*92;d.line((x,230,x+60,605),fill=(88,109,106),width=3)
        d.rectangle((234,290,304,390),fill=(233,206,143))
        d.rectangle((224,390,316,660),fill=(19,30,34))
    else:
        d.rectangle((92,155,448,746),fill=(36,48,52),outline=(118,111,96),width=10)
        d.rectangle((122,183,417,730),fill=(54,62,60),outline=(94,86,72),width=5)
        d.rectangle((202,280,338,340),fill=(185,171,135))
        d.text((270,291),"1207",font=font(31,True),fill=(34,37,36),anchor="mt")
        d.ellipse((369,490,390,512),fill=(216,179,96))
        if scene==4:d.polygon([(275+drift,540),(322+drift,515),(378,505),(376,527),(327+drift,544)],fill=(200,155,126))
        if scene==5:
            d.polygon([(132,185),(395,185),(395,720),(132,720)],fill=(21,30,35))
            d.ellipse((222,345,322,456),fill=(17,21,25))
            d.polygon([(181,480),(358,480),(390,715),(148,715)],fill=(14,19,24))
    if caption:
        f=font(25,True);lines=wrap(d,caption,f,450)[:3]
        d.rounded_rectangle((25,790,515,810+len(lines)*37),radius=12,fill=(239,224,192))
        for j,line in enumerate(lines):d.text((270,800+j*37),line,font=f,fill=(25,37,43),anchor="mt")
    return im
def duration(path):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],text=True))
def compose(manifest,voice_dir,output,seconds=60,fps=24):
    lines=manifest["lines"]
    if len(lines)!=10:raise ValueError("Episode 01 requires 10 dialogue lines")
    output.parent.mkdir(parents=True,exist_ok=True)
    scene_for_line=[0,1,1,2,3,3,4,5,5,5]
    lengths=[duration(voice_dir/item["file"]) for item in lines]
    gaps=[.45]*len(lines);gaps[6]=.8;gaps[7]=.9
    spoken=sum(lengths)+sum(gaps)
    if spoken>seconds-.7:raise ValueError(f"Dialogue {spoken:.1f}s exceeds target {seconds}s; no truncation")
    extra=(seconds-.7-spoken)/(len(lines)+1)
    events=[];cursor=extra
    for i,item in enumerate(lines):
        events.append((cursor,cursor+lengths[i],scene_for_line[i],item["text"]))
        cursor+=lengths[i]+gaps[i]+extra
    inputs=[];filters=[]
    for i,item in enumerate(lines):
        inputs+=["-i",str(voice_dir/item["file"])]
        delay=int(events[i][0]*1000)
        filters.append(f"[{i+1}:a]aresample=48000,adelay={delay}|{delay}[v{i}]")
    filters.append("".join(f"[v{i}]" for i in range(len(lines)))+f"amix=inputs={len(lines)}:duration=longest:normalize=0,alimiter=limit=0.90[a]")
    cmd=["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pixel_format","rgb24","-video_size","540x960","-framerate",str(fps),"-i","pipe:0",*inputs,"-filter_complex",";".join(filters),"-map","0:v","-map","[a]","-vf","scale=1080:1920:flags=lanczos","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-t",str(seconds),"-movflags","+faststart",str(output)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for frame in range(seconds*fps):
            t=frame/fps
            event=next(((a,b,s,txt) for a,b,s,txt in events if a<=t<b),None)
            idx=event[2] if event else next((s for a,b,s,txt in reversed(events) if a<=t),0)
            caption=event[3] if event else ""
            if caption:
                words=caption.split();phase=(t-event[0])/(event[1]-event[0])
                chunks=max(1,math.ceil(len(words)/8));which=min(chunks-1,int(phase*chunks))
                lo=round(which*len(words)/chunks);hi=round((which+1)*len(words)/chunks)
                caption=" ".join(words[lo:hi])
            p.stdin.write(paint(idx,t,caption).tobytes())
    finally:p.stdin.close()
    if p.wait():raise RuntimeError("FFmpeg failed")
    return events
def main():
    p=argparse.ArgumentParser();p.add_argument("--voice-dir",default="output/13kat_voice")
    p.add_argument("--output",default="output/13kat_episode01.mp4");p.add_argument("--duration",type=int,default=60)
    a=p.parse_args();voice_dir=Path(a.voice_dir)
    manifest=json.loads((voice_dir/"manifest.json").read_text(encoding="utf8"))
    events=compose(manifest,voice_dir,Path(a.output),a.duration)
    Path(a.output).with_suffix(".timing.json").write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding="utf8")
if __name__=="__main__":main()
