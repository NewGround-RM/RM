---
name: geo-prompt-generator
description: >
  Generates a complete set of n RM (reputation monitoring) prompts for any institution
  and saves them as individual Markdown files. Use this skill whenever
  the user wants to create a RM prompt set, generate reputation monitoring prompts,
  set up institutional monitoring, or mentions "Erhebungs-Prompts" for any organization.
  Also trigger when the user says things like "erstelle Monitoring-Prompts für [Institution]",
  "GEO-Prompts generieren", "Reputationsmonitoring aufsetzen", or "Prompt-Set erstellen".
---

# GEO Prompt Generator

Generates n structured monitoring prompts (m per category) for institutional reputation
monitoring across AI systems, and saves each as an individual Markdown file.

## Usage

Run the generator script. It requires five inputs which Claude must collect from the user
before running:

1. **Zielinstitution** – The institution to monitor (e.g. "Goethe-Universität Frankfurt am Main")
2. **Vergleichsinstitutionen** – Comma-separated list of comparison institutions for the
   "vergleichend" category (e.g. "LMU München, Universität Heidelberg")
3. **Ausgabeverzeichnis** – Where to save the prompt files
4. **m** - total number of prompts to be generated
5. **n** - number of prompts per category to be generated
6. **o** - number of categories

### Running the script

```bash
python3 /mnt/skills/user/geo-prompt-generator/scripts/generate_prompts.py \
  --institution "Goethe-Universität Frankfurt am Main" \
  --vergleich "LMU München, Universität Heidelberg" \
  --output "/path/to/output/directory"  \
  --n "n"  \
  --m "m"  \
  --o "o"
```

### What it generates

m prompts in o categories (n each):

| Kategorie | IDs | Beobachtungsdimensionen |
|---|---|---|
| **implizit** | 0001–0010 | Sichtbarkeit, Kontextualisierung, Themenassoziation |
| **explizit** | 0011–0020 | Kontextualisierung, Tonalität, Rollenzuschreibung |
| **vergleichend** | 0021–0030 | Konkurrenz- und Positionierungslogiken |
| **kontextualisierend** | 0031–0040 | Kontextualisierung, Tonalität, Rollenzuschreibung, Vergleiche, Themenassoziation |
| **provokativ** | 0041–0050 | Erfassung problematischer Narrative |

### File naming convention

```
PROMPT <4-digit ID> <Version> <Attribut> <Kontext>.md
```

Example: `PROMPT 0001 01.00 implizit Wirtschaftswissenschaften.md`

### Customization

The prompt texts are defined in the script's `PROMPT_DEFINITIONS` dictionary.
To adapt the prompts for a different type of institution (e.g. a company instead of
a university), edit the prompt templates in the script. The `{institution}` and
`{vergleich_text}` placeholders are replaced automatically.

### After generation

Claude should confirm the number of files created and show a summary table of all
50 prompts grouped by category.
