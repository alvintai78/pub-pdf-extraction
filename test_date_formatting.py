#!/usr/bin/env python
"""
Test the date formatting function with various input formats
"""

from pdf_extractor import format_date_time
import json

# Test different date-time formats
test_cases = [
    "12/12/07, 1510 hrs",  # Original format
    "01/01/23, 0830 hrs",  # Morning time
    "31/12/22, 2359 hrs",  # Late night
    "15/06/2023, 1200 hrs",  # 4-digit year, noon
    "5/9/21, 130 hrs",     # Single digit day/month, 3-digit time
    "10/10/10, 10 hrs",    # Short time
    "01/01/1999, 0001 hrs" # Very early morning
]

def test_formatting():
    """Test the date formatting function with various inputs"""
    results = []
    
    for i, test_case in enumerate(test_cases):
        formatted = format_date_time(test_case)
        results.append({
            "original": test_case,
            "formatted": formatted
        })
        print(f"Test {i+1}: '{test_case}' → '{formatted}'")
    
    # Save results to file
    with open('date_format_tests.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to date_format_tests.json")

if __name__ == "__main__":
    test_formatting()
