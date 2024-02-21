import logger
from anki.input.input_data import InputData
from anki.input.reader.gsheet_input_reader import GSheetInputReader
from anki.input.reader.input_reader import InputReader
from compose.deck_specification import DeckSpecification, DeckInputType
import random
import genanki
import os
from audio import audio

logger = logger.get_new_logger("deck_builder")


def build(spec: DeckSpecification):
    reader: InputReader = __create_reader(spec)
    input_data: InputData = reader.read_input()
    __create_anki_deck_from_sheet(input_data, spec)


def __create_anki_deck_from_sheet(input_data: InputData, spec: DeckSpecification):
    audio.generate_audio_by_row(input_data, spec)
    __write_package(input_data, spec)


def __create_reader(spec: DeckSpecification) -> InputReader | None:
    readers: dict[str, InputReader] = {
        DeckInputType.GSHEET: GSheetInputReader(spec)
    }
    return readers[spec.input_config.type]


def __write_package(input_data: InputData, spec: DeckSpecification):
    model: genanki.Model = __create_model(spec)
    deck = __create_deck(spec.deck_name, input_data, model)
    package = genanki.Package(deck)

    if spec.media_folder_path is not None:
        media_files = [os.path.join(spec.media_folder_path, media_file) for media_file in
                       os.listdir(spec.media_folder_path)]
        package.media_files = media_files

    package.write_to_file(f'{spec.deck_name}.apkg')


def __generate_id():
    return random.randrange(1 << 30, 1 << 31)


def __create_model(spec: DeckSpecification):
    return genanki.Model(
        __generate_id(),
        spec.deck_name,
        fields=[{'name': field.name} for field in spec.fields],
        templates=[
            {
                'name': spec.deck_name,
                'qfmt': spec.front_template,
                'afmt': spec.back_template,
            },
        ])


def __create_deck(name: str, input_data: InputData, model: genanki.Model):
    deck = genanki.Deck(__generate_id(), name)

    for note in __generate_notes(input_data, model):
        deck.add_note(note)

    return deck


def __generate_notes(input_data: InputData, model: genanki.Model):
    for record in input_data.records:
        yield genanki.Note(
            model=model,
            fields=[field.field_value for field in record.fields]
        )