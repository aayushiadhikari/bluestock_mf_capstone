"""
Day 1 - Data Ingestion Script
Project: Mutual Fund Analytics

Tasks:
1. Load all CSV files from data/raw
2. Print shape, dtypes, and head
3. Note anomalies
4. Explore fund master
5. Validate AMFI scheme codes between fund_master and nav_history
6. Save summary reports
"""

from pathlib import Path
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
REPORTS_DIR = ROOT_DIR / "reports"


def load_csv_files(raw_dir: Path) -> dict:
    """Load all CSV files from raw directory."""
    csv_files = list(raw_dir.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in {raw_dir}")
        print("Please put the 10 provided CSV datasets inside data/raw/")
        return {}

    datasets = {}

    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)
            datasets[file_path.stem] = df

            print("\n" + "=" * 80)
            print(f"FILE: {file_path.name}")
            print("=" * 80)

            print("\nShape:")
            print(df.shape)

            print("\nDtypes:")
            print(df.dtypes)

            print("\nHead:")
            print(df.head())

            print("\nMissing Values:")
            print(df.isnull().sum())

            print("\nDuplicate Rows:")
            print(df.duplicated().sum())

        except Exception as e:
            print(f"Error loading {file_path.name}: {e}")

    return datasets


def create_anomaly_summary(datasets: dict) -> pd.DataFrame:
    """Create basic anomaly/data quality summary for each dataset."""
    summary_rows = []

    for name, df in datasets.items():
        summary_rows.append({
            "dataset": name,
            "rows": df.shape[0],
            "columns": df.shape[1],
            "missing_values_total": int(df.isnull().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "empty_columns": int((df.isnull().sum() == len(df)).sum()),
            "columns_list": ", ".join(df.columns.astype(str))
        })

    summary_df = pd.DataFrame(summary_rows)
    return summary_df


def find_dataset_by_name(datasets: dict, keyword: str):
    """Find dataset whose filename contains keyword."""
    keyword = keyword.lower()
    for name, df in datasets.items():
        if keyword in name.lower():
            return name, df
    return None, None


def explore_fund_master(datasets: dict):
    """Explore fund_master if present."""
    name, fund_master = find_dataset_by_name(datasets, "fund_master")

    if fund_master is None:
        print("\nfund_master CSV not found. Skipping fund master exploration.")
        return

    print("\n" + "#" * 80)
    print("FUND MASTER EXPLORATION")
    print("#" * 80)

    possible_columns = {
        "fund_house": ["fund_house", "amc", "fund house", "fundhouse"],
        "category": ["category", "scheme_category", "scheme category"],
        "sub_category": ["sub_category", "subcategory", "scheme_sub_category", "scheme sub category"],
        "risk_grade": ["risk_grade", "risk", "riskometer", "risk grade"]
    }

    lower_cols = {col.lower().strip(): col for col in fund_master.columns}

    for label, options in possible_columns.items():
        matched_col = None
        for option in options:
            if option in lower_cols:
                matched_col = lower_cols[option]
                break

        if matched_col:
            print(f"\nUnique values in {matched_col}:")
            print(fund_master[matched_col].dropna().unique())
        else:
            print(f"\nColumn for {label} not found.")


def validate_amfi_codes(datasets: dict):
    """Validate scheme codes in fund_master against nav_history."""
    fund_name, fund_master = find_dataset_by_name(datasets, "fund_master")
    nav_name, nav_history = find_dataset_by_name(datasets, "nav_history")

    if fund_master is None or nav_history is None:
        print("\nfund_master or nav_history not found. Skipping AMFI validation.")
        return None

    def find_code_col(df):
        for col in df.columns:
            if "code" in col.lower() or "scheme" in col.lower():
                return col
        return None

    fund_code_col = find_code_col(fund_master)
    nav_code_col = find_code_col(nav_history)

    if not fund_code_col or not nav_code_col:
        print("\nCould not identify scheme code columns.")
        print("Fund master columns:", list(fund_master.columns))
        print("NAV history columns:", list(nav_history.columns))
        return None

    fund_codes = set(fund_master[fund_code_col].dropna().astype(str).str.strip())
    nav_codes = set(nav_history[nav_code_col].dropna().astype(str).str.strip())

    missing_in_nav = sorted(fund_codes - nav_codes)
    extra_in_nav = sorted(nav_codes - fund_codes)

    validation_summary = {
        "fund_master_file": fund_name,
        "nav_history_file": nav_name,
        "fund_master_code_column": fund_code_col,
        "nav_history_code_column": nav_code_col,
        "total_fund_master_codes": len(fund_codes),
        "total_nav_history_codes": len(nav_codes),
        "codes_missing_in_nav_history": len(missing_in_nav),
        "extra_codes_in_nav_history": len(extra_in_nav),
        "missing_codes_sample": missing_in_nav[:20],
        "extra_codes_sample": extra_in_nav[:20]
    }

    print("\n" + "#" * 80)
    print("AMFI CODE VALIDATION SUMMARY")
    print("#" * 80)
    for key, value in validation_summary.items():
        print(f"{key}: {value}")

    return validation_summary


def main():
    REPORTS_DIR.mkdir(exist_ok=True)

    datasets = load_csv_files(RAW_DIR)

    if not datasets:
        return

    anomaly_summary = create_anomaly_summary(datasets)
    anomaly_report_path = REPORTS_DIR / "day1_data_quality_summary.csv"
    anomaly_summary.to_csv(anomaly_report_path, index=False)

    print("\n" + "#" * 80)
    print("DAY 1 DATA QUALITY SUMMARY")
    print("#" * 80)
    print(anomaly_summary)
    print(f"\nSaved summary to: {anomaly_report_path}")

    explore_fund_master(datasets)

    validation_summary = validate_amfi_codes(datasets)

    if validation_summary:
        validation_report_path = REPORTS_DIR / "amfi_code_validation_summary.json"
        pd.Series(validation_summary).to_json(validation_report_path, indent=4)
        print(f"\nSaved AMFI validation summary to: {validation_report_path}")


if __name__ == "__main__":
    main()
