
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM fully loaded, getting lidarr info');
    const lidarrUrl = await refreshLidarrInfo();
    const lidbrainzEventLog = document.getElementById('logs-scrollable');
    const lidbrainzEventSource = new EventSource('/lidbrainz/interface_logs/interface_logs');
    lidbrainzEventSource.onmessage = async function(event) {
        const data = JSON.parse(event.data);
        console.log("Lidbrainz Event:", data);

        if (data.event_content.toLowerCase().includes("lidarr")){
            const lidarrLink = `<a href="${lidarrUrl}" target="_blank" rel="noopener noreferrer">Lidarr</a>`;
            data.event_content = data.event_content.replace(/lidarr/gi, lidarrLink);
        }

        const eventItem = document.createElement('div');
        eventItem.className = 'event-item';
        eventItem.innerHTML = `
            <div class="first-row">
                <h5 class="text white event-time">[${data.event_time}]</h5>
                <h5 class="text default event-type">${data.event_type}</h5>
            </div>
            <div class="second-row">
                <h4 class="text event-content-indent">└─╲</h5> 
                <h5 class="text default-secondary event-content">${data.event_content}</h5>
            </div>
        `;
        lidbrainzEventLog.prepend(eventItem);
    }
});
const searchCache = {};


async function fetchLidarrInfo() {
        const response = await fetch(`/lidbrainz/add_to_lidarr/system_info`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to fetch system info');
        }
        return response.json();
}
async function refreshLidarrInfo() {
    try {
        const lidarrInfo = await fetchLidarrInfo();
        await populateMetadataProfiles(lidarrInfo.metadata_profiles);
        await populateQualityProfiles(lidarrInfo.quality_profiles);
        console.log("FOLDER PROFILES:", lidarrInfo.root_folders)
        await populateFolderProfiles(lidarrInfo.root_folders);
        return lidarrInfo.lidarr_url;
    } catch (error) {
        
    }
}
async function populateMetadataProfiles(profiles) {
    const container = document.getElementById('metadata-profile-select');
    container.innerHTML = ''; // Clear existing options
    profiles.forEach(profile => {
        console.log(profile.name, profile.id);
        const metadataProfileElementId = `metadata-profile-${profile.id}`;
        container.innerHTML += `
            <input type="radio" id="${metadataProfileElementId}" name="metadata-profile" value="${profile.id}" ${profile.id === 1 ? 'checked' : ''}>
            <label for="${metadataProfileElementId}">└─╲ ${profile.name}</label>
        `;
    });
    container.addEventListener('change', (event) => {
        const selectedMetadataProfileId = document.querySelector('#metadata-profile-select > input[type="radio"]:checked').value;
        console.log(`Selected metadata profile ID is : ${selectedMetadataProfileId}`);
    });
}
async function populateQualityProfiles(profiles) {
    const container = document.getElementById('quality-profile-select');
    container.innerHTML = ''; // Clear existing options
    const firstProfileId = profiles[0].id;
    profiles.forEach(profile => {
        console.log(profile.name, profile.id);
        const qualityProfileElementId = `quality-profile-${profile.id}`;
        container.innerHTML += `
            <input type="radio" id="${qualityProfileElementId}" name="quality-profile" value="${profile.id}" ${profile.id === firstProfileId ? 'checked' : ''}>
            <label for="${qualityProfileElementId}">└─╲ ${profile.name}</label>
        `;
    });
    container.addEventListener('change', (event) => {
        const selectedQualityProfileId = document.querySelector('#quality-profile-select > input[type="radio"]:checked').value;
        console.log(`Selected Quality profile ID is : ${selectedQualityProfileId}`);
    });
}
async function populateFolderProfiles(profiles) {
    const container = document.getElementById('folder-profile-select');
    container.innerHTML = ''; // Clear existing options
    const firstProfileId = profiles[0].id;
    profiles.forEach(profile => {
        console.log(profile.name, profile.path);
        const folderProfileElementId = `folder-profile-${profile.id}`;
        container.innerHTML += `
            <input type="radio" id="${folderProfileElementId}" name="folder-profile" value="${profile.path}" ${profile.id === firstProfileId ? 'checked' : ''}>
            <label for="${folderProfileElementId}">└─╲ ${profile.name}</label>
        `;
    });
    container.addEventListener('change', (event) => {
        const selectedFolderProfileId = document.querySelector('#folder-profile-select > input[type="radio"]:checked').value;
        console.log(`Selected Folder profile ID is : ${selectedFolderProfileId}`);
    });
}
function getSettings() {
    const metadataProfileId = document.querySelector('#metadata-profile-select > input[type="radio"]:checked').value;
    const qualityProfileId = document.querySelector('#quality-profile-select > input[type="radio"]:checked').value;
    const folderPath = document.querySelector('#folder-profile-select > input[type="radio"]:checked').value;
    const autoDownload = document.getElementById('auto-download-checkbox').checked;
    const settings = {
        metadataProfileId,
        qualityProfileId,
        folderPath,
        autoDownload
    };
    console.log("Current settings:", settings);
    return settings
}



