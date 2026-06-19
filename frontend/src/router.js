import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"

const routes = [
	{
		path: "/account/login",
		name: "Login",
		component: () => import("@/pages/Login.vue"),
	},

	{
		path: "/",
		component: () => import("@/pages/Home.vue"),
		children: [
			{
				path: "",
				redirect: () => {
					if (session.isTicketRaiser) {
						return "/tickets"
					}
					return "/dashboard"
				},
			},

			{
				path: "dashboard",
				name: "Dashboard",
				component: () => import("@/pages/Dashboard.vue"),
			},

			{
				path: "tickets/:name?",
				name: "Tickets",
				component: () => import("@/pages/Ticket.vue"),
			},

			{
				path: "tasks/:name?",
				name: "Tasks",
				component: () => import("@/pages/Tasks.vue"),
			},

			{
				path: "leave-applications",
				name: "Leave Applications",
				component: () => import("@/pages/LeaveApplication.vue"),
			},

			{
				path: "timesheets",
				name: "Timesheets",
				component: () => import("@/pages/Timesheets.vue"),
			},

			{
				path: "performance",
				name: "Performance",
				component: () => import("@/pages/Performance.vue"),
			},

			{
				path: "data-sources",
				name: "DataSources",
				component: () => import("@/pages/DataSource.vue"),
			},

			{
				path: "users",
				name: "Users",
				component: () => import("@/pages/Users.vue"),
			},

			{
				path: "contributions",
				name: "Contributions",
				component: () => import("@/pages/Contributions.vue"),
			},
		],
	},
]

const router = createRouter({
	history: createWebHistory("/tactix/"),
	routes,
})

router.beforeEach(async (to, from, next) => {
	let isLoggedIn = session.isLoggedIn

	if (isLoggedIn) {
		try {
			await userResource.promise

			// Only fetch user info if not already loaded to prevent redundant network requests on every navigation
			if (!session.userInfo.fetched) {
				await session.userInfo.fetch()
			}
		} catch (error) {
			isLoggedIn = false
		}
	}

	if (to.name === "Login" && isLoggedIn) {
		if (session.isTicketRaiser) {
			next("/tickets")
		} else {
			next("/dashboard")
		}
		return
	}

	if (to.name !== "Login" && !isLoggedIn) {
		next({ name: "Login" })
		return
	}

	// prevent ticket raiser accessing dashboard
	if (session.isTicketRaiser && to.path === "/dashboard") {
		next("/tickets")
		return
	}

	next()
})

export default router
