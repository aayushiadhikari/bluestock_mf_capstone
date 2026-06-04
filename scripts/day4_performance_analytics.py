
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"
NOTEBOOKS.mkdir(exist_ok=True)

def md(text):
    return nbf.v4.new_markdown_cell(text.strip())

def code(text):
    return nbf.v4.new_code_cell(text.strip())

nb = nbf.v4.new_notebook()
cells = []

cells.append(md("""
# Day 4 — Fund Performance Analytics

This notebook computes:
- Daily returns
- CAGR for 1yr, 3yr and 5yr
- Sharpe Ratio
- Sortino Ratio
- Alpha and Beta against Nifty 100
- Maximum Drawdown
- Fund Scorecard
- Benchmark comparison chart
"""))

cells.append(code("""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress
from pathlib import Path

sns.set_style("whitegrid")

DATA = Path("../data/processed")
REPORTS = Path("../reports")
REPORTS.mkdir(exist_ok=True)

nav = pd.read_csv(DATA / "clean_nav_history.csv")
fund_master = pd.read_csv(DATA / "clean_fund_master.csv")
benchmark = pd.read_csv(DATA / "clean_benchmark_indices.csv")

nav["date"] = pd.to_datetime(nav["date"])
benchmark["date"] = pd.to_datetime(benchmark["date"])

nav["amfi_code"] = nav["amfi_code"].astype(str)
fund_master["amfi_code"] = fund_master["amfi_code"].astype(str)

print("Data loaded successfully")
print(nav.shape, benchmark.shape, fund_master.shape)
"""))

cells.append(md("## 1. Compute Daily Returns"))
cells.append(code("""
nav = nav.sort_values(["amfi_code", "date"]).copy()
nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change().fillna(0)

plt.figure(figsize=(10,6))
sns.histplot(nav["daily_return"], bins=100, kde=True)
plt.title("Daily Return Distribution Across All Funds")
plt.xlabel("Daily Return")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig(REPORTS / "daily_return_distribution.png", dpi=300, bbox_inches="tight")
plt.show()

nav["daily_return"].describe()
"""))

cells.append(md("## 2. CAGR for 1yr, 3yr and 5yr"))
cells.append(code("""
def cagr(group, days):
    group = group.sort_values("date").dropna(subset=["nav"])
    if len(group) < 2:
        return np.nan
    period = group.tail(days) if len(group) > days else group
    start_nav = period["nav"].iloc[0]
    end_nav = period["nav"].iloc[-1]
    years = len(period) / 252
    if start_nav <= 0 or years <= 0:
        return np.nan
    return ((end_nav / start_nav) ** (1 / years) - 1) * 100

rows = []
for code, g in nav.groupby("amfi_code"):
    rows.append({
        "amfi_code": code,
        "cagr_1yr_pct": cagr(g, 252),
        "cagr_3yr_pct": cagr(g, 756),
        "cagr_5yr_pct": cagr(g, 1260)
    })

cagr_report = pd.DataFrame(rows).merge(
    fund_master[["amfi_code", "scheme_name", "fund_house", "category", "sub_category", "expense_ratio_pct"]],
    on="amfi_code",
    how="left"
)

cagr_report.to_csv(DATA / "cagr_report.csv", index=False)
cagr_report.head()
"""))

cells.append(md("## 3. Sharpe Ratio and Sortino Ratio"))
cells.append(code("""
RF = 0.065

risk_rows = []
for code, g in nav.groupby("amfi_code"):
    r = g["daily_return"].dropna()
    annual_return = r.mean() * 252
    annual_vol = r.std() * np.sqrt(252)
    sharpe = (annual_return - RF) / annual_vol if annual_vol != 0 else np.nan

    downside = r[r < 0]
    downside_vol = downside.std() * np.sqrt(252)
    sortino = (annual_return - RF) / downside_vol if downside_vol != 0 else np.nan

    risk_rows.append({
        "amfi_code": code,
        "annual_return_pct": annual_return * 100,
        "annual_volatility_pct": annual_vol * 100,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino
    })

sharpe_sortino_report = pd.DataFrame(risk_rows).merge(
    fund_master[["amfi_code", "scheme_name", "fund_house", "category", "sub_category", "expense_ratio_pct"]],
    on="amfi_code",
    how="left"
).sort_values("sharpe_ratio", ascending=False)

sharpe_sortino_report.to_csv(DATA / "sharpe_sortino_report.csv", index=False)
sharpe_sortino_report.head(10)
"""))

