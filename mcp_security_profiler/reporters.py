"""Report generation for scan results."""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class ReportGenerator:
    """Generate reports in various formats."""
    
    def __init__(self, scan_results: Dict[str, Any]):
        """
        Initialize report generator.
        
        Args:
            scan_results: Scan results dictionary
        """
        self.scan_results = scan_results
    
    def generate_json(self, output_path: Path) -> None:
        """
        Generate JSON report.
        
        Args:
            output_path: Path to output file
        """
        with open(output_path, "w") as f:
            json.dump(self.scan_results, f, indent=2)
    
    def generate_markdown(self, output_path: Path) -> None:
        """
        Generate Markdown report.
        
        Args:
            output_path: Path to output file
        """
        md_content = self._build_markdown()
        with open(output_path, "w") as f:
            f.write(md_content)
    
    def _build_markdown(self) -> str:
        """Build markdown report content."""
        repo_info = self.scan_results.get("repository", {})
        summary = self.scan_results.get("summary", {})
        findings = self.scan_results.get("findings", [])
        stats = self.scan_results.get("statistics", {})
        mcp_tools = self.scan_results.get("mcp_tools", [])
        
        md = []
        
        # Header
        md.append("# Security Scan Report\n")
        md.append(f"**Scan ID:** {self.scan_results.get('scan_id', 'N/A')}  ")
        md.append(f"**Timestamp:** {self.scan_results.get('timestamp', 'N/A')}  \n")
        
        # Repository Information
        md.append("## Repository Information\n")
        md.append(f"- **Name:** {repo_info.get('full_name', 'N/A')}")
        md.append(f"- **Description:** {repo_info.get('description', 'N/A')}")
        md.append(f"- **Language:** {repo_info.get('language', 'N/A')}")
        md.append(f"- **Stars:** {repo_info.get('stars', 0)}")
        md.append(f"- **Forks:** {repo_info.get('forks', 0)}")
        md.append(f"- **Default Branch:** {repo_info.get('default_branch', 'N/A')}\n")
        
        # MCP Tools/Functions Section
        if mcp_tools:
            md.append("## MCP Server Functions\n")
            md.append(f"Found **{len(mcp_tools)}** MCP server function(s)/tool(s):\n")
            md.append("| Function Name | Description |")
            md.append("|---------------|-------------|")
            for tool in mcp_tools:
                md.append(f"| `{tool.get('name', 'N/A')}` | {tool.get('description', 'N/A')} |")
            md.append("")
        
        # Summary
        md.append("## Scan Summary\n")
        md.append(f"**Total Findings:** {summary.get('total_findings', 0)}\n")
        
        md.append("| Severity | Count |")
        md.append("|----------|-------|")
        md.append(f"| Critical | {summary.get('critical', 0)} |")
        md.append(f"| High     | {summary.get('high', 0)} |")
        md.append(f"| Medium   | {summary.get('medium', 0)} |")
        md.append(f"| Low      | {summary.get('low', 0)} |")
        md.append(f"| Info     | {summary.get('info', 0)} |\n")
        
        # Statistics
        md.append("## Repository Statistics\n")
        md.append(f"- **Total Files:** {stats.get('total_files', 0)}")
        md.append(f"- **Total Lines:** {stats.get('total_lines', 0)}\n")
        
        if stats.get('file_types'):
            md.append("### File Types Distribution\n")
            file_types = sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True)
            md.append("| Extension | Count |")
            md.append("|-----------|-------|")
            for ext, count in file_types[:10]:  # Top 10
                md.append(f"| {ext} | {count} |")
            md.append("")
        
        # Findings
        if findings:
            md.append("## Findings\n")
            
            # Group by severity
            severity_order = ["critical", "high", "medium", "low", "info"]
            findings_by_severity = {sev: [] for sev in severity_order}
            
            for finding in findings:
                severity = finding.get("severity", "info").lower()
                if severity in findings_by_severity:
                    findings_by_severity[severity].append(finding)
            
            for severity in severity_order:
                severity_findings = findings_by_severity[severity]
                if severity_findings:
                    md.append(f"### {severity.capitalize()} Severity\n")
                    
                    for finding in severity_findings:
                        md.append(f"#### {finding.get('id', 'N/A')}: {finding.get('title', 'No title')}\n")
                        md.append(f"**Description:** {finding.get('description', 'N/A')}  ")
                        md.append(f"**Category:** {finding.get('category', 'N/A')}  ")
                        
                        # Add confidence level for MCP findings
                        if finding.get('confidence'):
                            md.append(f"**Confidence:** {finding['confidence']}  ")
                        
                        if finding.get('file'):
                            md.append(f"**File:** `{finding['file']}`  ")
                        
                        # Display affected files with code snippets for MCP findings
                        if finding.get('affected_files'):
                            md.append(f"\n**Affected Files:**")
                            for idx, file_info in enumerate(finding['affected_files'], 1):
                                md.append(f"\n{idx}. `{file_info.get('path', 'Unknown')}`")
                                if file_info.get('code_snippet'):
                                    md.append(f"```")
                                    md.append(file_info['code_snippet'])
                                    md.append(f"```")
                        
                        # Display MCP tools if present
                        if finding.get('tools'):
                            md.append(f"\n**MCP Tools Found:**")
                            for tool in finding['tools']:
                                md.append(f"- **{tool.get('name')}**: {tool.get('description')}")
                        
                        if finding.get('recommendation'):
                            md.append(f"\n**Recommendation:** {finding['recommendation']}  ")
                        
                        md.append("")
        else:
            md.append("## Findings\n")
            md.append("No findings detected.\n")
        
        # Footer
        md.append("---")
        md.append(f"\n*Report generated by MCP Security Profiler v{self.scan_results.get('scan_metadata', {}).get('scanner_version', '0.1.0')}*")
        
        return "\n".join(md)


def generate_reports(scan_results: Dict[str, Any], output_dir: Path, formats: list[str]) -> Dict[str, Path]:
    """
    Generate reports in specified formats.
    
    Args:
        scan_results: Scan results dictionary
        output_dir: Directory to save reports
        formats: List of report formats ('json', 'markdown')
    
    Returns:
        Dictionary mapping format to output file path
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    generator = ReportGenerator(scan_results)
    
    scan_id = scan_results.get("scan_id", "scan")
    report_files = {}
    
    if "json" in formats:
        json_path = output_dir / f"{scan_id}.json"
        generator.generate_json(json_path)
        report_files["json"] = json_path
    
    if "markdown" in formats:
        md_path = output_dir / f"{scan_id}.md"
        generator.generate_markdown(md_path)
        report_files["markdown"] = md_path
    
    return report_files

