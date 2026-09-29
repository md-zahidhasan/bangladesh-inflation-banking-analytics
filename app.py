"""Bangladesh Inflation & Banking dashboard (Streamlit + SQLite).
Every chart is driven by one of the 10 SQL queries from analysis_queries.sql.
Run:  streamlit run app.py
"""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Bangladesh Inflation & Banking", page_icon="📊", layout="wide")

# ---------- colours ----------
BG, CARD = "#0A1A33", "#102B52"
BLUE, SKY, ICE = "#3B82F6", "#60A5FA", "#BFDBFE"
BAD, GOOD = "#F87171", "#38BDF8"
GRID = "rgba(255,255,255,0.10)"

st.markdown(f"""
<style>
.block-container {{padding-top: 1.6rem;}}
h1, h2, h3, h4, p, label, span, div {{color: #FFFFFF;}}
[data-testid="stMetric"] {{background: linear-gradient(135deg,{CARD},#0E2547); border:1px solid #1E4B8F;
    border-radius:14px; padding:14px 18px;}}
[data-testid="stMetricLabel"] p {{color:{ICE} !important; font-size:0.85rem;}}
[data-testid="stMetricValue"] {{color:#FFFFFF;}}
.stTabs [data-baseweb="tab-list"] {{gap:6px;}}
.stTabs [data-baseweb="tab"] {{background:{CARD}; border-radius:10px 10px 0 0; padding:8px 16px;}}
.stTabs [aria-selected="true"] {{background:{BLUE};}}
[data-testid="stSidebar"] {{border-right:1px solid #1E4B8F;}}
.note {{background:{CARD}; border-left:4px solid {SKY}; padding:10px 14px; border-radius:6px; margin:6px 0 14px 0;}}
.warn {{background:#3A1F2B; border-left:4px solid {BAD}; padding:10px 14px; border-radius:6px; margin:6px 0 14px 0;}}
</style>
""", unsafe_allow_html=True)

# ---------- data ----------
CSV = Path(__file__).parent / "bangladesh_master_raw.csv"


def build_economy(raw: pd.DataFrame) -> pd.DataFrame:
    """Rebuild the 'economy' table used by the SQL file."""
    raw = raw.sort_values("Year").reset_index(drop=True)
    d = pd.DataFrame({
        "Year": raw["Year"],
        "cpi": raw["CPI_Inflation_Annual_%"],
        "food": raw["Food_Inflation_Annual_%"],
        "lending_rate": raw["Lending_Interest_Rate_%"],
        "npl": raw["NPL_percent_Total_Gross_Loans"],
        "credit_growth": raw["Private_Sector_Credit_Growth_%"],
        "deposit_growth": raw["Total_Deposit_Growth_%"],
        "depreciation": raw["Exchange_Rate_Depreciation_%"],
    })
    d["m2_growth"] = raw["Broad_Money_M2_Tk_million"].pct_change() * 100  # recomputed, as in the notebook
    d["food_gap"] = d["food"] - d["cpi"]
    d["real_lending_rate"] = d["lending_rate"] - d["cpi"]
    d["real_deposit_growth"] = d["deposit_growth"] - d["cpi"]
    d["loan_to_deposit"] = raw["Claims_Private_Sector_Tk_million"] / raw["Total_Deposits_Tk_million"] * 100
    return d


@st.cache_data
def load_raw() -> pd.DataFrame:
    return pd.read_csv(CSV)


LOGO = f"""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
  <svg width="46" height="46" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
    <rect width="48" height="48" rx="12" fill="{BLUE}"/>
    <path d="M9 36 L9 22 M17 36 L17 16 M25 36 L25 26 M33 36 L33 12" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>
    <path d="M8 18 L18 10 L26 17 L39 6" stroke="{ICE}" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
  <div style="font-size:1.05rem;font-weight:700;line-height:1.2;">Bangladesh<br>Banking &amp; Inflation</div>
</div>
<hr style="border:none;border-top:1px solid #1E4B8F;margin:12px 0 4px 0;">
"""

