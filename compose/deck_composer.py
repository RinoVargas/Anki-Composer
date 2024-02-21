import yaml
import os
import logger

from compose.deck_specification import DeckSpecification
from compose import composer_parser
import anki.deck_builder as builder

logger = logger.get_new_logger("deck-composer")


class DeckComposer:
    _file_path = None
    _specifications: list[DeckSpecification] = None

    def __init__(self, file_path):
        self._file_path = file_path

    def compose(self):

        self.validate()
        self._specifications = composer_parser.parse(self._file_path)

        for spec in self._specifications:
            builder.build(spec)

    def validate(self):
        if self._file_path is None or not self._file_path:
            raise ValueError("You must define a compose-file path")

        if not os.path.exists(self._file_path):
            raise ValueError(f"The compose-file hasn't found in '{self._file_path}'")
