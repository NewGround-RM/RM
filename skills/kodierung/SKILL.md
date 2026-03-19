---
name: geo-kodierung
description: >
  Kodiert LLM-Antworten aus GEO-Monitoring-Erhebungen nach einem standardisierten
  Kodierschema mit 6 Dimensionen plus sekundäre Dimensionen. Liest Record-YAML-Dateien
  (gemäß record_schema.yaml), analysiert den antwort_text und schreibt die Kodierfelder
  direkt in dieselbe Datei zurück. Referenziert config/dimensionen.yaml als Kodierschema
  und config/themen.yaml als Themenliste. Nutze diesen Skill wenn der User Antworten
  kodieren, auswerten oder analysieren möchte.
---

# GEO Kodierung

Kodiert LLM-Antworten aus GEO-Monitoring-Erhebungen nach einem standardisierten
Kodierschema. Liest Record-YAML-Dateien, analysiert den `antwort_text` und
schreibt die Kodierfelder direkt in dieselbe Datei zurück.

## Vor der Kodierung

Claude liest zuerst die beiden Config-Dateien, um mit dem aktuellen Stand zu arbeiten:

1. **`config/dimensionen.yaml`** – Das vollständige Kodierschema mit allen Codes
2. **`config/themen.yaml`** – Die aktuelle Themenliste (Th1001–Th3999)

Diese Dateien sind die Single Source of Truth. Die Zusammenfassung weiter unten
dient nur der schnellen Orientierung.

## Workflow

1. Claude liest `config/dimensionen.yaml` und `config/themen.yaml`
2. Claude liest die Record-YAML-Dateien aus dem Quellverzeichnis
3. Für jede Datei analysiert Claude den `antwort_text` anhand des Kodierschemas
4. Claude schreibt die Kodierfelder direkt in dieselbe Record-YAML-Datei zurück:
   `sichtbarkeit`, `kontext`, `tonalitaet`, `vergleich`, `rolle`, `thema`,
   `vollstaendigkeit`, `faktenfehler`, `faktenfehler_detail`,
   `kodiert_von`, `kodiert_am`, `anmerkung`
5. Alle anderen Felder bleiben unverändert

## Inputs die Claude vom User erfragen muss

1. **Quellverzeichnis** – Wo liegen die Record-YAML-Dateien?

Die Zielinstitution und alle weiteren Metadaten werden aus den Record-Dateien gelesen.

## Kodierschema (Kurzreferenz)

Vollständige Definition: `config/dimensionen.yaml`

### S – Sichtbarkeit

| Code | Beschreibung |
|------|-------------|
| S0   | keine Nennung |
| S1   | beiläufige Nennung (Fließtext ohne Fokus) |
| S2   | zentrale Nennung (klarer Bezug, eigener Satz oder Abschnitt) |
| S3   | dominante Nennung (erstes Beispiel, Leitbeispiel, mehrfach hervorgehoben) |

Bei S0 entfallen alle weiteren Dimensionen → alle mit `"—"` belegen.

### K – Kontext

| Code | Kontext |
|------|---------|
| K0   | kein erkennbarer Kontext |
| K1   | fachlich-wissenschaftlich |
| K2   | politikbezogen |
| K3   | gesellschaftlich/zivilgesellschaftlich |
| K4   | institutions-/organisationsbezogen |

Mehrfachkodierung möglich → YAML-Liste, z.B. `["K1", "K4"]`. Bei S0: `"—"`

### T – Tonalität

| Code | Tonalität |
|------|-----------|
| T+   | positiv/legitimierend |
| T0   | neutral/beschreibend (Default) |
| T±   | ambivalent (nur bei klaren gegensätzlichen Signalen) |
| T−   | kritisch/problematisierend |

Bei S0: `"—"`

### V – Vergleich

| Code | Beschreibung |
|------|-------------|
| V0   | kein Vergleich (Default) |
| V=   | gleichrangig |
| V+   | führende Institution / Spitzenposition |
| V−   | nachgeordnet |
| V≠   | nicht vergleichbar / andersartig |

Auch implizite Vergleiche zählen. Bei S0: `"—"`

### R – Rolle

| Code | Rolle |
|------|-------|
| R0   | keine klare Rollenzuschreibung (Default) |
| R1   | autoritative Wissensquelle |
| R2   | forschende Institution |
| R3   | beratende Institution |
| R4   | umsetzende/operative Akteurin |
| R5   | politischer Akteur |
| R6   | Problemträger/-verursacher |
| R7   | Vergleichsmaßstab |

Mehrfachkodierung möglich → YAML-Liste, z.B. `["R1", "R2"]`. Bei S0: `"—"`

