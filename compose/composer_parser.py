import yaml
import logger

from compose.deck_specification import DeckSpecification

logger = logger.get_new_logger("composer-parser")

__version_supports = {
    "V1": '1.0'
}


def parse(file_path):
    try:
        file = open(file_path, 'r')

    except Exception as e:
        logger.error(f"Error: {e}")
        raise f'An error occurred during the compose-file reading: {e}'

    with file:
        compose_dict = yaml.load(file, Loader=yaml.Loader)
        file.close()
        return _parse_specifications(compose_dict['decks'])


def _validate(compose_dict):
    if not compose_dict['version']:
        raise ValueError("The 'version' attribute must be defined")

    if not __version_supports['V1'] == compose_dict['version']:
        raise ValueError(f"The deck-composer file version is not supported: {compose_dict['version']}")

    if not compose_dict['decks']:
        raise ValueError("The 'decks' attribute must be defined")


def _parse_specifications(compose_dict: dict):
    return [DeckSpecification(compose_dict[spec_name]) for spec_name in compose_dict.keys()]
