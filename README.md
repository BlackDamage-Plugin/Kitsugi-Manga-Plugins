# 📚 Kitsugi Manga Plugins & Sources (TR)

Kitsugi Android uygulaması için tüm Türkçe manga, manhwa ve webtoon eklentilerinin / kaynak ayrıştırıcılarının (parser) merkezi kaynak deposudur.

Bu depo, Türkiye'deki manga ve webtoon okuyucularının kullandığı **tüm Türkçe kaynakları** iki ana açık kaynak ekosisteminden (Kotatsu ve Keiyoushi / Mihon) eksiksiz olarak bir araya getirir.

---

## 📂 Dizin Yapısı

```
Kitsugi-Manga-Plugins/
├── kotatsu-parsers-tr/          # 🤖 Kotatsu-Redo tabanlı 121 Türkçe Parser
│   ├── MangaParser.kt           # Temel Kotatsu ayrıştırıcı arayüzü
│   └── site/
│       ├── madara/tr/           # WordPress + WP-Manga tabanlı 70 TR kaynak
│       ├── mangareader/tr/      # MangaReader temalı 38 TR kaynak
│       ├── tr/                  # Özel kodlanmış 7 TR kaynak (ElderManga, SadScans vb.)
│       ├── zeistmanga/tr/       # Blogspot/Blogger tabanlı 4 TR kaynak
│       ├── mmrcms/tr/           # MMRCMS tabanlı 1 TR kaynak (MangaDenizi)
│       └── all/MangaBall.kt     # Çok dilli MangaBall TR ayrıştırıcısı
│
└── keiyoushi-extensions-tr/     # ⚡ Keiyoushi / Mihon tabanlı 81 Türkçe Eklenti
    ├── lib-multisrc/            # Ortak motor kütüphaneleri (UzayManga, Madara, Themesia)
    └── src/tr/                  # 81 bağımsız eklenti paketi (.apk derlenebilir)
        ├── afroditscans/        # AfroditScans (SvelteKit / UzayManga motoru)
        ├── golgebahcesi/        # Gölge Bahçesi
        ├── mangatr/             # Manga-TR
        ├── tortugaceviri/       # Tortuga Çeviri
        ├── hayalistic/          # Hayalistic
        ├── mangaruhu/           # MangaRuhu
        └── ... (81 eklenti)

├── apk/                         # 📦 Derlenmiş eklentiler (APK + ikon)
├── builds/                      # 🔁 Depo kökü normalize edildiğinde okunan kopya
├── tools/build_catalog.py       # 🛠️ Katalog üreticisi / doğrulayıcısı
├── .github/workflows/katalog.yml# ✅ Katalog ↔ APK tutarlılık denetimi
├── index.json / plugins.json    # Katalog (v1 biçimi)
└── *.min.json                   # Katalog (sıkıştırılmış — istemci önce bunu ister)
```

---

## 🧩 Katalog Dosyaları (Uygulamanın Okuduğu Dosyalar)

Kitsugi istemcisi depo URL'sini `builds/index.json` uç noktasına normalize eder ve **önce `.min.json` sürümlerini** ister; `.min.json` yoksa eklentiler "depoda yok" görünür. Bu yüzden aşağıdaki 10 dosya her zaman birlikte üretilir:

| Dosya | Amaç |
|---|---|
| `index.json`, `plugins.json` | Kök katalog (Mihon/Keiyoushi uyumlu dizi biçimi) |
| `index.min.json`, `plugins.min.json` | Aynı kataloğun sıkıştırılmış hâli — istemcilerin ilk baktığı dosyalar |
| `builds/index.json`, `builds/plugins.json` | Depo kökü normalize edildiğinde okunan uç nokta |
| `builds/index.min.json`, `builds/plugins.min.json` | Sıkıştırılmış `builds/` kopyaları |
| `builds/index.v2.json`, `builds/index.min.v2.json` | v2 biçimi (`extensionList.extensions` + `sources`) |

**URL tabanı (tek kaynak):** `https://raw.githubusercontent.com/BlackDamage-Plugin/Kitsugi-Manga-Plugins/main/apk/`

> Eski (`f26901964-eng`) hesap adı GitHub'da artık bulunmadığı için tüm `url` / `iconUrl` / `apkUrl` adresleri 404 dönüyordu; bu yüzden eklentiler uygulamada aktif görünmüyordu. Adresler artık tek yerden üretiliyor.

### Katalog üretimi / doğrulama

