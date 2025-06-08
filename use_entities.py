#!/usr/bin/env python
"""
Utility script to use the extracted entities from PDF files
"""

import os
import sys
import json
from pathlib import Path

def print_formatted_report(entities_file):
    """
    Print a formatted report from the extracted entities
    
    Args:
        entities_file (str): Path to the JSON file with extracted entities
    """
    # Load the entities
    with open(entities_file, 'r', encoding='utf-8') as f:
        entities = json.load(f)
    
    # Print header
    print("\n" + "="*80)
    print(f"LABORATORY TEST REPORT SUMMARY - {Path(entities_file).stem.split('_')[0]}")
    print("="*80)
    
    # Print general information
    print(f"\nReference: {entities.get('our_reference', 'Not found')}")
    print(f"Date: {entities.get('date', 'Not found')}")
    print(f"\nSubject: {entities.get('subject', 'Not found')}")
    
    # Print sample information
    print("\nSAMPLE INFORMATION:")
    print(f"  Sample Reference: {entities.get('sample_reference', 'Not found')}")
    print(f"  Sampling Date/Time: {entities.get('sampling_date_time', 'Not found')}")
    print(f"  Catchment: {entities.get('sampling_catchment', 'Not found')}")
    print(f"  Officer In-Charge: {entities.get('sample_officer_incharge', 'Not found')}")
    
    # Print test results
    print("\nTEST RESULTS:")
    test_params = entities.get('test_parameters', [])
    units = entities.get('units', [])
    methods = entities.get('test_methods', [])
    results = entities.get('results', [])
    
    # Calculate column widths
    param_width = max(len("Parameter"), max(len(p) for p in test_params) if test_params else 0) + 2
    unit_width = max(len("Unit"), max(len(u) for u in units) if units else 0) + 2
    method_width = max(len("Test Method"), max(len(m) for m in methods) if methods else 0) + 2
    result_width = max(len("Result"), max(len(r) for r in results) if results else 0) + 2
    
    # Print table header
    print(f"  {'Parameter'.ljust(param_width)}{'Unit'.ljust(unit_width)}{'Test Method'.ljust(method_width)}{'Result'.ljust(result_width)}")
    print(f"  {'-'*param_width}{'-'*unit_width}{'-'*method_width}{'-'*result_width}")
    
    # Print table rows
    for i in range(len(test_params)):
        param = test_params[i] if i < len(test_params) else ""
        unit = units[i] if i < len(units) else ""
        method = methods[i] if i < len(methods) else ""
        result = results[i] if i < len(results) else ""
        print(f"  {param.ljust(param_width)}{unit.ljust(unit_width)}{method.ljust(method_width)}{result.ljust(result_width)}")
    
    print("\n" + "="*80)

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python use_entities.py <path_to_entities_json>")
        return
    
    entities_file = sys.argv[1]
    
    if not os.path.exists(entities_file):
        print(f"Error: File not found - {entities_file}")
        return
    
    print_formatted_report(entities_file)

if __name__ == "__main__":
    main()
