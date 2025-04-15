# from pymongo import MongoClient
from datetime import datetime
import schedule
import time
import os
import litellm
from langchain.chat_models import ChatLiteLLM
import ast
from backend.agents.text_generator_agent import text_generator
from backend.agents.image_generator_agent import image_generator
# from backend.agents.video_generator_agent import video_generator


# MongoDB connection setup
# client = MongoClient('mongodb://localhost:27017/')  # Update with your MongoDB connection string
# db = client['your_database']  # Replace with your database name
# collection = db['your_collection']  # Replace with your collection name

# Initialize Gemini LLM using LiteLLM
llm = ChatLiteLLM(
    model="gemini/gemini-2.0-flash",
    api_key="AIzaSyDsJwuELEsuTZy59EFTP-zPXKmIFKRUans"
    # api_key=os.getenv("GOOGLE_API_KEY")
)

def content_decider(doc):
    try:
        platform = doc.get('platform', '').lower()
        content_type = doc.get('content_type', '').lower()
        prompt = f"""
        Given the platform '{platform}' and content type '{content_type}', suggest the most appropriate post type or combination
         of post type, choosing only from 'Text', 'Image', or 'Video'. The output can be a single post type (e.g., 'Text') 
         or a combination (e.g., ['Text', 'Image']). If the platform or content type is unknown, infer based on common social 
         media patterns. Always return a Python list, where the list is either contain single string
         type or multiple items. 

        Examples:
        - For platform 'LinkedIn' and content type 'Article', return ['Text', 'Image']
        - For platform 'TikTok' and content type 'Reel', return ['Video']
        - For platform 'Twitter' and content type 'Text', return ['Text']
        Note: Don't give code only provide answer
        Output format: A single Python list containing one string, e.g., ["Text"], ["Text","Image"], ["Text","Video"], etc.
        """
        try:
            llm_response = llm.invoke(prompt)
            # post_types = llm_response.strip().split(", ") or ['text']  # Fallback to ['text']
            post_types = llm_response.content # Fallback to ['text']
        except Exception as e:
            print(f"LLM error: {e}")
            post_types = ['text']  # Fallback

      
        print(f"Parsed post_types: {post_types}")

        # Convert string to list if necessary
        if isinstance(post_types, str):
            post_types = ast.literal_eval(post_types)
        
        system_map = {
            'text': 'text_generator',
            'image': 'image_generator',
            'video': 'video_generator'
        }

        systems_to_call = []

        # Map components to systems
        for post_type in post_types:
            post_type = post_type.lower()  # Convert to lowercase
            if post_type in system_map and system_map[post_type] not in systems_to_call:
                systems_to_call.append(system_map[post_type])

        print("Systems to call:", systems_to_call)                        
        
        # Prepare result
        result = {
            'platform': platform,
            'content_type': content_type,
            'post_types': post_types,
            'systems_to_call': systems_to_call,
            'description': doc.get('description', ''),
            'pillar_or_campaign': doc.get('pillar_or_campaign', '')
        }
        
        print(f"Decision for {platform} ({content_type}):")
        print(f"Post Types: {post_types}")
        print(f"Systems to call: {systems_to_call}")
        
        return result
    
    except Exception as e:
        print(f"Error in content_decider: {str(e)}")
        return {
            'platform': platform,
            'content_type': content_type,
            'post_types': [],
            'systems_to_call': [],
            'error': str(e)
        }

def check_datetime_and_trigger():
    try:
        # Get current datetime (rounded to minute for comparison)
        current_time = datetime.now().replace(second=0, microsecond=0)
        print("*****",current_time)
        
        # # Query MongoDB for matching datetime
        # query = {"datetime": current_time}
        # matching_documents = collection.find(query)
        
        # # Process each matching document
        # for doc in matching_documents:
        #     print(f"Match found for datetime: {current_time}")
        #     # Call content_decider with the document data
        #     content_decider(doc)
        doc = {"platform": "Linkedin",
                "content_type":"Article",
                "pillar_or_campaign":"Ask the Expert",
                "description": "Post about AI Technology",
                "week": 1,
                "day":"Monday",
                "date":"2025-04-15",
                "datetime":"2025-04-15 11:00:00 EST",
                "time":"11:00 AM EST"}
        result = content_decider(doc)
        print(result)
        # Get the values
        platform = result['platform']
        systems_to_call = result['systems_to_call']
        description = result['description']
        for fn in systems_to_call:
            print(fn)
            if fn == 'text_generator':
                text_generator(platform,description)
            elif fn == 'image_generator':
                image_generator(platform,description)
            elif fn == 'video_generator':
                video_generator(platform,description)

        print(f"Error occurred: {str(e)}")

# Schedule the function to run every minute
schedule.every(1).minutes.do(check_datetime_and_trigger)

def main():
    print("Starting scheduler...")
    while True:
        schedule.run_pending()
        time.sleep(1)  # Prevent CPU overload

if __name__ == "__main__":
    main()