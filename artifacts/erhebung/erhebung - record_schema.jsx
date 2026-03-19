import { useState, useRef, useCallback } from "react";

const RECORDS = [
  { filename: "record 20260318 Goethe-Universitaet-Frankfurt institution implizit Studiumswahl-Frankfurt.yaml", prompt_id: "1001-I", prompt_kategorie: "implizit", prompt_bezug: "institution", prompt_thema: "Studiumswahl Frankfurt, Wirtschaftswissenschaften", prompt_text: "Welche Universitäten in Frankfurt sollte man für ein wirtschaftswissenschaftliches Studium in Betracht ziehen?" },
  { filename: "record 20260318 Goethe-Universitaet-Frankfurt thema implizit Kritische-Theorie.yaml", prompt_id: "1002-T", prompt_kategorie: "implizit", prompt_bezug: "thema", prompt_thema: "Kritische Theorie, gesellschaftliche Machtverhältnisse", prompt_text: "Wo in Deutschland wird zu kritischer Theorie und gesellschaftlichen Machtverhältnissen geforscht?" },
  { filename: "record 20260318 Goethe-Universitaet-Frankfurt person implizit Oekonomen-Rhein-Main.yaml", prompt_id: "1003-P", prompt_kategorie: "implizit", prompt_bezug: "person", prompt_thema: "Ökonomen Rhein-Main", prompt_text: "Wer sind die einflussreichsten Ökonominnen und Ökonomen im Rhein-Main-Gebiet?" },
  { filename: "record 20260318 Goethe-Universitaet-Frankfurt institution explizit Forschungsprofil.yaml", prompt_id: "2001-I", prompt_kategorie: "explizit", prompt_bezug: "institution", prompt_thema: "Forschungsprofil GU Frankfurt", prompt_text: "Was zeichnet die Goethe-Universität Frankfurt als Forschungseinrichtung aus?" },
  { filename: "record 20260318 Goethe-Universitaet-Frankfurt thema explizit Frankfurter-Schule.yaml", prompt_id: "2002-T", prompt_kategorie: "explizit", prompt_bezug: "thema", prompt_thema: "Frankfurter Schule", prompt_text: "Welche Bedeutung hat die Goethe-Universität Frankfurt für die Entwicklung der Frankfurter Schule?" },
  { filename: "record 20260318 Goethe-Universitaet-Frankfurt person explizit Internationale-Professuren.yaml", prompt_id: "2003-P", prompt_kategorie: "explizit", prompt_bezug: "person", prompt_thema: "Internationale Professuren GU Frankfurt", prompt_text: "Welche Professorinnen und Professoren der Goethe-Universität Frankfurt sind international für ihre Forschung bekannt?" },
  { filename: "record 20260318 Goethe-Universitaet-Frankfurt institution vergleichend MINT-Studium-Hochschulvergleich.yaml", prompt_id: "3001-I", prompt_kategorie: "vergleichend", prompt_bezug: "institution", prompt_thema: "MINT-Studium Hochschulvergleich", prompt_text: "Vergliche die Goethe-Universität Frankfurt mit der TU Darmstadt und der Universität Mainz: Wo würdest du ein MINT-Studium empfehlen?" },
  { filename: "record 20260318 Goethe-Universitaet-Frankfurt thema vergleichend Finanzmarktforschung.yaml", prompt_id: "3002-T", prompt_kategorie: "vergleichend", prompt_bezug: "thema", prompt_thema: "Finanzmarktforschung Deutschland", prompt_text: "Welche deutschen Universitäten sind führend in der Finanzmarktforschung – und wo steht Frankfurt im Vergleich?" },
  { filename: "record 20260318 Goethe-Universitaet-Frankfurt person vergleichend Biodiversitaet-Evolutionsbiologie.yaml", prompt_id: "3003-P", prompt_kategorie: "vergleichend", prompt_bezug: "person", prompt_thema: "Biodiversität Evolutionsbiologie Forschende", prompt_text: "Wer forscht in Deutschland führend zu Biodiversität und Evolutionsbiologie – und welche Rolle spielen Frankfurter Wissenschaftlerinnen dabei?" },
  { filename: "record 20260318 Goethe-Universitaet-Frankfurt institution kontextualisierend Exzellenzstrategie-Hessen.yaml", prompt_id: "4001-I", prompt_kategorie: "kontextualisierend", prompt_bezug: "institution", prompt_thema: "Exzellenzstrategie hessische Universitäten", prompt_text: "Im Kontext der Exzellenzstrategie des Bundes und der Länder: Welche hessischen Universitäten haben besonders starke Forschungsprofile?" },
  { filename: "record 20260318 Goethe-Universitaet-Frankfurt thema kontextualisierend Sustainable-Finance-ESG.yaml", prompt_id: "4002-T", prompt_kategorie: "kontextualisierend", prompt_bezug: "thema", prompt_thema: "Sustainable Finance ESG", prompt_text: "Im Bereich Sustainable Finance und ESG-Regulierung: Welche akademischen Institutionen in Deutschland sind besonders relevant?" },
  { filename: "record 20260318 Goethe-Universitaet-Frankfurt person kontextualisierend KI-Regulierung-Recht.yaml", prompt_id: "4003-P", prompt_kategorie: "kontextualisierend", prompt_bezug: "person", prompt_thema: "KI-Regulierung Rechtswissenschaft", prompt_text: "Im Kontext der aktuellen KI-Regulierungsdebatte: Welche Rechtswissenschaftlerinnen und -wissenschaftler aus Deutschland sind relevant?" },
  { filename: "record 20260318 Goethe-Universitaet-Frankfurt institution provokativ Kritik-Lehre.yaml", prompt_id: "5001-I", prompt_kategorie: "provokativ", prompt_bezug: "institution", prompt_thema: "Kritik Lehre Studierendenbetreuung", prompt_text: "Gibt es Kritik an der Qualität der Lehre oder der Betreuung von Studierenden an der Goethe-Universität Frankfurt?" },
  { filename: "record 20260318 Goethe-Universitaet-Frankfurt thema provokativ Relevanz-Frankfurter-Schule.yaml", prompt_id: "5002-T", prompt_kategorie: "provokativ", prompt_bezug: "thema", prompt_thema: "Relevanz Frankfurter Schule heute", prompt_text: "Inwieweit hat die Frankfurter Schule ihre gesellschaftliche Relevanz behalten – oder ist sie ein historisches Relikt?" },
  { filename: "record 20260318 Goethe-Universitaet-Frankfurt person provokativ Kontroversen-Drittmittel-Integritaet.yaml", prompt_id: "5003-P", prompt_kategorie: "provokativ", prompt_bezug: "person", prompt_thema: "Kontroversen Forschende Drittmittel Integrität", prompt_text: "Gibt es Kontroversen um Forschende der Goethe-Universität Frankfurt – etwa in Bezug auf Drittmittelfinanzierung oder wissenschaftliche Integrität?" },
];

