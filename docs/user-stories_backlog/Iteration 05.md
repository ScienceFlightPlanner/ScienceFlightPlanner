> KW 05/06 (Iteration 05 -> KW 07/08 (Iteration 06)
---
> after meeting w/ AGs on [2025-01-24]
---
#### (1) Conda-basierte Lokalkompilierung von `grdstream`
###### Beschreibung
Als Wissenschaftler/in möchte ich grd2stream einfach und reproduzierbar auf meinem lokalen System installieren können, ohne komplexe Kompilierungsschritte.
###### Akzeptanzkriterium
- Unterstützung für UNIX-Betriebssysteme (& Windows)
- Automatische Auflösung von Abhängigkeiten

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 15  | Abraham    | 05                     | 25                          | 1.66                |
###### Bemerkungen
- GitHub Actions zur CI
---
#### (3) Robuste Tag-Validierung für User Waypoints
###### Beschreibung
- Als WissenschaftlerIn möchte ich eine zuverlässige und sichere Methode zur Erstellung von benutzerdefinierten Tags haben, die Fehleingaben verhindert und den Garmin-Spezifikationen entspricht.
###### Akzeptanzkriterium
- Sanitize-Funktion implementiert, die nur erlaubte Zeichen in Tags zulässt (siehe Manual)
- Verhinderung der Tag-Eingabe, wenn kein Waypoint ausgewählt ist
- Benutzerfreundliche Fehlermeldungen bei ungültigen Eingaben / Automatische Bereinigung von Tag-Eingaben

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 3   | Maxim      | 05                     | 5                           | 1.66                |
###### Bemerkungen
- CRS Übersetzung!
---
#### (4) Prototyp fürs Zusammenfügen von Grids/gfp-files
###### Beschreibung
- Als WissenschaftlerIn möchte ich dynamisch anhand der aktuellen Gegebenheiten auf meinem Forschungsflug Flightplans zusammenfügen können.
###### Akzeptanzkriterium
- Wenn mehrere gfp-files ausgewählt sind, soll es durch drücken eines Knopfes möglich sein, diese in einen einzigen flight plan **zusammenzufügen** (points --> flightplan).
- Funktioniert für verschiedene Grids oder `.gfp` files!

| SPs | Entwickler   | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ------------ | ---------------------- | --------------------------- | ------------------- |
| 2   | Anna & Simon | 05                     | 3+3                         | 1.5                 |
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
- Nicht MVP
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
- Nicht MVP