### Th – Thema

Vollständige Liste: `config/themen.yaml`

Nummernkreise:
- **Th1001–Th1999** – Allgemeine Themen (Forschung, Lehre, Digitalisierung, ...)
- **Th2001–Th2999** – Fachgebiete (Wirtschaftswissenschaften, Physik, ...)
- **Th3001–Th3999** – Institutionelle Kontexte (EZB-Nähe, Exzellenzcluster, ...)

Mehrfachkodierung → YAML-Liste, z.B. `["Th1001", "Th2024"]`.
Neue Themen mit nächster freier ID als `"Thx: Bezeichnung"` kodieren.
Bei S0: `"—"`

### Sekundäre Dimensionen

**vollstaendigkeit:** `"hoch"` | `"mittel"` | `"niedrig"` | `null`
Bewertet, ob die Antwort die für die Zielinstitution relevanten Aspekte
vollständig abdeckt (unabhängig von Sichtbarkeit).

**faktenfehler:** `true` | `false` | `null`
Wird auf `true` gesetzt, wenn die Antwort nachweislich falsche Aussagen
über die Zielinstitution enthält.

**faktenfehler_detail:** Freitext-Beschreibung des Fehlers, sonst `""`.

## Kodierte Felder im Record-YAML

Claude überschreibt nach der Analyse folgende Felder in der Record-YAML-Datei:

```yaml
sichtbarkeit: "S2"
kontext: ["K1", "K4"]
tonalitaet: "T+"
vergleich: "V+"
rolle: ["R1", "R2"]
thema: ["Th1001", "Th2001", "Th3002"]

vollstaendigkeit: "hoch"
faktenfehler: false
faktenfehler_detail: ""

kodiert_von: "claude-sonnet-4-6"   # oder Name des menschlichen Kodierers
kodiert_am: "2026-03-18"
anmerkung: "Kurze qualitative Begründung der Kodierung, Grenzfälle erläutern"
```

Alle übrigen Felder (Metadaten, prompt_*, antwort_text, intervention_*)
bleiben unverändert.

## Dateinamen

Record-Dateien folgen dem Schema:
```
record <datum> <ziel-institution> <prompt_bezug> <prompt_kategorie> <thema>.yaml
```

Die Dateien werden durch die Kodierung nicht umbenannt.

## Nach der Kodierung

### 1. Übersichtstabelle im Chat

Claude gibt eine kompakte Markdown-Tabelle aller Kodierungen im Chat aus:

```
| prompt_id | prompt_kategorie   | prompt_bezug | S  | K       | T  | V  | R       | Th              | anmerkung |
|-----------|--------------------|--------------|----|---------|----|----|---------|-----------------|-----------|
| 1001-I    | implizit           | institution  | S2 | K1, K4  | T+ | V0 | R1, R2  | Th1001, Th2001  | ...       |
| 1002-T    | implizit           | thema        | S0 | —       | —  | —  | —       | —               | ...       |
```

### 2. Übersichts-YAML als Datei

Claude speichert eine maschinenlesbare Übersicht als YAML-Datei
im selben Verzeichnis wie die Records:

**Dateiname:** `uebersicht_<ziel-institution>_<datum>.yaml`

**Format:**

```yaml
# Kodierungsübersicht
institution: "Goethe-Universität Frankfurt am Main"
modell: "claude-sonnet-4-6"
kodiert_von: "claude-sonnet-4-6"
kodiert_am: "2026-03-18"
anzahl: 15

kodierungen:
  - prompt_id: "1001-I"
    prompt_kategorie: "implizit"
    prompt_bezug: "institution"
    prompt_thema: "Studiumswahl Frankfurt, Wirtschaftswissenschaften"
    S: "S2"
    K: ["K1", "K4"]
    T: "T+"
    V: "V0"
    R: ["R1", "R2"]
    Th: ["Th1001", "Th2001"]
    anmerkung: "..."

  - prompt_id: "1002-T"
    prompt_kategorie: "implizit"
    prompt_bezug: "thema"
    prompt_thema: "Kritische Theorie, gesellschaftliche Machtverhältnisse"
    S: "S0"
    K: "—"
    T: "—"
    V: "—"
    R: "—"
    Th: "—"
    anmerkung: "nicht genannt"
```

Diese YAML dient als Grundlage für Aggregation, Visualisierung und Vergleiche.

### 3. Neue Themen

Falls neue Themen als `Thx` kodiert wurden, schlägt Claude vor, diese in
`config/themen.yaml` aufzunehmen und vergibt dabei die nächste freie ID.
