# LidBrainz

<p align="center">
  <img src="interface/assets/icon.svg" width="128" height="128">
</p>

---

A simple one-page interface to manage all Lidarr requests, built upon the MusicBrainz api, centered around specific Releases and **Release Groups** (instead of artists), i.e. albums, singles, mixtapes, etc. If a release is on MusicBrainz, LidBrainz can search for and find it in ~1 - 2 seconds. With one click it can be added to your Lidarr instance and automatically search (for your linux ISOs, ofc.) 

![Alt text](assets/videos/demo_1.gif)

_Please note; this is a container i made for my own server and to get a docker container project under my belt, its not vibecoded so its probably kinda shitty, the code is a mess, and theres certainly better alternatives out there. buuut if you like it thats awesome :)_<3

## Features (and sorta how they work)
LidBrainz focuses mainly on being lightweight and fast, what i found lacking in Lidarr itself. Its also focused on being transparent about whats happening "under the hood", with clear logs and the ability to change more or less every setting for adding music to lidarr (with more options to come). 

### Release centered querying:
Lidarr itself and most forks or wrappers use Artist objects as the "main" form of adding and storing data, i didnt like this as 99% of the time i dont want ALL the releases of an artist, i usually just want 1-2 albums. LidBrainz handles this by automatically seeing if the artist of the release you want to add already exists in your library or not, and if it doesnt it'll add automatically add it with the correct release monitored (and all other releases un-monitored)

### Speedy searches:
LidBrainz takes around ~1 second per query, depending on how much you're querying and if you've configured your user agent correctly. This query contains 0 - 100 release groups immediately ready to be added to lidarr

### Being particular about specific releases:
If youre like me and can be a little picky about specific releases in release groups (by this i mean release variants like deluxe editions, bootlegs, specific foreign releases, or just the release with the most tracks) but hated having to go into lidarr and manually select it each time youre in luck. WIth lidbrainz you can select which release you want before its even sent to lidarr, and this will be automatically selected as soon as its added. 

### Specifying settings (folder, metadata/quality profile, auto-grab)
the ui has buttons and dials for all those things, i like knowing exactly what i do when i add stuff. thats abt it xP

---

## (more importantly) Non-features (and how they dont work)
Like i said earlier, being lightweight and fast (and working _just enough_) was and is the only focus of the application, so a lot of features like authentication, (as in a login page, api header auth is being added soon, login page too who knows *shrugs), mobile styling, additional recommendations, batch adding artist discograpghies, and editing / deleting in your lidarr library is not present. (that last part likely wont ever be either, im not planning on putting a single PUT or DELETE request in here lol)

### Adding whole artist discographies at a time
LidBrainz is made with release groups in mind so theres no native features to add entire artist discographies quickly (unless you type really fast), you can theoretically use it to add artists, but there are much better alternatives for that out there Aurral or just searching the musibrainz website itself

### Making use of any more metadata than what musicbrainz has to offer
LidBrainz _only uses MusicBrainz_, if you need to add anything thats not on musicbrainz it cant help you. I made it like this because, well, lidarr only uses musicbrainz (unless you set it up not to), and thats what worked for me. For anything else i just use slskd manually.  

### Recommendations 
The search functionality is basically just a wrapper on top of the musicbrainz search on their website, so what matches most there is all you get. Theres no tracking of what you download or listen to, and no extra metadata other than musicbrainz, so theres no cool recommendations

### Mobile ui
I scrapped together this ui with my high school html and css knowledge, and it works for most desktops! but i have not even begun to look at making it mobile friendly lol


---
## Installation 
_Note: if you're an **UnRaid** user like me, ive added a template that can be manually added and used, instructions are [below]()_
### Prerequisites: 
1. a running lidarr instance reachable from this container
2. some public url/email u can put in the musicbrainz user agent
3. (optional, but **highly** recommended), a not-so-restrictive metadata profile, and a **good quality profile** based on your preferences. A good quality profile will vastly increase the quality of your automatic searches, _**which can be triggered from within LidBrainz**_. 
4. (optional, but recommended) if youre not already using slskd and tubifarry, i highly recommend it, its awesome

### Environment: 
1. either clone the repo: ```git clone https://github.com/dual-shock/lidbrainz.git``` <br> or just grab the ```docker-compose.example.yml``` file
2. fill in the ```.env.example``` file, and rename it to just ```.env```, if you're unsure about how to format your musicbrainz user agent see [here](https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting) <br> fill in the ```docker-compose.example.yml``` and rename it to just ```docker-compose.yml``` (here you can change the exposed port and docker network, if your lidarr is running on a custom network for example)

### Running
&nbsp;&nbsp;&nbsp;&nbsp;run docker compose from the same folder as your cloned repo / docker-compose file. 
```bash
docker-compose up -d
```
--- 


---
## Installation (UnRaid)
since i made this for myself, and i use UnRaid, ive included an unraid template that'll let you manually add a template to run this container like any of your other UnRaid docker containers!

_Note: given this container was just made for myself and is just in development, i havent published it to the Community Applications plugin, i might in the future though, but for now this is just a :dev build. this also means the container adhere to the same quality control as the CA containers, again, i made this for myself so use at your own discretion_ 

### how to manually add the template
1. move/copy `my-lidbrainz.xml` to `/boot/config/plugins/dockerMan/templates-user/`
2. in the docker tab on unraid, click "add container"
3. the lidbrainz template should show up in the template dropdown, select it

### how to set up the container
1. pick a webui port thats not in use by any of your other containers
2. to access lidarr through its hostname, select the same docker network as your lidarr instance
3. fill in the required fields, see the .env.example configuration if youre unsure what to put there 

it should now run just like any other UnRaid docker container, and you can automatically pull eventual updates through the docker tab. 

---

## who is this for?
lidarr uses musicbrainz, most of the music i listen to is on musicbrainz, this app uses musicbrainz and lidarr to search for and subsequently download linux ISOs.

i didnt like using the musicbrainz website as a search engine and having to switch tabs to lidarr just for it to load super slowly and take ages to add the artist, so i put it all into one ui. if you feel the same, this could be for you.

im running lidarr with tubifarry + slskd, and with lidbrainz i do all my searching and downloading through one ui, ive also only tested it with these conditions fyi. 

things like what stuff is grabbed from your indexers is all set up in lidarr, personally i have setup multiple quality profiles to handle this. 

## who is this NOT for
basically anyone who wants more functionality than whats mentioned above. 

---

## probable issues
- Failing to add to lidarr because of metadata profiles: if you try to add a single, but the metadata profile youve selected only includes albums, the single wont be present in your lidarr library and therefore cannot be added. The fix for this is to use another metadata profile
- Rate limiting: if you've improperly formatted your musicbrainz user agent, youll automatically get rate limited. you can also get rate limited for other reasons, info on this is on the musicbrainz docs. Note that, LidBrainz has a built-in rate limiter so if you are getting rate limited more than youd expect its likely because of improper config.

