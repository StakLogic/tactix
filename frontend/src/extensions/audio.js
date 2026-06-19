import { Node, mergeAttributes } from "@tiptap/core"
import { VueNodeViewRenderer } from "@tiptap/vue-3"
import AudioPlayer from "../components/AudioPlayer.vue"

export const AudioExtension = Node.create({
	name: "audio",
	group: "block",
	selectable: true,
	draggable: true,
	atom: true,

	addAttributes() {
		return {
			src: {
				default: null,
			},
			controls: {
				default: true,
			},
		}
	},

	parseHTML() {
		return [
			{
				tag: "audio",
				getAttrs: (node) => {
					if (typeof node === "string") return {}
					return {
						src: node.getAttribute("src"),
					}
				},
			},
		]
	},

	renderHTML({ HTMLAttributes }) {
		return [
			"audio",
			mergeAttributes(HTMLAttributes, {
				controls: "",
				class:
					"my-2 outline-none border border-slate-200/60 rounded-full shadow-sm bg-slate-50 p-0.5",
				style: "display: block; max-width: 260px; height: 36px;",
			}),
		]
	},

	addNodeView() {
		return VueNodeViewRenderer(AudioPlayer)
	},
})
