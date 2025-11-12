# mOody

A song application that analyzes your emotions and recommends songs based on the emotion detected.
burası sonradan doldurulacaktır

# 🎵 mOody — Duyguya Göre Müzik Çalar  
### *Spotify entegreli, yüz ifadesi analiziyle duyguyu tahmin eden, akıllı müzik önerici uygulaması*  

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/CustomTkinter-GUI-orange?logo=python&logoColor=white" alt="CustomTkinter">
  <img src="https://img.shields.io/badge/Spotify_API-73ace5159f9a-1DB954?logo=spotify" alt="Spotify API">
  <img src="https://img.shields.io/badge/DeepFace-Facial_Emotion-red?logo=opencv" alt="DeepFace">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

<p align="center">
  <i>Yüzünde bir tebessüm mü var? 🥹 Hüzünlü bir bakış mı? mOody anında hislerini algılar ve sana tam uygun şarkıyı çalar!</i>
</p>

---

## 🌟 Özellikler

| 🎯 Özellik | Açıklama |
|-----------|----------|
| 😃 **Duygu Analizi** | Kamera ile gerçek zamanlı yüz ifadesi analizi (`DeepFace` + `MediaPipe`) |
| 🎧 **Spotify Entegrasyonu** | Şarkı arama, önizleme, beğenilenleri listeleme, Spotify’da açma |
| 📥 **MP3 İndirme** | `spotdl` ile yüksek kaliteli şarkı indirme desteği |
| 📺 **YouTube Bağlantısı** | YouTube Music’te aynı şarkıyı açma seçeneği |
| 🎚️ **Akıllı Kontroller** | Ses düzeyi ayarı, çal/durdur butonları, albüm kapağı gösterimi |
| 🤖 **Mood Modları** | <ul><li>✋ **Tek el** → Motivasyon modu (enerjik şarkılar)</li><li>🤟 **İki el** → Romantik mod (baladlar)</li></ul> |

---

## 🖥️ Ekran Görüntüleri *(Örnek — kendi ekranlarını eklemeyi unutma!)*

> 📌 *İleride uygulama ekranlarını buraya ekleyebilirsin. Örneğin:*
> ```
> ![Ana Ekran](screenshots/main.png)
> ![Duygu Analizi](screenshots/emotion.png)
> ```

---

## 🛠️ Kurulum

### Ön Gereksinimler
- Python 3.9+
- Spotify Developer hesabı ([ücretsiz kayıt](https://developer.spotify.com/dashboard))
- Kamera (duygu analizi için)

### Adım Adım

1. **Depoyu klonla:**
   ```bash
   git clone https://github.com/kullanici-adi/mOody.git
   cd mOody

