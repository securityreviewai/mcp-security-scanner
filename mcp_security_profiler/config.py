"""Configuration management for MCP Security Profiler."""

import json
import os
from pathlib import Path
from typing import Optional


class Config:
    """Manages configuration for the security profiler."""
    
    CONFIG_DIR = Path.home() / ".mcp-security-profiler"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    
    def __init__(self):
        """Initialize config manager."""
        self.config_dir = self.CONFIG_DIR
        self.config_file = self.CONFIG_FILE
        self._ensure_config_dir()
    
    def _ensure_config_dir(self) -> None:
        """Ensure config directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def save_token(self, token: str) -> None:
        """
        Save GitHub token to config file.
        
        Args:
            token: GitHub personal access token
        """
        config_data = self._load_config()
        config_data["github_token"] = token
        self._save_config(config_data)
    
    def get_token(self) -> Optional[str]:
        """
        Get GitHub token from config.
        
        Returns:
            GitHub token or None if not set
        """
        config_data = self._load_config()
        return config_data.get("github_token")
    
    def _load_config(self) -> dict:
        """Load config from file."""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_config(self, config_data: dict) -> None:
        """Save config to file."""
        with open(self.config_file, "w") as f:
            json.dump(config_data, f, indent=2)
        
        # Set restrictive permissions (owner read/write only)
        os.chmod(self.config_file, 0o600)
    
    def is_configured(self) -> bool:
        """Check if GitHub token is configured."""
        return self.get_token() is not None

