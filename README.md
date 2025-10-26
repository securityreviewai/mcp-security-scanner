# MCP Security Profiler

A CLI tool for scanning GitHub repositories for security issues. This tool provides an extensible framework for analyzing GitHub repositories with customizable scanning logic and multiple report formats.

## Features

- 🔐 **Secure Token Management**: GitHub personal access token stored securely in user config
- 🔍 **Repository Scanning**: Clone and analyze GitHub repositories
- 📊 **Multiple Report Formats**: Generate reports in JSON and Markdown formats
- 🔧 **Extensible Architecture**: Easy to add custom scanning logic
- 🚀 **CLI Interface**: User-friendly command-line interface with progress indicators
- 🧹 **Automatic Cleanup**: Temporary repositories cleaned up after scanning

## Installation

This project uses `uv` as the package manager. Make sure you have `uv` installed:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone the repository and install dependencies:

```bash
git clone <your-repo-url>
cd mcp-security-profiler
uv sync
```

### MCP Server Dependencies

The scanner uses MCP (Model Context Protocol) servers for advanced code analysis:

- **ast-grep-mcp**: Pattern-based code search and analysis
- **xray-mcp**: Code structure analysis

These MCP servers are automatically installed and managed via `uvx` when you run a scan - no manual installation is required. The scanner will:
1. Download and cache the MCP servers on first use
2. Run them in isolated environments
3. Automatically reuse cached versions on subsequent scans

**Note**: The first scan may take slightly longer as MCP servers are being installed in the background.

## Setup

### 1. Configure Environment Variables

Create a `.env` file in the project root with your API credentials:

```bash
cp .env.example .env
```

Edit the `.env` file and add your values:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 2. Configure GitHub Token

Before using the scanner, you need to configure your GitHub personal access token:

```bash
uv run mcp-security-profiler config --token <YOUR_GITHUB_TOKEN>
```

Or let it prompt you:

```bash
uv run mcp-security-profiler config
```

**Creating a GitHub Token:**

1. Go to GitHub Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (for private repos) or `public_repo` (for public repos only)
4. Generate and copy the token

The token is stored securely in `~/.mcp-security-profiler/config.json` with restricted permissions.

## Usage

### Scan a Repository

```bash
uv run mcp-security-profiler scan <REPOSITORY>
```

The `REPOSITORY` argument accepts multiple formats:
- Full URL: `https://github.com/owner/repo`
- Short format: `owner/repo`
- Git URL: `git@github.com:owner/repo.git`

### Options

```bash
# Generate specific report formats
uv run mcp-security-profiler scan owner/repo --format json
uv run mcp-security-profiler scan owner/repo --format markdown
uv run mcp-security-profiler scan owner/repo --format json --format markdown

# Specify output directory
uv run mcp-security-profiler scan owner/repo --output-dir ./my-reports
```

### Examples

```bash
# Scan a public repository
uv run mcp-security-profiler scan django/django

# Scan with custom output directory
uv run mcp-security-profiler scan https://github.com/pallets/flask --output-dir ./flask-scan

# Generate only JSON report
uv run mcp-security-profiler scan owner/repo -f json
```

## Report Formats

### JSON Report

The JSON report contains structured data including:
- Repository metadata
- Scan timestamp and ID
- Detailed findings with severity levels
- Repository statistics
- Summary with finding counts by severity

### Markdown Report

The Markdown report provides a human-readable format with:
- Repository information
- Visual summary tables
- Findings grouped by severity
- Recommendations for each finding
- File type distribution statistics

## Customizing the Scanner

The scanner is designed to be extensible. You can add your custom scanning logic by modifying the `Scanner` class in `mcp_security_profiler/scanner.py`.

### Adding Custom Scans

Edit the `_run_custom_scans()` method to add your custom scanning logic:

```python
def _run_custom_scans(self) -> List[Dict[str, Any]]:
    findings = []
    
    # Add your custom scanning logic here
    findings.extend(self._scan_for_secrets())
    findings.extend(self._scan_dependencies())
    findings.extend(self._scan_code_quality())
    findings.extend(self._scan_configurations())
    
    return findings
```

### Example Custom Scanner Methods

```python
def _scan_for_secrets(self) -> List[Dict[str, Any]]:
    """Scan for hardcoded secrets."""
    findings = []
    # Your implementation here
    return findings

def _scan_dependencies(self) -> List[Dict[str, Any]]:
    """Scan for vulnerable dependencies."""
    findings = []
    # Your implementation here
    return findings
```

## Project Structure

```
mcp-security-profiler/
├── main.py                          # Entry point
├── pyproject.toml                   # Project configuration
├── README.md                        # This file
├── PLAN.md                         # Project plan
└── mcp_security_profiler/
    ├── __init__.py                 # Package init
    ├── cli.py                      # CLI commands and interface
    ├── config.py                   # Configuration management
    ├── github_handler.py           # GitHub API operations
    ├── scanner.py                  # Scanning engine
    └── reporters.py                # Report generation
```

## Development

### Running from Source

```bash
# Run the CLI
uv run python main.py config
uv run python main.py scan owner/repo

# Or use the installed script
uv run mcp-security-profiler --help
```

### Adding Dependencies

Use `uv add` to add new dependencies:

```bash
uv add package-name
```

## CLI Commands

### `config`

Configure GitHub token for API access.

```bash
uv run mcp-security-profiler config --token <TOKEN>
```

**Options:**
- `--token`: GitHub personal access token (prompted if not provided)

### `scan`

Scan a GitHub repository for security issues.

```bash
uv run mcp-security-profiler scan REPOSITORY [OPTIONS]
```

**Arguments:**
- `REPOSITORY`: GitHub repository (URL or owner/repo format)

**Options:**
- `-f, --format [json|markdown]`: Report format (can specify multiple, default: both)
- `-o, --output-dir PATH`: Output directory for reports (default: ./scan-results)

## Security Notes

- GitHub tokens are stored with `0600` permissions (owner read/write only)
- Configuration directory: `~/.mcp-security-profiler/`
- Temporary repositories are cleaned up by default
- All GitHub API access uses authenticated requests

## Troubleshooting

### Token Issues

If you get authentication errors:
1. Verify your token is valid
2. Reconfigure: `uv run mcp-security-profiler config`
3. Ensure token has appropriate scopes

### Cloning Issues

If repository cloning fails:
- Check your network connection
- Verify you have access to the repository
- For private repos, ensure token has `repo` scope

### Report Generation

If reports are not generated:
- Check write permissions in output directory
- Verify output path is valid
- Check disk space

## License

MIT License

Copyright (c) 2025 Abhay Bhargav, SecurityReview.AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contributing

We welcome contributions to MCP Security Profiler! Here's how you can help:

### Reporting Issues

- **Bug Reports**: Open an issue with a clear description, steps to reproduce, and expected vs actual behavior
- **Feature Requests**: Describe the feature, use case, and potential implementation approach

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**:
   - Write clear, commented code
   - Follow the existing code style
   - Add tests if applicable
   - Update documentation as needed
5. **Commit your changes**: `git commit -m "Add feature: description"`
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Open a Pull Request**: Provide a clear description of the changes

### Development Guidelines

- Use `uv` for dependency management (no pip)
- Follow PEP 8 style guidelines for Python code
- Write descriptive commit messages
- Keep PRs focused on a single feature or fix
- Update README.md if adding new features or changing usage

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow

## Author

**Abhay Bhargav**  
[SecurityReview.AI](https://securityreview.ai)

MCP Security Profiler is developed and maintained by Abhay Bhargav at SecurityReview.AI, focusing on AI-powered security analysis for MCP servers and applications.

