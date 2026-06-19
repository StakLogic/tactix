<template>
  <div ref="containerRef" class="w-full transition-all duration-300">
    <!-- Collapsed View (Screenshot 1) -->
    <div 
      v-if="!isExpanded" 
      @click.stop="expandEditor"
      class="flex items-center gap-3 p-3 bg-slate-50 hover:bg-slate-100/80 border border-slate-200/60 rounded-full cursor-pointer transition-all duration-200 select-none shadow-sm shadow-slate-100/50"
    >
      <Avatar 
        :image="avatar" 
        :label="user" 
        size="sm" 
        class="shrink-0 font-bold border-2 border-white shadow-sm" 
      />
      <span class="text-slate-400 text-xs font-medium tracking-wide">
        {{ placeholder }}
      </span>
    </div>

    <!-- Expanded View (Screenshot 2) -->
    <div 
      v-else 
      class="bg-white border border-slate-200/80 rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.05)] overflow-hidden transition-all duration-300 transform scale-100 flex flex-col"
    >
      <!-- Header -->
      <div class="px-4 py-3 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <Avatar 
            :image="avatar" 
            :label="user" 
            size="sm" 
            class="font-bold border-2 border-white shadow-sm shrink-0" 
          />
          <span class="text-xs font-bold text-slate-700 tracking-wide">{{ userName || user }}</span>
        </div>
        <button 
          @click.stop="collapseEditorIfEmpty"
          class="text-[10px] font-bold text-slate-400 hover:text-slate-600 transition-colors uppercase tracking-wider"
        >
          Minimize
        </button>
      </div>

      <!-- Editor Body -->
      <div class="flex-1 min-h-[120px] bg-white relative">
        <TextEditor
          ref="editorRef"
          editor-class="prose-sm p-4 outline-none min-h-[100px] max-w-none text-slate-600 bg-white"
          :content="modelValue"
          @change="updateContent"
          :fixed-menu="false"
          :bubbleMenu="true"
          :placeholder="placeholder"
        />
      </div>

      <!-- Footer / Toolbar -->
      <div class="px-4 py-3 border-t border-slate-100 bg-slate-50/80 flex items-center justify-between flex-wrap gap-3">
        <!-- Formatting Tools (Bottom Left) -->
        <div class="flex items-center gap-1.5 flex-wrap">
          <button @click="triggerAttachment" class="tool-btn" type="button" title="Add attachment">
            <IconPaperclip class="w-4 h-4 text-slate-400 hover:text-slate-600" />
          </button>
          
          <div class="w-[1px] h-4 bg-slate-200 mx-1"></div>

          <button @click="toggleFormat('heading', { level: 2 })" class="tool-btn" type="button" title="Heading 2" :class="{ 'active-tool': isFormatActive('heading', { level: 2 }) }">
            <span class="text-slate-400 hover:text-slate-600 font-black text-xs">H₂</span>
          </button>
          <button @click="toggleFormat('bold')" class="tool-btn" type="button" title="Bold" :class="{ 'active-tool': isFormatActive('bold') }">
            <IconBold class="w-4 h-4 text-slate-400 hover:text-slate-600" />
          </button>
          <button @click="toggleFormat('italic')" class="tool-btn" type="button" title="Italic" :class="{ 'active-tool': isFormatActive('italic') }">
            <IconItalic class="w-4 h-4 text-slate-400 hover:text-slate-600" />
          </button>
          
          <div class="w-[1px] h-4 bg-slate-200 mx-1"></div>

          <button @click="toggleFormat('bulletList')" class="tool-btn" type="button" title="Bulleted List" :class="{ 'active-tool': isFormatActive('bulletList') }">
            <IconList class="w-4 h-4 text-slate-400 hover:text-slate-600" />
          </button>
          <button @click="toggleFormat('orderedList')" class="tool-btn" type="button" title="Numbered List" :class="{ 'active-tool': isFormatActive('orderedList') }">
            <IconListOrdered class="w-4 h-4 text-slate-400 hover:text-slate-600" />
          </button>

          <button @click="insertImage" class="tool-btn" type="button" title="Insert Image">
            <IconImage class="w-4 h-4 text-slate-400 hover:text-slate-600" />
          </button>
          <button @click="insertVideo" class="tool-btn" type="button" title="Insert Video">
            <IconVideo class="w-4 h-4 text-slate-400 hover:text-slate-600" />
          </button>
          <button @click="insertLink" class="tool-btn" type="button" title="Insert Link" :class="{ 'active-tool': isFormatActive('link') }">
            <IconLink class="w-4 h-4 text-slate-400 hover:text-slate-600" />
          </button>
          <button @click="toggleFormat('blockquote')" class="tool-btn" type="button" title="Quote" :class="{ 'active-tool': isFormatActive('blockquote') }">
            <IconQuote class="w-4 h-4 text-slate-400 hover:text-slate-600" />
          </button>
          <button @click="toggleFormat('codeBlock')" class="tool-btn" type="button" title="Code Block" :class="{ 'active-tool': isFormatActive('codeBlock') }">
            <IconCode class="w-4 h-4 text-slate-400 hover:text-slate-600" />
          </button>
          <button @click="clearFormatting" class="tool-btn" type="button" title="Clear Formatting">
            <IconEraser class="w-4 h-4 text-slate-400 hover:text-slate-600" />
          </button>
        </div>

        <!-- Post Action (Bottom Right) -->
        <div class="flex items-center gap-3 ml-auto">
          <span class="text-[10px] text-slate-400 font-medium hidden sm:inline-block">
            Press Ctrl + Enter to post
          </span>
          <Button 
            size="sm" 
            variant="solid" 
            @click="submitComment" 
            class="!px-5 !h-8 !text-xs !bg-blue-600 hover:!bg-blue-700 transition-colors shadow-sm text-white font-bold"
            :loading="loading"
            :disabled="!modelValue || modelValue.trim() === '' || modelValue === '<p></p>'"
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Avatar, Button, TextEditor } from "frappe-ui"
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue"

