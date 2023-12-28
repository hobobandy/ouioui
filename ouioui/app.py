import argparse
import gzip
import re
import logging

from datetime import datetime
from pathlib import Path

from .database import *
from .utils import get_ieee_oui, parse_custom_oui


logger = logging.getLogger(__name__)


class App:
    def __init__(self, config):
        self.config = config
    
    def db_init(self):
        db_file = Path(self.config.db_path)
        
        if not db_file.parent.exists():
            db_file.parent.mkdir(exist_ok=True)
            logger.debug(f"Making database folder: {config.db_path.parent}")
        else:
            logger.debug("Database folder already exists, moving on...")
        
        db = SqliteDatabase(db_file)
        db.bind([OUI, LastUpdate])
        db.connect()
        db.create_tables([OUI, LastUpdate])

    def update(self):
        self.db_init()
        
        lastUpdate, _ = LastUpdate.get_or_create(id=0, defaults={"timestamp": "Never"})
        logger.info(f"Last update: {lastUpdate.timestamp}")

        ieee_set = get_ieee_oui()
        custom_set = parse_custom_oui(self.config.custom_oui)

        for prefix, manuf in custom_set:
            if prefix in ieee_set:
                logger.info(
                    f"Custom OUI - Overriding {prefix} `{ieee_set[prefix].strip()}` with `{manuf.strip()}`."
                )
            else:
                logger.info(
                    f"Custom OUI - Adding {prefix} `{manuf}` from custom OUI list."
                )
            ieee_set[prefix] = manuf

        # Create OUI object for all matches
        list_oui = list()
        for prefix, org in ieee_set.items():
            oui = OUI(prefix=prefix, org=org)
            list_oui.append(oui)

        logger.info(f"Truncating OUI table ({OUI.select().count()} rows)...")
        schema = SchemaManager(OUI)
        schema.truncate_table()
        logger.info(f"OUI table now has {OUI.select().count()} rows")
        logger.info("Saving OUI records, this may take a while...")
        # Bulk create in batch of 500 records at a time
        OUI.bulk_create(list_oui, 500)
        # Update the last update value in database
        lastUpdate.update(
            {"timestamp": datetime.now().isoformat(timespec="seconds")}
        ).execute()
        logger.info(f"Total of {len(list_oui)} OUI records saved.")

    def update_custom(self):
        self.db_init()
        
        lastUpdate, _ = LastUpdate.get_or_create(id=0, defaults={"timestamp": "Never"})
        logger.info(f"Last update: {lastUpdate.timestamp}")

        ieee_set = get_ieee_oui()  # @todo load from database existing entries
        custom_set = parse_custom_oui(self.config.custom_oui)

        for prefix, manuf in custom_set:
            if prefix in ieee_set:
                logger.info(
                    f"Overriding {prefix} `{ieee_set[prefix].strip()}` with `{manuf.strip()}`."
                )
            else:
                logger.info(f"Adding {prefix} `{manuf}` from custom OUI list.")
            ieee_set[prefix] = manuf

    def package_for_kismet(self):
        ieee_set = get_ieee_oui()
        custom_set = parse_custom_oui(self.config.custom_oui)

        for prefix, manuf in custom_set:
            if prefix in ieee_set:
                logger.info(
                    f"Overriding {prefix} `{ieee_set[prefix].strip()}` with `{manuf.strip()}`."
                )
            else:
                logger.info(f"Adding {prefix} `{manuf}` from custom OUI list.")
            ieee_set[prefix] = manuf

        final_set = set(
            f"{prefix}\t{manuf.strip()}" for prefix, manuf in ieee_set.items()
        )

        content = bytes("\n".join(sorted(final_set)), "utf-8")
        gzip_content = gzip.compress(content)

        logger.info(f"Prepared {len(final_set)} records to save...")

        # parent existence already checked from_args/from_config
        out_path = self.config.db_path.parent / "kismet_manuf.txt.gz"
        with out_path.open("wb") as f:
            f.write(gzip_content)

        logger.info(f"Successfully packaged OUI file for Kismet.")
        logger.info(
            f"To use, add the following to your kismet_site.conf:\nouifile={out_path}"
        )

    def lookup(self, addr: str) -> set:
        self.db_init()
        
        # match AA-BB-CC, AA:BB:CC, AABBCC - up to full MAC addr
        m = re.fullmatch(
            r"^([0-9A-F]{2})[:-]?([0-9A-F]{2})[:-]?([0-9A-F]{2})(?:[:-]?(?:[0-9A-F]{2})?[:-]?(?:[0-9A-F]{2})?[:-]?(?:[0-9A-F]{2})?)?$",
            addr.upper(),
        )
        if m:
            # normalize to AA:BB:CC
            normalized_oui = f"{m[1]}:{m[2]}:{m[3]}"
        else:
            raise ValueError("Invalid OUI or MAC address passed.")
        logger.info(f"Looking up: {normalized_oui}")
        # Retrieve MAC info from OUI database
        i = OUI.select(OUI.org).where(OUI.prefix.startswith(normalized_oui))
        # Return information as a tuple (supports one or more result)
        return set(o.org for o in i)


def start_app(config):
    return App(config)
