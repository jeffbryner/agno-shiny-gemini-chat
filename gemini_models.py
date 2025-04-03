from agno.models.google import Gemini
from google import genai
from google.genai import types
import google.auth

credentials, PROJECT_ID = google.auth.default()
GEMINI_PRO = "gemini-1.5-pro"
GEMINI_FLASH = "gemini-2.0-flash"

generation_config = types.GenerateContentConfig(
    temperature=0,
    top_p=0.1,
    top_k=1,
    max_output_tokens=4096,
)

safety_settings = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_UNSPECIFIED,
        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
]

# init for Vertex AI API
# client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")

model_pro = Gemini(
    id=GEMINI_PRO,
    vertexai=True,
    project_id=PROJECT_ID,
    location="us-central1",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

model_flash = Gemini(
    id=GEMINI_FLASH,
    vertexai=True,
    project_id=PROJECT_ID,
    location="us-central1",
    generation_config=generation_config,
    safety_settings=safety_settings,
)