import IconBold from "~icons/lucide/bold"
import IconCode from "~icons/lucide/code"
import IconEraser from "~icons/lucide/eraser"
import IconImage from "~icons/lucide/image"
import IconItalic from "~icons/lucide/italic"
import IconLink from "~icons/lucide/link"
import IconList from "~icons/lucide/list"
import IconListOrdered from "~icons/lucide/list-ordered"
// Import Icons
import IconPaperclip from "~icons/lucide/paperclip"
import IconQuote from "~icons/lucide/quote"
import IconVideo from "~icons/lucide/video"

const props = defineProps({
	modelValue: {
		type: String,
		default: "",
	},
	placeholder: {
		type: String,
		default: "Type a message",
	},
	loading: {
		type: Boolean,
		default: false,
	},
	avatar: {
		type: String,
		default: "",
	},
	user: {
		type: String,
		required: true,
	},
	userName: {
		type: String,
		default: "",
	},
})

const emit = defineEmits(["update:modelValue", "submit"])

const isExpanded = ref(false)
const editorRef = ref(null)
const containerRef = ref(null)

function expandEditor() {
	isExpanded.value = true
	nextTick(() => {
		try {
			if (editorRef.value?.editor) {
				editorRef.value.editor.commands.focus()
			} else {
				setTimeout(() => {
					if (editorRef.value?.editor) {
						editorRef.value.editor.commands.focus()
					}
				}, 50)
			}
		} catch (e) {
			console.warn("Could not programmatically focus editor", e)
		}
	})
}

function updateContent(val) {
	emit("update:modelValue", val)
}

function submitComment() {
	if (
		props.modelValue &&
		props.modelValue.trim() !== "" &&
		props.modelValue !== "<p></p>"
	) {
		emit("submit")
		nextTick(() => {
			// Auto-collapse after posting comment
			isExpanded.value = false
		})
	}
}

function collapseEditorIfEmpty() {
	if (
		!props.modelValue ||
		props.modelValue.trim() === "" ||
		props.modelValue === "<p></p>"
	) {
		isExpanded.value = false
	}
}

