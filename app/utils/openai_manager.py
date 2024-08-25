from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessage
from openai import APITimeoutError, APIError

class OpenaiClient:
    def __init__(self, api_key: str):
        self.async_client: AsyncOpenAI = AsyncOpenAI(api_key=api_key)

    async def async_get_response(self, messages: list, max_retries: int = 3) -> ChatCompletionMessage:
        """
        Отправляет запрос к OpenAI и возвращает ответ. В случае тайм-аута или других ошибок
        повторяет запрос до max_retries раз.

        :param messages: Список сообщений для отправки в OpenAI.
        :param max_retries: Максимальное количество попыток в случае ошибки.
        :return: Сообщение от OpenAI.
        """
        for attempt in range(max_retries):
            try:
                completion = await self.async_client.chat.completions.create(
                    model='gpt-3.5-turbo',
                    messages=messages
                )
                return completion.choices[0].message
            except APITimeoutError:
                if attempt < max_retries - 1:
                    print(f"Timeout occurred. Retrying {attempt + 1}/{max_retries}...")
                else:
                    raise
            except APIError as e:
                # Обработка других ошибок API
                print(f"API error occurred: {e}")
                raise
