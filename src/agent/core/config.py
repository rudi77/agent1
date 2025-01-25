from dataclasses import dataclass
from pathlib import Path

@dataclass
class AgentConfig:
    openai_api_key: str
    model_name: str = "gpt-4-turbo-preview"
    templates_dir: Path = Path("templates")
    log_level: str = "INFO" 