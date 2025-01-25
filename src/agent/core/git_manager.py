from git import Repo
from pathlib import Path
from .config import AgentConfig

class GitManager:
    def __init__(self, config: AgentConfig):
        self.config = config
    
    def init_repository(self, path: Path) -> Repo:
        """Initialize a new Git repository"""
        return Repo.init(path)
    
    def set_remote(self, repo: Repo, remote_url: str) -> None:
        """Set the remote origin for the repository"""
        if "origin" in repo.remotes:
            repo.delete_remote("origin")
        repo.create_remote("origin", remote_url)
    
    def commit_and_push(self, repo: Repo, message: str) -> None:
        """Commit all changes and push to remote"""
        repo.git.add(A=True)
        repo.index.commit(message)
        repo.remotes.origin.push() 