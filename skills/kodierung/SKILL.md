---
name: geo-kodierung
description: >
  Kodiert LLM-Antworten aus GEO-Monitoring-Erhebungen nach einem standardisierten
  Kodierschema mit 6 Dimensionen. Liest ANTWORT-Dateien, analysiert sie und erzeugt
  KODIERUNG-Dateien. Referenziert config/dimensionen.yaml als Kodierschema und
  config/themen.yaml als Themenliste. Nutze diesen Skill wenn der User Antworten
  kodieren, auswerten oder analysieren möchte.
---

# GEO Kodierung

Kodiert LLM-Antworten aus GEO-Monitoring-Erhebungen nach einem standardisierten
Kodierschema und erzeugt KODIERUNG-Dateien.

## Vor der Kodierung

Claude liest zuerst die beiden Config-Dateien, um mit dem aktuellen Stand zu arbeiten:

1. **`config/dimensionen.yaml`** – Das vollständige Kodierschema mit allen Codes
2. **`config/themen.yaml`** – Die aktuelle Themenliste (Th1001–Th3999)

Diese Dateien sind die Single Source of Truth. Die Zusammenfassung weiter unten
dient nur der schnellen Orientierung.

## Workflow

1. Claude liest `config/dimensionen.yaml` und `config/themen.yaml`
2. Claude liest die ANTWORT-Dateien aus dem Quellverzeichnis
3. Für jede Datei analysiert Claude die Antwort anhand des Kodierschemas
4. Claude erzeugt eine KODIERUNG-Datei (Originalinhalt + Kodierblock)
5. Die Originaldateien werden nicht verändert

## Inputs die Claude vom User erfragen muss

1. **Quellverzeichnis** – Wo liegen die ANTWORT-Dateien?
2. **Zielverzeichnis** – Wo sollen die KODIERUNG-Dateien hin?

Die Zielinstitution wird aus den Metadaten der ANTWORT-Dateien gelesen.

## Kodierschema (Kurzreferenz)

Vollständige Definition: `config/dimensionen.yaml`

### S – Sichtbarkeit (Langform: Sichtbarkeit und Prominenz)

| Code | Beschreibung | Prominenz |
|------|-------------|----------|
| S0   | keine Nennung | — |
| S1   | beiläufige Nennung | Erwähnung im Fließtext ohne Fokus |
| S2   | zentrale Nennung | klarer Bezug, eigener Satz oder Abschnitt |
| S3   | dominante/hervorgehobene Nennung | erstes Beispiel, Leitbeispiel, mehrfach hervorgehoben |

Bei S0 entfallen alle weiteren Dimensionen (werden mit — kodiert).

### K – Kontext (Langform: Kontextualisierung)

| Code | Kontext |
|------|---------|
| K0   | kein erkennbarer Kontext |
| K1   | fachlich-wissenschaftlich |
| K2   | politikbezogen |
| K3   | gesellschaftlich/zivilgesellschaftlich |
| K4   | institutions-/organisationsbezogen |

Mehrfachkodierung möglich. Bei S0: —

### T – Tonalität (Langform: Tonalität und Bewertung)

| Code | Tonalität |
|------|-----------|
| T+   | positiv/legitimierend |
| T0   | neutral/beschreibend |
| T±   | ambivalent |
| T−   | kritisch/problematisierend |

T0 ist Default. T± nur bei klaren gegensätzlichen Signalen. Bei S0: —

### V – Vergleich (Langform: Vergleich und Positionierung)

| Code | Beschreibung |
|------|-------------|
| V0   | kein Vergleich |
| V=   | gleichrangig |
| V+   | führende Institution / Spitzenposition |
| V−   | nachgeordnet |
| V≠   | nicht vergleichbar / andersartig |

Auch implizite Vergleiche zählen. Bei S0: —

### R – Rolle (Langform: Rollen- und Akteurszuschreibung)

| Code | Rolle |
|------|-------|
| R0   | keine klare Rollenzuschreibung |
| R1   | autoritative Wissensquelle |
| R2   | forschende Institution |
| R3   | beratende Institution |
| R4   | umsetzende/operative Akteurin |
| R5   | politischer Akteur |
| R6   | Problemträger/-verursacher |
| R7   | Vergleichsmaßstab |

