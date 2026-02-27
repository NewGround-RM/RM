# GEO-Monitoring Workflow

Workflow für die systematische Erhebung und Analyse der Repräsentation einer Institution in KI-Systemen.

## Übersicht

```
Prompts generieren → Erhebung durchführen → Kodierung → Auswertung
     (1)                    (2)                (3)          (4)
```

Jeder Schritt hat definierte Inputs, Outputs, Dateiformate und einen zugehörigen Skill oder ein Tool.

---

## Verzeichnisstruktur

```
_Claude_ GEO monitoring/
└── <Institutionsname>/
    ├── Erhebungs-Prompts/       ← Output Schritt 1
    │   ├── PROMPT 0001 01.00 implizit Wirtschaftswissenschaften.md
    │   ├── PROMPT 0002 01.00 implizit Philosophie_und_Sozialwissenschaften.md
    │   └── ...                  (50 Dateien)
    │
    ├── Antworten/               ← Output Schritt 2
    │   ├── ANTWORT 0001 01.00 implizit Wirtschaftswissenschaften.md
    │   ├── ANTWORT 0002 01.00 implizit Philosophie_und_Sozialwissenschaften.md
    │   └── ...                  (50 Dateien)
    │
    ├── Kodierungen/             ← Output Schritt 3
    │   ├── KODIERUNG 0001 01.00 implizit Wirtschaftswissenschaften.md
    │   ├── KODIERUNG 0002 01.00 implizit Philosophie_und_Sozialwissenschaften.md
    │   └── ...                  (50 Dateien)
    │
    └── Auswertungen/            ← Output Schritt 4
        ├── Sichtbarkeit.jsx
        ├── Uebersichtstabelle.md
        └── ...
```

---

## Dateinamenkonventionen

Alle Dateien folgen dem Schema:

```
<TYP> <ID> <VERSION> <ATTRIBUT> <KONTEXT>.md
```

| Feld | Beschreibung | Beispiel |
|------|-------------|---------|
| TYP | PROMPT, ANTWORT oder KODIERUNG | ANTWORT |
| ID | 4-stellig, durchlaufend 0001–0050 | 0035 |
| VERSION | Major.Minor | 01.00 |
| ATTRIBUT | Prompt-Kategorie | kontextualisierend |
| KONTEXT | Thematischer Kontext, Umlaute ersetzt | Lehrerbildung |

Umlaut-Ersetzung: ä→ae, ö→oe, ü→ue, ß→ss. Leerzeichen und Sonderzeichen → Unterstrich.

---

## Schritt 1: Prompts generieren

**Skill:** `geo-prompt-generator`
**Input:** Institutionsname, Vergleichsinstitutionen, Ausgabeverzeichnis
**Output:** 50 PROMPT-Dateien (je 10 pro Kategorie)

### Prompt-Kategorien und ID-Bereiche

| Kategorie | IDs | Beobachtungsdimensionen |
|---|---|---|
| implizit | 0001–0010 | Sichtbarkeit, Kontextualisierung, Themenassoziation |
| explizit | 0011–0020 | Kontextualisierung, Tonalität, Rollenzuschreibung |
| vergleichend | 0021–0030 | Konkurrenz- und Positionierungslogiken |
| kontextualisierend | 0031–0040 | Kontextualisierung, Tonalität, Rollenzuschreibung, Vergleiche, Themenassoziation |
| provokativ | 0041–0050 | Erfassung problematischer Narrative |

### Ausführung

```bash
python3 generate_prompts.py \
  --institution "Goethe-Universität Frankfurt am Main" \
  --vergleich "LMU München, Universität Heidelberg" \
  --output "/pfad/zu/Erhebungs-Prompts"
```

### Aufbau einer PROMPT-Datei

```markdown
# PROMPT 0035 | Version 01.00 | kontextualisierend | Lehrerbildung

## Prompt
Welche Universitäten gelten in Deutschland als besonders wichtig für die Lehrerbildung?

## Metadaten
- **Prompt-ID:** 0035
- **Version:** 01.00
- **Kontext:** Lehrerbildung
- **Attribut:** kontextualisierend
- **Zielinstitution:** Goethe-Universität Frankfurt am Main
- **Beobachtungsdimensionen:** Kontextualisierung, Tonalität, Rollenzuschreibung, Vergleiche, Themenassoziation
- **Erstellt:** 2026-02-25
```

