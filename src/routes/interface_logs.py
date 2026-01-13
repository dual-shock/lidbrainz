from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from src.logger import logger, sse_event_queue
import asyncio

router = APIRouter()


@router.get("/interface_logs")
async def interface_logs():
    async def event_generator():
        logger.info("interface connecting to event stream")
        while True:
            event = await sse_event_queue.get()
            yield f"data: {event}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")