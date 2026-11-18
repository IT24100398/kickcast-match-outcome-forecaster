import json, joblib, io, base64
import numpy as np, pandas as pd
import streamlit as st
import matplotlib as mpl
import matplotlib.pyplot as plt

import os
if not os.path.exists(".streamlit/config.toml"):
    os.makedirs(".streamlit", exist_ok=True)
    open(".streamlit/config.toml", "w").write('[theme]\nbase = "light"\nprimaryColor = "#0b5ed7"\nbackgroundColor = "#f5f8fc"\n'
                                              'secondaryBackgroundColor = "#eaf1f8"\ntextColor = "#0f2747"\n')

st.set_page_config(page_title="KickCast", page_icon="⚽", layout="wide")

# ------------------------- KickCast light palette -------------------------
TXT, SUB, LINE = "#0f2747", "#5b6b82", "#e3e9f1"
TEAL, BLUE = "#1fa39a", "#2f6fe4"
AWAY, DRAW, HOME = "#8e44e8", "#f4b400", "#2fc16a"

st.markdown(f"""
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{background:#f5f8fc !important;color:{TXT} !important}}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp p, .stApp li, .stApp label, .stApp span {{color:{TXT}}}
.stTabs [data-baseweb="tab"] p {{color:{TXT} !important}}
[data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-baseweb="base-input"] {{background:#ffffff !important;color:{TXT} !important}}
[data-testid="stVerticalBlockBorderWrapper"] {{background:#ffffff;border-color:{LINE}}}
.stButton > button[kind="primary"] {{background:#0b5ed7;color:#ffffff;border:none}}
.stButton > button[kind="primary"] p {{color:#ffffff !important}}
[data-testid="stSidebar"] {{background:#eaf1f8;}}
.card {{background:#fff;border:1px solid {LINE};border-radius:14px;padding:14px 18px;margin-bottom:10px;box-shadow:0 1px 4px rgba(15,39,71,0.06)}}
.card .lab {{font-size:0.8rem;color:{SUB}}}
.card .val {{font-size:1.65rem;font-weight:700;color:{TXT}}}
.kpi {{display:flex;align-items:center;gap:14px}}
.badge {{width:46px;height:46px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.3rem}}
.result {{background:#e7f6f5;border:1px solid #8fd3cd;border-radius:14px;padding:22px 26px;display:flex;align-items:center;gap:22px}}
.result .big {{width:70px;height:70px;border-radius:50%;background:#cdeeea;display:flex;align-items:center;justify-content:center;font-size:2rem}}
.result h2 {{color:{TEAL};margin:0;font-weight:800;letter-spacing:0.5px}} .result p {{color:{TXT};margin:6px 0 10px 0}}
.tag {{display:inline-block;background:#fff;border:1.5px solid {TEAL};color:{TXT};border-radius:22px;padding:5px 14px;margin:3px 6px 3px 0;font-size:0.88rem;font-weight:600}}
.bar-bg {{background:#e5eaf1;border-radius:8px;height:10px;width:100%}} .bar-fg {{height:10px;border-radius:8px}}
.cm {{margin:4px;padding:14px 10px;min-height:70px;box-sizing:border-box;border-radius:10px;text-align:center;font-weight:700;display:flex;flex-direction:column;justify-content:center;gap:6px;line-height:1.35}}
.good {{background:#d9f2ec;color:#0f766e}} .bad {{background:#ffe0e0;color:#c0264b}}
.side-card {{background:#fff;border:1px solid {LINE};border-radius:12px;padding:12px 14px;margin-bottom:12px;font-size:0.9rem;color:{TXT}}}
.side-warn {{background:#fff4d6;border:1px solid #f6dc8b;border-radius:12px;padding:10px 14px;color:#8a5a00;font-size:0.9rem}}
.stTabs [data-baseweb="tab-highlight"] {{background-color:{TEAL};height:3px}}
.stTabs [aria-selected="true"] {{color:{TXT};font-weight:700}}
table.res {{width:100%;border-collapse:collapse;background:#fff;border:1px solid {LINE};border-radius:8px;font-size:0.9rem}}
table.res th {{background:#eaf1f8;color:{TXT};text-align:left;padding:8px 10px}}
table.res td {{padding:7px 10px;border-top:1px solid {LINE};color:{TXT}}}
</style>""", unsafe_allow_html=True)

