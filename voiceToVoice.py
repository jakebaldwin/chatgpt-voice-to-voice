import speech_recognition as sr
from translate import Translator
from openai import OpenAI
import pygame

with open('../boring/fte_ky.txt') as f:
    fte_ky = f.readline()

client = OpenAI(api_key=fte_ky)

thread = [{"role": "system", "content": "You are a french teacher, speaking in english. Keep responses short, max 3 sentences."}]

#singleThread = [{"role": "system", "content": "You are a french teacher, speaking in english. Keep responses short, max 3 sentences."}, {}]

pygame.init()
pygame.mixer.init()

def recognize_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say something...")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

def translate_text(text, target_language='en'):
    translator= Translator(to_lang=target_language)
    translation = translator.translate(text)
    print('Student:', translation)
    return translation

if __name__ == "__main__":
    while True:
        speech_text = recognize_speech()
        if speech_text:
            translated_text = translate_text(speech_text, target_language='en')

            thread.append({"role": "user", "content": translated_text})
            #singleThread.pop()
            #singleThread.append({"role": "user", "content": translated_text})
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=thread
            )

            teacherResponse = response.choices[0].message.content
            print('Teacher:', teacherResponse)
            
            response = client.audio.speech.create(
                model="tts-1",
                voice="onyx",
                input=teacherResponse
            )
            thread.append({"role": "assistant", "content": teacherResponse})
            response.stream_to_file("output.mp3")
            try:
                pygame.init()
                pygame.mixer.init()
                pygame.mixer.music.load('./output.mp3')
                pygame.mixer.music.play()

                # Keep the program running while the music plays
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            finally:
                pygame.mixer.quit()
                pygame.quit()

        
        