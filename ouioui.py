import argparse
import logging
import tomllib
from pathlib import Path
from dataclasses import fields, dataclass
from ouioui import OUIManager

@dataclass
class OUIConfig:
    db_path: Path = Path.cwd() / "oui.db"
    logging_level: int = logging.INFO
    sources: set = (
        'https://standards-oui.ieee.org/oui/oui.txt',
    )


def get_config(config_path: Path, to_override: OUIConfig = None) -> OUIConfig:
    if to_override:
        config = to_override
    else:
        config = OUIConfig()

    try:
        with open(config_path, "rb") as f:
            config_dict = tomllib.load(f)
            for field in fields(config):
                try:
                    # @todo is there a more clever way to do this?
                    match field.name:
                        case "db_path":
                            setattr(config, field.name, Path(config_dict[field.name]))
                        case _:
                            setattr(config, field.name, config_dict[field.name])
                except KeyError:
                    continue
    except tomllib.TOMLDecodeError:
        logging.error(
            "Invalid configuration, ignored and using defaults."
        )  # @todo probably not the expected behavior, so change this?

    return config


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Microservice to download OUI sources and normalize them into a database to query."
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="FILE",
        help="configuration file to override default settings",
    )
    parser.add_argument(
        "--debug", action="store_true", help="increase verbosity with debug messages"
    )
    
    # @todo add lookup from commandline?

    args = parser.parse_args()
    
    config = get_config("config.toml")

    if args.config:
        config = get_config(args.config, config)
    
    if args.debug:
        logging_level = logging.DEBUG
    else:
        logging_level = config.logging_level

    logging.basicConfig(
        format="%(asctime)s: %(message)s", level=logging_level, datefmt="%H:%M:%S"
    )

    o = OUIManager(config.db_path)
    o.update()
    logging.info(o.lookup("A4C7F6"))