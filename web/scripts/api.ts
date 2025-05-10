
function fetchJson(asset: string) {
    return new Promise((resolve, reject) => {
        fetch(asset)
            .then(response => response.json())
            .then(data => resolve(data))
            .catch(error => reject(`Error fetching JSON: ${error}`));
    });
}

type TagData = {
    files: string[],
    shared: string[],
};


function intersect2(list1: string[], list2: string[]): string[] {
    return list1.filter(value => list2.includes(value));
}
function intersect(lists: string[][]): string[] {
    var ret = lists[0];
    for (var i = 1; i < lists.length; i++)
        ret = intersect2(ret, lists[i]);
    return ret;
}

/* Randomize array in-place using Durstenfeld shuffle algorithm */
function shuffleArray(list: string[]) {
    for (var i = list.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = list[i];
        list[i] = list[j];
        list[j] = temp;
    }
}

export class API {

    static allTags: string[];
    private static tagData: { [key: string]: TagData } = {};

    static async load(): Promise<void> {
        await fetchJson("data/all_tags.json")
            .then(all => API.allTags = all as string[]);
    }

    static async getRandomTag(tags: string[]): Promise<string> {
        const allowedTags: string[] = await API.getTagsByTags(tags);
        const index = Math.floor(Math.random() * allowedTags.length);
        return allowedTags[index];
    }

    private static async fetchTagData(tag: string): Promise<TagData> {
        if (tag in API.tagData) {
            return API.tagData[tag];
        }

        return fetchJson(`data/tags/${tag}.json`)
            .then(data => {
                return API.tagData[tag] = data as TagData;
            });
    }

    private static async getImagesByTag(tag: string): Promise<string[]> {
        const tagData = await API.fetchTagData(tag);
        return tagData.files.map(name => `/data/sprites/${name}`);
    }

    private static async getTagsByTag(tag: string): Promise<string[]> {
        const tagData = await API.fetchTagData(tag);
        return tagData.shared;
    }

    static async getTagsByTags(tags: string[]): Promise<string[]> {
        if (tags.length === 0) return API.allTags;
        const tagsByEach = await Promise.all(
            tags.map(tag => API.getTagsByTag(tag))
        );
        return intersect(tagsByEach);
    }

    static async getImagesByTags(tags: string[]): Promise<string[] | undefined> {
        if (tags.length === 0) return undefined;
        const imagesByEach = await Promise.all(
            tags.map(tag => API.getImagesByTag(tag))
        );
        const images = intersect(imagesByEach);
        shuffleArray(images);
        return images;
    }

}