mpl.rcParams.update({"figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
                     "text.color": TXT, "axes.labelcolor": SUB, "xtick.color": SUB, "ytick.color": SUB,
                     "axes.edgecolor": LINE, "axes.grid": True, "grid.color": "#edf1f6", "axes.axisbelow": True,
                     "axes.spines.top": False, "axes.spines.right": False})

LEAGUES = {"league_1": "Belgium Jupiler League", "league_1729": "England Premier League", "league_4769": "France Ligue 1",
           "league_7809": "Germany Bundesliga", "league_10257": "Italy Serie A", "league_13274": "Netherlands Eredivisie",
           "league_15722": "Poland Ekstraklasa", "league_17642": "Portugal Liga ZON Sagres",
           "league_19694": "Scotland Premier League", "league_21518": "Spain LIGA BBVA", "league_24558": "Switzerland Super League"}
CLASSES = ["Away win", "Draw", "Home win"]
COLORS = [AWAY, DRAW, HOME]

def show_fig(fig):
    """Show a matplotlib figure as an embedded image, so it does not depend on extra file requests through the tunnel."""
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=110, bbox_inches="tight"); plt.close(fig)
    b64 = base64.b64encode(buf.getvalue()).decode()
    st.markdown(f'<img src="data:image/png;base64,{b64}" style="width:100%;height:auto">', unsafe_allow_html=True)

def card(label, value): return f'<div class="card"><div class="lab">{label}</div><div class="val">{value}</div></div>'
def kpi(icon, bg, label, value):
    return (f'<div class="card kpi"><div class="badge" style="background:{bg}">{icon}</div>'
            f'<div><div class="lab">{label}</div><div class="val">{value}</div></div></div>')
def bar(pct, color=TEAL): return f'<div class="bar-bg"><div class="bar-fg" style="width:{min(max(pct,0),100):.0f}%;background:{color}"></div></div>'

@st.cache_resource
def load():
    feats = json.load(open("final_feature_sets.json"))
    return (feats, joblib.load("rf_no_odds.joblib"), joblib.load("rf_with_odds.joblib"),
            pd.read_csv("results_all.csv"), pd.read_csv("season_outcomes.csv", index_col=0),
            pd.read_csv("predictions_test.csv"))
feats, rf_no, rf_odds, results, season, preds = load()

# ------------------------------ sidebar ------------------------------
st.sidebar.markdown(f"<h2 style='color:{TXT};margin-bottom:0'>⚽ KickCast</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='side-card'><b>About</b><br>Predicts a football result before kick-off from team form and optional odds.</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='side-card'><b>Model:</b> Random Forest<br><b>Data:</b> ~26k matches<br><b>Leagues:</b> 11<br><b>Test:</b> 2014/15 - 2015/16</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='side-warn'>ⓘ Football is uncertain. Read as probabilities.</div>", unsafe_allow_html=True)

