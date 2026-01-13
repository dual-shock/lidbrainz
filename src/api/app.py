from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.routes import search_musicbrainz, add_to_lidarr, interface_logs
from pathlib import Path

def start() -> FastAPI:
    print("INFO: Starting API server")
    app = FastAPI(title="LidBrainz", summary="Search MusicBrainz, add to Lidarr")

    

    print("INFO: adding routers")
    app.include_router(search_musicbrainz.router, prefix="/lidbrainz/search_musicbrainz", tags=["search_musicbrainz"])
    app.include_router(add_to_lidarr.router, prefix="/lidbrainz/add_to_lidarr", tags=["add_to_lidarr"])
    app.include_router(interface_logs.router, prefix="/lidbrainz/interface_logs", tags=["interface_logs"])


    print("INFO: mounting static interface files")
    interface_path = Path(__file__).parent.parent.parent / "interface"
    app.mount("/", StaticFiles(directory=interface_path, html=True), name="interface")

    print("INFO: adding root endpoint to serve index.html")
    @app.get("/")
    async def serve_index():
        return FileResponse(interface_path / "index.html")

    
    print("INFO: API server started")
    return app