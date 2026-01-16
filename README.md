# MRG Reporting HUB

## Project Overview

MRG Reporting HUB is a centralized analytics platform for Market Risk, Model Risk, and Risk Governance (MRG) reporting.

## Database Connection

### MAVRICK DB Configuration

- **Server**: `YKE0-P19SP1301.fg.rbc.com\IN01`
- **Database**: `DMAV_MAVRICK`
- **Driver**: ODBC Driver 17 for SQL Server
- **Authentication**: Windows Authentication (trusted_connection=yes)

### Quick Start

```python
from utils import create_mavrick_db_manager

# Connect to MAVRICK DB
db = create_mavrick_db_manager()

# Run query from string
df = db.run_query_from_string("SELECT * FROM MAV2.UIUMissingData")

# Run query from file
from pathlib import Path
df = db.run_query_from_file(Path("queries/uiu_missing_data.sql"))

# Save result to interim data
df.to_csv("interim_data/result.csv", index=False)

# Save to Excel using Excel Manager
from utils import ExcelManager

excel_mgr = ExcelManager()
excel_mgr.save_dataframe(df, "output_data/report.xlsx", sheet_name="Data")

# Save multiple DataFrames to one Excel file
dataframes = {
    "Summary": df_summary,
    "Detail": df_detail
}
excel_mgr.save_multiple_dataframes(dataframes, "output_data/report.xlsx")

# Close connection
db.close()
```

## Project Structure

```
MRG_ReportingHUB/
├── db_manager.py          # Database manager class
├── excel_manager.py       # Excel file manager class
├── queries/               # SQL query scripts
│   └── uiu_missing_data.sql
├── interim_data/          # Temporary/intermediate data files
├── output_data/           # Output Excel files and reports
├── example_usage.py       # DB manager usage examples
├── excel_example.py       # Excel manager usage examples
└── requirements.txt       # Python dependencies
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure ODBC Driver 17 for SQL Server is installed on your system.

## Usage Examples

See `example_usage.py` for comprehensive examples.

## Reports

### Running Reports

**Unified Runner** (Recommended):
```bash
# List all available reports
python run_report.py

# Run a specific report
python run_report.py cuso_ram
```

**Programmatic Usage**:
```python
from reports import run_report, list_reports

# List all reports
print(list_reports())

# Run a report
report_path = run_report("cuso_ram")
```

### Available Reports

#### CUSO RAM Report

Risk Appetite Measure report that processes model information from Model Governance team.

- **Query**: `queries/Risk Appetite Measure.sql`
- **Script**: `reports/cuso_ram_report.py`
- **Output**: `output_data/cuso_ram/`

**Usage**:
```python
from reports.cuso_ram_report import CUSORAMReport
report = CUSORAMReport()
report.run()
```

### Creating New Reports

1. Copy `reports/REPORT_TEMPLATE.py` to `reports/your_report_name_report.py`
2. Implement the abstract methods: `extract_data()`, `transform_data()`, `calculate_aggregations()`
3. Register the report in `reports/__init__.py`
4. Run using: `python run_report.py your_report_name`

## Notes

- All SQL queries should be stored in the `queries/` folder
- Interim data files (CSV, Parquet) should be saved in `interim_data/` folder
- Use Windows Authentication by default (no credentials needed)
- Reports are stored in `reports/` folder with their own subdirectories