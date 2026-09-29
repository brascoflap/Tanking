# TankKompas Deventer

Voor papa: elke dag het goedkoopste tankstation in Deventer, met een knop naar Google Maps.

Vaste merkregel: **FHJ Brasser · Brasco Holding**. Deze naam staat als zichtbare merkstempel, subtiel watermerk, printstempel en metadata in de app.

## Beveiliging

De statische app bevat een browser-CSP, beperkte referrer, geen secrets in de repository en veilige verwerking van station- en nieuwsdata. Prijsdata blijft read-only voor de browser; gebruikersgegevens voor registratie blijven lokaal in `localStorage`. Een statische GitHub Pages-app kan geen server-side geheimen of absolute bescherming tegen client-side wijzigingen bieden.

## Wat erin zit

1. `scrape.py` — haalt automatisch actuele pompprijzen op via de Oliehandel.nl-API, per regio en brandstof. Landgemiddelden en stale prijzen worden bewust uitgesloten. De bronstatus wordt per brandstof opgeslagen als `live`, `partial` of `handmatig`; alleen bij een volledig mislukte bron wordt de fallback gebruikt.
2. `nieuws.py` — haalt gemengde koppen op uit auto/mobiliteit, regio, alternatief/duiding, ICT/cybersecurity en entertainment/televisie. Iedere kop krijgt een categorie en de bronnen worden afgewisseld.
3. `weer.py` — haalt het actuele weer op van het dichtstbijzijnde meetstation (Heino, via Buienradar).
4. `docs/` — de website zelf. Dit is wat papa ziet.
5. `.github/workflows/update.yml` — laat GitHub 's ochtends automatisch alle scripts draaien en de site verversen. Gratis, geen server nodig.

## Live zetten (eenmalig, 5 minuten)

1. Maak een gratis GitHub-account (als je die nog niet hebt) en een nieuwe **public** repository, bijvoorbeeld `tankkompas`.
2. Push deze map ernaartoe:
   ```
   git init
   git add .
   git commit -m "TankKompas"
   git branch -M main
   git remote add origin https://github.com/<jouw-gebruikersnaam>/tankkompas.git
   git push -u origin main
   ```
3. Op GitHub: **Settings → Pages → Source: GitHub Actions**.
4. Op GitHub: **Settings → Actions → General → Workflow permissions** → zet op "Read and write permissions" (nodig zodat de robot de prijzen mag bijwerken).
5. Klaar. De site staat live op `https://<jouw-gebruikersnaam>.github.io/tankkompas/` en ververst zichzelf elke ochtend.

## Op de telefoon van papa (Samsung S25 Ultra)

1. Open de link hierboven in Chrome.
2. Menu (drie puntjes) → **App installeren** / **Toevoegen aan startscherm**.
3. Er verschijnt een TankKompas-icoontje op zijn scherm, alsof het een echte app is.

## Op de laptop (Asus TUF)

1. Open de link in Chrome of Edge.
2. Klik op het install-icoontje rechts in de adresbalk (of menu → "App installeren").
3. Hij kan 'm vastpinnen aan de taakbalk.

## Prijzen van de overige stations bijwerken

Open `stations_handmatig.json`, pas een prijs aan, commit en push — de site staat er de volgende ochtend op (of meteen, via **Actions → Prijzen bijwerken → Run workflow**).
