"""
Reports Module
Contains all report generators
"""

from .base_report import BaseReport
from .report_manager import ReportManager, get_report_manager, register_report, run_report, list_reports
from .cuso_ram_report import CUSORAMReport
from .placeholder_reports import ComplianceReport, ConsolidateReport, KPIReport

# Register reports
register_report("CUSO RAM Report", CUSORAMReport)

# Register placeholder reports for UI testing
register_report("Compliance Report", ComplianceReport)
register_report("Consolidate Report", ConsolidateReport)
register_report("KPI Report", KPIReport)

__all__ = [
    "BaseReport",
    "ReportManager",
    "get_report_manager",
    "register_report",
    "run_report",
    "list_reports",
    "CUSORAMReport",
    "ComplianceReport",
    "ConsolidateReport",
    "KPIReport",
]
