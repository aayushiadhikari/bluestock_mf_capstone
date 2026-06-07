
import pandas as pd
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "processed"

scorecard = pd.read_csv(DATA / "fund_scorecard.csv")

def recommend_funds(risk_appetite: str, top_n: int = 3):
    risk_appetite = risk_appetite.lower().strip()

    if risk_appetite == "low":
        filtered = scorecard[scorecard["category"].str.contains("Debt", case=False, na=False)]
    elif risk_appetite == "moderate":
        filtered = scorecard[
            scorecard["sub_category"].str.contains("Hybrid|Large", case=False, na=False)
        ]
    else:
        filtered = scorecard[scorecard["category"].str.contains("Equity", case=False, na=False)]

    if filtered.empty:
        filtered = scorecard.copy()

    result = filtered.sort_values("sharpe_ratio", ascending=False).head(top_n)

    return result[[
        "scheme_name",
        "fund_house",
        "category",
        "sub_category",
        "sharpe_ratio",
        "cagr_3yr_pct",
        "fund_score"
    ]]

if __name__ == "__main__":
    for risk in ["Low", "Moderate", "High"]:
        print("\nRisk Appetite:", risk)
        print(recommend_funds(risk))
