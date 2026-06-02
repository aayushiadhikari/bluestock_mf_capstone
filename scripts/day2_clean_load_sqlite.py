"""
DAY 2 — Data Cleaning + SQLite Database Design
Project: Bluestock Mutual Fund Analytics Capstone

This script:
1. Cleans all 10 raw CSV datasets from data/raw/
2. Saves cleaned CSVs to data/processed/
3. Creates schema.sql and queries.sql
4. Creates SQLite database: data/db/bluestock_mf.db
5. Loads cleaned datasets into SQLite
6. Verifies row counts
7. Generates data_dictionary.md

Run from project root:
    python scripts/day2_clean_load_sqlite.py
"""

from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
from sqlalchemy import create_engine


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
DB_DIR = ROOT_DIR / "data" / "db"
SQL_DIR = ROOT_DIR / "sql"
REPORTS_DIR = ROOT_DIR / "reports"

DB_PATH = DB_DIR / "bluestock_mf.db"
SCHEMA_PATH = SQL_DIR / "schema.sql"
QUERIES_PATH = SQL_DIR / "queries.sql"
DATA_DICT_PATH = REPORTS_DIR / "data_dictionary.md"
ROW_COUNT_PATH = REPORTS_DIR / "day2_sqlite_row_counts.csv"


REQUIRED_FILES = {
    "fund_master": "01_fund_master.csv",
    "nav_history": "02_nav_history.csv",
    "aum_by_fund_house": "03_aum_by_fund_house.csv",
    "monthly_sip_inflows": "04_monthly_sip_inflows.csv",
    "category_inflows": "05_category_inflows.csv",
    "industry_folio_count": "06_industry_folio_count.csv",
    "scheme_performance": "07_scheme_performance.csv",
    "investor_transactions": "08_investor_transactions.csv",
    "portfolio_holdings": "09_portfolio_holdings.csv",
    "benchmark_indices": "10_benchmark_indices.csv",
}


def ensure_dirs() -> None:
    for folder in [PROCESSED_DIR, DB_DIR, SQL_DIR, REPORTS_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def load_raw_data() -> dict:
    data = {}
    missing_files = []

    for name, filename in REQUIRED_FILES.items():
        path = RAW_DIR / filename
        if not path.exists():
            missing_files.append(filename)
            continue

        data[name] = pd.read_csv(path)

    if missing_files:
        raise FileNotFoundError(
            "Missing required raw files in data/raw/: " + ", ".join(missing_files)
        )

    return data


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )
    return df


