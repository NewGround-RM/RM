import { useState, useRef, useCallback } from "react";

const CATEGORY_COLORS = {
  implizit: "#2563eb",
  explizit: "#7c3aed",
  vergleichend: "#0891b2",
  kontextualisierend: "#059669",
  provokativ: "#dc2626",
};

const CATEGORY_ORDER = ["implizit", "explizit", "vergleichend", "kontextualisierend", "provokativ"];

function parsePromptMd(content, filename) {
  const promptMatch = content.match(/## Prompt\s*\n\s*([\s\S]*?)(?=\n## )/);
  const idMatch = content.match(/\*\*Prompt-ID:\*\*\s*(\d+)/);
  const versionMatch = content.match(/\*\*Version:\*\*\s*([\d.]+)/);
  const kontextMatch = content.match(/\*\*Kontext:\*\*\s*(.+)/);
  const attributMatch = content.match(/\*\*Attribut:\*\*\s*(.+)/);
  const institutionMatch = content.match(/\*\*Zielinstitution:\*\*\s*(.+)/);
  const beobMatch = content.match(/\*\*Beobachtungsdimensionen:\*\*\s*(.+)/);
  const vergleichMatch = content.match(/\*\*Vergleichsinstitutionen:\*\*\s*(.+)/);

  return {
    id: idMatch ? parseInt(idMatch[1], 10) : 0,
    version: versionMatch ? versionMatch[1].trim() : "01.00",
    kontext: kontextMatch ? kontextMatch[1].trim() : "",
    attribut: attributMatch ? attributMatch[1].trim() : "",
    institution: institutionMatch ? institutionMatch[1].trim() : "",
    beobachtungsdimensionen: beobMatch ? beobMatch[1].trim() : "",
    vergleich: vergleichMatch ? vergleichMatch[1].trim() : "",
    text: promptMatch ? promptMatch[1].trim() : "",
    filename: filename,
  };
}

function sanitize(text) {
  const rep = { "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue" };
  let s = text;
  for (const [k, v] of Object.entries(rep)) s = s.replaceAll(k, v);
  return s.replace(/[^a-zA-Z0-9_]/g, "_").replace(/_+/g, "_").replace(/^_|_$/g, "");
}

function generateAnswerMd(prompt, answer) {
  const today = new Date().toISOString().split("T")[0];
  const idStr = String(prompt.id).padStart(4, "0");
  const kontextSafe = sanitize(prompt.kontext);
  let lines = [
    `# ANTWORT ${idStr} | Version ${prompt.version} | ${prompt.attribut} | ${kontextSafe}`,
    "", "## Antwort", "", answer, "",
    "## Metadaten", "",
    `- **Prompt-ID:** ${idStr}`,
    `- **Version:** ${prompt.version}`,
    `- **Kontext:** ${prompt.kontext}`,
    `- **Attribut:** ${prompt.attribut}`,
    `- **Zielinstitution:** ${prompt.institution}`,
  ];
  if (prompt.vergleich) {
    lines.push(`- **Vergleichsinstitutionen:** ${prompt.vergleich}`);
  }
  lines.push(
    `- **Beobachtungsdimensionen:** ${prompt.beobachtungsdimensionen}`,
    `- **Prompt:** ${prompt.text}`,
    `- **Modell:** claude-sonnet-4-20250514`,
    `- **Erhoben:** ${today}`,
    ""
  );
  return lines.join("\n");
}

function generateGesamtdatei(results, institution) {
  const today = new Date().toISOString().split("T")[0];
  const header = [
    `# GEO-Erhebung: ${institution}`,
    `# Datum: ${today}`,
    `# Modell: claude-sonnet-4-20250514`,
    `# Anzahl: ${results.length} Antworten`,
    "",
    "---",
    "",
  ].join("\n");

  const separator = "\n\n===DATEIGRENZE===\n\n";
  const blocks = results.map(r => {
    const idStr = String(r.prompt.id).padStart(4, "0");
    const kontextSafe = sanitize(r.prompt.kontext);
    const filename = `ANTWORT ${idStr} ${r.prompt.version} ${r.prompt.attribut} ${kontextSafe}.md`;
    return `===DATEI: ${filename}===\n\n${r.md}`;
  });

  return header + blocks.join(separator);
}

async function callClaude(promptText) {
  const systemPrompt = "Du bist ein KI-Assistent. Antworte auf die folgende Frage in ca. 250 Zeichen (nicht Wörter). Sei präzise und informativ. Antworte auf Deutsch.";
  const resp = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 300,
      system: systemPrompt,
      messages: [{ role: "user", content: promptText }],
    }),
  });
  const data = await resp.json();
  const text = data.content?.filter(b => b.type === "text").map(b => b.text).join("") || "";
  return text.trim();
}

