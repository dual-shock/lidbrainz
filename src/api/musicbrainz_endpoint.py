import asyncio 
import time
import httpx
from collections import deque
from src.config import Config
from src.logger import logger
class RateLimit:
    max_requests = 4
    time_window = 5.0 

    def __init__(self):
        self.request_times = deque(maxlen=self.max_requests)
    
    async def wait(self) -> None: 
        curr_time = time.monotonic()
        
        if len(self.request_times) >= self.max_requests:
            oldest_time = self.request_times[0]
            time_since_oldest = curr_time - oldest_time
            
            if time_since_oldest < self.time_window:
                wait_time = self.time_window - time_since_oldest
                logger.warning(f"rate limit hit on musicbrainz requests", extra={"frontend": True})
                await asyncio.sleep(wait_time)
                curr_time = time.monotonic()

        self.request_times.append(curr_time)

class MusicBrainzClient:
    RETRIES = 10
    rate_limit = RateLimit()

    def __init__(self):
        self.client: httpx.AsyncClient | None = None
    
    async def get_client(self) -> httpx.AsyncClient:
        logger.info("getting MusicBrainz httpx AsyncClient")

        if not self.client or self.client.is_closed:
            logger.info(f" user agent is {Config.MUSICBRAINZ_USERAGENT}")
            self.client = httpx.AsyncClient(
                base_url="https://musicbrainz.org/ws/2",
                headers={
                    "User-Agent": Config.MUSICBRAINZ_USERAGENT or "",
                    "Accept": "application/json"
                },
                timeout=httpx.Timeout(
                    connect=10.0, #init connection
                    write=10.0,  #request send
                    read=30.0, #request answer
                    pool=10.0   #connection from pool
                ),
                limits=httpx.Limits(
                    max_connections=1,
                    max_keepalive_connections=1,
                    keepalive_expiry=60.0
                ),
                http2=True #saw mb supported it ans given it all seems to struggle i figure its better
            )

        return self.client
    

    async def close_client(self) -> None:
        if self.client is not None:
            try:
                await self.client.aclose()

            except Exception:
                pass  

            self.client = None


    async def request_with_retries(self, endpoint: str, params: dict, retry: bool = True) -> dict: #TODO turning retry on and off to be implemented
        logger.info(f"requesting MusicBrainz")
        attempt = 0

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
                return response.json()
            
            except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout) as exc:
                delay = 2.0 + (attempt * 0.5)

                if attempt < self.RETRIES:
                    logger.warning(f"Network error on attempt {attempt} Retrying in {delay:.2f} seconds...")
                    logger.warning(f"Error details: {type(exc).__name__}: {exc}")

                await self.close_client()
                await asyncio.sleep(delay)

            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code

                if status == 503:  
                    logger.warning(f"MusicBrainz returned 503 (overloaded), retrying...")
                    logger.warning(f"Response text: {exc.response.text[:200]}")
                    await asyncio.sleep(3.0) #shrugs
                    continue

                if status == 403: 
                    logger.error(f"MusicBrainz forbid your request, this is likely because of missing/invalid User-Agent header", extra={"frontend": True})
                    logger.error(f"Response text: {exc.response.text}")
                    break
                    
                if status == 429:  
                    logger.warning(f"Rate limited by server (429), waiting 10s...")
                    logger.warning(f"Response text: {exc.response.text[:200]}")
                    await asyncio.sleep(6) #? this is just a fallback if the rate limit class is a little zesty 
                    continue
                
                logger.error(f"HTTP {status}: {exc.response.text[:200]}")

        logger.error("exceeded maximum retries for MusicBrainz request without getting valid response")
        logger.error("failed to get valid response from MusicBrainz after retries", extra={"frontend": True})
        return {
            "error": "Failed to get valid response from MusicBrainz after retries",
            "status": "failed"
        }
        

    async def get_release_groups(self, query: str, limit: int = 5) -> dict:
        params = {
            "query": query,
            "fmt": "json",
            "limit": limit
        }
        return await self.request_with_retries("release-group/", params)


    async def get_releases(self, release_group_id: str) -> dict:
        logger.info("getting specific releases from musicbrainz", extra={"frontend": True})
        params = {
            "inc": "releases+media",
            "fmt": "json"
        }
        return await self.request_with_retries(f"release-group/{release_group_id}", params)                 
    

    async def fully_search(self, query: str, limit: int = 5) -> dict:
        logger.info(f"searching musicbrainz...", extra={"frontend": True})
        params = {
            "query": query,
            "fmt": "json",
            "limit": limit
        }
        release_groups =  await self.request_with_retries("release-group/", params)

        if not release_groups["release-groups"]:
            logger.info(f"no release groups found for query: ({query})", extra={"frontend": True})
            return {}
        
        logger.info(f"release groups parsed", extra={"frontend": True})
        first_release_group = release_groups["release-groups"][0] 
        first_release_group_releases = await self.get_releases(first_release_group["id"])
        return {
            "release-groups": release_groups["release-groups"],
            "best-match-releases": first_release_group_releases["releases"]
        }
        

    







