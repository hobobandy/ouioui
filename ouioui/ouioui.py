"""
Simple module that downloads a sanitized IEEE OUI data file
to generate a SQLite3 database for later use.
"""

import re
import requests
import logging
from datetime import datetime
from peewee import *
from pathlib import Path

class OUI(Model):
    prefix = CharField()
    org = CharField()

class LastUpdate(Model):
    timestamp = TextField()

class OUIManager:
    def __init__(self, db_path: Path):
        db = SqliteDatabase(db_path)
        db.bind([OUI, LastUpdate])
        db.connect()
        db.create_tables([OUI, LastUpdate])
    
    def update(self):
        lastUpdate, _ = LastUpdate.get_or_create(id=0, defaults={'timestamp': 'Never'})
        logging.info("Last update: %s" % lastUpdate.timestamp)
        logging.info("Truncating OUI table (%s rows)..." % OUI.select().count())
        schema = SchemaManager(OUI)
        schema.truncate_table()
        logging.info("OUI table now has %s rows" % OUI.select().count())
        logging.info("Downloading the latest IEEE OUI data file...")
        # Download the latest sanitized IEEE OUI data file
        try:
            r = requests.get('https://standards-oui.ieee.org/oui/oui.txt')
        except requests.RequestException as e:
            logging.critical(e)
            return
        except:
            logging.critical("Unknown exception caught, couldn't download OUI data file.")
            return

        # Extract only the MAC prefix and organization information
        # m = re.findall(r'^([0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2})   \(hex\)\t\t(.{1,128})$', r.text, re.MULTILINE)
        m = re.findall(r'^([0-9A-F]{6})     \(base 16\)\t\t(.{1,128})$', r.text, re.MULTILINE)
        logging.info("Found %s records to save..." % len(m))

        # Create OUI object for all matches
        list_oui = list()
        for prefix, org in m:
            oui = OUI()
            oui.prefix = prefix.replace('-', '')
            oui.org = re.sub("[\r\n\t]", "", org)
            list_oui.append(oui)

        logging.info("Saving OUI records, this may take a while...")
        # Bulk create in batch of 500 records at a time
        OUI.bulk_create(list_oui, 500)
        # Update the last update value in database
        lastUpdate.update({'timestamp': datetime.now().isoformat(timespec='seconds')}).execute()
        logging.info("Total of %s OUI records saved." % len(list_oui))
    
    def lookup(self, m):
        # Normalize MAC argument (credit to Craig Balfour for this simple, yet effective way)
        m = re.sub("[.:-]", "", m)
        if len(m) < 6:
            # Prefix needs 3 bytes minimum (6 chars)
            return False
        m = m.upper()
        # Retrieve MAC info from OUI database
        i = OUI.select(OUI.org).where(OUI.prefix.startswith(m))
        # Return information as a tuple (supports one or more result)
        return [o.org for o in i]