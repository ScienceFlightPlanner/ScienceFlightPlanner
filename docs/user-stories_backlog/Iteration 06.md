> KW 07/08 (Iteration 06) -> KW 09/10 (Iteration 07) 
---
> after meeting w/ AGs on [2025-02-07]
---
##### (6.1) Extraktion des Topographieprofiles entlang des Flugplans
###### Beschreibung
- Als WissenschaftlerIn, der Flüge über Seen plant, möchte ich sehen, wie die Topologie entlang meiner Flugroute aussieht. Ich möchte farblich darauf hingewiesen werden, wenn entlang der geplanten Route starke Erhebungen sind, die verhindern, dass bestimmte Sensoren eye-safe genutzt werden können, damit ich meine Route entsprechend besser planen kann.
###### Akzeptanzkriterium
- Für jede geplante Route kann per Knopfdruck ein Höhenprofil berechnet werden
- Automatisches Öffnen eines separaten Fensters für Höhendaten
- Separate Fenster für Höhenprofil-Darstellung
- Topographie-Analyse mit folgenden Eigenschaften:
    - Lineare Interpolation der Höhe alle 1000 Meter
    - X-Achse beschriftet als "Strecke" oder "Distanz"
    - Y-Achse beschriftet als "Elevation" oder "Höhe"
    - Kritische Erhebungen in Rot markiert
    - Visualisierung von Stellen, an denen Sensoren nicht eye-safe genutzt werden können
- Markierung von Bereichen, die das Steigen oder Absinken des Flugzeugs um mindestens eine definierte Höhendifferenz erfordern
- Möglichkeit, verschiedene Sensorhöhen zu definieren

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
- Zusätzlich zur Topologie soll eine geschätzte Flughöhe in das Diagramm eingezeichnet werden
- Implementierung der Steigratenkalkulation mit:
    - Standardwert: 1 km Steigrate
    - Benutzerdefinierte Eingabe alternativer Werte möglich
    - Berechnung basierend auf Mindestabständen für Lasersensoren
- Diagramm mit folgenden Elementen:
    - Visualisierung moderater Steig- und Sinkraten
    - Farbliche Markierung kritischer Flugabschnitte
    - Anzeige der empfohlenen Flughöhen
- Berücksichtigung von Sensorspezifischen Höhenanforderungen
    - Markierung von Höhenbereichen, in denen bestimmte Sensoren nicht einsetzbar sind
- Optionen zur Feinjustierung der Steigratenkonfiguration

| SPs | Entwickler | Umgesetzt in Iteration | Tatsächl. Aufwand (in Std.) | Velocity (Std./SPs) |
| --- | ---------- | ---------------------- | --------------------------- | ------------------- |
| 12  | /          | /                      | /                           | /                   |
###### Bemerkungen
- Nicht MVP