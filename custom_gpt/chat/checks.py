from .models import Chat


def check_messages(chat: Chat, messages: list) -> bool:
    db_messages = chat.get_decoded_messages()

    return db_messages == messages

