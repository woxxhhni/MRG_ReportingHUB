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
from db_manager import create_mavrick_db_manager

# Connect to MAVRICK DB
db = create_mavrick_db_manager()

# Run query from string
df = db.run_query_from_string("SELECT * FROM MAV2.UIUMissingData")

# Run query from file
from pathlib import Path
df = db.run_query_from_file(Path("queries/uiu_missing_data.sql"))

# Save result to interim data
df.to_csv("interim_data/result.csv", index=False)

# Close connection
db.close()
```

## Project Structure

```
MRG_ReportingHUB/
├── db_manager.py          # Database manager class
├── queries/               # SQL query scripts
│   └── uiu_missing_data.sql
├── interim_data/          # Temporary/intermediate data files
├── example_usage.py       # Usage examples
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

## Notes

- All SQL queries should be stored in the `queries/` folder
- Interim data files (CSV, Parquet) should be saved in `interim_data/` folder
- Use Windows Authentication by default (no credentials needed)
