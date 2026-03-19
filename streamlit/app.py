"""
GEO-Monitoring Dashboard
Liest uebersicht_*.yaml aus dem institutions-Verzeichnis und visualisiert die Kodierungen.

Tab-Struktur nach Auswertungsfragestellung:
  1. Wie sichtbar?        → S (Sichtbarkeit)
  2. Wie bewertet?        → T (Tonalität) + V (Vergleich)
  3. In welchem Rahmen?   → K (Kontext) + Th (Themenassoziation)
  4. In welcher Rolle?    → R (Rollenzuschreibung)
  5. Übersicht            → Heatmap-Matrix Kategorie × Bezug für alle Dimensionen
  6. Tabelle              → Alle Records, filterbar, CSV-Export
  7. Faktenfehler         → Records mit faktenfehler=true
  8. Längsschnitt         → Vergleich zweier Datumsstände pro prompt_id

Starten:
    cd "/Users/thilokoerkel/Dropbox/Thilo/WK/New Ground/_Claude_/_Claude_ RM/RM/streamlit"
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yaml
import glob
from pathlib import Path

# ── Konfiguration ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="New Ground - RM Dashboard",
    page_icon="🔭",
    layout="wide",
)

INSTITUTIONS_DIR = Path(__file__).parent.parent / "institutions"

# ── Farbschemata ─────────────────────────────────────────────────────────────

KAT_REIHENFOLGE = ["explizit", "implizit", "vergleichend", "kontextualisierend", "provokativ"]

KAT_FARBEN = {
    "explizit":           "#534ab7",
    "implizit":           "#1d9e75",
    "vergleichend":       "#854f0b",
    "kontextualisierend": "#185fa5",
    "provokativ":         "#a32d2d",
}

BEZUG_FARBEN = {
    "institution": "#378add",
    "thema":       "#9F77DD",
    "person":      "#EF9F27",
}

S_FARBEN = {
    "S0": "#cbd5e1",
    "S1": "#93c5fd",
    "S2": "#3b82f6",
    "S3": "#1d4ed8",
}

T_FARBEN = {
    "T+":  "#16a34a",
    "T0":  "#94a3b8",
    "T±":  "#d97706",
    "T-":  "#dc2626",
    "—":   "#e2e8f0",
}

V_FARBEN = {
    "V+":  "#16a34a",
    "V=":  "#94a3b8",
    "V0":  "#cbd5e1",
    "V-":  "#dc2626",
    "V≠":  "#9333ea",
    "—":   "#e2e8f0",
}

# ── Globale Code → Klartext-Mappings (Format: "Code (Klartext)") ─────────────

ALLE_S = ["S0", "S1", "S2", "S3"]
S_LABELS = {"S0": "S0 (nicht genannt)", "S1": "S1 (beiläufig)",
            "S2": "S2 (zentral)",       "S3": "S3 (dominant)"}
S_FARBEN_L = {S_LABELS[k]: v for k, v in S_FARBEN.items()}
S_CAPTION = " · ".join(S_LABELS.values())

ALLE_T = ["T+", "T0", "T±", "T-"]
T_LABELS = {"T+": "T+ (positiv)",    "T0": "T0 (neutral)",
            "T±": "T± (ambivalent)", "T-": "T- (negativ)"}
T_FARBEN_L = {T_LABELS[k]: v for k, v in T_FARBEN.items() if k in T_LABELS}
T_CAPTION = " · ".join(T_LABELS.values())

ALLE_V = ["V+", "V=", "V0", "V-", "V≠", "—"]
V_LABELS = {"V+": "V+ (besser positioniert)", "V=": "V= (gleichwertig)",
            "V0": "V0 (kein Vergleich)",       "V-": "V- (schlechter)",
            "V≠": "V≠ (nicht vergleichbar)",  "—":  "— (nicht kodiert)"}
V_FARBEN_L = {V_LABELS[k]: v for k, v in V_FARBEN.items() if k in V_LABELS}
V_CAPTION = " · ".join(v for k, v in V_LABELS.items() if k != "—")

ALLE_K = ["K0", "K1", "K2", "K3", "K4"]
K_LABELS = {"K0": "K0 (kein Kontext)",  "K1": "K1 (fachlich-wissenschaftlich)",
            "K2": "K2 (politikbezogen)", "K3": "K3 (gesellschaftlich)",
            "K4": "K4 (institutionell)"}
K_CAPTION = " · ".join(K_LABELS.values())

ALLE_R = ["R0","R1","R2","R3","R4","R5","R6","R7"]
R_LABELS = {"R0": "R0 (keine klare Rolle)",     "R1": "R1 (autoritative Wissensquelle)",
            "R2": "R2 (forschende Institution)", "R3": "R3 (beratende Institution)",
            "R4": "R4 (umsetzende Akteurin)",    "R5": "R5 (politischer Akteur)",
            "R6": "R6 (Problemträger)",           "R7": "R7 (Vergleichsmaßstab)"}
R_CAPTION = " · ".join(R_LABELS.values())

# Änderungsfarben für Längsschnitt
DELTA_FARBEN = {
    "besser":     "#16a34a",
    "schlechter": "#dc2626",
    "gleich":     "#94a3b8",
    "neu":        "#8b5cf6",
}

# ── Datenladen ────────────────────────────────────────────────────────────────

@st.cache_data
def lade_alle_uebersichten():
    pattern = str(INSTITUTIONS_DIR / "**" / "uebersicht*.yaml")
    dateien = glob.glob(pattern, recursive=True)
    # Dateien mit "original", "backup", "kopie" im Namen ausschließen
    dateien = [d for d in dateien
               if not any(x in Path(d).stem.lower() for x in ["original", "backup", "kopie"])]
    alle_records = []
    for datei in dateien:
        with open(datei, "r", encoding="utf-8") as f:
            daten = yaml.safe_load(f)
        institution = daten.get("institution", "Unbekannt")
        # Datum aus dem Ordnernamen lesen (zuverlässiger als kodiert_am)
        ordner_datum = Path(datei).parent.name
        kodiert_am   = daten.get("kodiert_am", ordner_datum)
        # Erhebungsdatum = Ordnername (z.B. "20260318"), falls vorhanden
        erhebungs_datum = ordner_datum if ordner_datum.isdigit() else kodiert_am
        for k in daten.get("kodierungen", []):
            def als_liste(val):
                if isinstance(val, list): return val
                if val in (None, "—", ""): return []
                return [str(val)]
            record = {
                "institution":       institution,
                "datum":             erhebungs_datum,
                "prompt_id":         k.get("prompt_id", ""),
                "prompt_kategorie":  k.get("prompt_kategorie", ""),
                "prompt_bezug":      k.get("prompt_bezug", ""),
                "prompt_thema":      k.get("prompt_thema", ""),
                "S":                 k.get("S", "S0"),
                "T":                 k.get("T", "—"),
                "V":                 k.get("V", "—"),
                "K_liste":           als_liste(k.get("K")),
                "R_liste":           als_liste(k.get("R")),
                "Th_liste":          als_liste(k.get("Th")),
                "K":                 ", ".join(als_liste(k.get("K"))) or "—",
                "R":                 ", ".join(als_liste(k.get("R"))) or "—",
                "Th":                ", ".join(als_liste(k.get("Th"))) or "—",
                "faktenfehler":      k.get("faktenfehler", False),
                "anmerkung":         k.get("anmerkung", ""),
            }
            alle_records.append(record)
    return pd.DataFrame(alle_records)


@st.cache_data
def lade_themen_labels():
    """Lädt das Th-Code → Klartextlabel-Mapping aus config/themen.yaml."""
    themen_pfad = Path(__file__).parent.parent / "config" / "themen.yaml"
    if themen_pfad.exists():
        with open(themen_pfad, "r", encoding="utf-8") as f:
            daten = yaml.safe_load(f)
        return {eintrag["id"]: eintrag["label"] for eintrag in daten if "id" in eintrag and "label" in eintrag}
    return {}

def s_zu_int(s): return {"S0": 0, "S1": 1, "S2": 2, "S3": 3}.get(s, 0)
def t_zu_int(t): return {"T+": 2, "T0": 1, "T±": 0, "T-": -1}.get(t, None)
def v_zu_int(v): return {"V+": 2, "V=": 1, "V0": 0, "V-": -1, "V≠": None}.get(v, None)

def layout_base(b=0):
    return dict(plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(l=0, r=10, t=10, b=b))

LEGEND_STD = dict(orientation="h", yanchor="bottom", y=1.02, x=0, xanchor="left")

def _fix_hover(fig):
    """Setzt ein sauberes hovertemplate auf alle Bar-Traces.
    Zeigt: x-Wert, Legendenname, y-Wert. Keine leeren Feldnamen mehr."""
    fig.update_traces(hovertemplate="%{x}<br>%{fullData.name}: %{y}<extra></extra>")
    return fig

def _fix_hover_h(fig):
    """Wie _fix_hover, aber für horizontale Balken (x/y vertauscht)."""
    fig.update_traces(hovertemplate="%{y}<br>%{fullData.name}: %{x}<extra></extra>")
    return fig

def _vollstaendige_daten(df_grouped, gruppenfeld, dim_feld, alle_codes):
    """Ergänzt fehlende Dimensions-Codes je Gruppe mit n=0,
    damit die Legende immer alle möglichen Werte zeigt."""
    gruppen = sorted(df_grouped[gruppenfeld].unique())
    idx = pd.MultiIndex.from_product([gruppen, alle_codes], names=[gruppenfeld, dim_feld])
    df_voll = df_grouped.set_index([gruppenfeld, dim_feld]).reindex(idx, fill_value=0).reset_index()
    return df_voll


# ── Grafik-Container mit Rahmen und laufender Nummer ──────────────────────────

# Zähler wird bei jedem Run zurückgesetzt (nicht persistent über Reruns)
# Wir nutzen session_state nur als Container, setzen aber immer auf 0 zurück.
st.session_state["_fig_counter"] = 0

from contextlib import contextmanager

@contextmanager
def fig_box(titel: str):
    """Zeichnet einen visuellen Rahmen um Grafiken.
    Zeigt oben links: 'Abb. N: <titel>'.
    Nutzung:  with fig_box("Tonalität (T)"):  ...st.plotly_chart(...)...
    """
    st.session_state["_fig_counter"] += 1
    nr = st.session_state["_fig_counter"]
    container = st.container(border=True)
    with container:
        st.caption(f"Abb. {nr}: {titel}")
        yield container


# ── Daten laden ───────────────────────────────────────────────────────────────

df_gesamt = lade_alle_uebersichten()

if df_gesamt.empty:
    st.error(f"Keine Übersichtsdateien gefunden unter: {INSTITUTIONS_DIR}")
    st.stop()

# ── Sidebar: Filter ───────────────────────────────────────────────────────────

with st.sidebar:
    st.title("New Ground - RM Dashboard")
    st.markdown("---")

    institutionen = sorted(df_gesamt["institution"].unique())
    inst_filter = st.multiselect("Institution", institutionen, default=institutionen)

    # Datum-Selector: nur Datumsstände der gewählten Institutionen
    verfuegbare_daten = sorted(
        df_gesamt[df_gesamt["institution"].isin(inst_filter)]["datum"].unique()
    )
    if len(verfuegbare_daten) > 1:
        datum_filter = st.selectbox(
            "Erhebungsdatum (Tabs 1–7)",
            options=verfuegbare_daten,
            index=len(verfuegbare_daten) - 1,  # Default: neuester Lauf
            help="Wählt einen einzelnen Lauf für die Auswertungs-Tabs. "
                 "Tab 8 (Längsschnitt) vergleicht zwei Läufe."
        )
    else:
        datum_filter = verfuegbare_daten[0] if verfuegbare_daten else None

    kategorien = sorted(df_gesamt["prompt_kategorie"].unique())
    kat_filter = st.multiselect("Prompt-Kategorie", kategorien, default=kategorien)

    bezuege = sorted(df_gesamt["prompt_bezug"].unique())
    bezug_filter = st.multiselect("Prompt-Bezug", bezuege, default=bezuege)

    s_werte = sorted(df_gesamt["S"].unique())
    s_filter = st.multiselect("Sichtbarkeit", s_werte, default=s_werte)

    st.markdown("---")
    nur_fehler = st.checkbox("Nur Faktenfehler anzeigen", value=False)

# ── Filtern: Tabs 1–7 zeigen immer nur EINEN Lauf ────────────────────────────

df = df_gesamt[
    df_gesamt["institution"].isin(inst_filter) &
    (df_gesamt["datum"] == datum_filter) &
    df_gesamt["prompt_kategorie"].isin(kat_filter) &
    df_gesamt["prompt_bezug"].isin(bezug_filter) &
    df_gesamt["S"].isin(s_filter)
].copy()

if nur_fehler:
    df = df[df["faktenfehler"] == True]

df["S_int"] = df["S"].map(s_zu_int)
df["T_int"] = df["T"].map(t_zu_int)
df["V_int"] = df["V"].map(v_zu_int)
df["label"] = df["prompt_id"] + " · " + df["prompt_thema"].str[:38]

# ── Header + KPIs ─────────────────────────────────────────────────────────────

st.title("New Ground - RM Dashboard")
st.caption(f"Erhebung: {datum_filter} · {len(df)} von {len(df_gesamt)} Records gesamt")

# Vorherigen Lauf ermitteln für Deltas
_vorige_daten = sorted(
    d for d in df_gesamt[df_gesamt["institution"].isin(inst_filter)]["datum"].unique()
    if d < datum_filter
)
df_prev = None
if _vorige_daten:
    _prev_datum = _vorige_daten[-1]
    df_prev = df_gesamt[
        df_gesamt["institution"].isin(inst_filter) &
        (df_gesamt["datum"] == _prev_datum)
    ]

c1, c2, c3, c4, c5 = st.columns(5)
n = len(df)
s0 = len(df[df["S"] == "S0"])
s_sichtbar = n - s0
t_pos = len(df[df["T"] == "T+"])
ff = len(df[df["faktenfehler"] == True])

def _delta_str(diff, label="vs. Vorlauf"):
    """Formatiert ein Delta als '+3 vs. Vorlauf' / '-1 vs. Vorlauf' / '±0 vs. Vorlauf'."""
    if diff == 0:
        return f"±0 {label}"
    return f"{diff:+d} {label}"

def _delta_color(diff, invers=False):
    """Gibt 'off' bei 0, sonst 'normal' oder 'inverse'."""
    if diff == 0:
        return "off"
    return "inverse" if invers else "normal"

if df_prev is not None and len(df_prev) > 0:
    n_p       = len(df_prev)
    s0_p      = len(df_prev[df_prev["S"] == "S0"])
    sicht_p   = n_p - s0_p
    tpos_p    = len(df_prev[df_prev["T"] == "T+"])
    ff_p      = len(df_prev[df_prev["faktenfehler"] == True])
    d_n       = n - n_p
    d_sicht   = s_sichtbar - sicht_p
    d_s0      = s0 - s0_p
    d_tpos    = t_pos - tpos_p
    d_ff      = ff - ff_p
    c1.metric("Records", n,
              delta=_delta_str(d_n), delta_color=_delta_color(d_n))
    c2.metric("Sichtbar (S\u22651)", s_sichtbar,
              delta=_delta_str(d_sicht), delta_color=_delta_color(d_sicht))
    c3.metric("Nicht genannt (S0)", s0,
              delta=_delta_str(d_s0), delta_color=_delta_color(d_s0, invers=True))
    c4.metric("Positiv (T+)", t_pos,
              delta=_delta_str(d_tpos), delta_color=_delta_color(d_tpos))
    c5.metric("Faktenfehler", ff,
              delta=_delta_str(d_ff), delta_color=_delta_color(d_ff, invers=True))
else:
    c1.metric("Records", n)
    c2.metric("Sichtbar (S\u22651)", s_sichtbar)
    c3.metric("Nicht genannt (S0)", s0)
    c4.metric("Positiv (T+)", t_pos)
    c5.metric("Faktenfehler", ff)

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab_s, tab_tv, tab_kth, tab_r, tab_matrix, tab_tabelle, tab_fehler, tab_laengs = st.tabs([
    "📊 Wie sichtbar?",
    "🎭 Wie bewertet?",
    "🗂️ In welchem Rahmen?",
    "🎭 In welcher Rolle?",
    "🔲 Übersicht",
    "📋 Tabelle",
    "⚠️ Faktenfehler",
    "📈 Längsschnitt",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — WIE SICHTBAR?  (Dimension S)
# ══════════════════════════════════════════════════════════════════════════════

with tab_s:
    st.subheader("Sichtbarkeit (S) — Wird die Institution genannt, und wie prominent?")
    st.caption(S_CAPTION)

    with fig_box("Sichtbarkeit je Prompt"):
        fig = px.bar(
            df.sort_values("S_int"),
            x="S_int", y="label",
            color="prompt_kategorie",
            color_discrete_map=KAT_FARBEN,
            orientation="h",
            hover_data={"S": True, "T": True, "V": True, "anmerkung": True,
                        "S_int": False, "label": False},
            labels={"S_int": "", "label": "", "prompt_kategorie": "Kategorie"},
            category_orders={"prompt_kategorie": KAT_REIHENFOLGE},
            range_x=[0, 3.5],
        )
        fig.update_layout(
            height=max(480, len(df) * 22),
            xaxis=dict(tickvals=[0,1,2,3],
                       ticktext=[S_LABELS[s] for s in ALLE_S]),
            legend=LEGEND_STD, legend_title_text="",
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=280, r=10, t=30, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)

    with fig_box("Sichtbarkeit – Verteilung"):
        s_cnt = df["S"].value_counts().reset_index()
        s_cnt.columns = ["S", "n"]
        for code in ALLE_S:
            if code not in set(s_cnt["S"]):
                s_cnt = pd.concat([s_cnt, pd.DataFrame([{"S": code, "n": 0}])], ignore_index=True)
        s_cnt["S"] = pd.Categorical(s_cnt["S"], categories=ALLE_S, ordered=True)
        s_cnt = s_cnt.sort_values("S")
        s_cnt["S_label"] = s_cnt["S"].map(S_LABELS)
        fig_d = px.bar(s_cnt, x="S_label", y="n", color="S_label",
                       color_discrete_map=S_FARBEN_L, text="n",
                       category_orders={"S_label": [S_LABELS[s] for s in ALLE_S]},
                       labels={"S_label": "", "n": "Anzahl"})
        fig_d.update_traces(textposition="outside")
        fig_d.update_layout(height=260, showlegend=False, **layout_base())
        _fix_hover(fig_d)
        st.plotly_chart(fig_d, use_container_width=True)

    ALLE_S_LABELS = [S_LABELS[s] for s in ALLE_S]

    with fig_box("Sichtbarkeit nach Prompt-Bezug"):
        df_sb = df.groupby(["prompt_bezug", "S"]).size().reset_index(name="n")
        df_sb = _vollstaendige_daten(df_sb, "prompt_bezug", "S", ALLE_S)
        df_sb["S_label"] = df_sb["S"].map(S_LABELS)
        fig_sb = px.bar(df_sb, x="prompt_bezug", y="n", color="S_label",
                        color_discrete_map=S_FARBEN_L,
                        barmode="stack",
                        category_orders={"S_label": ALLE_S_LABELS},
                        labels={"prompt_bezug": "", "n": "Anzahl"})
        fig_sb.update_layout(height=260, **layout_base(),
                             legend=LEGEND_STD, legend_title_text="")
        _fix_hover(fig_sb)
        st.plotly_chart(fig_sb, use_container_width=True)

    with fig_box("Sichtbarkeit nach Prompt-Kategorie"):
        df_sk = df.groupby(["prompt_kategorie", "S"]).size().reset_index(name="n")
        df_sk = _vollstaendige_daten(df_sk, "prompt_kategorie", "S", ALLE_S)
        df_sk["S_label"] = df_sk["S"].map(S_LABELS)
        fig_sk = px.bar(df_sk, x="prompt_kategorie", y="n", color="S_label",
                        color_discrete_map=S_FARBEN_L,
                        barmode="stack",
                        category_orders={"S_label": ALLE_S_LABELS, "prompt_kategorie": KAT_REIHENFOLGE},
                        labels={"prompt_kategorie": "", "n": "Anzahl"})
        fig_sk.update_layout(height=260, **layout_base(),
                             legend=LEGEND_STD, legend_title_text="",
                             xaxis=dict(tickangle=-30))
        _fix_hover(fig_sk)
        st.plotly_chart(fig_sk, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — WIE BEWERTET?  (T + V)
# ══════════════════════════════════════════════════════════════════════════════

with tab_tv:
    st.subheader("Tonalität (T) und Vergleichspositionierung (V)")
    st.caption(T_CAPTION + "\n\n" + V_CAPTION)

    ALLE_T_LABELS = [T_LABELS[t] for t in ALLE_T]
    ALLE_V_LABELS = [V_LABELS[v] for v in ALLE_V]

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Tonalität (T)")
        df_t = df[df["T"] != "—"]

        with fig_box("Tonalität – Verteilung"):
            t_cnt = df_t["T"].value_counts().reset_index()
            t_cnt.columns = ["T", "n"]
            for code in ALLE_T:
                if code not in set(t_cnt["T"]):
                    t_cnt = pd.concat([t_cnt, pd.DataFrame([{"T": code, "n": 0}])], ignore_index=True)
            t_cnt["T"] = pd.Categorical(t_cnt["T"], categories=ALLE_T, ordered=True)
            t_cnt = t_cnt.sort_values("T")
            t_cnt["T_label"] = t_cnt["T"].map(T_LABELS)
            fig_t = px.bar(t_cnt, x="T_label", y="n", color="T_label",
                           color_discrete_map=T_FARBEN_L, text="n",
                           category_orders={"T_label": ALLE_T_LABELS},
                           labels={"T_label": "", "n": "Anzahl"})
            fig_t.update_traces(textposition="outside")
            fig_t.update_layout(height=260, showlegend=False, **layout_base())
            _fix_hover(fig_t)
            st.plotly_chart(fig_t, use_container_width=True)

        with fig_box("Tonalität nach Prompt-Kategorie"):
            df_tk = df_t.groupby(["prompt_kategorie", "T"]).size().reset_index(name="n")
            df_tk = _vollstaendige_daten(df_tk, "prompt_kategorie", "T", ALLE_T)
            df_tk["T_label"] = df_tk["T"].map(T_LABELS)
            fig_tk = px.bar(df_tk, x="prompt_kategorie", y="n", color="T_label",
                            color_discrete_map=T_FARBEN_L, barmode="stack",
                            category_orders={"T_label": ALLE_T_LABELS, "prompt_kategorie": KAT_REIHENFOLGE},
                            labels={"prompt_kategorie": "", "n": "Anzahl"})
            fig_tk.update_layout(height=220, **layout_base(),
                                 legend=LEGEND_STD, legend_title_text="",
                                 xaxis=dict(tickangle=-30))
            _fix_hover(fig_tk)
            st.plotly_chart(fig_tk, use_container_width=True)

        with fig_box("Tonalität nach Prompt-Bezug"):
            df_tb = df_t.groupby(["prompt_bezug", "T"]).size().reset_index(name="n")
            df_tb = _vollstaendige_daten(df_tb, "prompt_bezug", "T", ALLE_T)
            df_tb["T_label"] = df_tb["T"].map(T_LABELS)
            fig_tb = px.bar(df_tb, x="prompt_bezug", y="n", color="T_label",
                            color_discrete_map=T_FARBEN_L, barmode="stack",
                            category_orders={"T_label": ALLE_T_LABELS},
                            labels={"prompt_bezug": "", "n": "Anzahl"})
            fig_tb.update_layout(height=200, **layout_base(),
                                 legend=LEGEND_STD, legend_title_text="")
            _fix_hover(fig_tb)
            st.plotly_chart(fig_tb, use_container_width=True)

    with col_r:
        st.markdown("#### Vergleichspositionierung (V)")

        with fig_box("Vergleichspositionierung – Verteilung"):
            v_cnt = df["V"].value_counts().reset_index()
            v_cnt.columns = ["V", "n"]
            for code in ALLE_V:
                if code not in set(v_cnt["V"]):
                    v_cnt = pd.concat([v_cnt, pd.DataFrame([{"V": code, "n": 0}])], ignore_index=True)
            v_cnt["V"] = pd.Categorical(v_cnt["V"], categories=ALLE_V, ordered=True)
            v_cnt = v_cnt.sort_values("V")
            v_cnt["V_label"] = v_cnt["V"].map(V_LABELS)
            fig_v = px.bar(v_cnt, x="V_label", y="n", color="V_label",
                           color_discrete_map=V_FARBEN_L, text="n",
                           category_orders={"V_label": ALLE_V_LABELS},
                           labels={"V_label": "", "n": "Anzahl"})
            fig_v.update_traces(textposition="outside")
            fig_v.update_layout(height=260, showlegend=False, **layout_base())
            _fix_hover(fig_v)
            st.plotly_chart(fig_v, use_container_width=True)

        with fig_box("Vergleichspositionierung nach Prompt-Kategorie"):
            df_vk = df.groupby(["prompt_kategorie", "V"]).size().reset_index(name="n")
            df_vk = _vollstaendige_daten(df_vk, "prompt_kategorie", "V", ALLE_V)
            df_vk["V_label"] = df_vk["V"].map(V_LABELS)
            fig_vk = px.bar(df_vk, x="prompt_kategorie", y="n", color="V_label",
                            color_discrete_map=V_FARBEN_L, barmode="stack",
                            category_orders={"V_label": ALLE_V_LABELS, "prompt_kategorie": KAT_REIHENFOLGE},
                            labels={"prompt_kategorie": "", "n": "Anzahl"})
            fig_vk.update_layout(height=220, **layout_base(),
                                 legend=LEGEND_STD, legend_title_text="",
                                 xaxis=dict(tickangle=-30))
            _fix_hover(fig_vk)
            st.plotly_chart(fig_vk, use_container_width=True)

        with fig_box("Vergleichspositionierung nach Prompt-Bezug"):
            df_vb = df.groupby(["prompt_bezug", "V"]).size().reset_index(name="n")
            df_vb = _vollstaendige_daten(df_vb, "prompt_bezug", "V", ALLE_V)
            df_vb["V_label"] = df_vb["V"].map(V_LABELS)
            fig_vb = px.bar(df_vb, x="prompt_bezug", y="n", color="V_label",
                            color_discrete_map=V_FARBEN_L, barmode="stack",
                            category_orders={"V_label": ALLE_V_LABELS},
                            labels={"prompt_bezug": "", "n": "Anzahl"})
            fig_vb.update_layout(height=200, **layout_base(),
                                 legend=LEGEND_STD, legend_title_text="")
            _fix_hover(fig_vb)
            st.plotly_chart(fig_vb, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — IN WELCHEM RAHMEN?  (K + Th)
# ══════════════════════════════════════════════════════════════════════════════

with tab_kth:
    st.subheader("Kontext (K) und Themenassoziation (Th)")
    st.caption(K_CAPTION + "\n\nTh = freitextliche Themenassoziationen, die das LLM der Institution zuschreibt")

    K_FARBEN_MAP = {k: c for k, c in zip(ALLE_K, px.colors.qualitative.Set2)}
    K_FARBEN_L_MAP = {K_LABELS[k]: c for k, c in K_FARBEN_MAP.items()}
    ALLE_K_LABELS = [K_LABELS[k] for k in ALLE_K]

    k_records = []
    for _, row in df.iterrows():
        for k in row["K_liste"]:
            k_records.append({"K": k, "prompt_kategorie": row["prompt_kategorie"],
                               "prompt_bezug": row["prompt_bezug"]})
    df_k = pd.DataFrame(k_records) if k_records else pd.DataFrame(
        columns=["K","prompt_kategorie","prompt_bezug"])

    TH_LABELS = lade_themen_labels()

    th_records = []
    for _, row in df.iterrows():
        for th in row["Th_liste"]:
            th_records.append({"Th": th,
                               "Th_label": TH_LABELS.get(th, th),
                               "prompt_kategorie": row["prompt_kategorie"],
                               "prompt_bezug": row["prompt_bezug"]})
    df_th = pd.DataFrame(th_records) if th_records else pd.DataFrame(
        columns=["Th","Th_label","prompt_kategorie","prompt_bezug"])

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Kontext (K)")

        if df_k.empty:
            st.info("Keine K-Codes in der aktuellen Auswahl.")
        else:
            with fig_box("Kontext – Verteilung"):
                k_cnt = df_k["K"].value_counts().reset_index()
                k_cnt.columns = ["K", "n"]
                for code in ALLE_K:
                    if code not in set(k_cnt["K"]):
                        k_cnt = pd.concat([k_cnt, pd.DataFrame([{"K": code, "n": 0}])], ignore_index=True)
                k_cnt["K"] = pd.Categorical(k_cnt["K"], categories=ALLE_K, ordered=True)
                k_cnt = k_cnt.sort_values("K")
                k_cnt["K_label"] = k_cnt["K"].map(K_LABELS)
                fig_k = px.bar(k_cnt, x="K_label", y="n", text="n", color="K_label",
                               color_discrete_map=K_FARBEN_L_MAP,
                               category_orders={"K_label": ALLE_K_LABELS},
                               labels={"K_label": "", "n": "Nennungen"})
                fig_k.update_traces(textposition="outside")
                fig_k.update_layout(height=260, showlegend=False, **layout_base())
                _fix_hover(fig_k)
                st.plotly_chart(fig_k, use_container_width=True)

            with fig_box("Kontext nach Prompt-Kategorie"):
                df_kk = df_k.groupby(["prompt_kategorie", "K"]).size().reset_index(name="n")
                df_kk = _vollstaendige_daten(df_kk, "prompt_kategorie", "K", ALLE_K)
                df_kk["K_label"] = df_kk["K"].map(K_LABELS)
                fig_kk = px.bar(df_kk, x="prompt_kategorie", y="n", color="K_label",
                                color_discrete_map=K_FARBEN_L_MAP,
                                barmode="stack",
                                category_orders={"K_label": ALLE_K_LABELS, "prompt_kategorie": KAT_REIHENFOLGE},
                                labels={"prompt_kategorie": "", "n": "Nennungen"})
                fig_kk.update_layout(height=220, **layout_base(),
                                     legend=LEGEND_STD, legend_title_text="",
                                     xaxis=dict(tickangle=-30))
                _fix_hover(fig_kk)
                st.plotly_chart(fig_kk, use_container_width=True)

    with col_r:
        st.markdown("#### Themenassoziation (Th)")

        if df_th.empty:
            st.info("Keine Th-Codes in der aktuellen Auswahl.")
        else:
            with fig_box("Themenassoziation – Top 20"):
                th_cnt = df_th.groupby(["Th", "Th_label"]).size().reset_index(name="n")
                th_cnt = th_cnt.sort_values("n", ascending=True).tail(20)
                fig_th = px.bar(
                    th_cnt,
                    x="n", y="Th_label", orientation="h", text="n", color="n",
                    color_continuous_scale=[[0,"#e0e7ff"],[1,"#4338ca"]],
                    hover_data={"Th": True, "Th_label": False, "n": True},
                    labels={"Th_label": "", "n": "Nennungen", "Th": "Code"},
                )
                fig_th.update_traces(textposition="outside")
                fig_th.update_layout(height=max(420, len(th_cnt) * 28),
                                     showlegend=False,
                                     coloraxis_showscale=False, **layout_base())
                st.plotly_chart(fig_th, use_container_width=True)

            with fig_box("Top-Themen nach Prompt-Bezug"):
                top_th = th_cnt.nlargest(8, "n")["Th"].tolist()
                df_thb = df_th[df_th["Th"].isin(top_th)].groupby(
                    ["prompt_bezug","Th","Th_label"]).size().reset_index(name="n")
                fig_thb = px.bar(df_thb, x="Th_label", y="n", color="prompt_bezug",
                                 color_discrete_map=BEZUG_FARBEN, barmode="group",
                                 hover_data={"Th": True, "Th_label": False},
                                 labels={"Th_label": "", "n": "Nennungen", "Th": "Code"})
                fig_thb.update_layout(height=260, **layout_base(),
                                      legend=LEGEND_STD, legend_title_text="",
                                      xaxis=dict(tickangle=-30))
                _fix_hover(fig_thb)
                st.plotly_chart(fig_thb, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — IN WELCHER ROLLE?  (R)
# ══════════════════════════════════════════════════════════════════════════════

with tab_r:
    st.subheader("Rollenzuschreibung (R)")
    st.caption(R_CAPTION)

    R_FARBEN = {
        "R0": "#e2e8f0", "R1": "#3b82f6", "R2": "#8b5cf6",
        "R3": "#06b6d4", "R4": "#f59e0b", "R5": "#10b981",
        "R6": "#ef4444", "R7": "#6366f1",
    }
    R_FARBEN_L = {R_LABELS[k]: v for k, v in R_FARBEN.items()}
    ALLE_R_LABELS = [R_LABELS[r] for r in ALLE_R]

    r_records = []
    for _, row in df.iterrows():
        for r in row["R_liste"]:
            r_records.append({"R": r, "R_label": R_LABELS.get(r, r),
                               "prompt_kategorie": row["prompt_kategorie"],
                               "prompt_bezug": row["prompt_bezug"], "label": row["label"]})
    df_r = pd.DataFrame(r_records) if r_records else pd.DataFrame(
        columns=["R","R_label","prompt_kategorie","prompt_bezug","label"])

    col_l, col_r = st.columns([1, 1])

    with col_l:
        if df_r.empty:
            st.info("Keine R-Codes in der aktuellen Auswahl.")
        else:
            with fig_box("Rollenzuschreibung – Verteilung"):
                r_cnt = df_r["R_label"].value_counts().reset_index()
                r_cnt.columns = ["R_label", "n"]
                for label in ALLE_R_LABELS:
                    if label not in set(r_cnt["R_label"]):
                        r_cnt = pd.concat([r_cnt, pd.DataFrame([{"R_label": label, "n": 0}])], ignore_index=True)
                fig_r = px.bar(
                    r_cnt.sort_values("n", ascending=True),
                    x="n", y="R_label", orientation="h", text="n", color="n",
                    color_continuous_scale=[[0,"#fce7f3"],[1,"#9d174d"]],
                    labels={"R_label": "", "n": "Nennungen"},
                )
                fig_r.update_traces(textposition="outside")
                fig_r.update_layout(height=340, showlegend=False,
                                    coloraxis_showscale=False, **layout_base())
                st.plotly_chart(fig_r, use_container_width=True)

    with col_r:
        if not df_r.empty:
            with fig_box("Rollenzuschreibung nach Prompt-Kategorie"):
                df_rk = df_r.groupby(["prompt_kategorie", "R"]).size().reset_index(name="n")
                df_rk = _vollstaendige_daten(df_rk, "prompt_kategorie", "R", ALLE_R)
                df_rk["R_label"] = df_rk["R"].map(R_LABELS)
                fig_rk = px.bar(df_rk, x="prompt_kategorie", y="n", color="R_label",
                                color_discrete_map=R_FARBEN_L, barmode="stack",
                                category_orders={"R_label": ALLE_R_LABELS, "prompt_kategorie": KAT_REIHENFOLGE},
                                labels={"prompt_kategorie": "", "n": "Nennungen"})
                fig_rk.update_layout(height=260, **layout_base(),
                                     legend=LEGEND_STD, legend_title_text="",
                                     xaxis=dict(tickangle=-30))
                _fix_hover(fig_rk)
                st.plotly_chart(fig_rk, use_container_width=True)

            with fig_box("Rollenzuschreibung nach Prompt-Bezug"):
                df_rb = df_r.groupby(["prompt_bezug", "R"]).size().reset_index(name="n")
                df_rb = _vollstaendige_daten(df_rb, "prompt_bezug", "R", ALLE_R)
                df_rb["R_label"] = df_rb["R"].map(R_LABELS)
                fig_rb = px.bar(df_rb, x="prompt_bezug", y="n", color="R_label",
                                color_discrete_map=R_FARBEN_L, barmode="stack",
                                category_orders={"R_label": ALLE_R_LABELS},
                                labels={"prompt_bezug": "", "n": "Nennungen"})
                fig_rb.update_layout(height=220, **layout_base(),
                                     legend=LEGEND_STD, legend_title_text="")
                _fix_hover(fig_rb)
                st.plotly_chart(fig_rb, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ÜBERSICHT  (Heatmap-Matrix)
# ══════════════════════════════════════════════════════════════════════════════

with tab_matrix:
    st.subheader("Übersicht: Kategorie × Bezug")
    st.caption("Mittlere Kodierungswerte pro Zelle der Prompt-Matrix.")

    dim_wahl = st.radio("Dimension",
        options=["Sichtbarkeit (S)", "Tonalität (T)", "Vergleich (V)"], horizontal=True)

    df_m = df.copy()
    df_m["prompt_kategorie"] = pd.Categorical(
        df_m["prompt_kategorie"], categories=KAT_REIHENFOLGE, ordered=True)

    if dim_wahl == "Sichtbarkeit (S)":
        pivot = df_m.pivot_table(index="prompt_kategorie", columns="prompt_bezug",
                                 values="S_int", aggfunc="mean", observed=False).round(2)
        colorscale = [[0,"#f1f5f9"],[0.33,"#93c5fd"],[0.66,"#3b82f6"],[1,"#1d4ed8"]]
        zmin, zmax = 0, 3
        tickvals = [0,1,2,3]; ticktext = ["S0","S1","S2","S3"]; ctitle = "S"
    elif dim_wahl == "Tonalität (T)":
        pivot = df_m.pivot_table(index="prompt_kategorie", columns="prompt_bezug",
                                 values="T_int", aggfunc="mean", observed=False).round(2)
        colorscale = [[0,"#dc2626"],[0.375,"#d97706"],[0.625,"#94a3b8"],[1,"#16a34a"]]
        zmin, zmax = -1, 2
        tickvals = [-1,0,1,2]; ticktext = ["T-","T±","T0","T+"]; ctitle = "T"
    else:
        pivot = df_m.pivot_table(index="prompt_kategorie", columns="prompt_bezug",
                                 values="V_int", aggfunc="mean", observed=False).round(2)
        colorscale = [[0,"#dc2626"],[0.5,"#94a3b8"],[1,"#16a34a"]]
        zmin, zmax = -1, 2
        tickvals = [-1,0,1,2]; ticktext = ["V-","V=","V0","V+"]; ctitle = "V"

    text_vals = [[f"{v:.1f}" if pd.notna(v) else "—" for v in row] for row in pivot.values]

    fig_h = go.Figure(go.Heatmap(
        z=pivot.values, x=list(pivot.columns), y=list(pivot.index),
        colorscale=colorscale, zmin=zmin, zmax=zmax,
        text=text_vals, texttemplate="%{text}",
        textfont={"size": 18, "color": "white"}, showscale=True,
        colorbar=dict(tickvals=tickvals, ticktext=ticktext, title=ctitle),
    ))
    fig_h.update_layout(height=380, margin=dict(l=10,r=10,t=20,b=10),
                        xaxis=dict(title="Prompt-Bezug"),
                        yaxis=dict(title="Prompt-Kategorie"))
    st.plotly_chart(fig_h, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — TABELLE
# ══════════════════════════════════════════════════════════════════════════════

with tab_tabelle:
    st.subheader("Alle Records")

    df_anz = df[["prompt_id","prompt_kategorie","prompt_bezug","prompt_thema",
                 "S","T","V","K","R","Th","faktenfehler","anmerkung"]].copy()
    df_anz["faktenfehler"] = df_anz["faktenfehler"].map({True: "⚠️", False: "", None: ""})

    st.dataframe(
        df_anz, use_container_width=True, height=520,
        column_config={
            "prompt_id":        st.column_config.TextColumn("ID",        width=90),
            "prompt_kategorie": st.column_config.TextColumn("Kategorie", width=130),
            "prompt_bezug":     st.column_config.TextColumn("Bezug",     width=100),
            "prompt_thema":     st.column_config.TextColumn("Thema",     width=180),
            "S":  st.column_config.TextColumn("S",  width=45),
            "T":  st.column_config.TextColumn("T",  width=45),
            "V":  st.column_config.TextColumn("V",  width=45),
            "K":  st.column_config.TextColumn("K",  width=80),
            "R":  st.column_config.TextColumn("R",  width=80),
            "Th": st.column_config.TextColumn("Th", width=160),
            "faktenfehler": st.column_config.TextColumn("⚠️", width=40),
            "anmerkung":    st.column_config.TextColumn("Anmerkung", width=340),
        },
        hide_index=True,
    )

    csv = df_anz.to_csv(index=False, sep=";").encode("utf-8")
    st.download_button("↓ CSV exportieren", data=csv,
                       file_name=f"geo_{datum_filter}.csv", mime="text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — FAKTENFEHLER
# ══════════════════════════════════════════════════════════════════════════════

with tab_fehler:
    st.subheader("Faktenfehler")
    st.caption("Records mit faktenfehler=true — unabhängig von den aktiven Sidebar-Filtern.")

    df_fe = df_gesamt[df_gesamt["faktenfehler"] == True][
        ["datum","prompt_id","prompt_kategorie","prompt_bezug","prompt_thema","S","T","anmerkung"]
    ].sort_values("datum")

    if df_fe.empty:
        st.success("Keine Faktenfehler in den geladenen Daten.")
    else:
        st.error(f"{len(df_fe)} Faktenfehler gefunden (alle Läufe).")
        st.dataframe(df_fe, use_container_width=True, hide_index=True,
                     column_config={
                         "datum":    st.column_config.TextColumn("Datum", width=90),
                         "anmerkung": st.column_config.TextColumn("Anmerkung / Fehlerdetail", width=380),
                     })
        st.markdown("""
