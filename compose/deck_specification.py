from typing import Final


class GenericTemplate:
    value: str | None
    file_path: str | None

    def __init__(self, data: dict):
        self.value = data.setdefault("value", None)
        self.html_file = data.setdefault("file_path", None)


class FrontTemplate(GenericTemplate):

    def __init__(self, data: dict):
        super().__init__(data)


class BackTemplate(GenericTemplate):

    def __init__(self, data: dict):
        super().__init__(data)


class DeckInputConfig:
    type: str = None
    file_path: str = None
    sheets: list[str] = []

    def __init__(self, input_type: str, file_path=None, sheets=None):
        self.type = input_type
        self.file_path = file_path
        self.sheets = [] if sheets is None else sheets


class DeckOutputConfig:
    folder_path: str = None
    filename: str | None = None

    def __init__(self, folder_path: str, filename: str | None = None):
        self.folder_path = folder_path
        self.filename = filename


class DeckSpecificationFieldType:
    TEXT: Final = 'TEXT'
    AUDIO: Final = 'AUDIO'


class DeckInputType:
    GSHEET = 'gsheet'
    XLSX = 'xlsx'


class DeckSpecificationField:
    reference_name: str
    name: str
    field_type: str
    related_text_field_name: str | None

    def __init__(self, reference_name: str, name: str, field_type: str | None, related_text_field_name: str | None):
        self.reference_name = reference_name
        self.name = name
        self.field_type = DeckSpecificationFieldType.TEXT if field_type is None else field_type
        self.related_text_field_name = related_text_field_name


class DeckSpecification:
    deck_name: str = None
    input_config: DeckInputConfig = None
    media_folder_path: str = None
    fields: list[DeckSpecificationField] = []
    front_template: FrontTemplate = None
    back_template: BackTemplate = None
    output_config: DeckOutputConfig = None

    def __init__(self, deck_spec_dict: dict):
        input_dict: dict[str, any] = deck_spec_dict['input']

        self.deck_name = deck_spec_dict["deck_name"]
        self.input_config = DeckInputConfig(
            input_type=input_dict["type"],
            file_path=input_dict["file_path"],
            sheets=input_dict.setdefault('sheets', None)
        )
        self.media_folder_path = deck_spec_dict['media_folder_path']
        self.collect_fields(deck_spec_dict["fields"])
        self.front_template = FrontTemplate(deck_spec_dict['front_template'])
        self.back_template = BackTemplate(deck_spec_dict['back_template'])
        self.output_config = DeckOutputConfig(
            folder_path=deck_spec_dict['output']['folder_path'],
            filename=deck_spec_dict['output']['filename']
        )

    def collect_fields(self, deck_spec_dict: dict):
        self.fields = [DeckSpecificationField(
            reference_name=key,
            name=deck_spec_dict[key]["name"],
            field_type=deck_spec_dict[key].get("field_type"),
            related_text_field_name=deck_spec_dict[key].get("related_text_field_name")) for key in deck_spec_dict.keys()
        ]

    def find_spec_field_by_reference_name(self, reference_name: str):
        result = list(filter(lambda x: x.reference_name == reference_name, self.fields))
        return None if len(result) == 0 else result[0]
