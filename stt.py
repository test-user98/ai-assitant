import speech_recognition as sr
from colorama import Fore, Style

class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 300

    async def listen_streaming(self, speaking_event):
        """Listen to the user via the microphone."""
        with sr.Microphone() as source:
            print(Fore.YELLOW + "🎤 Listening... (Speak now)" + Style.RESET_ALL)
            try:
                if speaking_event.is_set():
                    speaking_event.clear()
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                return audio
            except sr.WaitTimeoutError:
                return None

    async def speech_to_text(self, audio):
        """Convert speech audio to text."""
        if not audio:
            return None
        try:
            text = self.recognizer.recognize_google(audio)
            print(Fore.BLUE + f"👤 You said: {text}" + Style.RESET_ALL)
            return text.lower()
        except (sr.UnknownValueError, sr.RequestError) as e:
            print(Fore.RED + f"Speech recognition error: {e}" + Style.RESET_ALL)
            return None
