# Report Configuration Files

This directory stores report configuration files. Configurations can be created and edited through the Streamlit configuration UI or by editing JSON files directly.

## Configuration Structure

The configuration system uses a **three-tier** structure:

```
config/
├── {report_name}_default.json    # Default configuration (template)
├── {report_name}_config.json     # Saved configuration (user-created)
└── temp/                         # Temporary configurations (timestamped)
    └── {report_name}_config_{YYYYMMDD_HHMMSS}.json
```

### Configuration Types

1. **Default Configuration** (`{report_name}_default.json`)
   - Template configuration for each report
   - Can be manually created or auto-generated
   - Used as fallback when no saved config exists
   - Should contain reasonable defaults
   - **Required** for all reports

2. **Saved Configuration** (`{report_name}_config.json`)
   - Configuration saved by users through the UI (or manually)
   - Used for regular report runs
   - Takes priority over default config
   - **Optional** — created when the user saves as "Official"

3. **Temporary Configuration** (`temp/{report_name}_config_{timestamp}.json`)
   - Test configurations saved as "Temp" from the UI
   - Useful for trying changes without overwriting the saved config
   - Can be loaded from the UI expander or by using `config_file="temp:YYYYMMDD_HHMMSS"`

### Configuration Loading Priority

When loading a report configuration:
1. **Saved** — `{report_name}_config.json` (highest priority)
2. **Default** — `{report_name}_default.json`
3. **Generated** — if neither exists, a default config is generated

### File Naming Convention

Report names are normalized for filenames:
- Convert to lowercase
- Replace spaces with underscores
- Example: `"CUSO RAM Report"` → `"cuso_ram_report"`

See `NAMING_CONVENTION.md` for detailed naming rules.

## Configuration File Format

Each report has a JSON configuration file with the following structure:

```json
{
  "report_name": "CUSO RAM Report",
  "report_description": "",
  "inventory_date": "2026-12-31",
  "compliance_date": "2026-12-31",
  "excel_template_path": null,
  "query": "queries/Risk Appetite Measure (RAM) Models_New.sql",
  "tab_queries": {},
  "sheet_filters": {
    "Detail": {
      "ModelOwner": {
        "operator": "equals",
        "value": "John Doe",
        "enabled": true
      }
    }
  }
}
```

### Report-level options

| Key | Type | Description |
|-----|------|-------------|
| `report_name` | string | Display name of the report. |
| `report_description` | string | Short description of the report (shown in UI). |
| `inventory_date` | string | Inventory date (YYYY-MM-DD). Used in query placeholders. |
| `compliance_date` | string | Compliance date (YYYY-MM-DD). Used in query placeholders. |
| `excel_template_path` | string \| null | Path to an Excel template file. If set and the file exists, the report is written into this template (one DataFrame per sheet). |
| `query` | string \| null | Path to the main SQL query file (single-query reports). Ignored if `tab_queries` is non-empty. |
| `tab_queries` | object | Map of **sheet name** → **query file path**. When non-empty, one query is run per sheet and results are written to the corresponding sheet. Overrides `query` when present. |
| `sheet_filters` | object | Per-sheet column filters (see UI and filter operators). |

## Usage

### Using Streamlit UI

1. **Launch Configuration UI** (from project root):
   ```bash
   streamlit run report_config_ui.py
   ```

2. **Configure Reports**:
   - Select a report from the sidebar
   - Edit **Report Description** (optional)
   - In **Report Template**, choose an Excel template from `templates/` (or "No template"); sheets and columns are derived from the selected template
   - In **Tab Queries**, for each sheet choose a SQL file from `queries/` (sheet → query mapping)
   - Set **inventory_date** and **compliance_date**
   - Configure **Sheet Filters** per sheet (columns come from the template)
   - Save as "Official" (writes `{report_name}_config.json` in consistent key order) or "Temp" (writes to `config/temp/` with timestamp)

3. **Load Configurations**:
   - "Load Default Config" — reset to default template
   - "Load Saved Config" — load official saved configuration
   - Expand temporary configs to view and load a temp file by timestamp

### Programmatic Usage

```python
from reports.cuso_ram_report import CUSORAMReport

# Use default loading (saved → default → generate)
report = CUSORAMReport()

# Force use default configuration
report = CUSORAMReport(config_file="default")

# Use specific temporary configuration
report = CUSORAMReport(config_file="temp:20260129_143022")

# Use specific config file path
report = CUSORAMReport(config_file="config/custom_config.json")
```

### Manual Configuration

You can also manually edit JSON files in this directory:
- Edit `{report_name}_default.json` to change default template
- Edit `{report_name}_config.json` to change saved configuration
- Temporary configs are auto-generated with timestamps

### Cleanup Temporary Configs

Temporary configurations older than 7 days can be cleaned up:

```python
from utils import cleanup_temp_configs

# Clean all temp configs older than 7 days
cleanup_temp_configs(days=7)

# Clean temp configs for specific report
cleanup_temp_configs(report_name="CUSO RAM", days=7)
```

## Filter Operators

- `equals`: Exact match
- `not_equals`: Not equal
- `contains`: Contains any of the given substrings (case-insensitive); value can be a list or comma-separated
- `not_contains`: Does not contain any of the given substrings; value can be a list or comma-separated
- `starts_with`: Starts with string
- `ends_with`: Ends with string
- `greater_than`: Greater than value
- `less_than`: Less than value
- `greater_equal`: Greater than or equal
- `less_equal`: Less than or equal
- `in_list`: Value is in list
- `not_in_list`: Value is not in list
- `is_null`: Value is null/empty
- `is_not_null`: Value is not null/empty
- `between`: Value is between min and max (requires list with 2 values)
