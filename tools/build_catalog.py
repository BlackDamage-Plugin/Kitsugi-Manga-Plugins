#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kitsugi Manga Eklentileri - katalog üreticisi / doğrulayıcısı.

`apk/` klasöründeki APK + ikon çiftlerinden uygulamanın okuduğu tüm katalog
dosyalarını üretir:

  index.json, plugins.json, index.min.json, plugins.min.json
  builds/index.json, builds/plugins.json, builds/index.min.json,
  builds/plugins.min.json, builds/index.v2.json, builds/index.min.v2.json

Kullanım:
    python3 tools/build_catalog.py            # dosyaları yazar
    python3 tools/build_catalog.py --check    # sadece doğrular (CI için)

Kurallar:
- Katalogdaki her kayıt için APK ve PNG dosyası `apk/` içinde bulunmak zorunda.
- URL'ler tek bir sabitten üretilir (OWNER/REPO/BRANCH); elle URL yazılmaz.
- Eklenti adları mevcut katalogdan korunur, yeni eklentide NAME_OVERRIDES
  tablosuna veya dosya adına düşülür.
- versionCode = major*100000 + minor*1000 + patch  (1.6.12 -> 106012)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APK_DIR = ROOT / "apk"

OWNER = "BlackDamage-Plugin"
REPO = "Kitsugi-Manga-Plugins"
BRANCH = "main"
BASE_URL = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/apk/"

APK_RE = re.compile(r"^tachiyomi-(?P<lang>[a-z]{2,3})\.(?P<slug>[a-z0-9]+)-v(?P<version>\d+\.\d+\.\d+)\.apk$")

# Katalogda görünen adlar (marka yazımı korunur). Yeni eklentiler buraya eklenir.
NAME_OVERRIDES = {
    "amangaplanet": "Amanga Planet",
    "anikiga": "Anikiga",
    "araznovel": "ArazNovel",
    "arcurafansub": "Arcura Fansub",
    "diamondfansub": "DiamondFansub",
    "eldermanga": "Elder Manga",
    "eskimangalar": "Eski Mangalar",
    "gafeland": "gafeland",
    "gaiatoon": "Gaiatoon",
    "ghosthentai": "GhosToon",
    "golgebahcesi": "Gölge Bahçesi",
    "hattorimanga": "Hattori Manga",
    "hattoriscans": "Hattori Scans",
    "hayalistic": "Hayalistic",
    "holyscans": "Holy Scans",
    "juratempest": "JuraTempest",
    "korelimanga": "Koreli Manga",
    "koreliscans": "Koreli Scans",
    "kuroimanga": "Kuroi Manga",
    "laviniafansub": "Lavinia Fansub",
    "limonmanga": "Limon Manga",
    "lunascans": "Luna Scans",
    "mangacix": "MangaciX",
    "mangadenizi": "MangaDenizi",
    "mangadiyari": "Manga Diyarı",
    "mangadusleri": "Mangadusleri",
    "mangakusu": "Manga Kusu",
    "mangaportali": "Manga Portalı",
    "mangaruhu": "Manga Ruhu",
    "mangaship": "Manga Bahçesi",
    "mangatilkisi": "MangaTilkisi",
    "ailurascans": "AiluraScans",
    "duckscans": "DuckScans",
    "fenrirscans": "Fenrir Scans",
    "lunariscans": "LunariScans",
    "oblivionscans": "Oblivion Scans",
    "sadscans": "SadScans",
    "turkmanga": "TürkManga",
    "kazescans": "KazeScans",
    "mangakulesi": "Manga Kulesi",
    "mangamac": "MangaMAC",
    "merlinmanga": "Merlin Manga",
    "outcatsscans": "Outcats Scans",
    "mangatr": "Manga-TR",
    "mangawow": "MangaWOW",
    "mangawt": "MangaWT",
    "mangitto": "Mangitto",
    "merlinscans": "MerlinToon",
    "mikrokosmosfansub": "Mikrokosmos Fansub",
    "milasub": "MilaSub",
    "mindafansub": "Minda Fansub",
    "monomanga": "Mono Manga",
    "moondaisyscans": "Moon Daisy Scans",
    "nemesisscans": "Nemesis scans",
    "nirvanamanga": "Nirvana Manga",
    "niverafansub": "Nivera Fansub",
    "norascans": "Nora Scans",
    "okutoon": "OkuToon",
    "opiatoon": "Opiatoon",
    "orimanga": "Ori Manga",
    "paradoxscans": "Paradox Scans",
    "patimanga": "Pati Manga",
    "ragnarscans": "Ragnar Scans",
    "raindropfansub": "Raindrop Fansub",
    "ruyamanga": "Rüya Manga",
    "sereinscan": "Serein Scan",
    "shadowceviri": "Shadow Çeviri",
    "shijiescans": "Shijie Scans",
    "siyahmelek": "Siyah Melek",
    "sleptmanga": "Slept Manga",
    "strayfansub": "Stray Fansub",
    "summertoon": "SummerToon",
    "sunsetmanga": "Sunset Manga",
    "tarotscans": "Tarot Scans",
    "tenshimanga": "Tenshi Manga",
    "tonizutoon": "TonizuToon",
    "toontaku": "Toontaku",
    "tortugaceviri": "Tortuga Ceviri",
    "trmanga": "Tr Manga",
    "turkcemangaoku": "Türkçe Manga Oku",
    "uzaymanga": "Uzay Manga",
    "webtoonhatti": "Webtoon Hatti",
    "webtoonia": "Webtoonia",
    "webtoonoku": "WebtoonOku",
    "yaoiflix": "Yaoi Flix",
    "yaoimangaoku": "Yaoi Manga Oku",
    "zenithscans": "Zenith Scans",
}

