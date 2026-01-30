"""
Basic import and package tests.
Run from project root: pytest tests/ -v
"""

import pytest


def test_utils_import():
    """Utils package and key exports are importable."""
    from utils import (
        DBManager,
        create_mavrick_db_manager,
        ExcelManager,
        MRGDate,
        get_config_manager,
        apply_filter_to_dataframe,
    )
    assert DBManager is not None
    assert ExcelManager is not None
    assert MRGDate is not None


def test_reports_import():
    """Reports package and key exports are importable."""
    from reports import (
        BaseReport,
        get_report_manager,
        list_reports,
        run_report,
        CUSORAMReport,
    )
    assert BaseReport is not None
    assert callable(list_reports)
    assert callable(run_report)
    reports = list_reports()
    assert isinstance(reports, list)
    assert "CUSO RAM Report" in reports


def test_filter_utils_parse():
    """Filter utils _parse_comma_separated_values handles string and list."""
    from utils.filter_utils import _parse_comma_separated_values

    assert _parse_comma_separated_values("a, b, c") == ["a", "b", "c"]
    assert _parse_comma_separated_values(["a", "b"]) == ["a", "b"]
    assert _parse_comma_separated_values(None) == []
    assert _parse_comma_separated_values("") == []
