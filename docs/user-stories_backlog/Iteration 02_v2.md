> KW 49/50 (Iteration 02) -> KW 51/02 (Iteration 03)
---
> after meeting w/ AGs on [2024-12-13]
> additional (online) meetings w/ AGs were held on [2024-12-17] & [2024-12-18]
---
#### (X) `README` und Help-Manual an implementierte Features anpassen
###### Beschreibung
- Als Nutzer möchte ich, dass die Dokumentation (README und Handbuch) die aktuell implementierten Features widerspiegelt.
###### Akzeptanzkriterium
- Alle relevanten Änderungen oder Ergänzungen werden klar strukturiert und nachvollziehbar in die Dokumentation eingefügt. Zusätzlich wird durch Teamkollegen auf Konsistenz & Verständlichkeit geprüft.

| SPs | Entwickler   | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ------------ | ---------------------- | --------------------------- | ------------------- |
| 3   | Anna & Maxim | 02                     | 8                           | 2.66                |
###### Bemerkungen
- ...
---
#### (X) Toolbar-Buttonleiste im Help-Manual dynamisch setzen
###### Beschreibung
- Als Nutzer möchte ich, dass sich die Toolbar automatisch anpasst, wenn die Fensterbreite zu klein wird, indem die Buttons in eine neue Zeile verschoben werden.
###### Akzeptanzkriterium
- Die Buttons behalten ihre Funktionalität und sind weiterhin vollständig nutzbar. Beim Vergrößern des Fensters kehren die Buttons automatisch in eine Zeile zurück.

| SPs | Entwickler      | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | --------------- | ---------------------- | --------------------------- | ------------------- |
| 3   | Maxim & Abraham |                        | 12                          |                     |
###### Bemerkungen
- ...
---
#### (1.2.1) Python-Aufruf der `grdstream` C-Bibliothek in UNIX 
###### Beschreibung
- Es wird eine Möglichkeit geschaffen, die Funktionen der `grdstream`-C-Bibliothek aus Python auf einem UNIX-System, aufzurufen.
###### Akzeptanzkriterium
- alle Kernfunktionen von `grdstream` können aus Python ausgeführt werden
- es gibt Unit-Tests, die den reibungslosen Aufruf auf UNIX Architekturen gewährleisten.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 5   | Abraham    | 02                     | 14                          | 2.8                 |
###### Bemerkungen
- ...
---
#### (1.2.3) Entwicklung eines Python Wrappers für `grdstream`
###### Beschreibung
- vereinfacht die Nutzung in Python (auch im Interesse von Thomas Kleiner)
###### Akzeptanzkriterium
- Funktionalität des Wrappers deckt Randfälle und Fehlerbehandlungen ab
- ist ausreichend dokumentiert

| SPs | Entwickler      | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | --------------- | ---------------------- | --------------------------- | ------------------- |
| 4   | Abraham & Simon |                        |                             |                     |
###### Bemerkungen
- ...
---
#### (2.1) Verständnis für Grid-Daten & Grundlogik von Racetracks
###### Beschreibung
- Als Entwickler möchte ich verstehen, wie die Auswahl eines Grids funktioniert und welche Parameter (Scanner, Wendekreis, Trackabstände) für die Berechnung der Racetracks oder Pendelflüge relevant sind, um die Basis für die spätere Implementierung zu schaffen.
###### Akzeptanzkriterium
- Die relevanten Parameter (Scanner, Wendekreis, Trackabstände) und deren Einfluss auf die Berechnung der Racetracks sind bekannt und nachvollziehbar.

| SPs | Entwickler    | Umgesetzt in Iteration | Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ------------- | ---------------------- | ----------------- | ------------------- |
| 6   | Moritz & Anna |                        | 10                |                     |
###### Bemerkungen
- Technische Abhängigkeiten?
- Zugriff auf Beispieldaten
- ...
---
#### (2.2) Grids in Racetrack/Pendelflug Flightplans überführen
###### Beschreibung
- Als WissenschaftlerIn möchte ich bestimmte Flächen, die ich als Grid markiert habe komplett einscannen und so in meinen Flightplan übernehmen. Der ausgewählte Grid soll automatisch anhand des ausgewählten Scanners die richtigen Racetracks berechnen und so sinnvoll in den Flightplan eingefügt werden.
###### Akzeptanzkriterium
- Nach Auswählen eines Polygons und klicken eines Knopfes, kann entweder ausgewählt werden, wie viele Meter ein Wendekreis mindestens groß sein soll, oder wie viele Tracks in einer Wendung übersprungen werden sollen. Nach Auswahl und Bestätigung werden Racetracks generiert und so verbunden, wie zuvor durch die Auswahl spezifiziert wurde. Die Punkte werden mit den neuen höchsten IDs generiert und als sperate Objekte hinzugefügt.

| SPs | Entwickler | Umgesetzt in Iteration | Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | ----------------- | ------------------- |
| 9   | /          | /                      | /                 | /                   |
###### Bemerkungen
- Präferenz für die Auswahl?
- ...
---
#### (4) Grids/gfp-files Zusammenfügen
###### Beschreibung
- Als WissenschaftlerIn möchte ich dynamisch anhand der aktuellen Gegebenheiten auf meinem Forschungsflug, verschiedene Grids oder `.gfp` files auswählen und in einen Flightplan zusammenfügen.
###### Akzeptanzkriterium
- Wenn mehrere gfp-files ausgewählt sind, soll es durch drücken eines Knopfes möglich sein, diese in einen einzigen flight plan zusammenzufügen.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 4   | /          | /                      | /                           | /                   |
###### Bemerkungen
- Wie wird die richtige Reihenfolge festgelegt? Vielleicht erst Knopf drücken, dann files in Reihenfolge auswählen? Direkte Konvertierung in `.gft` & `.wpt`? Anzeige in QGIS und dann exportieren?
- ...
---
##### (6) Extraktion des Topographieprofiles entlang des Flugplans
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
##### (6) Berechnung von Sink/Steigraten
###### Beschreibung
- Als WissenschaftlerIn, der Flüge über Seen plant, möchte ich sehen, wie die Topologie entlang meiner Flugroute aussieht. In dieser Anzeige möchte ich auch sehen, wie die Sink- und Steigraten des Flugzeugs sein müssen, damit die kritischen Abstände für die Lasersensoren eingehalten werden. Diese Sink- und Steigraten möchte ich in einem Diagramm visuell angezeigt bekommen.
###### Akzeptanzkriterium
- Zusätzlich zur Topologie soll eine geschätzte Flughöhe in das Diagramm eingezeichnet werden. Diese soll aufgrund von Mindestabständen berechnet werden und gemäßigte Steig- und Sinkraten nutzen.

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 9   | /          | /                      | /                           | /                   |
###### Bemerkungen
- Nicht MVP, mehrere Punkte müssen noch geklärt werden, wie Topologie in Teardrops, die dem Piloten frei stehen zu fliegen, wie er möchte, etc. Wie können Sink- und Steigraten abgeschätzt werden?