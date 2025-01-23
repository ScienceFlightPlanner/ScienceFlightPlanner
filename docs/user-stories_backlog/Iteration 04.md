> KW 03/04 (Iteration 04) -> KW 05/06 (Iteration 05)
---
> after meeting w/ AGs on [2025-01-10] & [2025-01-17]
---
#### (X) Docker QGIS Test Suite ausweiten
###### Beschreibung
- Ich möchte, dass keine Fehler für Randfälle des ScienceFlightPlanner auftreten.
###### Akzeptanzkriterium
- Die Docker QGIS Test Suite muss Randfälle des ScienceFlightPlanner abdecken und sicherstellen, dass keine Fehler auftreten. Tests müssen erfolgreich durchlaufen und alle identifizierten Randfälle korrekt behandelt werden.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 10  | Maxim      | 04                     | 21                          | 2.1                 |
###### Bemerkungen
- Tests für Feature 3 & 5 + Plugin allgemein
---
#### (1) Shared Libs statt Python Wrapper für `grdstream`
###### Beschreibung
- Als Entwickler möchte ich grd2stream als Shared Library direkt in Python einbinden, anstatt externe Prozesse per subprocess zu starten für bessere Performance, weniger Disk-I/O und tiefer integrierte Fehlerbehandlung.
###### Akzeptanzkriterium
- Erfolgreiche Cross-Kompilierung von grd2stream mit allen Abhängigkeiten (NetCDF, HDF5, libxml2, curl, zlib)
- Python-Interface implementiert, das direkt mit der Shared Lib kommuniziert

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 20  | Abraham    | 04                     | 30                          | 1.5                 |
###### Bemerkungen
- MinGW als Cross-Compiler
- GitHub Actions als Möglichkeit erstmals selbst auf Mac zu testen (& CI)
---
#### (2) 2 Racetrack Algorithmen implementieren
###### Beschreibung
- Als WissenschaftlerIn möchte ich Flächen, die ich als Grid markiert habe, komplett einscannen und in meinen Flightplan übernehmen. Der ausgewählte Grid soll automatisch anhand des ausgewählten Scanners die richtigen Racetracks berechnen.
###### Akzeptanzkriterium
- Die gesamte markierte Fläche wird durch die generierten Racetracks vollständig abgedeckt. Die Wendemanöver werden so berechnet, dass sie möglichst nahe an der maximalen Turnrate des gewählten Scanners liegen, um eine effiziente Flugplanung zu gewährleisten.
- Automatisch die Turningrate in den Namen der File schreiben
- Default in den Properties setzen

| SPs | Entwickler   | Umgesetzt in Iteration | Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ------------ | ---------------------- | ----------------- | ------------------- |
| 20  | Anna & Simon | 04                     | 18.5+16.5         | 1                   |
###### Bemerkungen
- Default Turning Rate: zwischen 2 & 4 tausend Metern
- Icon noch ergänzen & Debugging-Fenster entfernen!
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