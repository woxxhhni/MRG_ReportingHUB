"""
Reports Module
Contains all report generators
"""

from .base_report import BaseReport
from .report_manager import ReportManager, get_report_manager, register_report, run_report, list_reports
from .cuso_ram_report import CUSORAMReport

# Register reports
register_report("cuso_ram", CUSORAMReport)
register_report("CUSO RAM", CUSORAMReport)

__all__ = [
    "BaseReport",
    "ReportManager",
    "get_report_manager",
    "register_report",
    "run_report",
    "list_reports",
    "CUSORAMReport",
]
