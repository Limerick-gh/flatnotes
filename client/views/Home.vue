<template>
  <div class="flex h-full flex-col gap-6 lg:flex-row lg:gap-8">
    <aside
      class="order-2 max-h-48 overflow-y-auto lg:order-1 lg:mt-[25vh] lg:w-52 lg:shrink-0"
    >
      <h2
        class="mb-2 px-2 text-xs font-bold uppercase text-theme-text-very-muted"
      >
        Tags
      </h2>
      <LoadingIndicator ref="tagsLoadingIndicator">
        <nav class="flex flex-wrap gap-1 lg:flex-col lg:flex-nowrap">
          <RouterLink
            v-for="tag in tags"
            :key="tag"
            :to="{ name: 'search', query: { term: `#${tag}` } }"
            class="rounded px-2 py-1 text-sm text-theme-text-muted hover:bg-theme-background-elevated hover:text-theme-text"
          >
            #{{ tag }}
          </RouterLink>
        </nav>
      </LoadingIndicator>
    </aside>
    <div class="order-1 flex flex-1 justify-center lg:order-2">
      <div class="flex max-w-[500px] flex-1 flex-col items-center pt-[25vh]">
        <Logo class="mb-5" />
        <SearchInput class="mb-5 shadow-[0_0_20px] shadow-theme-shadow" />
        <LoadingIndicator
          ref="loadingIndicator"
          class="flex min-h-56 flex-col items-center"
          hideLoader
        >
          <p
            v-if="notes.length > 0"
            class="mb-2 text-xs font-bold uppercase text-theme-text-very-muted"
          >
            {{ globalStore.config.quickAccessTitle }}
          </p>
          <RouterLink
            v-for="note in notes.slice(0, globalStore.config.quickAccessLimit)"
            :to="{ name: 'note', params: { title: note.title } }"
            class="mb-1"
          >
            <CustomButton :label="note.title" />
          </RouterLink>
          <RouterLink
            v-if="notes.length > globalStore.config.quickAccessLimit"
            :to="{
              name: 'search',
              query: {
                term: globalStore.config.quickAccessTerm,
                sortBy: searchSortOptions[globalStore.config.quickAccessSort],
              },
            }"
            title="Show more"
            ><CustomButton :iconPath="mdiDotsHorizontal"
          /></RouterLink>
        </LoadingIndicator>
      </div>
    </div>
  </div>
</template>

<script setup>
import { mdiDotsHorizontal } from "@mdi/js";
import { useToast } from "primevue/usetoast";
import { onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";

import { apiErrorHandler, getNotes, getTags } from "../api.js";
import CustomButton from "../components/CustomButton.vue";
import LoadingIndicator from "../components/LoadingIndicator.vue";
import Logo from "../components/Logo.vue";
import { searchSortOptions } from "../constants.js";
import { useGlobalStore } from "../globalStore.js";
import SearchInput from "../partials/SearchInput.vue";

const globalStore = useGlobalStore();
const loadingIndicator = ref();
const tags = ref([]);
const tagsLoadingIndicator = ref();
const notes = ref([]);
const toast = useToast();

function init() {
  if (globalStore.config.quickAccessHide) {
    return;
  }
  getNotes(
    globalStore.config.quickAccessTerm,
    globalStore.config.quickAccessSort,
    // Order by ascending if sorting by title, descending otherwise.
    globalStore.config.quickAccessSort === "title"
      ? "asc"
      : "desc",
    // Limit is increased by 1 to check if there are more notes than the limit.
    globalStore.config.quickAccessLimit + 1,
  )
    .then((data) => {
      notes.value = data;
      loadingIndicator.value.setLoaded();
    })
    .catch((error) => {
      loadingIndicator.value.setFailed();
      apiErrorHandler(error, toast);
    });
}

function initTags() {
  getTags()
    .then((data) => {
      tags.value = data;
      tagsLoadingIndicator.value.setLoaded();
    })
    .catch((error) => {
      tagsLoadingIndicator.value.setFailed();
      apiErrorHandler(error, toast);
    });
}

// Watch to allow for delayed config load.
watch(() => globalStore.config.hideRecentlyModified, init);
onMounted(() => {
  init();
  initTags();
});
</script>
