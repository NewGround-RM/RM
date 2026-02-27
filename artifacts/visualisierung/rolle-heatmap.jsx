import { useState } from "react";

const data = [
  { id: "0001", attribut: "implizit", rollen: ["R0"] },
  { id: "0002", attribut: "implizit", rollen: ["R2"] },
  { id: "0011", attribut: "explizit", rollen: ["R1", "R2", "R3"] },
  { id: "0012", attribut: "explizit", rollen: ["R1", "R2"] },
  { id: "0021", attribut: "vergleichend", rollen: ["R2"] },
  { id: "0022", attribut: "vergleichend", rollen: ["R2"] },
  { id: "0031", attribut: "kontextual.", rollen: ["R3"] },
  { id: "0032", attribut: "kontextual.", rollen: ["R0"] },
  { id: "0041", attribut: "provokativ", rollen: ["R6"] },
  { id: "0042", attribut: "provokativ", rollen: ["R6"] },
];

const kategorien = ["implizit", "explizit", "vergleichend", "kontextual.", "provokativ"];
const rollen = ["R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7"];
const rollenLabels = {
  R0: "keine Rolle",
  R1: "Wissensquelle",
  R2: "forschend",
  R3: "beratend",
  R4: "operativ",
  R5: "politisch",
  R6: "Problemtraeger",
  R7: "Vergleichsmassstab",
};

const catColors = {
  "implizit": "#2563eb",
  "explizit": "#7c3aed",
  "vergleichend": "#0891b2",
  "kontextual.": "#059669",
  "provokativ": "#dc2626",
};

// Count occurrences per cell
function buildMatrix() {
  const matrix = {};
  for (const k of kategorien) {
    matrix[k] = {};
    for (const r of rollen) {
      matrix[k][r] = 0;
    }
  }
  for (const d of data) {
    for (const r of d.rollen) {
      if (matrix[d.attribut] && matrix[d.attribut][r] !== undefined) {
        matrix[d.attribut][r]++;
      }
    }
  }
  return matrix;
}

// Find which prompt IDs contribute to each cell
function buildDetails() {
  const details = {};
  for (const k of kategorien) {
    details[k] = {};
    for (const r of rollen) {
      details[k][r] = [];
    }
  }
  for (const d of data) {
    for (const r of d.rollen) {
      if (details[d.attribut] && details[d.attribut][r]) {
        details[d.attribut][r].push(d.id);
      }
    }
  }
  return details;
}

