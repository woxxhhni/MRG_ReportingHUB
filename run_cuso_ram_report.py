"""
Run CUSO RAM Report
Simple script to execute the CUSO RAM report
"""

import sys
from reports.cuso_ram_report import CUSORAMReport

# ============================================================================
# CONFIGURATION: Set your data stamp date here
# ============================================================================
# Option 1: Set a specific date (string format: 'YYYY-MM-DD', 'YYYYMMDD', or 'YYYY/MM/DD')
# Example: DATA_STAMP_DATE = '2025-12-31'
# Example: DATA_STAMP_DATE = '20251231'
# Example: DATA_STAMP_DATE = '2025/12/31'
DATA_STAMP_DATE = '2026-12-31'  # Set to None to use command line argument or default (today)

# Option 2: Leave as None and pass date via command line:
#   python run_cuso_ram_report.py 2025-12-31
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CUSO RAM Report - Risk Appetite Measure")
    print("=" * 60)
    print()
    
    # Priority: 1. Script configuration, 2. Command line argument, 3. Default (today)
    data_stamp_date = None
    
    if DATA_STAMP_DATE is not None:
        data_stamp_date = DATA_STAMP_DATE
        print(f"Using data stamp date from script configuration: {data_stamp_date}")
    elif len(sys.argv) > 1:
        data_stamp_date = sys.argv[1]
        print(f"Using data stamp date from command line: {data_stamp_date}")
    else:
        print("Using default data stamp date (today)")
    print()
    
    try:
        report = CUSORAMReport(data_stamp_date=data_stamp_date)
        report_path = report.run()
        
        print()
        print("=" * 60)
        print("Report generated successfully!")
        print(f"Location: {report_path}")
        print("=" * 60)
    
    except Exception as e:
        print(f"\nError: {e}")
        raise
