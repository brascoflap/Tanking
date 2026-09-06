#!/usr/bin/env python3
"""
TankKompas - prijzen ophalen

Haalt de actuele Euro95-prijzen op van tankstationprijzen.nl voor Deventer
(dit zijn de enige stations met een echte, gratis, live bron: Tango en TinQ).
Vult dit aan met de stations uit stations_handmatig.json (prijzen die jij zelf
af en toe bijwerkt, want daar is geen gratis live bron voor).

Schrijft het resultaat naar docs/data.json, dat de website (docs/index.html)
inleest.
"""
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
LIVE_URL = "https://tankstationprijzen.nl/goedkoop-tanken-deventer/"
HANDMATIG_FILE = ROOT / "stations_handmatig.json"
OUTPUT_FILE = ROOT / "docs" / "data.json"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TankKompas/1.0"}


def haal_live_stations():
    """Scrapet Tango + TinQ Deventer van tankstationprijzen.nl."""
    stations = []
    try:
        req = urllib.request.Request(LIVE_URL, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        # Elk station zit in <div class="row locatie-rij" ... data-adres="...">
        #   <h2>Naam</h2> ... <tr class="brandstof-rij"><td>Euro 95</td><td>€x.xxx</td>
        blokken = re.findall(
            r'locatie-rij"[^>]*data-adres="([^"]+)".*?<h2>([^<]+)</h2>(.*?)</table>',
            html,
            re.DOTALL,
        )
        for adres, naam, tabel in blokken:
            match = re.search(
                r'<td>\s*Euro\s*95\s*</td>\s*<td>€\s*([\d.,]+)\s*</td>',
                tabel,
                re.IGNORECASE,
            )
            if match:
                prijs = float(match.group(1).replace(",", "."))
                stations.append(
                    {
                        "naam": naam.strip().replace("&#8211;", "-"),
                        "adres": adres.strip() + ", Deventer",
                        "prijs": prijs,
                        "bron": "live",
                    }
                )
    except Exception as e:
        print(f"Kon live prijzen niet ophalen ({e}). Ga verder met handmatige lijst.")
    return stations


def haal_handmatige_stations():
    if not HANDMATIG_FILE.exists():
        return []
    with open(HANDMATIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    for s in data:
        s["bron"] = "handmatig"
    return data


def main():
    live = haal_live_stations()
    live_namen = {s["naam"] for s in live}

    handmatig = [s for s in haal_handmatige_stations() if s["naam"] not in live_namen]

    alle_stations = live + handmatig
    alle_stations.sort(key=lambda s: s["prijs"])

    output = {
        "bijgewerkt": datetime.now(timezone.utc).isoformat(),
        "stations": alle_stations,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Klaar. {len(alle_stations)} stations weggeschreven naar {OUTPUT_FILE}")
    print(f"  - live gescraped: {len(live)}")
    print(f"  - handmatig: {len(handmatig)}")
    if alle_stations:
        w = alle_stations[0]
        print(f"Goedkoopst vandaag: {w['naam']} - €{w['prijs']:.3f}")


if __name__ == "__main__":
    main()
