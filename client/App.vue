<template>
  <LoadingIndicator
    ref="loadingIndicator"
    class="container mx-auto flex h-screen flex-col px-2 py-4 print:max-w-full"
  >
    <PrimeToast />
    <SearchModal v-model="isSearchModalVisible" />
    <NavBar
      v-if="showNavBar"
      ref="navBar"
      :class="{ 'print:hidden': route.name == 'note' }"
      :hide-logo="!showNavBarLogo"
      @toggleSearchModal="toggleSearchModal"
    />
    <div v-if="showNavBar" class="flex min-h-0 flex-1 flex-col lg:flex-row lg:gap-8">
      <aside
        class="max-h-48 shrink-0 overflow-y-auto border-b border-theme-border py-3 lg:max-h-none lg:w-64 lg:border-b-0 lg:border-r lg:py-4 lg:pr-4"
      >
        <h2
          class="mb-2 px-3 text-sm font-bold uppercase text-theme-text-very-muted"
        >
          Tags
        </h2>
        <LoadingIndicator ref="tagsLoadingIndicator">
          <nav class="flex flex-wrap gap-1">
            <RouterLink
              v-for="tag in tags"
              :key="tag"
              :to="{ name: 'search', query: { term: `#${tag}` } }"
              class="rounded px-3 py-2 text-base text-theme-text-muted hover:bg-theme-background-elevated hover:text-theme-text"
            >
              #{{ tag }}
            </RouterLink>
          </nav>
        </LoadingIndicator>
      </aside>
      <main class="min-h-0 min-w-0 flex-1">
        <RouterView />
      </main>
    </div>
    <RouterView v-else />
  </LoadingIndicator>
</template>

<script setup>
import Mousetrap from "mousetrap";
import "mousetrap/plugins/global-bind/mousetrap-global-bind";
import { useToast } from "primevue/usetoast";
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";

import { apiErrorHandler, getConfig, getTags } from "./api.js";
import PrimeToast from "./components/PrimeToast.vue";
import { useGlobalStore } from "./globalStore.js";
import { loadTheme } from "./helpers.js";
import NavBar from "./partials/NavBar.vue";
import SearchModal from "./partials/SearchModal.vue";
import LoadingIndicator from "./components/LoadingIndicator.vue";
import router from "./router.js";

const globalStore = useGlobalStore();
const isSearchModalVisible = ref(false);
const loadingIndicator = ref();
const tags = ref([]);
const tagsLoadingIndicator = ref();
const navBar = ref();
const route = useRoute();
const toast = useToast();

// '/' to search
Mousetrap.bind("/", () => {
  if (route.name !== "login") {
    toggleSearchModal();
    return false;
  }
});

// 'CTRL + ALT/OPT + N' to create new note
Mousetrap.bindGlobal("ctrl+alt+n", () => {
  if (route.name !== "login") {
    router.push({ name: "new" });
    return false;
  }
});

// 'CTRL + ALT/OPT + H' to go to home
Mousetrap.bindGlobal("ctrl+alt+h", () => {
  if (route.name !== "login") {
    router.push({ name: "home" });
    return false;
  }
});

getConfig()
  .then((data) => {
    globalStore.config = data;
    loadingIndicator.value.setLoaded();
  })
  .catch((error) => {
    apiErrorHandler(error, toast);
    loadingIndicator.value.setFailed();
  });

const showNavBar = computed(() => {
  return route.name !== "login";
});

const showNavBarLogo = computed(() => {
  return route.name !== "home";
});

function toggleSearchModal() {
  isSearchModalVisible.value = !isSearchModalVisible.value;
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

watch(showNavBar, (isVisible) => {
  if (isVisible && tags.value.length === 0) {
    initTags();
  }
});

onMounted(() => {
  if (showNavBar.value) {
    initTags();
  }
});

loadTheme();
</script>