def clean_fund_master(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)
    df = df.drop_duplicates(subset=["amfi_code"]).copy()

    df["amfi_code"] = df["amfi_code"].astype(str).str.strip()
    df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce")
    df["expense_ratio_pct"] = pd.to_numeric(df["expense_ratio_pct"], errors="coerce")
    df["exit_load_pct"] = pd.to_numeric(df["exit_load_pct"], errors="coerce")

    text_cols = [
        "fund_house", "scheme_name", "category", "sub_category", "plan",
        "benchmark", "fund_manager", "risk_category", "sebi_category_code"
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


def clean_nav_history(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)

    df["amfi_code"] = df["amfi_code"].astype(str).str.strip()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    df = df.dropna(subset=["amfi_code", "date", "nav"])
    df = df[df["nav"] > 0]
    df = df.drop_duplicates(subset=["amfi_code", "date"])
    df = df.sort_values(["amfi_code", "date"])

    # Reindex to business days per scheme and forward fill missing NAV.
    cleaned_parts = []
    for code, group in df.groupby("amfi_code"):
        group = group.set_index("date").sort_index()
        full_dates = pd.bdate_range(group.index.min(), group.index.max())
        group = group.reindex(full_dates)
        group["amfi_code"] = code
        group["nav"] = group["nav"].ffill()
        group = group.dropna(subset=["nav"])
        group = group.reset_index().rename(columns={"index": "date"})
        cleaned_parts.append(group)

    cleaned = pd.concat(cleaned_parts, ignore_index=True)
    cleaned["daily_return"] = cleaned.groupby("amfi_code")["nav"].pct_change()
    cleaned["daily_return"] = cleaned["daily_return"].fillna(0)
    return cleaned


def clean_aum(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["aum_lakh_crore"] = pd.to_numeric(df["aum_lakh_crore"], errors="coerce")
    df["aum_crore"] = pd.to_numeric(df["aum_crore"], errors="coerce")
    df["num_schemes"] = pd.to_numeric(df["num_schemes"], errors="coerce").astype("Int64")
    df["fund_house"] = df["fund_house"].astype(str).str.strip()
    df = df.dropna(subset=["date", "fund_house", "aum_crore"])
    df = df.drop_duplicates(subset=["date", "fund_house"])
    return df.sort_values(["fund_house", "date"])


def clean_monthly_sip(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)
    df["month"] = pd.to_datetime(df["month"], errors="coerce").dt.to_period("M").dt.to_timestamp()
    numeric_cols = [c for c in df.columns if c != "month"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["month"])
    df = df.drop_duplicates(subset=["month"])
    return df.sort_values("month")


def clean_category_inflows(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)
    df["month"] = pd.to_datetime(df["month"], errors="coerce").dt.to_period("M").dt.to_timestamp()
    df["category"] = df["category"].astype(str).str.strip()
    df["net_inflow_crore"] = pd.to_numeric(df["net_inflow_crore"], errors="coerce")
    df = df.dropna(subset=["month", "category", "net_inflow_crore"])
    df = df.drop_duplicates(subset=["month", "category"])
    return df.sort_values(["category", "month"])


def clean_folio_count(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)
    df["month"] = pd.to_datetime(df["month"], errors="coerce").dt.to_period("M").dt.to_timestamp()
    for col in df.columns:
        if col != "month":
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["month"])
    df = df.drop_duplicates(subset=["month"])
    return df.sort_values("month")


def clean_scheme_performance(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)
    df["amfi_code"] = df["amfi_code"].astype(str).str.strip()

    numeric_cols = [
        "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
        "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio",
        "sortino_ratio", "std_dev_ann_pct", "max_drawdown_pct",
        "aum_crore", "expense_ratio_pct", "morningstar_rating"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["performance_anomaly_flag"] = False
    anomaly_conditions = []

    if "expense_ratio_pct" in df.columns:
        anomaly_conditions.append(~df["expense_ratio_pct"].between(0.1, 2.5))

    for col in ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct"]:
        if col in df.columns:
            anomaly_conditions.append(df[col].abs() > 100)

    if anomaly_conditions:
        combined = anomaly_conditions[0]
        for condition in anomaly_conditions[1:]:
            combined = combined | condition
        df["performance_anomaly_flag"] = combined.fillna(False)

    df = df.drop_duplicates(subset=["amfi_code"])
    return df


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)

    df["investor_id"] = df["investor_id"].astype(str).str.strip()
    df["amfi_code"] = df["amfi_code"].astype(str).str.strip()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")

    transaction_map = {
        "sip": "SIP",
        "lumpsum": "Lumpsum",
        "lump sum": "Lumpsum",
        "redemption": "Redemption",
        "redeem": "Redemption"
    }
    df["transaction_type"] = (
        df["transaction_type"].astype(str).str.strip().str.lower().map(transaction_map)
    )

    allowed_kyc = {"Verified", "Pending", "Rejected"}
    df["kyc_status"] = df["kyc_status"].astype(str).str.strip().str.title()
    df.loc[~df["kyc_status"].isin(allowed_kyc), "kyc_status"] = "Pending"

    text_cols = ["state", "city", "city_tier", "age_group", "gender", "payment_mode"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df = df.dropna(subset=["investor_id", "transaction_date", "amfi_code", "transaction_type", "amount_inr"])
    df = df[df["amount_inr"] > 0]
    df = df.drop_duplicates()
    df.insert(0, "transaction_id", range(1, len(df) + 1))
    return df.sort_values(["transaction_date", "investor_id"])


def clean_portfolio_holdings(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)
    df["amfi_code"] = df["amfi_code"].astype(str).str.strip()
    df["portfolio_date"] = pd.to_datetime(df["portfolio_date"], errors="coerce")
    for col in ["weight_pct", "market_value_cr", "current_price_inr"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["amfi_code", "stock_symbol", "portfolio_date"])
    df = df[df["weight_pct"] >= 0]
    df = df.drop_duplicates(subset=["amfi_code", "stock_symbol", "portfolio_date"])
    return df


def clean_benchmark_indices(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["index_name"] = df["index_name"].astype(str).str.strip()
    df["close_value"] = pd.to_numeric(df["close_value"], errors="coerce")
    df = df.dropna(subset=["date", "index_name", "close_value"])
    df = df[df["close_value"] > 0]
    df = df.drop_duplicates(subset=["date", "index_name"])
    return df.sort_values(["index_name", "date"])


def create_dim_date(*date_series_list: pd.Series) -> pd.DataFrame:
    all_dates = pd.concat(date_series_list, ignore_index=True).dropna()
    min_date = all_dates.min()
    max_date = all_dates.max()

    dates = pd.date_range(min_date, max_date, freq="D")
    dim_date = pd.DataFrame({"date": dates})
    dim_date["date_id"] = dim_date["date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["year"] = dim_date["date"].dt.year
    dim_date["month"] = dim_date["date"].dt.month
    dim_date["month_name"] = dim_date["date"].dt.month_name()
    dim_date["quarter"] = dim_date["date"].dt.quarter
    dim_date["day_of_week"] = dim_date["date"].dt.day_name()
    dim_date["is_weekday"] = dim_date["date"].dt.weekday < 5
    return dim_date


def write_schema_sql() -> None:
    schema_sql = """
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS fact_sip_industry;
DROP TABLE IF EXISTS fact_category_inflows;
DROP TABLE IF EXISTS fact_folio_count;
DROP TABLE IF EXISTS fact_portfolio;
DROP TABLE IF EXISTS fact_benchmark_indices;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_fund;

CREATE TABLE dim_fund (
    amfi_code TEXT PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT,
    sub_category TEXT,
    plan TEXT,
    launch_date DATE,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    year INTEGER,
    month INTEGER,
    month_name TEXT,
    quarter INTEGER,
    day_of_week TEXT,
    is_weekday BOOLEAN
);

CREATE TABLE fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT NOT NULL,
    date DATE NOT NULL,
    nav REAL NOT NULL,
    daily_return REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY,
    investor_id TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    amfi_code TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    amount_inr REAL NOT NULL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_performance (
    amfi_code TEXT PRIMARY KEY,
    scheme_name TEXT,
    fund_house TEXT,
    category TEXT,
    plan TEXT,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL,
    morningstar_rating INTEGER,
    risk_grade TEXT,
    performance_anomaly_flag BOOLEAN,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    fund_house TEXT NOT NULL,
    aum_lakh_crore REAL,
    aum_crore REAL,
    num_schemes INTEGER
);

CREATE TABLE fact_sip_industry (
    sip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month DATE NOT NULL,
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);

CREATE TABLE fact_category_inflows (
    category_inflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month DATE NOT NULL,
    category TEXT NOT NULL,
    net_inflow_crore REAL
);

CREATE TABLE fact_folio_count (
    folio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month DATE NOT NULL,
    total_folios_crore REAL,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);

CREATE TABLE fact_portfolio (
    portfolio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT NOT NULL,
    stock_symbol TEXT,
    stock_name TEXT,
    sector TEXT,
    weight_pct REAL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date DATE,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_benchmark_indices (
    benchmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    index_name TEXT NOT NULL,
    close_value REAL
);

CREATE INDEX idx_fact_nav_amfi_date ON fact_nav(amfi_code, date);
CREATE INDEX idx_fact_transactions_amfi_date ON fact_transactions(amfi_code, transaction_date);
CREATE INDEX idx_fact_aum_fund_house_date ON fact_aum(fund_house, date);
CREATE INDEX idx_benchmark_date_index ON fact_benchmark_indices(date, index_name);
"""
    SCHEMA_PATH.write_text(schema_sql.strip(), encoding="utf-8")


def write_queries_sql() -> None:
    queries_sql = """
-- DAY 2 — 10 Analytical SQL Queries

-- 1. Top 5 fund houses by latest AUM
SELECT fund_house, date, aum_crore
FROM fact_aum
WHERE date = (SELECT MAX(date) FROM fact_aum)
ORDER BY aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month
SELECT 
    amfi_code,
    strftime('%Y-%m', date) AS month,
    ROUND(AVG(nav), 4) AS avg_nav
FROM fact_nav
GROUP BY amfi_code, strftime('%Y-%m', date)
ORDER BY amfi_code, month;

-- 3. SIP inflow YoY growth
SELECT 
    month,
    sip_inflow_crore,
    yoy_growth_pct
FROM fact_sip_industry
ORDER BY month;

-- 4. Transactions by state
SELECT 
    state,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- 5. Funds with expense ratio below 1%
SELECT 
    amfi_code,
    scheme_name,
    fund_house,
    category,
    plan,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1
ORDER BY expense_ratio_pct ASC;

-- 6. Top 10 funds by 3-year return
SELECT 
    amfi_code,
    scheme_name,
    fund_house,
    return_3yr_pct,
    sharpe_ratio
FROM fact_performance
ORDER BY return_3yr_pct DESC
LIMIT 10;

-- 7. Fund count by risk category
SELECT 
    risk_category,
    COUNT(*) AS fund_count
FROM dim_fund
GROUP BY risk_category
ORDER BY fund_count DESC;

-- 8. Transaction type mix
SELECT 
    transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM fact_transactions
GROUP BY transaction_type
ORDER BY transaction_count DESC;

-- 9. Category-wise net inflows
SELECT 
    category,
    ROUND(SUM(net_inflow_crore), 2) AS total_net_inflow_crore
FROM fact_category_inflows
GROUP BY category
ORDER BY total_net_inflow_crore DESC;

-- 10. Benchmark latest close values
SELECT 
    index_name,
    date,
    close_value
FROM fact_benchmark_indices
WHERE date = (SELECT MAX(date) FROM fact_benchmark_indices)
ORDER BY index_name;
"""
    QUERIES_PATH.write_text(queries_sql.strip(), encoding="utf-8")


def write_data_dictionary(cleaned_data: dict) -> None:
    business_definitions = {
        "amfi_code": "Unique AMFI scheme code used to identify a mutual fund scheme.",
        "nav": "Net Asset Value per unit of a mutual fund scheme.",
        "daily_return": "Daily percentage change in NAV, calculated as current NAV / previous NAV - 1.",
        "aum_crore": "Assets under management in Indian rupees crore.",
        "sip_inflow_crore": "Monthly SIP inflow amount in Indian rupees crore.",
        "transaction_type": "Investor transaction category: SIP, Lumpsum, or Redemption.",
        "expense_ratio_pct": "Annual fund expense ratio in percentage.",
        "sharpe_ratio": "Risk-adjusted return measure.",
        "beta": "Sensitivity of fund returns to benchmark returns.",
        "max_drawdown_pct": "Worst peak-to-trough decline in percentage."
    }

    lines = ["# Day 2 Data Dictionary\n"]
    lines.append("This data dictionary documents cleaned datasets, column data types, business definitions, and source references.\n")

    for name, df in cleaned_data.items():
        lines.append(f"\n## {name}\n")
        lines.append("| Column | Data Type | Business Definition | Source |\n")
        lines.append("|---|---|---|---|\n")

        for col in df.columns:
            dtype = str(df[col].dtype)
            definition = business_definitions.get(col, "Project dataset field used for mutual fund analytics.")
            source = REQUIRED_FILES.get(name, "Generated during cleaning / ETL process")
            lines.append(f"| {col} | {dtype} | {definition} | {source} |\n")

    DATA_DICT_PATH.write_text("".join(lines), encoding="utf-8")


def convert_dates_to_string(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%Y-%m-%d")
    return df


def save_cleaned_csvs(cleaned_data: dict) -> None:
    for name, df in cleaned_data.items():
        output_path = PROCESSED_DIR / f"clean_{name}.csv"
        convert_dates_to_string(df).to_csv(output_path, index=False)
        print(f"Saved cleaned CSV: {output_path}")


def load_to_sqlite(cleaned_data: dict) -> pd.DataFrame:
    if DB_PATH.exists():
        DB_PATH.unlink()

    write_schema_sql()
    write_queries_sql()

    connection = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
        connection.executescript(file.read())
    connection.close()

    engine = create_engine(f"sqlite:///{DB_PATH}")

    table_mapping = {
        "fund_master": "dim_fund",
        "dim_date": "dim_date",
        "nav_history": "fact_nav",
        "investor_transactions": "fact_transactions",
        "scheme_performance": "fact_performance",
        "aum_by_fund_house": "fact_aum",
        "monthly_sip_inflows": "fact_sip_industry",
        "category_inflows": "fact_category_inflows",
        "industry_folio_count": "fact_folio_count",
        "portfolio_holdings": "fact_portfolio",
        "benchmark_indices": "fact_benchmark_indices",
    }

    row_counts = []

    for dataset_name, table_name in table_mapping.items():
        df = cleaned_data[dataset_name]
        df_to_load = convert_dates_to_string(df)

        # Remove auto-increment ID columns if not present in dataframe schema need.
        df_to_load.to_sql(table_name, engine, if_exists="append", index=False)

        with engine.connect() as conn:
            db_count = pd.read_sql(f"SELECT COUNT(*) AS count FROM {table_name}", conn)["count"].iloc[0]

        row_counts.append({
            "dataset": dataset_name,
            "sqlite_table": table_name,
            "cleaned_csv_rows": len(df),
            "sqlite_rows": int(db_count),
            "status": "MATCH" if len(df) == int(db_count) else "MISMATCH"
        })

        print(f"Loaded {dataset_name} -> {table_name}: {len(df)} rows")

    row_count_df = pd.DataFrame(row_counts)
    row_count_df.to_csv(ROW_COUNT_PATH, index=False)
    return row_count_df


def main() -> None:
    ensure_dirs()

    print("Loading raw datasets...")
    raw = load_raw_data()

    print("Cleaning datasets...")
    cleaned = {
        "fund_master": clean_fund_master(raw["fund_master"]),
        "nav_history": clean_nav_history(raw["nav_history"]),
        "aum_by_fund_house": clean_aum(raw["aum_by_fund_house"]),
        "monthly_sip_inflows": clean_monthly_sip(raw["monthly_sip_inflows"]),
        "category_inflows": clean_category_inflows(raw["category_inflows"]),
        "industry_folio_count": clean_folio_count(raw["industry_folio_count"]),
        "scheme_performance": clean_scheme_performance(raw["scheme_performance"]),
        "investor_transactions": clean_transactions(raw["investor_transactions"]),
        "portfolio_holdings": clean_portfolio_holdings(raw["portfolio_holdings"]),
        "benchmark_indices": clean_benchmark_indices(raw["benchmark_indices"]),
    }

    cleaned["dim_date"] = create_dim_date(
        cleaned["nav_history"]["date"],
        cleaned["investor_transactions"]["transaction_date"],
        cleaned["aum_by_fund_house"]["date"],
        cleaned["monthly_sip_inflows"]["month"],
        cleaned["category_inflows"]["month"],
        cleaned["industry_folio_count"]["month"],
        cleaned["benchmark_indices"]["date"],
    )

    print("\nSaving cleaned CSV files...")
    # Save only the 10 cleaned source CSVs in data/processed as required.
    cleaned_source_data = {k: v for k, v in cleaned.items() if k != "dim_date"}
    save_cleaned_csvs(cleaned_source_data)

    print("\nWriting schema.sql, queries.sql, and data dictionary...")
    write_schema_sql()
    write_queries_sql()
    write_data_dictionary(cleaned)

    print("\nLoading cleaned data into SQLite...")
    row_count_df = load_to_sqlite(cleaned)

    print("\nSQLite row count verification:")
    print(row_count_df)

    print("\nDAY 2 COMPLETED SUCCESSFULLY")
    print(f"SQLite database created at: {DB_PATH}")
    print(f"Schema file: {SCHEMA_PATH}")
    print(f"Queries file: {QUERIES_PATH}")
    print(f"Data dictionary: {DATA_DICT_PATH}")
    print(f"Row count report: {ROW_COUNT_PATH}")


if __name__ == "__main__":
    main()
