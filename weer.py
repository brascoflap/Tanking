#!/usr/bin/env python3
"""
TankKompas - weer ophalen

Haalt het actuele weer op bij het dichtstbijzijnde meetstation van Deventer
(Meetstation Heino, Buienradar) en schrijft het naar docs/weer.json.
"""
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
OUTPUT_FILE = ROOT / "docs" / "weer.json"
BRON_URL = "https://json.buienradar.nl/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TankKompas/1.0"}
STATION_NAAM = "Meetstation Heino"  # dichtstbijzijnde station bij Deventer


def main():
    weer = None
    try:
        req = urllib.request.Request(BRON_URL, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        for station in data["actual"]["stationmeasurements"]:
            if station["stationname"] == STATION_NAAM:
                weer = {
                    "temperatuur": round(station["temperature"]),
                    "gevoelstemperatuur": round(station["feeltemperature"]),
                    "omschrijving": station["weatherdescription"],
                    "icoon": station["fullIconUrl"],
                    "windkracht_bft": station["windspeedBft"],
                    "winddichting": station["winddirection"],
                    "tijdstip": station["timestamp"],
                }
                break
    except Exception as e:
        print(f"Kon het weer niet ophalen ({e}).")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(weer, f, ensure_ascii=False, indent=2)

    print(f"Klaar: {weer}" if weer else "Geen weerdata weggeschreven.")


if __name__ == "__main__":
    main()
