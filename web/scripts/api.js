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
function difference2(list1, list2) {
    return list1.filter(value => !list2.includes(value));
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
    static async getRandomTags(requiredCategory, minCount, maxCount) {
        var tags = [];
        while (true) {
            if (tags.length !== 0) {
                const images = await this.getImagesByTags(tags);
                const count = images.length;
                if (count < minCount) {
                    tags = [];
                    continue;
                }
                if (requiredCategory !== undefined) {
                    const categoryImages = await this.getImagesByTags([requiredCategory, ...tags]);
                    if (categoryImages.length === 0) {
                        tags = [];
                        continue;
                    }
                }
                if (count > minCount && count < maxCount)
                    return tags.join(" ");
                // Reset if too specific
            }
            const nextChoices = await this.getTagsByTags(tags);
            // Reset if too specific
            if (nextChoices.length === 0) {
                tags = [];
                console.log("Reset.");
                continue;
            }
            const nextTag = choose(nextChoices);
            console.log(`[${tags.join(",")}] += ${nextTag}`);
            tags.push(nextTag);
        }
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
    // get a list of 5+ images that share some of the specified tags.
    static async getSimilarImagesByTags(tags) {
        const exactMatches = await API.getImagesByTags(tags);
        if (exactMatches.length > 3 || tags.length === 1)
            return exactMatches;
        var best = [];
        for (const tag of tags) {
            // const tagsWithoutTag = tags.filter(t => t !== tag);
            // const imagesWithoutTag = await API.getImagesByTags(tagsWithoutTag);
            // if (imagesWithoutTag.length > 3) return imagesWithoutTag;
            const imagesWithTag = await API.getImagesByTags([tag]);
            if (imagesWithTag.length > 3 && (best.length > imagesWithTag.length || best.length === 0)) {
                best = imagesWithTag;
            }
        }
        return best;
    }
    static async getImagesByTags(tags) {
        if (tags.length === 0)
            return [];
        const imagesByEach = await Promise.all(tags.map(tag => API.getImagesByTag(tag)));
        var images = intersect(imagesByEach);
        // unless 'partial' is EXPLICITLY given, exclude everything with it
        if (!tags.includes("partial")) {
            const imagesToExclude = await API.getImagesByTag("partial");
            images = difference2(images, imagesToExclude);
        }
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
