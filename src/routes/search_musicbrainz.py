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
        logger.error(f"ERROR: Exception in /fully_search endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching MusicBrainz: {e}")
    

