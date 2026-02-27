# RM – Reputation Monitoring

Systematische Erhebung und Analyse der Repräsentation von akademischen Institutionen in KI-Systemen/LLMs.

## Struktur

```
repmon/
├── docs/              Workflow-Dokumentation
├── skills/            Claude-Skills (Prompt-Generator, Kodierung)
├── artifacts/         React-Artifacts (Erhebung, Visualisierung)
└── institutions/      Daten pro Institution
    └── <name>/
        ├── prompts/                        50 Monitoring-Prompts
        ├── antworten/<modell>/<datum>/     LLM-Antworten
        └── kodierungen/<modell>/<datum>/   Kodierte Antworten
```

## Workflow

1. `skills/prompt-generator/` → Prompts generieren
2. `artifacts/erhebung.jsx` → Erhebung durchführen  
3. `skills/kodierung/` → Antworten kodieren
4. `artifacts/visualisierung/` → Ergebnisse visualisieren

Details: [docs/workflow.md](docs/workflow.md)
