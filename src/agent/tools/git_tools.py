from langchain.tools import BaseTool
from git import Repo
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class InitRepoTool(BaseTool):
    name: str = "init_repository"
    description: str = "Initialize a new Git repository at the specified path"
    
    def _run(self, path: str) -> str:
        try:
            repo = Repo.init(Path(path))
            return f"Successfully initialized repository at {path}"
        except Exception as e:
            return f"Failed to initialize repository: {str(e)}"
    
    async def _arun(self, path: str) -> str:
        # For synchronous operations, we can just return the _run result
        return self._run(path)

class GitCommitTool(BaseTool):
    name: str = "git_commit"
    description: str = "Commit changes to the repository with a message"
    
    def _run(self, args: str) -> str:
        """
        Args should be in format: "repo_path::message"
        """
        try:
            repo_path, message = args.split("::")
            repo = Repo(repo_path)
            repo.git.add(A=True)
            repo.index.commit(message)
            return f"Successfully committed changes with message: {message}"
        except Exception as e:
            return f"Failed to commit changes: {str(e)}"
    
    async def _arun(self, args: str) -> str:
        return self._run(args)

class GitPushTool(BaseTool):
    name: str = "git_push"
    description: str = "Push changes to the remote repository. Args format: 'repo_path::remote_url' (remote_url is optional)"
    
    def _run(self, args: str) -> str:
        try:
            parts = args.split("::")
            repo_path = parts[0]
            remote_url = parts[1] if len(parts) > 1 else None
            
            repo = Repo(repo_path)
            if remote_url and "origin" not in repo.remotes:
                repo.create_remote("origin", remote_url)
            repo.remotes.origin.push()
            return "Successfully pushed changes to remote"
        except Exception as e:
            return f"Failed to push changes: {str(e)}"
    
    async def _arun(self, args: str) -> str:
        return self._run(args) 