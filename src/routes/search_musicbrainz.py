from src.api.musicbrainz_endpoint import MusicBrainzClient
from fastapi import APIRouter, HTTPException, Query, Request
from src.logger import logger

router = APIRouter()

@router.get("/fully_search")
async def fully_search(
    request: Request,
    query: str, 
    limit: int = 5
):
    try:
        mb_client = request.app.state.musicbrainz_client
        search_result = await mb_client.fully_search(query, limit)
        return search_result
    
    except Exception as e:
        logger.error(f"Exception in /fully_search endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching MusicBrainz: {e}")


@router.get("/releases")
async def get_releases(
    request: Request,
    release_group_mbid: str
):
    try:
        mb_client = request.app.state.musicbrainz_client
        releases = await mb_client.get_releases(release_group_mbid)
        return {"id": release_group_mbid, "releases": releases["releases"]}
    
    except Exception as e:
        logger.error(f"Exception in /releases endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving releases from MusicBrainz: {e}")

