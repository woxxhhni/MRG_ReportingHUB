# Report Excel Templates

Excel templates define the structure of report output: sheet names and (optionally) column headers. Each report can specify an `excel_template_path` in its configuration; the Report Configuration UI uses the selected template to derive sheets and columns for **Tab Queries** and **Sheet Filters**.

## Available Templates

| Template | Report(s) | Notes |
|----------|-----------|--------|
| `cuso_ram_report_template.xlsx` | CUSO RAM Report | Sheets: **Model**, **Issues**, **MDO_MBO_Rollup** |
| `compliance_report_template.xlsx` | Compliance Report | Used when Compliance Report template is selected in UI |
| `consolidate_report_template.xlsx` | Consolidate Report | Used when Consolidate Report template is selected |
| `kpi_report_template.xlsx` | KPI Report | Used when KPI Report template is selected |

## How Templates Are Used

1. **Configuration UI**  
   In **Report Template**, you choose a template from the dropdown (or "No template"). The UI then:
   - Lists sheets from that template for **Tab Queries** (sheet → SQL file).
   - Uses the template’s column headers for **Sheet Filter** configuration.

2. **Report runs**  
   If the config has `excel_template_path` set and the file exists, the report writes data into that template (one DataFrame per sheet). Otherwise, the report may create a new workbook or use its own logic.

## Creating or Updating Templates

- **CUSO RAM**: A default template can be created with:
  ```bash
  python scripts/create_cuso_ram_template.py
  ```
  The Report Configuration UI can also create a sample template for a report if none is specified or the file is missing.

- **Other reports**: Add or edit `.xlsx` files in this folder. The UI lists all `.xlsx` files in `templates/` for selection (excluding temporary files like `~$*.xlsx`).

## Location

All templates live under the project’s `templates/` directory. Config files reference them by path, e.g. `templates/cuso_ram_report_template.xlsx`.
