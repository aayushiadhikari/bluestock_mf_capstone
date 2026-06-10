# Mutual Fund Analytics Capstone Project

## Project Overview

This project analyzes the Indian Mutual Fund industry using data engineering, exploratory data analysis, fund performance analytics, advanced risk metrics, and interactive dashboards.

The project covers the complete analytics lifecycle:

* Data Ingestion
* Data Cleaning and Validation
* SQLite Data Warehouse
* Exploratory Data Analysis (EDA)
* Fund Performance Analytics
* Advanced Risk Analytics
* Interactive Power BI Dashboard
* Final Reporting and Recommendations

---

## Project Objectives

* Analyze mutual fund industry trends from 2022–2025
* Evaluate fund performance using CAGR, Sharpe Ratio, Sortino Ratio, Alpha, Beta, and Maximum Drawdown
* Perform investor behavior analysis and SIP trend analysis
* Measure downside risk using VaR and CVaR
* Assess portfolio concentration using Sector HHI
* Build an interactive dashboard for business users

---

## Project Structure

```text
data/
│
├── raw/
├── processed/
├── db/

notebooks/
│
├── 03_eda_analysis.ipynb
├── 04_performance_analytics.ipynb
├── 06_advanced_analytics.ipynb

scripts/
│
├── day2_clean_load_sqlite.py
├── day4_performance_analytics.py
├── recommender.py

reports/
│
├── Dashboard.pdf
├── rolling_sharpe_chart.png
├── sector_hhi_chart.png

dashboard/
│
└── Power BI assets

bluestock_mf_dashboard.pbix
README.md
requirements.txt
```

---

## Day-wise Deliverables

### Day 1

* Project Setup
* Data Ingestion
* Folder Structure

### Day 2

* Data Validation
* Data Cleaning
* SQLite Integration

### Day 3

* Exploratory Data Analysis
* AUM Analysis
* SIP Analysis
* Investor Analysis

### Day 4

* CAGR Analysis
* Sharpe Ratio
* Sortino Ratio
* Alpha/Beta Analysis
* Fund Scorecard

### Day 5

* Power BI Dashboard
* Industry Overview
* Fund Performance Dashboard
* Investor Analytics Dashboard
* SIP Trends Dashboard

### Day 6

* Historical VaR
* Conditional VaR
* Rolling Sharpe Ratio
* Cohort Analysis
* SIP Continuity Analysis
* Sector HHI Analysis
* Fund Recommendation Engine

### Day 7

* Final Report
* Presentation Deck
* Documentation
* GitHub Release

---

## Key Performance Metrics

* CAGR
* Sharpe Ratio
* Sortino Ratio
* Alpha
* Beta
* Maximum Drawdown
* Historical VaR
* Conditional VaR
* Sector HHI

---

## Dashboard Pages

### Page 1: Industry Overview

* Total AUM
* SIP Inflows
* Folio Count
* AUM by Fund House

### Page 2: Fund Performance

* Risk vs Return Analysis
* Fund Scorecard
* Benchmark Comparison

### Page 3: Investor Analytics

* State-wise Transactions
* SIP vs Lumpsum Analysis
* Age Group Analysis

### Page 4: SIP & Market Trends

* SIP Growth Trend
* Category Inflow Heatmap
* SIP Growth KPIs

---

## Technologies Used

* Python
* Pandas
* NumPy
* Matplotlib
* SQLite
* Jupyter Notebook
* Power BI
* Git
* GitHub

---

## Results

The project successfully identified:

* Top-performing mutual funds using risk-adjusted metrics.
* Investor participation trends across demographics.
* SIP growth patterns from 2022–2025.
* Portfolio concentration risk using HHI.
* High-risk funds using VaR and CVaR analytics.

---

## Author

Aayushi Adhikari

Mutual Fund Analytics Capstone Project
Bluestock Fintech