**Warum relevant?** Faktenfehler zeigen, wo das Modell Personen oder Sachverhalte
fälschlich der Zielinstitution zuordnet. Das ist ein direktes Reputationsrisiko.
Bei Person-Bezügen (P) treten Faktenfehler systematisch häufiger auf.
""")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 8 — LÄNGSSCHNITT
# ══════════════════════════════════════════════════════════════════════════════

with tab_laengs:
    st.subheader("Längsschnitt: Vergleich zweier Erhebungsläufe")
    st.caption("Zeigt pro Prompt-ID die Kodierung von Lauf A vs. Lauf B und hebt Veränderungen hervor.")

    alle_daten = sorted(df_gesamt[df_gesamt["institution"].isin(inst_filter)]["datum"].unique())

    if len(alle_daten) < 2:
        st.info("Für den Längsschnitt werden mindestens zwei Erhebungsläufe benötigt. "
                "Bisher ist nur ein Datum vorhanden.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            lauf_a = st.selectbox("Lauf A (älter / Baseline)", alle_daten,
                                  index=0, key="ls_a")
        with col_b:
            lauf_b = st.selectbox("Lauf B (neuer / Vergleich)", alle_daten,
                                  index=len(alle_daten)-1, key="ls_b")

        if lauf_a == lauf_b:
            st.warning("Bitte zwei verschiedene Läufe auswählen.")
        else:
            # ── Daten der zwei Läufe holen ────────────────────────────────────
            df_a = df_gesamt[
                (df_gesamt["institution"].isin(inst_filter)) &
                (df_gesamt["datum"] == lauf_a)
            ].set_index("prompt_id")

            df_b = df_gesamt[
                (df_gesamt["institution"].isin(inst_filter)) &
                (df_gesamt["datum"] == lauf_b)
            ].set_index("prompt_id")

            # Alle prompt_ids aus beiden Läufen
            alle_ids = sorted(set(df_a.index) | set(df_b.index))

            # ── Differenztabelle aufbauen ─────────────────────────────────────
            def delta_symbol(val_a, val_b, dimension):
                """Gibt ein Icon zurück das die Richtung der Änderung zeigt."""
                if val_a == val_b:
                    return ""
                ordnung = {
                    "S": ["S0","S1","S2","S3"],
                    "T": ["T-","T±","T0","T+"],
                    "V": ["V-","V=","V0","V+","V≠"],
                }
                if dimension not in ordnung:
                    return "↔"
                skala = ordnung[dimension]
                try:
                    ia = skala.index(val_a)
                    ib = skala.index(val_b)
                    if ib > ia: return "↑"
                    if ib < ia: return "↓"
                except ValueError:
                    pass
                return "↔"

            rows = []
            for pid in alle_ids:
                in_a = pid in df_a.index
                in_b = pid in df_b.index
                if not in_a or not in_b:
                    continue  # nur Prompts die in beiden Läufen vorhanden sind

                ra = df_a.loc[pid]
                rb = df_b.loc[pid]

                s_a, s_b = ra["S"], rb["S"]
                t_a, t_b = ra["T"], rb["T"]
                v_a, v_b = ra["V"], rb["V"]
                fe_a, fe_b = ra["faktenfehler"], rb["faktenfehler"]

                geaendert = (s_a != s_b) or (t_a != t_b) or (v_a != v_b)

                rows.append({
                    "prompt_id":        pid,
                    "kategorie":        ra["prompt_kategorie"],
                    "bezug":            ra["prompt_bezug"],
                    "thema":            ra["prompt_thema"][:40],
                    f"S ({lauf_a})":    s_a,
                    f"S ({lauf_b})":    s_b,
                    "ΔS":               delta_symbol(s_a, s_b, "S"),
                    f"T ({lauf_a})":    t_a,
                    f"T ({lauf_b})":    t_b,
                    "ΔT":               delta_symbol(t_a, t_b, "T"),
                    f"V ({lauf_a})":    v_a,
                    f"V ({lauf_b})":    v_b,
                    "ΔV":               delta_symbol(v_a, v_b, "V"),
                    f"⚠️ ({lauf_a})":   "⚠️" if fe_a else "",
                    f"⚠️ ({lauf_b})":   "⚠️" if fe_b else "",
                    "geaendert":        geaendert,
                })

            df_delta = pd.DataFrame(rows)

            if df_delta.empty:
                st.warning("Keine übereinstimmenden prompt_ids in beiden Läufen gefunden.")
            else:
                # ── KPI-Zeile ─────────────────────────────────────────────────
                n_geaendert = df_delta["geaendert"].sum()
                n_gesamt    = len(df_delta)
                s_besser = sum(1 for r in rows if r["ΔS"] == "↑")
                s_schlechter = sum(1 for r in rows if r["ΔS"] == "↓")
                t_besser = sum(1 for r in rows if r["ΔT"] == "↑")
                t_schlechter = sum(1 for r in rows if r["ΔT"] == "↓")

                k1,k2,k3,k4,k5 = st.columns(5)
                k1.metric("Prompts verglichen", n_gesamt)
                k2.metric("Verändert (S/T/V)", n_geaendert)
                k3.metric("S verbessert ↑", s_besser)
                k4.metric("S verschlechtert ↓", s_schlechter, delta_color="inverse")
                k5.metric("T verbessert ↑", t_besser)

                st.markdown("---")

                # ── Filter: nur Veränderungen zeigen ─────────────────────────
                nur_delta = st.checkbox("Nur veränderte Prompts anzeigen", value=True)
                df_show = df_delta[df_delta["geaendert"]] if nur_delta else df_delta
                df_show = df_show.drop(columns=["geaendert"])

                st.dataframe(
                    df_show,
                    use_container_width=True,
                    height=min(60 + len(df_show) * 36, 560),
                    hide_index=True,
                    column_config={
                        "prompt_id":  st.column_config.TextColumn("ID",       width=80),
                        "kategorie":  st.column_config.TextColumn("Kategorie",width=120),
                        "bezug":      st.column_config.TextColumn("Bezug",    width=90),
                        "thema":      st.column_config.TextColumn("Thema",    width=200),
                        "ΔS": st.column_config.TextColumn("ΔS", width=36),
                        "ΔT": st.column_config.TextColumn("ΔT", width=36),
                        "ΔV": st.column_config.TextColumn("ΔV", width=36),
                    },
                )

                st.markdown("---")

                # ── Balkendiagramm: S-Verteilung Lauf A vs B ─────────────────
                st.markdown("#### Sichtbarkeit (S): Lauf A vs. Lauf B")
                col_l, col_r = st.columns(2)

                for col, lauf, df_lauf in [
                    (col_l, lauf_a, df_a),
                    (col_r, lauf_b, df_b),
                ]:
                    with col:
                        st.caption(f"Lauf {lauf}")
                        ALLE_S = ["S0", "S1", "S2", "S3"]
                        s_cnt = df_lauf["S"].value_counts().reset_index()
                        s_cnt.columns = ["S", "n"]
                        for code in ALLE_S:
                            if code not in set(s_cnt["S"]):
                                s_cnt = pd.concat([s_cnt, pd.DataFrame([{"S": code, "n": 0}])], ignore_index=True)
                        s_cnt["S"] = pd.Categorical(s_cnt["S"], categories=ALLE_S, ordered=True)
                        s_cnt = s_cnt.sort_values("S")
                        fig_s = px.bar(s_cnt, x="S", y="n",
                                       color="S", color_discrete_map=S_FARBEN,
                                       text="n", labels={"S":"","n":"Anzahl"})
                        fig_s.update_traces(textposition="outside")
                        fig_s.update_layout(height=240, showlegend=False, **layout_base())
                        st.plotly_chart(fig_s, use_container_width=True)

                # ── Tonalität: A vs B ─────────────────────────────────────────
                st.markdown("#### Tonalität (T): Lauf A vs. Lauf B")
                col_l, col_r = st.columns(2)
                for col, lauf, df_lauf in [
                    (col_l, lauf_a, df_a),
                    (col_r, lauf_b, df_b),
                ]:
                    with col:
                        st.caption(f"Lauf {lauf}")
                        ALLE_T_LS = ["T+", "T0", "T±", "T-"]
                        t_cnt = df_lauf[df_lauf["T"] != "—"]["T"].value_counts().reset_index()
                        t_cnt.columns = ["T", "n"]
                        for code in ALLE_T_LS:
                            if code not in set(t_cnt["T"]):
                                t_cnt = pd.concat([t_cnt, pd.DataFrame([{"T": code, "n": 0}])], ignore_index=True)
                        t_cnt["T"] = pd.Categorical(t_cnt["T"], categories=ALLE_T_LS, ordered=True)
                        t_cnt = t_cnt.sort_values("T")
                        fig_t = px.bar(t_cnt, x="T", y="n",
                                       color="T", color_discrete_map=T_FARBEN,
                                       text="n", labels={"T":"","n":"Anzahl"})
                        fig_t.update_traces(textposition="outside")
                        fig_t.update_layout(height=220, showlegend=False, **layout_base())
                        st.plotly_chart(fig_t, use_container_width=True)

                # ── S0-Konsistenz: welche Prompts waren in beiden Läufen S0? ──
                st.markdown("#### Persistente Nicht-Sichtbarkeit (S0 in beiden Läufen)")
                s0_beide = [
                    r for r in rows
                    if r[f"S ({lauf_a})"] == "S0" and r[f"S ({lauf_b})"] == "S0"
                ]
                if s0_beide:
                    st.error(f"{len(s0_beide)} Prompt(s) in beiden Läufen S0 — robuste GEO-Lücke:")
                    for r in s0_beide:
                        st.markdown(f"- **{r['prompt_id']}** · {r['kategorie']} · {r['bezug']} · _{r['thema']}_")
                else:
                    st.success("Kein Prompt war in beiden Läufen S0.")
