from typing import Dict
import json
from pathlib import Path
from .config import AgentConfig

class TemplateManager:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.templates_path = Path(config.templates_dir)
    
    def get_template(self, language: str) -> Dict:
        """
        Load and return the appropriate template for the given language
        """
        template_file = self.templates_path / f"template_{language.lower()}.json"
        
        if not template_file.exists():
            raise ValueError(f"No template found for language: {language}")
            
        with open(template_file, 'r') as f:
            return json.load(f) 