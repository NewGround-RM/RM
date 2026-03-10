import { useState } from "react";

const data = [
  { id: "0001", attribut: "implizit", kontext: "Wirtschaftswiss.", s: 0, anmerkung: "Nicht genannt - Frankfurt School statt Goethe-Uni" },
  { id: "0002", attribut: "implizit", kontext: "Philosophie/SoWi", s: 1, anmerkung: "Beilaeufig, auf Kritische Theorie reduziert" },
  { id: "0011", attribut: "explizit", kontext: "Wirtschaftswiss.", s: 3, anmerkung: "Dominant: fuehrendes Zentrum, EZB/Bundesbank" },
  { id: "0012", attribut: "explizit", kontext: "Philosophie/SoWi", s: 3, anmerkung: "Dominant: internationales Renommee" },
  { id: "0021", attribut: "vergleichend", kontext: "Wirtschaftswiss.", s: 2, anmerkung: "Eigener Abschnitt, als Finance-Spezialist" },
  { id: "0022", attribut: "vergleichend", kontext: "Philosophie/SoWi", s: 1, anmerkung: "Nische hinter LMU" },
  { id: "0031", attribut: "kontextual.", kontext: "Politikber. Wi", s: 1, anmerkung: "Nur Standort Frankfurt, nicht die Uni" },
  { id: "0032", attribut: "kontextual.", kontext: "Politikber. Ges", s: 0, anmerkung: "Nicht genannt, keine Uni erwaehnt" },
  { id: "0041", attribut: "provokativ", kontext: "Massenuni", s: 2, anmerkung: "Explizit als Negativbeispiel" },
  { id: "0042", attribut: "provokativ", kontext: "Exzellenz Kritik", s: 2, anmerkung: "Schwaecher als erhofft" },
];

const catColors = {
  "implizit": "#2563eb",
  "explizit": "#7c3aed",
  "vergleichend": "#0891b2",
  "kontextual.": "#059669",
  "provokativ": "#dc2626",
};

const sLabels = ["S0 keine", "S1 beilaeufig", "S2 zentral", "S3 dominant"];
const maxS = 3;

export default function Sichtbarkeit() {
  const [hover, setHover] = useState(null);

  const barMaxWidth = 320;
  const labelWidth = 160;
  const rowHeight = 44;
  const chartTop = 60;
  const chartLeft = labelWidth + 16;
  const totalHeight = chartTop + data.length * rowHeight + 80;
  const totalWidth = chartLeft + barMaxWidth + 40;

  return (
    <div style={{ fontFamily: "'IBM Plex Sans', 'Segoe UI', sans-serif", background: "#ffffff", color: "#1e293b", minHeight: "100vh", padding: "32px 24px" }}>
      <div style={{ maxWidth: 680, margin: "0 auto" }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, color: "#0f172a", margin: "0 0 4px 0", letterSpacing: "-0.02em" }}>
          Sichtbarkeit · Goethe-Universitat Frankfurt
        </h1>
        <p style={{ fontSize: 12, color: "#94a3b8", margin: "0 0 24px 0" }}>
          GEO-Monitoring · 10 Prompts · Claude Sonnet 4 · 2026-02-25
        </p>

        <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 20 }}>
          {Object.entries(catColors).map(([cat, col]) => (
            <div key={cat} style={{ display: "flex", alignItems: "center", gap: 5 }}>
              <div style={{ width: 10, height: 10, borderRadius: 2, background: col }} />
              <span style={{ fontSize: 11, color: "#64748b" }}>{cat}</span>
            </div>
          ))}
        </div>

        <svg viewBox={`0 0 ${totalWidth} ${totalHeight}`} style={{ width: "100%", height: "auto" }}>
          {[0, 1, 2, 3].map(s => {
            const x = chartLeft + (s / maxS) * barMaxWidth;
            return (
              <g key={s}>
                <line x1={x} y1={chartTop - 10} x2={x} y2={chartTop + data.length * rowHeight} stroke="#e2e8f0" strokeWidth={1} />
                <text x={x} y={chartTop - 18} fill="#94a3b8" fontSize={10} textAnchor="middle">{sLabels[s]}</text>
              </g>
            );
          })}

          {data.map((d, i) => {
            const y = chartTop + i * rowHeight;
            const barWidth = (d.s / maxS) * barMaxWidth;
            const color = catColors[d.attribut] || "#64748b";
            const isHovered = hover === i;

            return (
              <g key={d.id}
                onMouseEnter={() => setHover(i)}
                onMouseLeave={() => setHover(null)}
                style={{ cursor: "pointer" }}
              >
                {isHovered && (
                  <rect x={0} y={y} width={totalWidth} height={rowHeight} fill="#f8fafc" rx={4} />
                )}

                <text x={labelWidth} y={y + 18} fill="#334155" fontSize={11} textAnchor="end" fontWeight={isHovered ? 600 : 400}>
                  {d.id} {d.kontext}
                </text>
                <text x={labelWidth} y={y + 32} fill={color} fontSize={9} textAnchor="end" fontWeight={500}>
                  {d.attribut}
                </text>

                {d.s > 0 ? (
                  <rect
                    x={chartLeft}
                    y={y + 6}
                    width={barWidth}
                    height={22}
                    rx={3}
                    fill={color}
                    opacity={isHovered ? 0.95 : 0.75}
                  />
                ) : (
                  <g>
                    <line x1={chartLeft} y1={y + 17} x2={chartLeft + 18} y2={y + 17} stroke="#cbd5e1" strokeWidth={2} strokeDasharray="3,3" />
                    <text x={chartLeft + 24} y={y + 21} fill="#94a3b8" fontSize={10} fontStyle="italic">nicht genannt</text>
                  </g>
                )}

                {d.s > 0 && (
                  <text
                    x={chartLeft + barWidth + 6}
                    y={y + 21}
                    fill="#64748b"
                    fontSize={10}
                    fontWeight={600}
                  >
                    S{d.s}
                  </text>
                )}

                {isHovered && (
                  <foreignObject x={chartLeft} y={y + 32} width={barMaxWidth} height={24}>
                    <div style={{ fontSize: 10, color: "#64748b", lineHeight: 1.3, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {d.anmerkung}
                    </div>
                  </foreignObject>
                )}
              </g>
            );
          })}

          {(() => {
            const y = chartTop + data.length * rowHeight + 30;
            const counts = [0, 0, 0, 0];
            data.forEach(d => counts[d.s]++);
            return (
              <g>
                <text x={0} y={y} fill="#64748b" fontSize={11} fontWeight={600}>Verteilung</text>
                {counts.map((c, s) => (
                  <g key={s}>
                    <text x={chartLeft + (s / maxS) * barMaxWidth} y={y} fill="#334155" fontSize={11} textAnchor="middle" fontWeight={600}>
                      {c}x
                    </text>
                  </g>
                ))}
              </g>
            );
          })()}
        </svg>

      </div>
    </div>
  );
}
