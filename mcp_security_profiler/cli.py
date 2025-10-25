"""CLI interface for MCP Security Profiler."""

import sys
from pathlib import Path
from typing import Optional

import click
from github import GithubException

from mcp_security_profiler.config import Config
from mcp_security_profiler.github_handler import GitHubHandler
from mcp_security_profiler.scanner import Scanner
from mcp_security_profiler.reporters import generate_reports


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """MCP Security Profiler - Scan GitHub repositories for security issues."""
    pass


@cli.command()
@click.option(
    "--token",
    required=True,
    prompt=True,
    hide_input=True,
    help="GitHub personal access token"
)
def config(token: str):
    """Configure GitHub token for API access."""
    config_manager = Config()
    
    # Validate token
    click.echo("Validating token...", nl=False)
    handler = GitHubHandler(token)
    
    if not handler.validate_token():
        click.echo(" ❌")
        click.secho("Error: Invalid GitHub token", fg="red", err=True)
        sys.exit(1)
    
    click.echo(" ✓")
    
    # Save token
    config_manager.save_token(token)
    click.secho("✓ GitHub token configured successfully!", fg="green")
    click.echo(f"Configuration saved to: {config_manager.config_file}")


@cli.command()
@click.argument("repository")
@click.option(
    "--format",
    "-f",
    "formats",
    multiple=True,
    type=click.Choice(["json", "markdown"], case_sensitive=False),
    default=["json", "markdown"],
    help="Report format(s) to generate (can specify multiple)"
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    default=Path("./scan-results"),
    help="Output directory for reports"
)
def scan(
    repository: str,
    formats: tuple[str, ...],
    output_dir: Path
):
    """
    Scan a GitHub repository for security issues.
    
    REPOSITORY can be:
    - Full URL: https://github.com/owner/repo
    - Short format: owner/repo
    """
    # Load config
    config_manager = Config()
    
    if not config_manager.is_configured():
        click.secho(
            "Error: GitHub token not configured. Run 'mcp-security-profiler config' first.",
            fg="red",
            err=True
        )
        sys.exit(1)
    
    token = config_manager.get_token()
    handler = GitHubHandler(token)
    
    # Parse repository
    try:
        owner, repo_name = handler.parse_repo_url(repository)
        click.echo(f"📦 Repository: {owner}/{repo_name}")
    except ValueError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)
    
    # Get repository info
    try:
        click.echo("Fetching repository information...", nl=False)
        repo_info = handler.get_repo_info(owner, repo_name)
        click.echo(" ✓")
        
        click.echo(f"   Description: {repo_info.get('description', 'N/A')}")
        click.echo(f"   Language: {repo_info.get('language', 'N/A')}")
        click.echo(f"   Stars: {repo_info.get('stars', 0)}")
    except GithubException as e:
        click.echo(" ❌")
        click.secho(f"Error: {e.data.get('message', str(e))}", fg="red", err=True)
        sys.exit(1)
    
    # Clone repository
    repo_path = None
    try:
        click.echo("Cloning repository...", nl=False)
        repo_path = handler.clone_repository(repository)
        click.echo(" ✓")
        click.echo(f"   Cloned to: {repo_path}")
    except Exception as e:
        click.echo(" ❌")
        click.secho(f"Error cloning repository: {e}", fg="red", err=True)
        sys.exit(1)
    
    # Scan repository
    try:
        click.echo("\n🔍 Starting security scan...")
        scanner = Scanner(repo_path, repo_info)
        scan_results = scanner.scan()
        
        click.echo("✓ Scan completed")
        
        # Display summary
        summary = scan_results.get("summary", {})
        click.echo(f"\n📊 Scan Summary:")
        click.echo(f"   Total findings: {summary.get('total_findings', 0)}")
        
        if summary.get("critical", 0) > 0:
            click.secho(f"   Critical: {summary['critical']}", fg="red", bold=True)
        if summary.get("high", 0) > 0:
            click.secho(f"   High: {summary['high']}", fg="red")
        if summary.get("medium", 0) > 0:
            click.secho(f"   Medium: {summary['medium']}", fg="yellow")
        if summary.get("low", 0) > 0:
            click.secho(f"   Low: {summary['low']}", fg="blue")
        if summary.get("info", 0) > 0:
            click.echo(f"   Info: {summary['info']}")
        
    except Exception as e:
        click.secho(f"Error during scan: {e}", fg="red", err=True)
        if repo_path:
            handler.cleanup_repo(repo_path)
        sys.exit(1)
    
    # Generate reports
    try:
        click.echo(f"\n📝 Generating reports...")
        report_files = generate_reports(scan_results, output_dir, list(formats))
        
        click.echo("✓ Reports generated:")
        for fmt, path in report_files.items():
            click.echo(f"   {fmt.upper()}: {path}")
    
    except Exception as e:
        click.secho(f"Error generating reports: {e}", fg="red", err=True)
        if repo_path:
            handler.cleanup_repo(repo_path)
        sys.exit(1)
    
    # Cleanup
    if repo_path:
        click.echo("\n🧹 Cleaning up...")
        handler.cleanup_repo(repo_path)
        click.echo("✓ Cleanup completed")
    
    click.secho("\n✨ Scan complete!", fg="green", bold=True)


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()

