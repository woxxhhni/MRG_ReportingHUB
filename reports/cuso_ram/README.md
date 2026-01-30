# CUSO RAM Report

## Overview

CUSO RAM (Risk Appetite Measure) Report processes and aggregates model information from the Model Governance team. Data source, query mapping, and output structure are driven by the report configuration (JSON).

## Configuration

- **Config files**: `config/cuso_ram_report_default.json`, `config/cuso_ram_report_config.json` (see `config/README.md`).
- **Report-level options**:
  - `excel_template_path`: Optional path to an Excel template (e.g. `templates/cuso_ram_report_template.xlsx`). If set, output is written into this template.
  - `query`: Path to a single SQL query file (used when `tab_queries` is empty).
  - `tab_queries`: Map of **sheet name** → **query file path**. When non-empty, one query runs per sheet and results are written to the corresponding sheet; this overrides `query`.
- **Sheet filters**: Configured per sheet in `sheet_filters`; column names are taken from the report’s Excel template when using the UI.

## Report Structure (typical)

When using the default template, the report can generate an Excel file with sheets such as:

1. **Model** — Model-level data
2. **Issues** — Issues data
3. **MDO_MBO_Rollup** — Rollup aggregations

Exact sheet names and columns depend on the template and config.

## Usage

### From config (recommended)

```python
from reports.cuso_ram_report import CUSORAMReport

# Load config from file (uses template path, query/tab_queries, filters, dates)
report = CUSORAMReport.from_config_file("config/cuso_ram_report_config.json")
report.run()

# Override dates
report = CUSORAMReport.from_config_file(
    "config/cuso_ram_report_config.json",
    inventory_date="2026-06-30",
    compliance_date="2026-06-30"
)
report.run()
```

### Constructor (dates / config override)

```python
# Default config loading: saved → default → generate
report = CUSORAMReport()
report.run()

# Explicit config
report = CUSORAMReport(
    inventory_date="2026-12-31",
    compliance_date="2026-12-31"
)
report.run()

# Force default or temp config
report = CUSORAMReport(config_file="default")
report.run()
report = CUSORAMReport(config_file="temp:20260129_143022")
report.run()
```

### Command line

```bash
python run_cuso_ram_report.py
python run_cuso_ram_report.py 2026-12-31
python run_cuso_ram_report.py 2026-12-31 2026-12-31
```

## Query placeholders

- `(0=0)` → Replaced with inventory date condition: `M.DateStamp = 'YYYY-MM-DD'`
- `(10=10)` → Replaced with compliance date value: `'YYYY-MM-DD'`
- `[DBName].[DBSchema]` → Replaced with `[DMAV_MAVRICK].[MAV2]`

## Output

- **Excel**: `output_data/cuso_ram/CUSO_RAM_Report_YYYYMMDD_HHMMSS.xlsx` (or as configured with template)
- **Interim data**: `interim_data/cuso_ram/` (e.g. CSV/Parquet)

## Data flow

1. Load config (saved → default → generated).
2. Resolve query: use `tab_queries` if non-empty, else `query`.
3. Extract: run SQL (with placeholders replaced), apply sheet filters.
4. Transform/aggregate as needed.
5. Write Excel (into template if `excel_template_path` is set and exists).
6. Save interim data.

## Notes

- Ensure the SQL query file and template (if used) exist at the paths specified in config.
- Sheet names in `tab_queries` and `sheet_filters` should match the template sheets.
- See root `README.md` and `config/README.md` for configuration and UI details.
