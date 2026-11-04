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



## Yeni üretim: Voyager 1
`python scripts/render.py --preview --output output/preview/voyager.mp4`
önce sessiz bir 540×960 / 30 FPS test üretir.
`python scripts/render.py --voice --output output/final/voyager.mp4`
1080×1920 / 30 FPS sesli taslak üretir. Her sahnenin sesi ayrı oluşturulur;
sahne süreleri ölçülen ses süresine göre hesaplanır. Ses hatası işlemi başarısız
kılar; report.json ve Actions hata kayıtları korunur. Altyazılar altı kelimelik
parçalardır; sahne içinde zamanları tahminidir, kelime hizalaması değildir.

Çıktılar: MP4, sahne sesleri, SRT, kapak, senaryo, storyboard, kaynaklar,
metadata ve teknik rapor. Görseller Python ile çizilen şemalardır; ölçekli değildir.
Ses olmadan, 60–90 saniye dışında veya yanlış çıktı boyutunda teknik geçiş yoktur.
Yayın izni daima kapalıdır; editoryal inceleme gereklidir.

### Henüz tamamlanmayanlar
Her gün farklı doğrulanmış konu üretimi, Remotion/SVG karakter sistemi,
profesyonel karakter animasyonu, kelime düzeyinde altyazı hizalaması ve müzik
henüz yoktur. Zamanlanan çalışma şimdilik aynı Voyager taslağını tekrar üretir.
Instagram referanslarına erişilemedi; referans uyumu doğrulanmadı.
edge-tts anahtar istemez fakat üçüncü taraf çevrimiçi hizmete bağlıdır;
ses hizmetinin ticari kullanım izni bu proje tarafından doğrulanmış değildir.
Ticari yayın öncesinde uygun lisanslı TTS sağlayıcısı seçilmelidir.
