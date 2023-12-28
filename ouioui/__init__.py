import argparse
import logging
from pathlib import Path

from .app import start_app
from .config import config


def main():
    parser = argparse.ArgumentParser(
        prog="ouioui",
        description="small utility script, and library, to download the IEEE OUI MA-L assignments file, override them if needed, and save them into a SQLite db to query.",
    )
    parser.add_argument(
        "--debug", action="store_true", help="increase verbosity with debug messages"
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="FILE",
        help="configuration file to override default settings",
    )
    group = parser.add_argument_group("actions", "one of these is required")
    mxgroup = group.add_mutually_exclusive_group(required=True)
    mxgroup.add_argument(
        "-q",
        "--query",
        help="OUI prefix to look up (charset: A-Z0-9, others will be removed)",
    )
    mxgroup.add_argument(
        "--update",
        action="store_true",
        help="fetch sources, load custom oui, rebuild database",
    )
    # mxgroup.add_argument(
    #     "--update_custom",
    #     action="store_true",
    #     help="load custom oui, update existing database"
    # )
    mxgroup.add_argument(
        "--package_for_kismet",
        action="store_true",
        help="fetch sources, package as .txt.gz for kismet (ouifile=<path> in kismet_site.conf)",
    )

    args = parser.parse_args()
    
    if args.config:
        config_file = Path(args.config).resolve(strict=True)
        config.load_file(path=config_file)
    
    config.validators.validate_all()
     
    if args.debug:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    logging.basicConfig(
        format="%(asctime)s: %(message)s", level=logging_level, datefmt="%H:%M:%S"
    )
    
    o = start_app(config)

    if args.update:
        o.update()
    # elif args.update_custom:
    #     o.update_custom()
    elif args.package_for_kismet:
        o.package_for_kismet()
    elif args.query:
        logging.info(o.lookup(args.query))


if __name__ == "__main__":
    main()
