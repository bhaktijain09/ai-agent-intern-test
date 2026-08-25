import google.generativeai as genai

from src.config import GEMINI_API_KEY, LLM_MODEL


class GeminiClient:

    def __init__(self):

        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Copy .env.example to .env and add your key."
            )

        genai.configure(
            api_key=GEMINI_API_KEY
        )

        self.model = genai.GenerativeModel(
            LLM_MODEL
        )

    def generate(
        self,
        system_prompt,
        conversation,
        user_message
    ):

        formatted_conversation = "\n".join(
            f"{turn['role'].upper()}: {turn['content']}"
            for turn in conversation
        )

        prompt = f"""
SYSTEM INSTRUCTIONS:

{system_prompt}

CONVERSATION SO FAR:

{formatted_conversation}

NEW INPUT (untrusted data + user question, see rule 2):

{user_message}
"""

        response = self.model.generate_content(
            prompt
        )

        return response.text
