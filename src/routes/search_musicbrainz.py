from src.api.musicbrainz_endpoint import MusicBrainzClient
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

mb_client = MusicBrainzClient()

@router.get("/release_groups")
async def release_groups(
    query: str, 
    limit: int = 5
):
    print("test")
    try:
        result = await mb_client.get_release_groups(query, limit)
        return result
    except Exception as e:
        print(f"ERROR: Exception in /release_groups endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching MusicBrainz: {e}")
    

