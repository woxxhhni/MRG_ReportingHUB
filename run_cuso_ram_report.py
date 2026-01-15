"""
Run CUSO RAM Report
Simple script to execute the CUSO RAM report
"""

from reports.cuso_ram_report import CUSORAMReport

if __name__ == "__main__":
    print("=" * 60)
    print("CUSO RAM Report - Risk Appetite Measure")
    print("=" * 60)
    print()
    
    try:
        report = CUSORAMReport()
        report_path = report.run()
        
        print()
        print("=" * 60)
        print("Report generated successfully!")
        print(f"Location: {report_path}")
        print("=" * 60)
    
    except Exception as e:
        print(f"\nError: {e}")
        raise
