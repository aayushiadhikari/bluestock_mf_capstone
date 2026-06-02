# Day 2 Data Dictionary
This data dictionary documents cleaned datasets, column data types, business definitions, and source references.

## fund_master
| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| amfi_code | str | Unique AMFI scheme code used to identify a mutual fund scheme. | 01_fund_master.csv |
| fund_house | str | Project dataset field used for mutual fund analytics. | 01_fund_master.csv |
| scheme_name | str | Project dataset field used for mutual fund analytics. | 01_fund_master.csv |
| category | str | Project dataset field used for mutual fund analytics. | 01_fund_master.csv |
| sub_category | str | Project dataset field used for mutual fund analytics. | 01_fund_master.csv |
| plan | str | Project dataset field used for mutual fund analytics. | 01_fund_master.csv |
| launch_date | datetime64[us] | Project dataset field used for mutual fund analytics. | 01_fund_master.csv |
| benchmark | str | Project dataset field used for mutual fund analytics. | 01_fund_master.csv |
| expense_ratio_pct | float64 | Annual fund expense ratio in percentage. | 01_fund_master.csv |
| exit_load_pct | float64 | Project dataset field used for mutual fund analytics. | 01_fund_master.csv |
| min_sip_amount | int64 | Project dataset field used for mutual fund analytics. | 01_fund_master.csv |
| min_lumpsum_amount | int64 | Project dataset field used for mutual fund analytics. | 01_fund_master.csv |
| fund_manager | str | Project dataset field used for mutual fund analytics. | 01_fund_master.csv |
| risk_category | str | Project dataset field used for mutual fund analytics. | 01_fund_master.csv |
| sebi_category_code | str | Project dataset field used for mutual fund analytics. | 01_fund_master.csv |

## nav_history
| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| date | datetime64[us] | Project dataset field used for mutual fund analytics. | 02_nav_history.csv |
| amfi_code | str | Unique AMFI scheme code used to identify a mutual fund scheme. | 02_nav_history.csv |
| nav | float64 | Net Asset Value per unit of a mutual fund scheme. | 02_nav_history.csv |
| daily_return | float64 | Daily percentage change in NAV, calculated as current NAV / previous NAV - 1. | 02_nav_history.csv |

## aum_by_fund_house
| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| date | datetime64[us] | Project dataset field used for mutual fund analytics. | 03_aum_by_fund_house.csv |
| fund_house | str | Project dataset field used for mutual fund analytics. | 03_aum_by_fund_house.csv |
| aum_lakh_crore | float64 | Project dataset field used for mutual fund analytics. | 03_aum_by_fund_house.csv |
| aum_crore | int64 | Assets under management in Indian rupees crore. | 03_aum_by_fund_house.csv |
| num_schemes | Int64 | Project dataset field used for mutual fund analytics. | 03_aum_by_fund_house.csv |

## monthly_sip_inflows
| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| month | datetime64[us] | Project dataset field used for mutual fund analytics. | 04_monthly_sip_inflows.csv |
| sip_inflow_crore | int64 | Monthly SIP inflow amount in Indian rupees crore. | 04_monthly_sip_inflows.csv |
| active_sip_accounts_crore | float64 | Project dataset field used for mutual fund analytics. | 04_monthly_sip_inflows.csv |
| new_sip_accounts_lakh | float64 | Project dataset field used for mutual fund analytics. | 04_monthly_sip_inflows.csv |
| sip_aum_lakh_crore | float64 | Project dataset field used for mutual fund analytics. | 04_monthly_sip_inflows.csv |
| yoy_growth_pct | float64 | Project dataset field used for mutual fund analytics. | 04_monthly_sip_inflows.csv |

## category_inflows
| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| month | datetime64[us] | Project dataset field used for mutual fund analytics. | 05_category_inflows.csv |
| category | str | Project dataset field used for mutual fund analytics. | 05_category_inflows.csv |
| net_inflow_crore | float64 | Project dataset field used for mutual fund analytics. | 05_category_inflows.csv |

## industry_folio_count
| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| month | datetime64[us] | Project dataset field used for mutual fund analytics. | 06_industry_folio_count.csv |
| total_folios_crore | float64 | Project dataset field used for mutual fund analytics. | 06_industry_folio_count.csv |
| equity_folios_crore | float64 | Project dataset field used for mutual fund analytics. | 06_industry_folio_count.csv |
| debt_folios_crore | float64 | Project dataset field used for mutual fund analytics. | 06_industry_folio_count.csv |
| hybrid_folios_crore | float64 | Project dataset field used for mutual fund analytics. | 06_industry_folio_count.csv |
| others_folios_crore | float64 | Project dataset field used for mutual fund analytics. | 06_industry_folio_count.csv |

## scheme_performance
| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| amfi_code | str | Unique AMFI scheme code used to identify a mutual fund scheme. | 07_scheme_performance.csv |
| scheme_name | str | Project dataset field used for mutual fund analytics. | 07_scheme_performance.csv |
| fund_house | str | Project dataset field used for mutual fund analytics. | 07_scheme_performance.csv |
| category | str | Project dataset field used for mutual fund analytics. | 07_scheme_performance.csv |
| plan | str | Project dataset field used for mutual fund analytics. | 07_scheme_performance.csv |
| return_1yr_pct | float64 | Project dataset field used for mutual fund analytics. | 07_scheme_performance.csv |
| return_3yr_pct | float64 | Project dataset field used for mutual fund analytics. | 07_scheme_performance.csv |
| return_5yr_pct | float64 | Project dataset field used for mutual fund analytics. | 07_scheme_performance.csv |
| benchmark_3yr_pct | float64 | Project dataset field used for mutual fund analytics. | 07_scheme_performance.csv |
| alpha | float64 | Project dataset field used for mutual fund analytics. | 07_scheme_performance.csv |
| beta | float64 | Sensitivity of fund returns to benchmark returns. | 07_scheme_performance.csv |
| sharpe_ratio | float64 | Risk-adjusted return measure. | 07_scheme_performance.csv |
| sortino_ratio | float64 | Project dataset field used for mutual fund analytics. | 07_scheme_performance.csv |
| std_dev_ann_pct | float64 | Project dataset field used for mutual fund analytics. | 07_scheme_performance.csv |
| max_drawdown_pct | float64 | Worst peak-to-trough decline in percentage. | 07_scheme_performance.csv |
| aum_crore | int64 | Assets under management in Indian rupees crore. | 07_scheme_performance.csv |
| expense_ratio_pct | float64 | Annual fund expense ratio in percentage. | 07_scheme_performance.csv |
| morningstar_rating | int64 | Project dataset field used for mutual fund analytics. | 07_scheme_performance.csv |
| risk_grade | str | Project dataset field used for mutual fund analytics. | 07_scheme_performance.csv |
| performance_anomaly_flag | bool | Project dataset field used for mutual fund analytics. | 07_scheme_performance.csv |

## investor_transactions
| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| transaction_id | int64 | Project dataset field used for mutual fund analytics. | 08_investor_transactions.csv |
| investor_id | str | Project dataset field used for mutual fund analytics. | 08_investor_transactions.csv |
| transaction_date | datetime64[us] | Project dataset field used for mutual fund analytics. | 08_investor_transactions.csv |
| amfi_code | str | Unique AMFI scheme code used to identify a mutual fund scheme. | 08_investor_transactions.csv |
| transaction_type | str | Investor transaction category: SIP, Lumpsum, or Redemption. | 08_investor_transactions.csv |
| amount_inr | int64 | Project dataset field used for mutual fund analytics. | 08_investor_transactions.csv |
| state | str | Project dataset field used for mutual fund analytics. | 08_investor_transactions.csv |
| city | str | Project dataset field used for mutual fund analytics. | 08_investor_transactions.csv |
| city_tier | str | Project dataset field used for mutual fund analytics. | 08_investor_transactions.csv |
| age_group | str | Project dataset field used for mutual fund analytics. | 08_investor_transactions.csv |
| gender | str | Project dataset field used for mutual fund analytics. | 08_investor_transactions.csv |
| annual_income_lakh | float64 | Project dataset field used for mutual fund analytics. | 08_investor_transactions.csv |
| payment_mode | str | Project dataset field used for mutual fund analytics. | 08_investor_transactions.csv |
| kyc_status | str | Project dataset field used for mutual fund analytics. | 08_investor_transactions.csv |

## portfolio_holdings
| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| amfi_code | str | Unique AMFI scheme code used to identify a mutual fund scheme. | 09_portfolio_holdings.csv |
| stock_symbol | str | Project dataset field used for mutual fund analytics. | 09_portfolio_holdings.csv |
| stock_name | str | Project dataset field used for mutual fund analytics. | 09_portfolio_holdings.csv |
| sector | str | Project dataset field used for mutual fund analytics. | 09_portfolio_holdings.csv |
| weight_pct | float64 | Project dataset field used for mutual fund analytics. | 09_portfolio_holdings.csv |
| market_value_cr | float64 | Project dataset field used for mutual fund analytics. | 09_portfolio_holdings.csv |
| current_price_inr | float64 | Project dataset field used for mutual fund analytics. | 09_portfolio_holdings.csv |
| portfolio_date | datetime64[us] | Project dataset field used for mutual fund analytics. | 09_portfolio_holdings.csv |

## benchmark_indices
| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| date | datetime64[us] | Project dataset field used for mutual fund analytics. | 10_benchmark_indices.csv |
| index_name | str | Project dataset field used for mutual fund analytics. | 10_benchmark_indices.csv |
| close_value | float64 | Project dataset field used for mutual fund analytics. | 10_benchmark_indices.csv |

## dim_date
| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| date | datetime64[us] | Project dataset field used for mutual fund analytics. | Generated during cleaning / ETL process |
| date_id | int64 | Project dataset field used for mutual fund analytics. | Generated during cleaning / ETL process |
| year | int32 | Project dataset field used for mutual fund analytics. | Generated during cleaning / ETL process |
| month | int32 | Project dataset field used for mutual fund analytics. | Generated during cleaning / ETL process |
| month_name | str | Project dataset field used for mutual fund analytics. | Generated during cleaning / ETL process |
| quarter | int32 | Project dataset field used for mutual fund analytics. | Generated during cleaning / ETL process |
| day_of_week | str | Project dataset field used for mutual fund analytics. | Generated during cleaning / ETL process |
| is_weekday | bool | Project dataset field used for mutual fund analytics. | Generated during cleaning / ETL process |