export default function RollenHeatmap() {
  const [hover, setHover] = useState(null);
  const matrix = buildMatrix();
  const details = buildDetails();

  const cellW = 72;
  const cellH = 52;
  const labelLeft = 120;
  const labelTop = 90;
  const gapX = 4;
  const gapY = 4;

  const maxCount = Math.max(...kategorien.flatMap(k => rollen.map(r => matrix[k][r])));

  return (
    <div style={{ fontFamily: "'IBM Plex Sans', 'Segoe UI', sans-serif", background: "#ffffff", color: "#1e293b", minHeight: "100vh", padding: "32px 24px" }}>
      <div style={{ maxWidth: 780, margin: "0 auto" }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, color: "#0f172a", margin: "0 0 4px 0", letterSpacing: "-0.02em" }}>
          Rollenzuschreibung · Goethe-Universitat Frankfurt
        </h1>
        <p style={{ fontSize: 12, color: "#94a3b8", margin: "0 0 28px 0" }}>
          GEO-Monitoring · Heatmap Prompt-Kategorie x Rolle · 10 Prompts · 2026-02-25
        </p>

        <div style={{ position: "relative", overflowX: "auto" }}>
          <svg
            viewBox={`0 0 ${labelLeft + rollen.length * (cellW + gapX) + 20} ${labelTop + kategorien.length * (cellH + gapY) + 60}`}
            style={{ width: "100%", height: "auto", maxWidth: 780 }}
          >
            {/* Column headers (Rollen) */}
            {rollen.map((r, ri) => {
              const x = labelLeft + ri * (cellW + gapX) + cellW / 2;
              return (
                <g key={r}>
                  <text x={x} y={labelTop - 32} fill="#334155" fontSize={11} fontWeight={600} textAnchor="middle">{r}</text>
                  <text x={x} y={labelTop - 18} fill="#94a3b8" fontSize={9} textAnchor="middle">{rollenLabels[r]}</text>
                </g>
              );
            })}

            {/* Row headers (Kategorien) + cells */}
            {kategorien.map((k, ki) => {
              const y = labelTop + ki * (cellH + gapY);
              const color = catColors[k];

              return (
                <g key={k}>
                  {/* Row label */}
                  <text x={labelLeft - 10} y={y + cellH / 2 + 4} fill={color} fontSize={12} fontWeight={600} textAnchor="end">{k}</text>

                  {/* Cells */}
                  {rollen.map((r, ri) => {
                    const x = labelLeft + ri * (cellW + gapX);
                    const count = matrix[k][r];
                    const ids = details[k][r];
                    const isHovered = hover && hover.k === k && hover.r === r;
                    const intensity = count > 0 ? 0.15 + (count / maxCount) * 0.55 : 0;

                    return (
                      <g
                        key={r}
                        onMouseEnter={() => setHover({ k, r, count, ids })}
                        onMouseLeave={() => setHover(null)}
                        style={{ cursor: count > 0 ? "pointer" : "default" }}
                      >
                        <rect
                          x={x}
                          y={y}
                          width={cellW}
                          height={cellH}
                          rx={6}
                          fill={count > 0 ? color : "#f8fafc"}
                          opacity={count > 0 ? intensity : 1}
                          stroke={isHovered ? color : (count > 0 ? color : "#e2e8f0")}
                          strokeWidth={isHovered ? 2 : 1}
                          strokeOpacity={isHovered ? 0.8 : (count > 0 ? 0.3 : 1)}
                        />
                        {count > 0 && (
                          <text
                            x={x + cellW / 2}
                            y={y + cellH / 2 + 5}
                            fill="#334155"
                            fontSize={16}
                            fontWeight={700}
                            textAnchor="middle"
                          >
                            {count}
                          </text>
                        )}
                        {count === 0 && (
                          <text
                            x={x + cellW / 2}
                            y={y + cellH / 2 + 4}
                            fill="#cbd5e1"
                            fontSize={12}
                            textAnchor="middle"
                          >
                            -
                          </text>
                        )}
                      </g>
                    );
                  })}
                </g>
              );
            })}

            {/* Column totals */}
            {rollen.map((r, ri) => {
              const x = labelLeft + ri * (cellW + gapX) + cellW / 2;
              const y = labelTop + kategorien.length * (cellH + gapY) + 20;
              const total = kategorien.reduce((s, k) => s + matrix[k][r], 0);
              return (
                <text key={r} x={x} y={y} fill={total > 0 ? "#334155" : "#cbd5e1"} fontSize={11} fontWeight={600} textAnchor="middle">
                  {total > 0 ? `${total}x` : ""}
                </text>
              );
            })}
          </svg>

          {/* Tooltip */}
          {hover && hover.count > 0 && (
            <div style={{
              position: "absolute",
              bottom: 8,
              left: 0,
              right: 0,
              textAlign: "center",
              fontSize: 12,
              color: "#475569",
              background: "#f8fafc",
              padding: "6px 12px",
              borderRadius: 6,
              border: "1px solid #e2e8f0",
            }}>
              <strong>{hover.k}</strong> + <strong>{hover.r} ({rollenLabels[hover.r]})</strong>: {hover.count}x — Prompts {hover.ids.join(", ")}
            </div>
          )}
        </div>

        {/* Interpretation */}
        <div style={{ marginTop: 24, padding: "16px 20px", background: "#f8fafc", borderRadius: 8, border: "1px solid #e2e8f0" }}>
          <p style={{ fontSize: 12, color: "#475569", margin: 0, lineHeight: 1.6 }}>
            <strong style={{ color: "#334155" }}>Muster:</strong> Die Goethe-Uni wird ueberwiegend als forschende Institution (R2) wahrgenommen — aber nur in expliziten und vergleichenden Kontexten.
            In provokativen Prompts kippt die Rolle ausschliesslich zum Problemtraeger (R6).
            Beratende Funktion (R3) und autoritative Wissensquelle (R1) erscheinen nur bei direkter Nachfrage (explizit).
            R4, R5, R7 werden nie zugeschrieben.
          </p>
        </div>

      </div>
    </div>
  );
}
