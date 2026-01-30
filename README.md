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
│   ├── date_utils.py      # Date utilities (MRGDate class)
│   ├── config_manager.py  # Configuration file manager
│   └── filter_utils.py    # DataFrame filter utilities
├── config/                 # Report configuration files (JSON)
│   ├── {report_name}_default.json  # Default configuration templates
│   ├── {report_name}_config.json   # Saved configurations
│   ├── temp/                        # Temporary configurations
│   ├── README.md                    # Configuration documentation
│   └── NAMING_CONVENTION.md         # Config file naming rules
├── reports/               # Report generators
│   ├── __init__.py        # Report registration
│   ├── base_report.py     # Abstract base class for all reports
│   ├── report_manager.py  # Centralized report manager
│   ├── cuso_ram_report.py # CUSO RAM report implementation
│   ├── placeholder_reports.py  # Placeholder report classes
│   └── cuso_ram/          # CUSO RAM report documentation
│       └── README.md
├── queries/               # SQL query scripts
│   ├── Risk Appetite Measure.sql
│   └── uiu_missing_data.sql
├── templates/              # Excel report templates (per-report)
│   ├── cuso_ram_report_template.xlsx
│   ├── compliance_report_template.xlsx
│   └── ...                # See templates/README.md
├── interim_data/          # Temporary/intermediate data files
│   └── {report_name}/     # Report-specific interim data
├── output_data/           # Output Excel files and reports
│   └── {report_name}/     # Report-specific output files
├── examples/              # Example scripts (run from project root)
│   ├── example_usage.py   # DB manager usage
│   ├── excel_example.py   # Excel manager usage
│   ├── date_example.py    # MRGDate and date utilities
│   └── config_example.py  # Sample DB config; copy to config.py
├── docs/                   # Project documentation
│   ├── PROGRESS_UPDATE.md
│   └── STATUS_SUMMARY.md
├── scripts/                # One-off and setup scripts
│   └── create_cuso_ram_template.py
├── tests/                  # Tests
│   └── test_imports.py
├── run_cuso_ram_report.py  # Script to run CUSO RAM report
├── run_report.py           # Unified report runner
├── report_config_ui.py     # Streamlit UI for report configuration
├── pyproject.toml          # Project metadata and entry points
└── requirements.txt        # Python dependencies
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure ODBC Driver 17 for SQL Server is installed on your system.

3. (Optional) For report configuration UI, ensure Streamlit is installed:
```bash
pip install streamlit>=1.28.0
```

## Usage Examples

Run from the project root:

```bash
python examples/example_usage.py    # DB manager examples
python examples/excel_example.py    # Excel manager examples
python examples/date_example.py     # MRGDate and date utilities
```

See `examples/README.md` for details.

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

- **Config**: `excel_template_path`, `query` or `tab_queries` (sheet → query path) in config JSON
- **Script**: `reports/cuso_ram_report.py`
- **Output**: `output_data/cuso_ram/`
- **Interim Data**: `interim_data/cuso_ram/`
- **Template**: Optional Excel template in `templates/` (e.g. `cuso_ram_report_template.xlsx`)

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

**Using Configuration Files**:
Reports support a three-tier configuration system (saved → default → temp):
```python
from reports.cuso_ram_report import CUSORAMReport

# Default loading: saved → default → generate
report = CUSORAMReport()
report.run()

# Initialize from a specific config file (reads template path, query, tab_queries, filters)
report = CUSORAMReport.from_config_file("config/cuso_ram_report_config.json")
report.run()

# Override dates when loading from file
report = CUSORAMReport.from_config_file(
    "config/cuso_ram_report_config.json",
    inventory_date="2026-06-30",
    compliance_date="2026-06-30"
)
report.run()

# Force use default configuration
report = CUSORAMReport(config_file="default")

# Use temporary configuration
report = CUSORAMReport(config_file="temp:20260129_143022")

# Use specific config file path
report = CUSORAMReport(config_file="config/custom_config.json")
```

### Creating New Reports

1. Use `reports/base_report.py` as reference; create `reports/your_report_name_report.py`.
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

### Report Configuration UI

A Streamlit-based web interface for configuring report parameters with three-tier configuration system.

**Launch Configuration UI**:
```bash
streamlit run report_config_ui.py
```

**Features**:
- **Report Selection**: Choose from available reports in the sidebar
- **Report Description**: Editable description field at the top (stored in config)
- **Report Template**: Select Excel template from `templates/`; sheet list and filters are derived from the selected template
- **Tab Queries**: For each sheet in the template, choose a SQL query file from `queries/` (sheet → query mapping)
- **Date Configuration**: Set inventory date and compliance date for each report
- **Sheet Filters**: Configure column filters per sheet (columns come from the report’s template)
- **Filter Types**: Supports 15+ filter operators (equals, contains, in_list, between, etc.); `contains`/`not_contains` and list filters accept multiple values (comma-separated or list in JSON)
- **Three-Tier Configuration**:
  - **Default Config**: Template configuration (`{report_name}_default.json`)
  - **Saved Config**: Official saved configuration (`{report_name}_config.json`)
  - **Temp Config**: Temporary test configurations with timestamps (`config/temp/{report_name}_config_{timestamp}.json`)
- **Save Options**: Save as "Official" (persistent) or "Temp" (temporary with timestamp); saved files use a consistent JSON key order and format
- **Load Options**: Load default, saved, or temporary configurations
- **Configuration Preview**: View and download configuration as JSON

**Filter Operators**:
- Text: `equals`, `not_equals`, `contains`, `not_contains`, `starts_with`, `ends_with`
- Numeric: `greater_than`, `less_than`, `greater_equal`, `less_equal`, `between`
- List: `in_list`, `not_in_list`
- Null: `is_null`, `is_not_null`

**Configuration Loading Priority**:
1. Saved configuration (`{report_name}_config.json`)
2. Default configuration (`{report_name}_default.json`)
3. Generated default configuration

**Configuration File Locations**:
- Default: `config/{report_name}_default.json`
- Saved: `config/{report_name}_config.json`
- Temp: `config/temp/{report_name}_config_{timestamp}.json`

See `config/README.md` for detailed configuration file format and usage.

## Notes

- All SQL queries belong in the `queries/` folder; report configs reference them via `query` or `tab_queries`
- Excel templates live in `templates/`; each report can specify `excel_template_path` in its config
- Interim data (CSV, Parquet) is saved under `interim_data/{report_name}/`
- Output files are saved under `output_data/{report_name}/`
- Use Windows Authentication by default (no credentials in code)
- Run example scripts from the project root (e.g. `python examples/example_usage.py`)
- See `config/README.md` and `config/NAMING_CONVENTION.md` for configuration details