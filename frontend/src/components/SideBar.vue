<script setup lang="ts">
import { Sidebar } from "frappe-ui"
import { computed } from "vue"
import { useRoute, useRouter } from "vue-router"

import BarChart3 from "~icons/lucide/bar-chart-3"
import CheckSquare from "~icons/lucide/check-square"
import Clock from "~icons/lucide/clock"
import Database from "~icons/lucide/database"
import FolderOpen from "~icons/lucide/folder-open"
import GitPullRequest from "~icons/lucide/git-pull-request"
// Icons
import LayoutDashboard from "~icons/lucide/layout-dashboard"
import LogOut from "~icons/lucide/log-out"
import Moon from "~icons/lucide/moon"
import Settings from "~icons/lucide/settings"
import Ticket from "~icons/lucide/ticket"
import Users from "~icons/lucide/users"
import { session } from "../data/session"

const route = useRoute()
const router = useRouter()

// Correct Role Logic
const isAdmin = session.isAdmin
const isTicketRaiser = session.isTicketRaiser
const isEmployee = session.isEmployee

function toggleTheme() {
	const currentTheme = document.documentElement.getAttribute("data-theme")
	const newTheme = currentTheme === "dark" ? "light" : "dark"
	document.documentElement.setAttribute("data-theme", newTheme)
}

const navigateTo = (path: string) => {
	if (route.path !== path) {
		router.push(path)
	}
}

const crmSidebar = computed(() => {
	// 1. Build Header Menu Items (Dropdown menu on user profile)
	const menuItems = [
		{ label: "Toggle Theme", icon: Moon, onClick: toggleTheme },
		{
			label: "Settings",
			icon: Settings,
			to: "/settings",
			onClick: () => navigateTo("/settings"),
		},
	]

	if (isAdmin) {
		menuItems.push({
			label: "Switch to Desk",
			icon: Database,
			onClick: () => {
				window.location.href = "/app"
			},
		})
	}

	menuItems.push({
		label: "Logout",
		icon: LogOut,
		onClick: () => session.logout.submit(),
	})

	// 2. Build Sidebar Navigation Sections
	let sidebarItems: any[] = []

	if (isTicketRaiser && !isAdmin) {
		// TIER 1: Ticket Raiser only sees Tickets
		sidebarItems = [
			{
				label: "Tickets",
				icon: Ticket,
				to: "/tickets",
				onClick: () => navigateTo("/tickets"),
				isActive: route.path === "/tickets",
			},
		]
	} else if (isEmployee || isAdmin) {
		// TIER 2: Standard Employee / Admin items
		sidebarItems = [
			{
				label: "Dashboard",
				icon: LayoutDashboard,
				to: "/dashboard",
				onClick: () => navigateTo("/dashboard"),
				isActive: route.path === "/dashboard",
			},
			{
				label: "Tasks",
				icon: CheckSquare,
				to: "/tasks",
				onClick: () => navigateTo("/tasks"),
				isActive: route.path === "/tasks",
			},
			{
				label: "Tickets",
				icon: Ticket,
				to: "/tickets",
				onClick: () => navigateTo("/tickets"),
				isActive: route.path === "/tickets",
			},
			{
				label: "Contributions",
				icon: GitPullRequest,
				to: "/contributions",
				onClick: () => navigateTo("/contributions"),
				isActive: route.path === "/contributions",
			},
			{
				label: "Drive",
				icon: FolderOpen,
				to: "/drive",
				onClick: () => navigateTo("/drive"),
				isActive: route.path === "/drive" || route.path.startsWith("/drive/"),
			},
			{
				label: "Timesheets",
				icon: Clock,
				to: "/timesheets",
				onClick: () => navigateTo("/timesheets"),
				isActive: route.path === "/timesheets",
			},
			{
				label: "Performance",
				icon: BarChart3,
				to: "/performance",
				onClick: () => navigateTo("/performance"),
				isActive: route.path === "/performance",
			},
		]

		// TIER 3: Admin additional items
		if (isAdmin) {
			sidebarItems.push(
				{
					label: "Data Sources",
					icon: Database,
					to: "/data-sources",
					onClick: () => navigateTo("/data-sources"),
					isActive: route.path === "/data-sources",
				},
				{
					label: "Users",
					icon: Users,
					to: "/users",
					onClick: () => navigateTo("/users"),
					isActive: route.path === "/users",
				},
			)
		}
	}

	return {
		header: {
			title: "Tactix",
			subtitle: session.userFullName || session.user || undefined,
			logo: "/assets/tactix/frontend/tactix_icon.png",
			menuItems: menuItems,
		},
		sections: [
			{
				label: "",
				items: sidebarItems,
			},
		],
	}
})
</script>

<template>
	<div class="h-screen flex bg-slate-50 border-r border-slate-200">
		<Sidebar 
			:header="crmSidebar.header" 
			:sections="crmSidebar.sections"
			class="!bg-white"
		/>
	</div>
</template>

<style scoped>
:deep(nav button) {
  border-radius: 12px !important;
  transition: all 0.2s ease;
}

:deep(nav button.\!bg-surface-selected),
:deep(nav button.bg-surface-selected) {
  background-color: #061d43 !important;
  font-weight: 700 !important;
  box-shadow: 0 4px 6px -1px #061d4333, 0 2px 4px -2px #061d4320 !important;
}

:deep(nav button.\!bg-surface-selected span),
:deep(nav button.bg-surface-selected span) {
  color: #ffffff !important;
  font-weight: 700 !important;
}

:deep(nav button.\!bg-surface-selected svg),
:deep(nav button.bg-surface-selected svg) {
  color: #ffffff !important;
}
</style>