import asyncio
import speech_recognition as sr
from gtts import gTTS
import pygame
import os
from datetime import datetime, timedelta
import colorama
import json
from colorama import Fore, Style
import openai
from threading import Event

openai.api_key = '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'

class SlotsManager:
    def __init__(self):
        self.slots_data = {
            datetime.now().strftime('%Y-%m-%d'): [
                "9:00 a.m.", "10:00 a.m.", "11:00 a.m.", "4:00 p.m."
            ],
            (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'): [
                "9:00 a.m.", "10:00 a.m."
            ]
        }

    def get_available_slots(self, date):
        return self.slots_data.get(date, [])

    def book_slot(self, date, time):
        available_slots = self.slots_data.get(date, [])
        if time in available_slots:
            available_slots.remove(time)
            return True
        return False

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.slots_manager = SlotsManager()
        pygame.mixer.init()
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 300
        self.speaking_event = Event()
        print(Fore.GREEN + "\n=== Voice Assistant Initialized ===" + Style.RESET_ALL)

    async def speak(self, text):
        print(Fore.GREEN + f"\n🤖 Assistant: {text}" + Style.RESET_ALL)
        tts = gTTS(text=text, lang='en')
        temp_file = "response.mp3"
        tts.save(temp_file)
        
        self.speaking_event.set() 
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy() and self.speaking_event.is_set():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.music.stop()
        self.speaking_event.clear()
        os.remove(temp_file)

    async def listen_streaming(self):
        with sr.Microphone() as source:
            print(Fore.YELLOW + "🎤 Listening... (Speak now)" + Style.RESET_ALL)
            try:
                if self.speaking_event.is_set():
                    self.speaking_event.clear()
                    pygame.mixer.music.stop()
                
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                return audio
            except sr.WaitTimeoutError:
                return None

    async def speech_to_text(self, audio):
        if not audio:
            return None
        try:
            text = self.recognizer.recognize_google(audio)
            print(Fore.BLUE + f"👤 You said: {text}" + Style.RESET_ALL)
            return text.lower()
        except (sr.UnknownValueError, sr.RequestError) as e:
            print(Fore.RED + f"Speech recognition error: {e}" + Style.RESET_ALL)
            return None


    async def process_text(self, text):
        if not text:
            return {"intent": "NO_SPEECH", "time": None, "date": None}

        prompt = f"""
        Analyze the user query and extract structured data in JSON format:
        {{
            "intent": "<book_slot/available_slots/hate_speech/gratitude/small_talk>",
            "time": "<time or None>",
            "date": "<date or None>"
        }}

        Examples:
            Input: "I want to book a slot."
            Output: {{"intent": "book_slot", "time": "None", "date": "None"}}

            Input: "I want to know available slots for today."
            Output: {{"intent": "available_slots", "time": "None", "date": "today"}}

            Input: "I hate this service."
            Output: {{"intent": "hate_speech", "time": "None", "date": "None"}}

            Input: "Thank you so much!"
            Output: {{"intent": "gratitude", "time": "None", "date": "None"}}

            Input: "How are you doing?"
            Output: {{"intent": "small_talk", "time": "None", "date": "None"}}

            Input: "Exit?"
            Output: {{"intent": "log_off", "time": "None", "date": "None"}}

            Input: "I'm heading off?"
            Output: {{"intent": "log_off", "time": "None", "date": "None"}}
            Input: "Goota go?"

            Output: {{"intent": "log_off", "time": "None", "date": "None"}}
            Input: "Good night?"
            Output: {{"intent": "log_off", "time": "None", "date": "None"}}

            Input: "Goodbye?"
            Output: {{"intent": "log_off", "time": "None", "date": "None"}}
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

            # Parse the JSON from the response content
            # parsed_output = json.loads(raw_output)
            # print("parsed_otuput", parsed_output)
            # print("raw_output", raw_output)
            return raw_output

        except json.JSONDecodeError:
            print(Fore.RED + "Error: Failed to decode JSON from model output." + Style.RESET_ALL)
            return {"intent": "UNRECOGNISED", "time": None, "date": None}
        except Exception as e:
            print(Fore.RED + f"Error processing intent with LLM: {e}" + Style.RESET_ALL)
            return {"intent": "UNRECOGNISED", "time": None, "date": None}


    async def handle_response(self, intent_data):
        intent_data = json.loads(intent_data)

        intent = intent_data.get("intent")
        time = intent_data.get("time")
        date = intent_data.get("date")

        print(f"Received intent: {intent}, time: {time}, date: {date}")

        if not date or date.lower() == "none" or date.lower() == "today":
            date = datetime.now().strftime('%Y-%m-%d')
            print("Setting default date:", date)

        response = ""

        if intent == "book_slot":
            available_slots = self.slots_manager.get_available_slots(date)

            if not available_slots:
                response = f"Unfortunately, there are no available slots for {date}."
            else:
                if not time or time.lower() == "none":
                    response = f"Here are the available slots for {date}: {', '.join(available_slots)}. Please specify a time."
                else:
                    if time in available_slots:
                        if self.slots_manager.book_slot(date, time):
                            response = f"Your appointment has been successfully booked for {time} on {date}."
                        else:
                            response = f"Sorry, {time} on {date} is already booked."
                    else:
                        response = f"The time {time} is not available for {date}. Here are the available slots: {', '.join(available_slots)}."

        elif intent == "available_slots":
            if date == 'today':
                date = datetime.now().strftime('%Y-%m-%d')
            if date == 'tomorrow':
                date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')


            available_slots = self.slots_manager.get_available_slots(date)
            if available_slots:
                response = f"Available slots for {date} are: {', '.join(available_slots)}."
            else:
                response = f"No available slots for {date}."

        elif intent == "hate_speech":
            response = "Please refrain from using offensive language. Let's keep the conversation respectful."

        elif intent == "gratitude":
            response = "You're very welcome! Let me know if you need further assistance."

        elif intent == "small_talk":
            response = "How's it going? How can I assist you today?"
        
        elif intent == "log_off":
            return "EXIT"
            # await self.speak(response)

        else:
            response = "Sorry, I couldn't understand your request. Could you please rephrase?"

        await self.speak(response)
        return intent

    async def handle_inactivity(self):
        await self.speak("Can you hear me? Could you please let me know what you are looking for?")
        await asyncio.sleep(3.5)
        return await self.listen_streaming()

    async def run(self):
        welcome_message_done = False

        while True:
            try:
                if not welcome_message_done:
                    welcome_task = asyncio.create_task(
                        self.speak("Hi there")
                    )
                    await welcome_task
                    welcome_message_done = True

                audio = await self.listen_streaming()
                count = True
                if audio is None and count is True:
                    await self.speak("Can you hear me? Could you please let me know?")
                    count = False
                    audio = await self.listen_streaming()

                if audio is None:
                    await self.speak("It seems like you're not responding. Goodbye!")
                    break

                text = await self.speech_to_text(audio)
                if text:
                    intent = await self.process_text(text)
                    result = await self.handle_response(intent)
                    if result == "EXIT":
                        await self.speak("Goodbye! Have a great day!")
                        break

            except KeyboardInterrupt:
                await self.speak("Goodbye! Have a great day!")
                break
            except Exception as e:
                print(Fore.RED + f"❌ An error occurred: {e}" + Style.RESET_ALL)
                continue


def main():
    assistant = VoiceAssistant()
    asyncio.run(assistant.run())

if __name__ == "__main__":
    main()
