# Configuration File Naming Convention

## Overview

All configuration files follow a consistent naming pattern based on the registered report name.

## Naming Rules

1. **Report Name Normalization**:
   - Convert to lowercase
   - Replace spaces with underscores (`_`)
   - Replace slashes with underscores (`/` → `_`)
   - Example: `"CUSO RAM Report"` → `"cuso_ram_report"`

2. **File Naming Pattern**:
   - **Default Config**: `{normalized_report_name}_default.json`
   - **Saved Config**: `{normalized_report_name}_config.json`

## Current Reports and Expected Files

| Report Name | Normalized Name | Default File | Config File |
|------------|----------------|--------------|-------------|
| CUSO RAM Report | `cuso_ram_report` | `cuso_ram_report_default.json` | `cuso_ram_report_config.json` |
| Compliance Report | `compliance_report` | `compliance_report_default.json` | `compliance_report_config.json` |
| Consolidate Report | `consolidate_report` | `consolidate_report_default.json` | `consolidate_report_config.json` |
| KPI Report | `kpi_report` | `kpi_report_default.json` | `kpi_report_config.json` |

## Implementation

The naming convention is implemented in `utils/config_manager.py`:

```python
def get_config_path(self, report_name: str, config_type: str = "config") -> Path:
    # Normalize report name for filename
    safe_name = report_name.lower().replace(" ", "_").replace("/", "_")
    
    if config_type == "default":
        return self.config_dir / f"{safe_name}_default.json"
    elif config_type == "config":
        return self.config_dir / f"{safe_name}_config.json"
```

## File Status

### Required Files (Default Configurations)
- ✅ `cuso_ram_report_default.json` - CUSO RAM Report default
- ✅ `compliance_report_default.json` - Compliance Report default
- ✅ `consolidate_report_default.json` - Consolidate Report default
- ✅ `kpi_report_default.json` - KPI Report default

### Optional Files (Saved Configurations)
- ✅ `cuso_ram_report_config.json` - CUSO RAM Report saved config (created when user saves)
- ⚠️ `compliance_report_config.json` - Will be created when user saves Compliance Report config
- ⚠️ `consolidate_report_config.json` - Will be created when user saves Consolidate Report config
- ⚠️ `kpi_report_config.json` - Will be created when user saves KPI Report config

## Best Practices

1. **Always use the config manager** to get file paths - don't hardcode filenames
2. **Register report names consistently** - use the same name in `reports/__init__.py` and when calling config functions
3. **Default files should exist** for all reports to provide fallback configurations
4. **Config files are optional** - created automatically when users save configurations through the UI

## Adding New Reports

When adding a new report:

1. Register the report in `reports/__init__.py`:
   ```python
   register_report("My New Report", MyNewReport)
   ```

2. Create a default configuration file:
   - File name: `my_new_report_default.json`
   - Location: `config/my_new_report_default.json`
   - Use `get_default_report_config()` or create manually

3. The saved config file (`my_new_report_config.json`) will be created automatically when users save through the UI.
