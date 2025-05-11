import { API, getQueryParam } from "./api.js";
export function mountApp() {
    // @ts-ignore
    const { createApp, ref, watch, onUpdated, onMounted, computed } = Vue;
    const app = createApp({
        setup() {
            const query = ref(getQueryParam("query", ""));
            const suggestions = ref(API.allTags);
            const images = ref([]);
            const randomize = async () => {
                query.value = await API.getRandomTags(2);
            };
            var activeQuery = "";
            const refreshImages = async () => {
                const currentTags = query.value.split(" ")
                    .filter((tag) => API.allTags.includes(tag));
                const nextQuery = currentTags.join(" ");
                if (nextQuery !== activeQuery) {
                    activeQuery = nextQuery;
                    const nextTags = await API.getTagsByTags(currentTags);
                    suggestions.value = nextTags.map(tag => [...currentTags, tag].join(" "));
                    console.log(currentTags);
                    console.log(nextTags);
                    console.log(suggestions.value);
                    images.value = await API.getImagesByTags(currentTags);
                }
            };
            // send query when the page loads.
            refreshImages();
            watch(query, refreshImages);
            return {
                query,
                randomize,
                suggestions,
                images,
            };
        },
    });
    app.mount("#app");
}
async function runScripts() {
    await API.load();
    mountApp();
}
runScripts();
