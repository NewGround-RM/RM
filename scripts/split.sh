#!/bin/bash
# Zerlegt die Gesamtdatei in Einzeldateien
# Ausführen im Verzeichnis, in dem die ERHEBUNG-Datei liegt

INPUT="ERHEBUNG_Goethe_Universitaet_Frankfurt_am_Main_2026-02-27.md"
COUNT=0

# Lies die Datei und splitte an den DATEI-Markern
awk '
/^===DATEI: / {
    # Extrahiere Dateinamen
    fname = $0
    gsub(/^===DATEI: /, "", fname)
    gsub(/===$/, "", fname)
    # Entferne führende/trailing Whitespace
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
ls -1 ANTWORT*.md 2>/dev/null | wc -l
