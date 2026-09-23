"""Logging setup shared across the app."""
import logging
import sys

def get_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """Return a logger that writes formatted records to stdout.

    Safe to call repeatedly: handlers are attached only once per logger name.
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    #standard output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger