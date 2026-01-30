"""
Configuration Manager
Handles saving and loading report configurations
Supports three-tier configuration: default → saved → temp
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import date, datetime
import logging

logger = logging.getLogger(__name__)

# Canonical key order for saved config JSON (same format as default configs)
CONFIG_KEY_ORDER = (
    "report_name",
    "report_description",
    "inventory_date",
    "compliance_date",
    "excel_template_path",
    "query",
    "tab_queries",
    "sheet_filters",
)


def _config_to_canonical_format(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return config with canonical key order and default values matching default JSON.
    Ensures saved config from UI has the same format as default config files.
    """
    out = {}
    for key in CONFIG_KEY_ORDER:
        if key in config:
            val = config[key]
        elif key == "report_description":
            val = config.get("report_description") or ""
        elif key == "tab_queries":
            val = config.get("tab_queries") if isinstance(config.get("tab_queries"), dict) else {}
        elif key == "sheet_filters":
            val = config.get("sheet_filters") if isinstance(config.get("sheet_filters"), dict) else {}
        else:
            val = config.get(key)
        out[key] = val
    return out


class ReportConfigManager:
    """
    Manages report configurations.
    Handles saving and loading configuration files.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory to store configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        # Create temp directory for temporary configurations
        self.temp_dir = self.config_dir / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Configuration manager initialized with config_dir: {config_dir}")
    
    def get_config_path(self, report_name: str, config_type: str = "config") -> Path:
        """
        Get the configuration file path for a report.
        
        Args:
            report_name: Name of the report
            config_type: Type of configuration ('default', 'config', 'temp')
                        For 'temp', returns temp directory path (not a specific file)
            
        Returns:
            Path to configuration file or directory
        """
        # Normalize report name for filename
        safe_name = report_name.lower().replace(" ", "_").replace("/", "_")
        
        if config_type == "default":
            return self.config_dir / f"{safe_name}_default.json"
        elif config_type == "config":
            return self.config_dir / f"{safe_name}_config.json"
        elif config_type == "temp":
            return self.temp_dir
        else:
            raise ValueError(f"Invalid config_type: {config_type}. Must be 'default', 'config', or 'temp'")
    
    def load_config(self, report_name: str, config_type: str = "config") -> Optional[Dict[str, Any]]:
        """
        Load configuration for a report.
        
        Args:
            report_name: Name of the report
            config_type: Type of configuration to load ('default', 'config', 'temp')
                        For 'temp', requires a specific filename or timestamp
            
        Returns:
            Configuration dictionary, or None if not found
        """
        if config_type == "temp":
            raise ValueError("For temp configs, use load_temp_config() with filename or timestamp")
        
        config_path = self.get_config_path(report_name, config_type)
        
        if not config_path.exists():
            logger.info(f"No {config_type} configuration found for report: {report_name}")
            return None
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"Loaded {config_type} configuration for report: {report_name}")
            return config
        except Exception as e:
            logger.error(f"Failed to load {config_type} configuration for {report_name}: {e}")
            return None
    
    def load_default_config(self, report_name: str) -> Optional[Dict[str, Any]]:
        """
        Load default configuration for a report.
        
        Args:
            report_name: Name of the report
            
        Returns:
            Default configuration dictionary, or None if not found
        """
        return self.load_config(report_name, config_type="default")
    
    def load_config_with_fallback(self, report_name: str) -> Dict[str, Any]:
        """
        Load configuration with fallback priority: saved config → default config → generate default.
        
        Args:
            report_name: Name of the report
            
        Returns:
            Configuration dictionary (always returns a config, never None)
        """
        # Try saved config first
        config = self.load_config(report_name, config_type="config")
        if config:
            logger.info(f"Using saved configuration for {report_name}")
            return config
        
        # Try default config
        config = self.load_default_config(report_name)
        if config:
            logger.info(f"Using default configuration for {report_name}")
            return config
        
        # Generate default config
        logger.info(f"Generating new default configuration for {report_name}")
        return self.get_default_config(report_name)
    
    def load_temp_config(self, report_name: str, filename: Optional[str] = None, 
                        timestamp: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Load a temporary configuration file.
        
        Args:
            report_name: Name of the report
            filename: Specific filename (e.g., "cuso_ram_config_20260129_143022.json")
            timestamp: Timestamp string (e.g., "20260129_143022")
            
        Returns:
            Configuration dictionary, or None if not found
        """
        safe_name = report_name.lower().replace(" ", "_").replace("/", "_")
        
        if filename:
            config_path = self.temp_dir / filename
        elif timestamp:
            config_path = self.temp_dir / f"{safe_name}_config_{timestamp}.json"
        else:
            raise ValueError("Either filename or timestamp must be provided")
        
        if not config_path.exists():
            logger.info(f"Temp configuration not found: {config_path}")
            return None
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"Loaded temp configuration: {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load temp configuration: {e}")
            return None
    
    def save_config(self, report_name: str, config: Dict[str, Any]) -> Path:
        """
        Save configuration as the official saved configuration for a report.
        
        Args:
            report_name: Name of the report
            config: Configuration dictionary
            
        Returns:
            Path to saved configuration file
        """
        config_path = self.get_config_path(report_name, config_type="config")
        canonical = _config_to_canonical_format(config)
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(canonical, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved configuration for report: {report_name} to {config_path}")
            return config_path
        except Exception as e:
            logger.error(f"Failed to save configuration for {report_name}: {e}")
            raise
    
    def save_default_config(self, report_name: str, config: Dict[str, Any]) -> Path:
        """
        Save default configuration template for a report.
        
        Args:
            report_name: Name of the report
            config: Configuration dictionary
            
        Returns:
            Path to saved default configuration file
        """
        config_path = self.get_config_path(report_name, config_type="default")
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved default configuration for report: {report_name} to {config_path}")
            return config_path
        except Exception as e:
            logger.error(f"Failed to save default configuration for {report_name}: {e}")
            raise
    
    def save_temp_config(self, report_name: str, config: Dict[str, Any]) -> Path:
        """
        Save configuration as a temporary configuration file with timestamp.
        
        Args:
            report_name: Name of the report
            config: Configuration dictionary
            
        Returns:
            Path to saved temporary configuration file
        """
        safe_name = report_name.lower().replace(" ", "_").replace("/", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_path = self.temp_dir / f"{safe_name}_config_{timestamp}.json"
        canonical = _config_to_canonical_format(config)
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(canonical, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved temp configuration for report: {report_name} to {config_path}")
            return config_path
        except Exception as e:
            logger.error(f"Failed to save temp configuration for {report_name}: {e}")
            raise
    
    def list_temp_configs(self, report_name: str) -> List[Dict[str, Any]]:
        """
        List all temporary configurations for a report.
        
        Args:
            report_name: Name of the report
            
        Returns:
            List of dictionaries with 'filename', 'timestamp', and 'path' keys
        """
        safe_name = report_name.lower().replace(" ", "_").replace("/", "_")
        pattern = f"{safe_name}_config_*.json"
        
        temp_configs = []
        for config_file in self.temp_dir.glob(pattern):
            # Extract timestamp from filename
            filename = config_file.name
            # Format: {safe_name}_config_{timestamp}.json
            if f"{safe_name}_config_" in filename:
                timestamp_str = filename.replace(f"{safe_name}_config_", "").replace(".json", "")
                temp_configs.append({
                    "filename": filename,
                    "timestamp": timestamp_str,
                    "path": config_file,
                    "modified_time": datetime.fromtimestamp(config_file.stat().st_mtime)
                })
        
        # Sort by modified time (newest first)
        temp_configs.sort(key=lambda x: x["modified_time"], reverse=True)
        return temp_configs
    
    def cleanup_temp_configs(self, report_name: Optional[str] = None, days: int = 7) -> int:
        """
        Clean up temporary configurations older than specified days.
        
        Args:
            report_name: Name of the report (if None, cleans all reports)
            days: Number of days to keep (default: 7)
            
        Returns:
            Number of files deleted
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        if report_name:
            safe_name = report_name.lower().replace(" ", "_").replace("/", "_")
            pattern = f"{safe_name}_config_*.json"
            files_to_check = list(self.temp_dir.glob(pattern))
        else:
            files_to_check = list(self.temp_dir.glob("*_config_*.json"))
        
        for config_file in files_to_check:
            try:
                modified_time = datetime.fromtimestamp(config_file.stat().st_mtime)
                if modified_time < cutoff_time:
                    config_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old temp config: {config_file}")
            except Exception as e:
                logger.warning(f"Failed to delete temp config {config_file}: {e}")
        
        logger.info(f"Cleaned up {deleted_count} temporary configuration files")
        return deleted_count
    
    def get_default_config(self, report_name: str) -> Dict[str, Any]:
        """
        Get default configuration structure for a report.
        
        Args:
            report_name: Name of the report
            
        Returns:
            Default configuration dictionary
        """
        from datetime import date
        today = date.today()
        
        return {
            "report_name": report_name,
            "report_description": "",
            "inventory_date": today.strftime("%Y-%m-%d"),
            "compliance_date": today.strftime("%Y-%m-%d"),
            "sheet_filters": {},
            "excel_template_path": None,
            "query": None,
            "tab_queries": {}
        }
    
    def merge_config(self, existing_config: Optional[Dict[str, Any]], 
                    new_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge new configuration with existing configuration.
        
        Args:
            existing_config: Existing configuration (can be None)
            new_config: New configuration to merge
            
        Returns:
            Merged configuration
        """
        if existing_config is None:
            return new_config.copy()
        
        merged = existing_config.copy()
        merged.update(new_config)
        
        # Deep merge sheet_filters
        if "sheet_filters" in new_config:
            if "sheet_filters" not in merged:
                merged["sheet_filters"] = {}
            merged["sheet_filters"].update(new_config["sheet_filters"])
        
        return merged


# Global configuration manager instance
_config_manager = ReportConfigManager()


def get_config_manager() -> ReportConfigManager:
    """Get the global configuration manager instance."""
    return _config_manager


def load_report_config(report_name: str) -> Optional[Dict[str, Any]]:
    """Load saved configuration for a report."""
    return _config_manager.load_config(report_name, config_type="config")


def load_report_config_with_fallback(report_name: str) -> Dict[str, Any]:
    """Load configuration with fallback: saved → default → generate."""
    return _config_manager.load_config_with_fallback(report_name)


def save_report_config(report_name: str, config: Dict[str, Any]) -> Path:
    """Save configuration as the official saved configuration for a report."""
    return _config_manager.save_config(report_name, config)


def load_default_config(report_name: str) -> Optional[Dict[str, Any]]:
    """Load default configuration for a report."""
    return _config_manager.load_default_config(report_name)


def save_default_config(report_name: str, config: Dict[str, Any]) -> Path:
    """Save default configuration template for a report."""
    return _config_manager.save_default_config(report_name, config)


def save_temp_config(report_name: str, config: Dict[str, Any]) -> Path:
    """Save configuration as a temporary configuration file with timestamp."""
    return _config_manager.save_temp_config(report_name, config)


def load_temp_config(report_name: str, filename: Optional[str] = None, 
                    timestamp: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Load a temporary configuration file."""
    return _config_manager.load_temp_config(report_name, filename, timestamp)


def list_temp_configs(report_name: str) -> List[Dict[str, Any]]:
    """List all temporary configurations for a report."""
    return _config_manager.list_temp_configs(report_name)


def cleanup_temp_configs(report_name: Optional[str] = None, days: int = 7) -> int:
    """Clean up temporary configurations older than specified days."""
    return _config_manager.cleanup_temp_configs(report_name, days)


def get_default_report_config(report_name: str) -> Dict[str, Any]:
    """Get default configuration for a report (generates if not exists)."""
    return _config_manager.get_default_config(report_name)


def get_canonical_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Return config with canonical key order (same format as saved/default JSON)."""
    return _config_to_canonical_format(config)
