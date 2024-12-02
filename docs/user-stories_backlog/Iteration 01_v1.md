> KW 47/48 (Iteration 01) -> KW 49/50 (Iteration 02)
---
> after meeting w/ AGs on [2024-11-29]
---
#### (1.1) Verständnis für `grd2stream` & dessen Integration
###### Beschreibung
- Als Entwickler möchte ich genau wissen wie `grd2stream` funktioniert (Eingabe, Ausgabe & Umsetzung) um sicherzustellen dass es korrekt integriert wird.
###### Akzeptanzkriterium
- Ich habe eine klare Vorstellung davon, welche Aufgabe `grd2stream` erfüllt bzw. wie es arbeitet, kenne die notwendigen Eingabe- und Ausgabeformate & habe eine Idee davon wie die Funktion mit der restlichen Codebase interagieren soll.

| SPs | Entwickler      | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | --------------- | ---------------------- | --------------------------- | ------------------- |
| 2   | Abraham & Simon |                        |                             |                     |
###### Bemerkungen
- Falls Unklarheiten bleiben, mit Thomas Kleiner in Kontakt setzen.
- ...
---
#### (1.2) Python-Aufruf der `grdstream` C-Bibliothek
###### Beschreibung
- Es wird eine Möglichkeit geschaffen, die Funktionen der `grdstream`-C-Bibliothek aus Python aufzurufen
###### Akzeptanzkriterium
- Alle Kernfunktionen von `grdstream` können aus Python ausgeführt werden & es gibt Unit-Tests, die den reibungslosen Ablauf des Aufrufs in unterschiedlichen Architekturen gewährleisten.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 3   | Abraham    |                        |                             |                     |
###### Bemerkungen
- ...
---
#### (1.3) `grdstream`-Output einlesen und als Punkteketten verarbeiten
###### Beschreibung
- Als Nutzer möchte ich eine CSV-Datei mit Koordinaten einlesen können, um die enthaltenen Punkte als Punktketten in QGIS zu visualisieren.
###### Akzeptanzkriterium
- Die resultierenden Punkteketten sind in QGIS visualisierbar.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 2   | Simon      |                        |                             |                     |
###### Bemerkungen
- ...
---
#### (2) Grids in Racetrack/Pendelflug Flightplans überführen

###### Beschreibung
- Als WissenschaftlerIn möchte ich bestimmte Flächen, die ich als Grid markiert habe komplett einscannen und so in meinen Flightplan übernehmen. Der ausgewählte Grid soll automatisch anhand des ausgewählten Scanners die richtigen Racetracks berechnen und so sinnvoll in den Flightplan eingefügt werden.
###### Akzeptanzkriterium
- Nach Auswählen eines Polygons und klicken eines Knopfes, kann entweder ausgewählt werden, wie viele Meter ein Wendekreis mindestens groß sein soll, oder wie viele Tracks in einer Wendung übersprungen werden sollen. Nach Auswahl und Bestätigung werden Racetracks generiert und so verbunden, wie zuvor durch die Auswahl spezifiziert wurde. Die Punkte werden mit den neuen höchsten IDs generiert und als sperate Objekte hinzugefügt.

