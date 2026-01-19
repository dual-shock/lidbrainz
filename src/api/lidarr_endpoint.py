import httpx
import asyncio
import traceback
from src.config import Config
from src.logger import logger

#? You test this whole program by running "python -m src.api.lidarr_endpoint"
#? you search, and then pick a release group id to add to lidarr

TEST_SEARCH : bool = False

#TODO check if check artist and check release-group can return a value
#TODO that is not an empty dict but also not an artist, as this could
#TODO lead to false positive in the fully add search method flow

#TODO handle the case of an artist being present without their release group
#? i think i fixed this, who knows

#TODO create option for not auto downloading or monitoring in full add
#TODO   create interactive search function


class LidarrClient:

    def __init__(self):

        self.client: httpx.AsyncClient | None = None
    
    async def get_client(self) -> httpx.AsyncClient:
        logger.info("getting lidarr httpx AsyncClient")
        if not self.client or self.client.is_closed:
            if not Config.LIDARR_URL:
                logger.error("LIDARR_URL is not configured", extra={"frontend": True})
                raise ValueError("LIDARR_URL or LIDARR_APIKEY is not configured")
            if not Config.LIDARR_APIKEY:
                logger.error("LIDARR_APIKEY is not configured", extra={"frontend": True})
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


        return self.client
    

    async def close_client(self) -> None:
        logger.info("closing lidarr httpx AsyncClient")
        if self.client is not None:
            try:
                await self.client.aclose()
            except Exception:
                pass  
            self.client = None
        
    async def get_system_info(self) -> dict:
        logger.info("fetching system info from lidarr", extra={"frontend": True})
        # logger.warning("fetching system info from lidarr Warning Test", extra={"frontend": True})
        # logger.error("fetching system info from lidarr Error Test", extra={"frontend": True})
        try: 

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


            metadata_profiles = await client.get(
                url="/api/v1/metadataprofile",
                params={

                }
            )
            metadata_profiles.raise_for_status()

            system_info = {
                "root_folders": root_folders.json(),
                "quality_profiles": quality_profiles.json(),
                "metadata_profiles": metadata_profiles.json(),
                "lidarr_url": Config.LIDARR_URL
            }
            return system_info
        except Exception as e:
            logger.error(f"ERROR: failed to get system info from Lidarr, more info in logs", extra={"frontend": True})
            logger.error(traceback.format_exc())
            return {}
    

    #! #################################################################
    #! this SHOULDNT have to be used, in theory, so not made yet
    async def lookup_release_info(self,release_group_mbid: str) -> dict:
        logger.info("looking up release info from lidarr")
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
            logger.error(f"ERROR: failed to lookup release info from Lidarr: {e}")
            return {}
    #! #################################################################
    #! #################################################################
    
    async def check_artist_in_library(self, artist_mbid: str) -> dict:
        logger.info("checking artist in lidarr library")
        try:
            logger.info(f"INFO: checking if artist with mbid: {artist_mbid} exists in Lidarr library")
            logger.info(f"checking if artist with mbid: {artist_mbid} exists in Lidarr library")
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
            logger.error(f"failed to check if artist in lidarr library", extra={"frontend": True})
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
        logger.info("adding artist to lidarr library")
        try:
            logger.info(f"INFO: adding artist to Lidarr library with mbid: {artist_mbid}")
            client = await self.get_client()
            payload = {
                "foreignArtistId": artist_mbid,
                "rootFolderPath": root_folder_path,
                "artistName": artist_name,
                "qualityProfileId": quality_profile_id,
                "metadataProfileId": metadata_profile_id,
                "monitored": True,
                "addOptions": {
                    "createArtistFolder": True ,
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
            logger.error(f"failed to add artist to lidarr library", extra={"frontend": True})
            return {}



    async def check_release_group_in_library(self, release_group_mbid: str) -> dict:
        logger.info("checking release group in lidarr library")
        try: 
            logger.info(f"INFO: checking if release group with mbid: {release_group_mbid} exists in Lidarr library")
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
            logger.error(f"failed to check if release group in lidarr library", extra={"frontend": True})
            return {}




    #! #################################################################
    #! this SHOULDNT have to be used, in theory, so not made yet    
    async def add_release_group_to_library(self,) -> dict:
        logger.info("adding release group to lidarr library - FUNCTION NOT IMPLEMENTED YET")
        try: 
            client = await self.get_client()
            

            return {}
        except Exception as e:
            logger.error(f"failed to add release group to lidarr library", extra={"frontend": True})
            return {}
    #! #################################################################
    #! #################################################################

    async def set_monitor_release_group(self, release_group_lrid: int, monitored: bool = True) -> dict:
        logger.info("setting monitor for release group in lidarr")
        try: 
            logger.info(f"INFO: setting monitor={monitored} for release group in Lidarr with id: {release_group_lrid}")
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
            logger.error(f"failed to set monitor for release group in lidarr", extra={"frontend": True})
            return {}
        
    async def set_release_in_release_group(self, release_group_data: dict, release_mbid: str) -> dict:
        logger.info("setting specific release in release group in lidarr")
        # release_group_data here is expected to be a return of get/album on lidarr api
        # id make an object for all this, cba
        try:
            logger.info(f"INFO: setting release with mbid: {release_mbid} in release group in Lidarr")
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
            logger.error(f"failed to set release in release group in lidarr", extra={"frontend": True})
            return {}

    async def trigger_search_for_release_group(self, release_group_lrid: int) -> dict:
        logger.info("triggering search for release group in lidarr")
        try:
            logger.info(f"INFO: triggering search for release group in Lidarr with id: {release_group_lrid}")
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
            logger.error(f"failed to trigger search for release group in lidarr", extra={"frontend": True})
            return {}

    #! #################################################################
    #! currently unused cause it doesnt work, the auto post-grab not respected
   
    async def refresh_release_group_metadata(self, release_group_lrid: int, max_wait: float = 30.0, poll_interval: float = 0.3) -> dict:
        logger.info("triggering release-group metadata refresh to affirm metadata presence before triggering download")
        try:
            client = await self.get_client()
            payload = {
                "name": "RefreshAlbum",
                "albumIds": [
                    release_group_lrid
                ]
            }
            
            command_response = await client.post(
                url="/api/v1/command",
                json=payload,
            )
            
            command_response.raise_for_status()
            command_response = command_response.json()
            command_id = command_response.get("id")


            logger.info(f"INFO: waiting for metadata refresh command with id: {command_id} to complete")
            if command_id:
                elapsed = 0.0

                while elapsed < max_wait:
                    command_status = await client.get(
                        url=f"/api/v1/command/{command_id}",
                        params={
                            
                        }
                    )
                    command_status.raise_for_status()
                    command_status = command_status.json()
                    status = command_status.get("status")
                    if status == "completed":
                        logger.info(f"INFO: metadata refresh command with id: {command_id} completed")
                        return command_status
                    if status == "failed":
                        logger.error(f"ERROR: metadata refresh command with id: {command_id} failed")
                        return {}
                    logger.info(f"INFO: metadata refresh command with id: {command_id} status: {status}, waiting...")
                    await asyncio.sleep(poll_interval)
                    elapsed += poll_interval
            logger.error(f"ERROR: metadata refresh command with id: {command_id} did not complete in time")
            return {}


        except Exception as e:
            logger.error(f"failed to trigger metadata refresh in lidarr", extra={"frontend": True})
            return {}
        
    #! #################################################################
    #! #################################################################

    async def refresh_artist_metadata(self, artist_lrid: int, max_wait: float = 30.0, poll_interval: float = 0.3) -> dict:
        logger.info("triggering artist metadata refresh to affirm metadata presence before triggering download")
        try:
            logger.info(f"INFO: triggering artist metadata refresh to affirm metadata presence before triggering download")
            client = await self.get_client()
            payload = {
                "name": "RefreshArtist",
                "artistIds": [
                    artist_lrid
                ]
            }
            
            command_response = await client.post(
                url="/api/v1/command",
                json=payload,
            )
            
            command_response.raise_for_status()
            command_response = command_response.json()
            command_id = command_response.get("id")


            logger.info(f"INFO: waiting for metadata refresh command with id: {command_id} to complete")
            if command_id:
                elapsed = 0.0

                while elapsed < max_wait:
                    command_status = await client.get(
                        url=f"/api/v1/command/{command_id}",
                        params={
                            
                        }
                    )
                    command_status.raise_for_status()
                    command_status = command_status.json()
                    status = command_status.get("status")
                    if status == "completed":
                        logger.info(f"INFO: metadata refresh command with id: {command_id} completed")
                        return command_status
                    if status == "failed":
                        logger.error(f"failed to trigger metadata refresh in lidarr", extra={"frontend": True})
                        return {}
                    logger.info(f"INFO: metadata refresh command with id: {command_id} status: {status}, waiting...")
                    await asyncio.sleep(poll_interval)
                    elapsed += poll_interval
            logger.error(f"failed to trigger metadata refresh in lidarr", extra={"frontend": True})
            return {}


        except Exception as e:
            logger.error(f"failed to trigger metadata refresh in lidarr", extra={"frontend": True})
            return {}
    
    async def fully_add_release(
        self,
        release_group_mbid: str,
        artist_mbid: str,
        auto_download: bool = True,
        quality_profile_id: int = 1,  #default profile, if not 1 its specified
        metadata_profile_id: int = 1, #default profile, if not 1 its specified
        root_folder_path: str | None = None, #default, gets picked from system info if None
        query: str | None = None, #for ui l8r mby 
        artist_name: str = "artistName", #not needed, can be handy if i find out it needed lol
        release_mbid: str | None = None, #optional, if specified it gets picked if not its default
        monitor_artist: bool = True, #optional, if specified it sets the artist to monitored
    ) -> dict:
        logger.info("fully adding release to lidarr")
        logger.info(f"attempting to add release to lidarr", extra={"frontend": True})
        try:


            # ? system info gets called on page load, but if a folder is not picked
            # ? we call system info to get the default root folder
            if not root_folder_path:

                system_info = await self.get_system_info()
                
                root_folder_path = system_info["root_folders"][0]["path"]
            
            logger.info(f"INFO: checking if artist with mbid: {artist_mbid}, name {artist_name} exists in Lidarr library")
            artist = await self.check_artist_in_library(artist_mbid)
            if not artist: 

                artist = await self.add_artist_to_library(
                    artist_mbid=artist_mbid,
                    release_group_mbid=release_group_mbid,
                    root_folder_path=root_folder_path, # type: ignore  this will be str for suuuure
                    artist_name=artist_name,
                    quality_profile_id=quality_profile_id,
                    metadata_profile_id=metadata_profile_id,
                    monitored=monitor_artist
                )
                
                release_group = await self.check_release_group_in_library(release_group_mbid)
            else:
                logger.info(f"INFO: artist was already added")
                logger.info(f"artist already found in library, not adding artist")
                release_group = await self.check_release_group_in_library(release_group_mbid)

            if isinstance(artist, list): 
                artist = artist[0]
                        
            if not release_group:
                logger.info(f"INFO: release group not found in library yet, forcing artist metadata refresh to affirm release group presence")
                await self.refresh_artist_metadata(
                    artist_lrid=artist["id"]
                )

            release_group = await self.check_release_group_in_library(release_group_mbid)

            if not release_group:
                logger.warning(
f"""Release group with mbid: {release_group_mbid} still not found in Lidarr
library after adding artist and refreshing metadata, this is likely because 
your METADATA PROFILE doesnt find this release. 
Either try a less strict metadata profile or add release manually.""", 
                    extra={"frontend": True}
                )
                print(
f"""ERROR: release group with mbid: {release_group_mbid} still not found in Lidarr
library after artist add and metadata refresh, this is likely because 
YOUR METADATA PROFILE BLOCKS THIS RELEASE / DOESNT FIND IT. 
Either try a less strict metadata profile or add release manually."""
                )
                #respond with internal server error to the route 
                raise Exception("Release group not found in Lidarr after artist add and metadata refresh")

                return {}    

            if isinstance(release_group, list): 
                release_group = release_group[0]
            
            monitored_release_group = await self.set_monitor_release_group(
                release_group_lrid=release_group['id'],
                monitored=True
            )
            

            if release_mbid:
                logger.info(f"INFO specific release has been specified")
                monitored_release_group = await self.set_release_in_release_group(
                    release_group_data=monitored_release_group,
                    release_mbid=release_mbid
                )

            if auto_download:
                logger.info(f"Auto download is true, triggering automatic search for release", extra={"frontend": True})


                await self.refresh_artist_metadata(
                    artist_lrid=artist["id"]
                )
                await asyncio.sleep(1.0)
                logger.info(f"INFO: triggering search for release group to start download")
                await self.trigger_search_for_release_group(
                    release_group_lrid=release_group['id']
                )

            return monitored_release_group
        except Exception as e:
            logger.error(f"ERROR: failed to fully add release to Lidarr: {e}")
            logger.error(f"ERROR: Error is coming from: {traceback.format_exc()}")
            logger.error(f"failed to fully add release to lidarr, more info in logs", extra={"frontend": True})
            return {}







import asyncio

async def test():

    from src.api.musicbrainz_endpoint import MusicBrainzClient

    #python -m src.api.lidarr_endpoint

    test_query = input("Enter search query for MusicBrainz release-group search: ").strip()

    lidarr_client = LidarrClient()
    mb_client = MusicBrainzClient()

    system_info = await lidarr_client.get_system_info()
    with open("lidarr_system_info_debug.json","w",encoding="utf-8") as f:
        import json
        json.dump(system_info,f,indent=4)

    full_search = await mb_client.fully_search(test_query)
    import json
    with open("full_search_debug.json","w",encoding="utf-8") as f:
        json.dump(full_search,f,indent=4)

    is_first = True

    for release_group in full_search["release-groups"]:

        logger.info(f"INFO: found release-group with title: {release_group['title']}, id: {release_group['id']}, score: {release_group['score']}, artist: {release_group['artist-credit'][0]['artist']['name']}")
        if is_first:
            logger.info(f"INFO: found releases for first release-group:")
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
    pass

    