st.caption("IT3091 · Group 2026-DS-59 · European Soccer Database")
st.markdown(f"<h1 style='color:{TXT};margin-top:0'>KickCast · match outcome forecaster</h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["Check a match", "Model dashboard"])

# ======================= TAB 1: CHECK A MATCH =======================
with tab1:
    st.markdown("#### Match details")
    c0, c00 = st.columns(2)
    with c0.container(border=True):
        league = st.selectbox("🏆 League", list(LEAGUES), format_func=LEAGUES.get)
    with c00.container(border=True):
        stage = st.slider("📅 Matchday (stage)", 1, 38, 15)

    c1, c2 = st.columns(2)
    with c1.container(border=True):
        st.markdown("**🏠 Home team form**")
        h_pts = st.slider("Form: avg points, last 5", 0.0, 3.0, 1.6, 0.1, key="hp")
        h_gf = st.slider("Avg goals scored, last 5", 0.0, 4.0, 1.5, 0.1, key="hg")
        h_ga = st.slider("Avg goals conceded, last 5", 0.0, 4.0, 1.2, 0.1, key="ha")
        h_ppg = st.slider("Points per game this season", 0.0, 3.0, 1.5, 0.05, key="hs")
    with c2.container(border=True):
        st.markdown("**✈️ Away team form**")
        a_pts = st.slider("Form: avg points, last 5", 0.0, 3.0, 1.3, 0.1, key="ap")
        a_gf = st.slider("Avg goals scored, last 5", 0.0, 4.0, 1.2, 0.1, key="ag")
        a_ga = st.slider("Avg goals conceded, last 5", 0.0, 4.0, 1.4, 0.1, key="aa")
        a_ppg = st.slider("Points per game this season", 0.0, 3.0, 1.2, 0.05, key="as")

    use_odds = st.checkbox("Also use bookmaker odds (Bet365 decimal odds)")
    if use_odds:
        o1, o2, o3 = st.columns(3)
        oh = o1.number_input("Home win odds", 1.01, 30.0, 2.10, 0.05)
        od = o2.number_input("Draw odds", 1.01, 30.0, 3.40, 0.05)
        oa = o3.number_input("Away win odds", 1.01, 30.0, 3.60, 0.05)

    if st.button("📊 Predict outcome", type="primary"):
        row = {c: 0.0 for c in feats["features_with_odds"]}
        row[league] = 1.0
        row.update({"stage": stage, "diff_form_pts": h_pts - a_pts, "diff_form_gf": h_gf - a_gf,
                    "diff_form_ga": h_ga - a_ga, "diff_season_ppg": h_ppg - a_ppg})
        if use_odds:
            raw = np.array([1 / oh, 1 / od, 1 / oa]); p = raw / raw.sum()
            row.update({"prob_H": p[0], "prob_D": p[1]})
            model, cols = rf_odds, feats["features_with_odds"]
        else:
            model, cols = rf_no, feats["features_no_odds"]
        proba = model.predict_proba(pd.DataFrame([row])[cols])[0]
        top = int(np.argmax(proba)); conf = proba[top]
        level = "High" if conf >= 0.55 else "Moderate" if conf >= 0.42 else "Low"
        headline = {0: "AWAY WIN LIKELY", 1: "DRAW LIKELY", 2: "HOME WIN LIKELY"}[top]
        tags = ["⭐ Clear favourite" if conf >= 0.55 else "🔍 Open match" if conf < 0.42 else "👍 Slight favourite"]
        if proba[1] >= 0.30: tags.append("⚖️ Draw risk")
        if abs(proba[0] - proba[2]) < 0.08: tags.append("📈 Evenly matched")
        if use_odds: tags.append("🪙 Odds included")
        st.markdown(f"""<div class="result"><div class="big">🏆</div><div>
            <h2>{headline}</h2><p>Model confidence: <b>{conf*100:.0f}%</b> ({level})</p>
            {''.join(f'<span class="tag">{t}</span>' for t in tags)}</div></div>""", unsafe_allow_html=True)

        st.markdown("#### Predicted probabilities")
        for i, c in enumerate(st.columns(3)):
            c.markdown(card(CLASSES[i], f"{proba[i]*100:.0f}%") + bar(proba[i] * 100, COLORS[i]), unsafe_allow_html=True)

        st.markdown("#### Team strength snapshot")
        for col, lab, hv, av, lo, hi in zip(st.columns(3),
                ["Recent form (points)", "Season points per game", "Goal balance (scored − conceded)"],
                [h_pts, h_ppg, h_gf - h_ga], [a_pts, a_ppg, a_gf - a_ga], [0, 0, -4], [3, 3, 4]):
            f = lambda v: (v - lo) / (hi - lo) * 100
            col.markdown(card(lab, f"{hv:.1f} vs {av:.1f}") + "<small>Home</small>" + bar(f(hv), HOME)
                         + "<small>Away</small>" + bar(f(av), AWAY), unsafe_allow_html=True)

# ======================= TAB 2: MODEL DASHBOARD =======================
with tab2:
    exp = st.radio("Feature set:", ["No odds", "With odds"], horizontal=True)
    r = results[results.features == exp]
    best = r[~r.model.str.startswith(("Baseline", "Reference"))].sort_values("macro_F1", ascending=False).iloc[0]
    base = r[r.model == "Baseline: always Home win"].iloc[0]
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(kpi("🏆", "#d9f2ec", "Highest macro F1", best.model), unsafe_allow_html=True)
    k2.markdown(kpi("📊", "#dbe8ff", "Test macro F1", f"{best.macro_F1:.3f}"), unsafe_allow_html=True)
    k3.markdown(kpi("🎯", "#d9f2ec", "Draw recall", f"{best.draw_recall:.3f}"), unsafe_allow_html=True)
    k4.markdown(kpi("📄", "#dbe8ff", "Baseline macro F1", f"{base.macro_F1:.3f}"), unsafe_allow_html=True)

    left, right = st.columns(2)
    with left.container(border=True):
        st.markdown("**Model comparison — test seasons**")
        metric = st.selectbox("Metric", ["macro_F1", "accuracy", "draw_recall", "weighted_F1"])
        order = ["Baseline: always Home win", "Logistic Regression", "Random Forest", "Decision Tree", "XGBoost"]
        v = [r[r.model == m][metric].values[0] for m in order]
        fig, ax = plt.subplots(figsize=(6, 3.3))
        bars = ax.bar(["Baseline", "Logistic", "RForest", "DTree", "XGBoost"], v, color=["#b8bec7", TEAL, TEAL, TEAL, TEAL])
        for b, val in zip(bars, v): ax.text(b.get_x() + b.get_width() / 2, val + 0.005, f"{val:.2f}", ha="center", fontsize=9, color=TXT)
        ax.set_ylabel(metric); show_fig(fig)
        st.caption("Accuracy alone is misleading: always predicting Home gives about 44% accuracy but never finds a draw.")
    with right.container(border=True):
        st.markdown("**Confidence bands — test set**")
        st.caption("How often the model was right at each confidence level")
        d = preds[preds.features == exp].copy()
        d["conf"] = d[["p_away", "p_draw", "p_home"]].max(axis=1)
        d["correct"] = (d.pred == d.actual)
        d["band"] = pd.cut(d.conf, bins=[0, 0.40, 0.50, 0.60, 1.01], labels=["<40%", "40-50%", "50-60%", "60%+"], right=False)
        g = d.groupby("band", observed=False).agg(matches=("correct", "size"), hit=("correct", "mean")).reset_index()
        fig, ax = plt.subplots(figsize=(6, 3.3))
        bars = ax.bar(g.band.astype(str), g.hit, color=BLUE)
        for b, (_, row_) in zip(bars, g.iterrows()):
            ax.text(b.get_x() + b.get_width() / 2, row_.hit + 0.015, f"{row_.hit*100:.0f}%\n(n={row_.matches})", ha="center", fontsize=8, color=TXT)
        ax.set_ylim(0, 1.05); ax.set_ylabel("share predicted correctly"); show_fig(fig)

    with st.container(border=True):
        st.markdown(f"**Confusion matrix — test set, Random Forest ({exp.lower()})**")
        st.caption(f"{len(d):,} matches")
        cm = pd.crosstab(d.actual, d.pred).reindex(index=[0, 1, 2], columns=[0, 1, 2], fill_value=0)
        cols = st.columns([1.1, 1, 1, 1])
        for i in range(3): cols[i + 1].markdown(f"<div style='text-align:center;font-size:0.82rem;color:{SUB}'>Predicted: {CLASSES[i]}</div>", unsafe_allow_html=True)
        for a in range(3):
            cols = st.columns([1.1, 1, 1, 1])
            cols[0].markdown(f"<div style='padding:20px 0 0 4px;font-size:0.85rem;color:{SUB}'>Actual: {CLASSES[a]}</div>", unsafe_allow_html=True)
            for p_ in range(3):
                n = int(cm.loc[a, p_]); share = n / cm.loc[a].sum() * 100
                lab = "correct" if a == p_ else "missed draw" if a == 1 else "false draw" if p_ == 1 else "wrong side"
                cols[p_ + 1].markdown(f"<div class='cm {'good' if a == p_ else 'bad'}'>{n:,} · {lab}<br><small>{share:.0f}% of row</small></div>", unsafe_allow_html=True)

    st.markdown("##### All results")
    tbl = results[results.features == exp].set_index("model").drop(columns=["features", "log_loss"]).round(3)
    st.markdown(tbl.to_html(classes="res", border=0), unsafe_allow_html=True)
    st.info("The four models are within about 0.01 macro F1 of each other, so none is clearly best. Bookmaker odds add about +0.05.")
