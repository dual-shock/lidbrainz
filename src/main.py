import logging
from src.config import Config
from src.api.app import start
import uvicorn 
import asyncio
from src.logger import logger





def main():
    Config.check()
    api_app = start()

    config = uvicorn.Config(
        app=api_app,
        host="0.0.0.0",
        port=8080,
        log_level="debug",
        loop="asyncio",
    )
    server = uvicorn.Server(config)
    try: 
        server.run()

    except (KeyboardInterrupt, asyncio.CancelledError) as e:
        logger.info("Manually shutting down server due to KeyboardInterrupt...")
        pass




if __name__ == "__main__":
    main()