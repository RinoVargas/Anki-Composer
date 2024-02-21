import unittest
from test import XLSX_COMPOSER_FILE_PATH
from compose.deck_composer import DeckComposer
from compose.deck_specification import DeckSpecificationField, DeckInputConfig, DeckOutputConfig


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
        back_template = getattr(result[0], 'back_template')
        self.assertEquals(back_template,
                          '<i>Meaning:</i> {{MEANING}}\n<hr id=answer>\n<i>Examples:</i> \n<ul>\n        <li>{{EXAMPLE 1}} {{AUDIO 1}}</li>\n        <li>{{EXAMPLE 2}} {{AUDIO 2}}</li>\n        <li>{{EXAMPLE 3}} {{AUDIO 3}}</li>\n</ul>\n')

    def test_composer_specification_deck_name_value(self):
        composer = DeckComposerTest.__create_composer()
        result = getattr(composer, '_specifications')
        deck_name = getattr(result[0], 'deck_name')
        self.assertEquals(deck_name, 'English Golden List')

    def test_composer_specification_front_template_value(self):
        composer = DeckComposerTest.__create_composer()
        result = getattr(composer, '_specifications')
        front_template = getattr(result[0], 'front_template')
        self.assertEquals(front_template,
                          "<div style='font-family: arial; font-size: 25px; text-align: center; color: white;'>{{EXPRESSION}}</div>")

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
        self.assertEquals(field.reference_name, 'expression')
        self.assertEquals(field.related_text_field_name, None)

    def test_composer_specification_audio_field_value(self):
        composer = DeckComposerTest.__create_composer()
        result = getattr(composer, '_specifications')
        fields = getattr(result[0], 'fields')

        self.assertIsNotNone(fields[0], None)
        field: DeckSpecificationField = fields[5]

        self.assertEqual(field.field_type, 'AUDIO')
        self.assertEqual(field.name, 'AUDIO 1')
        self.assertEqual(field.reference_name, 'audio_1')
        self.assertEqual(field.related_text_field_name, 'example_1')

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
