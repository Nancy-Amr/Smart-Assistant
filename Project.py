import asyncio
import platform
import speech_recognition as sr
from gtts import gTTS
import playsound
import time
import re
from random import choice
# import datetime
import os

import threading  # For running alarms in the background
import tempfile

from pydub import AudioSegment
from pydub.playback import play
import pygame


import subprocess
import platform
from datetime import datetime, timedelta

import glob
import fnmatch
from pathlib import Path
import subprocess
import sys
# Add to your imports section
if platform.system() == "Windows":
    import winsound

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
        self.alarms = []
        self.alarm_threads = []  # Separate list to maintain references
        self.load_alarms()


   

    def speak(self, text):
        try:
            # Slow down speech for better clarity
            tts = gTTS(text=text, lang='en', slow=False)
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                temp_path = f.name
            
            tts.save(temp_path)
            
            # Use pygame for more reliable playback
            pygame.mixer.init()
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
            os.unlink(temp_path)
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
        hour = int(datetime.now().hour)
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
            print("DEBUG: Listening...")  # Debug
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.speak("I’m listening... Please speak clearly.")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                said = self.recognizer.recognize_google(audio)
                print(f"You said: {said}")
                print(f"DEBUG: Heard: {said}")  # Debug
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
                print(f"DEBUG: Audio error: {e}")  # Debug
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
            current_time = datetime.now().strftime("%H:%M:%S")
            self.speak(f"It’s {current_time}. You got a watch, or just too lazy to check?")
        elif "date" in text or "day" in text:
            current_date = datetime.now().strftime("%B %d, %Y")
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
        elif "set alarm" in text or "alarm for" in text:
            time_str = text.replace("set alarm", "").replace("alarm for", "").strip()
            self.set_system_alarm(time_str)  # Changed to use system alarm
        elif "list alarms" in text:
            self.speak("Alarms are stored in your system clock app. I'll open it for you.")
            self.open_clock_app()
        elif "cancel alarm" in text or "delete alarm" in text:
            self.delete_system_alarms()
        elif "open alarm" in text or "open clock" in text:
            self.open_clock_app()
        elif ("calendar" in text or "schedule" in text or 
              "open calender" in text or "show calender" in text):
            self.open_calendar()
        else:
            self.speak("I heard you, but I’ve got no clue what you’re on about. Try harder.")
            self.web_search(text)
        return True
    def set_windows_alarm(self, alarm_time):
        """Actually set an alarm on Windows"""
        try:
            # Windows 10/11 supports creating alarms via URI scheme
            time_str = alarm_time.strftime("%H:%M")
            uri = f"ms-clock:?alarmTime={time_str}&alarmTitle=Assistant%20Alarm"
            subprocess.run(f'start {uri}', shell=True, check=True)
            return True
        except Exception as e:
            print(f"Windows alarm error: {e}")
            return False
    def set_system_alarm(self, time_str):
        """Actually set an alarm in Windows Alarms & Clock app"""
        try:
            alarm_time = self.parse_time(time_str)
            if not alarm_time:
                self.speak("Sorry, I didn't understand that time")
                return False

            time_str = alarm_time.strftime("%H:%M")
            time_display = alarm_time.strftime("%I:%M %p")
            
            # Windows-specific implementation
            try:
                # Method 1: Use URI scheme (works on Windows 10/11)
                uri = f"ms-clock:?alarmTime={time_str}&alarmTitle=Assistant%20Alarm"
                result = subprocess.run(
                    ["start", uri], 
                    shell=True, 
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Verify the alarm was actually created
                time.sleep(2)  # Give the app time to open
                if self._verify_windows_alarm(alarm_time):
                    self.speak(f"Alarm successfully set for {time_display}")
                    return True
                
                # Fallback to PowerShell method if URI didn't work
                return self._set_windows_alarm_powershell(alarm_time)
                
            except Exception as e:
                print(f"Windows alarm error: {e}")
                self.speak(f"Please set the alarm manually for {time_display}")
                self.open_clock_app()
                return False
                
        except Exception as e:
            print(f"Error setting system alarm: {e}")
            self.speak("Failed to set the alarm. Please try again.")
            return False

    def _verify_windows_alarm(self, alarm_time):
        """Check if alarm exists in Windows Alarms & Clock app"""
        try:
            # This requires Windows 10/11 with PowerShell 5.1+
            ps_script = f'''
            $alarms = Get-AppointmentStore -StoreType Alarm | 
                    Select-Object -ExpandProperty Appointments |
                    Where-Object {{$_.StartTime -eq "{alarm_time.strftime('%H:%M')}"}}
            $alarms -ne $null
            '''
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True
            )
            return "True" in result.stdout
        except:
            return False

    def _set_windows_alarm_powershell(self, alarm_time):
        """Alternative method using PowerShell"""
        try:
            time_str = alarm_time.strftime("%H:%M")
            ps_script = f'''
            $alarm = Add-Appointment -StoreType Alarm -StartTime "{time_str}" -Duration 0 `
                    -Subject "Assistant Alarm" -Location "" -Details "" -Reminder 0
            $alarm -ne $null
            '''
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True
            )
            if "True" in result.stdout:
                self.speak(f"Alarm successfully set for {alarm_time.strftime('%I:%M %p')}")
                return True
            return False
        except Exception as e:
            print(f"PowerShell alarm error: {e}")
            return False
    def parse_time(self, time_str):
            """Improved time parsing that handles common formats"""
            now = datetime.now()
            time_str = time_str.lower().strip()
            
            # More thorough cleaning of the input string
            time_str = re.sub(r'\b(set|alarm|for|at|an|a|the)\b', '', time_str, flags=re.IGNORECASE)
            time_str = re.sub(r'\s+', ' ', time_str).strip()  # Normalize spaces
            print(f"DEBUG: Cleaned time string: '{time_str}'")  # Debug
            
            # Handle "in X minutes/hours"
            in_match = re.match(r'in\s+(\d+)\s+(minute|hour|second)s?', time_str)
            if in_match:
                num, unit = in_match.groups()
                num = int(num)
                if unit.startswith('min'):
                    return now + timedelta(minutes=num)
                elif unit.startswith('hour'):
                    return now + timedelta(hours=num)
                else:
                    return now + timedelta(seconds=num)
            
            # Handle absolute times with various formats
            try:
                # Normalize time string
                time_str = time_str.replace('.', '')  # Remove periods in "p.m."
                time_str = time_str.replace(' pm', 'pm').replace(' am', 'am')
                time_str = time_str.replace('p.m.', 'pm').replace('a.m.', 'am')
                time_str = re.sub(r'\s+', '', time_str)  # Remove all spaces
                
                # Try different time formats
                time_formats = [
                    ('%I:%M%p', lambda h, m: (h, m)),  # "3:00pm"
                    ('%I%p', lambda h, m: (h, 0)),     # "3pm"
                    ('%H:%M', lambda h, m: (h, m)),    # "15:00"
                ]
                
                for fmt, converter in time_formats:
                    try:
                        parsed = datetime.strptime(time_str, fmt)
                        hour, minute = converter(parsed.hour, parsed.minute if hasattr(parsed, 'minute') else 0)
                        alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        if alarm_time <= now:
                            alarm_time += timedelta(days=1)
                        return alarm_time
                    except ValueError:
                        continue
                        
            except Exception as e:
                print(f"Time parsing error: {e}")
            
            print(f"DEBUG: Failed to parse time string: '{time_str}'")  # Debug
            return None
    def trigger_alarm(self):
        """Improved alarm triggering"""
        self.speak("WAKE UP! WAKE UP! ALARM ALARM ALARM!")
        
        # Platform-specific alerts
        try:
            if platform.system() == "Windows":
                winsound.Beep(1000, 2000)  # High-pitch beep
                subprocess.Popen(['notepad.exe'], 
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
            elif platform.system() == "Darwin":  # macOS
                os.system('afplay /System/Library/Sounds/Ping.aiff')
                os.system('''osascript -e 'display dialog "ALARM!" buttons {"OK"} default button 1' ''')
            else:  # Linux
                os.system('spd-say "ALARM ALARM ALARM"')
                os.system('notify-send "ALARM!"')
        except Exception as e:
            print(f"Alarm sound error: {e}")

    def save_alarms(self):
        pass

    def load_alarms(self):
        self.alarms = []
    def snooze_alarm(self, minutes=5):
        threading.Timer(minutes * 60, self.trigger_alarm).start()
        self.speak(f"Snoozing for {minutes} minutes")
    def show_visual_alert(self):
        try:
            if platform.system() == "Windows":
                subprocess.Popen(['notepad.exe'])  # Simple popup
            else:
                os.system('xmessage "ALARM!" &')  # Linux/macOS
        except:
            pass
    def open_clock_app(self):
        """Open the system's default clock/alarm application"""
        try:
            system_os = platform.system()
            
            if system_os == "Windows":
                # Windows 10/11 has Alarms & Clock app
                subprocess.run(["start", "ms-clock:"], shell=True)
                self.speak("Opening Windows Alarms & Clock app")
            elif system_os == "Darwin":  # macOS
                # Open Apple's Clock app
                subprocess.run(["open", "-a", "Clock"])
                self.speak("Opening macOS Clock app")
            elif system_os == "Linux":
                # Try common Linux clock apps
                try:
                    subprocess.run(["gnome-clocks"], check=True)
                    self.speak("Opening GNOME Clocks")
                except:
                    try:
                        subprocess.run(["kclock"], check=True)
                        self.speak("Opening KClock")
                    except:
                        self.speak("Couldn't find a clock app. Please install GNOME Clocks or KClock")
            else:
                self.speak("I don't know how to open the clock app on this system")
        except Exception as e:
            print(f"Error opening clock app: {e}")
            self.speak("Failed to open the clock application")

    def set_system_alarm(self, time_str):
        """Actually set an alarm in Windows Alarms & Clock app"""
        try:
            alarm_time = self.parse_time(time_str)
            if not alarm_time:
                self.speak("Sorry, I didn't understand that time")
                return False

            time_display = alarm_time.strftime("%I:%M %p")
            
            # Try all available methods in sequence
            if self._set_windows_alarm_v1(alarm_time):
                self.speak(f"Alarm set for {time_display}")
                return True
                
            if self._set_windows_alarm_v2(alarm_time):
                self.speak(f"Alarm set for {time_display}")
                return True
                
            # Final fallback
            self.open_clock_app()
            self.speak(f"Please set the alarm manually for {time_display}")
            return False
            
        except Exception as e:
            print(f"Error setting alarm: {e}")
            self.speak("Failed to set the alarm. Please try again.")
            return False

    # def _set_windows_alarm_v1(self, alarm_time):
    #     """Method 1: Using Windows URI scheme"""
    #     try:
    #         time_str = alarm_time.strftime("%H:%M")
    #         uri = f"ms-clock:?alarmTime={time_str}&alarmTitle=Assistant%20Alarm"
    #         result = subprocess.run(
    #             ["cmd", "/c", "start", uri],
    #             shell=True,
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.PIPE,
    #             timeout=5
    #         )
    #         time.sleep(2)  # Wait for app to open
    #         return self._verify_windows_alarm(alarm_time)
    #     except:
    #         return False

    def set_system_alarm(self, time_str):
        """Set alarm using Windows Task Scheduler as primary method"""
        try:
            alarm_time = self.parse_time(time_str)
            if not alarm_time:
                self.speak("Sorry, I didn't understand that time")
                return False

            time_display = alarm_time.strftime("%I:%M %p")
            
            # First try Task Scheduler method
            if self._set_alarm_with_task_scheduler(alarm_time):
                self.speak(f"Alarm set for {time_display}")
                return True
                
            # Fallback to other methods if Task Scheduler fails
            if self._set_windows_alarm_v1(alarm_time):  # URI scheme
                self.speak(f"Alarm set for {time_display}")
                return True
                
            if self._set_windows_alarm_v2(alarm_time):  # PowerShell
                self.speak(f"Alarm set for {time_display}")
                return True
                
            # Final fallback
            self.open_clock_app()
            self.speak(f"Please set the alarm manually for {time_display}")
            return False
            
        except Exception as e:
            print(f"Error setting alarm: {e}")
            self.speak("Failed to set the alarm. Please try again.")
            return False

    def _set_alarm_with_task_scheduler(self, alarm_time):
        """Create a scheduled task for the alarm"""
        try:
            # Generate unique task name
            task_name = f"AssistantAlarm_{alarm_time.strftime('%H%M')}"
            
            # Calculate time difference
            now = datetime.now()
            if alarm_time < now:
                alarm_time += timedelta(days=1)
            delta = (alarm_time - now).total_seconds()
            
            # Get Python executable path
            python_exe = sys.executable or "pythonw.exe"
            script_path = os.path.abspath(__file__)
            
            # Create the task XML
            xml_template = f'''
            <Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
            <RegistrationInfo>
                <Description>Assistant Alarm</Description>
            </RegistrationInfo>
            <Triggers>
                <TimeTrigger>
                <StartBoundary>{alarm_time.isoformat()}</StartBoundary>
                <Enabled>true</Enabled>
                </TimeTrigger>
            </Triggers>
            <Actions Context="Author">
                <Exec>
                <Command>"{python_exe}"</Command>
                <Arguments>"{script_path}" --trigger-alarm "{alarm_time.isoformat()}"</Arguments>
                </Exec>
            </Actions>
            </Task>
            '''
            
            # Save XML to temp file
            with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as f:
                xml_path = f.name
                f.write(xml_template.encode('utf-8'))
            
            # Create the task
            subprocess.run([
                'schtasks', '/Create', 
                '/TN', task_name, 
                '/XML', xml_path,
                '/F'
            ], check=True, timeout=10)
            
            # Clean up
            os.unlink(xml_path)
            
            return True
            
        except Exception as e:
            print(f"Task Scheduler error: {e}")
            return False

    def _trigger_alarm_from_task(self):
        """Handle alarm triggered from scheduled task"""
        self.speak("WAKE UP! Your scheduled alarm is going off!")
        winsound.Beep(1000, 2000)
        
        # Add visual notification
        subprocess.Popen(['notepad.exe', 'ALARM! Your scheduled alarm is going off!'])

    def _verify_windows_alarm(self, alarm_time):
            """Verify alarm was actually created"""
            try:
                time_str = alarm_time.strftime("%H:%M")
                ps_script = f'''
                $alarms = Get-AppointmentStore -StoreType Alarm -WarningAction SilentlyContinue | 
                        Select-Object -ExpandProperty Appointments |
                        Where-Object {{$_.StartTime -eq "{time_str}"}}
                return $alarms -ne $null
                '''
                result = subprocess.run(
                    ["powershell", "-Command", ps_script],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return "True" in result.stdout
            except:
                return False

    def delete_system_alarms(self):
        """Delete all alarms in the system's clock app"""
        try:
            system_os = platform.system()
            
            if system_os == "Windows":
                # Windows - no direct way to delete alarms via command line
                self.open_clock_app()
                self.speak("Please delete alarms manually in the Alarms & Clock app")
            elif system_os == "Darwin":  # macOS
                # AppleScript to delete all alarms
                script = '''
                tell application "Clock"
                    activate
                    tell application "System Events" to tell process "Clock"
                        click button "Alarm" of toolbar 1 of window "Clock"
                        repeat while exists (button "Edit" of group 1 of window "Clock")
                            click button "Edit" of group 1 of window "Clock"
                            delay 0.5
                            if exists (button "Delete All" of group 1 of window "Clock") then
                                click button "Delete All" of group 1 of window "Clock"
                                click button "Delete All" of sheet 1 of window "Clock"
                                exit repeat
                            else
                                exit repeat
                            end if
                        end repeat
                    end tell
                end tell
                '''
                subprocess.run(["osascript", "-e", script])
                self.speak("Deleted all alarms in the Clock app")
            else:
                self.open_clock_app()
                self.speak("Please delete alarms manually in your clock app")
            
            return True
        except Exception as e:
            print(f"Error deleting system alarms: {e}")
            self.speak("Failed to delete system alarms")
            return False
    def open_calendar(self):
        """Open the system calendar application persistently"""
        try:
            system_os = platform.system()
            
            if system_os == "Windows":
                # Method that keeps the calendar open
                try:
                    # Use start without waiting for completion
                    subprocess.Popen(
                        ["cmd", "/c", "start", "outlookcal:"],
                        shell=True,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                    self.speak("Opening Windows Calendar")
                    return True
                except Exception as e:
                    print(f"Calendar open error: {e}")
                    # Fallback to direct executable
                    try:
                        subprocess.Popen(
                            ["explorer", "outlookcal:"],
                            shell=True
                        )
                        self.speak("Opening calendar")
                        return True
                    except:
                        webbrowser.open("https://calendar.google.com")
                        self.speak("Opening web calendar")
                        return True

        except Exception as e:
            print(f"Calendar error: {e}")
            self.speak("Couldn't open calendar. Please try manually.")
            return False



async def main():
    assistant = SmartAssistant()
    assistant.wish_me()
    assistant.usrname()
    
    running = True
    while running:
        assistant.speak("What's on your tiny mind now?")
        text = assistant.get_audio()
        running = assistant.process_command(text)
        await asyncio.sleep(1)

def sync_main():
    """Synchronous wrapper for the async main function"""
    asyncio.run(main())

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--trigger-alarm":
        # Run alarm trigger synchronously
        assistant = SmartAssistant()
        assistant._trigger_alarm_from_task()
    else:
        # Check if we're in Pyodide environment
        if platform.system() == "Emscripten":
            asyncio.ensure_future(main())
        else:
            # Run normal async main
            sync_main()