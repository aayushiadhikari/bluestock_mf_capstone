# Capstone Project I - Mutual Fund Analytics

## Day 1: Project Setup + Data Ingestion

### Folder Structure
- data/raw: original CSV files and API raw data
- data/processed: cleaned/processed data
- notebooks: Jupyter notebooks
- sql: SQL queries
- dashboard: dashboard files
- reports: project reports
- src: Python scripts

### Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

For Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Day 1 scripts

Put all provided 10 CSV files inside:

```text
data/raw/
```

Then run:

```bash
python src/data_ingestion.py
python src/live_nav_fetch.py
```

### Git Commit

```bash
git add .
git commit -m "Day 1: Data ingestion complete"
git push origin main
```
