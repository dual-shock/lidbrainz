from src.api.musicbrainz_endpoint import MusicBrainzClient
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

mb_client = MusicBrainzClient()

@router.get("/fully_search")
async def fully_search(
    query: str, 
    limit: int = 5
):
    print("INFO: running fully_search from fastAPI server")
    try:
        search_result = await mb_client.fully_search(query, limit)
        return search_result
    except Exception as e:
        print(f"ERROR: Exception in /fully_search endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching MusicBrainz: {e}")
    

