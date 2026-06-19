import path from "node:path"
import vue from "@vitejs/plugin-vue"
import frappeui from "frappe-ui/vite"
import AutoImport from "unplugin-auto-import/vite"
import Icons from "unplugin-icons/vite"
import { defineConfig } from "vite"

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [
		frappeui({
			frappeProxy: true,
			jinjaBootData: true,
			lucideIcons: true,
			buildConfig: {
				outDir: "../tactix/public/frontend",
				indexHtmlPath: "../tactix/www/tactix.html",
				emptyOutDir: true,
				sourcemap: true,
			},
		}),
		vue(),

		AutoImport({
			imports: ["vue"],
			dts: true,
		}),

		Icons({
			autoInstall: true,
		}),
	],
	build: {
		chunkSizeWarningLimit: 1500,
		outDir: "../tactix/public/frontend",
		emptyOutDir: true,
		target: "es2015",
		sourcemap: true,
	},
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "src"),
			"tailwind.config.js": path.resolve(__dirname, "tailwind.config.js"),
		},
	},
	optimizeDeps: {
		include: [
			"feather-icons",
			"showdown",
			"highlight.js/lib/core",
			"interactjs",
			"prosemirror-state",
			"prosemirror-transform",
			"prosemirror-model",
			"prosemirror-view",
		],
	},
	server: {
		allowedHosts: true,
	},
})
