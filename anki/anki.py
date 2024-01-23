import genanki
import random
import os
from generation import generation


def create_anki_deck_from_sheet(url, sheets, predefined_template):
    main_df = generation.merge_sheets(url, sheets)

    if predefined_template.get_audio_folder() is not None:
        generation.generate_audio_by_row(main_df, target_folder=predefined_template.get_audio_folder())

    __write_package(main_df, predefined_template)


def __generate_id():
    return random.randrange(1 << 30, 1 << 31)


def __create_model(df, predefined_template):
    return genanki.Model(
        __generate_id(),
        predefined_template.get_deck_name(),
        fields=[{'name': column} for column in df.columns],
        templates=[
            {
                'name': predefined_template.get_deck_name(),
                'qfmt': predefined_template.get_front_template(),
                'afmt': predefined_template.get_back_template(),
            },
        ])


def __write_package(df, predefined_template):
    if not os.path.exists(predefined_template.get_audio_folder()):
        raise Exception(f"The path '{predefined_template.get_audio_folder()}' doesn't exist")

    model = __create_model(df, predefined_template)
    deck = __create_deck_from_df(predefined_template.get_deck_name(), df, model)
    package = genanki.Package(deck)
    media_files = []

    if predefined_template.get_audio_folder() is not None:
        media_files = [os.path.join(predefined_template.get_audio_folder(), media_file) for media_file in
                       os.listdir(predefined_template.get_audio_folder())]
        package.media_files = media_files

    package.write_to_file(f'{predefined_template.get_deck_name()}.apkg')


def __create_deck_from_df(name, df, model):
    deck = genanki.Deck(__generate_id(), name)

    for note in __generate_notes_from_df(df, model):
        deck.add_note(note)

    return deck


def __generate_notes_from_df(df, model):
    for index, row in df.iterrows():
        yield genanki.Note(
            model=model,
            fields=[row[column] for column in df.columns]
        )
