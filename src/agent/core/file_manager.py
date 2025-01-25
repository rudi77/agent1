from pathlib import Path
from typing import Dict
from .config import AgentConfig

class FileManager:
    def __init__(self, config: AgentConfig):
        self.config = config
    
    def create_directory_structure(self, base_path: Path, template: Dict) -> None:
        """Create directory structure based on template"""
        for dir_path in template["directories"]:
            (base_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    def write_file(self, file_path: Path, content: str) -> None:
        """Write content to a file, creating parent directories if needed"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content) 