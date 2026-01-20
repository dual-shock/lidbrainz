import os
from dotenv import load_dotenv
from src.logger import logger

load_dotenv()
class Config: 
    LIDARR_URL = os.getenv("LIDARR_URL")
    LIDARR_APIKEY = os.getenv("LIDARR_APIKEY")
    MUSICBRAINZ_USERAGENT = os.getenv("MUSICBRAINZ_USERAGENT")

    @classmethod
    def exists(cls, env_var: str):
        value = os.getenv(env_var)
        
        if not value: 
            logger.error(f"{env_var} not set either in .env config file or environment")
        
        return value

    @classmethod
    def check(cls):
        if not cls.LIDARR_URL:
            logger.error("LIDARR_URL not found in environment", extra={"frontend": True})
        
        else: logger.info(f"LIDARR_URL found: {cls.LIDARR_URL[:4]}****")
        
        if not cls.LIDARR_APIKEY:
            logger.error("LIDARR_APIKEY not found in environment", extra={"frontend": True})
        
        else: logger.info(f"LIDARR_APIKEY found: {cls.LIDARR_APIKEY[:4]}****")
        
        if not cls.MUSICBRAINZ_USERAGENT:
            logger.error("MUSICBRAINZ_USERAGENT not found in environment", extra={"frontend": True})
        
        else: logger.info(f"MUSICBRAINZ_USERAGENT found: {cls.MUSICBRAINZ_USERAGENT[:4]}****")




