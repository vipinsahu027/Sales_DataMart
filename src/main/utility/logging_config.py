import logging
import sys
import os
import json
from logging.handlers import RotatingFileHandler
import datetime

# Toggle for enabling/disabling file logging
ENABLE_FILE_LOGGING = False

class JSONFormatter(logging.Formatter):
    def format(self, record):
        # 'record.module' automatically contains the calling module's name
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "module": record.module,  # <-- calls the actual module name
            "message": record.getMessage(),
        }
        return json.dumps(log_record)

class Logger:
    _instance = None  # Private class-level variable to store the single instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)

            # We fix the logger name to "Sales_DataMart" for a true Singleton
            logger_name = "Sales_DataMart"
            cls._instance.logger = logging.getLogger(logger_name)
            cls._instance.logger.setLevel(logging.INFO)


            # Create console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_format = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"
            console_formatter = logging.Formatter(console_format)
            console_handler.setFormatter(console_formatter)

            # Add console handler (always enabled)
            cls._instance.logger.addHandler(console_handler)

            # Only add file logging if ENABLE_FILE_LOGGING is True
            if ENABLE_FILE_LOGGING:
                log_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', "logs")
                os.makedirs(log_dir, exist_ok=True)
                timestamp = datetime.datetime.now().strftime("%Y%m%d")
                log_file = os.path.join(log_dir,f"application_{timestamp}.log")

                # Create handlers (console + rotating file)
                file_handler = RotatingFileHandler(log_file, mode='w' ,maxBytes=5*1024*1024, backupCount=5)

                # JSON format for file, also showing actual module from record.module
                json_formatter = JSONFormatter()

                # Assign formatters to handlers
                file_handler.setFormatter(json_formatter)

                cls._instance.logger.addHandler(file_handler)

            # Prevent logs from being passed to the root logger
            cls._instance.logger.propagate = False

        return cls._instance

    def get_logger(self):
        return self.logger

# Singleton logger accessor
logger = Logger().get_logger()
