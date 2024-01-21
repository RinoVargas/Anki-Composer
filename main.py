from generation import generation
import os

SAMPLE_SPREADSHEET_ID = "YOUR_SAMPLE_SPREADSHEET_ID"
BASE_PATH = os.getcwd()
SHEET_NAMES = ["SHEET_1", "SHEET_2", "SHEET_3", "SHEET_4", "SHEET_5"]


def main():
    url = f'https://docs.google.com/spreadsheet/ccc?key={SAMPLE_SPREADSHEET_ID}&output=xlsx'

    main_df = generation.merge_sheets(url, SHEET_NAMES)
    generation.generate_audio_by_row(main_df)
    print("End!")


if __name__ == "__main__":
    main()
