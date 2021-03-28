from os import getenv
from typing import Final
from dotenv import load_dotenv

load_dotenv
class Config():

    try:
        with open(getenv("TOKEN", "")) as f:
            token = f.read()
    except FileNotFoundError:
        token = getenv("TOKEN", "")

    try:
        with open(getenv("DSN", "")) as f:
            dsn = f.read()
    except  FileNotFoundError:
        dsn = getenv("DSN", "")

    TOKEN: Final = token
    DSN: Final = dsn
    DEFAULT_PREFIX: Final = getenv("DEFAULT_PREFIX", '#$')    
    BOT_NAME: Final = getenv("BOT_NAME", "Mystro")