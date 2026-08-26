<template>
  <div class="mx-auto max-w-[700px]">
    <div class="mb-5 flex items-center justify-between">
      <h1 class="text-xl font-semibold">Tag Hierarchy</h1>
      <CustomButton
        :label="saving ? 'Saving...' : 'Save'"
        :iconPath="mdilContentSave"
        :disabled="saving"
        @click="save"
      />
    </div>

    <p class="mb-5 text-sm text-theme-text-muted">
      Organize tags into parent-child groups. Selecting a parent searches all of
      its descendants.
    </p>

    <LoadingIndicator ref="loadingIndicator">
      <div class="mb-5 rounded border border-theme-border p-3">
        <div class="mb-2 text-sm font-semibold">Add relationship</div>
        <div class="flex flex-col gap-2 sm:flex-row">
          <select v-model="newParent" class="min-w-0 flex-1 rounded border border-theme-border bg-theme-background px-2 py-2">
            <option value="">Select parent</option>
            <option v-for="tag in configuredTags" :key="`parent-${tag}`" :value="tag">{{ tag }}</option>
          </select>
          <select v-model="newChild" class="min-w-0 flex-1 rounded border border-theme-border bg-theme-background px-2 py-2">
            <option value="">Select child</option>
            <option v-for="tag in configuredTags" :key="`child-${tag}`" :value="tag">{{ tag }}</option>
          </select>
          <CustomButton label="Add" :disabled="!canAdd" @click="addRelationship" />
        </div>
      </div>

      <div v-if="rows.length > 0" class="space-y-2">
        <div
          v-for="row in rows"
          :key="row.id"
          class="flex flex-col gap-2 rounded border border-theme-border p-3 sm:flex-row sm:items-center"
        >
          <select v-model="row.parent" class="min-w-0 flex-1 rounded border border-theme-border bg-theme-background px-2 py-2">
            <option v-for="tag in configuredTags" :key="`row-parent-${row.id}-${tag}`" :value="tag">{{ tag }}</option>
          </select>
          <span class="text-center text-theme-text-muted">&rarr;</span>
          <select v-model="row.child" class="min-w-0 flex-1 rounded border border-theme-border bg-theme-background px-2 py-2">
            <option v-for="tag in configuredTags" :key="`row-child-${row.id}-${tag}`" :value="tag">{{ tag }}</option>
          </select>
          <CustomButton label="Remove" :iconPath="mdilDelete" @click="removeRelationship(row.id)" />
        </div>
      </div>
      <p v-else class="text-sm text-theme-text-muted">No relationships configured.</p>
    </LoadingIndicator>
  </div>
</template>

<script setup>
import { mdilContentSave, mdilDelete } from "@mdi/light-js";
import { useToast } from "primevue/usetoast";
import { computed, onMounted, ref } from "vue";

import { apiErrorHandler, getTags, updateTagHierarchy } from "../api.js";
import CustomButton from "../components/CustomButton.vue";
import LoadingIndicator from "../components/LoadingIndicator.vue";
import { useGlobalStore } from "../globalStore.js";
import { getToastOptions } from "../helpers.js";

const globalStore = useGlobalStore();
const loadingIndicator = ref();
const rows = ref([]);
const tags = ref([]);
const newParent = ref("");
const newChild = ref("");
const saving = ref(false);
const toast = useToast();
let nextId = 0;

const canAdd = computed(() => newParent.value && newChild.value && newParent.value !== newChild.value);

const configuredTags = computed(() => [...new Set([
  ...tags.value,
  ...Object.keys(globalStore.config.tagHierarchy || {}),
  ...Object.values(globalStore.config.tagHierarchy || {}).flat(),
])].sort());

function loadRows(hierarchy) {
  rows.value = Object.entries(hierarchy || {}).flatMap(([parent, children]) =>
    children.map((child) => ({ id: nextId++, parent, child })),
  );
}

function addRelationship() {
  if (!canAdd.value || rows.value.some((row) => row.parent === newParent.value && row.child === newChild.value)) {
    return;
  }
  rows.value.push({ id: nextId++, parent: newParent.value, child: newChild.value });
  newParent.value = "";
  newChild.value = "";
}

function removeRelationship(id) {
  rows.value = rows.value.filter((row) => row.id !== id);
}

function hierarchyFromRows() {
  return rows.value.reduce((hierarchy, row) => {
    if (!hierarchy[row.parent]) {
      hierarchy[row.parent] = [];
    }
    if (!hierarchy[row.parent].includes(row.child)) {
      hierarchy[row.parent].push(row.child);
    }
    return hierarchy;
  }, {});
}

function save() {
  saving.value = true;
  updateTagHierarchy(hierarchyFromRows())
    .then((hierarchy) => {
      globalStore.config.tagHierarchy = hierarchy;
      toast.add(getToastOptions("Tag hierarchy saved.", "Saved", "success"));
    })
    .catch((error) => apiErrorHandler(error, toast))
    .finally(() => {
      saving.value = false;
    });
}

onMounted(() => {
  getTags()
    .then((data) => {
      tags.value = data;
      loadRows(globalStore.config.tagHierarchy);
      loadingIndicator.value.setLoaded();
    })
    .catch((error) => {
      loadingIndicator.value.setFailed();
      apiErrorHandler(error, toast);
    });
});
</script>