| SPs | Entwickler    | Umgesetzt in Iteration | Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ------------- | ---------------------- | ----------------- | ------------------- |
| 9   | Moritz & Anna | /                      | /                 | /                   |
###### Bemerkungen
- Präferenz für die Auswahl?
- ...
---
#### (3) Export in Garmin GTN750Xi (Standard Cockpit GPS) Format
###### Beschreibung
- Als Nutzer möchte ich aus meinen, in einem Shapefile gespeicherten, Waypoints durch einen Knopfdruck in das Format für das Garmin GTN750Xi Standard Cockpit GPS generieren können.
###### Akzeptanzkriterium
- Es werden 2 Files generiert, ein `.gfp` und ein `.wpt` File, welche vom Garmin GTN750Xi Standard Cockpit GPS eingelesen werden können und die Waypoints mit ihren Tags korrekt abbilden.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 3   | Maxim      |                        | 6                           |                     |
###### Bemerkungen
- ...
---
#### (4) Grids/`gfp`-Files Zusammenfügen
###### Beschreibung
- Als WissenschaftlerIn möchte ich dynamisch anhand der aktuellen Gegebenheiten auf meinem Forschungsflug, verschiedene Grids oder `.gfp`-Files auswählen und in einen Flightplan zusammenfügen.
###### Akzeptanzkriterium
- Wenn mehrere `.gfp`-Files ausgewählt sind, soll es durch drücken eines Knopfes möglich sein, diese in einen einzigen Flightplan zusammenzufügen.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 4   | /          | /                      | /                           | /                   |
###### Bemerkungen
- Wie wird die richtige Reihenfolge festgelegt? Vielleicht erst Knopf drücken, dann files in Reihenfolge auswählen?
- Direkte Konvertierung in `.gft` & `.wpt`?
- Anzeige in QGIS und dann exportieren?
- ...
---
#### (5) Tags für Waypoints
###### Beschreibung
- Als Nutzer möchte ich meinen Waypoints sowohl vor- (270°/180° RH/LH turn, fly-over, fly-by) als auch benutzerdefinierte Tags geben.
###### Akzeptanzkriterium
- Die Auswahl der Tags wird korrekt angezeigt und die Tags werden korrekt gespeichert. Die benutzerdefinierten Tags sind maximal 10 Zeichen lang und stehen dem Piloten so nach Export im Navigationsgerät zur Verfügung.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 6   | Maxim      |                        | 8                           |                     |
###### Bemerkungen
- ...
---
##### (6.1) Extraktion des Topographieprofiles entlang des Flugplans
###### Beschreibung
- Als WissenschaftlerIn, der Flüge über Seen plant, möchte ich sehen, wie die Topologie entlang meiner Flugroute aussieht. Ich möchte farblich darauf hingewiesen werden, wenn entlang der geplanten Route starke Erhebungen sind, die verhindern, dass bestimmte Sensoren eye-safe genutzt werden können, damit ich meine Route entsprechend besser planen kann.
###### Akzeptanzkriterium
- Für jede geplante Route kann per Knopfdruck ein Höhenprofil berechnet werden. Dieses wird in einem separaten Fenster geöffnet und zeigt die Topographie entlang der entsprechenden Route. Falls hohe Wände entlang der Route zu finden sind, werden diese mit roter Farbe gekennzeichnet, besonders, wenn diese das steigen oder absinken des Flugzeugs von mindestens einer bestimmten Höhendifferenz verlangen.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 9   | /          | /                      | /                           | /                   |
###### Bemerkungen
- Nicht MVP, mehrere Punkte müssen noch geklärt werden, wie Topologie in Teardrops, die dem Piloten frei stehen zu fliegen, wie er möchte, etc.
---
##### (6.2) Berechnung von Sink/Steigraten
###### Beschreibung
- Als WissenschaftlerIn, der Flüge über Seen plant, möchte ich sehen, wie die Topologie entlang meiner Flugroute aussieht. In dieser Anzeige möchte ich auch sehen, wie die Sink- und Steigraten des Flugzeugs sein müssen, damit die kritischen Abstände für die Lasersensoren eingehalten werden. Diese Sink- und Steigraten möchte ich in einem Diagramm visuell angezeigt bekommen.
###### Akzeptanzkriterium
- Zusätzlich zur Topologie soll eine geschätzte Flughöhe in das Diagramm eingezeichnet werden. Diese soll aufgrund von Mindestabständen berechnet werden und gemäßigte Steig- und Sinkraten nutzen.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 9   | /          | /                      | /                           | /                   |
###### Bemerkungen
- Nicht MVP, mehrere Punkte müssen noch geklärt werden, wie Topologie in Teardrops, die dem Piloten frei stehen zu fliegen, wie er möchte, etc. Wie können Sink- und Steigraten abgeschätzt werden?