import argparse
import logging
import unittest
from ouioui import version as ouioui_version
import ouioui.ouioui as ouioui
from pathlib import Path


logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s %(module)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)


class TestFunctions(unittest.TestCase):
    test_config = ouioui.get_config(Path.cwd() / "tests/test_config.toml")
    test_config.db_path = Path.cwd() / "tests/test_ouioui.db"
    o = ouioui.Ouioui(test_config)

    def test1_version(self):
        logger.info(f"VERSION - Running {ouioui_version}")

    def test2_update(self):
        logger.info(f"UPDATE - Test database: {self.test_config.db_path}")
        self.o.update()
        logger.info("UPDATE - OK")

    def test3_query(self):
        # Supported formats
        # Should all normalize to AA:BB:CC
        logging.info(self.o.lookup("AABBCC"))
        logging.info(self.o.lookup("AABBCC11"))
        logging.info(self.o.lookup("AABBCC1122"))
        logging.info(self.o.lookup("AA:BB:CC"))
        logging.info(self.o.lookup("AA:BB:CC:11"))
        logging.info(self.o.lookup("AA:BB:CC:11:22"))
        logging.info(self.o.lookup("AA-BB-CC"))
        logging.info(self.o.lookup("AA-BB-CC-11"))
        logging.info(self.o.lookup("AA-BB-CC-11-22"))

    def test4_from_args(self):
        test_config_path = str(Path.cwd() / "tests/test_config.toml")
        args = argparse.Namespace(
            debug=False, config=test_config_path, query="AA:BB:CC"
        )
        ouioui.from_args(args)
        logger.info("FROM_ARGS - QUERY - OK")
        args = argparse.Namespace(debug=False, config=test_config_path, update=True)
        ouioui.from_args(args)
        logger.info("FROM_ARGS - UPDATE - OK")
        args = argparse.Namespace(
            debug=False, config=test_config_path, package_for_kismet=True
        )
        ouioui.from_args(args)
        logger.info("FROM_ARGS - PACKAGE_FOR_KISMET - OK")

    def test5_from_config(self):
        ouioui.from_config(Path.cwd() / "tests/test_config.toml")
        logger.info("FROM_CONFIG - OK")


if __name__ == "__main__":
    unittest.main()
