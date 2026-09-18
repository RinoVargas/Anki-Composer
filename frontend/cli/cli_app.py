import argparse
from backend.compose.deck_composer import DeckComposer

def run(args=None):
    parser = argparse.ArgumentParser(description="Anki Deck Composer - CLI")
    parser.add_argument("descriptor_path_positional", nargs="?", default=None, help="Path to descriptor YAML file")
    parser.add_argument("--descriptor-path", "-d", dest="descriptor_path_flag", default=None, help="Path to descriptor YAML file")
    
    parsed_args = parser.parse_args(args)
    deck_composer_file = parsed_args.descriptor_path_flag or parsed_args.descriptor_path_positional
    
    if not deck_composer_file:
        parser.error("the following arguments are required: descriptor-path (positional or via --descriptor-path)")
        
    compose = DeckComposer(deck_composer_file)
    compose.compose()
