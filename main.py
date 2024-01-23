import os
from anki import anki
from anki.template.examples import ENGLISH_GOLDEN_LIST

SAMPLE_SPREADSHEET_ID = "YOUR_SAMPLE_SPREADSHEET_ID"
BASE_PATH = os.getcwd()
SHEET_NAMES = ["SHEET_1", "SHEET_2", "SHEET_3", "SHEET_4", "SHEET_5"]


def main():
    url = f'https://docs.google.com/spreadsheet/ccc?key={SAMPLE_SPREADSHEET_ID}&output=xlsx'

    ENGLISH_GOLDEN_LIST.set_audio_folder("/my/audio/folder")
    anki.create_anki_deck_from_sheet(url, SHEET_NAMES, ENGLISH_GOLDEN_LIST)
    print("End!")


if __name__ == "__main__":
    main()
