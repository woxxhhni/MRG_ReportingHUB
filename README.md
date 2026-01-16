# MRG Reporting HUB

## Project Overview

MRG Reporting HUB is a centralized analytics platform for the Model Governance team's reporting purposes. The platform supports Excel report generation and will include Tableau report capabilities in the future.

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
├── utils/                  # Utility classes (centralized)
│   ├── __init__.py        # Unified export interface
│   ├── db_manager.py      # Database manager for MAVRICK DB
│   ├── excel_manager.py   # Excel file manager
│   └── date_utils.py      # Date utilities (MRGDate class)
├── reports/               # Report generators
│   ├── __init__.py        # Report registration
│   ├── base_report.py    # Abstract base class for all reports
│   ├── report_manager.py  # Centralized report manager
│   ├── cuso_ram_report.py # CUSO RAM report implementation
│   ├── REPORT_TEMPLATE.py # Template for creating new reports
│   └── MULTI_QUERY_EXAMPLE.py # Example for multi-query reports
├── queries/               # SQL query scripts
│   ├── Risk Appetite Measure (RAM) Models_New.sql
│   └── uiu_missing_data.sql
├── interim_data/          # Temporary/intermediate data files
│   └── {report_name}/     # Report-specific interim data
├── output_data/           # Output Excel files and reports
│   └── {report_name}/     # Report-specific output files
├── run_cuso_ram_report.py # Script to run CUSO RAM report
├── run_report.py          # Unified report runner
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

- **Query**: `queries/Risk Appetite Measure (RAM) Models_New.sql`
- **Script**: `reports/cuso_ram_report.py`
- **Output**: `output_data/cuso_ram/`
- **Interim Data**: `interim_data/cuso_ram/`

**Usage**:

**Command Line**:
```bash
# Run with default dates (today)
python run_cuso_ram_report.py

# Run with specific inventory date
python run_cuso_ram_report.py 2026-12-31

# Run with both inventory and compliance dates
python run_cuso_ram_report.py 2026-12-31 2026-12-31
```

**Direct Script Configuration**:
Edit `run_cuso_ram_report.py` and set:
```python
INVENTORY_DATE = '2026-12-31'   # Replaces (0=0) placeholder
COMPLIANCE_DATE = '2026-12-31'  # Replaces (10=10) placeholder
```

**Programmatic Usage**:
```python
from reports.cuso_ram_report import CUSORAMReport

# With dates
report = CUSORAMReport(
    inventory_date='2026-12-31',
    compliance_date='2026-12-31'
)
report.run()

# With default (today)
report = CUSORAMReport()
report.run()
```

**Query Placeholders**:
- `(0=0)` → Replaced with inventory date condition: `M.DateStamp = 'YYYY-MM-DD'`
- `(10=10)` → Replaced with compliance date value: `'YYYY-MM-DD'`
- `[DBName].[DBSchema]` → Replaced with `[DMAV_MAVRICK].[MAV2]`

### Creating New Reports

1. Copy `reports/REPORT_TEMPLATE.py` to `reports/your_report_name_report.py`
2. Implement the abstract methods:
   - `extract_data()` - Extract data from database (single or multiple queries)
   - `transform_data()` - Clean and transform raw data
   - `calculate_aggregations()` - Calculate aggregations and prepare data
   - `generate_report()` - Generate output in desired format (Excel, CSV, etc.)
3. Register the report in `reports/__init__.py`
4. Run using: `python run_report.py your_report_name`

**Note**: Each report can customize its output format. The `generate_report()` method is abstract, allowing each report to implement its own format (Excel, CSV, multiple files, etc.).

## Key Features

### Date Handling
- Uses `MRGDate` class for robust date operations
- Supports multiple date formats: 'YYYY-MM-DD', 'YYYYMMDD', 'YYYY/MM/DD'
- Handles dates from strings, datetime objects, or pandas Timestamps

### Query Placeholders
Reports can use custom placeholders in SQL queries:
- `(0=0)` - Inventory date (DateStamp condition)
- `(10=10)` - Compliance date (date value)
- `[DBName].[DBSchema]` - Database and schema name
- Custom placeholders can be added per report

### Report Architecture
- **BaseReport**: Abstract base class with common functionality
- **Modular Design**: Each report implements its own logic
- **Flexible Output**: Each report can customize output format
- **Multi-Query Support**: Reports can use multiple SQL queries
- **Interim Data**: Automatic saving of intermediate results

## Notes

- All SQL queries should be stored in the `queries/` folder
- Interim data files (CSV, Parquet) are automatically saved in `interim_data/{report_name}/` folder
- Output files are saved in `output_data/{report_name}/` folder
- Use Windows Authentication by default (no credentials needed)
- Reports are stored in `reports/` folder
- Utility classes are centralized in `utils/` folder