---

## Schritt 2: Erhebung durchführen

**Tool:** React-Artifact `geo-erhebung`
**Input:** PROMPT-Dateien (die Prompt-Texte sind im Script hinterlegt)
**Output:** ANTWORT-Dateien

### Methodik

- Jeder Prompt wird als **isolierter API-Call** an Claude geschickt (kein Gesprächskontext)
- System-Prompt: Antwort in ca. 250 Zeichen, Deutsch, präzise und informativ
- Modell: claude-sonnet-4-20250514

### Wichtig: Kontextfreiheit

Die Erhebung darf **nicht** im selben Chat erfolgen, in dem über die Institution gesprochen wird. Das Artifact löst das, indem jeder Prompt ein eigener API-Call ohne Kontext ist.

### Ausführung

1. Artifact öffnen
2. Institution, Vergleichsinstitutionen und Version eingeben
3. "Erhebung starten" klicken
4. Nach Abschluss ZIP herunterladen
5. Dateien in den Antworten-Ordner entpacken

### Aufbau einer ANTWORT-Datei

```markdown
# ANTWORT 0035 | Version 01.00 | kontextualisierend | Lehrerbildung

## Antwort
[Antwort des LLM]

## Metadaten
- **Prompt-ID:** 0035
- **Version:** 01.00
- **Kontext:** Lehrerbildung
- **Attribut:** kontextualisierend
- **Zielinstitution:** Goethe-Universität Frankfurt am Main
- **Beobachtungsdimensionen:** Kontextualisierung, Tonalität, Rollenzuschreibung, Vergleiche, Themenassoziation
- **Prompt:** Welche Universitäten gelten in Deutschland als besonders wichtig für die Lehrerbildung?
- **Modell:** claude-sonnet-4-20250514
- **Erhoben:** 2026-02-25
```

---

## Schritt 3: Kodierung

**Skill:** `geo-kodierung`
**Input:** ANTWORT-Dateien, Zielinstitution
**Output:** KODIERUNG-Dateien (Originalinhalt + Kodierblock)

### Kodierschema (6 Dimensionen)

#### Dimension 1: Sichtbarkeit (S)
*Wird die Institution genannt – und wie prominent?*

| Code | Beschreibung |
|------|-------------|
| S0 | keine Nennung |
| S1 | beiläufige Nennung |
| S2 | zentrale Nennung |
| S3 | dominante/hervorgehobene Nennung |

Vermerke: V1 (Fließtext ohne Fokus), V2 (eigener Satz/Abschnitt), V3 (Leitbeispiel, mehrfach hervorgehoben)

#### Dimension 2: Kontext (K)
*In welchem inhaltlichen Rahmen erscheint die Institution?*

| Code | Kontext |
|------|---------|
| K0 | kein erkennbarer Kontext / Default |
| K1 | fachlich-wissenschaftlich |
| K2 | politikbezogen |
| K3 | gesellschaftlich/zivilgesellschaftlich |
| K4 | institutions-/organisationsbezogen |

Mehrfachkodierung möglich. Bei S0 → K0.

#### Dimension 3: Tonalität (T)
*Wie wird die Institution dargestellt?*

| Code | Tonalität |
|------|-----------|
| T+ | positiv/legitimierend |
| T0 | neutral/beschreibend |
| T± | ambivalent |
| T− | kritisch/problematisierend |

T0 ist Default. Bei S0 → nicht kodierbar (—).

#### Dimension 4: Vergleiche (V)
*Wird die Institution relativ zu anderen eingeordnet?*

| Code | Rolle |
|------|-------|
| V0 | kein Vergleich / Default |
| V= | gleichrangig |
| V+ | führende Institution / Spitzenposition |
| V− | nachgeordnet |
| V≠ | nicht vergleichbar / andersartig |

Auch implizite Vergleiche zählen. Bei S0 → V0.

#### Dimension 5: Rolle (R)
*Welche Funktion wird der Institution zugeschrieben?*

