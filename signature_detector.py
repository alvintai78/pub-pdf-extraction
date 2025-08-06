#!/usr/bin/env python
"""
Human Signature Detection Module
Uses Azure Document Intelligence to detect images and Azure OpenAI to classify signatures
"""

import os
import base64
import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
import openai
from PIL import Image
import io

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("Warning: PyMuPDF not available. Image extraction from PDF regions will be limited.")

class SignatureDetector:
    """
    A class to detect human signatures in PDF documents using Azure services.
    
    Uses Azure Document Intelligence to detect images in PDFs and Azure OpenAI
    to classify whether detected images are human signatures.
    """
    
    def __init__(self):
        """Initialize the SignatureDetector with Azure service clients."""
        # Azure Document Intelligence setup
        self.doc_intelligence_key = os.environ.get("AZURE_DOC_INTELLIGENCE_KEY")
        self.doc_intelligence_endpoint = os.environ.get("AZURE_DOC_INTELLIGENCE_ENDPOINT")
        
        # Azure OpenAI setup
        self.openai_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        self.openai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        # Validate environment variables
        self._validate_environment()
        
        # Initialize clients
        self.doc_client = DocumentIntelligenceClient(
            endpoint=self.doc_intelligence_endpoint,
            credential=AzureKeyCredential(self.doc_intelligence_key)
        )
        
        self.openai_client = openai.AzureOpenAI(
            api_key=self.openai_api_key,
            api_version="2023-12-01-preview",
            azure_endpoint=self.openai_endpoint
        )
    
    def _validate_environment(self) -> None:
        """Validate that all required environment variables are set."""
        required_vars = [
            "AZURE_DOC_INTELLIGENCE_KEY",
            "AZURE_DOC_INTELLIGENCE_ENDPOINT", 
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT_NAME"
        ]
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    def detect_images_in_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Detect all images in a PDF using Azure Document Intelligence.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            List[Dict]: List of detected images with metadata
        """
        print(f"Detecting images in PDF: {pdf_path}")
        
        try:
            # Read PDF file
            with open(pdf_path, "rb") as f:
                document_bytes = f.read()
            
            # Analyze the document using the layout model
            poller = self.doc_client.begin_analyze_document(
                "prebuilt-layout",
                body=document_bytes,
                content_type="application/pdf"
            )
            
            # Get results
            result = poller.result()
            
            detected_images = []
            
            # Extract images from the result
            if hasattr(result, 'figures') and result.figures:
                for idx, figure in enumerate(result.figures):
                    image_info = {
                        'figure_id': idx,
                        'page_number': getattr(figure, 'page_number', 'unknown'),
                        'bounding_regions': getattr(figure, 'bounding_regions', []),
                        'caption': getattr(figure, 'caption', None),
                        'confidence': getattr(figure, 'confidence', 0.0)
                    }
                    detected_images.append(image_info)
                    print(f"Detected figure {idx} on page {image_info['page_number']}")
            
            # Also check for embedded images in pages
            if hasattr(result, 'pages') and result.pages:
                for page_idx, page in enumerate(result.pages):
                    # Some document intelligence results may have image elements
                    if hasattr(page, 'images') and page.images:
                        for img_idx, image in enumerate(page.images):
                            image_info = {
                                'image_id': f"page_{page_idx}_img_{img_idx}",
                                'page_number': page_idx + 1,
                                'bounding_box': getattr(image, 'bounding_box', None),
                                'confidence': getattr(image, 'confidence', 0.0)
                            }
                            detected_images.append(image_info)
                            print(f"Detected image on page {page_idx + 1}")
            
            print(f"Total images detected: {len(detected_images)}")
            return detected_images
            
        except Exception as e:
            print(f"Error detecting images in PDF: {str(e)}")
            raise
    
    def extract_image_from_pdf_region(self, pdf_path: str, page_number: int, bounding_box: Dict) -> Optional[bytes]:
        """
        Extract image data from a specific region of a PDF page.
        
        Args:
            pdf_path (str): Path to the PDF file
            page_number (int): Page number (1-indexed)
            bounding_box (Dict): Bounding box coordinates
            
        Returns:
            Optional[bytes]: Image data if extraction is successful
        """
        if not PYMUPDF_AVAILABLE:
            print("PyMuPDF not available. Cannot extract image from PDF region.")
            return None
        
        try:
            # Open the PDF document
            doc = fitz.open(pdf_path)
            
            # Convert to 0-indexed page number  
            if isinstance(page_number, str):
                if page_number == "unknown":
                    page_idx = 0  # Default to first page
                else:
                    try:
                        page_idx = int(page_number) - 1
                    except ValueError:
                        page_idx = 0
            else:
                page_idx = page_number - 1
            
            if page_idx >= len(doc) or page_idx < 0:
                print(f"Page {page_number} not found in PDF")
                doc.close()
                return None
            
            # Get the page
            page = doc[page_idx]
            
            # For now, we'll extract the entire page as we don't have proper
            # bounding box coordinates from Document Intelligence
            # This is a limitation that could be improved with proper coordinate mapping
            
            print(f"Extracting region from page {page_idx + 1} (bounding box processing not fully implemented)")
            
            # Convert the page to a pixmap (image)
            mat = fitz.Matrix(2, 2)  # Scale factor for better quality
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PNG bytes
            img_data = pix.tobytes("png")
            
            doc.close()
            return img_data
            
        except Exception as e:
            print(f"Error extracting image from PDF region: {str(e)}")
            return None
    
    def extract_all_images_from_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Extract all embedded images from a PDF using PyMuPDF.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            List[Dict]: List of extracted images with metadata
        """
        if not PYMUPDF_AVAILABLE:
            print("PyMuPDF not available. Cannot extract embedded images.")
            return []
        
        extracted_images = []
        
        try:
            # Open the PDF document
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get image list from the page
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    # Extract image
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Store image information
                    image_info = {
                        "page_number": page_num + 1,
                        "image_index": img_index,
                        "xref": xref,
                        "extension": image_ext,
                        "image_data": image_bytes,
                        "size": len(image_bytes)
                    }
                    
                    extracted_images.append(image_info)
                    print(f"Extracted image {img_index} from page {page_num + 1} ({image_ext}, {len(image_bytes)} bytes)")
            
            doc.close()
            print(f"Total embedded images extracted: {len(extracted_images)}")
            return extracted_images
            
        except Exception as e:
            print(f"Error extracting embedded images: {str(e)}")
            return []
    
    def classify_image_as_signature(self, image_data: bytes = None, image_path: str = None) -> Dict:
        """
        Use Azure OpenAI to classify whether an image contains a human signature.
        
        Args:
            image_data (bytes, optional): Image data as bytes
            image_path (str, optional): Path to image file
            
        Returns:
            Dict: Classification result with confidence and reasoning
        """
        try:
            # Handle image input
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    image_data = f.read()
            elif image_data is None:
                return {"error": "No image data provided"}
            
            # Convert image to base64 for OpenAI API
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare the prompt for signature detection
            system_message = """
            You are an expert in document analysis and signature detection. 
            Your task is to analyze images and determine if they contain human signatures.
            
            A human signature typically has these characteristics:
            - Handwritten text or marks made by a person (usually their name or initials)
            - Flowing, cursive-like strokes
            - Personal style and unique characteristics
            - Usually appears at the bottom of documents near "signature" labels
            - May include printed name nearby
            - Often irregular and organic in appearance
            - Should represent a person's legal identity mark
            
            IMPORTANT: Be conservative in counting signatures. Only count distinct, separate 
            signature instances. If you see printed names, stamps, or simple initials, 
            be cautious about classifying them as full signatures.
            
            NOT signatures:
            - Printed text or names
            - Logos or stamps (unless they contain handwritten elements)
            - Digital signatures (unless they represent handwritten signatures)
            - Random marks or drawings
            - Form fields or checkboxes
            - Simple initials (unless clearly signature-style)
            """
            
            user_message = """
            Please analyze this image and determine if it contains human signatures.
            
            IMPORTANT: Classify each mark by type and only count "full_signature" types:
            
            **full_signature**: Complete handwritten name or elaborate signature with flowing strokes
            **initials**: Simple initials or short marks (1-3 characters)
            **mark**: Simple marks, dots, or basic strokes that aren't full names
            **stamp**: Printed stamps or seals (not handwritten)
            
            Only count "full_signature" types as actual signatures. Be conservative - if unsure 
            whether something is a full signature or just initials/marks, classify it appropriately.
            
            Provide your response as a JSON object with the following structure:
            {
                "is_signature": true/false,
                "confidence": 0.0-1.0,
                "signature_count": total_number_of_marks_found,
                "full_signature_count": number_of_full_signatures_only,
                "reasoning": "explanation focusing on full signatures vs other marks",
                "signature_characteristics": ["list", "of", "observed", "characteristics"],
                "individual_signatures": [
                    {
                        "position": "description of where this mark is located",
                        "type": "full_signature/initials/mark/stamp",
                        "description": "what this mark looks like",
                        "characteristics": ["specific", "characteristics"]
                    }
                ],
                "alternative_classification": "what this might be if not signatures"
            }
            
            Focus on identifying true full signatures that represent complete names or elaborate 
            personal marks, not just any handwritten element.
            """
            
            # Call Azure OpenAI API with vision capabilities
            response = self.openai_client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": user_message},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            print(f"Signature classification result: {result}")
            return result
            
        except Exception as e:
            print(f"Error classifying image as signature: {str(e)}")
            return {
                "error": str(e),
                "is_signature": False,
                "confidence": 0.0
            }
    
    def detect_signatures_in_pdf(self, pdf_path: str) -> Dict:
        """
        Complete workflow to detect human signatures in a PDF.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            Dict: Complete signature detection results
        """
        print(f"Starting signature detection for: {pdf_path}")
        
        results = {
            "pdf_path": pdf_path,
            "total_images_detected": 0,
            "embedded_images_found": 0,
            "signatures_found": 0,
            "signature_details": [],
            "processing_errors": [],
            "detection_method": "Azure Document Intelligence + Azure OpenAI"
        }
        
        try:
            # Step 1: Extract embedded images using PyMuPDF (prioritize this method)
            embedded_images = []
            if PYMUPDF_AVAILABLE:
                embedded_images = self.extract_all_images_from_pdf(pdf_path)
                results["embedded_images_found"] = len(embedded_images)
            
            # Step 2: Only use Document Intelligence if no embedded images found
            detected_images = []
            if not embedded_images:
                detected_images = self.detect_images_in_pdf(pdf_path)
                results["total_images_detected"] = len(detected_images)
            else:
                print("Using embedded images from PyMuPDF, skipping Document Intelligence image detection")
                results["total_images_detected"] = len(embedded_images)
            
            # Use embedded images if available, otherwise use detected images
            images_to_process = embedded_images if embedded_images else detected_images
            
            if not images_to_process:
                print("No images found in the PDF")
                return results
            
            print(f"Processing {len(images_to_process)} images for signature classification")
            
            # Step 3: Classify each image as signature or not
            for idx, image_info in enumerate(images_to_process):
                try:
                    print(f"Processing image {idx + 1}/{len(images_to_process)}")
                    
                    # Get image data for classification
                    image_data = None
                    
                    if "image_data" in image_info:
                        # This is an embedded image extracted with PyMuPDF
                        image_data = image_info["image_data"]
                    else:
                        # This is from Document Intelligence - try to extract region
                        page_num = image_info.get("page_number", 1)
                        bounding_box = image_info.get("bounding_regions", [])
                        
                        if bounding_box:
                            image_data = self.extract_image_from_pdf_region(
                                pdf_path, page_num, bounding_box[0] if bounding_box else {}
                            )
                    
                    if image_data:
                        # Classify the image
                        classification = self.classify_image_as_signature(image_data=image_data)
                        
                        # Add image info to classification result
                        classification["image_info"] = image_info
                        classification["image_size_bytes"] = len(image_data)
                        
                        # Check if it's classified as a signature
                        if classification.get("is_signature", False):
                            confidence = classification.get("confidence", 0.0)
                            total_signature_count = classification.get("signature_count", 1)
                            individual_sigs = classification.get("individual_signatures", [])
                            
                            # Count only "full_signature" types
                            full_signature_count = 0
                            for sig in individual_sigs:
                                if sig.get("type", "").lower() == "full_signature":
                                    full_signature_count += 1
                            
                            # If no individual signatures specified, use the total count as fallback
                            if not individual_sigs and total_signature_count > 0:
                                full_signature_count = total_signature_count
                            
                            print(f"Found {total_signature_count} total marks, {full_signature_count} full signatures")
                            
                            # Only count as signature if confidence is above threshold AND we have full signatures
                            if confidence >= 0.5 and full_signature_count > 0:  # 50% confidence threshold
                                
                                # Handle multiple signatures in the same image
                                if full_signature_count > 1:
                                    print(f"✓ {full_signature_count} full signatures detected in one image with {confidence:.2f} confidence")
                                    
                                    # Add each full signature separately
                                    full_sig_index = 0
                                    for sig_idx, sig_info in enumerate(individual_sigs):
                                        if sig_info.get("type", "").lower() == "full_signature":
                                            results["signatures_found"] += 1
                                            sig_detail = {
                                                "signature_id": f"sig_{len(results['signature_details']) + 1}",
                                                "page_number": image_info.get("page_number", "unknown"),
                                                "classification": classification,
                                                "confidence": confidence,
                                                "signature_index_in_image": full_sig_index + 1,
                                                "total_full_signatures_in_image": full_signature_count,
                                                "total_marks_in_image": total_signature_count,
                                                "image_source": "embedded" if "image_data" in image_info else "document_intelligence",
                                                "signature_type": "full_signature"
                                            }
                                            
                                            # Add individual signature details
                                            sig_detail["individual_signature_info"] = sig_info
                                            
                                            results["signature_details"].append(sig_detail)
                                            full_sig_index += 1
                                elif full_signature_count == 1:
                                    # Single full signature
                                    results["signatures_found"] += 1
                                    
                                    # Find the full signature in individual_sigs
                                    full_sig_info = None
                                    for sig_info in individual_sigs:
                                        if sig_info.get("type", "").lower() == "full_signature":
                                            full_sig_info = sig_info
                                            break
                                    
                                    sig_detail = {
                                        "signature_id": f"sig_{len(results['signature_details']) + 1}",
                                        "page_number": image_info.get("page_number", "unknown"),
                                        "classification": classification,
                                        "confidence": confidence,
                                        "total_marks_in_image": total_signature_count,
                                        "image_source": "embedded" if "image_data" in image_info else "document_intelligence",
                                        "signature_type": "full_signature"
                                    }
                                    
                                    if full_sig_info:
                                        sig_detail["individual_signature_info"] = full_sig_info
                                    
                                    results["signature_details"].append(sig_detail)
                                    print(f"✓ 1 full signature detected with {confidence:.2f} confidence")
                            elif confidence >= 0.5 and full_signature_count == 0:
                                print(f"✗ Found {total_signature_count} marks but no full signatures - not counted")
                            else:
                                print(f"✗ Low confidence ({confidence:.2f}) - not counted")
                        else:
                            print(f"✗ Not a signature: {classification.get('alternative_classification', 'unknown')}")
                    else:
                        print(f"⚠ Could not extract image data for analysis")
                        
                except Exception as e:
                    error_msg = f"Error processing image {idx + 1}: {str(e)}"
                    print(error_msg)
                    results["processing_errors"].append(error_msg)
            
            print(f"\n=== Signature Detection Summary ===")
            print(f"PDF: {os.path.basename(pdf_path)}")
            print(f"Total images analyzed: {len(images_to_process)}")
            print(f"Signatures found: {results['signatures_found']}")
            print(f"Processing errors: {len(results['processing_errors'])}")
            
            return results
            
        except Exception as e:
            error_msg = f"Error in signature detection workflow: {str(e)}"
            print(error_msg)
            results["processing_errors"].append(error_msg)
            return results
    
    def save_signature_detection_results(self, results: Dict, output_path: str) -> str:
        """
        Save signature detection results to a JSON file.
        
        Args:
            results (Dict): Detection results
            output_path (str): Path to save the results
            
        Returns:
            str: Path to the saved file
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"Signature detection results saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error saving results: {str(e)}")
            raise


def test_signature_detection(pdf_path: str) -> None:
    """
    Test function to demonstrate signature detection functionality.
    
    Args:
        pdf_path (str): Path to the PDF file to test
    """
    print("=== Testing Signature Detection ===")
    
    try:
        # Initialize detector
        detector = SignatureDetector()
        
        # Detect signatures
        results = detector.detect_signatures_in_pdf(pdf_path)
        
        # Print results
        print("\n=== Detection Results ===")
        print(json.dumps(results, indent=2, default=str))
        
        # Save results
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"{Path(pdf_path).stem}_signature_detection.json"
        detector.save_signature_detection_results(results, str(output_file))
        
    except Exception as e:
        print(f"Test failed: {str(e)}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python signature_detector.py <path_to_pdf_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: File not found - {pdf_path}")
        sys.exit(1)
    
    test_signature_detection(pdf_path)