with st.sidebar:
    st.markdown(LOGO, unsafe_allow_html=True)
    try:
        raw = load_raw()
        eco_full = build_economy(raw)
    except Exception as e:
        st.error(f"Could not read data: {e}")
        st.stop()

    y0, y1 = int(eco_full.Year.min()), int(eco_full.Year.max())
    yr = st.slider("Year range", y0, y1, (y0, y1))
    top_n = st.slider("Rows in 'top / worst' lists", 3, 10, 5)
    thr = st.slider("High-inflation line (%)", 5.0, 12.0, 8.0, 0.5)
    split = st.slider("Era split: recent era starts", y0 + 2, y1 - 1, 2022)
    outlier = st.selectbox("Outlier year to exclude (NPL test)", ["None"] + list(eco_full.Year), index=list(eco_full.Year).index(2024) + 1 if 2024 in list(eco_full.Year) else 0)
    show_sql = st.toggle("Show SQL under each chart", value=True)

eco = eco_full[eco_full.Year.between(*yr)].copy()
con = sqlite3.connect(":memory:")
eco.to_sql("economy", con, index=False)


def q(sql, params=()):
    return pd.read_sql_query(sql, con, params=params)


def style(fig, h=380, **kw):
    fig.update_layout(height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#FFFFFF"), margin=dict(l=10, r=10, t=105, b=10),
                      title=dict(y=0.94, yanchor="top", x=0.0),
                      legend=dict(orientation="h", y=1.03, yanchor="bottom", x=0), **kw)
    fig.update_xaxes(gridcolor=GRID, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor="rgba(255,255,255,0.35)")
    return fig


def sign_colors(s):
    return [BAD if v < 0 else GOOD for v in s]


def sql_box(title, sql):
    if show_sql:
        with st.expander(f"SQL · {title}"):
            st.code(sql.strip(), language="sql")


def table(df):
    st.dataframe(df, hide_index=True, width="stretch")


def note(text, kind="note"):
    st.markdown(f'<div class="{kind}">{text}</div>', unsafe_allow_html=True)


# ---------- SQL (from analysis_queries.sql; numbers replaced by ? controls) ----------
Q1 = """SELECT Year, ROUND(cpi,2) AS inflation, RANK() OVER (ORDER BY cpi DESC) AS rnk
FROM economy ORDER BY cpi DESC LIMIT ?;"""
Q2 = """SELECT Year, ROUND(cpi,2) AS overall, ROUND(food,2) AS food, ROUND(food_gap,2) AS gap,
       CASE WHEN food_gap > 0 THEN 'Food worse' ELSE 'Food milder' END AS verdict
FROM economy WHERE food IS NOT NULL ORDER BY gap DESC;"""
Q3 = """SELECT Year, ROUND(cpi,2) AS inflation, ROUND(lending_rate,2) AS lending_rate,
       ROUND(real_lending_rate,2) AS real_lending_rate
FROM economy ORDER BY real_lending_rate LIMIT ?;"""
Q4 = """SELECT Year, ROUND(deposit_growth,2) AS deposit_growth, ROUND(cpi,2) AS inflation,
       ROUND(real_deposit_growth,2) AS real_growth
FROM economy WHERE deposit_growth IS NOT NULL ORDER BY real_growth LIMIT ?;"""
Q5 = """WITH e AS (SELECT *, CASE WHEN Year >= ? THEN 'Recent (' || ? || '+)'
                              ELSE 'Earlier (before ' || ? || ')' END AS era FROM economy)
SELECT era, COUNT(*) AS years, ROUND(AVG(cpi),2) AS avg_inflation, ROUND(AVG(npl),2) AS avg_npl,
       ROUND(AVG(credit_growth),2) AS avg_credit_growth, ROUND(AVG(deposit_growth),2) AS avg_deposit_growth,
       ROUND(AVG(m2_growth),2) AS avg_m2_growth, ROUND(AVG(depreciation),2) AS avg_depreciation,
       ROUND(AVG(real_lending_rate),2) AS avg_real_lending
FROM e GROUP BY era ORDER BY era;"""
Q6 = """SELECT CASE WHEN cpi >= ? THEN 'High inflation' ELSE 'Normal' END AS grp, COUNT(*) AS years,
       ROUND(AVG(npl),2) AS avg_npl_all,
       ROUND(AVG(CASE WHEN Year <> ? THEN npl END),2) AS avg_npl_ex_outlier
FROM economy GROUP BY grp;"""
Q7 = """SELECT Year, ROUND(cpi,2) AS inflation, ROUND(cpi - LAG(cpi) OVER (ORDER BY Year),2) AS change_pts
FROM economy ORDER BY change_pts DESC LIMIT ?;"""
Q8 = """SELECT Year, ROUND(depreciation,2) AS depreciation, ROUND(LEAD(cpi) OVER (ORDER BY Year),2) AS next_year_inflation
FROM economy WHERE depreciation IS NOT NULL ORDER BY depreciation DESC LIMIT ?;"""
Q9 = """SELECT Year, ROUND(loan_to_deposit,1) AS credit_to_deposit,
       ROUND(AVG(loan_to_deposit) OVER (ORDER BY Year ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),1) AS moving_avg_3y
FROM economy ORDER BY Year;"""
ALL = 1000  # "no limit" for charts

