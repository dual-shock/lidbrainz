//TODO modularize this mess

function convertTime(dateObj) {
  let hours = dateObj.getHours(); 
  let minutes = dateObj.getMinutes(); 
  let seconds = dateObj.getSeconds(); 
  const pad = (num) => num.toString().padStart(2, '0');
  console.log(`${pad(hours)}:${pad(minutes)}:${pad(seconds)}`)
  return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
}

document.addEventListener('DOMContentLoaded', async () => {
    const lidbrainzEventLog = document.getElementById('logs-scrollable');
    const lidbrainzEventSource = new EventSource('/lidbrainz/interface_logs/interface_logs');
    let lidarrUrl = await refreshLidarrInfo();

    if(lidarrUrl == undefined){
        const eventItem = document.createElement('div');
        eventItem.className = 'event-item';
        const timeString = convertTime(new Date());
        eventItem.innerHTML = 
        `
            <div class="first-row">
                <h5 class="text default event-type WARNING">WARNING</h5>
                <h5 class="text white event-time">[${timeString}]</h5>
            </div>
            <div class="second-row">
                <h4 class="text event-content-indent">└─╲</h5>
                <h5 class="text default-secondary event-content">It seems no Lidarr URL has been configured.</h5>
            </div>
        `;
        lidbrainzEventLog.prepend(eventItem);
    }

    lidbrainzEventSource.onmessage = async function(event) {
        const data = JSON.parse(event.data);

        if (data.event_content.toLowerCase().includes("lidarr")){
            const lidarrLink = `<a href="${lidarrUrl}" target="_blank" rel="noopener noreferrer">Lidarr</a>`;
            data.event_content = data.event_content.replace(/lidarr/gi, lidarrLink);
        }

        const eventItem = document.createElement('div');
        eventItem.className = 'event-item';
        const timeString = convertTime(new Date());
        eventItem.innerHTML = 
        `
            <div class="first-row">
                <h5 class="text default event-type ${data.event_type}">${data.event_type}</h5>
                <h5 class="text white event-time">[${timeString}]</h5>
            </div>
            <div class="second-row">
                <h4 class="text event-content-indent">└─╲</h5>
                <h5 class="text default-secondary event-content">${data.event_content}</h5>
            </div>
        `;
        lidbrainzEventLog.prepend(eventItem);
    }

    if(lidarrUrl != undefined && lidbrainzEventLog.children.length === 0){
        const eventItem = document.createElement('div');
        eventItem.className = 'event-item';
        const timeString = convertTime(new Date());
        eventItem.innerHTML = 
        `
            <div class="first-row">
                <h5 class="text default event-type INFO">INFO</h5>
                <h5 class="text white event-time">[${timeString}]</h5>
            </div>
            <div class="second-row">
                <h4 class="text event-content-indent">└─╲</h5>
                <h5 class="text default-secondary event-content">Fetched Lidarr system info</h5>
            </div>
        `;
        lidbrainzEventLog.prepend(eventItem); 
    }
});



window.addEventListener('beforeunload', () => {
    if (lidbrainzEventSource) {
        lidbrainzEventSource.close();
    }
});



const searchCache = {};



function loadAllCoverImages(parentContainer) {
    const imageWrappers = parentContainer.querySelectorAll('.results-box-image-container[data-mbid]');

    imageWrappers.forEach(imageWrapper => {
        const mbid = imageWrapper.getAttribute('data-mbid');
        const thumbUrl = `https://coverartarchive.org/release-group/${mbid}/front-250`;
        const tempImg = new Image();
        tempImg.src = thumbUrl;

        const resultBox = imageWrapper.querySelector('.results-box.release-group-result');
        const initialHeight = resultBox.getBoundingClientRect().height;

        tempImg.decode()
            .then(() => {

                tempImg.style.height = `${initialHeight - 2}px`;
                const imageDiv = document.createElement('div');
                imageDiv.className = 'results-box-image';
                const img = document.createElement('img');
                tempImg.decoding = "sync";
                imageDiv.appendChild(tempImg);
                imageWrapper.prepend(imageDiv);
            })

            .catch((encodingError) => {
                console.warn(`Cover missing or decode failed for ${mbid}`);
            });
    });
}



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
        await populateFolderProfiles(lidarrInfo.root_folders);
        return lidarrInfo.lidarr_url;
    } 
    
    catch (error) {}
}
async function populateMetadataProfiles(profiles) {
    const container = document.getElementById('metadata-profile-select');
    container.innerHTML = '';

    profiles.forEach(profile => {
        const metadataProfileElementId = `metadata-profile-${profile.id}`;
        container.innerHTML += 
        `
            <input type="radio" id="${metadataProfileElementId}" name="metadata-profile" value="${profile.id}" ${profile.id === 1 ? 'checked' : ''}>
            <label for="${metadataProfileElementId}">└─╲ ${profile.name}</label>
        `;
    });

    container.addEventListener('change', (event) => {
        const selectedMetadataProfileId = document.querySelector('#metadata-profile-select > input[type="radio"]:checked').value;
    });
}