```bash
python3 tools/build_catalog.py            # apk/ klasöründen 10 katalog dosyasını üretir
python3 tools/build_catalog.py --check    # sadece denetler (CI: .github/workflows/katalog.yml)
```

Araç `apk/` içindeki her APK için ikon (`.png`) arar, `versionCode`'u sürümden hesaplar
(`1.6.12 → 106012`), adları korur ve eksik dosya / tutarsızlık varsa uyarır.

### 🔄 Güncel sürümler

\`.github/workflows/upstream-guncelle.yml\` her gün 03:00 UTC'de (veya elle) çalışır:
Keiyoushi resmi kataloğundan TR eklentilerinin en güncel APK + ikonlarını indirir, `apk/`
klasörünü günceller, katalogları üretir ve `docs/guncelleme-raporu.md` raporuyla commit eder.

### ➕ Yeni eklenti ekleme

1. APK'yı `apk/tachiyomi-tr.<paket>-v<sürüm>.apk` adıyla koy (örn. `tachiyomi-tr.sadscans-v1.6.19.apk`).
2. İkonu `apk/eu.kanade.tachiyomi.extension.tr.<paket>.png` adıyla koy.
3. `python3 tools/build_catalog.py` çalıştır, değişiklikleri gönder.

Araç gerisini (10 katalog dosyası, `code`, sıralama, URL'ler) kendisi yapar; elle JSON düzenlemeye gerek yok.

### ⚠️ Paket içinde bulunmayan kaynaklar

Şu an `apk/` klasöründe **81** eklenti var (hepsi yayınlanan en güncel sürümde). Aşağıdaki kaynaklar için **APK/ikon dosyası depoda yok**, bu yüzden kataloğa eklenemiyor (kataloğa eklenseydi uygulamada "indirilemedi" hatası verirdi):

`SadScans` · `DuckScans` · `LunariScans` · `AiluraScans` · `Oblivion Scans` · `TürkManga` · `Fenrir Scans`

APK'ları temin edildiğinde yukarıdaki 3 adımlık akışla dakikalar içinde aktif hâle gelir.

---

## 🏆 En Sağlam ve En Çok Kullanılan TR Manga Kaynakları Analizi

| Kaynak Adı | Alan Adı | Motor / Altyapı | Durum | Açıklama |
|---|---|---|---|---|
| **Gölge Bahçesi** | `golgebahcesi.com` | Özel (Next.js / React) | 🟢 Aktif | Türkiye'nin en geniş manhwa/aksiyon arşivi. Eski MangaReader kodundan Next.js altyapısına geçti. |
| **Manga-TR** | `manga-tr.com` | Özel API / HTML | 🟢 Aktif | En köklü ve en zengin klasik manga kütüphanesi. |
| **Tortuga Çeviri** | `tortugaceviri.com` | WordPress (Madara) | 🟢 Aktif | One Piece ve Shonen odaklı, en istikrarlı ve kesintisiz kaynak. |
| **AfroditScans** | `afroditscans.com` | SvelteKit (`__data.json`) | 🟢 Aktif | Çok hızlı bölüm güncellemeleri; Kitsugi'nin yerel `SvelteMangaEngine` motoruyla tam uyumlu. |
| **MangaRuhu** | `mangaruhu.com` | WordPress (Madara) | 🟢 Aktif | Popüler romantik, dram ve fantastik manhwa arşivi. |
| **SadScans** | `sadscans.org` | Özel HTML | 🟡 APK yok | Kaliteli çevirileriyle tanınan bağımsız ekip; Kotatsu parser'ı depoda var, APK henüz yok. |

---

## ⚙️ Teknik Hata Notları ve Çözümler (Neden Bazı Kaynaklar Bozulur?)

1. **Kotatsu MangaReader 404 (`KTS-SRC-9004`):**
   - Siteler (örneğin Gölge Bahçesi veya AfroditScans) WordPress MangaReader temasından SvelteKit veya Next.js'e taşındığında eski AJAX adresleri 404 verir.
   - **Çözüm:** Bu siteler için Keiyoushi UzayManga/SvelteKit scraper'ı veya Kitsugi içindeki `SvelteMangaEngine` kullanılmalıdır.

2. **Cloudflare & SSL Handshake (`KTS-SRC-9008` / HTTP 525):**
   - AlucardScans ve ZenithScans gibi sitelerin sunucu taraflı SSL sertifikaları veya alan adı yönlendirmeleri periyodik olarak çöker.
   - **Çözüm:** Domain aynalama (mirror) ve Cloudflare WebView Cookie desteği devreye alınır.
