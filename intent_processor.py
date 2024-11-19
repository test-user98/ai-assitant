import openai
from colorama import Fore, Style
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')


class IntentProcessor:
    async def process_text(self, text):
        """Process user input text to extract intent."""
        if not text:
            return {"intent": "NO_SPEECH", "time": None, "date": None}

        prompt = f"""
        Analyze the user query and extract structured data in JSON format:
        {{
            "intent": "<book_slot/available_slots/hate_speech/gratitude/small_talk/log_off>",
            "time": "<time or None>",
            "date": "<date or None>"
        }}
        Input: "{text}"
        Output:
        """
        try:
            response = await asyncio.to_thread(
                openai.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0,
            )
            raw_output = response.choices[0].message.content.strip()
            print(Fore.CYAN + f"Detected Output: {raw_output}" + Style.RESET_ALL)

            return raw_output
        except Exception as e:
            print(Fore.RED + f"Error processing intent with LLM: {e}" + Style.RESET_ALL)
            return {"intent": "UNRECOGNISED", "time": None, "date": None}
