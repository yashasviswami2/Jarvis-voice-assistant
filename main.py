import speech_recognition as sr  # type: ignore
import webbrowser
import pyttsx3
import musicLibrary
import requests
from gtts import gTTS 
import pygame 
import os
import openai  # type: ignore

# ----------------------------
# Configuration / API Keys
# ----------------------------
newsapi = "1b581357d6874108903f95eb4a5121de"
openai.api_key = "<Your OpenAI Key Here>"

# ----------------------------
# Initialize speech engine
# ----------------------------
recognizer = sr.Recognizer()
engine = pyttsx3.init()
pygame.mixer.init()  # Initialize mixer once at the start

# ----------------------------
# Speak functions
# ----------------------------
def speak_old(text):
    engine.say(text)
    engine.runAndWait()

def speak(text):
    try:
        tts = gTTS(text)
        tts.save("temp.mp3")
        pygame.mixer.music.load("temp.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        os.remove("temp.mp3")
    except Exception as e:
        print("Error playing speech:", e)

# ----------------------------
# AI Command
# ----------------------------
def aiProcess(command):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a virtual assistant named Jarvis skilled in general tasks. Give short responses."},
                {"role": "user", "content": command}
            ]
        )
        return completion.choices[0].message['content']
    except Exception as e:
        return f"AI processing error: {e}"

# ----------------------------
# Command Processing
# ----------------------------
def processCommand(c):
    c = c.lower()
    if "open google" in c:
        webbrowser.open("https://google.com")
    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")
    elif c.startswith("play"):
        try:
            song = c.split(" ")[1]
            link = musicLibrary.music[song]
            webbrowser.open(link)
        except KeyError:
            speak(f"Song {song} not found in library.")
    elif "news" in c:
        try:
            r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}")
            if r.status_code == 200:
                articles = r.json().get('articles', [])
                for article in articles[:5]:  # limit to first 5 headlines
                    speak(article['title'])
            else:
                speak("Unable to fetch news.")
        except Exception as e:
            speak(f"Error fetching news: {e}")
    else:
        output = aiProcess(c)
        speak(output)

# ----------------------------
# Main loop
# ----------------------------
if __name__ == "__main__":
    speak("Initializing Jarvis...")
    
    while True:
        print("recognizing...")
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                word = recognizer.recognize_google(audio)
                print(f"You said: {word}")
                if word.lower() == "jarvis":
                    speak("Ya")
                    # Listen for command
                    with sr.Microphone() as source:
                        print("Jarvis Active...")
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        command = recognizer.recognize_google(audio)
                        processCommand(command)

        except sr.WaitTimeoutError:
            print("No speech detected, trying again...")
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except OSError:
            print("Microphone not found. Please install PyAudio.")
            exit()
