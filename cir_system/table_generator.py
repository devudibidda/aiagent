"""
Dynamic Table Generator
Creates flexible tables based on actual extracted content
"""

import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)


class DynamicTableGenerator:
    """Generate flexible tables with columns based on actual content"""
    
    def __init__(self):
        self.priority_metadata_fields = [
            "CIR ID", "Report Type", "Service Report Number",
            "Turbine ID", "WTG ID", "Turbine Type",
            "Component Type", "Manufacturer",
            "Reason for Service", "Service Date"
        ]
        
        self.priority_requirement_fields = [
            "Status", "Confidence", "Evidence Found", "Comments"
        ]
    
    def generate_compliance_table(
        self,
        cir_metadata_list: List[Dict[str, Any]],
        compliance_evidence_list: List[List[Dict[str, Any]]],
        cim_requirements: List[Dict[str, Any]] = None,
        max_width: int = 120
    ) -> str:
        """
        Generate text-based compliance summary table
        
        Args:
            cir_metadata_list: List of CIR metadata dictionaries
            compliance_evidence_list: List of compliance evidence per CIR
            cim_requirements: CIM requirements reference
            max_width: Maximum table width for formatting
        
        Returns:
            Formatted text table
        """
        
        # Build dynamic headers
        headers = self._build_headers(cir_metadata_list, cim_requirements)
        
        # Format header row
        table_lines = []
        table_lines.append(self._format_header_row(headers, max_width))
        table_lines.append("-" * max_width)
        
        # Format data rows
        for i, (cir_meta, evidence) in enumerate(zip(cir_metadata_list, compliance_evidence_list)):
            row_data = self._build_row_data(cir_meta, evidence, headers, cim_requirements)
            table_lines.append(self._format_data_row(row_data, headers, max_width))
        
        return "\n".join(table_lines)
    
    def generate_evidence_table(
        self,
        compliance_evidence_list: List[List[Dict[str, Any]]],
        max_width: int = 150
    ) -> str:
        """
        Generate detailed evidence assessment table
        
        Args:
            compliance_evidence_list: Compliance evidence per requirement
            max_width: Maximum table width
        
        Returns:
            Formatted evidence table
        """
        
        headers = [
            "CIR", "Req ID", "Requirement", "Status",
            "Evidence", "Confidence", "Comments"
        ]
        
        table_lines = []
        table_lines.append(self._format_header_row(headers, max_width))
        table_lines.append("-" * max_width)
        
        for cir_idx, cir_evidence in enumerate(compliance_evidence_list):
            for evidence in cir_evidence:
                row_data = {
                    "CIR": f"CIR-{cir_idx + 1}",
                    "Req ID": evidence.get("Requirement ID", ""),
                    "Requirement": evidence.get("Requirement", "")[:40],
                    "Status": evidence.get("Status", ""),
                    "Evidence": evidence.get("Evidence Found", "")[:30],
                    "Confidence": evidence.get("Confidence", ""),
                    "Comments": evidence.get("Comments", "")[:30]
                }
                
                table_lines.append(self._format_data_row(row_data, headers, max_width))
        
        return "\n".join(table_lines)
    
    def generate_metadata_table(
        self,
        cir_metadata: Dict[str, Any],
        max_width: int = 100
    ) -> str:
        """
        Generate detailed metadata table for a single CIR
        
        Args:
            cir_metadata: CIR metadata dictionary
            max_width: Maximum table width
        
        Returns:
            Formatted metadata table
        """
        
        # Prioritize fields for display
        fields = self._prioritize_fields(cir_metadata.keys())
        
        table_lines = []
        table_lines.append("=" * max_width)
        table_lines.append("METADATA DETAILS")
        table_lines.append("=" * max_width)
        
        for field in fields:
            value = cir_metadata.get(field, "N/A")
            
            # Format long values
            if isinstance(value, str) and len(value) > 60:
                # Word wrap long text
                words = value.split()
                lines = []
                current_line = []
                
                for word in words:
                    current_line.append(word)
                    if len(" ".join(current_line)) > 60:
                        lines.append(" ".join(current_line[:-1]))
                        current_line = [word]
                
                if current_line:
                    lines.append(" ".join(current_line))
                
                value = " ".join(lines)
            
            table_lines.append(f"{field:.<35} {str(value):<60}")
        
        table_lines.append("=" * max_width)
        
        return "\n".join(table_lines)
    
    def generate_requirement_summary(
        self,
        cim_requirements: List[Dict[str, Any]],
        max_width: int = 120
    ) -> str:
        """
        Generate summary table of CIM requirements
        
        Args:
            cim_requirements: List of CIM requirements
            max_width: Maximum table width
        
        Returns:
            Formatted requirements table
        """
        
        headers = ["Req ID", "Type", "Severity", "Components", "Title"]
        
        table_lines = []
        table_lines.append(self._format_header_row(headers, max_width))
        table_lines.append("-" * max_width)
        
        for req in cim_requirements:
            row_data = {
                "Req ID": req.get("id", ""),
                "Type": req.get("type", "")[:12],
                "Severity": req.get("severity", ""),
                "Components": ", ".join(req.get("components", []))[:20],
                "Title": req.get("title", "")[:40]
            }
            
            table_lines.append(self._format_data_row(row_data, headers, max_width))
        
        return "\n".join(table_lines)
    
    def generate_summary_statistics(
        self,
        compliance_summary: Dict[str, Any]
    ) -> str:
        """
        Generate summary statistics box
        
        Args:
            compliance_summary: Compliance summary from assessment
        
        Returns:
            Formatted summary box
        """
        
        lines = []
        lines.append("╔" + "═" * 48 + "╗")
        lines.append("║  COMPLIANCE ANALYSIS SUMMARY" + " " * 20 + "║")
        lines.append("╠" + "═" * 48 + "╣")
        
        lines.append(f"║  Compliance Score: {compliance_summary.get('compliance_score', 0):.1f}%" + " " * 20 + "║")
        lines.append(f"║  GO/NO-GO: {compliance_summary.get('go_nogo', 'N/A')}" + " " * 33 + "║")
        
        lines.append("╠" + "═" * 48 + "╣")
        lines.append(f"║  Total Requirements: {compliance_summary.get('total_requirements', 0)}" + " " * 22 + "║")
        lines.append(f"║  ✓ Met: {compliance_summary.get('met', 0)}" + " " * 37 + "║")
        lines.append(f"║  ≈ Partial: {compliance_summary.get('partial', 0)}" + " " * 32 + "║")
        lines.append(f"║  ✗ Not Met: {compliance_summary.get('not_met', 0)}" + " " * 31 + "║")
        
        lines.append("╚" + "═" * 48 + "╝")
        
        return "\n".join(lines)
    
    def _build_headers(
        self,
        cir_metadata_list: List[Dict[str, Any]],
        cim_requirements: List[Dict[str, Any]] = None
    ) -> List[str]:
        """Build dynamic header list"""
        
        headers = []
        
        # Collect all unique metadata fields
        all_fields: Set[str] = set()
        for cir_meta in cir_metadata_list:
            all_fields.update(cir_meta.keys())
        
        # Add prioritized fields first
        for field in self.priority_metadata_fields:
            if field in all_fields:
                headers.append(field)
                all_fields.discard(field)
        
        # Add remaining fields
        for field in sorted(all_fields):
            headers.append(field)
        
        # Add compliance columns
        headers.extend(["Compliance Score", "GO/NO-GO"])
        
        return headers
    
    def _build_row_data(
        self,
        cir_meta: Dict[str, Any],
        evidence: List[Dict[str, Any]],
        headers: List[str],
        cim_requirements: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build row data from CIR metadata and evidence"""
        
        row_data = {}
        
        for header in headers:
            if header in cir_meta:
                row_data[header] = cir_meta[header]
            elif header == "Compliance Score":
                # Calculate from evidence
                scores = []
                for ev in evidence:
                    confidence = ev.get("Confidence", "0%").rstrip("%")
                    try:
                        scores.append(float(confidence))
                    except ValueError:
                        pass
                
                if scores:
                    avg_score = sum(scores) / len(scores)
                    row_data[header] = f"{avg_score:.1f}%"
                else:
                    row_data[header] = "N/A"
            
            elif header == "GO/NO-GO":
                # Determine from compliance score
                score_str = row_data.get("Compliance Score", "0%")
                score = float(score_str.rstrip("%")) if "%" in score_str else 0
                row_data[header] = "GO" if score >= 85 else "NO-GO"
            
            else:
                row_data[header] = "N/A"
        
        return row_data
    
    def _prioritize_fields(self, fields: Any) -> List[str]:
        """Sort fields by priority"""
        
        field_list = list(fields) if not isinstance(fields, list) else fields
        
        prioritized = []
        
        # Add priority fields first
        for field in self.priority_metadata_fields:
            if field in field_list:
                prioritized.append(field)
        
        # Add remaining fields
        for field in sorted(field_list):
            if field not in prioritized:
                prioritized.append(field)
        
        return prioritized
    
    def _format_header_row(self, headers: List[str], max_width: int) -> str:
        """Format header row with alignment"""
        
        # Calculate column widths
        col_widths = self._calculate_column_widths(headers, max_width)
        
        cells = []
        for header, width in zip(headers, col_widths):
            cells.append(header[:width].ljust(width))
        
        return " | ".join(cells)
    
    def _format_data_row(
        self,
        row_data: Dict[str, Any],
        headers: List[str],
        max_width: int
    ) -> str:
        """Format data row with alignment"""
        
        col_widths = self._calculate_column_widths(headers, max_width)
        
        cells = []
        for header, width in zip(headers, col_widths):
            value = str(row_data.get(header, "N/A"))
            cells.append(value[:width].ljust(width))
        
        return " | ".join(cells)
    
    def _calculate_column_widths(
        self,
        headers: List[str],
        max_width: int
    ) -> List[int]:
        """Calculate optimal column widths"""
        
        # Reserved space for separators
        separator_width = (len(headers) - 1) * 3  # " | "
        available_width = max_width - separator_width
        
        # Minimum width per column
        min_width = 8
        
        # Start with equal distribution
        col_widths = [available_width // len(headers)] * len(headers)
        
        # Adjust for header length
        for i, header in enumerate(headers):
            desired_width = len(header) + 2
            if desired_width > col_widths[i]:
                col_widths[i] = min(desired_width, available_width // len(headers) * 2)
        
        # Ensure minimum width
        col_widths = [max(width, min_width) for width in col_widths]
        
        return col_widths
