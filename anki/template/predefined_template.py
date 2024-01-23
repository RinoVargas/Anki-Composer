class PredefinedTemplate:
    __fields = []
    __deck_name = None
    __front_template = None
    __back_template = None
    __audio_folder = None

    def __init__(self, deck_name, front_template, back_template, fields):
        self.__deck_name = deck_name
        self.__front_template = front_template
        self.__back_template = back_template
        self.__fields = fields

    def get_back_template(self):
        return self.__back_template

    def get_front_template(self):
        return self.__front_template

    def get_deck_name(self):
        return self.__deck_name

    def get_audio_folder(self):
        return self.__audio_folder

    def set_audio_folder(self, audio_folder):
        self.__audio_folder = audio_folder

    def get_fields(self):
        return self.__fields


class TemplateField:
    __name = None
    __field_type = None
    __related_text_field_name = None

    def __init__(self, name, field_type="TEXT", related_text_field_name=None):
        self.__name = name
        self.__field_type = field_type
        self.__related_text_field_name = related_text_field_name

    def get_name(self):
        return self.__name

    def get_field_type(self):
        return self.__field_type

    def get_related_text_field_name(self):
        return self.__related_text_field_name
