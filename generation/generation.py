from speech import speech
import pandas as pd
from os import path, getcwd


def generate_audio_by_sheet(url, sheet_name):
    df = pd.read_excel(url, sheet_name, index_col="#")
    generate_audio_by_row(df)

def generate_audio_by_row(df, target_folder):
    for index, row in df.iterrows():
        generate_audios(row, target_folder)
        print(f"Row {index} done")


def generate_audios(row, target_folder=None):
    speech.text_to_speech(row['EXAMPLE 1'], format_audio_name(row['AUDIO 1']), target_folder)
    speech.text_to_speech(row['EXAMPLE 2'], format_audio_name(row['AUDIO 2']), target_folder)
    speech.text_to_speech(row['EXAMPLE 3'], format_audio_name(row['AUDIO 3']), target_folder)

def format_audio_name(raw_audio_name):
    return raw_audio_name.replace("[sound:", "").replace("]", "")


def merge_sheets(url, sheet_names):
    df = None
    for sheet_name in sheet_names:
        df = sheet_to_df(url, sheet_name) if df is None else df.append(sheet_to_df(url, sheet_name), ignore_index=True)

    return df


def sheet_to_df(url, sheet_name):
    return pd.read_excel(url, sheet_name, index_col="#")


def to_tsv_file(df, filename, base_path=None):
    filepath = getcwd() if base_path is None else base_path
    filename = path.join(filepath, filename)
    df.to_csv(filename, sep="\t", encoding='utf-8-sig')