function downloadText(content, filename) {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export default function Erhebung() {
  const [prompts, setPrompts] = useState([]);
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(-1);
  const [loaded, setLoaded] = useState(false);
  const cancelRef = useRef(false);

  const handleFileSelect = useCallback((e) => {
    const files = Array.from(e.target.files).filter(f => f.name.startsWith("PROMPT") && f.name.endsWith(".md"));
    if (files.length === 0) return;

    const parsed = [];
    let done = 0;

    files.forEach(file => {
      const reader = new FileReader();
      reader.onload = (ev) => {
        const content = ev.target.result;
        const prompt = parsePromptMd(content, file.name);
        if (prompt.text && prompt.id > 0) {
          parsed.push(prompt);
        }
        done++;
        if (done === files.length) {
          parsed.sort((a, b) => a.id - b.id);
          setPrompts(parsed);
          setLoaded(true);
          setResults([]);
        }
      };
      reader.readAsText(file);
    });
  }, []);

  const institution = prompts.length > 0 ? prompts[0].institution : "";

  const categoryCounts = {};
  for (const cat of CATEGORY_ORDER) {
    const catPrompts = prompts.filter(p => p.attribut === cat);
    categoryCounts[cat] = {
      total: catPrompts.length,
      done: results.filter(r => r.prompt.attribut === cat && r.status === "ok").length,
      error: results.filter(r => r.prompt.attribut === cat && r.status === "error").length,
    };
  }

  const startErhebung = useCallback(async () => {
    setRunning(true);
    setResults([]);
    cancelRef.current = false;

    const newResults = [];

    for (let i = 0; i < prompts.length; i++) {
      if (cancelRef.current) break;
      setCurrentIdx(i);
      const p = prompts[i];
      try {
        const answer = await callClaude(p.text);
        const md = generateAnswerMd(p, answer);
        newResults.push({ prompt: p, answer, md, status: "ok" });
      } catch (e) {
        newResults.push({ prompt: p, answer: "", md: "", status: "error", error: e.message });
      }
      setResults([...newResults]);
    }

    setCurrentIdx(-1);
    setRunning(false);
  }, [prompts]);

  const stopErhebung = () => { cancelRef.current = true; };

  const handleDownload = () => {
    const okResults = results.filter(r => r.status === "ok");
    if (okResults.length === 0) return;
    const today = new Date().toISOString().split("T")[0];
    const content = generateGesamtdatei(okResults, institution);
    const instSafe = sanitize(institution);
    downloadText(content, `ERHEBUNG_${instSafe}_${today}.md`);
  };

  const completedOk = results.filter(r => r.status === "ok");
  const completedErr = results.filter(r => r.status === "error");
  const progress = prompts.length > 0 ? results.length / prompts.length : 0;

  return (
    <div style={{ fontFamily: "'IBM Plex Sans', 'Segoe UI', sans-serif", background: "#0a0f1a", color: "#e2e8f0", minHeight: "100vh", padding: "32px 24px" }}>
      <div style={{ maxWidth: 720, margin: "0 auto" }}>

        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: "#f8fafc", margin: 0, letterSpacing: "-0.02em" }}>
            GEO Monitoring · Erhebung
          </h1>
          <p style={{ fontSize: 13, color: "#64748b", marginTop: 6 }}>
            Prompt-Dateien laden · Isolierte API-Calls · Gesamtdatei exportieren
          </p>
        </div>

        {/* Prompt-Dateien laden */}
        <div style={{ background: "#111827", borderRadius: 10, padding: 20, marginBottom: 20, border: "1px solid #1e293b" }}>
          <label style={{ fontSize: 12, color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.05em", display: "block", marginBottom: 10 }}>
            Prompt-Dateien auswählen
          </label>
          <input
            type="file"
            multiple
            accept=".md"
            onChange={handleFileSelect}
            disabled={running}
            style={{ fontSize: 13, color: "#cbd5e1" }}
          />
          {loaded && (
            <div style={{ marginTop: 12, fontSize: 13, color: "#94a3b8" }}>
              {prompts.length} Prompts geladen
              {institution && <span> · {institution}</span>}
            </div>
          )}
        </div>

        {/* Kategorie-Übersicht nach Laden */}
        {loaded && prompts.length > 0 && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8, marginBottom: 20 }}>
            {CATEGORY_ORDER.map(cat => {
              const c = categoryCounts[cat];
              const pct = c.total > 0 ? c.done / c.total : 0;
              return (
                <div key={cat} style={{ background: "#111827", borderRadius: 8, padding: "10px 8px", textAlign: "center", border: `1px solid ${pct === 1 ? CATEGORY_COLORS[cat] + "44" : "#1e293b"}` }}>
                  <div style={{ fontSize: 10, color: CATEGORY_COLORS[cat], textTransform: "uppercase", letterSpacing: "0.05em", fontWeight: 600, marginBottom: 4 }}>{cat}</div>
                  <div style={{ fontSize: 18, fontWeight: 700, color: pct === 1 ? CATEGORY_COLORS[cat] : "#cbd5e1" }}>
                    {results.length > 0 ? c.done : c.total}
                    {results.length > 0 && <span style={{ fontSize: 12, color: "#475569" }}>/{c.total}</span>}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Buttons */}
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 24 }}>
          {!running && loaded && prompts.length > 0 && results.length === 0 && (
            <button onClick={startErhebung}
              style={{ padding: "12px 28px", background: "#2563eb", color: "#fff", border: "none", borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: "pointer" }}>
              ▶ Erhebung starten ({prompts.length} Prompts)
            </button>
          )}
          {running && (
            <button onClick={stopErhebung}
              style={{ padding: "12px 28px", background: "#dc2626", color: "#fff", border: "none", borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: "pointer" }}>
              ■ Abbrechen
            </button>
          )}
          {completedOk.length > 0 && !running && (
            <button onClick={handleDownload}
              style={{ padding: "12px 28px", background: "#059669", color: "#fff", border: "none", borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: "pointer" }}>
              ↓ Gesamtdatei herunterladen ({completedOk.length} Antworten)
            </button>
          )}
        </div>

        {/* Fortschritt */}
        {(running || results.length > 0) && (
          <div style={{ background: "#111827", borderRadius: 10, padding: 20, marginBottom: 20, border: "1px solid #1e293b" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
              <span style={{ fontSize: 13, color: "#94a3b8" }}>
                {running ? `Prompt ${results.length + 1} / ${prompts.length}` : `Fertig: ${completedOk.length} / ${prompts.length}`}
              </span>
              {completedErr.length > 0 && (
                <span style={{ fontSize: 13, color: "#f87171" }}>{completedErr.length} Fehler</span>
              )}
            </div>
            <div style={{ height: 6, background: "#1e293b", borderRadius: 3, overflow: "hidden" }}>
              <div style={{ height: "100%", width: `${progress * 100}%`, background: running ? "#2563eb" : "#059669", borderRadius: 3, transition: "width 0.3s" }} />
            </div>
          </div>
        )}

        {/* Aktueller Prompt */}
        {running && currentIdx >= 0 && currentIdx < prompts.length && (
          <div style={{ background: "#111827", borderRadius: 10, padding: 16, marginBottom: 20, border: "1px solid #2563eb33" }}>
            <div style={{ fontSize: 11, color: "#2563eb", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 6 }}>
              {String(prompts[currentIdx].id).padStart(4, "0")} · {prompts[currentIdx].attribut} · {prompts[currentIdx].kontext}
            </div>
            <div style={{ fontSize: 13, color: "#e2e8f0", lineHeight: 1.5 }}>
              {prompts[currentIdx].text}
            </div>
          </div>
        )}

        {/* Ergebnisse */}
        {results.length > 0 && !running && (
          <div style={{ background: "#111827", borderRadius: 10, padding: 20, border: "1px solid #1e293b" }}>
            <h3 style={{ fontSize: 14, fontWeight: 600, color: "#f8fafc", marginTop: 0, marginBottom: 16 }}>Ergebnisse</h3>
            <div style={{ maxHeight: 400, overflowY: "auto" }}>
              {results.map((r, i) => (
                <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 10, padding: "10px 0", borderBottom: "1px solid #1e293b" }}>
                  <div style={{ minWidth: 44, fontSize: 11, color: CATEGORY_COLORS[r.prompt.attribut], fontWeight: 600, paddingTop: 2 }}>
                    {String(r.prompt.id).padStart(4, "0")}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 11, color: "#64748b", marginBottom: 2 }}>{r.prompt.attribut} · {r.prompt.kontext}</div>
                    <div style={{ fontSize: 13, color: r.status === "ok" ? "#cbd5e1" : "#f87171", lineHeight: 1.4, wordBreak: "break-word" }}>
                      {r.status === "ok" ? r.answer : `Fehler: ${r.error}`}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
