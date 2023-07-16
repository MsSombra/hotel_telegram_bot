import logging.config
import sys

# Словарь с описанием конфигурации для логгирования (консоль и файл)

dict_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "oneFormatter": {
            "format": "%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s",
            "datefmt": "%m.%d.%Y %H:%M:%S"
        },
    },
    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "oneFormatter",
            "stream": sys.stdout,
        },
        "fileHandler": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "oneFormatter",
            "filename": "log_file.log",
        }
    },
    "loggers": {
      "appLogger": {
          "level": "DEBUG",
          "handlers": ["consoleHandler", "fileHandler"],
          "qualname": "appLogger",
          "propagate": False
      }
    },
    "root": {
        "level": "DEBUG",
    }
}


def logging_config():
    logging.config.dictConfig(dict_config)


logger = logging.getLogger("appLogger")
