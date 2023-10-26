import logging
import re
import requests


logger = logging.getLogger(__name__)


def get_ieee_oui(prefix_type: str = 'base 16'):
    url = 'https://standards-oui.ieee.org/oui/oui.txt' # MA-L Assignments
    ieee_set = set()
    
    logger.info("IEEE OUI - Downloading the latest data file...")
    try:
        r = requests.get(url)
    except requests.RequestException as e:
        logger.critical(e)
    except:
        logger.critical("Unknown exception caught, couldn't download OUI data file.")
    else:
        # Extract only the prefix and organization information
        matches = re.findall(r'^([0-9A-F]{2})-([0-9A-F]{2})-([0-9A-F]{2})\s{1,10}\(hex\)\t{1,5}(.{1,128})$', r.text, re.MULTILINE)
        ieee_set = {f"{m[0]}:{m[1]}:{m[2]}": m[3] for m in matches}

        logger.info(f"IEEE OUI - Found {len(ieee_set)} records...")
    finally:
        return ieee_set
