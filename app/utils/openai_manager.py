from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessage


class OpenaiClient:
    def __init__(self, api_key: str):
        self.async_client: AsyncOpenAI = AsyncOpenAI(api_key=api_key)

    async def async_get_response(self, messages: list) -> ChatCompletionMessage:
        completion = await self.async_client.chat.completions.create(
            model='gpt-4o',
            messages=messages
        )
        return completion.choices[0].message
