# Import the required module for text
# to speech conversion
from gtts import gTTS
from os import path

# This module is imported so that we can
# play the converted audio
import os


def text_to_speech(text, filepath, target_folder=None):
    final_path = filepath if target_folder is None else path.join(target_folder, filepath)
    myobj = gTTS(text, lang='en', slow=False)
    myobj.save(final_path)