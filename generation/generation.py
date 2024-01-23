import os.path

from speech import speech
import pandas as pd
from os import path, getcwd
import logger

logger = logger.get_new_logger("generation")


def generate_audio_by_sheet(url, sheet_name, predefined_template):
    df = pd.read_excel(url, sheet_name, index_col="#")
    generate_audio_by_row(df, predefined_template)


def generate_audio_by_row(df, predefined_template):

    if predefined_template.get_audio_folder() is None:
        return

    if not os.path.exists(predefined_template.get_audio_folder()):
        logger.warning(f"The audio folder path '{predefined_template.get_audio_folder()}' doesnt' exist")
        predefined_template.set_audio_folder(None)
        return

    for index, row in df.iterrows():
        generate_audio_from_fields(row, predefined_template)
        logger.info(f"Row {index} done")


def generate_audio_from_fields(row, predefined_template):
    audio_fields = list(filter(lambda x: x.get_field_type() == 'AUDIO', predefined_template.get_fields()))

    if not audio_fields:
        logger.warning(f"There aren't audio fields defined in the template")
        return

    for audio_field in audio_fields:

        if audio_field.get_related_text_field_name() is None:
            logger.warning(f"The audio column '{audio_field.get_name()}' hasn't defined a related text field.")
            continue

        try:
            generate_audio_from_field(
                row,
                audio_field,
                predefined_template.get_audio_folder()
            )
        except KeyError:
            logger.warning(f"The column '{audio_field.get_name()}' hasn't exist in the worksheet")


def generate_audio_from_field(row, audio_field, audio_folder_path):
    text_to_audio = row[audio_field.get_related_text_field_name()]
    raw_audio_filename = row[audio_field.get_name()]

    speech.text_to_speech(
        text=text_to_audio,
        filename=format_audio_name(raw_audio_filename),
        audio_folder_path=audio_folder_path
    )


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
