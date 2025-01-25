from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Dict
import logging
import json
from pydantic import Field, PrivateAttr
import os

logger = logging.getLogger(__name__)

class GenerateCodeTool(BaseTool):
    name: str = "generate_code"
    description: str = "Generate source code based on requirements and template"
    
    def __init__(self, model_name: str, openai_api_key: str, **data):
        super().__init__(**data)
        # Initialize private attributes before using them
        object.__setattr__(self, '_model_name', model_name)
        object.__setattr__(self, '_openai_api_key', openai_api_key)
        object.__setattr__(self, '_llm', ChatOpenAI(
            model_name=model_name,
            openai_api_key=openai_api_key,
            temperature=0.2
        ))
    
    def _run(self, requirements: Dict, template: str, language: str) -> Dict[str, str]:
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert software developer specializing in creating well-structured applications.
                You follow clean architecture principles and best practices."""),
                ("user", """
                Generate code for a {language} project with these requirements:
                {requirements}
                
                Using this template as a guide for project structure and architecture:
                {template}
                
                Follow these guidelines:
                1. Implement the project following the hexagonal architecture described in the template
                2. Create all necessary files including domain models, interfaces, and implementations
                3. Ensure the code follows clean code principles and best practices
                4. Include proper error handling and logging
                5. Add appropriate comments and docstrings
                
                Return a JSON object where keys are file paths and values are the file contents.
                The file paths should follow the structure described in the template.
                """)
            ])
            
            response = self._llm.predict_messages(
                prompt.format_messages(
                    language=language,
                    requirements=requirements,
                    template=template
                )
            )
            
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                logger.error("Failed to parse LLM response as JSON")
                return {"error": "Failed to generate valid code structure"}
            
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            return {"error": f"Failed to generate code: {str(e)}"}
    
    def _arun(self, requirements: Dict, template: str, language: str) -> Dict[str, str]:
        return self._run(requirements, template, language)

class GenerateDocumentationTool(BaseTool):
    name: str = "generate_documentation"
    description: str = "Generate project documentation including README and architecture docs. Args format: 'repo_path'"
    
    def __init__(self, model_name: str, openai_api_key: str, **data):
        super().__init__(**data)
        object.__setattr__(self, '_model_name', model_name)
        object.__setattr__(self, '_openai_api_key', openai_api_key)
        object.__setattr__(self, '_llm', ChatOpenAI(
            model_name=model_name,
            openai_api_key=openai_api_key,
            temperature=0.3
        ))
    
    def _run(self, repo_path: str) -> str:
        try:
            # Collect information about the generated files
            generated_files = {}
            for root, _, files in os.walk(repo_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            generated_files[os.path.relpath(file_path, repo_path)] = f.read()

            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert technical writer."),
                ("user", """
                Generate documentation for a Python project with these files:
                {files}
                
                Return a JSON object with 'readme' and 'architecture' documentation.
                The README should include:
                1. Project overview
                2. Installation instructions
                3. Usage examples
                4. API documentation
                
                The architecture doc should explain:
                1. Project structure
                2. Design patterns used
                3. Key components
                4. Data flow
                """)
            ])
            
            response = self._llm.invoke(
                prompt.format_messages(files=json.dumps(generated_files, indent=2))
            )
            
            try:
                docs = json.loads(response.content)
                
                # Write the documentation files
                readme_path = os.path.join(repo_path, 'README.md')
                arch_path = os.path.join(repo_path, 'docs')
                os.makedirs(arch_path, exist_ok=True)
                arch_path = os.path.join(arch_path, 'architecture.md')
                
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(docs['readme'])
                with open(arch_path, 'w', encoding='utf-8') as f:
                    f.write(docs['architecture'])
                
                return f"Successfully generated documentation in {repo_path}"
                
            except json.JSONDecodeError:
                logger.error("Failed to parse LLM response as JSON")
                return f"Failed to generate documentation: Invalid response format"
            
        except Exception as e:
            logger.error(f"Error generating documentation: {str(e)}")
            return f"Failed to generate documentation: {str(e)}"
    
    async def _arun(self, repo_path: str) -> str:
        return self._run(repo_path) 