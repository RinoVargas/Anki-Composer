import sys
from argparse import ArgumentParser

from compose.deck_composer import DeckComposer

DESCRIPTOR_PATH_ARG = "descriptor-path"


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Anki Deck Composer")
    parser.add_argument("descriptor_path_positional", nargs="?", default=None, help="Path to descriptor YAML file")
    parser.add_argument("--descriptor-path", "-d", dest="descriptor_path_flag", default=None, help="Path to descriptor YAML file")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    deck_composer_file = args.descriptor_path_flag or args.descriptor_path_positional
    if not deck_composer_file:
        parser.error("the following arguments are required: descriptor-path (positional or via --descriptor-path)")
    compose = DeckComposer(deck_composer_file)
    compose.compose()


if __name__ == "__main__":
    main()
