function fetchJson(asset) {
    return new Promise((resolve, reject) => {
        fetch(asset)
            .then(response => response.json())
            .then(data => resolve(data))
            .catch(error => reject(`Error fetching JSON: ${error}`));
    });
}
const urlParams = new URLSearchParams(window.location.search);
export function getQueryParam(name, fallback) {
    const param = urlParams.get(name);
    if (param === null)
        return fallback;
    return param;
}
function intersect2(list1, list2) {
    return list1.filter(value => list2.includes(value));
}
function intersect(lists) {
    var ret = lists[0];
    for (var i = 1; i < lists.length; i++)
        ret = intersect2(ret, lists[i]);
    return ret;
}
/* Randomize array in-place using Durstenfeld shuffle algorithm */
function shuffleArray(list) {
    for (var i = list.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = list[i];
        list[i] = list[j];
        list[j] = temp;
    }
}
export function choose(list) {
    return list[Math.floor(Math.random() * list.length)];
}
export class API {
    static async load() {
        await fetchJson("/data/all_tags.json")
            .then(all => API.allTags = all);
    }
    static async getRandomTags(count) {
        var tags = [];
        for (var i = 0; i < count; i++) {
            const choices = await this.getTagsByTags(tags);
            // maximally specific
            if (choices.length === 0)
                break;
            tags.push(choose(choices));
        }
        return tags.join(" ");
    }
    static async fetchTagData(tag) {
        if (tag in API.tagData) {
            return API.tagData[tag];
        }
        return fetchJson(`/data/tags/${tag}.json`)
            .then(data => {
            return API.tagData[tag] = data;
        });
    }
    static async getImagesByTag(tag) {
        const tagData = await API.fetchTagData(tag);
        return tagData.files.map(name => `/data/sprites/${name}`);
    }
    static async getTagsByTag(tag) {
        const tagData = await API.fetchTagData(tag);
        return tagData.shared;
    }
    static async getTagsByTags(tags) {
        if (tags.length === 0)
            return API.allTags;
        const tagsByEach = await Promise.all(tags.map(tag => API.getTagsByTag(tag)));
        return intersect(tagsByEach)
            .filter(tag => !tags.includes(tag));
    }
    static async getImagesByTags(tags) {
        if (tags.length === 0)
            return [];
        const imagesByEach = await Promise.all(tags.map(tag => API.getImagesByTag(tag)));
        const images = intersect(imagesByEach);
        shuffleArray(images);
        return images;
    }
    static async getTagsByImage(image) {
        return fetchJson(image.replace(".png", "t.json"))
            .then(data => {
            return data;
        });
    }
}
API.tagData = {};
