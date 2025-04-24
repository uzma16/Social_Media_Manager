from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from bson import ObjectId
from datetime import datetime
import os
from uuid import uuid4
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
try:
    client = MongoClient(MONGO_URI)
    # Test the connection
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB")
except ConnectionFailure as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

db = client["social_media_manager"]

# Collections
users_collection = db["users"]
setups_collection = db["setups"]
schedules_collection = db["schedules"]
credentials_collection = db["credentials"]

def get_user_by_email(email: str):
    """Retrieve a user by email."""
    try:
        user = users_collection.find_one({"email": email})
        logger.info(f"User lookup for email {email}: {user}")
        return user
    except PyMongoError as e:
        logger.error(f"Error retrieving user by email {email}: {str(e)}")
        raise

def create_user(email: str):
    """Create a new user with a UUID and return the user document."""
    try:
        uuid = str(uuid4())
        user = {
            "uuid": uuid,
            "email": email,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        users_collection.insert_one(user)
        logger.info(f"Created user with email {email} and UUID {uuid}")
        return user
    except PyMongoError as e:
        logger.error(f"Error creating user with email {email}: {str(e)}")
        raise

def store_setup(user_uuid: str, email: str, setup_data: dict, content_strategy: str):
    """Store setup data and content strategy."""
    try:
        setup = {
            "user_uuid": user_uuid,
            "email": email,
            "brand_guidelines": setup_data.get("brand_guidelines", {}),
            "goals": setup_data.get("goals", ""),
            "target_audience": setup_data.get("target_audience", {}),
            "platforms": setup_data.get("platforms", []),
            "content_strategy": content_strategy,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = setups_collection.insert_one(setup)
        logger.info(f"Stored setup for user {email} with ID {result.inserted_id}")
        return str(result.inserted_id)
    except PyMongoError as e:
        logger.error(f"Error storing setup for user {email}: {str(e)}")
        raise

def store_schedule(user_uuid: str, email: str, strategy_text: str, posts: list):
    """Store content schedule."""
    try:
        schedule = {
            "user_uuid": user_uuid,
            "email": email,
            "strategy_text": strategy_text,
            "posts": posts,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = schedules_collection.insert_one(schedule)
        logger.info(f"Stored schedule for user {email} with ID {result.inserted_id}")
        return str(result.inserted_id)
    except PyMongoError as e:
        logger.error(f"Error storing schedule for user {email}: {str(e)}")
        raise

def store_credentials(user_uuid: str, email: str, credentials: dict, posting_email: str = None):
    """Store platform credentials or posting email."""
    try:
        credential = {
            "user_uuid": user_uuid,
            "email": email,
            "credentials": credentials,
            "posting_email": posting_email,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = credentials_collection.insert_one(credential)
        logger.info(f"Stored credentials for user {email} with ID {result.inserted_id}")
        return str(result.inserted_id)
    except PyMongoError as e:
        logger.error(f"Error storing credentials for user {email}: {str(e)}")
        raise