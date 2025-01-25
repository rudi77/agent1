import asyncio
from pathlib import Path
from agent.repository_agent import RepositoryAgent
import os
from dotenv import load_dotenv
import logging


requirements = """
## 1. Overview

**Name**: `user-service`  
**Description**: A REST API microservice for user management, built with [FastAPI](https://fastapi.tiangolo.com/) and backed by a PostgreSQL database.

---

## 2. Functional Requirements

1. **User Listing (GET /api/users)**
   - **Description**: List all users with support for pagination.
   - **Request Parameters**:  
     - *Optional:*  
       - `page`: Integer specifying the page number (default=1).  
       - `page_size`: Integer specifying the maximum number of items per page (default=10).
   - **Response**:  
     - A JSON array of user objects for the given page.  
     - Pagination metadata (e.g., total count, current page, total pages).

2. **Get User by ID (GET /api/users/{user_id})**
   - **Description**: Retrieve detailed information about a single user, identified by a unique `user_id`.
   - **Path Parameter**:  
     - `user_id`: Unique identifier of the user.
   - **Response**:  
     - A JSON object containing the user’s details.

3. **Create New User (POST /api/users)**
   - **Description**: Create a new user resource.
   - **Request Body**:  
     - JSON object with the following fields:  
       - `username`: String, required.  
       - `email`: String, required (must be unique and in valid email format).  
       - *(Optional)* Additional metadata fields as needed.
   - **Response**:  
     - JSON object containing the newly created user’s details.

4. **Update User (PUT /api/users/{user_id})**
   - **Description**: Update an existing user’s details.
   - **Path Parameter**:  
     - `user_id`: Unique identifier of the user to be updated.
   - **Request Body** (JSON object, fields optional if only partial update is needed, or use PATCH):
     - `username`: String, optional.  
     - `email`: String, optional.
   - **Response**:
     - JSON object containing the updated user details.

5. **Delete User (DELETE /api/users/{user_id})**
   - **Description**: Remove a user from the system.
   - **Path Parameter**:
     - `user_id`: Unique identifier of the user to be deleted.
   - **Response**:
     - Confirmation (e.g., HTTP 204 No Content) that the user was deleted or appropriate error response if not found.

6. **Authentication & Authorization (Future Extension)**
   - **Description**: Secure endpoints with token-based authentication (e.g., JWT) and support role-based access.  
   - *Note*: This requirement can be implemented in future if the service needs protected routes.

7. **Search & Filtering (Future Extension)**
   - **Description**: Provide search functionality on certain fields (e.g., `username`, `email`) and filters (e.g., date ranges).  
   - *Note*: This requirement can be implemented in future if advanced search is required.

---

## 3. Domain Entities

1. **User**
   - **Attributes**:
     - `id` (String/UUID): Primary key, unique identifier for a user.
     - `username` (String): Unique username chosen by the user.
     - `email` (String): Unique, valid email address of the user.
     - `created_at` (Datetime): Timestamp indicating when the user record was created.
     - *(Optional extension)* `updated_at` (Datetime): Timestamp indicating the last update time.
   - **Entity Rules**:
     - `id` should be auto-generated (e.g., UUID) if not provided.
     - `username` and `email` must be unique.
     - `email` must conform to a valid email format.
     - `created_at` is set automatically during record creation.

---

## 4. Non-Functional Requirements

1. **Performance**
   - The service should handle a minimum of 100 requests per second in a typical deployment scenario.
   - Pagination should be used to ensure only a reasonable number of records are returned per request.

2. **Scalability**
   - The service shall be stateless where possible to allow easy scaling (e.g., use of multiple containers behind a load balancer).
   - Database connection pooling must be configured to support concurrent connections efficiently.

3. **Reliability & Availability**
   - The service should include a health-check endpoint (e.g., `/health`) to verify its availability.
   - Graceful error handling and proper status codes must be returned (4xx for client errors, 5xx for server errors, etc.).

4. **Security**
   - **Future**: JWT or OAuth2-based authentication for secure endpoints.
   - Sensitive user data (like passwords or tokens) should be encrypted in transit (HTTPS) and stored securely if required.
   - Input validation and sanitization must be implemented to prevent common security vulnerabilities (SQL injection, XSS, etc.).

5. **Logging & Monitoring**
   - The service should log all incoming requests (method, path, status, response time).
   - Error logs should provide sufficient information to debug issues.
   - Logs should not expose sensitive data (such as tokens or passwords).
   - Consider integration with centralized logging and monitoring (e.g., Prometheus, ELK stack) for production environments.

6. **Maintainability**
   - The codebase should follow FastAPI best practices (e.g., use of Pydantic models, dependency injection).
   - Database schema migrations should be managed (e.g., via [Alembic](https://alembic.sqlalchemy.org/)).
   - The API should be documented with an OpenAPI/Swagger definition, auto-generated by FastAPI.

7. **Testability**
   - Automated tests (unit, integration) should be provided for all endpoints (happy path and error handling).
   - Local testing with an in-memory or lightweight test database (e.g., SQLite) is recommended for CI/CD pipelines.

8. **Deployment**
   - The service should be containerized (Docker) for consistency across environments.
   - Environment variables should be used for configuration (database URL, secrets, etc.) rather than hard-coded values.

---

## 5. System Components & Architecture

1. **FastAPI Application**
   - Main entry point exposing the REST endpoints.
   - Uses Pydantic models for request/response validation.
   - Automatically generates OpenAPI documentation at `/docs` or `/openapi.json`.

2. **Database Layer**
   - PostgreSQL database to store user data.
   - SQLAlchemy as an ORM layer (optional) for cleaner data access and migrations.
   - Alembic (recommended) for database migrations.

3. **Containerization**
   - Dockerfile describing how to build the service image.
   - Docker Compose (or similar) can be used to orchestrate the service and database together.

4. **Configuration**
   - Environment variables: `DATABASE_URL`, `PORT`, etc.
   - Separate configuration for local, staging, and production environments (e.g., `.env` files).

5. **Load Balancer / API Gateway (Optional)**
   - If deploying in a microservices environment, the user-service might sit behind an API gateway such as Kong, NGINX, or a cloud-based load balancer.

6. **CI/CD (Optional)**
   - Automated pipeline to run tests, build the Docker image, and deploy to staging/production.

---

## 6. Summary

The **user-service** provides the essential functionality for user resource management via REST APIs. It is designed to be **modular**, **scalable**, and **secure** by leveraging FastAPI and PostgreSQL. This requirements document covers the **core functional endpoints**, the **domain entity (User)**, and **non-functional requirements** (performance, security, logging, etc.) to ensure a robust and maintainable microservice.

---

*These updated requirements serve as a foundation. As the service evolves, additional features (authentication, audit logs, advanced search, etc.) can be integrated in line with the overall system architecture and business needs.*
"""

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