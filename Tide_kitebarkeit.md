# Tide-Kitebarkeit

## Ziel

Diese Uebersicht bewertet fuer jeden Spot, ob die Tide auf Destinationsebene einen **klar negativen Einfluss auf die Kitebarkeit** hat und deshalb in der App zu einem **Abzug von 0.5 bis 1.5 Sternen** fuehren soll.

Wichtige Abgrenzung:
- Die App bewertet aktuell **Destinationen**, nicht einzelne Unterspots innerhalb einer Destination.
- Ich ziehe nur dann Sterne ab, wenn die verfuegbaren Online-Quellen eine **wiederholbare negative Tide-Situation** fuer den typischen Sessionspot beschreiben.
- Wenn die Quellenlage gemischt ist, die Tide eher nur den Character aendert oder positive und negative Effekte zugleich hat, setze ich **keinen generischen Abzug**.

## Umgesetzte Tide-Abzuege

### Denmark | Hvide Sande
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Die verfuegbaren Quellen beschreiben die Destination ueber Nordsee plus Fjord-Optionen, aber ohne klaren, wiederholbaren astronomischen Tide-Trigger fuer schlechtere Kitebarkeit.
- Quellen: `[S6]`

### Germany | Fehmarn
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Fehmarn ist im Ostsee-Kontext und die Quelle beschreibt vor allem viele Einstiege und Flachwasseroptionen. Auf Destinationsebene gibt es keinen klaren negativen Tide-Trigger.
- Quellen: `[S7]`

### Italy | Sicily
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Lo Stagnone wird in den Spotquellen explizit als nur schwach tideabhaengig beschrieben. Das passt nicht zu einem generischen Strafabzug.
- Quellen: `[S8]`

### Morocco | Essaouira
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Hoehere Tide veraendert Shorebreak und Wellenbild, aber ich habe keine belastbare, einfache Schwelle gefunden, ab der die Destination insgesamt klar schlechter kitebar wird.
- Quellen: `[S9]`

### Morocco | Dakhla
- Bewertung: `Tide-Abzug aktiv`
- Regel:
  - `tide < -0.2 m` -> `-1.0 Sterne`
  - `tide < -0.8 m` -> `-1.5 Sterne`
- Warum: Die Holiday- und Spotseiten beschreiben die Lagune bei mehr Wasser als besonders gut und bei sehr niedrigem Wasser als deutlich eingeschraenkt. Das ist ein klarer, wiederholbarer Negativfall.
- Quellen: `[S2]`, `[S19]`

### Spain | Tarifa
- Bewertung: `kein generischer Tide-Abzug`
- Warum: In Tarifa aendert die Tide einzelne Beach-Setups, etwa Lagunenbildung oder Breite des Strands, aber die Destination bleibt nicht allgemein tidebedingt schlechter kitebar.
- Quellen: `[S20]`

### Spain | Fuerteventura
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Die Quellen beschreiben tideabhaengige Unterschiede einzelner Spot-Varianten, aber keine robuste Destination-Regel fuer einen pauschalen Abzug.
- Quellen: `[S10]`, `[S21]`

### Sardinia | Kite2Sail
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Das Produkt ist ein bootsbasiertes Multi-Spot-Setup. Ohne fixen Homespot ist ein einheitlicher astronomischer Tide-Abzug auf Destinationsebene nicht belastbar.
- Quellen: `[S11]`

### Greece | Kos
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Die Quellen betonen Meltemi und Spotwahl, nicht Tide-Limits. Auf Destinationsebene gibt es keinen klaren negativen Tide-Trigger.
- Quellen: `[S12]`, `[S22]`

### Egypt | El Gouna
- Bewertung: `kein generischer Tide-Abzug`
- Warum: El Gouna ist flach und bei wenig Wasser teils lauffaellig, die Quellen beschreiben den Spot aber nicht als tidekritisch genug fuer einen pauschalen Strafabzug.
- Quellen: `[S13]`, `[S23]`

### Egypt | Seahorse Bay
- Bewertung: `Tide-Abzug aktiv`
- Regel:
  - `tide < 0.1 m` -> `-1.0 Sterne`
  - `tide < -0.4 m` -> `-1.5 Sterne`
- Warum: Mehrere Quellen beschreiben sehr flaches Wasser, Korallen und einen klaren Qualitaetsverlust bei wenig Wasser. Das ist der deutlichste tidekritische Spot im aktuellen Set.
- Quellen: `[S1]`, `[S24]`

