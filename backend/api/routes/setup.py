from fastapi import APIRouter, UploadFile, File, Form
from agents.setup_agent import process_setup
from typing import List
import json

router = APIRouter(prefix="/setup", tags=["setup"])

@router.post("/")
async def setup(
    json_data: str = Form(...),  # JSON string from frontend
    logos: List[UploadFile] = File(None),
    fonts: List[UploadFile] = File(None),
    templates: List[UploadFile] = File(None),
    past_data: UploadFile = File(None)
):
    # Parse JSON data from the frontend
    data = json.loads(json_data)

    # Call the process_setup function directly (no agent instantiation needed with CrewAI)
    result = await process_setup(
        brand_guidelines=data["brand_guidelines"],
        goals=data["goals"],
        target_audience=data["target_audience"],
        platforms=data["platforms"],
        logos=logos,
        fonts=fonts,
        templates=templates,
        past_data=past_data
    )

    # Return the result in the expected format
    return {
        "brand_voice_profile": result["brand_voice_profile"],
        "content_strategy": result["content_strategy"],
        "message": "Setup completed"
    }