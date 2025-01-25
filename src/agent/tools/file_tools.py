from langchain.tools import BaseTool
from pathlib import Path
import json
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class CreateDirectoriesTool(BaseTool):
    name: str = "create_directory"
    description: str = "Create a single directory at the specified path, including any necessary parent directories"
    
    def _run(self, directory_path: str) -> str:
        """Create a single directory and its parent directories if needed"""
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return f"Successfully created directory: {directory_path}"
        except Exception as e:
            logger.error(f"Failed to create directory: {str(e)}")
            return f"Failed to create directory: {str(e)}"
    
    async def _arun(self, directory_path: str) -> str:
        return self._run(directory_path)

class WriteFileTool(BaseTool):
    name: str = "write_file"
    description: str = "Write content to a file, creating parent directories if needed. Args format: 'file_path::content'"
    
    def _run(self, args: str | dict) -> str:
        try:
            # Extract file path and content based on input format
            if isinstance(args, dict):
                if 'v__args' in args:
                    # Format: {'v__args': [file_path, content]}
                    file_path, content = args['v__args']
                elif 'file_path' in args and 'content' in args:
                    # Format: {'file_path': path, 'content': content}
                    file_path = args['file_path']
                    content = args['content']
                else:
                    raise ValueError(f"Invalid argument format: {args}")
            else:
                # Format: "file_path::content"
                file_path, content = args.split("::", 1)
            
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            # Write with UTF-8 encoding
            path.write_text(content, encoding='utf-8')
            return f"Successfully wrote file: {file_path}"
        except Exception as e:
            logger.error(f"Failed to write file: {str(e)}")
            return f"Failed to write file: {str(e)}"
    
    async def _arun(self, *args: str | dict, **kwargs: str | dict) -> str:
        # Handle both positional and keyword arguments
        if args and len(args) > 0:
            return self._run(args[0])
        elif kwargs:
            # If we receive kwargs directly, pass them as a dict
            return self._run(kwargs)
        return "No arguments provided"

class LoadTemplateTool(BaseTool):
    name: str = "load_template"
    description: str = "Load project template for the specified language"
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