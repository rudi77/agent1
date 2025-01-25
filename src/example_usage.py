import asyncio
from pathlib import Path
from agent.repository_agent import RepositoryAgent
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize agent with OpenAI API key
    agent = RepositoryAgent(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model_name="gpt-4o-mini"
    )
    
    # Define requirements for a sample REST API
    requirements = {
        "name": "user-service",
        "description": "A REST API microservice for user management",
        "endpoints": [
            {
                "path": "/api/users",
                "method": "GET",
                "description": "List all users with pagination"
            },
            {
                "path": "/api/users/{user_id}",
                "method": "GET",
                "description": "Get user details by ID"
            },
            {
                "path": "/api/users",
                "method": "POST",
                "description": "Create a new user"
            }
        ],
        "domain_entities": [
            {
                "name": "User",
                "attributes": [
                    {"name": "id", "type": "str"},
                    {"name": "username", "type": "str"},
                    {"name": "email", "type": "str"},
                    {"name": "created_at", "type": "datetime"}
                ]
            }
        ]
    }
    
    try:
        # Create repository
        success = await agent.create_repository(
            requirements=requirements,
            language="python",
            repo_path=Path("./generated/user-service"),
            remote_url=None  # Set this if you want to push to a remote repository
        )
        
        if success:
            logger.info("Repository created successfully!")
        else:
            logger.error("Failed to create repository")
            
    except Exception as e:
        logger.error(f"Error during repository creation: {str(e)}")
        raise

if __name__ == "__main__":    
    asyncio.run(main()) 