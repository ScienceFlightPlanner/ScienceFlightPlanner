> KW 47/48 (Iteration 01) -> KW 49/50 (Iteration 02)
---
#### (1) QGIS plugin für Berechnung von Fließlinien auf Basis des codes grd2stream, Verfügbarkeit der Fließlinien im Science Flight Planner
###### Beschreibung
- Als WissenschaftlerIn möchte ich Fließlinien aus gerasterten Geschwindigkeitsfeldern (gridded velocity fields) berechnen und in meinen Flugplan übernehmen.
###### Akzeptanzkriterium
- Die Fließlinien sind aus gerasterten Geschwindigkeitsfeldern (gridded velocity fields) mittels  Runge-Kutta-Verfahren korrekt berechnet und sind in dem Flugplan angezeigt.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 9   |            |                        |                             |                     |
###### Bemerkungen
- ...
---
#### (2) Grids in Racetrack/Pendelflug Flightplans überführen
###### Beschreibung
- Als WissenschaftlerIn möchte ich bestimmte Flächen, die ich als Grid markiert habe komplett einscannen und so in meinen Flightplan übernehmen. Der ausgewählte Grid soll automatisch anhand des ausgewählten Scanners die richtigen Racetracks berechnen und so sinnvoll in den Flightplan eingefügt werden.
###### Akzeptanzkriterium
- ...

| SPs | Entwickler | Umgesetzt in Iteration | Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | ----------------- | ------------------- |
| ?   |            |                        |                   |                     |
###### Bemerkungen
- ...
---
#### (3) Export in Garmin GTN750Xi (Standard Cockpit GPS) Format als User Waypoints (user.wpt) und Flightplan (`gfp`-Files)
###### Beschreibung
- Als Nutzer möchte ich aus meinen, in einem Shapefile gespeicherten, Waypoints durch einen Knopfdruck `.wpt`-Files und `.gfp`-Files für das Garmin GTN750Xi Standard Cockpit GPS generieren können.
###### Akzeptanzkriterium
- Es werden 2 Files generiert, welche vom Garmin GTN750Xi Standard Cockpit GPS eingelesen werden können und die Waypoints mit ihren Tags korrekt abbilden.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 3   | Maxim      |                        |                             |                     |
###### Bemerkungen
- ...
---
#### (4) Möglichkeit einzelne Grids (berechnet aus dem aktuellen Science Flight Planner) in einzelne `gfp`-Files zu exportieren und sie ebenso in einen Flugplan zusammenzufassen
###### Beschreibung
- Als WissenschaftlerIn möchte ich dynamisch anhand der aktuellen Gegebenheiten auf meinem Forschungsflug, verschiedene Grids auswählen, sodass ich verschiedene Areas of Interest einfach in einem Flightplan zusammenfügen kann.
###### Akzeptanzkriterium
- Es wird nach Auswahl der Area of Interest (AoI) und drücken des dazugehörigen Knopfes ein separates `gfp`-File erstellt, das nur die Waypoints aus dieser AoI enthält.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 2   |            |                        |                             |                     |
###### Bemerkungen
- Wie wird die richtige Reihenfolge festgelegt?
- Können mehrere `gfp`-Files an das Navigationsgerät übergeben werden, oder müssen die files zusammengefügt werden?
- ...
---
#### (5) Einführen von tags für waypoints, die Informationen für Piloten zur Verfügung stellen (270° turn, 180° turn, transition etc)
###### Beschreibung
- Als Nutzer möchte ich meinen Waypoints sowohl vor- als auch benutzerdefinierte Tags geben
###### Akzeptanzkriterium
- Die Auswahl der Tags wird korrekt angezeigt und die Tags werden korrekt gespeichert. Die benutzerdefinierten Tags sind maximal 25 Zeichen lang und stehen dem Piloten so nach Export im Navigationsgerät zur Verfügung.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 6   | Maxim      |                        |                             |                     |
###### Bemerkungen
- ...
---
##### (6) Extraktion des Topographieprofiles entlang des Flugplans und Berechnung von Sink/Steigraten und Abgleich mit kritischen Zonen von Sensoren
###### Beschreibung
- Als WissenschaftlerIn, der Flüge über Seen plant, möchte ich sehen, wie die Topologie entlang meiner Flugroute aussieht. In dieser Anzeige möchte ich auch sehen, wie die Sink- und Steigraten des Flugzeugs sein müssen, damit die kritischen Abstände für die Lasersensoren eingehalten werden. Ich möchte darauf hingewiesen werden, an welchen Stellen in meinem Flugplan die Abstände zu gering sein könnten, damit ich meine Route entsprechend besser planen kann und alle erforderlichen Abstände eingehalten werden.
###### Akzeptanzkriterium
- Für jede geplante Route gibt es eine Anzeige, in der die Topologie entland dieser anzeigt, sowie Stellen markiert, an der die nötigen Höhen-Abstände nicht eingehalten werden können.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 9   |            |                        |                             |                     |
###### Bemerkungen
- Nicht MVP, mehrere Punkte müssen noch geklärt werden, wie Topologie in Teardrops, die dem Piloten frei stehen zu fliegen, wie er möchte, etc.