cells.append(md("## 4. Alpha and Beta using Nifty 100"))
cells.append(code("""
benchmark = benchmark.sort_values(["index_name", "date"]).copy()
benchmark["benchmark_return"] = benchmark.groupby("index_name")["close_value"].pct_change()

print(benchmark["index_name"].unique())
"""))

cells.append(code("""
nifty100 = benchmark[
    benchmark["index_name"].str.contains("Nifty 100", case=False, na=False)
][["date", "benchmark_return"]].dropna()

if nifty100.empty:
    nifty100 = benchmark.groupby("date")["benchmark_return"].mean().reset_index()

ab_rows = []
for code, g in nav.groupby("amfi_code"):
    fund_r = g[["date", "daily_return"]].dropna()
    merged = fund_r.merge(nifty100, on="date", how="inner").dropna()

    if len(merged) < 30:
        alpha, beta, r2 = np.nan, np.nan, np.nan
    else:
        reg = linregress(merged["benchmark_return"], merged["daily_return"])
        beta = reg.slope
        alpha = reg.intercept * 252 * 100
        r2 = reg.rvalue ** 2

    ab_rows.append({
        "amfi_code": code,
        "alpha_pct": alpha,
        "beta": beta,
        "r_squared": r2
    })

alpha_beta = pd.DataFrame(ab_rows).merge(
    fund_master[["amfi_code", "scheme_name", "fund_house", "category", "sub_category"]],
    on="amfi_code",
    how="left"
)

alpha_beta.to_csv(DATA / "alpha_beta.csv", index=False)
alpha_beta.sort_values("alpha_pct", ascending=False).head(10)
"""))

cells.append(md("## 5. Maximum Drawdown"))
cells.append(code("""
dd_rows = []
for code, g in nav.groupby("amfi_code"):
    g = g.sort_values("date").copy()
    g["running_max"] = g["nav"].cummax()
    g["drawdown"] = g["nav"] / g["running_max"] - 1

    max_dd = g["drawdown"].min()
    trough_date = g.loc[g["drawdown"].idxmin(), "date"]
    peak_date = g.loc[g[g["date"] <= trough_date]["nav"].idxmax(), "date"]

    dd_rows.append({
        "amfi_code": code,
        "max_drawdown_pct": max_dd * 100,
        "peak_date": peak_date,
        "trough_date": trough_date
    })

max_drawdown_report = pd.DataFrame(dd_rows).merge(
    fund_master[["amfi_code", "scheme_name", "fund_house", "category", "sub_category"]],
    on="amfi_code",
    how="left"
)

max_drawdown_report.to_csv(DATA / "max_drawdown_report.csv", index=False)
max_drawdown_report.sort_values("max_drawdown_pct").head(10)
"""))

cells.append(md("## 6. Fund Scorecard"))
cells.append(code("""
scorecard = cagr_report.merge(
    sharpe_sortino_report[["amfi_code", "sharpe_ratio", "sortino_ratio", "annual_volatility_pct"]],
    on="amfi_code",
    how="left"
).merge(
    alpha_beta[["amfi_code", "alpha_pct", "beta", "r_squared"]],
    on="amfi_code",
    how="left"
).merge(
    max_drawdown_report[["amfi_code", "max_drawdown_pct", "peak_date", "trough_date"]],
    on="amfi_code",
    how="left"
)

scorecard["rank_3yr_return"] = scorecard["cagr_3yr_pct"].rank(pct=True)
scorecard["rank_sharpe"] = scorecard["sharpe_ratio"].rank(pct=True)
scorecard["rank_alpha"] = scorecard["alpha_pct"].rank(pct=True)

scorecard["rank_expense_inverse"] = scorecard["expense_ratio_pct"].rank(pct=True, ascending=False)
scorecard["rank_drawdown_inverse"] = scorecard["max_drawdown_pct"].rank(pct=True)

scorecard["fund_score"] = (
    0.30 * scorecard["rank_3yr_return"] +
    0.25 * scorecard["rank_sharpe"] +
    0.20 * scorecard["rank_alpha"] +
    0.15 * scorecard["rank_expense_inverse"] +
    0.10 * scorecard["rank_drawdown_inverse"]
) * 100

scorecard = scorecard.sort_values("fund_score", ascending=False)
scorecard.to_csv(DATA / "fund_scorecard.csv", index=False)

scorecard[[
    "amfi_code", "scheme_name", "fund_house", "cagr_3yr_pct",
    "sharpe_ratio", "alpha_pct", "beta", "max_drawdown_pct",
    "expense_ratio_pct", "fund_score"
]].head(10)
"""))

