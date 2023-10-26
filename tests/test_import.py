import logging
import unittest


logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s %(module)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)


class TestImport(unittest.TestCase):
    def test_import(self):
        try:
            exec("from ouioui import *")
        except:
            logger.info("from ouioui import * -- FAILED")
        else:
            logger.info("from ouioui import * -- OK")


if __name__ == "__main__":
    unittest.main()
