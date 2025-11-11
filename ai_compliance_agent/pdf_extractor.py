#!/usr/bin/env python3
"""
Comprehensive PDF extraction and detailed summarization module.

Extracts ALL details from PDF and creates a structured summary.
"""

from pathlib import Path
from typing import Dict, List, Any
import logging

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


class PDFDetailExtractor:
    """Extract comprehensive details from PDF files."""
    
    @staticmethod
    def extract_all_details(pdf_path: Path | str) -> Dict[str, Any]:
        """Extract ALL details from a PDF file.
        
        Returns dictionary with:
        - full_text: Complete text from all pages
        - page_count: Number of pages
        - pages: List of page contents
        - metadata: PDF metadata
        - word_count: Total words
        - sections: Identified sections/headers
        - key_points: Extracted key information
        """
        path = Path(pdf_path).expanduser().resolve()
        
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")
        
        logger.info(f"Extracting details from: {path.name}")
        
        reader = PdfReader(str(path))
        
        # Extract metadata
        metadata = {
            "filename": path.name,
            "file_path": str(path),
            "file_size_kb": path.stat().st_size / 1024,
            "page_count": len(reader.pages),
            "created": None,
            "modified": None,
            "author": None,
            "title": None,
        }
        
        if reader.metadata:
            metadata.update({
                "created": reader.metadata.get("/CreationDate"),
                "modified": reader.metadata.get("/ModDate"),
                "author": reader.metadata.get("/Author"),
                "title": reader.metadata.get("/Title"),
            })
        
        # Extract text from all pages
        pages = []
        full_text_parts = []
        
        for page_num, page in enumerate(reader.pages, 1):
            try:
                page_text = page.extract_text() or ""
            except Exception as e:
                logger.warning(f"Failed to extract page {page_num}: {e}")
                page_text = ""
            
            pages.append({
                "page_number": page_num,
                "text": page_text.strip(),
                "char_count": len(page_text),
                "word_count": len(page_text.split()),
            })
            
            full_text_parts.append(page_text.strip())
        
        full_text = "\n\n--- PAGE BREAK ---\n\n".join(full_text_parts)
        
        # Calculate statistics
        word_count = len(full_text.split())
        
        # Extract sections (look for typical section markers)
        sections = PDFDetailExtractor._extract_sections(full_text)
        
        # Extract key information
        key_points = PDFDetailExtractor._extract_key_points(full_text)
        
        return {
            "metadata": metadata,
            "full_text": full_text,
            "pages": pages,
            "word_count": word_count,
            "sections": sections,
            "key_points": key_points,
        }
    
    @staticmethod
    def _extract_sections(text: str) -> List[Dict[str, str]]:
        """Extract sections and headers from text."""
        sections = []
        lines = text.split("\n")
        
        current_section = None
        current_content = []
        
        for line in lines:
            stripped = line.strip()
            
            # Detect section headers (lines that are short and possibly in caps)
            if (len(stripped) < 100 and 
                stripped and 
                (stripped.isupper() or 
                 stripped.startswith("#") or
                 stripped.startswith("•") or
                 any(c.isupper() for c in stripped[:3]))):
                
                # Save previous section
                if current_section:
                    sections.append({
                        "title": current_section,
                        "content": "\n".join(current_content).strip(),
                    })
                
                current_section = stripped
                current_content = []
            else:
                if current_section:
                    current_content.append(stripped)
        
        # Save last section
        if current_section:
            sections.append({
                "title": current_section,
                "content": "\n".join(current_content).strip(),
            })
        
        return sections[:20]  # Limit to first 20 sections
    
    @staticmethod
    def _extract_key_points(text: str) -> List[str]:
        """Extract key points and main topics."""
        key_points = []
        lines = text.split("\n")
        
        for line in lines:
            stripped = line.strip()
            
            # Look for bullet points, numbered items
            if (stripped and 
                (stripped.startswith("•") or 
                 stripped.startswith("-") or 
                 stripped.startswith("*") or
                 (len(stripped) > 0 and stripped[0].isdigit() and "." in stripped[:3]))):
                
                key_points.append(stripped)
        
        return key_points[:30]  # Limit to first 30 key points
    
    @staticmethod
    def create_summary(details: Dict[str, Any]) -> str:
        """Create a comprehensive summary from extracted details."""
        
        summary_lines = []
        
        # Header
        summary_lines.append("=" * 80)
        summary_lines.append("📄 COMPREHENSIVE PDF SUMMARY")
        summary_lines.append("=" * 80)
        summary_lines.append("")
        
        # Metadata
        metadata = details.get("metadata", {})
        summary_lines.append("📋 DOCUMENT METADATA")
        summary_lines.append("-" * 80)
        summary_lines.append(f"Filename:      {metadata.get('filename', 'N/A')}")
        summary_lines.append(f"File Size:     {metadata.get('file_size_kb', 0):.1f} KB")
        summary_lines.append(f"Pages:         {metadata.get('page_count', 0)}")
        summary_lines.append(f"Author:        {metadata.get('author', 'N/A')}")
        summary_lines.append(f"Title:         {metadata.get('title', 'N/A')}")
        summary_lines.append("")
        
        # Content Statistics
        word_count = details.get("word_count", 0)
        pages = details.get("pages", [])
        summary_lines.append("📊 CONTENT STATISTICS")
        summary_lines.append("-" * 80)
        summary_lines.append(f"Total Words:   {word_count}")
        summary_lines.append(f"Avg per Page:  {word_count // len(pages) if pages else 0}")
        summary_lines.append(f"Character Avg: {sum(p['char_count'] for p in pages) // len(pages) if pages else 0} per page")
        summary_lines.append("")
        
        # Page Breakdown
        summary_lines.append("📄 PAGE BREAKDOWN")
        summary_lines.append("-" * 80)
        for page in pages[:10]:  # Show first 10 pages
            summary_lines.append(f"Page {page['page_number']:2d}: {page['word_count']:5d} words ({page['char_count']:6d} chars)")
        if len(pages) > 10:
            summary_lines.append(f"... and {len(pages) - 10} more pages")
        summary_lines.append("")
        
        # Sections
        sections = details.get("sections", [])
        if sections:
            summary_lines.append("🏷️  DOCUMENT SECTIONS IDENTIFIED")
            summary_lines.append("-" * 80)
            for i, section in enumerate(sections[:15], 1):
                summary_lines.append(f"{i}. {section['title']}")
                # Show first 100 chars of content
                content = section['content'][:100].replace("\n", " ")
                if section['content']:
                    summary_lines.append(f"   └─ {content}...")
            summary_lines.append("")
        
        # Key Points
        key_points = details.get("key_points", [])
        if key_points:
            summary_lines.append("🔑 KEY POINTS EXTRACTED")
            summary_lines.append("-" * 80)
            for i, point in enumerate(key_points[:20], 1):
                # Clean up and truncate
                clean_point = point.replace("•", "").replace("-", "").strip()
                if len(clean_point) > 100:
                    clean_point = clean_point[:100] + "..."
                summary_lines.append(f"{i}. {clean_point}")
            summary_lines.append("")
        
        # Full Text Preview
        summary_lines.append("📝 FULL DOCUMENT TEXT (First 2000 chars)")
        summary_lines.append("-" * 80)
        full_text = details.get("full_text", "")
        preview = full_text[:2000] + ("..." if len(full_text) > 2000 else "")
        summary_lines.append(preview)
        summary_lines.append("")
        
        summary_lines.append("=" * 80)
        
        return "\n".join(summary_lines)


def extract_and_summarize_pdf(pdf_path: Path | str) -> tuple[Dict[str, Any], str]:
    """Extract all details from PDF and create comprehensive summary.
    
    Returns:
        (details_dict, summary_string)
    """
    extractor = PDFDetailExtractor()
    details = extractor.extract_all_details(pdf_path)
    summary = extractor.create_summary(details)
    return details, summary


if __name__ == "__main__":
    # Test
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <pdf_path>")
        sys.exit(1)
    
    pdf_file = Path(sys.argv[1])
    
    if not pdf_file.exists():
        print(f"❌ File not found: {pdf_file}")
        sys.exit(1)
    
    print("\n⏳ Extracting details from PDF...")
    details, summary = extract_and_summarize_pdf(pdf_file)
    
    print(summary)
    
    # Also save to file
    output_file = pdf_file.with_suffix(".summary.txt")
    with open(output_file, "w") as f:
        f.write(summary)
    
    print(f"\n💾 Summary saved to: {output_file}")
