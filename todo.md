- make the musicbrainz api calls filter for only the important stuff
- make the lidarr api calls, instead of first adding artist and then adding
specific releases as monitored, just send it all with the artist payload (if artist doesnt exist)
- in lidarr, add handling for when api requests answer with possibly something (like forbidden, so payload gets sent) but doesnt register it as an artist or album actually being present, i.e, dont count any filled string as confirmation that an artist / album is present (lidarr_endpoint)
