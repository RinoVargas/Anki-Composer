import csv
import requests
from backend.anki.input.input_data import InputData, InputDataRecord
from backend.anki.input.reader.input_reader import InputReader
from backend.compose.deck_specification import DeckSpecification


class CSVInputReader(InputReader):

    def __init__(self, spec: DeckSpecification):
        super().__init__(spec)

    def read_input(self) -> InputData:
        data = InputData()
        file_path = self._spec.input_config.file_path
        lines = _load_csv_lines(file_path)

        reader = csv.DictReader(lines)
        records = []

        for row in reader:
            record: InputDataRecord = self._create_record()
            for field in record.fields:
                field.field_value = row.get(field.field_name, "")
            records.append(record)

        data.records = records
        return data


def _load_csv_lines(file_path: str) -> list[str]:
    if file_path.startswith("http://") or file_path.startswith("https://"):
        response = requests.get(file_path)
        response.raise_for_status()
        text = response.text
        return text.splitlines()
    else:
        with open(file_path, mode="r", encoding="utf-8-sig", errors="replace") as f:
            return f.readlines()
