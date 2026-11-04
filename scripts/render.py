import argparse
import asyncio
import json
import math
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H = 540, 960
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
NAVY, PAPER, RED, SAND = (18, 53, 63), (244, 231, 203), (172, 67, 55), (224, 204, 161)

def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)

def lines(draw, text, f, width):
    output, current = [], ""
    for word in text.split():
        candidate = (current + " " + word).strip()
        if current and draw.textbbox((0, 0), candidate, font=f)[2] > width:
            output.append(current)
            current = word
        else:
            current = candidate
    if current:
        output.append(current)
    return output

def frame(scene, progress, index, count):
    image = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, W, 185), fill=(21, 62, 73))
    for y in range(205, H, 48):
        shift = int(12 * math.sin(progress * 2 * math.pi + y / 50))
        draw.arc((-50 + shift, y, 590 + shift, y + 58), 0, 180, fill=(42, 106, 115), width=3)
    draw.ellipse((365, 175, 490, 300), fill=(214, 184, 123))
    shift = round(14 * math.sin(progress * 2 * math.pi))
    kind = scene.get("kind", "ship")
    if kind == "space":
        # Layered schematic: moving stars, orbit, probe and radio pulses.
        draw.rectangle((0,185,W,690),fill=NAVY)
        for star in range(65):
            x=int((star*137-progress*35)%W); y=205+(star*79)%450
            draw.ellipse((x,y,x+2,y+2),fill=SAND)
        draw.ellipse((-135,330,145,610),fill=(187,120,84))
        for ring in range(3):
            radius=60+((progress*160+ring*60)%180)
            draw.arc((300-radius,430-radius,300+radius,430+radius),-65,65,fill=(65,130,137),width=2)
        x=round(240+100*progress); y=400+round(8*math.sin(progress*math.pi*2))
        draw.line((x,y,x-80,y+110),fill=SAND,width=5)
        draw.polygon([(x-35,y+60),(x+35,y+60),(x+20,y+105),(x-20,y+105)],fill=RED)
        draw.ellipse((x-52,y-18,x+52,y+38),fill=PAPER,outline=SAND,width=4)
        draw.line((x,y+10,x+35,y-45),fill=PAPER,width=4)
        draw.ellipse((x+29,y-51,x+41,y-39),fill=RED)
        draw.text((180,610),scene.get("label","VOYAGER 1"),font=font(21,True),fill=SAND)
    elif kind == "ship":
        draw.polygon([(85+shift, 480), (440+shift, 480), (382+shift, 548), (140+shift, 548)], fill=(115, 76, 57))
        draw.line((265+shift, 325, 265+shift, 480), fill=PAPER, width=9)
        draw.polygon([(271+shift, 338), (271+shift, 461), (404+shift, 462)], fill=SAND)
        draw.polygon([(255+shift, 353), (255+shift, 461), (153+shift, 462)], fill=(236, 222, 186))
    elif kind == "map":
        draw.rounded_rectangle((65, 320, 475, 600), radius=15, fill=SAND)
        draw.line([(105, 375), (175, 420), (230, 395), (310, 485), (415, 515)], fill=RED, width=8)
        for x, y in [(105, 375), (230, 395), (415, 515)]:
            draw.ellipse((x-13, y-13, x+13, y+13), fill=NAVY)
        draw.text((105, 550), "ESKİ TİCARET YOLLARI", font=font(18, True), fill=NAVY)
    else:
        draw.ellipse((105, 360, 435, 640), fill=(84, 112, 108))
        draw.polygon([(195, 410), (350, 410), (328, 530), (225, 530)], fill=(187, 120, 84))
        draw.ellipse((195, 391, 350, 435), fill=(205, 148, 106))
    draw.polygon([(23, 34), (516, 31), (508, 139), (30, 145)], fill=RED)
    heading_font = font(30, True)
    for n, text in enumerate(lines(draw, scene["heading"], heading_font, 455)[:2]):
        draw.text((W//2, 49+n*39), text, font=heading_font, anchor="mt", fill=PAPER)
    draw.polygon([(17, 703), (523, 696), (515, 911), (22, 918)], fill=PAPER)
    caption_font = font(24, True)
    for n, text in enumerate(lines(draw, scene["narration"], caption_font, 450)[:7]):
        draw.text((46, 728+n*29), text, font=caption_font, fill=NAVY)
    draw.text((28, 930), f"{index+1}/{count}  •  TASLAK", font=font(15, True), fill=SAND)
    return image

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))

