import asyncio
import json
import os
import subprocess
import edge_tts

# Dizi Hafızası ve Senaryo Veritabanı
BOLUMLER = {
    1: {
        "baslik": "BOLUM 01 - 27 Yillik Frekans",
        "metin": "Mert... Saat tam gece yarısı ve şu an camdan dışarı bakıyorsun, değil mi? Bu imkansız... Bu radyo yirmi yedi yıldır çalışmıyor. Kaçamazsın Mert, bin dokuz yüz doksan dokuzdaki o geceyi hatırlıyor musun? Mert, arkanda...",
        "alt_yazi": "DEVAMI 2. BOLUMDE"
    },
    2: {
        "baslik": "BOLUM 02 - Muhurlu Kapi",
        "metin": "Kapıyı açma. O sesler radyodan değil, bodrum katındaki mühürlü stüdyodan geliyor. Aylin bunu nereden biliyor? Kapı yirmi yedi yıldır açıktı Mert, sen içeri girmeyi unuttun. Mert... Arkandakine sakın bakma.",
        "alt_yazi": "DEVAMI 3. BOLUMDE"
    },
    3: {
        "baslik": "BOLUM 03 - Gecmisten Gelen Not",
        "metin": "Doksan dokuz mu? Ben o yıl beş yaşındaydım... Bu benim imzam! Aylin'e sakın güvenme. Bodrumdaki stüdyoya inersen kapıyı üstüne kilitleyecek. O mektubu sana ben yazdırdım Mert... Ama henüz değil.",
        "alt_yazi": "DEVAMI 4. BOLUMDE"
    },
    4: {
        "baslik": "BOLUM 04 - Saat 03:33",
        "metin": "Saat tam üç otuz üç. Apartmanın duvarlarındaki boyalar dökülüyor, her şey doksan dokuz yılındaki o geceye dönüyor. Radyodaki ses benim sesim değil... Bu, bodrumda kilitli kalan gelecekteki halimin sesi!",
        "alt_yazi": "DEVAMI 5. BOLUMDE"
    }
}

HAFIZA_DOSYASI = "dizi_hafizasi.json"

def hafiza_oku():
    if os.path.exists(HAFIZA_DOSYASI):
        with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"son_bolum": 0}

def hafiza_kaydet(bolum_no):
    with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
        json.dump({"son_bolum": bolum_no}, f, indent=4)

async def ses_uret(metin, ses_dosyasi):
    communicate = edge_tts.Communicate(metin, "tr-TR-AhmetNeural", rate="-10%", pitch="-15Hz")
    await communicate.save(ses_dosyasi)

def video_uret(bolum_no, veri):
    os.makedirs("output", exist_ok=True)
    ses_dosyasi = f"output/ses_bolum_{bolum_no}.mp3"
    video_dosyasi = f"output/radyonun_kabusu_bolum_{bolum_no}.mp4"
    
    print(f">>> {bolum_no}. Bölüm sesi üretiliyor...")
    asyncio.run(ses_uret(veri["metin"], ses_dosyasi))
    
    print(f">>> {bolum_no}. Bölüm 9:16 Dikey MP4 videosu FFmpeg ile işleniyor...")
    # Karanlık gerilim atmosferli (lacivert/antrasit) 1080x1920 dikey video ve ses birleştirme
    komut = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=#0b132b:s=1080x1920:r=30",
        "-i", ses_dosyasi,
        "-vf", f"drawtext=text='RADYONUN KABUSU':fontcolor=white:fontsize=65:x=(w-text_w)/2:y=350,"
               f"drawtext=text='{veri['baslik']}':fontcolor=#e63946:fontsize=50:x=(w-text_w)/2:y=460,"
               f"drawtext=text='{veri['alt_yazi']}':fontcolor=yellow:fontsize=45:x=(w-text_w)/2:y=1550",
        "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p", "-shortest", video_dosyasi
    ]
    subprocess.run(komut, check=True)
    print(f">>> BAŞARILI: {video_dosyasi} üretildi!")

if __name__ == "__main__":
    hafiza = hafiza_oku()
    siradaki = hafiza["son_bolum"] + 1
    if siradaki in BOLUMLER:
        video_uret(siradaki, BOLUMLER[siradaki])
        hafiza_kaydet(siradaki)
    else:
        print("Tüm mevcut bölümler üretildi.")