| Code | Rolle |
|------|-------|
| R0 | keine klare Rollenzuschreibung / Default |
| R1 | autoritative Wissensquelle |
| R2 | forschende Institution |
| R3 | beratende Institution |
| R4 | umsetzende/operative Akteurin |
| R5 | politischer Akteur |
| R6 | Problemträger/-verursacher |
| R7 | Vergleichsmaßstab |

Mehrfachkodierung möglich. Bei S0 → R0.

#### Dimension 6: Themenassoziation (Th)
*Mit welchen Themen wird die Institution verknüpft?*

| Code | Thema |
|------|-------|
| Th1 | Forschung/Wissenschaft |
| Th2 | Politikberatung |
| Th3 | Innovation/Zukunft |
| Th4 | Ethik/Verantwortung |
| Th5 | Förderung/Finanzierung |
| Th6 | Organisation/Governance |
| Th7 | Kontroversen/Kritik |
| Th8 | Lehre/Studium |
| Th9 | Physik |
| Th10 | Biologie |
| Th11 | transformative Forschung |
| Thx | Sonstiges (benennen) |

Offene Liste, Mehrfachkodierung. Bei S0 → nicht kodierbar (—).

### Ausführung

Claude mit dem Skill beauftragen:
> "Kodiere die Antworten in [Quellverzeichnis] für [Institution] und speichere die Kodierungen in [Zielverzeichnis]."

### Aufbau einer KODIERUNG-Datei

Vollständiger Inhalt der ANTWORT-Datei, ergänzt um:

```markdown
## Kodierung

- **Sichtbarkeit:** S2 (V2)
- **Kontext:** K4
- **Tonalität:** T−
- **Vergleiche:** V−
- **Rolle:** R6
- **Themenassoziation:** Th6, Th7, Th8
- **Kodierer:** Claude Opus 4.6
- **Kodiert:** 2026-02-26
- **Anmerkung:** [Qualitative Begründung]
```

---

## Schritt 4: Auswertung

**Tools:** React-Artifacts, Übersichtstabellen, ggf. Excel
**Input:** KODIERUNG-Dateien
**Output:** Visualisierungen, Aggregationstabellen

### Aggregationsebenen

**Ebene 1 – Verteilung pro Dimension:**
Wie oft kommt jeder Code vor? z.B. S0: 12× | S1: 15× | S2: 13× | S3: 10×

**Ebene 2 – Kreuzmatrix Kategorie × Dimension:**
Pro Prompt-Kategorie den dominanten Code je Dimension zeigen.

**Ebene 3 – Übersichtstabelle:**

```
| ID   | Attribut   | Kontext   | S  | K  | T  | V  | R  | Th  | Anmerkung |
|------|------------|-----------|----|----|----|----|----|----- |-----------|
| 0001 | implizit   | WiWi      | S0 | K0 | —  | V0 | R0 | —   | ...       |
```

### Visualisierung

Balkendiagramme pro Dimension (React-Artifacts), farbkodiert nach Prompt-Kategorie.

---

## Wiederholung und Längsschnitt

Der Workflow ist für regelmäßige Wiederholung ausgelegt:

- **Neue Erhebung:** Gleiche Prompts, neues Datum → neue ANTWORT-Dateien mit aktuellem Datum
- **Versionierung:** Bei Änderung der Prompts Version hochzählen (01.00 → 02.00)
- **Vergleich über Zeit:** Kodierungen verschiedener Erhebungszeitpunkte nebeneinanderlegen
- **Andere Modelle:** Erhebung mit verschiedenen LLMs wiederholen (GPT, Gemini, etc.)

---

## Zugehörige Skills und Tools

| Schritt | Skill/Tool | Speicherort |
|---------|-----------|-------------|
| 1. Prompts | geo-prompt-generator | `New Ground skills/geo-prompt-generator/` |
| 2. Erhebung | geo-erhebung (Artifact) | im Chat erzeugt |
| 3. Kodierung | geo-kodierung | `New Ground skills/geo-kodierung/` |
| 4. Auswertung | Visualisierungs-Artifacts | im Chat erzeugt |
