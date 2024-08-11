import functools

import logger
from anki.input.input_data import InputData
from anki.input.reader.gsheet_input_reader import GSheetInputReader
from anki.input.reader.input_reader import InputReader
from compose.deck_specification import DeckSpecification, DeckInputType, GenericTemplate
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
    if not spec.disable_audio_generation:
        audio.generate_audio_by_row(input_data, spec)
    __write_package(input_data, spec)


def __create_reader(spec: DeckSpecification) -> InputReader | None:
    readers: dict[str, InputReader] = {
        DeckInputType.GSHEET: GSheetInputReader(spec),
        DeckInputType.XLSX: GSheetInputReader(spec)
    }
    return readers[spec.input_config.type]


def __write_package(input_data: InputData, spec: DeckSpecification):
    model: genanki.Model = __create_model(spec)
    deck = __create_deck(spec.deck_name, input_data, model)
    package = genanki.Package(deck)

    filename = spec.output_config.filename
    if None is filename or len(filename.strip()) == 0:
        filename = spec.deck_name

    output_filename = os.path.join(spec.output_config.folder_path, filename)

    if spec.media_folder_path is not None:
        media_files = [os.path.join(spec.media_folder_path, media_file) for media_file in
                       os.listdir(spec.media_folder_path)]
        package.media_files = media_files

    package.write_to_file(f'{output_filename}.apkg')


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
                'qfmt': __template_to_string(spec.front_template),
                'afmt': __template_to_string(spec.back_template),
            },
        ])


def __template_to_string(template: GenericTemplate):
    if template["file_path"] is not None:
        return html_file_to_string(template.file_path)

    return template["value"]


def html_file_to_string(file_path : str):
    try:
        html_file = open(file_path, 'r')

    except Exception as e:
        raise RuntimeError(f"It has occurred an error when the template file was opened: {e}")

    with html_file:
        value = functools.reduce(lambda a, b: a + b, html_file.readlines())
        html_file.close()
        return value


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
