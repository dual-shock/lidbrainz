import asyncio 
import time
import httpx
from src.config import Config

class RateLimit:
    interval = 1.75

    def __init__(self):
        self.last_req_time: float = 0.0
    
    async def wait(self) -> None: 
        print("INFO: checking if musicbrainz rate limit wait needed")
        curr_time = time.monotonic()
        elapsed_time = curr_time - self.last_req_time

        if elapsed_time < self.interval:
            wait_time = self.interval - elapsed_time
            print(f"INFO: waiting {wait_time:.2f}s to respect musicbrainz rate limit . . .")
            await asyncio.sleep(wait_time)
        self.last_req_time = time.monotonic()


class MusicBrainzClient:
    RETRIES = 10
    rate_limit = RateLimit()

    def __init__(self):
        print("INFO: initializing httpx AsyncClient for MusicBrainz")
        self.client: httpx.AsyncClient | None = None
    
    async def get_client(self) -> httpx.AsyncClient:
        if not self.client or self.client.is_closed:
            print("INFO: Musicbrainz httpx AsyncClient is None or closed, creating new one")
            print(f"INFO: user agent is {Config.MUSICBRAINZ_AGENT}")
            self.client = httpx.AsyncClient(
                base_url="https://musicbrainz.org/ws/2",
                headers={
                    "User-Agent": Config.MUSICBRAINZ_AGENT,
                    "Accept": "application/json"
                },
                timeout=httpx.Timeout(
                    connect=10.0, #init connection
                    write=10.0,  #request send
                    read=30.0, #request answer
                    pool=10.0   #connection from pool, TODO wth is a pool and why do i need it
                ),
                limits=httpx.Limits(
                    max_connections=1,
                    max_keepalive_connections=1,
                    keepalive_expiry=60.0
                ),
                http2=True #saw mb supported it ans given it all seems to struggle i figure its better
            )
            print("INFO: created new httpx AsyncClient for MusicBrainz")

        return self.client
    
    async def close_client(self) -> None:
        print("INFO: closing MusicBrainz httpx AsyncClient")
        if self.client is not None:
            try:
                await self.client.aclose()
            except Exception:
                pass  
            self.client = None

    async def request_with_retries(self, endpoint: str, params: dict, retry: bool = True) -> dict: #turning retry on and off to be implemented
        attempt = 0
        print(f"INFO: requesting MusicBrainz endpoint {endpoint} with params {params}")
        while attempt < self.RETRIES:
            attempt += 1
            try:
                await self.rate_limit.wait()
                client = await self.get_client()
                response = await client.get(
                    endpoint,
                    params=params
                )
                response.raise_for_status()

                print(f"INFO: received response on attempt {attempt} with status code {response.status_code}")
                return response.json()
            except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout) as exc:
                delay = self.rate_limit.interval + (self.rate_limit.interval * attempt / 2) 
                if attempt < self.RETRIES:
                    print(f"WARNING: Network error on attempt {attempt} Retrying in {delay:.2f} seconds...")
                    print(f"WARNING: Error details: {type(exc).__name__}: {exc}")
                await self.close_client()
                await asyncio.sleep(delay)
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if status == 503:  
                    print(f"WARN: MusicBrainz returned 503 (overloaded), retrying...")
                    print(f"WARN: Response text: {exc.response.text[:200]}")
                    await asyncio.sleep(self.rate_limit.interval * 2)
                    continue
                    
                if status == 429:  
                    print(f"WARN: Rate limited by server (429), waiting 10s...")
                    print(f"WARN: Response text: {exc.response.text[:200]}")
                    await asyncio.sleep(6) # u can make X requests per 5 seconds, i saw in a forum, xP
                    continue
                
                print(f"ERROR: HTTP {status}: {exc.response.text[:200]}")
        print("ERROR: exceeded maximum retries for MusicBrainz request without getting valid response")
        return {
            "error": "Failed to get valid response from MusicBrainz after retries",
            "status": "failed"
        }
        

    async def get_release_groups(self, query: str, limit: int = 5) -> dict:
        print(f"INFO: searching MusicBrainz release-groups with query: {query}")
        params = {
            "query": query,
            "fmt": "json",
            "limit": limit
        }
        return await self.request_with_retries("release-group/", params)

    async def get_releases(self, release_group_id: str) -> dict:
        print(f"INFO: getting MusicBrainz releases for release-group id: {release_group_id}")
        params = {
            "inc": "releases",
            "fmt": "json"
        }
        return await self.request_with_retries(f"release-group/{release_group_id}", params)                 
    
    async def fully_search(self, query: str, limit: int = 5) -> dict:
        print(f"INFO: performing fully_search on MusicBrainz with query: {query}")
        params = {
            "query": query,
            "fmt": "json",
            "limit": limit
        }
        release_groups =  await self.request_with_retries("release-group/", params)
        if not release_groups["release-groups"]:
            print(f"INFO: no release-groups found in fully_search with query: {query}")
            return {}
    
        first_release_group = release_groups["release-groups"][0] 

        first_release_group_releases = await self.get_releases(first_release_group["id"])
        return {
            "release-groups": release_groups["release-groups"],
            "best-match-releases": first_release_group_releases["releases"]
        }
        

    







