# Ücretsiz 2D Animasyon Kanalı

Bu depo, referans tarzında **2D tarih/bilgi videosu** üretmek için açık kaynak başlangıç projesidir.

## Kullanım
1. GitHub deposunda **Actions → Daily 2D explainer draft → Run workflow** açın.
2. İşlem tamamlandığında **Artifacts → daily-explainer-draft** dosyasını indirin.
3. Günlük zamanlama UTC 07:17 / Türkiye 10:17'dir; GitHub geciktirebilir.

## Şu anda neler var?
- Python/Pillow ile dikey 2D animasyon taslağı.
- FFmpeg ile H.264 MP4 üretimi.
- İnternet üzerinden Türkçe ses denemesi (edge-tts; çevrimdışı değildir ve servis erişimine bağlıdır).
- Güncel konu adaylarını RSS'den çekip **doğrulanmamış taslak** dosyasına yazma.

**Önemli:** Her gün gerçek bir haber videosu üretilmez; her çalışmada aynı örnek içerik görselleştirilir. RSS kayıtları kontrol edilmeden haber olarak sunulmaz. Instagram'a otomatik paylaşım bulunmaz.

## Ücretsiz kullanım
Depo Public olarak tutulduğunda standart GitHub-hosted Actions çalışmaları ücretsizdir (GitHub'ın kullanım ilkeleri geçerlidir). Bilgisayar kapalıyken de zamanlanan çalışma tetiklenebilir.
