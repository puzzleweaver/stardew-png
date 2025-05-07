
function fetchJson(asset) {
    return new Promise((resolve, reject) => {
        fetch(asset)
            .then(response => response.json()) // Parse JSON
            .then(data => resolve(data))
            .catch(error => reject('Error fetching JSON:', error));
    });
}

function populateList(id, list) {
    datalist = document.getElementById(id)
    for (const tag of list) {
        option = document.createElement("option")
        option.setAttribute("value", tag)
        datalist.appendChild(option)
    }
}

async function doEverything() {
    allTags = await fetchJson('data/all_tags.json')

    console.log(allTags)
    populateList("all-tags-list", allTags)

    // document.appendChild(datalist)
    document.getElementById("query-input")
        .setAttribute("list", "all-tags-list")
}

doEverything()