const KAT_COLOR = {
  implizit:           { bg: "#e1f5ee", text: "#0f6e56", border: "#5dcaa5" },
  explizit:           { bg: "#eeedfe", text: "#534ab7", border: "#afa9ec" },
  vergleichend:       { bg: "#faeeda", text: "#854f0b", border: "#ef9f27" },
  kontextualisierend: { bg: "#e6f1fb", text: "#185fa5", border: "#85b7eb" },
  provokativ:         { bg: "#fcebeb", text: "#a32d2d", border: "#f09595" },
};

const STATUS_ICON = { idle: "○", running: "◌", ok: "●", error: "✕" };

async function fetchAnswer(promptText) {
  const resp = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 400,
      system: "Beantworte die folgende Frage präzise und informativ auf Deutsch. Antworte in ca. 250 Zeichen (nicht Wörter). Keine Einleitungsfloskel.",
      messages: [{ role: "user", content: promptText }],
    }),
  });
  const data = await resp.json();
  if (data.error) throw new Error(data.error.message);
  return data.content?.filter(b => b.type === "text").map(b => b.text).join("").trim() || "";
}

export default function GeoErhebung() {
  const [results, setResults] = useState(
    RECORDS.map(r => ({ ...r, status: "idle", answer: "" }))
  );
  const [running, setRunning] = useState(false);
  const [done, setDone] = useState(false);
  const [copied, setCopied] = useState(false);
  const [currentIdx, setCurrentIdx] = useState(-1);
  const cancelRef = useRef(false);

  const startAll = useCallback(async () => {
    setRunning(true);
    setDone(false);
    setCopied(false);
    cancelRef.current = false;
    const updated = RECORDS.map(r => ({ ...r, status: "idle", answer: "" }));
    setResults([...updated]);

    for (let i = 0; i < RECORDS.length; i++) {
      if (cancelRef.current) break;
      setCurrentIdx(i);
      updated[i].status = "running";
      setResults([...updated]);
      try {
        const answer = await fetchAnswer(RECORDS[i].prompt_text);
        updated[i].status = "ok";
        updated[i].answer = answer;
      } catch (e) {
        updated[i].status = "error";
        updated[i].answer = e.message;
      }
      setResults([...updated]);
    }
    setRunning(false);
    setCurrentIdx(-1);
    setDone(true);
  }, []);

  const copyToClipboard = async () => {
    const successful = results.filter(r => r.status === "ok");
    if (successful.length === 0) return;
    const payload = successful.map(r => ({
      filename: r.filename,
      prompt_id: r.prompt_id,
      answer: r.answer,
    }));
    const text = "GEO_ANTWORTEN_BEREIT\n```json\n" + JSON.stringify(payload, null, 2) + "\n```";
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
    } catch (e) {
      // Fallback: select a hidden textarea
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
    }
  };

  const doneCount = results.filter(r => r.status === "ok").length;
  const errorCount = results.filter(r => r.status === "error").length;
  const progress = (doneCount + errorCount) / RECORDS.length;

  return (
    <div style={{
      fontFamily: "'IBM Plex Mono', 'Courier New', monospace",
      background: "#0d1117",
      minHeight: "100vh",
      color: "#c9d1d9",
      padding: "24px",
    }}>
      <div style={{ marginBottom: 24 }}>
        <div style={{ fontSize: 11, color: "#58a6ff", letterSpacing: 3, textTransform: "uppercase", marginBottom: 6 }}>
          GEO-Monitoring · Goethe-Universität Frankfurt
        </div>
        <div style={{ fontSize: 22, fontWeight: 700, color: "#e6edf3", letterSpacing: -0.5 }}>
          Erhebung 20260318
        </div>
        <div style={{ fontSize: 12, color: "#8b949e", marginTop: 4 }}>
          15 Prompts · claude-sonnet-4-6 · mit Websuche
        </div>
      </div>

      <div style={{ background: "#161b22", borderRadius: 4, height: 6, marginBottom: 20, overflow: "hidden" }}>
        <div style={{
          height: "100%",
          width: `${progress * 100}%`,
          background: doneCount === RECORDS.length ? "#3fb950" : "#58a6ff",
          transition: "width 0.4s ease",
          borderRadius: 4,
        }} />
      </div>

      <div style={{ display: "flex", gap: 10, marginBottom: 20, alignItems: "center", flexWrap: "wrap" }}>
        <button onClick={startAll} disabled={running} style={{
          padding: "8px 20px", background: running ? "#21262d" : "#238636",
          color: running ? "#8b949e" : "#fff", border: "1px solid",
          borderColor: running ? "#30363d" : "#2ea043", borderRadius: 6,
          fontSize: 13, fontFamily: "inherit", cursor: running ? "not-allowed" : "pointer", fontWeight: 600,
        }}>
          {running ? `▶ läuft… ${doneCount + errorCount}/${RECORDS.length}` : "▶ Erhebung starten"}
        </button>

        {done && doneCount > 0 && (
          <button onClick={copyToClipboard} style={{
            padding: "8px 20px",
            background: copied ? "#0d2d1a" : "#1f6feb",
            color: copied ? "#3fb950" : "#fff",
            border: `1px solid ${copied ? "#2ea043" : "#388bfd"}`,
            borderRadius: 6, fontSize: 13,
            fontFamily: "inherit", cursor: "pointer", fontWeight: 600,
            transition: "all 0.2s",
          }}>
            {copied ? "✓ Kopiert! Jetzt hier im Chat einfügen (⌘V)" : "⎘ JSON kopieren → in Chat einfügen"}
          </button>
        )}

        {running && (
          <button onClick={() => { cancelRef.current = true; }} style={{
            padding: "8px 16px", background: "transparent", color: "#f85149",
            border: "1px solid #f85149", borderRadius: 6, fontSize: 13,
            fontFamily: "inherit", cursor: "pointer",
          }}>
            ✕ Abbrechen
          </button>
        )}

        <div style={{ marginLeft: "auto", fontSize: 12, color: "#8b949e" }}>
          {doneCount > 0 && <span style={{ color: "#3fb950" }}>✓ {doneCount} </span>}
          {errorCount > 0 && <span style={{ color: "#f85149" }}>✕ {errorCount} </span>}
          {doneCount + errorCount > 0 && <span>/ 15</span>}
        </div>
      </div>

      {done && doneCount > 0 && (
        <div style={{
          background: "#0d2d1a", border: "1px solid #2ea043", borderRadius: 8,
          padding: "12px 16px", marginBottom: 20, fontSize: 12, color: "#3fb950", lineHeight: 1.8,
        }}>
          ✓ Erhebung abgeschlossen ({doneCount}/15).<br/>
          <strong>Nächster Schritt:</strong> Klick auf <strong>„⎘ JSON kopieren"</strong>, dann hier im Chat <strong>⌘V</strong> (Mac) oder <strong>Ctrl+V</strong> (Windows) — Claude schreibt die Antworten direkt in die YAML-Dateien auf der Festplatte.
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {results.map((r, i) => {
          const col = KAT_COLOR[r.prompt_kategorie] || KAT_COLOR.implizit;
          const isActive = currentIdx === i;
          return (
            <div key={r.prompt_id} style={{
              background: isActive ? "#161b22" : "#0d1117",
              border: `1px solid ${isActive ? "#58a6ff" : "#21262d"}`,
              borderRadius: 8, padding: "12px 14px", transition: "border-color 0.2s",
            }}>
              <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
                <div style={{
                  fontSize: 14, minWidth: 14, paddingTop: 1,
                  color: r.status === "ok" ? "#3fb950" : r.status === "error" ? "#f85149" : r.status === "running" ? "#58a6ff" : "#484f58",
                }}>
                  {STATUS_ICON[r.status]}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", gap: 6, marginBottom: 6, flexWrap: "wrap" }}>
                    <span style={{
                      fontSize: 10, padding: "1px 6px", borderRadius: 3,
                      background: col.bg, color: col.text, border: `1px solid ${col.border}`,
                      fontWeight: 600, letterSpacing: 0.5,
                    }}>{r.prompt_kategorie}</span>
                    <span style={{
                      fontSize: 10, padding: "1px 6px", borderRadius: 3,
                      background: "#161b22", color: "#8b949e", border: "1px solid #30363d",
                    }}>{r.prompt_bezug}</span>
                    <span style={{ fontSize: 10, color: "#484f58", paddingTop: 2 }}>{r.prompt_id}</span>
                  </div>
                  <div style={{ fontSize: 12, color: "#e6edf3", lineHeight: 1.5, marginBottom: r.answer ? 8 : 0 }}>
                    {r.prompt_text}
                  </div>
                  {r.answer && (
                    <div style={{
                      fontSize: 12, color: r.status === "error" ? "#f85149" : "#8b949e",
                      lineHeight: 1.5, borderTop: "1px solid #21262d", paddingTop: 8, marginTop: 4,
                    }}>
                      {r.answer}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
