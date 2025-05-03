import os
import uuid
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "social_media_manager")

def get_db_connection():
    """Get MongoDB connection."""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        return client, db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email."""
    try:
        client, db = get_db_connection()
        user = db.users.find_one({"email": email})
        client.close()
        return user
    except Exception as e:
        logger.error(f"Error getting user by email: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def create_user(email: str) -> Dict:
    """Create a new user."""
    try:
        client, db = get_db_connection()
        user_uuid = str(uuid.uuid4())
        user = {
            "uuid": user_uuid,
            "email": email,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        db.users.insert_one(user)
        client.close()
        return user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def store_setup(user_uuid: str, email: str, setup_data: Dict, content_strategy: str) -> str:
    """Store setup data and content strategy."""
    try:
        client, db = get_db_connection()
        
        # Create setup document
        setup = {
            "user_uuid": user_uuid,
            "email": email,
            "brand_guidelines": setup_data.get("brand_guidelines", {}),
            "goals": setup_data.get("goals", ""),
            "target_audience": setup_data.get("target_audience", {}),
            "platforms": setup_data.get("platforms", []),
            "special_instructions": setup_data.get("special_instructions", ""),
            "content_strategy": content_strategy,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Insert or update setup
        result = db.setups.update_one(
            {"user_uuid": user_uuid},
            {"$set": setup},
            upsert=True
        )
        
        # Get the ID of the inserted/updated document
        if result.upserted_id:
            setup_id = str(result.upserted_id)
        else:
            setup_doc = db.setups.find_one({"user_uuid": user_uuid})
            setup_id = str(setup_doc["_id"])
        
        client.close()
        return setup_id
    except Exception as e:
        logger.error(f"Error storing setup: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def store_schedule(user_uuid: str, email: str, strategy_text: str, posts: List[Dict], 
                  time_period: str = "2 Weeks", post_frequency: str = "3 times per week",
                  special_instructions: Optional[str] = None) -> str:
    """Store content schedule."""
    try:
        client, db = get_db_connection()
        
        # Create schedule document
        schedule = {
            "user_uuid": user_uuid,
            "email": email,
            "strategy_text": strategy_text,
            "posts": posts,
            "time_period": time_period,
            "post_frequency": post_frequency,
            "special_instructions": special_instructions,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Insert schedule
        result = db.schedules.insert_one(schedule)
        schedule_id = str(result.inserted_id)
        
        client.close()
        return schedule_id
    except Exception as e:
        logger.error(f"Error storing schedule: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def store_credentials(user_uuid: str, email: str, credentials: Dict, posting_email: str) -> str:
    """Store platform credentials."""
    try:
        client, db = get_db_connection()
        
        # Create credentials document
        creds_doc = {
            "user_uuid": user_uuid,
            "email": email,
            "credentials": credentials,
            "posting_email": posting_email,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Insert or update credentials
        result = db.credentials.update_one(
            {"user_uuid": user_uuid},
            {"$set": creds_doc},
            upsert=True
        )
        
        # Get the ID of the inserted/updated document
        if result.upserted_id:
            creds_id = str(result.upserted_id)
        else:
            creds_doc = db.credentials.find_one({"user_uuid": user_uuid})
            creds_id = str(creds_doc["_id"])
        
        client.close()
        return creds_id
    except Exception as e:
        logger.error(f"Error storing credentials: {str(e)}")
        logger.error(traceback.format_exc())
        raise
