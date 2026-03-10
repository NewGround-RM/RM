#!/bin/bash
# split.sh – Zerlegt eine Gesamtdatei (ERHEBUNG oder KODIERUNG) in Einzeldateien
# Erkennt ===DATEI: ...=== und ===DATEIGRENZE=== als Trennmarker
#
# Verwendung:
#   bash /pfad/zu/scripts/split.sh GESAMTDATEI.md
#
# Beispiele:
#   bash split.sh ERHEBUNG_Goethe_Universitaet_Frankfurt_am_Main_2026-02-27.md
#   bash split.sh KODIERUNG_GESAMT_2026-02-27.md

if [ -z "$1" ]; then
  echo "Verwendung: bash split.sh GESAMTDATEI.md"
  exit 1
fi

INPUT="$1"

if [ ! -f "$INPUT" ]; then
  echo "❌ Datei nicht gefunden: $INPUT"
  exit 1
fi

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

COUNT=$(ls -1 ANTWORT*.md KODIERUNG*.md 2>/dev/null | grep -v GESAMT | grep -v UEBERSICHT | wc -l | tr -d ' ')
echo "✅ Fertig. $COUNT Einzeldateien erstellt."
