import asyncio
from datetime import datetime, timedelta
from threading import Event
from colorama import Fore, Style
import json
from stt import SpeechToText
from tts import TextToSpeech
from intent_processor import IntentProcessor
from slots_manager import SlotsManager

class VoiceAssistant:
    def __init__(self):
        self.speaking_event = Event()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.intent_processor = IntentProcessor()
        self.slots_manager = SlotsManager()

        print(Fore.GREEN + "\n=== Voice Assistant Initialized ===" + Style.RESET_ALL)

    async def handle_response(self, intent_data):
        intent_data = json.loads(intent_data)

        intent = intent_data.get("intent")
        time = intent_data.get("time")
        date = intent_data.get("date")

        if not date or date.lower() == "none":
            date = datetime.now().strftime('%Y-%m-%d')

        response = ""
        if intent == "book_slot":
            available_slots = self.slots_manager.get_available_slots(date)
            if not available_slots:
                response = f"Unfortunately, there are no available slots for {date}."
            else:
                if not time or time.lower() == "none":
                    response = f"Here are the available slots for {date}: {', '.join(available_slots)}. Please specify a time."
                else:
                    if time in available_slots and self.slots_manager.book_slot(date, time):
                        response = f"Your appointment has been successfully booked for {time} on {date}."
                    else:
                        response = f"The time {time} is not available for {date}. Available slots: {', '.join(available_slots)}."
        elif intent == "available_slots":
            available_slots = self.slots_manager.get_available_slots(date)
            response = f"Available slots for {date}: {', '.join(available_slots)}." if available_slots else f"No available slots for {date}."
        elif intent == "hate_speech":
            response = "Please refrain from offensive language."
        elif intent == "gratitude":
            response = "You're welcome!"
        elif intent == "small_talk":
            response = "How can I assist you today?"
        elif intent == "log_off":
            return "EXIT"
        else:
            response = "I couldn't understand your request. Please try again."

        await self.tts.speak(response, self.speaking_event)
        return intent

    async def run(self):
        await self.tts.speak("Hi there!", self.speaking_event)
        while True:
            audio = await self.stt.listen_streaming(self.speaking_event)
            if not audio:
                await self.tts.speak("Can you hear me?", self.speaking_event)
                audio = await self.stt.listen_streaming(self.speaking_event)
                if not audio:
                    await self.tts.speak("Goodbye!", self.speaking_event)
                    break
            text = await self.stt.speech_to_text(audio)
            if text:
                intent = await self.intent_processor.process_text(text)
                result = await self.handle_response(intent)
                if result == "EXIT":
                    await self.tts.speak("Goodbye!", self.speaking_event)
                    break

if __name__ == "__main__":
    assistant = VoiceAssistant()
    asyncio.run(assistant.run())
