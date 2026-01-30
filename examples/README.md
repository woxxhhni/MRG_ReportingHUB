# Examples

Example scripts for MRG Reporting HUB. Run from the **project root** so paths and imports resolve correctly.

```bash
# From project root (MRG_ReportingHUB/)
python examples/example_usage.py    # DB manager examples
python examples/excel_example.py    # Excel manager examples
python examples/date_example.py     # MRGDate and date utilities
python examples/config_example.py   # (view only) sample DB config structure
```

| Script | Description |
|--------|-------------|
| **example_usage.py** | DBManager: connect, run queries from string/file, save/load interim data, query placeholders |
| **excel_example.py** | ExcelManager: save/append DataFrames, read Excel, multiple sheets |
| **date_example.py** | MRGDate: create dates, operations, business days, DataFrame conversion |
| **config_example.py** | Sample DB connection config structure; copy to `config.py` at project root and customize (do not commit credentials) |
