import json
import os
import subprocess
from datetime import datetime, timezone


BRON_API = "https://www.oliehandel.nl/rest/V1/oliehandel/fuelstations/nearby"
BRON_PAGINA = "https://www.oliehandel.nl/tankstations"
REGIO_COORDINATEN = {
    "Deventer": (52.250000, 6.160000),
    "Twello": (52.236000, 6.102000),
    "Bathmen": (52.250000, 6.287000),
    "Schalkhaar": (52.255000, 6.194000),
    "Diepenveen": (52.295000, 6.142000),
}
BRANDSTOF_API_KEY = {
    "EURO95": "euro95",
    "DIESEL": "diesel",
    "SUPER98": "super98",
}


def haal_stations_op(plaats="Deventer", brandstof="EURO95"):
    stations = []
    coords = REGIO_COORDINATEN.get(plaats)
    fuel_key = BRANDSTOF_API_KEY.get(brandstof)
    if not coords or not fuel_key:
        return stations

    url = (
        f"{BRON_API}?lat={coords[0]:.6f}&lng={coords[1]:.6f}"
        "&radius=15&limit=30"
    )

    try:
        # Systeem-curl gebruikt op macOS en GitHub dezelfde vertrouwde HTTPS-keten.
        result = subprocess.run(
            [
                "curl", "--fail", "--silent", "--show-error", "--location",
                "--max-time", "15", "--user-agent", "TankKompas/1.0", url,
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )
        payload = json.loads(result.stdout)
        records = payload[3] if isinstance(payload, list) and len(payload) >= 4 else []
        for record in records:
            prijs_info = (record.get("prices") or {}).get(fuel_key) or {}
            if prijs_info.get("tier") != "actual" or prijs_info.get("is_stale"):
                continue
            naam = str(record.get("name", "")).strip()
            adres = str(record.get("address", "")).strip()
            prijs = prijs_info.get("value")
            if not naam or not adres or not isinstance(prijs, (int, float)):
                continue
            stations.append(
                {
                    "naam": naam,
                    "adres": adres,
                    "prijs": round(float(prijs), 3),
                    "plaats": plaats,
                    "bron": "live",
                    "bron_detail": prijs_info.get("source", "oliehandel"),
                    "bron_gecontroleerd_op": prijs_info.get("fetched_at"),
                    "bron_url": record.get("external_link") or BRON_PAGINA,
                }
            )
    except (OSError, subprocess.SubprocessError, ValueError, TypeError, json.JSONDecodeError):
        return []

    return stations


FALLBACK_DB = {
    "EURO95": [
        {
            "naam": "Tango Siemelinksweg",
            "adres": "Siemelinksweg 25, Deventer",
            "prijs": 2.139,
        },
        {
            "naam": "Tango Piet van Donkplein",
            "adres": "Piet van Donkplein, Deventer",
            "prijs": 2.139,
        },
        {
            "naam": "TinQ Twello",
            "adres": "Rijksstraatweg 50, Twello",
            "prijs": 2.149,
        },
        {
            "naam": "Tango Twello",
            "adres": "Duistervoordseweg 3, Twello",
            "prijs": 2.149,
        },
        {
            "naam": "DCO Rubensstraat",
            "adres": "Rubensstraat 10, Deventer",
            "prijs": 2.159,
        },
        {
            "naam": "TinQ Diepenveenseweg",
            "adres": "Diepenveenseweg 1a, Deventer",
            "prijs": 2.159,
        },
        {
            "naam": "AVIA Dunantlaan",
            "adres": "H Dunantlaan 8, Deventer",
            "prijs": 2.184,
        },
        {
            "naam": "AVIA Schalkhaar",
            "adres": "Koningin Wilhelminalaan 2, Schalkhaar",
            "prijs": 2.189,
        },
        {
            "naam": "Shell Margijnenenk",
            "adres": "Margijnenenk 44, Deventer",
            "prijs": 2.199,
        },
        {
            "naam": "BP Express Zutphenseweg",
            "adres": "Zutphenseweg 17, Deventer",
            "prijs": 2.209,
        },
        {
            "naam": "Shell Bathmen",
            "adres": "Deventerweg 30, Bathmen",
            "prijs": 2.219,
        },
        {
            "naam": "AVIA Bergweide",
            "adres": "Hanzeweg 36, Deventer",
            "prijs": 2.224,
        },
        {
            "naam": "Shell Snipperlingsdijk",
            "adres": "Snipperlingsdijk 48, Deventer",
            "prijs": 2.229,
        },
        {
            "naam": "BP Koerhuis",
            "adres": "Zutphenseweg 51, Deventer",
            "prijs": 2.269,
        },
    ],
    "DIESEL": [
        {
            "naam": "Tango Siemelinksweg",
            "adres": "Siemelinksweg 25, Deventer",
            "prijs": 1.799,
        },
        {
            "naam": "Tango Piet van Donkplein",
            "adres": "Piet van Donkplein, Deventer",
            "prijs": 1.799,
        },
        {
            "naam": "TinQ Twello",
            "adres": "Rijksstraatweg 50, Twello",
            "prijs": 1.809,
        },
        {
            "naam": "TinQ Diepenveenseweg",
            "adres": "Diepenveenseweg 1a, Deventer",
            "prijs": 1.819,
        },
        {
            "naam": "DCO Rubensstraat",
            "adres": "Rubensstraat 10, Deventer",
            "prijs": 1.819,
        },
        {
            "naam": "AVIA Schalkhaar",
            "adres": "Koningin Wilhelminalaan 2, Schalkhaar",
            "prijs": 1.839,
        },
        {
            "naam": "Shell Margijnenenk",
            "adres": "Margijnenenk 44, Deventer",
            "prijs": 1.849,
        },
        {
            "naam": "BP Express Zutphenseweg",
            "adres": "Zutphenseweg 17, Deventer",
            "prijs": 1.859,
        },
        {
            "naam": "BP Koerhuis",
            "adres": "Zutphenseweg 51, Deventer",
            "prijs": 1.899,
        },
    ],
    "SUPER98": [
        {
            "naam": "Tango Siemelinksweg",
            "adres": "Siemelinksweg 25, Deventer",
            "prijs": 2.379,
        },
        {
            "naam": "TinQ Diepenveenseweg",
            "adres": "Diepenveenseweg 1a, Deventer",
            "prijs": 2.389,
        },
        {
            "naam": "Tango Twello",
            "adres": "Duistervoordseweg 3, Twello",
            "prijs": 2.399,
        },
        {
            "naam": "BP Express Zutphenseweg",
            "adres": "Zutphenseweg 17, Deventer",
            "prijs": 2.439,
        },
        {
            "naam": "Shell Snipperlingsdijk",
            "adres": "Snipperlingsdijk 48, Deventer",
            "prijs": 2.479,
        },
    ],
}


def main():
    regios = ["Deventer", "Twello", "Bathmen", "Schalkhaar", "Diepenveen"]
    brandstoffen = ["EURO95", "DIESEL", "SUPER98"]
    output_data = {}
    output_data["aanbiedingen"] = {b: [] for b in brandstoffen}
    gecontroleerd_op = datetime.now(timezone.utc).isoformat()
    status_per_brandstof = {}

    for b in brandstoffen:
        verzameld = []
        geslaagde_regios = 0
        for r in regios:
            scraped = haal_stations_op(r, b)
            if scraped:
                geslaagde_regios += 1
            verzameld.extend(scraped)

        # Ketens gebruiken soms alleen de merknaam; behoud daarom elk station
        # afzonderlijk op basis van naam en adres.
        uniek = {
            f'{item["naam"]}|{item["adres"]}': item
            for item in verzameld
        }
        res_list = list(uniek.values())

        if not res_list:
            res_list = [
                {**item, "bron": "handmatig"}
                for item in FALLBACK_DB.get(b, [])
            ]
            status = "handmatig"
        elif geslaagde_regios == len(regios):
            status = "live"
        else:
            status = "partial"

        res_list.sort(key=lambda x: x["prijs"])

        # Bij een gedeeltelijke live bron blijven extra regionale opties zichtbaar.
        # Ze worden bewust niet als actuele prijs gebruikt: de prijs blijft n.n.b.
        live_keys = {f'{item["naam"]}|{item["adres"]}' for item in res_list}
        suggesties = []
        if len(res_list) < 6:
            for item in FALLBACK_DB.get(b, []):
                key = f'{item["naam"]}|{item["adres"]}'
                if key not in live_keys:
                    suggesties.append({
                        "naam": item["naam"],
                        "adres": item["adres"],
                        "prijs": None,
                        "bron": "suggestie",
                        "tip": "regionale optie · prijs controleren",
                    })

        if res_list:
            duurste = res_list[-1]["prijs"]
            for s in res_list:
                s["besparing_liter"] = round(duurste - s["prijs"], 3)

        output_data[b] = res_list
        output_data.setdefault("suggesties", {})[b] = suggesties
        status_per_brandstof[b] = {
            "status": status,
            "live_stations": sum(1 for item in res_list if item.get("bron") == "live"),
            "regios_met_data": geslaagde_regios,
            "regios_totaal": len(regios),
            "bron": BRON_PAGINA,
            "gecontroleerd_op": gecontroleerd_op,
        }

    output_data["bijgewerkt"] = gecontroleerd_op
    output_data["_meta"] = {
        "merk": "FHJ Brasser · Brasco Holding",
        "bron": BRON_PAGINA,
        "brandstoffen": status_per_brandstof,
    }

    os.makedirs("docs", exist_ok=True)
    json_path = os.path.join("docs", "data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Data succesvol opgeslagen in {json_path}")


if __name__ == "__main__":
    main()
