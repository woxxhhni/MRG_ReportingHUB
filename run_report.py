"""
Run Report
Unified script to run any registered report
"""

import sys
import logging
from reports import get_report_manager, list_reports, run_report

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run reports."""
    if len(sys.argv) < 2:
        print("=" * 60)
        print("MRG Reporting HUB - Report Runner")
        print("=" * 60)
        print()
        print("Usage: python run_report.py <report_name>")
        print()
        print("Available reports:")
        available_reports = list_reports()
        for report in available_reports:
            print(f"  - {report}")
        print()
        print("Example: python run_report.py cuso_ram")
        print("=" * 60)
        sys.exit(1)
    
    report_name = sys.argv[1]
    
    try:
        print("=" * 60)
        print(f"Running Report: {report_name}")
        print("=" * 60)
        print()
        
        report_path = run_report(report_name)
        
        print()
        print("=" * 60)
        print("Report generated successfully!")
        print(f"Location: {report_path}")
        print("=" * 60)
    
    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        logger.exception("Report execution failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