### Tunisia | Djerba
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Die Quelle beschreibt den Spot explizit als nur gering tideabhaengig. Deshalb kein pauschaler Abzug.
- Quellen: `KiteWorldWide-Recherche waehrend dieses Schritts; keine belastbare, spot-genaue URL mit klarerer Tide-Aussage gespeichert`

### Cape Verde | Sal
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Tide spielt fuer einzelne Wave-Spots wie Ponta Preta eine Rolle, die Destination `Sal` in der App ist aber breiter als dieser Unterspot. Kein generischer Abzug.
- Quellen: `[S15]`, `[S25]`

### Brazil | Tatajuba
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Bei Ebbe veraendert sich der Charakter stark und die Lagune kann ausduennen, aber die Quellen beschreiben weiter kitebare Alternativen nach kurzem Walk. Kein harter Destination-Abzug.
- Quellen: `[S16]`, `[S26]`

### Brazil | Prea
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Die Quellenlage ist gemischt. Einzelne Beschreibungen sagen, dass Prea nur moderat tideabhaengig ist oder praktisch auf allen Tiden funktioniert. Daher kein pauschaler Abzug.
- Quellen: `Recherche mit allgemeinen Spotguides; keine ausreichend belastbare destination-spezifische Quelle mit klarer Negativschwelle gespeichert`

### Brazil | Jericoacoara
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Ich habe keine ausreichend robuste, destinationsweite Tide-Schwelle gefunden, die klar und wiederholt negativ fuer die allgemeine Kitebarkeit ist.
- Quellen: `keine ausreichend belastbare destination-spezifische Quelle gefunden`

### Brazil | Kite Safari
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Das Produkt ist eine Route mit mehreren Lagunen, Muendungen und Ozean-Spots. Tide beeinflusst die Spotwahl stark, aber nicht sinnvoll als eine einzige globale Strafregel.
- Quellen: `[S16]`

### Panama | Punta Chame
- Bewertung: `Tide-Abzug aktiv`
- Regel:
  - `tide > 1.2 m` -> `-0.5 Sterne`
- Warum: Die Quellen beschreiben sehr gute Bedingungen auf den Flats, aber auch, dass bei sehr hohem Wasser die Beach-Zone zeitweise verschwindet. Das ist ein klarer, wenn auch eher milder Negativfall.
- Quellen: `[S3]`, `[S17]`

### Zanzibar | Jambiani
- Bewertung: `Tide-Abzug aktiv`
- Regel:
  - `tide < 0.0 m` -> `-0.5 Sterne`
  - `tide > 1.0 m` -> `-1.0 Sterne`
- Warum: Bei sehr wenig Wasser wird der Walk ueber das Reef-Flat lang; bei viel Wasser wird das Spot-Setup technischer. Beide Extreme sind in den Quellen klar beschrieben.
- Quellen: `[S4]`, `[S5]`

### Kenya | Mwazaro Beach
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Die verfuegbare Beschreibung betont ganzjaehrig stehbares Wasser und nennt keinen klaren tidebedingten Negativfall fuer den Homespot.
- Quellen: `[S18]`

### South Africa | Cape Town
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Einzelne Wave-Spots aendern sich mit der Tide, aber fuer die Destination `Cape Town` finde ich keine robuste globale Schwelle, die klar Sterne kosten sollte.
- Quellen: `[S28]`

### Sri Lanka | Kalpitiya
- Bewertung: `kein generischer Tide-Abzug`
- Warum: Die Quellen nennen Tide-Effekte, aber ohne klare negative Schwelle fuer die Destination als Ganzes. Deshalb kein pauschaler Abzug.
- Quellen: `[S29]`, `[S30]`

## Zusammenfassung der Code-Umsetzung

Aktiv als Sternabzug in der App:
- `Egypt | Seahorse Bay`
- `Morocco | Dakhla`
- `Panama | Punta Chame`
- `Zanzibar | Jambiani`

Bewusst **nicht** als generischer Sternabzug umgesetzt:
- alle anderen Spots, weil die Tide dort entweder nur den Spot-Character aendert, spot-spezifisch statt destinationsweit ist oder die Quellen keine belastbare Negativschwelle hergeben.

## Quellen

