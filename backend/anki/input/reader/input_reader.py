from backend.compose.deck_specification import DeckSpecification
from backend.anki.input.input_data import InputData, InputDataRecord, InputDataField


class InputReader:
    _spec: DeckSpecification

    def __init__(self, spec: DeckSpecification):
        self._spec = spec

    def _create_record(self):
        return InputDataRecord(rows=[InputDataField(field_name=field.column_name) for field in self._spec.fields])

    def read_input(self) -> InputData: pass

