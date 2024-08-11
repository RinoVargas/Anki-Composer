from typing import Final


class GenericTemplate:
    value: str | None = None
    file_path: str | None = None

    def __init__(self, data: dict):
        self.value = data.setdefault("value", None)
        self.html_file = data.setdefault("file_path", None)

    def __getitem__(self, item):
        if "file_path" == item:
            return self.file_path

        if "value" == item:
            return self.value

        raise KeyError(f"Unknown key: {item}")


class FrontTemplate(GenericTemplate):

    def __init__(self, data: dict):
        super().__init__(data)

    def __getitem__(self, item):
        return super().__getitem__(item)


class BackTemplate(GenericTemplate):

    def __init__(self, data: dict):
        super().__init__(data)

    def __getitem__(self, item):
        return super().__getitem__(item)


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

    def __init__(self, output_config: dict):
        self.folder_path = output_config.get('folder_path')
        self.filename = output_config.setdefault('filename', None)


class DeckSpecificationFieldType:
    TEXT: Final = 'TEXT'
    AUDIO: Final = 'AUDIO'


class DeckInputType:
    GSHEET = 'gsheet'
    XLSX = 'xlsx'


class DeckSpecificationField:
    name: str
    generate_audio_file: bool

    def __init__(self, name: str):
        self.name = name
        self.generate_audio_file = False


class DeckSpecificationFieldBuilder:
    __field = None

    def __init__(self, field: DeckSpecificationField):
        self.__field = field

    @staticmethod
    def new_field(name: str):
        builder = DeckSpecificationFieldBuilder(DeckSpecificationField(name))
        return builder

    def generate_audio_file(self, generate_audio_file: bool):
        self.__field.generate_audio_file = generate_audio_file
        return self

    def build(self) -> DeckSpecificationField:
        return self.__field


class DeckSpecification:
    deck_name: str = None
    input_config: DeckInputConfig = None
    media_folder_path: str = None
    disable_audio_generation: bool
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
        self.disable_audio_generation = not not deck_spec_dict.get('disable_audio_generation')
        self.collect_fields(deck_spec_dict["fields"])
        self.front_template = FrontTemplate(deck_spec_dict['front_template'])
        self.back_template = BackTemplate(deck_spec_dict['back_template'])
        self.output_config = DeckOutputConfig(output_config=deck_spec_dict['output'])

    def collect_fields(self, deck_spec_dict: dict):
        self.fields = list(map(lambda key: DeckSpecification.__map_field(deck_spec_dict, key) ,deck_spec_dict.keys()))

    @staticmethod
    def __map_field(deck_spec_dict: dict, key: str):
        name = deck_spec_dict[key]["name"]
        generate_audio_file = not not deck_spec_dict[key].get("generate_audio_file")

        return (DeckSpecificationFieldBuilder.new_field(name)
                .generate_audio_file(generate_audio_file)
                .build())

    def add_spec_field(self, spec_field: DeckSpecificationField):
        self.fields.append(spec_field)