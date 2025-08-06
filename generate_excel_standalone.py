#!/usr/bin/env python
"""
Standalone Excel Report Generator
Generates Excel reports from JSON entity files created by the PDF extraction system.

Usage: python3 generate_excel_standalone.py <entities_json_file> [output_excel_file]
"""

import os
import sys
from generate_excel_report import load_entities, generate_excel_report
from pathlib import Path

def main():
    """Main function for standalone Excel generation"""
    if len(sys.argv) < 2:
        print("Usage: python3 generate_excel_standalone.py <entities_json_file> [output_excel_file]")
        print("\nExamples:")
        print("  python3 generate_excel_standalone.py output/Sample1_entities.json")
        print("  python3 generate_excel_standalone.py output/Sample1_entities.json my_report.xlsx")
        print("\nThis script generates Excel reports from JSON entity files created by the PDF extraction system.")
        return
    
    # Get the entities JSON file
    entities_json = sys.argv[1]
    if not os.path.exists(entities_json):
        print(f"Error: File not found - {entities_json}")
        return
    
    # Determine output file name
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        # Generate output file name based on input file
        input_path = Path(entities_json)
        if input_path.stem.endswith("_entities"):
            base_name = input_path.stem.replace("_entities", "")
        else:
            base_name = input_path.stem
        output_file = f"{base_name}_report.xlsx"
    
    # Ensure output directory exists
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate the report
    try:
        print(f"Loading entities from: {entities_json}")
        entities = load_entities(entities_json)
        
        print(f"Generating Excel report...")
        excel_file = generate_excel_report(entities, None, str(output_file))
        print(f"✅ Excel report successfully generated: {excel_file}")
        
        # Print summary
        test_results = entities.get('test_results', [])
        pass_count = sum(1 for test in test_results if test.get('pass_fail', '').lower() == 'pass')
        fail_count = sum(1 for test in test_results if test.get('pass_fail', '').lower() == 'fail')
        
        print(f"\n📊 Report Summary:")
        print(f"   Company: {entities.get('company_name', 'Unknown')}")
        print(f"   Sample: {entities.get('subject', 'Unknown')}")
        print(f"   Total Tests: {len(test_results)}")
        print(f"   Tests Passed: {pass_count}")
        print(f"   Tests Failed: {fail_count}")
        print(f"   Signatures Found: {entities.get('actual_signatures', 0)}")
        print(f"   Results Comply: {entities.get('results_comply', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error generating Excel report: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
