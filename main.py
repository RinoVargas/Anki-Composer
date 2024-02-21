import sys

from compose.deck_composer import DeckComposer


def main():
    deck_composer_file = sys.argv[1]
    compose = DeckComposer(deck_composer_file)
    compose.compose()


if __name__ == "__main__":
    main()
