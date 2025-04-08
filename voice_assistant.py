import asyncio
import platform
import speech_recognition as sr
from gtts import gTTS
import playsound
import time
import re
from random import choice
import datetime
import os

# For opening URLs in local environment
try:
    import webbrowser
    WEBBROWSER_AVAILABLE = True
except ImportError:
    WEBBROWSER_AVAILABLE = False

# For JavaScript interop in Pyodide
try:
    import js
    PYODIDE_ENV = True
except ImportError:
    PYODIDE_ENV = False

class SmartAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.name = "Parhsu the Magnificent"
        self.greetings = [
            "Morning, sunshine! Ready to boss me around?",
            "Afternoon, huh? Don’t expect me to make you lunch.",
            "Evening already? Time flies when I’m doing all the work."
        ]
        self.user_name = "Anonymous"
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        self.recognizer.dynamic_energy_threshold = True

    def speak(self, text):
        try:
            tts = gTTS(text=text, lang='en')
            filename = 'voice.mp3'
            tts.save(filename)
            playsound.playsound(filename)
            os.remove(filename)  # Clean up the file after playing
        except Exception as e:
            print(f"Speech error: {e}")
            print(f"Assistant (text fallback): {text}")

    def open_web(self, url, message):
        self.speak(message)
        if PYODIDE_ENV:
            # Use JavaScript to open the URL in Pyodide
            try:
                js.window.open(url, "_blank")
                print(f"Opened URL in browser: {url}")
            except Exception as e:
                print(f"Failed to open URL in Pyodide: {e}")
                print(f"Please open this URL manually: {url}")
        elif WEBBROWSER_AVAILABLE:
            # Use webbrowser in local environment
            try:
                webbrowser.open(url, new=2)  # new=2 opens in a new tab if possible
                print(f"Opened URL in browser: {url}")
            except Exception as e:
                print(f"Failed to open URL: {e}")
                print(f"Please open this URL manually: {url}")
        else:
            # Fallback if neither method is available
            print(f"Cannot open URL automatically. Please open this URL manually: {url}")

    def web_search(self, query):
        url = f"https://www.google.com/search?q={query}"
        self.open_web(url, f"Searching for '{query}'. Hope it’s worth my time.")

    def wish_me(self):
        hour = int(datetime.datetime.now().hour)
        if 0 <= hour < 12:
            self.speak(self.greetings[0])
        elif 12 <= hour < 18:
            self.speak(self.greetings[1])
        else:
            self.speak(self.greetings[2])
        self.speak(f"I’m {self.name}, your oh-so-smart assistant.")

    def usrname(self):
        self.speak("What’s your name, mortal?")
        text = self.get_audio()
        if not text or text == "none":
            self.user_name = "Anonymous"
            self.speak("Fine, I’ll just call you Anonymous. How original.")
        else:
            self.user_name = text
            self.speak(f"Welcome, {self.user_name}. Try not to bore me.")

    def get_audio(self):
        with sr.Microphone() as source:
            self.speak("Adjusting for background noise, please wait...")
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.speak("I’m listening... Please speak clearly.")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                said = self.recognizer.recognize_google(audio)
                print(f"You said: {said}")
                return said.lower()
            except sr.WaitTimeoutError:
                self.speak("I didn’t hear anything. Speak like you mean it next time.")
                print("Recognition error: Timeout waiting for audio")
                return self.get_text_input()
            except sr.RequestError as e:
                self.speak("My speech recognition is on the fritz. Blame the internet.")
                print(f"Recognition service error: {e}")
                return self.get_text_input()
            except sr.UnknownValueError:
                self.speak("Sorry, I couldn’t understand that. Speak clearly or type it, lazy.")
                print("Recognition error: Could not understand audio")
                return self.get_text_input()
            except Exception as e:
                self.speak("Sorry, I encountered an error while listening.")
                print(f"Unexpected error: {e}")
                return self.get_text_input()

    def get_text_input(self):
        self.speak("Please type your command instead:")
        try:
            return input("You (type): ").lower()
        except:
            self.speak("Text input is not supported in this environment. Please try speaking again.")
            return ""

    def process_command(self, text):
        if not text:
            return True

        if "wikipedia" in text:
            self.speak("Digging through Wikipedia. Hold your horses.")
            query = text.replace("wikipedia", "").strip()
            self.web_search(f"{query} wikipedia")
        elif "open youtube" in text:
            self.open_web("https://www.youtube.com", "YouTube, because staring at cat videos is peak productivity.")
        elif "open google" in text:
            self.open_web("https://www.google.co.in", "Google. Go figure it out yourself for once.")
        elif "open stack overflow" in text:
            self.open_web("https://www.stackoverflow.com", "Stack Overflow. Good luck pretending you’re a coder.")
        elif "time" in text:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.speak(f"It’s {current_time}. You got a watch, or just too lazy to check?")
        elif "date" in text or "day" in text:
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today’s {current_date}. Mark it on your calendar if you can find it.")
        elif "how are you" in text:
            self.speak("I’m fantastic, thanks for asking. You? Oh wait, I don’t really care.")
        elif "search" in text or "what is" in text:
            query = text.replace("search", "").replace("what is", "").strip()
            expr = re.search(r'\d+[\+\-\*/]\d+', query)
            if expr:
                try:
                    result = eval(expr.group(), {"__builtins__": {}})
                    self.speak(f"Your little math problem equals {result}. Impressed yet?")
                except:
                    self.speak("That’s not math, that’s gibberish. Try again.")
            else:
                self.web_search(query)
        elif "calculate" in text:
            query = text.replace("calculate", "").strip()
            expr = re.search(r'\d+[\+\-\*/]\d+', query)
            if expr:
                try:
                    result = eval(expr.group(), {"__builtins__": {}})
                    self.speak(f"Your little math problem equals {result}. Impressed yet?")
                except:
                    self.speak("That’s not math, that’s gibberish. Try again.")
            else:
                self.speak("Give me something to calculate, not just hot air.")
        elif "exit" in text or "bye" in text:
            self.speak("Finally, some peace. Catch you later, or not.")
            return False
        else:
            self.speak("I heard you, but I’ve got no clue what you’re on about. Try harder.")
            self.web_search(text)
        return True

async def main():
    assistant = SmartAssistant()
    assistant.wish_me()
    assistant.usrname()
    
    running = True
    while running:
        assistant.speak("What’s on your tiny mind now?")
        text = assistant.get_audio()
        running = assistant.process_command(text)
        await asyncio.sleep(1)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())