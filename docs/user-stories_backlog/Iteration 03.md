> KW 51/02 (Iteration 03) -> KW 03/04 (Iteration 04)
---
> after winter break
---
#### (X) Recherche zu Docker QGIS Test Suite
###### Beschreibung
- Ich möchte, dass keine Fehler für Randfälle des ScienceFlightPlanner auftreten.
###### Akzeptanzkriterium
- Die Docker QGIS Test Suite muss Randfälle des ScienceFlightPlanner abdecken und sicherstellen, dass keine Fehler auftreten. Tests müssen erfolgreich durchlaufen und alle identifizierten Randfälle korrekt behandelt werden.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 10  | Maxim      | 03                     | 35                          | 3.5                 |
###### Bemerkungen
- Tests für Feature 3 bereits erstellt
---
#### (1.1) Erstellung eines separaten `grdstream` Plugins
###### Beschreibung
- Ich möchte einen vom ScienceFlightPlanner seperaten Plugin.
###### Akzeptanzkriterium
- In der selben GitHub Organisation wurde ein weiteres Repository erstellt. Zudem wurden die Zugangsdaten zum OSGeo-Account sichergestellt damit dieses weitere Plugin released werden kann.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 1   | Maxim      | 03                     | 2                           | 2                   |
###### Bemerkungen
- https://github.com/ScienceFlightPlanner/grd2stream-QGIS-Plugin
---
#### (1.2) Entwicklung eines Python Wrappers für `grdstream`
###### Beschreibung
- vereinfacht die Nutzung in Python (auch im Interesse von Thomas Kleiner)
###### Akzeptanzkriterium
- Funktionalität des Wrappers deckt Randfälle und Fehlerbehandlungen ab
- ist ausreichend dokumentiert

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 10  | Abraham    |                        | 40                          | 4                   |
###### Bemerkungen
- alternativ --> Shared Libs Ansatz
---
#### (2) Waypoints für Racetrack generieren
###### Beschreibung
- Als WissenschaftlerIn möchte ich bestimmte Flächen, die ich als Grid markiert habe komplett einscannen und so in meinen Flightplan übernehmen. Der ausgewählte Grid soll automatisch anhand des ausgewählten Scanners die richtigen Racetracks berechnen und so sinnvoll in den Flightplan eingefügt werden.
###### Akzeptanzkriterium
- Nach Auswählen eines Polygons und klicken eines Knopfes, kann entweder ausgewählt werden, wie viele Meter ein Wendekreis mindestens groß sein soll, oder wie viele Tracks in einer Wendung übersprungen werden sollen. Nach Auswahl und Bestätigung werden Racetracks generiert und so verbunden, wie zuvor durch die Auswahl spezifiziert wurde. Die Punkte werden mit den neuen höchsten IDs generiert und als sperate Objekte hinzugefügt.

| SPs | Entwickler   | Umgesetzt in Iteration | Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ------------ | ---------------------- | ----------------- | ------------------- |
| 10  | Anna & Simon | 3                      | 31+31             | 3                   |
###### Bemerkungen
- Anzahl oder Wendekreis angeben ermöglichen!
---
#### #### (3) Format vom Garmin-Export anpassen
###### Beschreibung
- Als Nutzer möchte ich aus meinen, in einem Shapefile gespeicherten, Waypoints durch einen Knopfdruck fürs Garmin GTN750Xi Standard Cockpit GPS generieren können.
###### Akzeptanzkriterium
- Es werden 2 Files (`.wpt` & `.gfp`), welche vom Garmin GTN750Xi Standard Cockpit GPS eingelesen werden können und die Waypoints mit ihren Tags korrekt abbilden.
- Das Koordinatenformat ist korrekt.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 1   | Maxim      | 03                     | 2                           | 2                   |
###### Bemerkungen
- ...
---
#### (4) Grids/gfp-files Zusammenfügen
###### Beschreibung
- Als WissenschaftlerIn möchte ich dynamisch anhand der aktuellen Gegebenheiten auf meinem Forschungsflug Flightplans zusammenfügen können.
###### Akzeptanzkriterium
- Wenn mehrere gfp-files ausgewählt sind, soll es durch drücken eines Knopfes möglich sein, diese in einen einzigen flight plan **zusammenzufügen** (points --> flightplan).
- Funktioniert für verschiedene Grids oder `.gfp` files!

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 4   | /          | /                      | /                           | /                   |
###### Bemerkungen
- Nicht MVP
---
#### (5) Format von Tags für Waypoints
###### Beschreibung
- Als Nutzer möchte ich meinen Waypoints sowohl vor- (270°/180° RH/LH turn, fly-over, fly-by) als auch benutzerdefinierte Tags geben, **die ich in meinem Garmin vollständig sehen kann.**
###### Akzeptanzkriterium
- Die Auswahl der Tags wird korrekt angezeigt und die Tags werden korrekt gespeichert. Die benutzerdefinierten Tags **sind maximal 10 Zeichen lang** und stehen dem Piloten so nach Export im Navigationsgerät zur Verfügung.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 3   | Maxim      | 03                     | 6                           | 2                   |
###### Bemerkungen
- 25 --> 10
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