# rsync/iCloud gibi araçların bıraktığı çöp dosyalar kataloğa girmesin.
JUNK = {"Thumbs.db", ".DS_Store"}


def tr_key(text: str) -> str:
    """Türkçe alfabeye yakın, deterministik sıralama anahtarı."""
    table = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    return text.translate(table).casefold()


def version_code(version: str) -> int:
    major, minor, patch = (int(p) for p in version.split("."))
    return major * 100_000 + minor * 1_000 + patch


def load_name_map() -> dict[str, str]:
    """tools/isimler.json varsa (paket aktarımının APK etiketlerinden ürettiği
    adlar) NAME_OVERRIDES'tan önce gelir."""
    path = ROOT / "tools" / "isimler.json"
    if not path.is_file():
        return {}
    try:
        return {k: v for k, v in json.loads(path.read_text(encoding="utf-8")).items() if isinstance(v, str)}
    except json.JSONDecodeError:
        return {}


def load_previous() -> dict[str, dict]:
    """Mevcut katalogdan pkg -> kayıt eşlemesi (ad, nsfw, sources korunur)."""
    previous: dict[str, dict] = {}
    for path in (ROOT / "index.json", ROOT / "builds" / "index.json"):
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for entry in data:
            previous.setdefault(entry["pkg"], entry)
    v2 = ROOT / "builds" / "index.v2.json"
    if v2.is_file():
        try:
            for entry in json.loads(v2.read_text(encoding="utf-8"))["extensionList"]["extensions"]:
                previous.setdefault(entry["packageName"], {}).setdefault("sources", entry.get("sources", []))
        except (json.JSONDecodeError, KeyError):
            pass
    return previous


def scan() -> list[dict]:
    if not APK_DIR.is_dir():
        sys.exit(f"HATA: {APK_DIR} bulunamadı.")
    previous = load_previous()
    names = load_name_map()
    entries: list[dict] = []
    problems: list[str] = []

    for apk in sorted(APK_DIR.glob("*.apk")):
        if apk.name in JUNK:
            continue
        match = APK_RE.match(apk.name)
        if not match:
            problems.append(f"dosya adı desene uymuyor: apk/{apk.name}")
            continue
        lang, slug, version = match.group("lang"), match.group("slug"), match.group("version")
        pkg = f"eu.kanade.tachiyomi.extension.{lang}.{slug}"
        icon = APK_DIR / f"{pkg}.png"
        if not icon.is_file():
            problems.append(f"ikon yok: apk/{pkg}.png (APK: {apk.name})")
            continue

        old = previous.get(pkg, {})
        name = names.get(slug) or NAME_OVERRIDES.get(slug) or old.get("name") or slug.capitalize()
        code = version_code(version)
        if old.get("version") and old.get("code"):
            old_code = version_code(old["version"])
            if old_code != old["code"]:
                problems.append(
                    f"versionCode tutarsız: {name} sürüm {old['version']} -> kod {old['code']} (beklenen {old_code})"
                )

        entries.append(
            {
                "name": name,
                "pkg": pkg,
                "apk": apk.name,
                "lang": lang,
                "code": code,
                "version": version,
                "nsfw": int(old.get("nsfw", 0)),
                "sources": old.get("sources")
                or [{"name": name, "language": lang, "type": "manga"}],
            }
        )

    entries.sort(key=lambda e: tr_key(e["name"]))
    return entries, problems