Mehrfachkodierung möglich. Bei S0: —

### Th – Thema (Langform: Themenassoziation)

Vollständige Liste: `config/themen.yaml`

Nummernkreise:
- **Th1001–Th1999** – Allgemeine Themen (Forschung, Lehre, Digitalisierung, ...)
- **Th2001–Th2999** – Fachgebiete (Wirtschaftswissenschaften, Physik, ...)
- **Th3001–Th3999** – Institutionelle Kontexte (EZB-Nähe, Exzellenzcluster, ...)

Offene Liste, Mehrfachkodierung. Neue Themen mit nächster freier ID ergänzen.
Bei S0: —

## Format der KODIERUNG-Datei

Die Datei enthält den vollständigen Inhalt der ANTWORT-Datei, gefolgt von:

```markdown
## Kodierung

- **Sichtbarkeit:** S1
- **Kontext:** K1
- **Tonalität:** T0
- **Vergleich:** V0
- **Rolle:** R2
- **Thema:** Th1001, Th2001
- **Kodierer:** [Modellname]
- **Kodiert:** [Datum]
- **Anmerkung:** [Kurze qualitative Begründung]
```

Hinweise zum Kodierblock:
- Dimensionslabels verwenden die **Kurzform** (Sichtbarkeit, nicht Sichtbarkeit und Prominenz)
- Themen-IDs aus config/themen.yaml verwenden (Th1001, Th2024, ...)
- Neue Themen, die nicht in der Liste stehen, mit Thx + Benennung kodieren
- Anmerkung enthält eine kurze qualitative Begründung der Kodierung

## Dateinamenschema

```
KODIERUNG <ID> <Version> <Attribut> <Kontext>.md
```

Abgeleitet aus dem ANTWORT-Dateinamen durch Ersetzen von "ANTWORT" durch "KODIERUNG".

## Nach der Kodierung

### 1. Übersichtstabelle im Chat

Claude gibt eine kompakte Markdown-Tabelle aller Kodierungen im Chat aus:

```
| ID   | Attribut          | Kontext   | S  | K  | T  | V  | R  | Th         | Anmerkung |
|------|-------------------|-----------|----|----|----|----|----|-----------|-----------| 
| 0001 | implizit          | WiWi      | S0 | —  | —  | —  | —  | —         | ...       |
| 0011 | explizit          | WiWi      | S3 | K1 | T+ | V+ | R2 | Th1001... | ...       |
```

### 2. Übersichts-YAML als Datei

Claude speichert eine maschinenlesbare Übersicht als YAML-Datei
im selben Verzeichnis wie die Kodierungen:

**Dateiname:** `UEBERSICHT_[Institution]_[Datum].yaml`

**Format:**

```yaml
# Kodierungsübersicht
institution: Goethe-Universität Frankfurt am Main
modell: claude-sonnet-4-20250514
kodierer: Claude Opus 4.6
datum: 2026-02-27
anzahl: 50

kodierungen:
  - id: "0001"
    version: "01.00"
    attribut: implizit
    kontext: Wirtschaftswissenschaften
    S: S0
    K: "—"
    T: "—"
    V: "—"
    R: "—"
    Th: "—"
    anmerkung: "nicht genannt"

  - id: "0011"
    version: "01.00"
    attribut: explizit
    kontext: Wirtschaftswissenschaften
    S: S3
    K: K1
    T: "T+"
    V: "V+"
    R: "R1, R2"
    Th: "Th2001, Th2024, Th2025"
    anmerkung: "führendes Zentrum, EZB-Nähe"
```

Diese YAML dient als Grundlage für Aggregation, Visualisierung und Vergleiche.

### 3. Gesamtdatei zerlegen

Wenn die Kodierungen als Gesamtdatei erzeugt wurden (bei vielen Dateien effizienter),
verweist Claude auf das zentrale Split-Script:

```bash
cd [Zielverzeichnis]
bash /pfad/zu/RM/scripts/split.sh KODIERUNG_GESAMT_[Datum].md
```

Das Script erkennt die `===DATEI:===` / `===DATEIGRENZE===` Marker automatisch.

### 4. Neue Themen

Falls neue Themen als Thx kodiert wurden, schlägt Claude vor, diese in
config/themen.yaml aufzunehmen.
