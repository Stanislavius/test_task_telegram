import json

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

    def analyze_conversation_quality(self, conversation_text: str) -> dict:
        prompt = """You are a JSON response generator. You must respond with ONLY valid JSON, no other text.
        Rules:
        1. Return ONLY the JSON object, no explanations or additional text
        2. The response must be parseable by json.loads()
        3. Do not include markdown, quotes or code blocks

        Analyze this conversation and generate a JSON response with this exact structure:
        {{
            "has_issues": boolean,
            "issues_found": string[],
            "severity": "low" | "medium" | "high",
            "summary": string
        }}

        Analysis criteria:
        - Emotional negativity or customer dissatisfaction
        - Poor quality of manager's consultation
        - Unresponsive or passive manager behavior
        - Communication errors or misunderstandings

        Conversation to analyze:
        {conversation}
        """.format(conversation=conversation_text)

        try:
            result = self.query(prompt)
            return json.loads(result)
        except Exception as e:
            return {
                "has_issues": False,
                "issues_found": [],
                "severity": "none",
                "summary": f"Error analyzing conversation: {str(e)}"
            }


