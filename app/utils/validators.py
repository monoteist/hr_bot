from aiogram.types import Message


def text_message_filter(message: Message) -> bool:
    return message.content_type == 'text'
