"""
Day 1 - Live NAV Fetch Script
Project: Mutual Fund Analytics

Tasks:
1. Fetch live NAV from mfapi.in
2. Save raw API data as CSV
3. Fetch NAV for 5 key schemes
"""

from pathlib import Path
import requests
import pandas as pd
from datetime import datetime


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"


SCHEMES = {
    "HDFC_Top_100_Direct": "125497",
    "SBI_Bluechip": "119551",
    "ICICI_Bluechip": "120503",
    "Nippon_Large_Cap": "118632",
    "Axis_Bluechip": "119092",
    "Kotak_Bluechip": "120841"
}


def fetch_scheme_nav(scheme_code: str) -> dict:
    """Fetch NAV JSON from mfapi.in."""
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def parse_nav_json(json_data: dict, scheme_name: str, scheme_code: str) -> pd.DataFrame:
    """Convert mfapi JSON to DataFrame."""
    meta = json_data.get("meta", {})
    nav_data = json_data.get("data", [])

    df = pd.DataFrame(nav_data)

    if df.empty:
        return df

    df["scheme_name_local"] = scheme_name
    df["scheme_code_requested"] = scheme_code
    df["fund_house"] = meta.get("fund_house")
    df["scheme_type"] = meta.get("scheme_type")
    df["scheme_category"] = meta.get("scheme_category")
    df["scheme_code_api"] = meta.get("scheme_code")
    df["scheme_name_api"] = meta.get("scheme_name")
    df["fetched_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Standardize date and nav
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    if "nav" in df.columns:
        df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    return df


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    all_nav_data = []

    for scheme_name, scheme_code in SCHEMES.items():
        print(f"Fetching NAV for {scheme_name} ({scheme_code})...")

        try:
            json_data = fetch_scheme_nav(scheme_code)
            df = parse_nav_json(json_data, scheme_name, scheme_code)

            if df.empty:
                print(f"No NAV data found for {scheme_name}")
                continue

            output_file = RAW_DIR / f"live_nav_{scheme_name}_{scheme_code}.csv"
            df.to_csv(output_file, index=False)

            print(f"Saved: {output_file}")
            print(df.head())

            all_nav_data.append(df)

        except requests.exceptions.RequestException as e:
            print(f"API error for {scheme_name}: {e}")

        except Exception as e:
            print(f"Unexpected error for {scheme_name}: {e}")

    if all_nav_data:
        combined_df = pd.concat(all_nav_data, ignore_index=True)
        combined_output = RAW_DIR / "live_nav_all_key_schemes.csv"
        combined_df.to_csv(combined_output, index=False)
        print(f"\nCombined NAV data saved to: {combined_output}")
        print("Combined shape:", combined_df.shape)


if __name__ == "__main__":
    main()
