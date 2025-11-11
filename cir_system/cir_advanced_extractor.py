"""
Advanced Dynamic CIR Metadata Extractor
Extracts ALL available metadata from CIR documents using pattern matching and NLP
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CIRMetadata:
    """Complete dynamic metadata extracted from CIR"""
    all_fields: Dict[str, Any] = field(default_factory=dict)
    field_sources: Dict[str, str] = field(default_factory=dict)  # Track where each field came from
    
    def add_field(self, name: str, value: Any, source: str = "extracted"):
        """Add a metadata field"""
        if value and str(value).strip():
            self.all_fields[name] = value
            self.field_sources[name] = source
    
    def get_all_fields(self) -> Dict[str, Any]:
        """Get all extracted fields"""
        return self.all_fields
    
    def get_field_names(self) -> List[str]:
        """Get all field names"""
        return sorted(list(self.all_fields.keys()))


class AdvancedCIRExtractor:
    """Dynamically extract ALL metadata from CIR documents"""
    
    def __init__(self):
        # Define extraction patterns
        self.patterns = self._build_extraction_patterns()
    
    def extract_metadata(self, text: str) -> CIRMetadata:
        """
        Extract ALL available metadata from CIR text
        
        Args:
            text: Full CIR document text
            
        Returns:
            CIRMetadata with all extracted fields
        """
        metadata = CIRMetadata()
        
        logger.info("Extracting CIR metadata dynamically")
        
        # Extract using predefined patterns
        for field_name, patterns in self.patterns.items():
            value = self._extract_field(text, patterns)
            if value:
                metadata.add_field(field_name, value, "pattern_matching")
        
        # Extract additional fields using key-value pairs
        additional_fields = self._extract_key_value_pairs(text)
        for field, value in additional_fields.items():
            if field not in metadata.all_fields:
                metadata.add_field(field, value, "key_value_extraction")
        
        # Extract list fields
        list_fields = self._extract_lists(text)
        for field, values in list_fields.items():
            if values:
                metadata.add_field(field, values, "list_extraction")
        
        # Extract numeric fields
        numeric_fields = self._extract_numeric_fields(text)
        for field, value in numeric_fields.items():
            if field not in metadata.all_fields:
                metadata.add_field(field, value, "numeric_extraction")
        
        # Extract dates
        dates = self._extract_dates(text)
        for date_field, date_value in dates.items():
            metadata.add_field(date_field, date_value, "date_extraction")
        
        logger.info(f"Extracted {len(metadata.all_fields)} metadata fields")
        
        return metadata
    
    def _build_extraction_patterns(self) -> Dict[str, List[str]]:
        """Build extraction patterns for common CIR fields"""
        return {
            # Identifiers
            "CIR ID": [
                r"CIR[:\s]+([A-Z0-9\-]+)",
                r"CIR Number[:\s]+([A-Z0-9\-]+)",
                r"Case[:\s]+([A-Z0-9\-]+)"
            ],
            "Report Type": [
                r"Report Type[:\s]+([^\n]+)",
                r"Type[:\s]+([^\n]+)",
                r"(?:Service|Technical|Incident)\s+Report"
            ],
            "Service Report Number": [
                r"Service Report[:\s]+([A-Z0-9\-]+)",
                r"Report Number[:\s]+([A-Z0-9\-]+)",
                r"SR#[:\s]+([A-Z0-9\-]+)"
            ],
            "Reason for Service": [
                r"Reason[:\s]+([^\n.]+)",
                r"Reason for Service[:\s]+([^\n.]+)",
                r"Service Reason[:\s]+([^\n.]+)"
            ],
            "Turbine ID": [
                r"Turbine[:\s]+([A-Z0-9\-]+)",
                r"Turbine ID[:\s]+([A-Z0-9\-]+)",
                r"WTG ID[:\s]+([A-Z0-9\-]+)",
                r"Turbine (?:Number|Identifier)[:\s]+([A-Z0-9\-]+)"
            ],
            "WTG ID": [
                r"WTG[:\s]+([A-Z0-9\-]+)",
                r"WTG ID[:\s]+([A-Z0-9\-]+)"
            ],
            "Turbine Type": [
                r"Turbine Type[:\s]+([^\n]+)",
                r"Model[:\s]+([^\n]+)",
                r"Platform[:\s]+([^\n]+)"
            ],
            "MK Version": [
                r"MK[:\s]+([0-9\.]+)",
                r"Version[:\s]+([0-9\.]+)",
                r"Platform Version[:\s]+([0-9\.]+)"
            ],
            "Country": [
                r"Country[:\s]+([^\n]+)",
                r"Location[:\s]+([^\n,]+),?\s*([A-Z]{2})"
            ],
            "Site Name": [
                r"Site[:\s]+([^\n]+)",
                r"Site Name[:\s]+([^\n]+)",
                r"Wind Farm[:\s]+([^\n]+)"
            ],
            "Component Type": [
                r"Component[:\s]+([^\n]+)",
                r"Component Type[:\s]+([^\n]+)",
                r"Failed Component[:\s]+([^\n]+)"
            ],
            "Manufacturer": [
                r"Manufacturer[:\s]+([^\n]+)",
                r"OEM[:\s]+([^\n]+)",
                r"Supplier[:\s]+([^\n]+)"
            ],
            "Field Observations": [
                r"Observations?[:\s]+([^\n.]+(?:\n[^\n]*?){0,3})",
                r"Findings?[:\s]+([^\n.]+(?:\n[^\n]*?){0,3})",
                r"Technical Findings[:\s]+([^\n.]+)"
            ],
            "Service Date": [
                r"Service Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
                r"Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})"
            ],
            "Technician": [
                r"Technician[:\s]+([^\n]+)",
                r"Performed By[:\s]+([^\n]+)",
                r"Inspector[:\s]+([^\n]+)"
            ],
            "Status": [
                r"Status[:\s]+([^\n]+)",
                r"Result[:\s]+([^\n]+)",
                r"(?:GO|NO-GO|PASS|FAIL)"
            ]
        }
    
    def _extract_field(self, text: str, patterns: List[str]) -> Optional[str]:
        """Extract a field using multiple patterns"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                # Get last group (most likely the value)
                for group in reversed(match.groups()):
                    if group:
                        return group.strip()
                return match.group(0).strip()
        return None
    
    def _extract_key_value_pairs(self, text: str) -> Dict[str, str]:
        """Extract key-value pairs from text"""
        pairs = {}
        
        # Look for patterns like "Key: Value" or "Key: Value\n"
        pattern = r'([A-Za-z\s\-/]+?)[:\s]+([^\n]+?)(?:\n|$)'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            key = match.group(1).strip()
            value = match.group(2).strip()
            
            # Filter out obvious non-field lines
            if (len(key) > 2 and len(key) < 100 and
                len(value) > 2 and len(value) < 200 and
                not key.startswith(('The', 'This', 'That', 'These'))):
                
                # Normalize key
                normalized_key = self._normalize_key(key)
                pairs[normalized_key] = value
        
        return pairs
    
    def _extract_lists(self, text: str) -> Dict[str, List[str]]:
        """Extract list-type fields"""
        lists = {}
        
        # Look for bulleted or numbered lists
        bullet_pattern = r'(?:^|\n)[\s]*[-•*]\s+([^\n]+)'
        bullets = re.findall(bullet_pattern, text, re.MULTILINE)
        if bullets and len(bullets) > 1:
            lists["Observations"] = bullets[:10]  # First 10 items
        
        # Look for numbered lists
        numbered_pattern = r'(?:^|\n)[\s]*(\d+)[.)\-:]\s+([^\n]+)'
        numbered = re.findall(numbered_pattern, text, re.MULTILINE)
        if numbered:
            lists["Steps/Items"] = [item[1] for item in numbered[:10]]
        
        return lists
    
    def _extract_numeric_fields(self, text: str) -> Dict[str, Any]:
        """Extract numeric data"""
        numeric = {}
        
        # Serial numbers, part numbers, etc.
        numeric_patterns = {
            "Serial Number": r"Serial[:\s]+([A-Z0-9\-]+)",
            "Part Number": r"Part[:\s]+([A-Z0-9\-]+)",
            "Lot Number": r"Lot[:\s]+([A-Z0-9\-]+)",
            "Test Result Value": r"Result[:\s]+(\d+[.,]\d+)",
            "Hours of Operation": r"(?:Hours|Operating Hours)[:\s]+(\d+)"
        }
        
        for field_name, pattern in numeric_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                numeric[field_name] = match.group(1)
        
        return numeric
    
    def _extract_dates(self, text: str) -> Dict[str, str]:
        """Extract date fields"""
        dates = {}
        
        date_keywords = ["received", "shipped", "created", "completed", "inspection", "test"]
        date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{1,2}-\d{1,2})'
        
        matches = re.finditer(date_pattern, text)
        date_count = 0
        for match in matches:
            date_count += 1
            dates[f"Date {date_count}"] = match.group(1)
        
        return dates
    
    def _normalize_key(self, key: str) -> str:
        """Normalize key names"""
        # Convert to title case and remove extra spaces
        key = re.sub(r'\s+', ' ', key.strip())
        key = re.sub(r'[:\-_]', ' ', key)
        key = ' '.join(word.capitalize() for word in key.split())
        return key
    
    def get_metadata_table_headers(self, metadata: CIRMetadata) -> List[str]:
        """Get headers for metadata table"""
        # Priority order for headers
        priority_fields = [
            "CIR ID", "Report Type", "Service Report Number",
            "Reason for Service", "Turbine ID", "WTG ID",
            "Turbine Type", "MK Version", "Country", "Site Name",
            "Component Type", "Manufacturer", "Technician",
            "Service Date", "Field Observations", "Status"
        ]
        
        headers = []
        
        # Add priority fields first
        for field in priority_fields:
            if field in metadata.all_fields:
                headers.append(field)
        
        # Add remaining fields
        for field in metadata.get_field_names():
            if field not in headers:
                headers.append(field)
        
        return headers
