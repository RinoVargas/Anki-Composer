class InputDataField:
    field_name: str
    field_value: str

    def __init__(self, field_name: str):
        self.field_name = field_name


class InputDataRecord:
    fields: list[InputDataField]

    def __init__(self, rows: list[InputDataField]):
        self.fields = rows

    def find_field_by_name(self, field_name: str):
        result = list(filter(lambda x: x.field_name == field_name, self.fields))
        return None if len(result) == 0 else result[0]


class InputData:
    records: list[InputDataRecord]
