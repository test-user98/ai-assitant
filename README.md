
# Voice Assistant:

**DEMO VIDEO**: [https://drive.google.com/file/d/1Taos7sFwtWbJxx6JE8NQgKHipkDViJga/](url)

---

## Features
1. **Audio Input**: 
   - Accepts user input via a microphone using `speech_recognition`.
   - Live audio stream can be added as an enhancement.

2. **Speech-to-Text (STT)**: 
   - Converts spoken audio to text using Google's Speech Recognition API.

3. **Language Model Processing**: 
   - Leverages OpenAI's GPT-3.5 model for natural language understanding.
   - Detects user intent and extracts structured information like:
     - Intent (e.g., `book_slot`, `available_slots`, `gratitude`)
     - Date
     - Time

4. **Slot Management**:
   - Supports querying for available slots using a `SlotsManager` class.
   - Allows booking a specific time slot for a given date.

5. **Text-to-Speech (TTS)**:
   - Uses Google Text-to-Speech (`gTTS`) for generating responses in audio form.
   - Plays the response via `pygame`.

6. **Error Handling**:
   - Handles invalid inputs and gracefully recovers from errors.

7. **Real-time Interaction**:
   - Provides feedback for unrecognized or ambiguous requests.
   - Re-prompts the user if no input is detected.

---

## System Flow

1. **Initialization**:
   - The system initializes the voice assistant and slot management.
   - Plays a welcome message.

2. **Listening for Input**:
   - The assistant continuously listens for audio input.
   - If no response is detected, it re-prompts the user.

3. **Speech-to-Text**:
   - Converts the user's audio input to text using `speech_recognition`.

4. **Language Model Processing**:
   - The text input is passed to the OpenAI GPT-3.5 API.
   - The model analyzes the input and provides structured data (JSON format) containing:
     - Intent
     - Date (if applicable)
     - Time (if applicable)

5. **Intent Handling**:
   - Based on the detected intent, the system performs one of the following actions:
     - **`book_slot`**: Books an available slot if the requested time is valid.
     - **`available_slots`**: Provides a list of available slots for a specific date.
     - **`hate_speech`**: Responds with a warning about respectful language.
     - **`gratitude`**: Acknowledges the user's gratitude.
     - **`small_talk`**: Engages in casual conversation.
     - **Unrecognized Intent**: Asks the user to clarify their request.

6. **Response Generation**:
   - Based on the action, generates a text response.
   - Converts the response to audio using `gTTS`.

7. **Audio Playback**:
   - Plays the audio response using `pygame`.
   - Waits for the response to finish before listening again.

8. **Error Recovery**:
   - If the assistant encounters an error or doesn't understand the input, it prompts the user for clarification.
   - Terminates the session if the user remains inactive or explicitly exits.

---

## Requirements

- Python 3.8 or higher
- Libraries:
  - `asyncio`
  - `speech_recognition`
  - `gTTS`
  - `pygame`
  - `colorama`
  - `openai`
  - `json`
  - `datetime`
  - `threading`

Install dependencies using:
```bash
pip install -r requirements.txt
```

---

## Usage

1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo/voice-assistant.git
   ```
2. Navigate to the project directory:
   ```bash
   cd voice-assistant
   ```
3. Run the program:
   ```bash
   python main.py
   ```


## Example Interaction
### Input:
> "Can you help me book an appointment for tomorrow at 10:00 a.m.?"

### Output:
- **Speech**: 
  - "Your appointment has been successfully booked for 10:00 a.m. on [date]."
- **Slot Status**:
  - Removes the booked slot from the availability list for the specified date.
