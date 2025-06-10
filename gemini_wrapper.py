from datetime import datetime
from typing import List, Dict

import google.generativeai as genai

from settings import TelegramScrapingSettings

settings = TelegramScrapingSettings()

genai.configure(api_key=settings.gemini_key)


class GeminiWrapper:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash-latest")
        self.used_models = []

    def query(self, query: str) -> str:
        while True:
            try:
                response = self.model.generate_content(query)
                return response.text
            except Exception as e:
                self.used_models.append(self.model.model_name)
                models = genai.list_models()
                for model in models:
                    if 'generateContent' in model.supported_generation_methods:
                        if model not in self.used_models:
                            self.model = genai.GenerativeModel(model.name)
                self.used_models = []
                raise e

    def check_unfinished_promises(self, conversation_text: str) -> bool:

        prompt = """
        Analyze this conversation and determine if:
        1. The manager promised to do something by the end of the day
        2. The promise wasn't fulfilled in the conversation

        Return "true" if there's an unfulfilled promise, "false" otherwise.

        Conversation:
        {conversation}
        """.format(conversation=conversation_text)

        result = self.query(prompt)
        return result.lower().strip() == "true"

