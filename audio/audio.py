from anki.input.input_data import InputDataRecord, InputData
from compose.deck_specification import DeckSpecificationField, DeckSpecification
from speech import speech
import os
import logger

logger = logger.get_new_logger("audio")


def generate_audio_by_row(input_data: InputData, spec: DeckSpecification):
    audio_folder_path = spec.media_folder_path
    if audio_folder_path is None:
        return

    if not os.path.exists(audio_folder_path):
        spec.media_folder_path = None
        logger.warning(f"The audio folder path '{audio_folder_path}' doesnt' exist")
        return

    for index, record in enumerate(input_data.records):
        __generate_audio_from_fields(record, spec)
        logger.info(f"Row {index} done")


def __generate_audio_from_fields(record: InputDataRecord, spec: DeckSpecification):
    audio_fields: list[DeckSpecificationField] = list(filter(lambda x: x.field_type == 'AUDIO', spec.fields))

    if not audio_fields:
        return

    for audio_field in audio_fields:

        if audio_field.related_text_field_name is None:
            logger.warning(f"The audio field '{audio_field.reference_name}' hasn't defined a related text field.")
            continue

        try:
            __generate_audio_from_field(
                record,
                audio_field,
                spec
            )
        except KeyError:
            logger.warning(f"The field '{audio_field.name}' hasn't exist in the worksheet")


def __generate_audio_from_field(record: InputDataRecord, audio_field: DeckSpecificationField, spec: DeckSpecification):
    related_text_field = spec.find_spec_field_by_reference_name(audio_field.related_text_field_name)

    text_to_audio_field = record.find_field_by_name(related_text_field.name)
    raw_audio_filename_field = record.find_field_by_name(audio_field.name)

    speech.text_to_speech(
        text=text_to_audio_field.field_value,
        filename=__format_audio_name(raw_audio_filename_field.field_value),
        audio_folder_path=spec.media_folder_path
    )


def __format_audio_name(raw_audio_name: str):
    return raw_audio_name.replace("[sound:", "").replace("]", "")
