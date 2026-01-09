from src.api.lidarr_endpoint import LidarrClient
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

lidarr_client = LidarrClient()

@router.get("/fully_add_release")
async def fully_add_release(
    release_group_mbid: str,
    artist_mbid: str,
    auto_download: bool = True,
    quality_profile_id: int = 1,  #default profile, if not 1 its specified
    metadata_profile_id: int = 1, #default profile, if not 1 its specified
    root_folder_path: str | None = None, #default, gets picked from system info if None
    query: str | None = None, #for ui
    artist_name: str = "artistName", #not needed, can be handy if i find out it needed lol
    release_mbid: str | None = None, #optional, if specified it gets picked if not its default
    monitor_artist: bool = True, #optional, if specified it sets the artist to monitored
):
    print("INFO: running fully_add_release from fastAPI server")
    try:
        result = await lidarr_client.fully_add_release(
            release_group_mbid,
            artist_mbid,
            auto_download,
            quality_profile_id,
            metadata_profile_id,
            root_folder_path,
            query,
            artist_name,
            release_mbid,
            monitor_artist
        )
        return result
    except Exception as e:
        print(f"ERROR: Exception in /fully_add_release: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding release to Lidarr: {e}")
    

@router.get("/system_info")
async def system_info():
    print("INFO: running system_info from fastAPI server")
    try:
        system_info = await lidarr_client.get_system_info()
        return system_info
    except Exception as e:
        print(f"ERROR: Exception in /system_info endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving Lidarr system info: {e}")

