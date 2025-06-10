import asyncio
from datetime import datetime, timedelta
from typing import List, Tuple

from telethon import TelegramClient
from telethon.tl.types import User, Dialog

from settings import TelegramScrapingSettings


async def create_client() -> TelegramClient:
    """
    Creates and configures a new Telegram client instance using settings from environment variables.
    """
    settings = TelegramScrapingSettings()

    api_id = settings.api_id
    api_hash = settings.api_hash
    client_name = settings.client_name
    client = TelegramClient(client_name, api_id, api_hash)
    return client


async def get_recent_client_chats(client: TelegramClient, 
                                  chat_limit: int = 10,
                                  history_depth: timedelta = timedelta(days=30),
                                  max_dialog_age: timedelta = timedelta(days=365)
                                  ) -> List[Tuple[Dialog, List]]:
    """
    Fetches recent client chat histories.
    """

    # Use the timezone from Telegram's messages
    dialogs = await client.get_dialogs(limit=1)
    if not dialogs:
        return []


    reference_date = dialogs[0].date
    now = datetime.now(reference_date.tzinfo)
    since_date = now - history_depth
    min_dialog_date = now - max_dialog_age

    dialogs = await client.get_dialogs(limit=100)

    client_chats = []

    for dialog in dialogs:
        if dialog.date < min_dialog_date:
            continue

        if not isinstance(dialog.entity, User):
            continue

        messages = await client.get_messages(
            dialog,
            limit=None,
            offset_date=since_date
        )

        if messages:
            client_chats.append((dialog, messages))

        if len(client_chats) >= chat_limit:
            break

    return client_chats[:chat_limit]


async def main_func():
    """
    Main function that handles the Telegram client connection
    """

    client = await create_client()

    async with client:
        # Get recent chats
        recent_chats = await get_recent_client_chats(client)


if __name__ == "__main__":
    asyncio.run(main_func())
