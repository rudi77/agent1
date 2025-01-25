from typing import Dict, List
import openai
from .config import AgentConfig

class LLMManager:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.client = openai.AsyncOpenAI(api_key=config.openai_api_key)
    
    async def generate_source_code(self,
                                 requirements: Dict,
                                 template: Dict,
                                 language: str) -> Dict[str, str]:
        """
        Generate source code files based on requirements and template
        """
        # Prepare the prompt for code generation
        prompt = self._prepare_code_generation_prompt(
            requirements,
            template,
            language
        )
        
        # Get completion from LLM
        response = await self.client.chat.completions.create(
            model=self.config.model_name,
            messages=[
                {"role": "system", "content": "You are an expert software developer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        # Parse and return generated files
        return self._parse_generated_code(response.choices[0].message.content)
    
    async def generate_documentation(self,
                                   requirements: Dict,
                                   template: Dict,
                                   generated_files: Dict[str, str]) -> Dict[str, str]:
        """
        Generate documentation including README and architecture docs
        """
        prompt = self._prepare_documentation_prompt(
            requirements,
            template,
            generated_files
        )
        
        response = await self.client.chat.completions.create(
            model=self.config.model_name,
            messages=[
                {"role": "system", "content": "You are an expert technical writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return self._parse_documentation(response.choices[0].message.content) 