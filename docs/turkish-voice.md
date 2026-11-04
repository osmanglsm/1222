# Açık kaynak Türkçe seslendirme — 13. Kat
Bu modül **EMA Lightning** kullanır: https://github.com/canberk7/ema-lightning
Kod ve model ağırlıkları Apache-2.0 lisanslıdır. İnternet yalnızca ilk model indirmesinde gerekir.
## Kurulum
Python 3.11–3.13 önerilir.
```bash
pip install ema-lightning
python scripts/turkish_voice.py --script content/13kat_episode01.json --output output/voice
```
Çıktılar: her replik için WAV ve süreleri içeren `manifest.json`.
**Önemli:** EMA Lightning tek sesli bir modeldir. Kerem, anlatıcı ve diğer Kerem bu ilk sürümde aynı temel sesle okunur. Çok karakterli doğal oyunculuk henüz yoktur. Gerilim için cümleleri ayrı üretip montajda duraklama ve efekt ekleyin. Üretilen sesleri dinlemeden yayımlamayın.
Piper tr_TR-dfki modelinin eğitim verisi CC BY-NC-SA olduğundan para kazanılabilecek bir kanal için varsayılan olarak seçilmedi.
GitHub Actions'da 60 saniyelik videoya birleştirme ayrıca gereklidir; bu değişiklik TTS WAV üretim adımını ekler, otomatik video montajını henüz değiştirmez.
