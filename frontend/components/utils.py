import requests

BASE_URL = "http://localhost:8000"  # Adjust to your FastAPI backend URL

def make_api_call(method, endpoint, data=None, files=None):
    url = f"http://localhost:8000{endpoint}"
    print(f"Calling API: {url}")
    return requests.post(url, data=data, files=files)
