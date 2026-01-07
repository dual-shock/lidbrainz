import httpx
from src.config import Config

#? You test this whole program by running "python -m src.api.lidarr_endpoint"
#? you search, and then pick a release group id to add to lidarr

TEST_SEARCH : bool = True

#TODO check if check artist and check release-group can return a value
#TODO that is not an empty dict but also not an artist, as this could
#TODO lead to false positive in the fully add search method flow

#TODO handle the case of an artist being present without their release group

#TODO create option for not auto downloading or monitoring in full add
#TODO   create interactive search function

class LidarrClient:

    def __init__(self):
        print("INFO: initializing httpx AsyncClient for Lidarr")
        self.client: httpx.AsyncClient | None = None
    
    async def get_client(self) -> httpx.AsyncClient:
        if not self.client or self.client.is_closed:
            print("INFO: Lidarr httpx AsyncClient is None or closed, creating new one")

            if not Config.LIDARR_URL or not Config.LIDARR_APIKEY:
                raise ValueError("LIDARR_URL or LIDARR_APIKEY is not configured")

            self.client = httpx.AsyncClient(
                base_url=Config.LIDARR_URL.rstrip("/"),
                headers={
                    "X-Api-Key": Config.LIDARR_APIKEY,
                    "Content-Type": "application/json"
                },
                timeout=30.0,
                http2=True 
            )
            print("INFO: created new httpx AsyncClient for Lidarr")

        return self.client
    

    async def close_client(self) -> None:
        print("INFO: closing Lidarr httpx AsyncClient")
        if self.client is not None:
            try:
                await self.client.aclose()
            except Exception:
                pass  
            self.client = None
        
    async def get_system_info(self) -> dict:
        try: 
            print("INFO: fetching system info from Lidarr")
            client = await self.get_client()
            root_folders = await client.get(
                url="/api/v1/rootfolder",
                params={

                }
            )
            root_folders.raise_for_status()
            quality_profiles = await client.get(
                url="/api/v1/qualityprofile",
                params={

                }
            )

            quality_profiles.raise_for_status()
            system_info = {
                "root_folders": root_folders.json(),
                "quality_profiles": quality_profiles.json()
            }
            return system_info
        except Exception as e:
            print(f"ERROR: failed to get system info from Lidarr: {e}")
            return {}
    

    #! #################################################################
    #! this SHOULDNT have to be used, in theory, so not made yet
    async def lookup_release_info(self,release_group_mbid: str) -> dict:
        try: 
            client = await self.get_client()
            lookup = await client.get(
                url="/api/v1/album/lookup",
                params={
                    "term":f"mbid:{release_group_mbid}"
                }
            )
            lookup.raise_for_status()
            return lookup.json()
        except Exception as e:
            print(f"ERROR: failed to lookup release info from Lidarr: {e}")
            return {}
    #! #################################################################
    #! #################################################################
    
    async def check_artist_in_library(self, artist_mbid: str) -> dict:
        try:
            print(f"INFO: checking if artist with mbid: {artist_mbid} exists in Lidarr library")
            client = await self.get_client()
            artist = await client.get(
                url="/api/v1/artist",
                params={
                    "mbid": artist_mbid
                }
            )
            artist.raise_for_status()
            return artist.json()


        except Exception as e:
            print(f"ERROR: failed to check artist in library from Lidarr: {e}")
            return {}

    async def add_artist_to_library(
        self, 
        artist_mbid: str,
        release_group_mbid: str,
        root_folder_path: str,
        artist_name: str = "artistName",
        quality_profile_id: int = 1,
        metadata_profile_id: int = 1,
        monitored: bool | None = None
    ) -> dict:
        try:
            print(f"INFO: adding artist to Lidarr library with mbid: {artist_mbid}")
            client = await self.get_client()
            payload = {
                "foreignArtistId": artist_mbid,
                "rootFolderPath": root_folder_path,
                "artistName": artist_name,
                "qualityProfileId": quality_profile_id,
                "metadataProfileId": metadata_profile_id,
                "monitored": True,
                "addOptions": {
                    "searchForMissingAlbums": False,
                    "monitor": "none",
                    "albumsToMonitor":[
                        release_group_mbid
                    ],
                    "monitored": True,
                }
            }
            if monitored is not None:
                payload["addOptions"]["monitored"] = monitored
                payload["monitored"] = monitored
            added_artist = await client.post(
                url="/api/v1/artist",
                json=payload,
            )
            added_artist.raise_for_status()
            added_artist = added_artist.json()
            return added_artist
        except Exception as e:
            print(f"ERROR: failed to add artist to library in Lidarr: {e}")
            return {}



    async def check_release_group_in_library(self, release_group_mbid: str) -> dict:
        try: 
            print(f"INFO: checking if release group with mbid: {release_group_mbid} exists in Lidarr library")
            client = await self.get_client()
            release_group = await client.get(
                url="/api/v1/album",
                params={
                    "foreignAlbumId": release_group_mbid
                }
            )
            release_group.raise_for_status()
            return release_group.json()
        except Exception as e:
            print(f"ERROR: failed to check if album in Lidarr library: {e}")
            return {}




    #! #################################################################
    #! this SHOULDNT have to be used, in theory, so not made yet    
    async def add_release_group_to_library(self,) -> dict:
        try: 
            client = await self.get_client()
            # Implement the actual add logic here
            print("INFO: adding release group to Lidarr library - FUNCTION NOT IMPLEMENTED YET")
            return {}
        except Exception as e:
            print(f"ERROR: failed to check if album in Lidarr library: {e}")
            return {}
    #! #################################################################
    #! #################################################################

    async def set_monitor_release_group(self, release_group_lrid: int, monitored: bool = True) -> dict:
        try: 
            print(f"INFO: setting monitor={monitored} for release group in Lidarr with id: {release_group_lrid}")
            client = await self.get_client()
            payload = {
                "albumIds": [
                    release_group_lrid
                ],
                "monitored": monitored
            }
            updated_release_group = await client.put(
                url=f"/api/v1/album/monitor",
                json=payload,
            )
            updated_release_group.raise_for_status()
            updated_release_group = updated_release_group.json()
            return updated_release_group
        except Exception as e:
            print(f"ERROR: failed to set monitor for release group in Lidarr: {e}")
            return {}
        
    async def set_release_in_release_group(self, release_group_data: dict, release_mbid: str) -> dict:
        # release_group_data here is expected to be a return of get/album on lidarr api
        try:
            print(f"INFO: setting release with mbid: {release_mbid} in release group in Lidarr")
            client = await self.get_client()

            if isinstance(release_group_data, list): 
                release_group_data = release_group_data[0]
            
            for release in release_group_data.get("releases", []):
                release["monitored"] = (release["foreignReleaseId"] == release_mbid)
            
            updated_release_group = await client.put(
                url=f"/api/v1/album/{release_group_data['id']}",
                json=release_group_data
            )
            updated_release_group.raise_for_status()
            updated_release_group = updated_release_group.json()

            return updated_release_group    
        except Exception as e:
            print(f"ERROR: failed to set release in release group in Lidarr: {e}")
            return {}

    async def trigger_search_for_release_group(self, release_group_lrid: int) -> dict:
        try:
            print(f"INFO: triggering search for release group in Lidarr with id: {release_group_lrid}")
            client = await self.get_client()
            payload = {
                "name": "AlbumSearch",
                "albumIds": [
                    release_group_lrid
                ]
            }
            
            command_status = await client.post(
                url="/api/v1/command",
                json=payload,
            )
            
            command_status.raise_for_status()
            command_status = command_status.json()
            return command_status
        except Exception as e:
            print(f"ERROR: failed to trigger search for release group in Lidarr: {e}")
            return {}
    
    async def fully_add_release(
        self,
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
    ) -> dict:
        try:
            print("INFO: starting full add of release to Lidarr")

            # ? system info gets called on page load, but if a folder is not picked
            # ? we call system info to get the default root folder
            if not root_folder_path:
                print("INFO: no root folder path specified, fetching from Lidarr system info")
                system_info = await self.get_system_info()
                root_folder_path = system_info["root_folders"][0]["path"]
            
            print(f"INFO: checking if artist with mbid: {artist_mbid}, name {artist_name} exists in Lidarr library")
            artist = await self.check_artist_in_library(artist_mbid)
            if not artist: 
                print("INFO: artist not found in library")
                added_artist = await self.add_artist_to_library(
                    artist_mbid=artist_mbid,
                    release_group_mbid=release_group_mbid,
                    root_folder_path=root_folder_path, # type: ignore  this will be str
                    artist_name=artist_name,
                    quality_profile_id=quality_profile_id,
                    metadata_profile_id=metadata_profile_id,
                    monitored=monitor_artist
                )
                
                release_group = await self.check_release_group_in_library(release_group_mbid)
            else:
                print(f"INFO: artist was already added")
                release_group = await self.check_release_group_in_library(release_group_mbid)
                        
            if not release_group:
                print("ERROR: release group not found in library after artist addition, unexpected state")
                return {}

            if isinstance(release_group, list): 
                release_group = release_group[0]
            
            monitored_release_group = await self.set_monitor_release_group(
                release_group_lrid=release_group['id'],
                monitored=True
            )
            

            if release_mbid:
                print(f"INFO specific release has been specified")
                monitored_release_group = await self.set_release_in_release_group(
                    release_group_data=monitored_release_group,
                    release_mbid=release_mbid
                )

            if auto_download:
                print(f"INFO: Auto download is true")
                await self.trigger_search_for_release_group(
                    release_group_lrid=release_group['id']
                )

            return monitored_release_group
        except Exception as e:
            print(f"ERROR: failed to fully add release to Lidarr: {e}")
            return {}







