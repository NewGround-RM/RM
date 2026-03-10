---
name: geo-auswertung
description: >
  Erzeugt visuelle Auswertungen aus GEO-Kodierungsergebnissen. Liest die
  UEBERSICHT-YAML-Datei und generiert ein interaktives HTML-Dashboard mit
  Filterfunktionen, Sortierung und Summary-Cards. Nutze diesen Skill wenn
  der User Kodierungen visualisieren, als Dashboard darstellen, HTML-Übersicht
  oder Auswertung erzeugen möchte.
---

# GEO Auswertung

Erzeugt visuelle Auswertungen und Dashboards aus Kodierungsergebnissen.

## Voraussetzung

Im Kodierungsverzeichnis muss eine `UEBERSICHT_[Institution]_[Datum].yaml`
vorhanden sein. Diese wird vom Kodierungs-Skill (skills/kodierung) erzeugt.

## Workflow: YAML → HTML-Dashboard

### 1. Input

Claude liest die UEBERSICHT-YAML aus dem Kodierungsverzeichnis.

### 2. HTML generieren

Claude erzeugt eine eigenständige HTML-Datei (kein Framework nötig, nur
CDN-Fonts) mit folgenden Elementen:

**Header:**
- Institution, Modell, Kodierer, Datum

**Summary-Cards (oben):**
- Anzahl Prompts
- Nicht sichtbar (S0) mit Prozentangabe
- Sichtbar (S1–S3) mit Aufschlüsselung
- Tonalität (T+/T−/T± Verteilung)
- Positionierung (V+/V− Verteilung)

Die Summary-Cards aktualisieren sich bei Filterwechsel.

**Filterfunktion:**
- Buttons für Kategorien: Alle, Implizit, Explizit, Vergleichend, Kontext., Provokativ
- Zähler-Badge zeigt aktive/gesamt

**Tabelle:**
- Spalten: ID, Kategorie, Kontext, S, K, T, V, R, Th, Anmerkung
- Sortierbar per Klick auf Spaltenheader
- Farbkodierung:
  - S-Codes: Blau-Abstufung (S0 grau → S3 dunkelblau)
  - T-Codes: T+ grün, T0 grau, T± gelb, T− rot
  - V-Codes: V+ grün, V= grau, V− rot
  - Kategorie-Tags: farbige Badges pro Attribut

**Footer:**
- RepMon-Branding, Quelldatei-Verweis

### 3. Design-Prinzipien

- Editorial/analytische Ästhetik, kein generisches Dashboard
- Fonts: DM Serif Display (Header), IBM Plex Sans (Body), IBM Plex Mono (Codes)
- Warmes Off-White (#faf9f7) als Hintergrund
- Single-File HTML (CSS + JS inline), offline lauffähig bis auf Fonts
- Responsive: Tabelle scrollt horizontal auf kleinen Screens

### 4. Output

Claude speichert die HTML-Datei im selben Verzeichnis wie die YAML:

```
UEBERSICHT_[Institution]_[Datum].html
```

Und bietet sie dem User zum Download/Ansicht an.

## Inputs die Claude vom User erfragen muss

1. **Quell-YAML** – Pfad zur UEBERSICHT-YAML (oder Claude sucht sie im
   Kodierungsverzeichnis)

## Erweiterungen (geplant)

Folgende Auswertungsformate können künftig ergänzt werden:
- YAML → Excel (sortier-/filterbar)
- Vergleich über mehrere Erhebungszeitpunkte (longitudinal)
- Vergleich über mehrere Modelle
- Radar-Charts für Reputationsprofile
- Aggregation nach Kategorien oder Dimensionen
