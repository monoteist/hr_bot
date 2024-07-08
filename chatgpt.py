from config import OPEN_AI_TOKEN

from app.utils.openai_manager import OpenaiClient

client = OpenaiClient(api_key=OPEN_AI_TOKEN)

client.async_client