"""Scanner module for repository security analysis."""

import datetime
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional


async def _run_mcp_agent_wrapper(repo_path: str) -> Optional[Any]:
    """
    Wrapper to properly execute the MCP agent in an async context.
    
    Args:
        repo_path: Path to the repository to scan
        
    Returns:
        MCPReport or None if scan fails
    """
    from mcp_security_profiler.profile_agent import run_mcp_scan_agent
    result = await run_mcp_scan_agent(repo_path)
    
    # Ensure all MCP subprocess operations complete
    # Give time for uvx subprocesses to finish file operations
    await asyncio.sleep(3)
    
    return result


class Scanner:
    """Repository scanner for security analysis."""
    
    def __init__(self, repo_path: Path, repo_info: Dict[str, Any]):
        """
        Initialize scanner.
        
        Args:
            repo_path: Path to cloned repository
            repo_info: Repository information from GitHub
        """
        self.repo_path = repo_path
        self.repo_info = repo_info
        self.mcp_tools = []  # Store MCP tools separately
    
    def scan(self) -> Dict[str, Any]:
        """
        Perform security scan on repository.
        
        This is a placeholder implementation. You can replace this with
        your custom scanning logic.
        
        Returns:
            Dictionary containing scan results
        """
        # Store start time to track scan duration
        import time
        start_time = time.time()
        
        scan_results = {
            "scan_id": self._generate_scan_id(),
            "timestamp": datetime.datetime.now().isoformat(),
            "repository": self.repo_info,
            "scan_metadata": {
                "scanner_version": "0.1.0",
                "scan_type": "security_analysis",
            },
            "mcp_tools": self.mcp_tools,  # Add MCP tools section
            "findings": self._run_custom_scans(),
            "statistics": self._gather_statistics(),
            "summary": {
                "total_findings": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            }
        }
        
        # Update summary based on findings
        scan_results["summary"]["total_findings"] = len(scan_results["findings"])
        for finding in scan_results["findings"]:
            severity = finding.get("severity", "info").lower()
            if severity in scan_results["summary"]:
                scan_results["summary"][severity] += 1
        
        # Add scan duration
        scan_results["scan_metadata"]["duration_seconds"] = round(time.time() - start_time, 2)
        
        return scan_results
    
    def _generate_scan_id(self) -> str:
        """Generate unique scan ID."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        repo_name = self.repo_info.get("full_name", "unknown").replace("/", "-")
        return f"scan-{repo_name}-{timestamp}"
    
    def _run_custom_scans(self) -> List[Dict[str, Any]]:
        """
        Run custom security scans using MCP agent.
        
        Returns:
            List of findings
        """
        findings = []
        
        # Run MCP security scan agent
        try:
            # Run the async MCP scan with proper event loop handling
            # Use the wrapper to ensure proper async context and subprocess completion
            mcp_report = asyncio.run(_run_mcp_agent_wrapper(str(self.repo_path)))
            
            # Convert MCP vulnerabilities to findings format
            if mcp_report and mcp_report.vulnerabilities:
                for idx, vuln in enumerate(mcp_report.vulnerabilities, 1):
                    finding = {
                        "id": f"MCP-{idx:03d}",
                        "title": vuln.name,
                        "description": vuln.description,
                        "severity": vuln.severity.lower(),
                        "category": "mcp_security_scan",
                        "recommendation": vuln.recommendation,
                        "confidence": vuln.confidence
                    }
                    
                    # Add file paths and code snippets if available
                    if vuln.paths:
                        finding["affected_files"] = []
                        for path_info in vuln.paths:
                            finding["affected_files"].append({
                                "path": path_info.path,
                                "code_snippet": path_info.code_snippet
                            })
                        # Also add the first path as "file" for compatibility
                        finding["file"] = vuln.paths[0].path
                    
                    findings.append(finding)
            
            # Store MCP tools separately (not as a finding)
            if mcp_report and mcp_report.tools:
                self.mcp_tools = [
                    {"name": tool.name, "description": tool.description}
                    for tool in mcp_report.tools
                ]
        
        except Exception as e:
            # If MCP scan fails, log it as a finding
            import traceback
            error_details = traceback.format_exc()
            findings.append({
                "id": "MCP-ERROR-001",
                "title": "MCP Security Scan Error",
                "description": f"Failed to run MCP security scan: {str(e)}",
                "severity": "info",
                "category": "scan_error",
                "recommendation": "Check MCP configuration and try again",
                "error_traceback": error_details
            })
        
        # Keep existing placeholder checks as fallback/additional checks
        findings.extend(self._run_basic_checks())
        
        return findings
    
    def _run_basic_checks(self) -> List[Dict[str, Any]]:
        """
        Run basic security checks.
        
        Returns:
            List of findings from basic checks
        """
        findings = []
        
        # Example: Check for common security files
        security_files = [
            "SECURITY.md",
            ".github/SECURITY.md",
            "security.txt",
            ".well-known/security.txt"
        ]
        
        has_security_policy = False
        for sec_file in security_files:
            if (self.repo_path / sec_file).exists():
                has_security_policy = True
                break
        
        if not has_security_policy:
            findings.append({
                "id": "SEC-001",
                "title": "Missing Security Policy",
                "description": "Repository does not have a SECURITY.md file",
                "severity": "low",
                "category": "documentation",
                "recommendation": "Add a SECURITY.md file to document security policies"
            })
        
        # Example: Check for dependency files
        dependency_files = {
            "requirements.txt": "Python",
            "package.json": "Node.js",
            "pom.xml": "Maven",
            "build.gradle": "Gradle",
            "Gemfile": "Ruby",
        }
        
        for dep_file, ecosystem in dependency_files.items():
            if (self.repo_path / dep_file).exists():
                findings.append({
                    "id": "INFO-001",
                    "title": f"{ecosystem} Dependencies Detected",
                    "description": f"Found {dep_file} - consider dependency scanning",
                    "severity": "info",
                    "category": "dependencies",
                    "file": dep_file
                })
        
        return findings
    
    def _gather_statistics(self) -> Dict[str, Any]:
        """
        Gather repository statistics.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_files": 0,
            "total_lines": 0,
            "file_types": {},
        }
        
        try:
            for file_path in self.repo_path.rglob("*"):
                if file_path.is_file() and not self._should_ignore(file_path):
                    stats["total_files"] += 1
                    
                    # Count by extension
                    ext = file_path.suffix or "no_extension"
                    stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
                    
                    # Count lines (for text files)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            stats["total_lines"] += sum(1 for _ in f)
                    except Exception:
                        pass
        except Exception as e:
            stats["error"] = str(e)
        
        return stats
    
    def _should_ignore(self, path: Path) -> bool:
        """
        Check if path should be ignored.
        
        Args:
            path: File path
        
        Returns:
            True if should be ignored
        """
        ignore_patterns = [
            ".git",
            "__pycache__",
            "node_modules",
            ".env",
            "venv",
            ".venv",
            "dist",
            "build",
        ]
        
        return any(pattern in str(path) for pattern in ignore_patterns)

