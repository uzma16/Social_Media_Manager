# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from setup_agent import process_setup_endpoint, SetupRequest
# from content_planner import ContentStrategyInput
# from content_planner import generate_content_schedule

# # Initialize FastAPI app
# app = FastAPI(title="Social Media Manager API")

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:8501"],  # Streamlit default port
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Define the endpoint with the correct path
# @app.post("/process_setup")
# async def setup_endpoint(request: SetupRequest):
#     print("Received request:", request)  # Debug print
#     try:
#         result = await process_setup_endpoint(request)
#         return result
#     except Exception as e:
#         print("Error processing request:", str(e))  # Debug print
#         raise


# @app.post("/content_planner")
# async def content_planner_endpoint(input_data: ContentStrategyInput):
#     try:
#         result = generate_content_schedule(strategy_text=input_data.strategy)
#         return result
#     except Exception as e:
#         print("Error processing request:", str(e))  # Debug print
#         raise

# # Test endpoint
# @app.get("/")
# async def root():
#     return {"message": "Social Media Manager API is running"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from setup_agent import process_setup_endpoint, SetupRequest
from content_planner import ContentStrategyInput, generate_content_schedule
from pydantic import BaseModel
from config.database import get_user_by_email, store_credentials
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="Social Media Manager API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CredentialsRequest(BaseModel):
    email: str
    credentials: dict
    posting_email: str = None

@app.post("/process_setup")
async def setup_endpoint(request: SetupRequest):
    print("Received request:", request)
    try:
        result = await process_setup_endpoint(request)
        return result
    except Exception as e:
        print("Error processing request:", str(e))
        raise

@app.post("/content_planner")
async def content_planner_endpoint(input_data: ContentStrategyInput):
    try:
        result = generate_content_schedule(email=input_data.email, strategy_text=input_data.strategy)
        return result
    except Exception as e:
        print("Error processing request:", str(e))
        raise

@app.post("/store_credentials")
async def store_credentials_endpoint(request: CredentialsRequest):
    try:
        user = get_user_by_email(request.email)
        if not user:
            raise ValueError("User not found")
        user_uuid = user["uuid"]
        credential_id = store_credentials(user_uuid, request.email, request.credentials, request.posting_email)
        return {"credential_id": credential_id}
    except Exception as e:
        print("Error processing request:", str(e))
        raise

@app.get("/")
async def root():
    return {"message": "Social Media Manager API is running"}

if __name__ == "__main__":
    uvicorn.run(
        "agents.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
