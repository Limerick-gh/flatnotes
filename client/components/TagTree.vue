<template>
  <ul class="space-y-1">
    <li v-for="node in nodes" :key="node.tag">
      <div class="flex items-center">
        <button
          v-if="node.children.length > 0"
          type="button"
          class="mr-1 flex h-7 w-7 shrink-0 items-center justify-center rounded text-theme-text-muted hover:bg-theme-background-elevated hover:text-theme-text"
          :aria-label="node.expanded ? 'Collapse tag' : 'Expand tag'"
          @click="node.expanded = !node.expanded"
        >
          <SvgIcon
            type="mdi"
            :path="node.expanded ? mdiChevronDown : mdiChevronRight"
            size="1em"
          />
        </button>
        <span v-else class="mr-1 h-7 w-7 shrink-0"></span>
        <RouterLink
          :to="{ name: 'search', query: { term: node.searchTerm } }"
          class="min-w-0 flex-1 truncate rounded px-2 py-1 text-base text-theme-text-muted hover:bg-theme-background-elevated hover:text-theme-text"
        >
          #{{ node.tag }}
        </RouterLink>
      </div>
      <TagTree
        v-if="node.expanded && node.children.length > 0"
        :nodes="node.children"
        class="ml-5 border-l border-theme-border pl-2"
      />
    </li>
  </ul>
</template>

<script setup>
import SvgIcon from "@jamescoyle/vue-icon";
import { mdiChevronDown, mdiChevronRight } from "@mdi/js";
import { RouterLink } from "vue-router";

defineProps({
  nodes: {
    type: Array,
    required: true,
  },
});
</script>
