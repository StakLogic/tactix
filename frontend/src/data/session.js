import router from "@/router"
import { createResource } from "frappe-ui"
import { computed, reactive } from "vue"

import { userResource } from "./user"

export function sessionUser() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	let _sessionUser = cookies.get("user_id")
	if (_sessionUser === "Guest") {
		_sessionUser = null
	}
	return _sessionUser
}

export const session = reactive({
	login: createResource({
		url: "login",
		method: "POST",
		makeParams({ email, password }) {
			return {
				usr: email,
				pwd: password,
			}
		},
		onSuccess(data) {
			userResource.reload()
			session.userInfo.reset()
			session.user = sessionUser()
			session.login.reset()
			// router.replace(data.default_route || "/")
			window.location.href = "/tactix"
		},
	}),
	logout: createResource({
		url: "logout",
		method: "POST",
		onSuccess() {
			userResource.reset()
			session.userInfo.reset()
			session.user = sessionUser()
			router.replace({ name: "Login" })
		},
	}),
	userInfo: createResource({
		url: "tactix.api.generic.get_user_info",
		cache: ["userInfo", localStorage.getItem("current_team"), getSessionUser()],
		initialData: {
			owner: false,
			admin: false,
			is_ticket_raiser: false,
			tactix_customer: "",
			user_image: "",
		},
	}),
	isAdmin: computed(() => session.userInfo.data?.admin),
	isTicketRaiser: computed(() => session.userInfo.data?.is_ticket_raiser),
	isEmployee: computed(() => session.roles.includes("Employee") && !session.userInfo.data?.is_ticket_raiser),
	ticketCustomerId: computed(() => session.userInfo.data.tactix_customer),
	userImage: computed(() => session.userInfo.data.user_image),
	roles: computed(() => session.userInfo.data.roles || []),
	user: sessionUser(),
	userFullName: getSessionCookies().get("full_name") || "",
	isLoggedIn: computed(() => !!session.user),
})

export function getSessionUser() {
	const cookies = getSessionCookies()
	let sessionUser = cookies.get("user_id")
	if (!sessionUser || sessionUser === "Guest") {
		sessionUser = null
	}
	return sessionUser
}

function getSessionCookies() {
	return new URLSearchParams(document.cookie.split("; ").join("&"))
}
