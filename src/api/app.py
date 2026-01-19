from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio

from src.routes import search_musicbrainz, add_to_lidarr, interface_logs
from src.logger import logger, cleanup_logging
from pathlib import Path

from src.api.lidarr_endpoint import LidarrClient
from src.api.musicbrainz_endpoint import MusicBrainzClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.lidarr_client = LidarrClient()
    app.state.musicbrainz_client = MusicBrainzClient()
    yield
    logger.info("Shutting down API server...")
    await app.state.lidarr_client.close_client()
    await app.state.musicbrainz_client.close_client()
    cleanup_logging()


def start() -> FastAPI:
    logger.info("Starting API server")
    app = FastAPI(
        title="LidBrainz", 
        summary="Search MusicBrainz, add to Lidarr",
        lifespan=lifespan
    )

    

    logger.info("adding routers")
    app.include_router(interface_logs.router, prefix="/lidbrainz/interface_logs", tags=["interface_logs"])
    app.include_router(search_musicbrainz.router, prefix="/lidbrainz/search_musicbrainz", tags=["search_musicbrainz"])
    app.include_router(add_to_lidarr.router, prefix="/lidbrainz/add_to_lidarr", tags=["add_to_lidarr"])



    logger.info("mounting static interface files")
    interface_path = Path(__file__).parent.parent.parent / "interface"
    app.mount("/", StaticFiles(directory=interface_path, html=True), name="interface")

    logger.info("adding root endpoint to serve index.html")
    @app.get("/")
    async def serve_index():
        return FileResponse(interface_path / "index.html")



    
    logger.info("API server started")
    return app