#!/bin/bash
# Zerlegt die Kodierungs-Gesamtdatei in Einzeldateien
# Ausführen im Verzeichnis, in dem die KODIERUNG_GESAMT-Datei liegt

INPUT="KODIERUNG_GESAMT_2026-02-27.md"
COUNT=0

awk '
/^===DATEI: / {
    fname = $0
    gsub(/^===DATEI: /, "", fname)
    gsub(/===$/, "", fname)
    gsub(/^[ \t]+|[ \t]+$/, "", fname)
    outfile = fname
    printing = 1
    next
}
/^===DATEIGRENZE===/ {
    if (outfile) close(outfile)
    printing = 0
    next
}
printing == 1 && outfile {
    print >> outfile
}
' "$INPUT"

echo "✅ Fertig. Einzeldateien erstellt:"
ls -1 KODIERUNG*.md 2>/dev/null | grep -v GESAMT | wc -l
