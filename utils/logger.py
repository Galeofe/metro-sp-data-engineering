import logging
import sys
import io

_FMT = "%(asctime)s  %(levelname)-8s  %(name)-30s  %(message)s"
_DATE = "%H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Força UTF-8 no stdout do Windows para evitar UnicodeEncodeError
        stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.Formatter(_FMT, datefmt=_DATE))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
