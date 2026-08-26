<template>
  <div ref="editorElement" class="relative">
    <div
      v-if="tagMenuVisible"
      class="absolute left-2 top-12 z-10 max-h-64 w-64 overflow-y-auto rounded-md border border-theme-border bg-theme-background p-1 shadow-lg"
    >
      <button
        v-for="(tag, index) in tagMatches"
        :key="tag"
        type="button"
        class="block w-full truncate rounded px-2 py-1 text-left text-sm hover:bg-theme-background-elevated"
        :class="{ 'bg-theme-background-elevated': index === tagMenuIndex }"
        @mousedown.prevent="tagChosen(tag)"
      >
        {{ tag }}
      </button>
    </div>
  </div>
</template>

<script setup>
import Editor from "@toast-ui/editor";
import { useToast } from "primevue/usetoast";
import { onMounted, ref } from "vue";

import { apiErrorHandler, getTags } from "../../api.js";
import baseOptions from "./baseOptions.js";

const props = defineProps({
  initialValue: String,
  initialEditType: {
    type: String,
    default: "markdown",
  },
  addImageBlobHook: Function,
});

const emit = defineEmits(["change", "keydown"]);

const editorElement = ref();
const tagMatches = ref([]);
const tagMenuIndex = ref(0);
const tagMenuVisible = ref(false);
const toast = useToast();
let tags = [];
let toastEditor;

onMounted(() => {
  toastEditor = new Editor({
    ...baseOptions,
    el: editorElement.value,
    initialValue: props.initialValue,
    initialEditType: props.initialEditType,
    events: {
      change: () => {
        emit("change");
      },
      keydown: (_, event) => {
        if (tagMenuVisible.value) {
          if (event.key === "ArrowDown") {
            event.preventDefault();
            tagMenuIndex.value = Math.min(
              tagMenuIndex.value + 1,
              tagMatches.value.length - 1,
            );
            return;
          }
          if (event.key === "ArrowUp") {
            event.preventDefault();
            tagMenuIndex.value = Math.max(tagMenuIndex.value - 1, 0);
            return;
          }
          if (event.key === "Enter" || event.key === "Tab") {
            event.preventDefault();
            tagChosen(tagMatches.value[tagMenuIndex.value]);
            return;
          }
          if (event.key === "Escape") {
            tagMenuVisible.value = false;
            return;
          }
        }
        emit("keydown", event);
      },
    },
    hooks: props.addImageBlobHook
      ? { addImageBlobHook: props.addImageBlobHook }
      : {},
  });
  editorElement.value.addEventListener("keyup", updateTagMatches);
});

async function updateTagMatches() {
  const word = getWordAtCursor();
  if (!word.startsWith("#")) {
    tagMenuVisible.value = false;
    return;
  }
  if (tags.length === 0) {
    try {
      tags = (await getTags()).map((tag) => `#${tag}`);
    } catch (error) {
      apiErrorHandler(error, toast);
      return;
    }
  }
  tagMatches.value = tags.filter(
    (tag) => tag.startsWith(word.toLowerCase()) && tag !== word.toLowerCase(),
  );
  tagMenuIndex.value = 0;
  tagMenuVisible.value = tagMatches.value.length > 0;
}

function getWordAtCursor() {
  const activeElement = document.activeElement;
  if (
    activeElement instanceof HTMLTextAreaElement ||
    activeElement instanceof HTMLInputElement
  ) {
    const beforeCursor = activeElement.value.substring(
      0,
      activeElement.selectionStart,
    );
    return beforeCursor.substring(beforeCursor.lastIndexOf(" ") + 1);
  }
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) {
    return "";
  }
  const range = selection.getRangeAt(0);
  if (!range.collapsed || !editorElement.value.contains(range.startContainer)) {
    return "";
  }
  const text = range.startContainer.textContent || "";
  const beforeCursor = text.substring(0, range.startOffset);
  return beforeCursor.substring(beforeCursor.lastIndexOf(" ") + 1);
}

function tagChosen(tag) {
  const word = getWordAtCursor();
  const suffix = tag.substring(word.length);
  if (suffix) {
    toastEditor.insertText(suffix);
  }
  tagMenuVisible.value = false;
}

function getMarkdown() {
  return toastEditor.getMarkdown();
}

function isWysiwygMode() {
  return toastEditor.isWysiwygMode();
}

defineExpose({ getMarkdown, isWysiwygMode });
</script>

<style>
@import "@toast-ui/editor/dist/toastui-editor.css";
@import "prismjs/themes/prism.css";
@import "@toast-ui/editor-plugin-code-syntax-highlight/dist/toastui-editor-plugin-code-syntax-highlight.css";
@import "./toastui-editor-overrides.scss";
</style>