# ---------- header ----------
st.title("📊 Bangladesh: Inflation & Banking")
st.caption(f"{yr[0]}–{yr[1]} · {len(eco)} yearly points · exploratory only: shows association, not cause")

if len(eco) < 4:
    st.warning("Pick a wider year range.")
    st.stop()

tabs = st.tabs(["Overview", "Food vs overall", "Real returns", "Eras & bank stress",
                "Timing", "Bank funding"])

# ===== Overview (Q1) =====
with tabs[0]:
    last = eco.iloc[-1]
    peak = eco.loc[eco.cpi.idxmax()]
    npl_last = eco.dropna(subset=["npl"]).iloc[-1] if eco.npl.notna().any() else None
    c = st.columns(4)
    c[0].metric(f"Inflation {int(last.Year)}", f"{last.cpi:.1f}%", f"{last.cpi - eco.iloc[-2].cpi:+.1f} pts vs prior yr", delta_color="inverse")
    c[1].metric("Peak inflation", f"{peak.cpi:.1f}%", f"in {int(peak.Year)}", delta_color="off")
    c[2].metric(f"Real lending rate {int(last.Year)}", f"{last.real_lending_rate:.1f}%")
    if npl_last is not None:
        c[3].metric(f"Latest NPL ({int(npl_last.Year)})", f"{npl_last.npl:.1f}%")

    t = q("SELECT Year, cpi, food FROM economy ORDER BY Year")
    fig = go.Figure()
    fig.add_scatter(x=t.Year, y=t.cpi, name="Overall", mode="lines+markers", line=dict(color=SKY, width=3))
    fig.add_scatter(x=t.Year, y=t.food, name="Food", mode="lines+markers", line=dict(color=ICE, width=3, dash="dot"))
    fig.add_hline(y=thr, line_dash="dash", line_color=BAD, annotation_text=f"{thr:g}% line", annotation_font_color=BAD)
    fig.update_layout(title="Inflation over time (%)")
    st.plotly_chart(style(fig), width="stretch")

    a, b = st.columns([1, 1])
    r = q(Q1, (ALL,))
    r_top = r.head(top_n)
    with a:
        fig = go.Figure(go.Bar(x=r_top.inflation, y=r_top.Year.astype(str), orientation="h",
                               marker_color=SKY, text=r_top.inflation, textposition="outside"))
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(title=f"Top {top_n} inflation years (Q1)")
        st.plotly_chart(style(fig, 330), width="stretch")
    with b:
        st.markdown("#### Ranking table")
        table(r_top)
    sql_box("Q1 top inflation years", Q1)

