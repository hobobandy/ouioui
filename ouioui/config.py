from pathlib import Path

from dynaconf import Dynaconf, Validator

config = Dynaconf()

# delays validation (manually triggered after config file is loaded)
config.validators.register(
    Validator("db_path", cast=Path, default=Path.cwd() / "data/oui.db"),
    Validator("custom_oui", cast=set, default=set()),
)