import asyncio

async def test():

    from src.api.musicbrainz_endpoint import MusicBrainzClient

    #python -m src.api.lidarr_endpoint

    test_query = input("Enter search query for MusicBrainz release-group search: ").strip()

    lidarr_client = LidarrClient()
    mb_client = MusicBrainzClient()

    full_search = await mb_client.fully_search(test_query)

    is_first = True

    for release_group in full_search["release-groups"]:

        print(f"INFO: found release-group with title: {release_group['title']}, id: {release_group['id']}, score: {release_group['score']}, artist: {release_group['artist-credit'][0]['artist']['name']}")
        if is_first:
            print(f"INFO: found releases for first release-group:")
            for release in full_search["best-match-releases"]:
                print(f"\trelease title: {release['title']}, id: {release['id']}, date: {release.get('date', 'N/A')}, medium: {release.get('mediums', 'N/A')}")
            is_first = False

    user_input_release_group_mbid = input("Enter release-group MBID to add to Lidarr: ").strip()
    artist_mbid = ""
    for release_group in full_search["release-groups"]:
        if release_group["id"] == user_input_release_group_mbid:
            artist_mbid = release_group["artist-credit"][0]["artist"]["id"]
            break
    user_input_release_mbid = input("Optionally enter release MBID to specifically monitor (or press Enter to skip): ").strip()
    
    print(f"selected group:{user_input_release_group_mbid},\nselected artist:{artist_mbid},\nselected release:{user_input_release_mbid}")

    await lidarr_client.fully_add_release(
        release_group_mbid=user_input_release_group_mbid,
        artist_mbid=artist_mbid,
        release_mbid=user_input_release_mbid if user_input_release_mbid else None
    )

    await mb_client.close_client()
    await lidarr_client.close_client()

if TEST_SEARCH:
    asyncio.run(test())

    