from backend.anki.input.reader.input_reader import InputReader
from backend.anki.input.input_data import InputData, InputDataRecord, InputDataField
from backend.db import deck_repository

class SQLiteInputReader(InputReader):
    def __init__(self, spec):
        self.spec = spec
        self.table_name = spec.table_name

    def read_input(self) -> InputData:
        records = []
        for batch in deck_repository.fetch_data_batch(self.table_name, 1000):
            for row in batch:
                fields = []
                for f_spec in self.spec.fields:
                    val = row.get(f_spec.id, "")
                    if f_spec.generate_audio_file:
                        audio_val = row.get(f_spec.id + "_$", "")
                        if audio_val:
                            val = f"{val} [sound:{audio_val}]"
                    
                    f = InputDataField(f_spec.id.upper())
                    f.field_value = val
                    fields.append(f)
                records.append(InputDataRecord(fields))
                
        data = InputData()
        data.records = records
        return data
