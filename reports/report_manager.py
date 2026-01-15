"""
Report Manager
Centralized manager for all reports
"""

import logging
from typing import Dict, Type, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportManager:
    """
    Centralized manager for all reports.
    Provides registration and execution of reports.
    """
    
    def __init__(self):
        """Initialize report manager."""
        self.reports: Dict[str, Type] = {}
        logger.info("Report Manager initialized")
    
    def register(self, report_name: str, report_class: Type):
        """
        Register a report class.
        
        Args:
            report_name: Name/ID of the report
            report_class: Report class (must inherit from BaseReport)
        """
        self.reports[report_name.lower()] = report_class
        logger.info(f"Registered report: {report_name}")
    
    def list_reports(self) -> list:
        """
        List all registered reports.
        
        Returns:
            List of report names
        """
        return list(self.reports.keys())
    
    def get_report(self, report_name: str):
        """
        Get a report instance.
        
        Args:
            report_name: Name of the report
            
        Returns:
            Report instance
        """
        report_name_lower = report_name.lower()
        if report_name_lower not in self.reports:
            available = ", ".join(self.reports.keys())
            raise ValueError(
                f"Report '{report_name}' not found. Available reports: {available}"
            )
        
        report_class = self.reports[report_name_lower]
        return report_class()
    
    def run_report(self, report_name: str) -> Path:
        """
        Run a specific report.
        
        Args:
            report_name: Name of the report to run
            
        Returns:
            Path to generated report
        """
        logger.info(f"Running report: {report_name}")
        report = self.get_report(report_name)
        return report.run()


# Global report manager instance
_report_manager = ReportManager()


def get_report_manager() -> ReportManager:
    """Get the global report manager instance."""
    return _report_manager


def register_report(report_name: str, report_class: Type):
    """Register a report with the global manager."""
    _report_manager.register(report_name, report_class)


def run_report(report_name: str) -> Path:
    """Run a report by name."""
    return _report_manager.run_report(report_name)


def list_reports() -> list:
    """List all registered reports."""
    return _report_manager.list_reports()