- `[S1]` KiteWorldWide, Seahorse Bay holiday page: `https://kiteworldwide.com/kiteholidays/kitesurfing-in-egypt-seahorse-bay/`
- `[S2]` KiteWorldWide, Dakhla holiday page: `https://kiteworldwide.com/kiteholidays/kitesurfing-in-morocco-dakhla/`
- `[S3]` Panama Kite Center, spot description: `https://www.panamakitecenter.com/kitesurf`
- `[S4]` KiteWorldWide, Jambiani holiday page: `https://kiteworldwide.com/kiteholidays/kitesurfing-in-zanzibar-jambiani/`
- `[S5]` Zanzibar Kite Paradise, Jambiani spot page: `https://zanzibarkiteparadise.com/zanzibar-kitesurfing-spots/jambiani/`
- `[S6]` KiteWorldWide, Denmark Kite Camp: `https://kiteworldwide.com/kiteholidays/denmark-kite-camp/`
- `[S7]` KiteWorldWide, Fehmarn holiday page: `https://kiteworldwide.com/kiteholidays/kitesurfing-in-fehmarn-germany/`
- `[S8]` KiteWorldWide, Sicily holiday page: `https://kiteworldwide.com/kiteholidays/kitesurfing-in-italy-sicily/`
- `[S9]` KiteWorldWide, Essaouira holiday page: `https://kiteworldwide.com/kiteholidays/kitesurfing-in-morocco-essaouira/`
- `[S10]` KiteWorldWide, Fuerteventura holiday page: `https://kiteworldwide.com/kiteholidays/kitesurfing-in-spain-fuerteventura/`
- `[S11]` KiteWorldWide, Sardinia Kite2Sail: `https://kiteworldwide.com/kiteholidays/sardinia-kite2sail/`
- `[S12]` KiteWorldWide, Kos holiday page: `https://kiteworldwide.com/kiteholidays/kitesurfing-in-greece-kos/`
- `[S13]` KiteWorldWide, El Gouna holiday page: `https://kiteworldwide.com/kiteholidays/kitesurfing-in-egypt-el-gouna/`
- `[S15]` KiteWorldWide, Sal holiday page: `https://kiteworldwide.com/kiteholidays/kitesurfing-in-cape-verde-sal/`
- `[S16]` KiteWorldWide, Tatajuba holiday page: `https://kiteworldwide.com/kiteholidays/kitesurfing-in-brazil-tatajuba/`
- `[S17]` KiteWorldWide, Punta Chame holiday page: `https://kiteworldwide.com/kiteholidays/kitesurfing-in-panama-punta-chame/`
- `[S18]` KiteWorldWide, Kenya Mwazaro Beach holiday page: `https://kiteworldwide.com/kiteholidays/kenya-mwazaro-beach/`
- `[S19]` KiteWorldWide, Dakhla lagoon spot page: `https://kiteworldwide.com/kitespots/kitesurfing-in-morocco-dakhla-kite-lagoon/`
- `[S20]` Tarifa Max, Los Lances Norte guide: `https://www.tarifamax.com/en/kitesurfing/los-lances-north/`
- `[S21]` KiteWorldWide, Matas Bay Fuerteventura spot page: `https://kiteworldwide.com/kitespots/kitesurfing-fuerteventura-kitespot-matas-bay/`
- `[S22]` KiteWorldWide, Kos Marmari spot page: `https://kiteworldwide.com/kitespots/kos-marmari/`
- `[S23]` KiteWorldWide, El Gouna Makani Beach Club spot page: `https://kiteworldwide.com/kitespots/kitesurfing-in-egypt-el-gouna-makani-beachclub/`
- `[S24]` KiteWorldWide, Seahorse Bay spot page: `https://kiteworldwide.com/kitespots/kitesurfing-egypt-kitespot-seahorse-bay/`
- `[S25]` KiteWorldWide, Sal Ponta Preta spot page: `https://kiteworldwide.com/kitespots/kitesurfing-sal-kitespot-ponta-preta/`
- `[S26]` KiteWorldWide, Tatajuba wave spot page: `https://kiteworldwide.com/kitespots/kitesurfing-tatajuba-wave-spot/`
- `[S28]` KiteWorldWide, Cape Town Sunset Beach spot page: `https://kiteworldwide.com/kitespots/kitesurfing-cape-town-kitespot-sunset-beach/`
- `[S29]` KiteWorldWide, Kalpitiya holiday page: `https://kiteworldwide.com/kiteholidays/kitesurfing-in-sri-lanka-kalpitiya/`
- `[S30]` KiteWorldWide, Kalpitiya main spot page: `https://kiteworldwide.com/kitespots/kiteworldwide-kalpitiya-main-spot/`
