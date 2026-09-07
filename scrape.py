import json
import os
import re
import urllib.request


def haal_stations_op(plaats="Deventer", brandstof="EURO95"):
    url = f"https://www.tankje.nl/Location/GasStations/Nederland/{plaats}/{brandstof}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
    }
    stations = []

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=4) as resp:
            html = resp.read().decode("utf-8")
            matches = re.findall(
                r'class="station-title">([^<]+).*?class="address">([^<]+).*?€\s*([\d\.\,]+)',
                html,
                re.DOTALL,
            )
            for m in matches:
                naam = m[0].strip()
                adres = m[1].strip()
                prijs = float(m[2].replace(",", "."))
                stations.append(
                    {
                        "naam": naam,
                        "adres": f"{adres}, {plaats}",
                        "prijs": prijs,
                        "plaats": plaats,
                    }
                )
    except Exception:
        pass

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

    for b in brandstoffen:
        verzameld = []
        for r in regios:
            scraped = haal_stations_op(r, b)
            verzameld.extend(scraped)

        uniek = {item["naam"]: item for item in verzameld}
        res_list = list(uniek.values())

        if not res_list:
            res_list = FALLBACK_DB.get(b, [])

        res_list.sort(key=lambda x: x["prijs"])

        if res_list:
            duurste = res_list[-1]["prijs"]
            for s in res_list:
                s["besparing_liter"] = round(duurste - s["prijs"], 3)

        output_data[b] = res_list

    os.makedirs("docs", exist_ok=True)
    json_path = os.path.join("docs", "data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Data succesvol opgeslagen in {json_path}")


if __name__ == "__main__":
    main()
