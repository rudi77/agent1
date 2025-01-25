from typing import Dict, Optional
from pathlib import Path
import logging
from .git_manager import GitManager
from .template_manager import TemplateManager
from .llm_manager import LLMManager
from .file_manager import FileManager
from .config import AgentConfig

class RepositoryAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.git_manager = GitManager(config)
        self.template_manager = TemplateManager(config)
        self.llm_manager = LLMManager(config)
        self.file_manager = FileManager(config)
    
    async def create_repository(self, 
                              requirements: Dict,
                              language: str,
                              repo_path: Path,
                              remote_url: Optional[str] = None) -> bool:
        """
        Main method to create a new repository with generated code
        """
        try:
            # 1. Initialize repository
            self.logger.info(f"Initializing repository at {repo_path}")
            repo = self.git_manager.init_repository(repo_path)
            
            # 2. Get appropriate template
            template = self.template_manager.get_template(language)
            
            # 3. Generate project structure and code
            await self.generate_project(requirements, template, repo_path, language)
            
            # 4. Set up Git remote and push
            if remote_url:
                self.git_manager.set_remote(repo, remote_url)
                self.git_manager.commit_and_push(repo, "Initial repository setup")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating repository: {str(e)}")
            raise
    
    async def generate_project(self,
                             requirements: Dict,
                             template: Dict,
                             repo_path: Path,
                             language: str) -> None:
        """
        Generate all project files based on requirements and template
        """
        # Generate directory structure
        self.file_manager.create_directory_structure(repo_path, template)
        
        # Generate source code files
        generated_files = await self.llm_manager.generate_source_code(
            requirements,
            template,
            language
        )
        
        # Write files
        for file_path, content in generated_files.items():
            self.file_manager.write_file(repo_path / file_path, content)
        
        # Generate documentation
        docs = await self.llm_manager.generate_documentation(
            requirements,
            template,
            generated_files
        )
        
        # Write documentation files
        self.file_manager.write_file(repo_path / "README.md", docs["readme"])
        if "architecture" in docs:
            self.file_manager.write_file(
                repo_path / "docs/architecture.md",
                docs["architecture"]
            ) 