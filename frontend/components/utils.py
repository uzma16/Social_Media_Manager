import requests

BASE_URL = "http://localhost:8000"  # Adjust to your FastAPI backend URL

def make_api_call(method, endpoint, data=None, files=None):
    url = f"{BASE_URL}{endpoint}"
    if method == "POST":
        return requests.post(url, data=data, files=files)
    return None  # Add other methods (GET, etc.) as needed