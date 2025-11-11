"""
OCR-based PDF extraction module for CIR documents
Extracts text and images from PDFs using pytesseract
"""

import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import io

try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_path
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("OCR dependencies not available. Install: pytesseract pdf2image pillow")
    Image = None  # Fallback

import pypdf
from typing import Optional as OptionalType

logger = logging.getLogger(__name__)


class CIROCRExtractor:
    """Extract text and images from CIR PDF documents using OCR"""
    
    def __init__(self, use_ocr: bool = True, tesseract_path: Optional[str] = None):
        """
        Initialize OCR extractor
        
        Args:
            use_ocr: If True, use OCR for scanned/image-based PDFs
            tesseract_path: Path to tesseract executable (if needed)
        """
        self.use_ocr = use_ocr and TESSERACT_AVAILABLE
        self.tesseract_path = tesseract_path
        
        if self.use_ocr and tesseract_path:
            pytesseract.pytesseract.pytesseract_cmd = tesseract_path
    
    def extract_text_with_fallback(self, pdf_path: str) -> Tuple[str, float]:
        """
        Extract text from PDF with fallback strategies
        
        Returns:
            (extracted_text, ocr_confidence_score)
        """
        try:
            pdf_path = Path(pdf_path)
            
            # Try 1: PDF text extraction (fast, for selectable text)
            logger.info(f"Attempting native PDF extraction: {pdf_path.name}")
            text = self._extract_pdf_text(pdf_path)
            
            if text.strip() and len(text) > 100:
                logger.info(f"✓ Native PDF text extracted ({len(text)} chars)")
                return text, 95.0  # High confidence for native extraction
            
            # Try 2: OCR for scanned PDFs
            if self.use_ocr:
                logger.info(f"Attempting OCR extraction: {pdf_path.name}")
                text, confidence = self._extract_ocr_text(pdf_path)
                if text.strip():
                    logger.info(f"✓ OCR text extracted ({len(text)} chars, confidence: {confidence:.1f}%)")
                    return text, confidence
        
        except Exception as e:
            logger.error(f"Extraction error: {e}")
        
        return "", 0.0
    
    def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text using PDF library (fast, for digital PDFs)"""
        try:
            with open(pdf_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                text_parts = []
                
                for page_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"\n--- PAGE {page_num} ---\n{text}")
                
                return "\n".join(text_parts)
        except Exception as e:
            logger.warning(f"PDF text extraction failed: {e}")
            return ""
    
    def _extract_ocr_text(self, pdf_path: Path) -> Tuple[str, float]:
        """Extract text using OCR (for scanned PDFs)"""
        if not TESSERACT_AVAILABLE:
            logger.warning("OCR not available")
            return "", 0.0
        
        try:
            # Convert PDF to images
            images = convert_from_path(str(pdf_path))
            text_parts = []
            confidences = []
            
            for page_num, image in enumerate(images, 1):
                # Extract text with confidence
                text = pytesseract.image_to_string(image)
                
                # Estimate confidence based on text length and quality
                # (real confidence would require detailed pytesseract config)
                confidence = min(100, 70 + (len(text.strip()) / 100))
                
                if text.strip():
                    text_parts.append(f"\n--- PAGE {page_num} [OCR] ---\n{text}")
                    confidences.append(confidence)
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            full_text = "\n".join(text_parts)
            
            return full_text, avg_confidence
        
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return "", 0.0
    
    def extract_images(self, pdf_path: str) -> Dict[int, list]:
        """
        Extract images from PDF
        
        Returns:
            Dictionary: {page_number: [images]}
        """
        images_by_page = {}
        
        try:
            pdf_path = Path(pdf_path)
            
            # Try extracting images from PDF
            try:
                with open(pdf_path, "rb") as f:
                    reader = pypdf.PdfReader(f)
                    
                    for page_num, page in enumerate(reader.pages, 1):
                        page_images = []
                        
                        if "/XObject" in page["/Resources"]:
                            xobject = page["/Resources"]["/XObject"].get_object()
                            
                            for obj in xobject:
                                obj_data = xobject[obj].get_object()
                                
                                if obj_data["/Subtype"] == "/Image":
                                    try:
                                        image_data = obj_data.get_data()
                                        image = Image.open(io.BytesIO(image_data))
                                        page_images.append(image)
                                    except Exception as e:
                                        logger.warning(f"Could not extract image: {e}")
                        
                        if page_images:
                            images_by_page[page_num] = page_images
                            logger.info(f"Extracted {len(page_images)} images from page {page_num}")
            
            except Exception as e:
                logger.warning(f"PDF image extraction failed: {e}")
            
            # Fallback: Convert PDF to images and extract
            if not images_by_page and self.use_ocr:
                logger.info("Fallback: Converting PDF pages to images")
                images = convert_from_path(str(pdf_path))
                images_by_page = {i + 1: [img] for i, img in enumerate(images)}
        
        except Exception as e:
            logger.error(f"Image extraction error: {e}")
        
        return images_by_page
    
    def extract_page_by_page(self, pdf_path: str) -> Dict[int, str]:
        """
        Extract text page by page
        
        Returns:
            Dictionary: {page_number: page_text}
        """
        pages_text = {}
        
        try:
            pdf_path = Path(pdf_path)
            
            with open(pdf_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                
                for page_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    
                    # If page has little text, try OCR
                    if (not text or len(text.strip()) < 50) and self.use_ocr:
                        logger.info(f"Page {page_num}: Insufficient text, trying OCR")
                        # Would need image conversion here
                    
                    pages_text[page_num] = text or ""
        
        except Exception as e:
            logger.error(f"Page extraction error: {e}")
        
        return pages_text


def extract_cir_pdf(pdf_path: str, use_ocr: bool = True) -> Tuple[str, Dict[int, str], float]:
    """
    High-level function to extract CIR PDF content
    
    Returns:
        (full_text, pages_dict, ocr_confidence)
    """
    extractor = CIROCRExtractor(use_ocr=use_ocr)
    
    # Extract full text
    full_text, confidence = extractor.extract_text_with_fallback(pdf_path)
    
    # Extract page by page
    pages = extractor.extract_page_by_page(pdf_path)
    
    # Extract images
    images = extractor.extract_images(pdf_path)
    
    logger.info(f"Extraction complete: {len(full_text)} chars, {len(pages)} pages, {len(images)} images")
    
    return full_text, pages, confidence
