import frappeUIPreset from "frappe-ui/tailwind"

export default {
	presets: [frappeUIPreset],
	content: [
		"./index.html",
		"./src/**/*.{vue,js,ts,jsx,tsx}",
		"./node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}",
		"../node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}",
	],
	plugins: [],
	theme: {
		extend: {
			colors: {
				blue: {
					50: 'var(--primary-color-shadow-light)',
					100: 'var(--primary-color-shadow-light)',
					200: 'var(--primary-color-shadow)',
					300: 'var(--primary-color-shadow)',
					400: 'var(--primary-color)',
					500: 'var(--primary-color)',
					600: 'var(--primary-color)',
					700: 'var(--primary-color-hover)',
					800: 'var(--primary-color-hover)',
					900: 'var(--primary-color-hover)',
					950: 'var(--primary-color-hover)',
				}
			}
		},
	},
}
