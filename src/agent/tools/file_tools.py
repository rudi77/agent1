from langchain.tools import BaseTool
from pathlib import Path
import json
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class CreateDirectoriesTool(BaseTool):
    name = "create_directories"
    description = "Create directory structure based on template. Args format: 'base_path::dir1,dir2,dir3'"
    
    def _run(self, args: str) -> str:
        """Create directories from a comma-separated list"""
        try:
            base_path, dir_list = args.split("::")
            directories = [d.strip() for d in dir_list.split(",")]
            
            base = Path(base_path)
            for dir_path in directories:
                (base / dir_path).mkdir(parents=True, exist_ok=True)
            return f"Successfully created directory structure at {base_path}"
        except Exception as e:
            logger.error(f"Failed to create directories: {str(e)}")
            return f"Failed to create directories: {str(e)}"
    
    async def _arun(self, args: str) -> str:
        return self._run(args)

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Write content to a file, creating parent directories if needed. Args format: 'file_path::content'"
    
    def _run(self, args: str) -> str:
        try:
            file_path, content = args.split("::", 1)  # Split on first occurrence only
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            # Write with UTF-8 encoding
            path.write_text(content, encoding='utf-8')
            return f"Successfully wrote file: {file_path}"
        except Exception as e:
            logger.error(f"Failed to write file: {str(e)}")
            return f"Failed to write file: {str(e)}"
    
    async def _arun(self, args: str) -> str:
        return self._run(args)

class LoadTemplateTool(BaseTool):
    name = "load_template"
    description = "Load project template for the specified language"
    templates_dir: str = "templates"  # Default templates directory
    
    def __init__(self, templates_dir: str = "templates", **kwargs):
        super().__init__(**kwargs)
        self.templates_dir = templates_dir
    
    def _run(self, language: str) -> str:
        """Load and return the template content as text"""
        try:
            template_file = Path(self.templates_dir) / f"template_{language.lower()}.txt"
            if not template_file.exists():
                return f"No template found for language: {language}"
            # Read with UTF-8 encoding
            return template_file.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Error loading template: {str(e)}")
            return f"Failed to load template: {str(e)}"
    
    async def _arun(self, language: str) -> str:
        return self._run(language) 