def subtitle_time(seconds):
    ms=round(seconds*1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

def validate_content(data):
    if not data.get('scenes'):
        raise ValueError('En az bir sahne gerekli')
    for scene in data['scenes']:
        if not scene.get('heading') or not scene.get('narration'):
            raise ValueError('Her sahnede başlık ve anlatım gerekli')
        if scene.get('kind','ship') not in {'space','ship','map','artifact'}:
            raise ValueError('Desteklenmeyen sahne türü')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--content',default=str(ROOT/'content/voyager.json'))
    parser.add_argument('--output',default='output/voyager.mp4')
    parser.add_argument('--fps',type=int,default=30)
    parser.add_argument('--preview',action='store_true')
    parser.add_argument('--voice',action='store_true')
    parser.add_argument('--duration',type=float,default=65)
    args=parser.parse_args()
    if args.fps<1 or args.duration<=0:
        parser.error('FPS ve süre pozitif olmalı')
    data=json.loads(Path(args.content).read_text(encoding='utf8')); validate_content(data)
    scenes=data['scenes']; dest=Path(args.output); dest.parent.mkdir(parents=True,exist_ok=True)
    report={'status':'failed','publish_allowed':False,'voice':False,'reference_analyzed':False,'errors':[]}
    try:
        durations=[]; audio_paths=[]; cursor=0; cues=[]; storyboard=[]
        for i,scene in enumerate(scenes):
            audio=dest.parent/f'voice_{i:02}.mp3'
            if args.voice:
                import edge_tts
                async def speak():
                    await asyncio.wait_for(edge_tts.Communicate(scene['narration'],'tr-TR-AhmetNeural',rate='-5%').save(str(audio)),timeout=45)
                asyncio.run(speak())
                duration=float(probe(audio)['format']['duration'])+0.25
                audio_paths.append(audio)
            else:
                duration=args.duration*len(scene['narration'].split())/sum(len(s['narration'].split()) for s in scenes)
            durations.append(duration)
            # Phrase times are estimates; no claim of forced word alignment.
            words=scene['narration'].split(); groups=[words[n:n+6] for n in range(0,len(words),6)]
            used=0
            for group in groups:
                start=cursor+duration*used/len(words); used+=len(group)
                cues.append((start,cursor+duration*used/len(words),' '.join(group)))
            storyboard.append({'scene':i+1,'start':cursor,'duration':duration,**scene})
            cursor+=duration
        report['voice']=bool(audio_paths)
        total=math.ceil(cursor*args.fps); size=(540,960) if args.preview else (1080,1920)
        command=['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{size[0]}x{size[1]}','-framerate',str(args.fps),'-i','pipe:0']
        if audio_paths:
            for path in audio_paths: command+=['-i',str(path)]
            filters=';'.join(f'[{i+1}:a]apad=pad_dur=0.25[a{i}]' for i in range(len(audio_paths)))
            filters+=';'+''.join(f'[a{i}]' for i in range(len(audio_paths)))+f'concat=n={len(audio_paths)}:v=0:a=1[voice]'
            command+=['-filter_complex',filters,'-map','0:v','-map','[voice]','-c:a','aac','-b:a','128k']
        command+=['-t',str(cursor),'-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
        process=subprocess.Popen(command,stdin=subprocess.PIPE)
        try:
            for number in range(total):
                t=number/args.fps; i=0; start=0
                while i<len(scenes)-1 and t>=start+durations[i]: start+=durations[i]; i+=1
                scene=dict(scenes[i]); scene['narration']=next((text for a,b,text in cues if a<=t<b),'')
                im=frame(scene,min(1,(t-start)/durations[i]),i,len(scenes))
                if size!=(W,H): im=im.resize(size,Image.Resampling.LANCZOS)
                process.stdin.write(im.tobytes())
        finally:
            process.stdin.close()
        if process.wait()!=0: raise RuntimeError('FFmpeg başarısız')
        info=probe(dest); video=next(s for s in info['streams'] if s['codec_type']=='video')
        report.update(duration=float(info['format']['duration']),width=video['width'],height=video['height'],fps=video['avg_frame_rate'])
        report['status']='draft' if audio_paths else 'silent_preview'
        report['technical_pass']=bool(audio_paths) and size==(1080,1920) and args.fps==30 and 60<=cursor<=90
        report['editorial_review_required']=True
        report['subtitle_alignment']='phrase estimates within individually synthesized scenes; manual review required'
        (dest.parent/'subtitles.srt').write_text('\n\n'.join(f'{i+1}\n{subtitle_time(a)} --> {subtitle_time(b)}\n{text}' for i,(a,b,text) in enumerate(cues)),encoding='utf8')
        (dest.parent/'storyboard.json').write_text(json.dumps(storyboard,ensure_ascii=False,indent=2),encoding='utf8')
        (dest.parent/'script.txt').write_text('\n\n'.join(s['narration'] for s in scenes),encoding='utf8')
        (dest.parent/'sources.json').write_text(json.dumps(data.get('sources',[]),ensure_ascii=False,indent=2),encoding='utf8')
        (dest.parent/'metadata.json').write_text(json.dumps({k:data.get(k) for k in ['title','description','tags']},ensure_ascii=False,indent=2),encoding='utf8')
        frame(scenes[0],0.4,0,len(scenes)).resize((1080,1920)).save(dest.parent/'cover.png')
    except Exception as exc:
        report['errors'].append(str(exc)); raise
    finally:
        (dest.parent/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__': main()
