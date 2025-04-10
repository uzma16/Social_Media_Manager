from fastapi import FastAPI
from api.routes.setup import router as setup_router
from config.database import get_db_connection

# Initialize FastAPI app
app = FastAPI(title="Social Media Manager API")

# Include routers for each step (Step 1 for now)
app.include_router(setup_router)

# Test endpoint to verify the server is running
@app.get("/")
async def root():
    return {"message": "Social Media Manager API is running"}

# # Optional: Startup event to check database connection
# @app.on_event("startup")
# async def startup_event():
#     db = get_db_connection()
#     try:
#         db.cursor()  # Test connection
#         print("Database connection established successfully")
#     except Exception as e:
#         print(f"Database connection failed: {e}")
#     finally:
#         db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)