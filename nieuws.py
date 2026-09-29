#!/usr/bin/env python3
"""
TankKompas - nieuws ophalen

Haalt recente koppen op uit meerdere categorieën: auto, regio, alternatief/
duiding, ICT/cybersecurity en entertainment/televisie.
Schrijft het resultaat naar docs/news.json.
"""
import html
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
OUTPUT_FILE = ROOT / "docs" / "news.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TankKompas/1.0"}

BRONNEN = [
    {"naam": "AutoWeek", "categorie": "Auto", "url": "https://www.autoweek.nl/rss/", "aantal": 2},
    {"naam": "Autoblog", "categorie": "Auto en mobiliteit", "url": "https://www.autoblog.nl/feed/news.xml", "aantal": 2},
    {"naam": "De Stentor Deventer", "categorie": "Regio", "url": "https://www.destentor.nl/deventer/rss.xml", "aantal": 2},
    {"naam": "MOZOM", "categorie": "Alternatief en duiding", "url": "https://mozom.nl/feed/", "aantal": 2},
    {"naam": "Tweakers", "categorie": "ICT en technologie", "url": "https://tweakers.net/feeds/nieuws.xml", "aantal": 2},
    {"naam": "NCSC", "categorie": "ICT en cybersecurity", "url": "https://feeds.ncsc.nl/nieuws.rss", "aantal": 2},
    {"naam": "Mediacourant", "categorie": "Entertainment en televisie", "url": "https://www.mediacourant.nl/feed/", "aantal": 2},
]


def schoon(tekst):
    tekst = html.unescape(tekst or "")
    tekst = re.sub(r"<[^>]+>", "", tekst)
    return tekst.strip()


def haal_feed(bron):
    items = []
    try:
        req = urllib.request.Request(bron["url"], headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml = resp.read().decode("utf-8", errors="ignore")

        ruwe_items = re.findall(r"<(?:item|entry)(?:\s[^>]*)?>(.*?)</(?:item|entry)>", xml, re.DOTALL)
        for ruw in ruwe_items[: bron["aantal"]]:
            titel = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", ruw, re.DOTALL)
            link = re.search(r"<link>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</link>", ruw, re.DOTALL)
            if not link:
                link = re.search(r"<link[^>]+href=[\"'](.*?)[\"']", ruw, re.DOTALL)
            if titel and link:
                items.append(
                    {
                        "bron": bron["naam"],
                        "categorie": bron["categorie"],
                        "titel": schoon(titel.group(1)),
                        "link": schoon(link.group(1)).split("?")[0],
                    }
                )
    except Exception as e:
        print(f"Kon {bron['naam']} niet ophalen ({e}), sla over.")
    return items


def main():
    per_bron = []
    for bron in BRONNEN:
        per_bron.append(haal_feed(bron))

    # Houd de lijst gevarieerd: eerst één kop per bron, daarna de tweede ronde.
    alle_items = []
    for ronde in range(max((len(items) for items in per_bron), default=0)):
        for items in per_bron:
            if ronde < len(items):
                alle_items.append(items[ronde])

    if not alle_items:
        print("Geen nieuws opgehaald; bestaande news.json blijft behouden.")
        return

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"items": alle_items}, f, ensure_ascii=False, indent=2)

    print(f"Klaar. {len(alle_items)} nieuwsitems weggeschreven naar {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
