# Lidbrainz
a simple interface built using a collection of python scripts to communicate with the musicbrainz api and a lidarr instance. NOTE: I MADE THIS FOR MYSELF, so, its not super high quality or anything but works (on my machine). 

## setup
you need: 
- a setup lidarr instance (with an indexer / download)
- (highly recommended) a quality profile in lidarr

you simply fill in the lidarr url relative to where this container / server will be runnning, your lidarr instance api key, and a user agent that defines you (more info on this can be found on the musicbrainz api site)

## who is this for?
lidarr uses musicbrainz, most of the music i listen to is on musicbrainz, this app uses musicbrainz and lidarr to search for and subsequently download linux ISOs.

i didnt like using the musicbrainz website as a search engine and having to switch tabs to lidarr just for it to load super slowly and take ages to add the artist, so i put it all into one ui. if you feel the same, this could be for you.

im running lidarr with tubifarry + slskd, and with lidbrainz i do all my searching and downloading through one ui, ive also only tested it with these conditions fyi. 

the ui has options for :
- querying musicbrainz for release groups that will be automatically formatted and forwarded to your lidarr instance 
- auto-downloading (automatically starting a search in your indexers for the musicbrainz release-group you added to lidarr)
- picking quality and metadata profiles, and folders
- picking specific releases for a given release group to be selected in lidarr

things like what stuff is grabbed from your indexers is all set up in lidarr, personally i have setup multiple quality profiles to handle this. 

## who is this NOT for
basically anyone who needs more functionality than whats mentioned above. if you : 
- want to grab music thats not on musicbrainz
- want your searcher / downloader to work all the time
- (currently) want to see all the events that are happening under the hood of lidarr, musicbrainz, slskd, qbit etc. (to be implemented tho)
this might not be for you
- if you use restrictive metadata profiles, as a lot of releases found on musicbrainz will not be added to your lidarr if you use a restrictive metadata profile in lidarr. 

## faq
- if the logs are saying the release group was still not found after artist add, its likely because your metadata profile didnt find that artists release, use a less restrictive metadata profile ig. 

### using on unraid 
if you wish to use unraids built in ui and handling (like pulling updates) you can manually add
the example xml template to your /boot/config/plugins/dockerMan/template-user/ folder
1. copy `my-lidbrainz.example.xml` to your `my-lidbrainz.xml`
2. move `my-lidbrainz.xml` to `/boot/config/plugins/dockerMan/template-user/`
3. in the docker tab on unraid, click "add container"
4. the lidbrainz template should show up in the template dropdown, select it
5. fill in the required values
and just like that it (should) run just like any other unraid docker container on unraid :3

