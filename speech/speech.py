# Import the required module for text
# to speech conversion
from gtts import gTTS

# This module is imported so that we can
# play the converted audio
import os


def text_to_speech(text, filepath):
    myobj = gTTS(text, lang='en', slow=False)
    myobj.save(filepath)