def legacy_catalog(entries: list[dict]) -> list[dict]:
    out = []
    for e in entries:
        out.append(
            {
                "name": e["name"],
                "pkg": e["pkg"],
                "apk": e["apk"],
                "lang": e["lang"],
                "code": e["code"],
                "version": e["version"],
                "nsfw": e["nsfw"],
                "url": BASE_URL + e["apk"],
                "iconUrl": f"{BASE_URL}{e['pkg']}.png",
            }
        )
    return out


def v2_catalog(entries: list[dict]) -> dict:
    extensions = []
    for e in entries:
        extensions.append(
            {
                "name": e["name"],
                "packageName": e["pkg"],
                "versionName": e["version"],
                "versionCode": str(e["code"]),
                "contentWarning": "CONTENT_WARNING_NSFW" if e["nsfw"] else "CONTENT_WARNING_SAFE",
                "resources": {
                    "apkUrl": BASE_URL + e["apk"],
                    "iconUrl": f"{BASE_URL}{e['pkg']}.png",
                },
                "sources": e["sources"],
            }
        )
    return {
        "name": "Kitsugi Türkçe Manga Eklentileri",
        "badgeLabel": "KİTSUGİ",
        "contact": {
            "website": f"https://github.com/{OWNER}/{REPO}",
        },
        "extensionList": {"extensions": extensions},
    }


def dumps(value, *, pretty: bool) -> str:
    if pretty:
        return json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n"


def targets(entries: list[dict]) -> dict[Path, str]:
    legacy = legacy_catalog(entries)
    v2 = v2_catalog(entries)
    files: dict[Path, str] = {}
    for name in ("index.json", "plugins.json"):
        files[ROOT / name] = dumps(legacy, pretty=True)
        files[ROOT / name.replace(".json", ".min.json")] = dumps(legacy, pretty=False)
        files[ROOT / "builds" / name] = dumps(legacy, pretty=True)
        files[ROOT / "builds" / name.replace(".json", ".min.json")] = dumps(legacy, pretty=False)
    files[ROOT / "builds" / "index.v2.json"] = dumps(v2, pretty=True)
    files[ROOT / "builds" / "index.min.v2.json"] = dumps(v2, pretty=False)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Kitsugi katalog üreticisi")
    parser.add_argument("--check", action="store_true", help="dosyaları yazma, sadece doğrula")
    args = parser.parse_args()

    entries, problems = scan()
    if not entries:
        sys.exit("HATA: apk/ klasöründe geçerli eklenti bulunamadı.")

    pkgs = [e["pkg"] for e in entries]
    if len(pkgs) != len(set(pkgs)):
        problems.append("aynı paket adına sahip birden fazla APK var.")

    files = targets(entries)
    stale: list[str] = []
    for path, content in files.items():
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        if current != content:
            stale.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

    print(f"eklenti: {len(entries)}  |  katalog dosyası: {len(files)}")
    if problems:
        print("\nUYARI:")
        for p in problems:
            print("  -", p)

    if args.check:
        if stale:
            print("\nGüncel olmayan katalog dosyaları:")
            for s in stale:
                print("  -", s)
            print("\nDüzeltmek için: python3 tools/build_catalog.py")
            return 1
        print("Tüm katalog dosyaları güncel.")
        return 1 if problems else 0

    if stale:
        print("Yazıldı/güncellendi:")
        for s in stale:
            print("  -", s)
    else:
        print("Katalog dosyaları zaten güncel.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
