from speech import speech
import pandas as pd

def generate_audio_by_sheet(url, sheet_name):
    df = pd.read_excel(url, sheet_name, index_col="#")
    generate_audio_by_row(df)

def generate_audio_by_row(df):
    for index, row in df.iterrows():
        generate_audios(row)
        print(f"Row {index} done")


def generate_audios(row):
    speech.text_to_speech(row['EXAMPLE 1'], format_audio_name(row['AUDIO 1']))
    speech.text_to_speech(row['EXAMPLE 2'], format_audio_name(row['AUDIO 2']))
    speech.text_to_speech(row['EXAMPLE 3'], format_audio_name(row['AUDIO 3']))

def format_audio_name(raw_audio_name):
    return raw_audio_name.replace("[sound:", "").replace("]", "")
