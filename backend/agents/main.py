import os
import sys
import logging
import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

# Add the parent directory to system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import agent modules
from setup_agent import process_setup_endpoint, SetupRequest
from content_planner import generate_content_schedule, ContentStrategyInput
from config.database import get_user_by_email, store_credentials

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'api.log'))
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs'), exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title="Social Media Manager API",
    description="API for managing social media content and scheduling",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models for API requests
class CredentialsRequest(BaseModel):
    email: str
    credentials: Dict[str, Dict[str, str]]
    posting_email: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )

# Health check endpoint
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    from datetime import datetime
    return {
        "status": "Social Media Manager API is running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Setup endpoint
@app.post("/setup")
async def setup(request: SetupRequest):
    """Process setup and generate content strategy."""
    logger.info(f"Received setup request for email: {request.email}")
    try:
        result = await process_setup_endpoint(request)
        return result
    except HTTPException as e:
        logger.error(f"HTTP exception in setup endpoint: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in setup endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to process setup: {str(e)}")

# Content planner endpoint
@app.post("/content_planner")
async def content_planner(request: ContentStrategyInput):
    """Generate content schedule based on strategy."""
    logger.info(f"Received content planner request for email: {request.email}")
    try:
        result = await generate_content_schedule(request)
        return result
    except HTTPException as e:
        logger.error(f"HTTP exception in content_planner endpoint: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in content_planner endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate content schedule: {str(e)}")

# Store credentials endpoint
@app.post("/store_credentials")
async def store_user_credentials(request: CredentialsRequest):
    """Store user credentials for social media platforms."""
    logger.info(f"Received credentials request for email: {request.email}")
    try:
        # Check if user exists
        user = get_user_by_email(request.email)
        if not user:
            logger.warning(f"User not found for email: {request.email}")
            raise HTTPException(status_code=404, detail="User not found")
        
        user_uuid = user["uuid"]
        posting_email = request.posting_email or request.email
        
        # Store credentials
        creds_id = store_credentials(
            user_uuid=user_uuid,
            email=request.email,
            credentials=request.credentials,
            posting_email=posting_email
        )
        
        logger.info(f"Credentials stored successfully with ID: {creds_id}")
        return {
            "status": "success",
            "message": "Credentials stored successfully",
            "credentials_id": creds_id
        }
    except HTTPException as e:
        logger.error(f"HTTP exception in store_credentials endpoint: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in store_credentials endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to store credentials: {str(e)}")

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info")
      