# ===== Food vs overall (Q2) =====
with tabs[1]:
    r = q(Q2).sort_values("Year")
    if r.empty:
        st.info("No food inflation data in this range.")
    else:
        fig = go.Figure(go.Bar(x=r.Year, y=r.gap, marker_color=[BAD if v > 0 else GOOD for v in r.gap],
                               text=r.gap, textposition="outside"))
        fig.update_layout(title="Food minus overall inflation (points). Red = food was worse")
        st.plotly_chart(style(fig), width="stretch")
        worse = int((r.gap > 0).sum())
        note(f"Food was worse than overall inflation in <b>{worse} of {len(r)}</b> years. "
             f"Biggest gap: <b>{int(r.loc[r.gap.idxmax(), 'Year'])}</b> ({r.gap.max():+.2f} pts).")
        table(q(Q2))
    sql_box("Q2 food vs overall", Q2)

# ===== Real returns (Q3, Q4) =====
with tabs[2]:
    r3 = q(Q3, (ALL,)).sort_values("Year")
    r4 = q(Q4, (ALL,)).sort_values("Year")
    a, b = st.columns(2)
    with a:
        fig = go.Figure(go.Bar(x=r3.Year, y=r3.real_lending_rate, marker_color=sign_colors(r3.real_lending_rate)))
        fig.update_layout(title="Real lending rate (%) = lending rate − inflation (Q3)")
        st.plotly_chart(style(fig), width="stretch")
    with b:
        fig = go.Figure(go.Bar(x=r4.Year, y=r4.real_growth, marker_color=sign_colors(r4.real_growth)))
        fig.update_layout(title="Real deposit growth (%) = deposit growth − inflation (Q4)")
        st.plotly_chart(style(fig), width="stretch")
    neg3 = r3[r3.real_lending_rate < 0].Year.tolist()
    neg4 = r4[r4.real_growth < 0].Year.tolist()
    note(f"Real lending rate below zero: <b>{neg3 or 'none'}</b><br>"
         f"Deposits grew slower than prices: <b>{neg4 or 'none'}</b>")
    note("The source deposit-rate column is empty, so these two are substitutes. "
         "Real deposit growth is about the size of deposits, not what savers earn.", "warn")
    a, b = st.columns(2)
    with a:
        st.markdown(f"#### Worst {top_n} real lending rates")
        table(r3.sort_values("real_lending_rate").head(top_n))
    with b:
        st.markdown(f"#### Worst {top_n} real deposit growth")
        table(r4.sort_values("real_growth").head(top_n))
    sql_box("Q3 real lending rate", Q3)
    sql_box("Q4 real deposit growth", Q4)

