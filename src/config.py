import os
from dotenv import load_dotenv

load_dotenv()

class Config: 
    LIDARR_URL = os.getenv("LIDARR_URL")
    LIDARR_APIKEY = os.getenv("LIDARR_APIKEY")
    MUSICBRAINZ_USERAGENT = os.getenv("MUSICBRAINZ_USERAGENT")

    @classmethod
    def exists(cls, env_var: str):
        value = os.getenv(env_var)
        if not value: 
            print(f"ERROR: {env_var} not set either in .env config file or environment")
        return value

    @classmethod
    def check(cls):
        if not cls.LIDARR_URL:
            print("ERROR: LIDARR_URL not set in .env")
        else: print(f"INFO: LIDARR_URL found: {cls.LIDARR_URL[:4]}****")
        if not cls.LIDARR_APIKEY:
            print("ERROR: LIDARR_APIKEY not set in .env")
        else: print(f"INFO: LIDARR_APIKEY found: {cls.LIDARR_APIKEY[:4]}****")
        if not cls.MUSICBRAINZ_USERAGENT:
            print("ERROR: MUSICBRAINZ_USERAGENT not set in .env")
        else: print(f"INFO: MUSICBRAINZ_USERAGENT found: {cls.MUSICBRAINZ_USERAGENT[:4]}****")




