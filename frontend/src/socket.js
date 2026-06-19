import { getCachedListResource, getCachedResource } from "frappe-ui"
import { io } from "socket.io-client"
import { socketio_port } from "../../../../sites/common_site_config.json"

let socket = null

export function getSiteName() {
	// 1. Try window.site_name or window.sitename
	const name = window.site_name || window.sitename
	if (name) return name

	// 2. Guess from hostname if not localhost or 127.0.0.1
	const hostname = window.location.hostname
	if (hostname && hostname !== "localhost" && hostname !== "127.0.0.1") {
		return hostname
	}

	// 3. Fallback for local development
	return "tactix.localhost"
}

export function initSocket() {
	const host = window.location.hostname
	const siteName = getSiteName()
	const isLocal = window.location.port !== ""
	const port = isLocal ? `:${socketio_port}` : ""
	const protocol = isLocal ? "http" : "https"
	const url = `${protocol}://${host}${port}/${siteName}`

	socket = io(url, {
		withCredentials: true,
		reconnectionAttempts: 5,
		transports: ["websocket", "polling"],
	})

	socket.on("refetch_resource", (data) => {
		if (data.cache_key) {
			const resource =
				getCachedResource(data.cache_key) ||
				getCachedListResource(data.cache_key)
			if (resource) {
				resource.reload()
			}
		}
	})

	return socket
}

export function useSocket() {
	if (!socket) {
		initSocket()
	}
	return socket
}
