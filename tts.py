import os
from gtts import gTTS
import pygame
from colorama import Fore, Style

class TextToSpeech:
    def __init__(self):
        pygame.mixer.init()

    async def speak(self, text, speaking_event):
        """Convert text to speech and play it."""
        print(Fore.GREEN + f"\n🤖 Assistant: {text}" + Style.RESET_ALL)
        tts = gTTS(text=text, lang='en')
        temp_file = "response.mp3"
        tts.save(temp_file)
        
        speaking_event.set()
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy() and speaking_event.is_set():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.music.stop()
        speaking_event.clear()
        os.remove(temp_file)
