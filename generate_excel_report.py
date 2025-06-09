#!/usr/bin/env python
"""
Generate Excel Report from Extracted PDF Entities
"""

import os
import json
import sys
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.drawing.image import Image
from datetime import datetime

def load_entities(json_file):
    """Load extracted entities from JSON file"""
    with open(json_file, 'r') as f:
        return json.load(f)

def generate_excel_report(entities, template_path, output_file):
    """Generate Excel report based on extracted entities"""
    # Create a new workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Lab Test Report"
    
    # Define styles
    header_font = Font(bold=True)
    title_font = Font(bold=True, size=14)
    centered = Alignment(horizontal='center', vertical='center')
    left_aligned = Alignment(horizontal='left', vertical='center')
    thin_border = Border(
        left=Side(style='thin'), 
        right=Side(style='thin'), 
        top=Side(style='thin'), 
        bottom=Side(style='thin')
    )
    header_fill = PatternFill(start_color='E6E6E6', end_color='E6E6E6', fill_type='solid')
    
    # Title
    ws['A1'] = "SIES GT Laboratory Test Report"
    ws['A1'].font = title_font
    ws.merge_cells('A1:D1')
    ws['A1'].alignment = centered
    
    # Add space below title
    current_row = 3
    
    # Sample Information Section
    ws.cell(row=current_row, column=1).value = "SAMPLE INFORMATION"
    ws.cell(row=current_row, column=1).font = header_font
    ws.merge_cells(f'A{current_row}:D{current_row}')
    ws.cell(row=current_row, column=1).alignment = centered
    ws.cell(row=current_row, column=1).fill = header_fill
    
    # Add sample information fields
    current_row += 1
    fields = [
        ("Our Reference:", entities.get('our_reference', 'N/A')),
        ("Date:", entities.get('date', 'N/A')),
        ("Subject:", entities.get('subject', 'N/A')),
        ("Sample Reference:", entities.get('sample_reference', 'N/A')),
        ("Sampling Date & Time:", entities.get('sampling_date_time', 'N/A')),
        ("Sample Officer In-charge:", entities.get('sample_officer_incharge', 'N/A')),
        ("Sampling Catchment:", entities.get('sampling_catchment', 'N/A'))
    ]
    
    for label, value in fields:
        ws.cell(row=current_row, column=1).value = label
        ws.cell(row=current_row, column=1).font = Font(bold=True)
        ws.cell(row=current_row, column=1).alignment = left_aligned
        
        ws.cell(row=current_row, column=2).value = value
        ws.merge_cells(f'B{current_row}:D{current_row}')
        ws.cell(row=current_row, column=2).alignment = left_aligned
        
        current_row += 1
    
    # Add a blank row for spacing
    current_row += 1
    
    # Test Results Section
    ws.cell(row=current_row, column=1).value = "TEST RESULTS"
    ws.cell(row=current_row, column=1).font = header_font
    ws.merge_cells(f'A{current_row}:D{current_row}')
    ws.cell(row=current_row, column=1).alignment = centered
    ws.cell(row=current_row, column=1).fill = header_fill
    
    # Test results header
    current_row += 1
    header_row = current_row
    headers = ["Parameter", "Unit", "Method", "Result"]
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=header_row, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.alignment = centered
        cell.border = thin_border
    
    # Test results data
    current_row += 1
    test_parameters = entities.get('test_parameters', [])
    units = entities.get('units', [])
    test_methods = entities.get('test_methods', [])
    results = entities.get('results', [])
    
    # Make sure all lists have the same length
    max_length = max(len(test_parameters), len(units), len(test_methods), len(results))
    test_parameters = (test_parameters + [''] * max_length)[:max_length]
    units = (units + [''] * max_length)[:max_length]
    test_methods = (test_methods + [''] * max_length)[:max_length]
    results = (results + [''] * max_length)[:max_length]
    
    # Add the test results
    data_rows = []
    for param, unit, method, result in zip(test_parameters, units, test_methods, results):
        row = current_row
        data_rows.append(row)
        
        ws.cell(row=row, column=1).value = param
        ws.cell(row=row, column=1).alignment = left_aligned
        ws.cell(row=row, column=1).border = thin_border
        
        ws.cell(row=row, column=2).value = unit
        ws.cell(row=row, column=2).alignment = centered
        ws.cell(row=row, column=2).border = thin_border
        
        ws.cell(row=row, column=3).value = method
        ws.cell(row=row, column=3).alignment = centered
        ws.cell(row=row, column=3).border = thin_border
        
        ws.cell(row=row, column=4).value = result
        ws.cell(row=row, column=4).alignment = centered
        ws.cell(row=row, column=4).border = thin_border
        
        current_row += 1
    
    # Add a blank row for spacing
    current_row += 2
    
    # Add footer
    ws.cell(row=current_row, column=1).value = "Generated by:"
    ws.cell(row=current_row, column=1).font = Font(bold=True)
    ws.cell(row=current_row, column=2).value = "PDF Extraction System"
    
    current_row += 1
    ws.cell(row=current_row, column=1).value = "Date:"
    ws.cell(row=current_row, column=1).font = Font(bold=True)
    ws.cell(row=current_row, column=2).value = datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")
    
    # Set column widths
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 30
    ws.column_dimensions['D'].width = 15
    
    # Save the workbook
    wb.save(output_file)
    print(f"Excel report generated: {output_file}")
    return output_file

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python generate_excel_report.py <entities_json_file> [output_excel_file]")
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
        output_file = Path(entities_json).stem.replace("_entities", "") + "_report.xlsx"
    
    # Generate the report
    try:
        entities = load_entities(entities_json)
        generate_excel_report(entities, None, output_file)
    except Exception as e:
        print(f"Error generating Excel report: {str(e)}")

if __name__ == "__main__":
    main()
