import { API } from "./api.js";

export function mountApp() {
    // @ts-ignore
    const { createApp, ref, watch, onUpdated, onMounted, computed } = Vue;

    const app = createApp({
        setup() {
            const message = 'Where Woof';

            const tags = ref([]);
            const query = ref("");
            const suggestedTags = ref(API.allTags);
            const images = ref([]);

            const randomize = async () => {
                query.value = await API.getRandomTag(tags.value);
            };

            const addTerm = () => {
                tags.value = [...tags.value, query.value];
                query.value = "";
            }

            const onRemoveTerm = (term: string) => {
                tags.value = tags.value.filter((item: string) => item !== term);
            };

            const getWiggle = () => {
                const radius = 10;
                return Math.floor(Math.random() * radius * 2 - radius);
            };

            setInterval(() => {
                images.value = [...images.value];
            }, 100);

            watch(query, () => {
                console.log(`Value changed to ${query.value}...`);
            });

            watch(tags, async () => {
                suggestedTags.value = await API.getTagsByTags(tags.value);
                images.value = await API.getImagesByTags(tags.value);
            });

            return {
                message,
                onRemoveTerm,
                terms: tags,
                query,
                randomize,
                addTerm,
                suggestedTags,
                images,
                getWiggle,
            };
        },
    });

    /**
     * Reused search term component.
     */
    app.component('search-term', {
        props: ['term', 'removeTerm'],
        template: "#search-term-template",
        setup(props: {
            term: string,
            removeTerm: (term: string) => void,
        }) {
            const removeIt = computed(() =>
                () => props.removeTerm(props.term),
            );
            return {
                removeIt,
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