cells.append(md("## 7. Benchmark Comparison Chart and Tracking Error"))
cells.append(code("""
top5_codes = scorecard["amfi_code"].head(5).tolist()

latest_date = nav["date"].max()
start_date = latest_date - pd.DateOffset(years=3)

nav_top5 = nav[(nav["amfi_code"].isin(top5_codes)) & (nav["date"] >= start_date)].copy()
nav_top5["normalized_value"] = nav_top5.groupby("amfi_code")["nav"].transform(lambda x: x / x.iloc[0] * 100)

bench_subset = benchmark[
    benchmark["index_name"].str.contains("Nifty 50|Nifty 100", case=False, na=False)
].copy()
bench_subset = bench_subset[bench_subset["date"] >= start_date]
bench_subset["normalized_value"] = bench_subset.groupby("index_name")["close_value"].transform(lambda x: x / x.iloc[0] * 100)

plt.figure(figsize=(14,8))

for code, g in nav_top5.groupby("amfi_code"):
    fund_name = fund_master.loc[fund_master["amfi_code"] == code, "scheme_name"]
    label = fund_name.iloc[0][:35] if not fund_name.empty else str(code)
    plt.plot(g["date"], g["normalized_value"], label=label)

for idx, g in bench_subset.groupby("index_name"):
    plt.plot(g["date"], g["normalized_value"], linestyle="--", label=idx)

plt.title("Top 5 Funds vs Nifty 50 and Nifty 100 — 3 Year Normalized Performance")
plt.xlabel("Date")
plt.ylabel("Normalized Value (Start = 100)")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(REPORTS / "benchmark_comparison_top5.png", dpi=300, bbox_inches="tight")
plt.show()
"""))

cells.append(code("""
nifty50 = benchmark[
    benchmark["index_name"].str.contains("Nifty 50", case=False, na=False)
][["date", "benchmark_return"]].dropna()

tracking_rows = []
for code in top5_codes:
    fund_r = nav[(nav["amfi_code"] == code) & (nav["date"] >= start_date)][["date", "daily_return"]].dropna()
    merged = fund_r.merge(nifty50, on="date", how="inner").dropna()

    te = np.nan
    if len(merged) > 30:
        te = (merged["daily_return"] - merged["benchmark_return"]).std() * np.sqrt(252) * 100

    tracking_rows.append({
        "amfi_code": code,
        "tracking_error_pct": te
    })

tracking_error_report = pd.DataFrame(tracking_rows).merge(
    fund_master[["amfi_code", "scheme_name", "fund_house"]],
    on="amfi_code",
    how="left"
)

tracking_error_report.to_csv(DATA / "tracking_error_report.csv", index=False)
tracking_error_report
"""))

cells.append(md("""
## Key Performance Findings

1. Daily return distribution is centered close to zero, which is expected for mutual fund NAV movement.
2. CAGR helps compare long-term fund growth across 1-year, 3-year and 5-year periods.
3. Sharpe Ratio identifies funds with better risk-adjusted returns.
4. Sortino Ratio focuses on downside volatility and is useful for investor risk assessment.
5. Alpha shows whether a fund outperformed its benchmark after adjusting for market movement.
6. Beta measures sensitivity of fund returns to benchmark returns.
7. Maximum Drawdown highlights the worst downside period for each scheme.
8. The composite scorecard balances return, risk, alpha, cost and drawdown.
9. Top 5 funds are benchmarked against Nifty 50 and Nifty 100 using normalized performance.
10. Tracking error measures how differently each fund behaves compared to the benchmark.
"""))

nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "pygments_lexer": "ipython3"},
}

out_path = NOTEBOOKS / "04_performance_analytics.ipynb"
with open(out_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("Created:", out_path)
