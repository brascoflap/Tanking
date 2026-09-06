#!/usr/bin/env python3
"""
TankKompas - nieuws ophalen

Haalt een paar recente koppen op uit onafhankelijke, niet-publieke-omroep
bronnen: AutoWeek en Autoblog (auto-nieuws), De Stentor Deventer (regionaal).
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
    {"naam": "AutoWeek", "url": "https://www.autoweek.nl/rss/", "aantal": 3},
    {"naam": "Autoblog", "url": "https://www.autoblog.nl/feed/news.xml", "aantal": 3},
    {"naam": "De Stentor Deventer", "url": "https://www.destentor.nl/deventer/rss.xml", "aantal": 3},
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

        ruwe_items = re.findall(r"<item>(.*?)</item>", xml, re.DOTALL)
        for ruw in ruwe_items[: bron["aantal"]]:
            titel = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", ruw, re.DOTALL)
            link = re.search(r"<link>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</link>", ruw, re.DOTALL)
            if titel and link:
                items.append(
                    {
                        "bron": bron["naam"],
                        "titel": schoon(titel.group(1)),
                        "link": schoon(link.group(1)).split("?")[0],
                    }
                )
    except Exception as e:
        print(f"Kon {bron['naam']} niet ophalen ({e}), sla over.")
    return items


def main():
    alle_items = []
    for bron in BRONNEN:
        alle_items.extend(haal_feed(bron))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"items": alle_items}, f, ensure_ascii=False, indent=2)

    print(f"Klaar. {len(alle_items)} nieuwsitems weggeschreven naar {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
