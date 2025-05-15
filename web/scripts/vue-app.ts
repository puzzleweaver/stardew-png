import { API, getQueryParam } from "./api.js";

export function mountApp() {
    // @ts-ignore
    const { createApp, ref, watch, onUpdated, onMounted, computed } = Vue;

    const app = createApp({
        setup() {
            const query = ref(getQueryParam("query", ""));
            const suggestions = ref(API.allTags);
            const images = ref([]);
            const category = ref(undefined);

            const randomize = async () => {
                query.value = await API.getRandomTags(category.value, 5, 100);
            };

            const toggleCategory = (newCategory: string) => {
                // set the category either to the new thing, or to nothing.
                if (newCategory === category.value) category.value = undefined;
                else category.value = newCategory;

                console.log(`Set category to: ${category.value}`);
                randomize();
            }

            // if it's empty to start, fill in a random one!
            if (query.value === "") randomize();

            var activeQuery = "";
            const refreshImages = async () => {
                const currentTags = query.value.split(" ")
                    .filter((tag: string) => API.allTags.includes(tag));

                const nextQuery = currentTags.join(" ");

                if (nextQuery !== activeQuery) {
                    activeQuery = nextQuery;
                    const nextTags = await API.getTagsByTags(currentTags);
                    suggestions.value = nextTags.map(
                        tag => [...currentTags, tag].join(" "),
                    );
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

                categoryMessage: computed(() => {
                    if (category.value !== undefined)
                        return `Each query is guaranteed to have at least one sprite tagged as '${category.value}'.`;
                    return undefined;
                }),

                category,
                toggleCategory,
            };
        },
    });

    app.component('category-button', {
        props: ['category', 'plural'],
        template: "#category-button-template",
        setup(props: {
            category: string,
            plural: string,
        }) {
            return {
                color: computed(() => {
                    switch (props.category) {
                        case "red": return "rgb(191, 1, 1)";
                        case "orange": return "rgb(211, 81, 39)";
                        case "yellow": return "rgb(205, 151, 26)";
                        case "green": return "rgb(88, 193, 36)";
                        case "blue": return "rgb(23, 128, 213)";
                        case "purple": return "purple";
                        case "black": return "black";
                        default: return '';
                    }
                }),
            };
        }
    });
    app.mount("#app");
}

async function runScripts() {
    await API.load();
    mountApp();
}

runScripts();