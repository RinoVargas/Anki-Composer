# Import the required module for text
# to speech conversion
from gtts import gTTS
from os import path

# This module is imported so that we can
# play the converted audio
import os


def text_to_speech(text, filename, audio_folder_path):
    filename_path = path.join(audio_folder_path, filename)
    myobj = gTTS(text, lang='en', slow=False)
    myobj.save(filename_path)