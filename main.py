from enum import Enum
import toml
import openai
import speech_recognition as sr
from gtts import gTTS
import os
import audio
import pygame

openai.api_key= os.environ.get("OPENAI_API_KEY")

class Models(Enum):
    GPT3 = "gpt-3.5-turbo"
    GPT4 = "gpt-4"

archivo_prompt = 'prompt.toml'

def getPrompt(archivo):
        with open(archivo, "r") as prompt_file:
            return toml.load(prompt_file)

def complete(api_prompt,input: dict,model: Models):
    messages = api_prompt["mensajes"]
    messages.append({"role": "user", "content": input})
    response = openai.ChatCompletion.create(
        model= model.value,
        messages = messages,
        temperature=0.0,
        stop=["<\STOP>"]
    )
    messages.append({"role": "system", "content": response.choices[0].message['content']})
    return response

def transcribir_audio():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Por favor, habla ahora...")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        
        try:
            return recognizer.recognize_google(audio, language='es-ES')
        except sr.UnknownValueError:
            print("No se pudo entender el audio")
            return ""
        except sr.RequestError as e:
            print(f"Error en el servicio de Google Speech Recognition; {e}")
            return ""

def hablar(texto):
    tts = gTTS(text=texto, lang='es')
    tts.save("output.mp3")
    
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("output.mp3")
    
    try:
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except KeyboardInterrupt:
        pygame.mixer.music.stop()
        print("Reproducción de audio detenida")
        exit()
    except Exception as e:
        print(f"Error al reproducir el audio: {e}")
        exit()
    finally:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    
    #engine = pyttsx3.init()
    #engine.say(texto)
    #engine.runAndWait()
    
def main():
    #Leyendo archivo de personalidad
    api_prompt = getPrompt(archivo_prompt)
    try:
        while True:
            audio.grabar_audio()
            input_voice = audio.transcribir_audio()
            completed = complete(api_prompt,input_voice,Models.GPT4) #cambiar el modelo aquí
            print(completed.choices[0].message['content'])
            hablar(completed.choices[0].message['content'])
    except KeyboardInterrupt:
        print("Saliendo del programa...")
        exit()

if __name__ == "__main__":
    main()