from enum import Enum
import toml
import openai
import speech_recognition as sr

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

def main():
    #Leyendo archivo de personalidad
    api_prompt = getPrompt(archivo_prompt)
    try:
        while True:
            audio.grabar_audio()
            input_voice = audio.transcribir_audio()
            completed = complete(api_prompt,input_voice,Models.GPT4) #cambiar el modelo aquí
            print(completed.choices[0].message['content'])
            audio.hablar(completed.choices[0].message['content'])
    except KeyboardInterrupt:
        print("Saliendo del programa...")
        exit()

if __name__ == "__main__":
    main()