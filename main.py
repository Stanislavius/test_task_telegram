import asyncio
from datetime import datetime, timedelta
from typing import List, Tuple, Dict

from telethon import TelegramClient
from telethon.tl.types import User, Dialog, Message

from gemini_wrapper import GeminiWrapper
from manager_performance import ManagerPerformanceAnalyzer
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

    dialogs = await client.get_dialogs(limit=1000)

    client_chats = []

    for dialog in dialogs:
        if dialog.date < min_dialog_date:
            continue

        if not isinstance(dialog.entity, User) or dialog.entity.bot:
            continue

        messages = await client.get_messages(
            dialog,
            limit=None,
            offset_date=since_date,
            reverse=True
        )

        if messages:
            client_chats.append((dialog, messages))

        if len(client_chats) >= chat_limit:
            break

    return client_chats[:chat_limit]


def format_conversation_to_strings(dialog: Dialog, messages: List[Message], my_id: int) -> List[str]:
    """
    Formats a Telegram conversation into a list of formatted strings.

    Args:
        dialog: Telegram dialog object
        messages: List of messages in the conversation
        my_id: ID of the manager's account

    Returns:
        List of strings in format "[HH:MM] Role: Message"
    """
    formatted_messages = []

    for message in messages:
        # Skip empty messages
        if not message.message:
            continue

        # Get message time
        time_str = message.date.strftime("%m/%d %H:%M")

        # Determine sender role
        sender_role = "Manager" if message.from_id and message.from_id.user_id == my_id else "Client"

        # Format the message
        formatted_line = f"[{time_str}] {sender_role}: {message.message}"
        formatted_messages.append(formatted_line)

    return formatted_messages


async def format_all_conversations(client_chats: List[Tuple[Dialog, List[Message]]], my_id: int) -> Dict[
    str, List[str]]:
    """
    Formats all conversations into strings.

    Returns:
        Dictionary where key is client name/id and value is list of formatted message strings
    """
    formatted_dialogs = {}

    for dialog, messages in client_chats:
        client_name = dialog.name or f"Client_{dialog.id}"
        formatted_messages = format_conversation_to_strings(dialog, messages, my_id)
        formatted_dialogs[client_name] = formatted_messages

    return formatted_dialogs


async def get_conversions_for_analysis(client: TelegramClient, client_chats: List[Tuple[Dialog, List[Message]]] = None):
    # Get manager's ID
    me = await client.get_me()
    my_id = me.id

    # Format conversations for analysis
    formatted_conversations = await format_all_conversations(client_chats, my_id)

    return formatted_conversations


async def main_func():
    """
    Main function that handles the Telegram client connection
    """
    client = await create_client()

    async with client:
        # Get manager's ID
        me = await client.get_me()
        my_id = me.id

        # Get recent chats
        client_chats = await get_recent_client_chats(client)
        all_analytics = {}

        gemini_wrapper = GeminiWrapper()

        for dialog, messages in client_chats:
            # Convert messages to text for AI analysis
            formatted_messages = format_conversation_to_strings(dialog, messages, my_id)
            text = "\n".join(formatted_messages)

            # Perform manager performance analysis
            analyzer = ManagerPerformanceAnalyzer(messages, my_id)
            performance_metrics = analyzer.analyze()

            client_name = dialog.name or f"Client_{dialog.id}"
            all_analytics[client_name] = {
                'performance': performance_metrics,
                'has_unfinished_promises': gemini_wrapper.check_unfinished_promises(text),
                'quality_analysis': gemini_wrapper.analyze_conversation_quality(text)
            }

        # Print summary report
        print("\n=== Manager Performance Analysis ===")
        for client_name, analytics in all_analytics.items():
            print(f"\nChat with {client_name}:")
            print(analytics['performance']['summary'])
            if analytics['has_unfinished_promises']:
                print("⚠️ Has unfinished promises")
            if analytics['quality_analysis']['has_issues']:
                print("⚠️ Has quality issues:", analytics['quality_analysis']['issues_found'])
            print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main_func())