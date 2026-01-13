import logging
import logging.handlers
from pathlib import Path

from .infra.settings import settings


def setup_logging():
    log_path = Path(settings.get("log_path", "logs"))
    log_path.mkdir(exist_ok=True)

    log_file = log_path / "actions.log"

    formatter = logging.Formatter(
        '%(levelname)s %(asctime)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )


    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)

    # корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.get("log_level", "INFO")))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger


logger = setup_logging()
