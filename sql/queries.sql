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