#!/usr/bin/env python
"""
Demo script to test signature detection functionality
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from signature_detector import SignatureDetector

def main():
    """Demo the signature detection functionality"""
    # Load environment variables
    load_dotenv()
    
    print("=== PDF Signature Detection Demo ===\n")
    
    # Check if a PDF path is provided
    if len(sys.argv) < 2:
        # Use a sample PDF from the workspace if available
        sample_pdfs = [
            "EN13945-4.pdf",
            "Sample1_low_bromide_salt.pdf", 
            "Sample2_liquid_oxygen.pdf"
        ]
        
        pdf_path = None
        for sample in sample_pdfs:
            if os.path.exists(sample):
                pdf_path = sample
                print(f"Using sample PDF: {pdf_path}")
                break
        
        if not pdf_path:
            print("Usage: python demo_signature_detection.py <path_to_pdf_file>")
            print("\nAvailable sample files in workspace:")
            for sample in sample_pdfs:
                status = "✓" if os.path.exists(sample) else "✗"
                print(f"  {status} {sample}")
            return
    else:
        pdf_path = sys.argv[1]
        
        if not os.path.exists(pdf_path):
            print(f"Error: File not found - {pdf_path}")
            return
    
    try:
        # Initialize the signature detector
        print("Initializing signature detector...")
        detector = SignatureDetector()
        
        # Run signature detection
        print(f"Analyzing PDF: {pdf_path}")
        print("-" * 50)
        
        results = detector.detect_signatures_in_pdf(pdf_path)
        
        # Display results
        print("\n" + "=" * 50)
        print("SIGNATURE DETECTION RESULTS")
        print("=" * 50)
        
        print(f"PDF File: {os.path.basename(pdf_path)}")
        print(f"Detection Method: {results.get('detection_method', 'Standard')}")
        print(f"Total Images Found: {results['total_images_detected']}")
        
        if "embedded_images_found" in results:
            print(f"Embedded Images: {results['embedded_images_found']}")
        
        print(f"Signatures Detected: {results['signatures_found']}")
        
        if results['signature_details']:
            print("\nSignature Details:")
            for i, sig in enumerate(results['signature_details'], 1):
                print(f"\n  Signature {i}:")
                print(f"    Page: {sig.get('page_number', 'unknown')}")
                print(f"    Confidence: {sig.get('confidence', 0.0):.2%}")
                
                classification = sig.get('classification', {})
                reasoning = classification.get('reasoning', 'N/A')
                if len(reasoning) > 100:
                    reasoning = reasoning[:97] + "..."
                print(f"    Reasoning: {reasoning}")
                
                characteristics = classification.get('signature_characteristics', [])
                if characteristics:
                    print(f"    Characteristics: {', '.join(characteristics[:3])}")
        
        if results['processing_errors']:
            print(f"\nProcessing Errors ({len(results['processing_errors'])}):")
            for i, error in enumerate(results['processing_errors'], 1):
                print(f"  {i}. {error}")
        
        # Save results
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{Path(pdf_path).stem}_signature_detection_demo.json"
        detector.save_signature_detection_results(results, str(output_file))
        
        print(f"\nDetailed results saved to: {output_file}")
        
        # Summary
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        
        if results['signatures_found'] > 0:
            print(f"✓ Found {results['signatures_found']} signature(s) in the PDF")
            print("  Consider reviewing the signature details above for accuracy")
        else:
            print("✗ No signatures detected in this PDF")
            if results['total_images_detected'] > 0:
                print("  Images were found but none were classified as signatures")
            else:
                print("  No images were detected in the PDF")
        
        if results['processing_errors']:
            print(f"⚠ {len(results['processing_errors'])} error(s) occurred during processing")
            print("  Check the error details above and your Azure service configuration")
        
        print("\nDemo completed successfully!")
        
    except Exception as e:
        print(f"\nError during demo: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check that your environment variables are set correctly")
        print("2. Verify Azure Document Intelligence and OpenAI services are accessible")
        print("3. Ensure the PDF file is not corrupted")
        print("4. Check that you have the required Python packages installed")

if __name__ == "__main__":
    main()