function checkScrollability() {
    const resultsContainer = document.getElementById("search-results-scrollable")
    const logsContainer = document.getElementById("logs-scrollable")

    if (resultsContainer.scrollHeight > resultsContainer.clientHeight) {
    resultsContainer.classList.add('is-scrollable');
    } else {
    resultsContainer.classList.remove('is-scrollable');
    }

    if (logsContainer.scrollHeight > logsContainer.clientHeight) {
    logsContainer.classList.add('is-scrollable');
    } else {
    logsContainer.classList.remove('is-scrollable');
    }
}
window.addEventListener('resize', checkScrollability);
checkScrollability();



// if artist: 
//     query = f"releasegroup:{query} AND artist:{artist}"
//     print(f"INFO: artist included in query with artist: {query}")


const confirmSearchButton = document.getElementById('search-input-button');
const releaseSearchInput = document.getElementById('release-search-input');
const artistSearchInput = document.getElementById('artist-search-input');

async function searchReleaseGroups(query) {
    const params = new URLSearchParams({ 
        query: query
    });
    const response = await fetch(`/lidbrainz/search_musicbrainz/fully_search?${params}`);
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Search failed');
    }
    return response.json();
}

async function handleSearch() {
    const release = releaseSearchInput.value.trim();
    let artist = artistSearchInput.value.trim();
    if(artist.toLowerCase() == "va"){
        artist = "Various Artists"
    }

    const query = artist ? `releasegroup:${release} AND artist:${artist}` : release;

    console.log("Final search query:", query);
    
    if (!query) return;
    
    try {
        
        if (searchCache[query]) {
            console.log(`Using cached results for: ${query}`);
            processSearchResults(searchCache[query]);
        } else {
            console.log(`Searching for: ${query}`);
            const results = await searchReleaseGroups(query);
            
            
            searchCache[query] = results;
            
            processSearchResults(results);
        }
    } catch (error) {
        console.error(`Search error: ${error.message}`);
    }
}

confirmSearchButton.addEventListener('click', handleSearch);
releaseSearchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSearch();
});



function processSearchResults(results) {
    const container = document.getElementById('search-results-scrollable');
    container.innerHTML = ''; 

    const releaseGroups = results['release-groups'] || [];
    const bestMatchReleases = results['best-match-releases'] || [];

    releaseGroups.forEach((rg, index) => {

        const releases = index === 0 ? bestMatchReleases : null;
        container.appendChild(createReleaseGroupElement(rg, releases));
    });

    checkScrollability();
}

