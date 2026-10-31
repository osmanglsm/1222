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
    if kind == "ship":
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
    draw.text((28, 930), f"{index+1}/{count}  •  ÖRNEK", font=font(15, True), fill=SAND)
    return image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", default=str(ROOT / "content/demo.json"))
    parser.add_argument("--output", default="output/demo.mp4")
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--fps", type=int, default=12)
    parser.add_argument("--voice", action="store_true")
    args = parser.parse_args()
    scenes = json.loads(Path(args.content).read_text(encoding="utf-8"))["scenes"]
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        audio = Path(directory) / "voice.mp3"
        has_voice = False
        if args.voice:
            try:
                import edge_tts
                narration = " ".join(scene["narration"] for scene in scenes)
                asyncio.run(edge_tts.Communicate(narration, "tr-TR-AhmetNeural", rate="-5%").save(str(audio)))
                has_voice = audio.exists() and audio.stat().st_size > 0
            except Exception as exc:
                print("Ses servisi kullanılamıyor, sessiz video oluşturulacak:", exc)
        duration = max(1, args.duration)
        fps = max(1, args.fps)
        total = duration * fps
        command = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pixel_format", "rgb24",
                   "-video_size", f"{W}x{H}", "-framerate", str(fps), "-i", "pipe:0"]
        if has_voice:
            command.extend(["-i", str(audio), "-map", "0:v", "-map", "1:a",
                            "-af", "apad", "-c:a", "aac", "-b:a", "128k"])
        command.extend(["-t", str(duration), "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "26", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(destination)])
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        try:
            for number in range(total):
                index = min(len(scenes)-1, number * len(scenes) // total)
                local = (number * len(scenes) / total) % 1
                process.stdin.write(frame(scenes[index], local, index, len(scenes)).tobytes())
        except BrokenPipeError:
            pass
        finally:
            process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError("FFmpeg video oluşturamadı")
    print("Video:", destination, "| Ses:", "var" if has_voice else "yok")

if __name__ == "__main__":
    main()
