// on each startup, change the input placeholder to a random track



const input = document.getElementById('search-input');
    const button = document.querySelector('button');
    const resultsDiv = document.getElementById('results');
    const sysInfoDiv = document.getElementById('system-info');

    async function searchReleaseGroups(query) {
        const params = new URLSearchParams({ query: query});
        const response = await fetch(`/lidbrainz/search_musicbrainz/fully_search?${params}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Search failed');
        }
        return response.json();
    }
    async function fetchSystemInfo() {
        const response = await fetch(`/lidbrainz/add_to_lidarr/system_info`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to fetch system info');
        }
        return response.json();
    }
    document.getElementById('fetch-system-info').addEventListener('click', async () => {
        try {
            const systemInfo = await fetchSystemInfo();
            document.getElementById('system-info-results').innerText = JSON.stringify(systemInfo, null, 2);
        } catch (error) {
            document.getElementById('system-info-results').innerText = `Error: ${error.message}`;
        }
    });
    button.addEventListener('click', async (event) => {
        event.preventDefault();
        const query = input.value.trim();
        if (query) {
            try {
                const data = await searchReleaseGroups(query);
                resultsDiv.innerText = JSON.stringify(data, null, 2);
            } catch (error) {
                resultsDiv.innerText = `Error: ${error.message}`;
            }
        }
    });