# ===== Eras & bank stress (Q5, Q6) =====
with tabs[3]:
    r5 = q(Q5, (split, split, split))
    st.markdown(f"#### Earlier vs recent era (split at {split}) · Q5")
    if len(r5) == 2:
        m = r5.set_index("era").drop(columns="years").T
        labels = {"avg_inflation": "Inflation", "avg_npl": "Bad loans (NPL)", "avg_credit_growth": "Credit growth",
                  "avg_deposit_growth": "Deposit growth", "avg_m2_growth": "M2 growth",
                  "avg_depreciation": "Taka fall", "avg_real_lending": "Real lending rate"}
        fig = go.Figure()
        for col, colr in zip(m.columns, [ICE, BLUE]):
            fig.add_bar(x=[labels[i] for i in m.index], y=m[col], name=col, marker_color=colr)
        fig.update_layout(barmode="group", title="Average of each indicator, by era (%)")
        st.plotly_chart(style(fig, 400), width="stretch")
    table(r5)
    sql_box("Q5 two eras", Q5)

    st.markdown(f"#### Does high inflation mean more bad loans? (threshold {thr:g}%) · Q6")
    ex = None if outlier == "None" else int(outlier)
    r6 = q(Q6, (thr, ex if ex is not None else -1))
    if not r6.empty:
        fig = go.Figure()
        fig.add_bar(x=r6.grp, y=r6.avg_npl_all, name="All years", marker_color=BLUE, text=r6.avg_npl_all, textposition="outside")
        fig.add_bar(x=r6.grp, y=r6.avg_npl_ex_outlier, name=f"Without {ex}" if ex else "Same (no exclusion)",
                    marker_color=ICE, text=r6.avg_npl_ex_outlier, textposition="outside")
        fig.update_layout(barmode="group", title="Average NPL (%)")
        st.plotly_chart(style(fig, 360), width="stretch")
        table(r6)
    note("If the 'high inflation' bar drops a lot once the outlier year is removed, the link between inflation "
         "and bad loans rests on one year. Test it: change the outlier in the sidebar.", "warn")
    sql_box("Q6 high vs normal", Q6)

# ===== Timing (Q7, Q8) =====
with tabs[4]:
    r7 = q(Q7, (ALL,)).dropna().sort_values("Year")
    fig = go.Figure(go.Bar(x=r7.Year, y=r7.change_pts, marker_color=sign_colors(r7.change_pts)))
    fig.update_layout(title="Year-on-year change in inflation (points) · Q7")
    st.plotly_chart(style(fig), width="stretch")
    st.markdown(f"#### Biggest {top_n} accelerations")
    table(r7.sort_values("change_pts", ascending=False).head(top_n))
    sql_box("Q7 change in inflation (LAG)", Q7)

    r8 = q(Q8, (ALL,))
    r8c = r8.dropna()
    fig = go.Figure()
    fig.add_scatter(x=r8c.depreciation, y=r8c.next_year_inflation, mode="markers+text", text=r8c.Year,
                    textposition="top center", marker=dict(size=11, color=SKY), name="Year")
    if len(r8c) >= 3:
        k, b0 = np.polyfit(r8c.depreciation, r8c.next_year_inflation, 1)
        xs = np.linspace(r8c.depreciation.min(), r8c.depreciation.max(), 20)
        fig.add_scatter(x=xs, y=k * xs + b0, mode="lines", line=dict(color=ICE, dash="dash"), name="Trend")
    fig.update_layout(title="Taka depreciation this year vs inflation NEXT year · Q8",
                      xaxis_title="Depreciation (%)", yaxis_title="Next-year inflation (%)")
    st.plotly_chart(style(fig, 420), width="stretch")
    if len(r8c) >= 4:
        r_ = r8c.depreciation.corr(r8c.next_year_inflation)
        note(f"Correlation: <b>{r_:+.2f}</b> from only <b>{len(r8c)}</b> points. "
             "With so few points this is a lead to test, not proof. 2022–2024 also move together, "
             "so they count as less than 3 independent points.", "warn")
    table(r8.sort_values("depreciation", ascending=False).head(top_n))
    sql_box("Q8 depreciation vs next-year inflation (LEAD)", Q8)

# ===== Bank funding (Q9) =====
with tabs[5]:
    r9 = q(Q9)
    fig = go.Figure()
    fig.add_scatter(x=r9.Year, y=r9.credit_to_deposit, name="Credit ÷ deposits", mode="lines+markers", line=dict(color=SKY, width=3))
    fig.add_scatter(x=r9.Year, y=r9.moving_avg_3y, name="3-year average", mode="lines", line=dict(color=ICE, width=3, dash="dash"))
    fig.update_layout(title="Private credit as % of deposits · Q9", yaxis_title="%")
    st.plotly_chart(style(fig, 400), width="stretch")
    table(r9)
    sql_box("Q9 credit-to-deposit + moving average", Q9)