// Click outside mechanism
function handleClickOutside(event) {
	if (containerRef.value && !containerRef.value.contains(event.target)) {
		collapseEditorIfEmpty()
	}
}

// Keyboard shortcuts (Ctrl+Enter / Cmd+Enter to Send)
function handleKeyDown(event) {
	if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
		event.preventDefault()
		submitComment()
	}
}

onMounted(() => {
	document.addEventListener("click", handleClickOutside)
	document.addEventListener("keydown", handleKeyDown)
})

onBeforeUnmount(() => {
	document.removeEventListener("click", handleClickOutside)
	document.removeEventListener("keydown", handleKeyDown)
})

// Tiptap Command Helpers
function getEditor() {
	return editorRef.value?.editor
}

function toggleFormat(type, options = {}) {
	const editor = getEditor()
	if (!editor) return

	if (type === "heading") {
		editor.chain().focus().toggleHeading(options).run()
	} else if (type === "bold") {
		editor.chain().focus().toggleBold().run()
	} else if (type === "italic") {
		editor.chain().focus().toggleItalic().run()
	} else if (type === "bulletList") {
		editor.chain().focus().toggleBulletList().run()
	} else if (type === "orderedList") {
		editor.chain().focus().toggleOrderedList().run()
	} else if (type === "blockquote") {
		editor.chain().focus().toggleBlockquote().run()
	} else if (type === "codeBlock") {
		editor.chain().focus().toggleCodeBlock().run()
	}
}

function isFormatActive(type, options = {}) {
	const editor = getEditor()
	if (!editor) return false
	return editor.isActive(type, options)
}

function clearFormatting() {
	const editor = getEditor()
	if (!editor) return
	editor.chain().focus().unsetAllMarks().clearNodes().run()
}

function insertLink() {
	const editor = getEditor()
	if (!editor) return

	const previousUrl = editor.getAttributes("link").href
	const url = window.prompt("Enter URL:", previousUrl)

	// cancelled
	if (url === null) return

	// empty, remove link
	if (url === "") {
		editor.chain().focus().extendMarkRange("link").unsetLink().run()
		return
	}

	editor.chain().focus().extendMarkRange("link").setLink({ href: url }).run()
}

function insertImage() {
	const editor = getEditor()
	if (!editor) return
	const url = window.prompt("Enter Image URL:")
	if (url) {
		editor.chain().focus().setImage({ src: url }).run()
	}
}

function insertVideo() {
	const editor = getEditor()
	if (!editor) return
	const url = window.prompt("Enter Video URL (YouTube, Vimeo, etc.):")
	if (url) {
		// Tiptap has setVideo or we can use custom iframes if supported
		if (editor.commands.setVideo) {
			editor.commands.setVideo({ src: url })
		} else {
			editor
				.chain()
				.focus()
				.insertContent(
					`<video src="${url}" controls class="w-full rounded-lg my-3"></video>`,
				)
				.run()
		}
	}
}

function triggerAttachment() {
	const editor = getEditor()
	if (!editor) return
	// Show a standard file upload alert or prompt for simple link.
	// In Frappe apps, files are typically uploaded in sidebars, so we can insert a download link
	const url = window.prompt("Enter Attachment URL or Link:")
	if (url) {
		const text = window.prompt("Enter link label:", "Attachment")
		editor
			.chain()
			.focus()
			.insertContent(
				`<a href="${url}" target="_blank" class="text-blue-600 font-semibold underline">${text || "Attachment"}</a> `,
			)
			.run()
	}
}
</script>

<style scoped>
.tool-btn {
  padding: 0.375rem;
  border-radius: 0.375rem;
  border: 1px solid transparent;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  cursor: pointer;
  background-color: transparent;
}

.tool-btn:hover {
  background-color: #f1f5f9;
  border-color: #cbd5e1;
}

.active-tool {
  background-color: #e2e8f0 !important;
  border-color: #cbd5e1 !important;
}

.active-tool svg {
  color: #2563eb !important;
}
</style>
