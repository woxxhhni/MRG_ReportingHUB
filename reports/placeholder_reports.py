"""
Placeholder Report Classes
These are placeholder classes for testing the configuration UI.
Actual report implementations will be added later.
"""

from .base_report import BaseReport
from pathlib import Path
import pandas as pd
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class ComplianceReport(BaseReport):
    """Placeholder for Compliance Report."""
    
    def __init__(self):
        super().__init__(
            report_name="Compliance Report",
            output_dir="output_data/compliance_report",
            interim_dir="interim_data/compliance_report"
        )
    
    def extract_data(self) -> pd.DataFrame:
        """Placeholder - to be implemented."""
        logger.warning("ComplianceReport.extract_data() not yet implemented")
        return pd.DataFrame()
    
    def transform_data(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """Placeholder - to be implemented."""
        return df_raw
    
    def calculate_aggregations(self, df: pd.DataFrame) -> dict:
        """Placeholder - to be implemented."""
        return {"Model": df, "Issues": df, "MDO_MBO_Rollup": df}
    
    def generate_report(self, aggregated_data: dict, filename_prefix: str = None) -> Path:
        """Placeholder - to be implemented."""
        file_path = self._get_output_path(filename_prefix, extension='.xlsx')
        if aggregated_data:
            self.excel_mgr.save_multiple_dataframes(
                dataframes=aggregated_data,
                file_path=file_path,
                index=False
            )
        else:
            pd.DataFrame().to_excel(file_path, index=False)
        return file_path


class ConsolidateReport(BaseReport):
    """Placeholder for Consolidate Report."""
    
    def __init__(self):
        super().__init__(
            report_name="Consolidate Report",
            output_dir="output_data/consolidate_report",
            interim_dir="interim_data/consolidate_report"
        )
    
    def extract_data(self) -> pd.DataFrame:
        """Placeholder - to be implemented."""
        logger.warning("ConsolidateReport.extract_data() not yet implemented")
        return pd.DataFrame()
    
    def transform_data(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """Placeholder - to be implemented."""
        return df_raw
    
    def calculate_aggregations(self, df: pd.DataFrame) -> dict:
        """Placeholder - to be implemented."""
        return {"Model": df, "Issues": df, "MDO_MBO_Rollup": df}
    
    def generate_report(self, aggregated_data: dict, filename_prefix: str = None) -> Path:
        """Placeholder - to be implemented."""
        file_path = self._get_output_path(filename_prefix, extension='.xlsx')
        if aggregated_data:
            self.excel_mgr.save_multiple_dataframes(
                dataframes=aggregated_data,
                file_path=file_path,
                index=False
            )
        else:
            pd.DataFrame().to_excel(file_path, index=False)
        return file_path


class KPIReport(BaseReport):
    """Placeholder for KPI Report."""
    
    def __init__(self):
        super().__init__(
            report_name="KPI Report",
            output_dir="output_data/kpi_report",
            interim_dir="interim_data/kpi_report"
        )
    
    def extract_data(self) -> pd.DataFrame:
        """Placeholder - to be implemented."""
        logger.warning("KPIReport.extract_data() not yet implemented")
        return pd.DataFrame()
    
    def transform_data(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """Placeholder - to be implemented."""
        return df_raw
    
    def calculate_aggregations(self, df: pd.DataFrame) -> dict:
        """Placeholder - to be implemented."""
        return {"Model": df, "Issues": df, "MDO_MBO_Rollup": df}
    
    def generate_report(self, aggregated_data: dict, filename_prefix: str = None) -> Path:
        """Placeholder - to be implemented."""
        file_path = self._get_output_path(filename_prefix, extension='.xlsx')
        if aggregated_data:
            self.excel_mgr.save_multiple_dataframes(
                dataframes=aggregated_data,
                file_path=file_path,
                index=False
            )
        else:
            pd.DataFrame().to_excel(file_path, index=False)
        return file_path
