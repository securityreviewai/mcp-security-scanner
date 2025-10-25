"""GitHub API handler for repository operations."""

import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from github import Github, GithubException, Auth
import git


class GitHubHandler:
    """Handles GitHub API operations and repository cloning."""
    
    def __init__(self, token: str):
        """
        Initialize GitHub handler.
        
        Args:
            token: GitHub personal access token
        """
        auth = Auth.Token(token)
        self.client = Github(auth=auth)
        self.token = token
    
    def validate_token(self) -> bool:
        """
        Validate the GitHub token.
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            self.client.get_user().login
            return True
        except GithubException:
            return False
    
    def parse_repo_url(self, repo_url: str) -> tuple[str, str]:
        """
        Parse GitHub repository URL to extract owner and repo name.
        
        Args:
            repo_url: GitHub repository URL (e.g., https://github.com/owner/repo)
        
        Returns:
            Tuple of (owner, repo_name)
        
        Raises:
            ValueError: If URL format is invalid
        """
        # Handle different URL formats
        # https://github.com/owner/repo
        # https://github.com/owner/repo.git
        # git@github.com:owner/repo.git
        # owner/repo
        
        repo_url = repo_url.strip()
        
        if repo_url.startswith("git@github.com:"):
            repo_url = repo_url.replace("git@github.com:", "")
        elif repo_url.startswith("https://github.com/"):
            repo_url = repo_url.replace("https://github.com/", "")
        elif repo_url.startswith("http://github.com/"):
            repo_url = repo_url.replace("http://github.com/", "")
        
        # Remove .git suffix if present
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]
        
        parts = repo_url.split("/")
        if len(parts) != 2:
            raise ValueError(
                f"Invalid repository URL format: {repo_url}. "
                "Expected format: owner/repo or https://github.com/owner/repo"
            )
        
        return parts[0], parts[1]
    
    def get_repo_info(self, owner: str, repo_name: str) -> Dict[str, Any]:
        """
        Get repository information from GitHub.
        
        Args:
            owner: Repository owner
            repo_name: Repository name
        
        Returns:
            Dictionary with repository information
        
        Raises:
            GithubException: If repository not found or access denied
        """
        try:
            repo = self.client.get_repo(f"{owner}/{repo_name}")
            return {
                "full_name": repo.full_name,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "language": repo.language,
                "created_at": repo.created_at.isoformat() if repo.created_at else None,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                "default_branch": repo.default_branch,
                "clone_url": repo.clone_url,
            }
        except GithubException as e:
            raise GithubException(
                status=e.status,
                data={"message": f"Failed to access repository: {e.data.get('message', str(e))}"}
            )
    
    def clone_repository(self, repo_url: str, target_dir: Optional[Path] = None) -> Path:
        """
        Clone a GitHub repository.
        
        Args:
            repo_url: GitHub repository URL
            target_dir: Target directory for cloning (temp dir if None)
        
        Returns:
            Path to cloned repository
        
        Raises:
            git.GitCommandError: If cloning fails
        """
        if target_dir is None:
            target_dir = Path(tempfile.mkdtemp(prefix="mcp-scan-"))
        
        # Use authenticated URL for private repos
        owner, repo_name = self.parse_repo_url(repo_url)
        auth_url = f"https://{self.token}@github.com/{owner}/{repo_name}.git"
        
        try:
            git.Repo.clone_from(auth_url, target_dir)
            return target_dir
        except git.GitCommandError as e:
            # Clean up on failure
            if target_dir.exists():
                shutil.rmtree(target_dir)
            raise
    
    def cleanup_repo(self, repo_path: Path) -> None:
        """
        Clean up cloned repository.
        
        Args:
            repo_path: Path to repository to clean up
        """
        if repo_path.exists():
            shutil.rmtree(repo_path)

