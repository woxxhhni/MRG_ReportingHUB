"""
Run CUSO RAM Report
Simple script to execute the CUSO RAM report
"""

import sys
from reports.cuso_ram_report import CUSORAMReport

if __name__ == "__main__":
    print("=" * 60)
    print("CUSO RAM Report - Risk Appetite Measure")
    print("=" * 60)
    print()
    
    # Get data stamp date from command line argument if provided
    data_stamp_date = None
    if len(sys.argv) > 1:
        data_stamp_date = sys.argv[1]
        print(f"Using data stamp date: {data_stamp_date}")
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
