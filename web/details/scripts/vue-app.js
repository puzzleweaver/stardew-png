import { API, getQueryParam } from "../../scripts/api.js";
export function mountApp() {
    // @ts-ignore
    const { createApp, ref, watch, onUpdated, onMounted, computed } = Vue;
    const app = createApp({
        setup() {
            const image = getQueryParam("img", "");
            const query = getQueryParam("query", "");
            const tags = ref([]);
            const relatedImages = ref([]);
            API.getTagsByImage(image).then(imageTags => {
                tags.value = imageTags;
                API.getImagesByTags(imageTags).then((imageTagImages) => {
                    relatedImages.value = imageTagImages;
                });
            });
            // this is OK only because [image] is constant.
            const fullImagePath = `https://stardew-png.github.io${image}`;
            const crossStitchLink = `https://puzzleweaver.github.io/cross-stitch-maker/?img=${encodeURIComponent(fullImagePath)}`;
            return {
                image,
                query,
                tags,
                relatedImages,
                crossStitchLink,
                downloadName: computed(() => {
                    return `${tags.value.join('-')}.png`;
                }),
            };
        },
    });
    app.mount("#app");
}
mountApp();
