"""
Run CUSO RAM Report
Simple script to execute the CUSO RAM report
"""

import sys
from reports.cuso_ram_report import CUSORAMReport

# ============================================================================
# CONFIGURATION: Set your dates here
# ============================================================================
# Option 1: Set specific dates (string format: 'YYYY-MM-DD', 'YYYYMMDD', or 'YYYY/MM/DD')
# INVENTORY_DATE: Used to replace (0=0) placeholder in queries (inventory date)
# COMPLIANCE_DATE: Used to replace (10=10) placeholder in queries (compliance date)
# Example: INVENTORY_DATE = '2026-12-31'
# Example: COMPLIANCE_DATE = '2026-12-31'
INVENTORY_DATE = '2026-12-31'  # Set to None to use command line argument or default (today)
COMPLIANCE_DATE = None  # Set to None to use command line argument or default (same as inventory date)

# Option 2: Leave as None and pass dates via command line:
#   python run_cuso_ram_report.py 2026-12-31 2026-12-31
#   (first argument: inventory_date, second argument: compliance_date)
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CUSO RAM Report - Risk Appetite Measure")
    print("=" * 60)
    print()
    
    # Priority: 1. Script configuration, 2. Command line argument, 3. Default (today)
    inventory_date = None
    compliance_date = None
    
    if INVENTORY_DATE is not None:
        inventory_date = INVENTORY_DATE
        print(f"Using inventory date from script configuration: {inventory_date}")
    elif len(sys.argv) > 1:
        inventory_date = sys.argv[1]
        print(f"Using inventory date from command line: {inventory_date}")
    else:
        print("Using default inventory date (today)")
    
    if COMPLIANCE_DATE is not None:
        compliance_date = COMPLIANCE_DATE
        print(f"Using compliance date from script configuration: {compliance_date}")
    elif len(sys.argv) > 2:
        compliance_date = sys.argv[2]
        print(f"Using compliance date from command line: {compliance_date}")
    elif inventory_date is not None:
        # If compliance date not specified, use same as inventory date
        compliance_date = inventory_date
        print(f"Using compliance date (same as inventory date): {compliance_date}")
    else:
        print("Using default compliance date (today)")
    print()
    
    try:
        report = CUSORAMReport(inventory_date=inventory_date, compliance_date=compliance_date)
        report_path = report.run()
        
        print()
        print("=" * 60)
        print("Report generated successfully!")
        print(f"Location: {report_path}")
        print("=" * 60)
    
    except Exception as e:
        print(f"\nError: {e}")
        raise