async function populateQualityProfiles(profiles) {
    const container = document.getElementById('quality-profile-select');
    container.innerHTML = '';
    const firstProfileId = profiles[0].id;

    profiles.forEach(profile => {
        const qualityProfileElementId = `quality-profile-${profile.id}`;
        container.innerHTML += 
        `
            <input type="radio" id="${qualityProfileElementId}" name="quality-profile" value="${profile.id}" ${profile.id === firstProfileId ? 'checked' : ''}>
            <label for="${qualityProfileElementId}">└─╲ ${profile.name}</label>
        `;
    });

    container.addEventListener('change', (event) => {
        const selectedQualityProfileId = document.querySelector('#quality-profile-select > input[type="radio"]:checked').value;
    });
}



async function populateFolderProfiles(profiles) {
    const container = document.getElementById('folder-profile-select');
    container.innerHTML = '';
    const firstProfileId = profiles[0].id;

    profiles.forEach(profile => {
        const folderProfileElementId = `folder-profile-${profile.id}`;
        container.innerHTML += 
        `
            <input type="radio" id="${folderProfileElementId}" name="folder-profile" value="${profile.path}" ${profile.id === firstProfileId ? 'checked' : ''}>
            <label for="${folderProfileElementId}">└─╲ ${profile.name}</label>
        `;
    });

    container.addEventListener('change', (event) => {
        const selectedFolderProfileId = document.querySelector('#folder-profile-select > input[type="radio"]:checked').value;
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
    return settings
}



function checkScrollability() {
    const resultsContainer = document.getElementById("search-results-scrollable")
    const logsContainer = document.getElementById("logs-scrollable")

    if (resultsContainer.scrollHeight > resultsContainer.clientHeight) {
        resultsContainer.classList.add('is-scrollable');
    } 
    
    else {
        resultsContainer.classList.remove('is-scrollable');
    }

    if (logsContainer.scrollHeight > logsContainer.clientHeight) {
        logsContainer.classList.add('is-scrollable');
    }

    else {
        logsContainer.classList.remove('is-scrollable');
    }
}
window.addEventListener('resize', checkScrollability);
checkScrollability();



const confirmSearchButton = document.getElementById('search-input-button');
const releaseSearchInput = document.getElementById('release-search-input');
const artistSearchInput = document.getElementById('artist-search-input');
const incresaeLimitButton = document.getElementById('limit-increase');
const decreaseLimitButton = document.getElementById('limit-decrease');
const limitValueDisplay = document.getElementById('limit-value');



incresaeLimitButton.addEventListener('click', () => {
    let currentLimit = parseInt(limitValueDisplay.innerText);

    if (currentLimit < 100) {
        currentLimit += 1;
        limitValueDisplay.innerText = currentLimit.toString();
    }
});



decreaseLimitButton.addEventListener('click', () => {
    let currentLimit = parseInt(limitValueDisplay.innerText);

    if (currentLimit > 1) {
        currentLimit -= 1;
        limitValueDisplay.innerText = currentLimit.toString();
    }
});



async function searchReleaseGroups(query) {
    const params = new URLSearchParams({
        query: query,
        limit: parseInt(limitValueDisplay.innerText)
    });

    const response = await fetch(`/lidbrainz/search_musicbrainz/fully_search?${params}`);

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Search failed');
    }

    return response.json();
}



async function fetchReleases(releaseGroupMbid) {
    const params = new URLSearchParams({
        release_group_mbid: releaseGroupMbid
    });

    const response = await fetch(`/lidbrainz/search_musicbrainz/releases?${params}`);

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch releases');
    }

    return response.json();
}



async function handleSearch() {
    const release = releaseSearchInput.value.trim();
    let artist = artistSearchInput.value.trim();

    if(artist.toLowerCase() === "va"){
        artist = "Various Artists"
    }

    const query = artist ? `releasegroup:${release} AND artist:${artist}` : release;

    if (!query) return;

    try {
        if (searchCache[query]) {
            processSearchResults(searchCache[query]);
        } 
        
        else {
            const results = await searchReleaseGroups(query);
            searchCache[query] = results;
            processSearchResults(results);
        }
    } 
    
    catch (error) {
        console.error(`Search error: ${error.message}`);
    }
}



confirmSearchButton.addEventListener('click', handleSearch);

releaseSearchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSearch();
});
artistSearchInput.addEventListener('keypress', (e) => {
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
    loadAllCoverImages(container);
}

async function handleAddReleaseGroup(releaseGroupId, artistId) {
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
    return result;
}



async function handleAddRelease(releaseGroupId, artistId, releaseId) {
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
    } 

    catch { return null; }
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

    div.innerHTML = 
    `
        <div class="shrinkable">
            <h4 class="text white releaseName">└─╲
                <a href="https://musicbrainz.org/release/${releaseId}" target="_blank" rel="noopener noreferrer">${title}</a>
            &nbsp;</h4>
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
        } 
        
        catch (error) {
            status = `Add release error: ${error.message}`;
        }
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
    const imageWrapper = document.createElement('div');
    imageWrapper.className = 'results-box-image-container';
    imageWrapper.setAttribute('data-mbid', releaseGroupId);
    const div = document.createElement('div');
    div.className = 'results-box release-group-result';

    let html = 
    `
        <div class="release-group-header">
            <div class="shrinkable">
                <h3 class="text white-tertiary releaseGrpArtist">${artist} -&nbsp;</h3>
                <h3 class="text white releaseGrpName">
                    <a href="https://musicbrainz.org/release-group/${releaseGroupId}" target="_blank" rel="noopener noreferrer">${title} (${year})</a>
                </h3>
                <h3 class="text white-tertiary releaseGrpType">&nbsp;[${type}] &nbsp;</h3>
            </div>
            <div class="non-shrinkable">
                <h3 class="text default matchScore">Match%: ${score}</h3>
                <button class="text default addButton" type="button">Add</button>
            </div>
        </div>
    `;

    if (releases && releases.length) {
        html += 
        `
            <hr>
            <button class="releases-toggle-button" type="button">
                <hr>
                <h4 class="text white releaseName">Specific releases ▷ (${releases.length})</h4>
            </button>
            <div class="release-group-releases"></div>
        `;
    } 

    else if (releases === null) {
        html += 
        `
            <hr>
            <button class="releases-toggle-button fetch-releases-button" type="button">
                <hr>
                <h4 class="text white releaseName">Fetch releases</h4>
            </button>
        `;
    }

    div.innerHTML = html;

    div.querySelector('.addButton').addEventListener('click', async () => {
        let status;

        try {
            status = await handleAddReleaseGroup(releaseGroupId, artistId)
        } 

        catch (error) {
            status = `Add release group error: ${error.message}`;
        }
    });

    if (releases && releases.length) {
        const releasesContainer = div.querySelector('.release-group-releases');
        const toggleButton = div.querySelector('.releases-toggle-button');
        releases.forEach(r => releasesContainer.appendChild(createReleaseElement(r,releaseGroupId,artistId)));

        toggleButton.addEventListener('click', () => {
            releasesContainer.classList.toggle('expanded');

            if (releasesContainer.classList.contains('expanded')) {
                toggleButton.innerHTML = `<h4 class="text white releaseName">Specific releases ▽ (${releases.length})</h4>`;
            } 
            else {
                toggleButton.innerHTML = `<h4 class="text white releaseName">Specific releases ▷ (${releases.length})</h4>`;
            }

            checkScrollability();
        });
    } 

    else if (releases === null) {
        const fetchButton = div.querySelector('.fetch-releases-button');

        fetchButton.addEventListener('click', async () => {
            try {
                const result = await fetchReleases(releaseGroupId);
                const fetchedReleases = result.releases;

                const newHtml = 
                `
                    <hr>
                    <button class="releases-toggle-button" type="button">
                        <hr>
                        <h4 class="text white releaseName">Specific releases ▷ (${fetchedReleases.length})</h4>
                    </button>
                    <div class="release-group-releases"></div>
                `;

                fetchButton.parentElement.querySelector('hr').remove();
                fetchButton.remove();
                div.insertAdjacentHTML('beforeend', newHtml);
                const releasesContainer = div.querySelector('.release-group-releases');
                const toggleButton = div.querySelector('.releases-toggle-button');
                fetchedReleases.forEach(r => releasesContainer.appendChild(createReleaseElement(r, releaseGroupId, artistId)));

                toggleButton.addEventListener('click', () => {
                    releasesContainer.classList.toggle('expanded');

                    if (releasesContainer.classList.contains('expanded')) {
                        toggleButton.innerHTML = `<h4 class="text white releaseName">Specific releases ▽ (${fetchedReleases.length})</h4>`;
                    } 
                    else {
                        toggleButton.innerHTML = `<h4 class="text white releaseName">Specific releases ▷ (${fetchedReleases.length})</h4>`;
                    }

                    checkScrollability();
                });
            } 

            catch (error) {
                console.error(`Fetch releases error: ${error.message}`);
            }
        });
    }

    if (score < 90) {
        imageWrapper.style.opacity = '0.55';
    }

    imageWrapper.appendChild(div);
    return imageWrapper;
}