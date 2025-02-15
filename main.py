import sys
from argparse import ArgumentParser

from compose.deck_composer import DeckComposer

DESCRIPTOR_PATH_ARG = "descriptor-path"


def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument(DESCRIPTOR_PATH_ARG)
    return parser


def main():
    parser = create_parser()
    result = vars(parser.parse_args())
    deck_composer_file = result.get(DESCRIPTOR_PATH_ARG)
    compose = DeckComposer(deck_composer_file)
    compose.compose()


if __name__ == "__main__":
    main()
