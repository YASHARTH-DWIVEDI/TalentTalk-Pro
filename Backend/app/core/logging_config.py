import logging
import sys
import json
from .config import settings

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def setup_logging():
    logger = logging.getLogger("talenttalk")
    logger.setLevel(settings.LOG_LEVEL)
    
    console_handler = logging.StreamHandler(sys.stdout)
    
    if settings.ENVIRONMENT == "production":
        console_handler.setFormatter(JsonFormatter())
    else:
        # Standard readable format for dev
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        
    logger.addHandler(console_handler)
    
    # Also capture uvicorn logs if in prod
    if settings.ENVIRONMENT == "production":
        uvicorn_logger = logging.getLogger("uvicorn.access")
        uvicorn_logger.handlers = [console_handler]

    return logger

logger = setup_logging()
