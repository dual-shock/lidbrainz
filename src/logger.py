import logging
import asyncio
import json
from datetime import datetime

sse_event_queue = asyncio.Queue() # for the frontend event stream




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
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(sse_event_queue.put_nowait, event_json)
        except RuntimeError:
            pass

def setup_logging(): 
    StreamHandler = SSEHandler()
    StreamHandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(StreamHandler)
    return logging.getLogger()
logger = setup_logging()
    