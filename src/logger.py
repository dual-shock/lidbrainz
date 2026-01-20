import logging
import asyncio
import json
from datetime import datetime

sse_event_queue = asyncio.Queue() 
class SSEHandler(logging.Handler):
    def emit(self, record):
        if not getattr(record, "frontend", False):
            return

        event_json = self.format(record)
        event_json = {
            "event_time": datetime.fromtimestamp(record.created).strftime("%H:%M:%S"),
            "event_type": record.levelname,
            "event_content": record.getMessage()
        }

        try:
            event_json = json.dumps(event_json)
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(sse_event_queue.put_nowait, event_json)
        
        except RuntimeError:
            pass

def setup_logging(): 
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    StreamHandler = SSEHandler()
    StreamHandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    ConsoleHandler = logging.StreamHandler()
    ConsoleHandler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

    logger.handlers = []
    logger.addHandler(StreamHandler)
    logger.addHandler(ConsoleHandler)
    return logging.getLogger()

def cleanup_logging():
    logger = logging.getLogger()
    handlers = logger.handlers[:]
    
    for handler in handlers:
        logger.removeHandler(handler)
        handler.close()

    logging.shutdown()

if not logging.getLogger().handlers:
    logger = setup_logging()
else:
    logger = logging.getLogger()
    