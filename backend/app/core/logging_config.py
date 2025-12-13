import logging
import sys
import json
from uvicorn.logging import DefaultFormatter

class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def configure_logging():
    """
    Configures the root logger to output JSON formatted logs to stdout.
    """
    handler = logging.StreamHandler(sys.stdout)
    # Use JSONFormatter for structured logging
    formatter = JSONFormatter()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplication
    root_logger.handlers = []
    root_logger.addHandler(handler)

    # Ensure uvicorn logs also use this configuration
    logging.getLogger("uvicorn.access").handlers = [handler]
    logging.getLogger("uvicorn.error").handlers = [handler]
