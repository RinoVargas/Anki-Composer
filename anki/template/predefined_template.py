class PredefinedTemplate:
    __deck_name = None
    __front_template = None
    __back_template = None
    __audio_folder = None

    def __init__(self, deck_name, front_template, back_template):
        self.__deck_name = deck_name
        self.__front_template = front_template
        self.__back_template = back_template

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