async function handleAddReleaseGroup(releaseGroupId, artistId) {
    console.log('Add release group:', releaseGroupId, artistId);

    const settings = getSettings();
    
    const params = new URLSearchParams({
        release_group_mbid: releaseGroupId, 
        artist_mbid: artistId,
        metadata_profile_id: settings.metadataProfileId,
        quality_profile_id: settings.qualityProfileId,
        root_folder_path: settings.folderPath,
        auto_download: settings.autoDownload
    });
    const response = await fetch(`/lidbrainz/add_to_lidarr/fully_add_release?${params}`);
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'failed to add release group');
    }
    const result = await response.json();
    console.log(result)
    return result; 
}
async function handleAddRelease(releaseGroupId, artistId, releaseId) {
    console.log('Add release:', releaseGroupId, artistId, releaseId);
    
    const settings = getSettings();
    
    const params = new URLSearchParams({
        release_group_mbid: releaseGroupId, 
        artist_mbid: artistId,
        release_mbid: releaseId,
        metadata_profile_id: settings.metadataProfileId,
        quality_profile_id: settings.qualityProfileId,
        root_folder_path: settings.folderPath,
        auto_download: settings.autoDownload
    });
    const response = await fetch(`/lidbrainz/add_to_lidarr/fully_add_release?${params}`);
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'failed to add release');
    }
    const result = await response.json();
    console.log(result)
    return result; 
}
function getArtistNames(artistCredit) {
    if (!artistCredit || !artistCredit.length) return 'N/A';
    return artistCredit.map(ac => ac.name || 'N/A').join(', ');
}
function getArtistId(artistCredit){
    if (!artistCredit || !artistCredit.length) return 'N/A';
    return artistCredit[0].artist.id || 'N/A';
}
function getYear(dateStr) {
    if (!dateStr) return 'N/A';
    return dateStr.substring(0, 4);
}
function getCountryCode(release) {
    try {
        const code = release['release-events']?.[0]?.area?.['iso-3166-1-codes']?.[0];
        if (!code) return null;
        if (code === 'XW') return 'un';
        if (code === 'XE') return 'eu';
        return code.toLowerCase();
    } catch { return null; }
}
function getTrackString(media) {
    if (!media || !media.length) return 'N/A';
    return media.map(m => m['track-count'] || 0).join('x');
}
function createReleaseElement(release, releaseGroupId, artistId) {
    const title = release.title || 'N/A';
    const format = release.media?.[0]?.format || 'N/A';
    const tracks = getTrackString(release.media);
    const status = release.status || 'N/A';
    const countryCode = getCountryCode(release);
    const countryDisplay = release['release-events']?.[0]?.area?.['iso-3166-1-codes']?.[0] || 'N/A';
    const date = release['release-events']?.[0]?.date || release.date || 'N/A';
    const releaseId = release.id;

    const div = document.createElement('div');
    div.className = 'release';
    div.innerHTML = `
        <div class="shrinkable">
            <h4 class="text white releaseName">└─╲ ${title}&nbsp;</h4>
            <h4 class="text default releaseFormat">[${format}]▷╲</h4>
            <h4 class="text default releaseTracks">(${tracks}),&nbsp;</h4>
            <h4 class="text default-secondary releaseStatus">${status}</h4>
        </div>
        <div class="non-shrinkable">
            ${countryCode ? `<img src="https://flagcdn.com/${countryCode}.svg">` : `<img src="https://upload.wikimedia.org/wikipedia/commons/b/b0/No_flag.svg">`}
            <h4 class="text white releaseCountry">${countryDisplay}&nbsp;¦</h4>
            <h4 class="text white releaseYear">${date}</h4>
            <h4 class="text green releaseAddButton">Add release</h4>
        </div>
    `;
    
    div.querySelector('.releaseAddButton').addEventListener('click', async () => {
        let status
        try {
            status = await handleAddRelease(releaseGroupId, artistId, releaseId);
        } catch (error) {
            status = `Add release error: ${error.message}`;
        }
        console.log(status)
    });
    return div;
}
function createReleaseGroupElement(releaseGroup, releases = null) {
    const artist = getArtistNames(releaseGroup['artist-credit']);
    const title = releaseGroup.title || 'N/A';
    const year = getYear(releaseGroup['first-release-date']);
    const type = releaseGroup['primary-type'] || 'N/A';
    const score = releaseGroup.score ?? 'N/A';
    const releaseGroupId = releaseGroup.id;
    const artistId = getArtistId(releaseGroup['artist-credit']); 

    const div = document.createElement('div');
    div.className = 'results-box release-group-result';

    let html = `
        <div class="release-group-header">
            <div class="shrinkable">
                <h3 class="text white-tertiary releaseGrpArtist">${artist} -&nbsp;</h3>
                <h3 class="text white releaseGrpName">${title} (${year})&nbsp;</h3>
                <h3 class="text white-tertiary releaseGrpType">[${type}] &nbsp;</h3>
            </div>
            <div class="non-shrinkable">
                <h3 class="text default matchScore">Match%: ${score}</h3>
                <button class="text default addButton" type="button">Add</button>
            </div>
        </div>
    `;

    if (releases && releases.length) {
        html += `<hr><div class="release-group-releases"></div>`;
    }

    div.innerHTML = html;
    div.querySelector('.addButton').addEventListener('click', async () => {
        let status;
        try {
            status = await handleAddReleaseGroup(releaseGroupId, artistId)
        } catch (error) {
            status = `Add release group error: ${error.message}`;
        }
        console.log(status)
    });

    if (releases && releases.length) {
        const releasesContainer = div.querySelector('.release-group-releases');
        releases.forEach(r => releasesContainer.appendChild(createReleaseElement(r,releaseGroupId,artistId)));
    }

    return div;
}








