import unittest

from anki import deck_builder
from test import XLSX_COMPOSER_FILE_PATH, FRONTEND_TEMPLATE_FILE_PATH, BACK_TEMPLATE_FILE_PATH
from compose.deck_composer import DeckComposer
from compose.deck_specification import DeckSpecificationField, DeckInputConfig, DeckOutputConfig, FrontTemplate, BackTemplate


class DeckComposerTest(unittest.TestCase):

    @staticmethod
    def __create_composer():
        composer = DeckComposer(XLSX_COMPOSER_FILE_PATH)
        composer.generate_specifications()
        return composer

    def test_compose_file_path_value(self):
        composer = DeckComposerTest.__create_composer()
        result = getattr(composer, '_file_path')
        self.assertTrue(result, XLSX_COMPOSER_FILE_PATH)

    def test_compose_specifications_size(self):
        composer = DeckComposerTest.__create_composer()
        result = getattr(composer, '_specifications')
        self.assertTrue(len(result), 1)

    def test_composer_specification_back_template_value(self):
        composer = DeckComposerTest.__create_composer()
        result = getattr(composer, '_specifications')
        back_template: BackTemplate | None = getattr(result[0], 'back_template')
        self.assertIsNotNone(back_template)
        self.assertEquals(back_template.value,
                          '<i>Meaning:</i> {{MEANING}}\n<hr id=answer>\n<i>Examples:</i> \n<ul>\n        <li>{{EXAMPLE_1}} {{$_EXAMPLE_1}}</li>\n        <li>{{EXAMPLE_2}} {{$_EXAMPLE_2}}</li>\n        <li>{{EXAMPLE_3}} {{$_EXAMPLE_3}}</li>\n</ul>\n')

    def test_composer_specification_back_template_file(self):
        composer = DeckComposerTest.__create_composer()
        result = getattr(composer, '_specifications')
        back_template: BackTemplate | None = getattr(result[0], 'back_template')
        back_template.html_file = BACK_TEMPLATE_FILE_PATH
        self.assertIsNotNone(back_template)
        self.assertEquals(deck_builder.html_file_to_string(back_template.html_file), '<div>\n    <p>This is the back_template: {{MEANING}}</p>\n</div>')

    def test_composer_specification_deck_name_value(self):
        composer = DeckComposerTest.__create_composer()
        result = getattr(composer, '_specifications')
        deck_name = getattr(result[0], 'deck_name')
        self.assertEquals(deck_name, 'English Golden List')

    def test_composer_specification_front_template_value(self):
        composer = DeckComposerTest.__create_composer()
        result = getattr(composer, '_specifications')
        front_template: FrontTemplate | None = getattr(result[0], 'front_template')
        self.assertIsNotNone(front_template)
        self.assertEquals(front_template.value,
                          "<div style='font-family: arial; font-size: 25px; text-align: center; color: white;'>{{EXPRESSION}}</div>")

    def test_composer_specification_front_template_file(self):
        composer = DeckComposerTest.__create_composer()
        result = getattr(composer, '_specifications')
        front_template: FrontTemplate | None = getattr(result[0], 'front_template')
        front_template.html_file = FRONTEND_TEMPLATE_FILE_PATH
        self.assertIsNotNone(front_template)
        self.assertEquals(deck_builder.html_file_to_string(front_template.html_file), '<div>\n    <p>This is the frontend_template: {{MEANING}}</p>\n</div>')

    def test_composer_specification_media_folder_path_value(self):
        composer = DeckComposerTest.__create_composer()
        result = getattr(composer, '_specifications')
        media_folder_path = getattr(result[0], 'media_folder_path')
        self.assertEquals(media_folder_path, '/my/audio/folder')

    def test_composer_specification_text_field_value(self):
        composer = DeckComposerTest.__create_composer()
        result = getattr(composer, '_specifications')
        fields = getattr(result[0], 'fields')
        field: DeckSpecificationField = fields[0]

        self.assertEquals(field.field_type, 'TEXT')
        self.assertEquals(field.name, 'EXPRESSION')

    def test_composer_specification_audio_field_value(self):
        composer = DeckComposerTest.__create_composer()
        result = getattr(composer, '_specifications')
        fields = getattr(result[0], 'fields')

        field_1: DeckSpecificationField = fields[2]
        field_2: DeckSpecificationField = fields[3]
        field_3: DeckSpecificationField = fields[4]

        self.assertIsNotNone(field_1, None)
        self.assertIsNotNone(field_2, None)
        self.assertIsNotNone(field_3, None)

        self.assertEqual(field_1.field_type, 'AUDIO')
        self.assertEqual(field_1.name, 'EXAMPLE_1')

        self.assertEqual(field_2.field_type, 'AUDIO')
        self.assertEqual(field_2.name, 'EXAMPLE_2')

        self.assertEqual(field_3.field_type, 'AUDIO')
        self.assertEqual(field_3.name, 'EXAMPLE_3')

    def test_composer_specification_input_config_value(self):
        composer = DeckComposerTest.__create_composer()
        result = getattr(composer, '_specifications')
        input_config: DeckInputConfig = getattr(result[0], 'input_config')

        self.assertEquals(input_config.type, 'xlsx')
        self.assertEquals(input_config.file_path, '/my/specific/file.xlsx')

    def test_composer_specification_output_config_value(self):
        composer = DeckComposerTest.__create_composer()
        result = getattr(composer, '_specifications')
        output_config: DeckOutputConfig = getattr(result[0], 'output_config')

        self.assertEquals(output_config.filename, 'my-package.dpkg')
        self.assertEquals(output_config.folder_path, '/my/output/folder')


if __name__ == '__main__':
    unittest.main()
