from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Dict
import json
import logging
from pydantic import Field, PrivateAttr

logger = logging.getLogger(__name__)

class ParseTemplateTool(BaseTool):
    name: str = "parse_template"
    description: str = "Parse the template text to extract directory structure and architectural requirements"
    
    def __init__(self, model_name: str, openai_api_key: str, **data):
        super().__init__(**data)
        # Initialize private attributes before using them
        object.__setattr__(self, '_model_name', model_name)
        object.__setattr__(self, '_openai_api_key', openai_api_key)
        object.__setattr__(self, '_llm', ChatOpenAI(
            model_name=model_name,
            openai_api_key=openai_api_key,
            temperature=0.1
        ))
    
    def _run(self, template: str) -> str:
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert in software architecture and project structure."),
                ("user", """
                Analyze this project template and extract:
                1. The directory structure
                2. Required architectural layers
                3. Key interfaces and components
                4. Implementation guidelines
                
                Template:
                {template}
                
                Return a JSON object with these sections structured for easy parsing.
                """)
            ])
            
            # Use invoke instead of predict_messages
            response = self._llm.invoke(
                prompt.format_messages(template=template)
            )
            
            try:
                # Extract the content from the response
                content = response.content if hasattr(response, 'content') else str(response)
                # Try to parse as JSON
                return json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                # Return a structured error response instead of raw JSON
                return {
                    "error": "Failed to parse template structure",
                    "raw_response": content
                }
            
        except Exception as e:
            logger.error(f"Error parsing template: {str(e)}")
            return {
                "error": f"Failed to parse template: {str(e)}",
                "raw_response": None
            }
    
    async def _arun(self, template: str) -> str:
        # For synchronous operations, we can just return the _run result
        return self._run(template) 