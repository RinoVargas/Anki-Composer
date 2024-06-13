class InputDataField:
    field_name: str
    field_value: str

    def __init__(self, field_name: str):
        self.field_name = field_name


class InputDataRecord:
    fields: list[InputDataField]

    def __init__(self, rows: list[InputDataField]):
        self.fields = rows

    def find_field_by_name(self, field_name: str) -> InputDataField | None:
        result = list(filter(lambda x: x.field_name == field_name, self.fields))

        if len(result) == 0:
            raise ValueError(f"The field named {field_name} hasn't found.")

        return result[0]

    def add_field(self, field: InputDataField):
        self.fields.append(field)


class InputData:
    records: list[InputDataRecord]
