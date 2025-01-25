from langchain.agents import AgentType, create_structured_chat_agent
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from pathlib import Path
from typing import Dict, Optional, Any, List
import logging
from pydantic import BaseModel, Field

from .tools.git_tools import InitRepoTool, GitCommitTool, GitPushTool
from .tools.file_tools import CreateDirectoriesTool, WriteFileTool, LoadTemplateTool
from .tools.template_tools import ParseTemplateTool
from .tools.code_generation_tools import GenerateCodeTool, GenerateDocumentationTool
from langchain.agents import AgentExecutor
from langchain.schema import AgentAction, AgentFinish
from langchain.tools.render import format_tool_to_openai_function

logger = logging.getLogger(__name__)

SYSTEM_MESSAGE = """You are an expert software developer assistant that helps create well-structured repositories.
Follow the instructions carefully and use the available tools to complete the tasks.
Make sure to handle errors gracefully and maintain a clean repository state.

You have access to the following tools:

{tool_descriptions}

Use these tools to help you complete the tasks. Always handle errors gracefully.

After completing all tasks, summarize what you've done and any important notes about the created repository."""

class RepositoryAgent(BaseModel):
    openai_api_key: str
    model_name: str = "gpt-4-turbo-preview"
    templates_dir: str = "templates"
    
    def model_post_init(self, __context) -> None:
        # Initialize private attributes after model initialization
        object.__setattr__(self, '_llm', ChatOpenAI(
            temperature=0,
            model_name=self.model_name,
            openai_api_key=self.openai_api_key
        ))
        
        # Initialize tools
        tools = [
            InitRepoTool(),
            GitCommitTool(),
            GitPushTool(),
            CreateDirectoriesTool(),
            WriteFileTool(),
            LoadTemplateTool(templates_dir=self.templates_dir),
            GenerateCodeTool(self.model_name, self.openai_api_key),
            GenerateDocumentationTool(self.model_name, self.openai_api_key),
            ParseTemplateTool(self.model_name, self.openai_api_key)
        ]
        object.__setattr__(self, '_tools', tools)
        
        # Initialize memory
        object.__setattr__(self, '_memory', ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        ))
        
        # Create tool descriptions
        tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in tools])
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_MESSAGE.format(tool_descriptions=tool_descriptions)),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent with OpenAI functions
        from langchain.agents import create_openai_functions_agent
        agent = create_openai_functions_agent(
            llm=self._llm,
            tools=tools,
            prompt=prompt
        )
        
        # Create the agent executor with proper output keys
        object.__setattr__(self, '_agent_executor', AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self._memory,
            verbose=True,
            handle_parsing_errors=True,
            return_intermediate_steps=False  # Changed to False to avoid memory issues
        ))
    
    async def create_repository(self,
                              requirements: Dict,
                              language: str,
                              repo_path: Path,
                              remote_url: Optional[str] = None) -> bool:
        """
        Create a new repository with generated code based on requirements
        """
        try:
            instruction = f"""
            Create a new {language} project repository at {repo_path} with these requirements:
            {requirements}
            
            Follow these steps:
            1. Initialize a Git repository at {repo_path}
            2. Load and analyze the template for {language} to understand the required structure
            3. Create the directory structure according to the template's hexagonal architecture
            4. Generate source code files following clean architecture principles
            5. Generate comprehensive documentation including README and architecture docs
            6. Commit all changes with appropriate messages
            7. If remote URL is provided ({remote_url}), push the changes
            
            Ensure that:
            - The code follows hexagonal architecture as described in the template
            - All necessary layers (domain, application, infrastructure) are properly implemented
            - The project structure matches the template guidelines
            - Documentation clearly explains the architecture and setup
            
            Handle any errors gracefully and maintain a clean repository state.
            """
            
            # Use ainvoke instead of arun
            result = await self._agent_executor.ainvoke({"input": instruction})
            
            # Log the result for debugging
            logger.info(f"Agent execution result: {result}")
            
            # Extract the output from the result dictionary
            output = result.get("output", "")
            if isinstance(output, str):
                return "error" not in output.lower() and "stopped due to" not in output.lower()
            return False
            
        except Exception as e:
            logger.error(f"Error in create_repository: {str(e)}")
            raise 