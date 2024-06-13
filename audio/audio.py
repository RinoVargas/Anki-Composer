from anki.input.input_data import InputDataRecord, InputData, InputDataField
from compose.deck_specification import DeckSpecificationField, DeckSpecification, DeckSpecificationFieldType
from speech import speech
import os
import logger
from uuid import uuid4
from datetime import datetime

logger = logger.get_new_logger("audio")


def generate_audio_by_row(input_data: InputData, spec: DeckSpecification):
    audio_folder_path = spec.media_folder_path
    spec_fields_by_audio: list[DeckSpecificationField] = __get_fields_by_audio_file_generation(spec)
    __add_spec_audio_fields(spec, spec_fields_by_audio)

    if audio_folder_path is None:
        return

    if not os.path.exists(audio_folder_path):
        spec.media_folder_path = None
        logger.warning(f"The audio folder path '{audio_folder_path}' doesnt' exist")
        return

    for index, record in enumerate(input_data.records):
        __generate_audio_from_fields(record, spec, spec_fields_by_audio)
        logger.info(f"Row {index} done")


def __get_fields_by_audio_file_generation(spec: DeckSpecification):
    return list(filter(lambda x: x.generate_audio_file, spec.fields))


def __generate_audio_from_fields(record: InputDataRecord, spec: DeckSpecification,
                                 audio_spec_fields: list[DeckSpecificationField]):
    if not audio_spec_fields:
        return

    for spec_field in audio_spec_fields:
        data_field = record.find_field_by_name(spec_field.name)
        audio_data_field = __create_audio_data_field(data_field)
        record.add_field(audio_data_field)

        __create_audio_file(data_field, audio_data_field, spec)


def __add_spec_audio_fields(spec: DeckSpecification, spec_fields: list[DeckSpecificationField]):
    for spec_field in spec_fields:
        spec.fields.append(DeckSpecificationField(f"$_{spec_field.name}"))


def __create_audio_data_field(data_field: InputDataField):
    field = InputDataField(f"$_{data_field.field_name}")
    field.field_value = __generate_audio_file_name()
    return field


def __create_audio_file(data_field: InputDataField, audio_data_field: InputDataField,
                        spec: DeckSpecification):
    text = data_field.field_value
    filename = audio_data_field.field_value.replace("[sound:", "").replace("]", "")

    speech.text_to_speech(text, filename, audio_folder_path=spec.media_folder_path)


def __generate_audio_file_name():
    prefix = str(uuid4().hex)
    suffix = datetime.now().strftime('%Y%m%d%H%M%S')

    return f"[sound:{prefix}{suffix}.mp3]"
