<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch, type Component } from "vue"
import { useRoute, useRouter } from "vue-router"

// Icons
import BarChart3 from "~icons/lucide/bar-chart-3"
import CheckSquare from "~icons/lucide/check-square"
import ChevronsUpDown from "~icons/lucide/chevrons-up-down"
import Clock from "~icons/lucide/clock"
import Database from "~icons/lucide/database"
import ExternalLink from "~icons/lucide/external-link"
import FolderOpen from "~icons/lucide/folder-open"
import GitPullRequest from "~icons/lucide/git-pull-request"
import LayoutDashboard from "~icons/lucide/layout-dashboard"
import LogOut from "~icons/lucide/log-out"
import Moon from "~icons/lucide/moon"
import PanelLeftClose from "~icons/lucide/panel-left-close"
import PanelLeftOpen from "~icons/lucide/panel-left-open"
import Settings from "~icons/lucide/settings"
import Sun from "~icons/lucide/sun"
import Ticket from "~icons/lucide/ticket"
import Users from "~icons/lucide/users"
import { session } from "../data/session"

type NavItem = { label: string; icon: Component; to: string }
type NavSection = { label: string; items: NavItem[] }
type MenuItem = { label: string; icon: Component; onClick: () => void; danger?: boolean; divider?: boolean }

const APP_TITLE = "Tactix"
const LOGO = "/assets/tactix/frontend/tactix_logo_highlighted.png"
const COLLAPSE_KEY = "tactix.sidebar.collapsed"

const route = useRoute()
const router = useRouter()

// Roles (same logic as before)
const isAdmin = computed(() => session.isAdmin)
const isTicketRaiser = computed(() => session.isTicketRaiser)
const isEmployee = computed(() => session.isEmployee)

const roleLabel = computed(() => {
	if (isAdmin.value) return "Administrator"
	if (isEmployee.value) return "Employee"
	if (isTicketRaiser.value) return "Ticket Raiser"
	return "Workspace"
})

const userName = computed(() => session.userFullName || session.user || "User")
const userEmail = computed(() => (session.user && session.user !== userName.value ? session.user : ""))
const initials = computed(() => {
	const parts = String(userName.value).trim().split(/\s+/).filter(Boolean)
	const letters = parts.length > 1 ? parts[0][0] + parts[parts.length - 1][0] : (parts[0] || "U").slice(0, 2)
	return letters.toUpperCase()
})

/* ---------------- Navigation ---------------- */
const sections = computed<NavSection[]>(() => {
	// Ticket Raiser only sees Tickets
	if (isTicketRaiser.value && !isAdmin.value) {
		return [{ label: "", items: [{ label: "Tickets", icon: Ticket, to: "/tickets" }] }]
	}

	if (!isEmployee.value && !isAdmin.value) return []

	const list: NavSection[] = [
		{
			label: "",
			items: [
				{ label: "Dashboard", icon: LayoutDashboard, to: "/dashboard" },
				{ label: "Tasks", icon: CheckSquare, to: "/tasks" },
				{ label: "Tickets", icon: Ticket, to: "/tickets" },
			],
		},
		{
			label: "Workspace",
			items: [
				{ label: "Contributions", icon: GitPullRequest, to: "/contributions" },
				{ label: "Drive", icon: FolderOpen, to: "/drive" },
			],
		},
		{
			label: "Time & Insights",
			items: [
				{ label: "Timesheets", icon: Clock, to: "/timesheets" },
				{ label: "Performance", icon: BarChart3, to: "/performance" },
			],
		},
	]

	if (isAdmin.value) {
		list.push({
			label: "Administration",
			items: [
				{ label: "Data Sources", icon: Database, to: "/data-sources" },
				{ label: "Users", icon: Users, to: "/users" },
			],
		})
	}
	return list
})

const homePath = computed(() => sections.value[0]?.items[0]?.to || "/")

// Active on the page itself and on its sub-pages (/tasks/123, /drive/folder/...)
function isActive(to: string) {
	return route.path === to || route.path.startsWith(to + "/")
}

function navigateTo(path: string) {
	if (route.path !== path) router.push(path)
}

/* ---------------- Theme ---------------- */
const isDark = ref(false)

function readTheme() {
	isDark.value = document.documentElement.getAttribute("data-theme") === "dark"
}

function toggleTheme() {
	const newTheme = isDark.value ? "light" : "dark"
	document.documentElement.setAttribute("data-theme", newTheme)
	document.documentElement.classList.toggle("dark", newTheme === "dark")
	try {
		localStorage.setItem("theme", newTheme)
	} catch {}
	isDark.value = newTheme === "dark"
}

/* ---------------- Account menu ---------------- */
const menuOpen = ref(false)
const menuWrap = ref<HTMLElement | null>(null)

const menuItems = computed<MenuItem[]>(() => {
	const items: MenuItem[] = [
		{ label: isDark.value ? "Light mode" : "Dark mode", icon: isDark.value ? Sun : Moon, onClick: toggleTheme },
	]
	if (isAdmin.value) {
		items.push(
			{ label: "Settings", icon: Settings, onClick: () => navigateTo("/settings"), divider: true },
			{ label: "Switch to Desk", icon: ExternalLink, onClick: () => (window.location.href = "/app") },
		)
	}
	items.push({ label: "Log out", icon: LogOut, onClick: () => session.logout.submit(), danger: true, divider: true })
	return items
})

function runMenu(item: MenuItem) {
	menuOpen.value = false
	item.onClick()
}

function onDocClick(e: MouseEvent) {
	if (menuOpen.value && menuWrap.value && !menuWrap.value.contains(e.target as Node)) menuOpen.value = false
}

/* ---------------- Collapse ---------------- */
function readCollapsed() {
	try {
		const v = localStorage.getItem(COLLAPSE_KEY)
		if (v !== null) return v === "1"
	} catch {}
	return window.innerWidth < 1024
}
const collapsed = ref(readCollapsed())

function toggleCollapsed() {
	collapsed.value = !collapsed.value
	tip.value = null
	try {
		localStorage.setItem(COLLAPSE_KEY, collapsed.value ? "1" : "0")
	} catch {}
}

// "[" toggles the sidebar (ignored while typing)
function onKey(e: KeyboardEvent) {
	if (e.key === "Escape") menuOpen.value = false
	const t = e.target as HTMLElement | null
	const typing = t && (t.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(t.tagName))
	if (e.key === "[" && !typing && !e.metaKey && !e.ctrlKey && !e.altKey) toggleCollapsed()
}

/* ---------------- Tooltip (collapsed mode) ---------------- */
const tip = ref<{ text: string; top: number; left: number } | null>(null)

function showTip(e: MouseEvent, text: string) {
	if (!collapsed.value) return
	const r = (e.currentTarget as HTMLElement).getBoundingClientRect()
	tip.value = { text, top: r.top + r.height / 2, left: r.right + 8 }
}
function hideTip() {
	tip.value = null
}

watch(
	() => route.path,
	() => {
		menuOpen.value = false
		hideTip()
	},
)

onMounted(() => {
	readTheme()
	document.addEventListener("mousedown", onDocClick)
	document.addEventListener("keydown", onKey)
	nextTick(readTheme)
})

onBeforeUnmount(() => {
	document.removeEventListener("mousedown", onDocClick)
	document.removeEventListener("keydown", onKey)
})

const logoFailed = ref(false)
</script>

<template>
	<aside
		class="sidebar relative flex h-screen shrink-0 flex-col border-r border-outline-gray-1 bg-surface-menu-bar transition-[width] duration-200 ease-out"
		:class="collapsed ? 'w-[52px]' : 'w-[232px]'"
		aria-label="Main navigation"
	>
		<!-- Brand -->
		<div class="flex h-12 shrink-0 items-center gap-1 px-2">
			<button
				type="button"
				class="flex min-w-0 flex-1 items-center gap-2 rounded-md p-1 text-left transition-colors hover:bg-surface-gray-2"
				:class="collapsed && 'justify-center'"
				@click="navigateTo(homePath)"
				@mouseenter="showTip($event, APP_TITLE)"
				@mouseleave="hideTip"
			>
				<img
					v-if="!logoFailed"
					:src="LOGO"
					:alt="APP_TITLE"
					class="h-7 w-7 shrink-0 rounded-md object-contain"
					@error="logoFailed = true"
				/>
				<span
					v-else
					class="grid h-7 w-7 shrink-0 place-items-center rounded-md bg-[color:var(--brand,#29ADFF)] text-sm font-semibold text-white"
				>{{ APP_TITLE.charAt(0) }}</span>
				<span v-if="!collapsed" class="min-w-0 leading-tight">
					<span class="block truncate text-[14px] font-semibold text-ink-gray-9">{{ APP_TITLE }}</span>
					<span class="block truncate text-[11.5px] text-ink-gray-5">{{ roleLabel }}</span>
				</span>
			</button>
			<button
				v-if="!collapsed"
				type="button"
				class="icon-btn"
				title="Collapse sidebar  [ "
				aria-label="Collapse sidebar"
				@click="toggleCollapsed"
			>
				<PanelLeftClose class="h-4 w-4" />
			</button>
		</div>

		<!-- Navigation -->
		<nav class="nav-scroll min-h-0 flex-1 overflow-y-auto overflow-x-hidden px-2 pb-2 pt-1">
			<div v-for="(section, si) in sections" :key="section.label || si" :class="si > 0 && 'mt-4'">
				<div
					v-if="section.label && !collapsed"
					class="mb-1 px-2 text-[11px] font-medium uppercase tracking-[0.06em] text-ink-gray-4"
				>
					{{ section.label }}
				</div>
				<div v-else-if="si > 0 && collapsed" class="mx-1.5 mb-3 border-t border-outline-gray-1"></div>

				<ul class="space-y-0.5">
					<li v-for="item in section.items" :key="item.to">
						<RouterLink
							:to="item.to"
							class="nav-item group flex h-8 items-center gap-2.5 rounded-md text-[13.5px] transition-colors"
							:class="[
								collapsed ? 'justify-center px-0' : 'px-2',
								isActive(item.to)
									? 'is-active nav-active font-medium'
									: 'text-ink-gray-7 hover:bg-surface-gray-2 hover:text-ink-gray-9',
							]"
							:aria-current="isActive(item.to) ? 'page' : undefined"
							@mouseenter="showTip($event, item.label)"
							@mouseleave="hideTip"
						>
							<component
								:is="item.icon"
								class="nav-icon h-4 w-4 shrink-0"
								:class="isActive(item.to) ? 'text-[color:var(--brand-text,#0A84D0)]' : 'text-ink-gray-6 group-hover:text-ink-gray-8'"
							/>
							<span v-if="!collapsed" class="truncate">{{ item.label }}</span>
						</RouterLink>
					</li>
				</ul>
			</div>
		</nav>

		<!-- Footer -->
		<div class="shrink-0 border-t border-outline-gray-1 p-2">
			<button
				v-if="collapsed"
				type="button"
				class="icon-btn mx-auto mb-1 flex"
				aria-label="Expand sidebar"
				@click="toggleCollapsed"
				@mouseenter="showTip($event, 'Expand sidebar  [')"
				@mouseleave="hideTip"
			>
				<PanelLeftOpen class="h-4 w-4" />
			</button>

			<div ref="menuWrap" class="relative">
				<button
					type="button"
					class="flex w-full items-center gap-2 rounded-md p-1.5 text-left transition-colors hover:bg-surface-gray-2"
					:class="[collapsed && 'justify-center', menuOpen && 'bg-surface-gray-2']"
					aria-haspopup="menu"
					:aria-expanded="menuOpen"
					@click="menuOpen = !menuOpen; hideTip()"
					@mouseenter="!menuOpen && showTip($event, userName)"
					@mouseleave="hideTip"
				>
					<span
						class="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-[color:var(--brand-soft,#E9F6FF)] text-[11px] font-semibold text-[color:var(--brand-text,#0A84D0)]"
					>{{ initials }}</span>
					<template v-if="!collapsed">
						<span class="min-w-0 flex-1 leading-tight">
							<span class="block truncate text-[13px] font-medium text-ink-gray-9">{{ userName }}</span>
							<span v-if="userEmail" class="block truncate text-[11.5px] text-ink-gray-5">{{ userEmail }}</span>
						</span>
						<ChevronsUpDown class="h-4 w-4 shrink-0 text-ink-gray-5" />
					</template>
				</button>

				<!-- Account menu -->
				<Transition name="pop">
					<div
						v-if="menuOpen"
						role="menu"
						class="menu absolute z-50 w-56 rounded-lg border border-outline-gray-2 bg-surface-modal p-1 shadow-xl"
						:class="collapsed ? 'bottom-0 left-full ml-2' : 'bottom-full left-0 right-0 mb-1.5 w-auto'"
					>
						<div class="px-2 pb-2 pt-1.5">
							<div class="truncate text-[13px] font-medium text-ink-gray-9">{{ userName }}</div>
							<div class="truncate text-[11.5px] text-ink-gray-5">{{ userEmail || roleLabel }}</div>
						</div>
						<div class="mb-1 border-t border-outline-gray-1"></div>
						<template v-for="m in menuItems" :key="m.label">
							<div v-if="m.divider" class="my-1 border-t border-outline-gray-1"></div>
							<button
								type="button"
								role="menuitem"
								class="flex h-8 w-full items-center gap-2 rounded-md px-2 text-left text-[13px] transition-colors"
								:class="m.danger ? 'text-ink-red-4 hover:bg-surface-red-1' : 'text-ink-gray-8 hover:bg-surface-gray-2'"
								@click="runMenu(m)"
							>
								<component :is="m.icon" class="h-4 w-4 shrink-0" :class="m.danger ? '' : 'text-ink-gray-6'" />
								<span class="flex-1 truncate">{{ m.label }}</span>
							</button>
						</template>
					</div>
				</Transition>
			</div>
		</div>

		<!-- Tooltip for collapsed mode (teleported so the scroll area cannot clip it) -->
		<Teleport to="body">
		<div
			v-if="tip"
			class="pointer-events-none fixed z-[100] -translate-y-1/2 whitespace-nowrap rounded-md bg-surface-gray-7 px-2 py-1 text-xs font-medium text-ink-white shadow-lg"
			:style="{ top: tip.top + 'px', left: tip.left + 'px' }"
		>
			{{ tip.text }}
		</div>
		</Teleport>
	</aside>
</template>

<style scoped>
.icon-btn {
	display: grid;
	place-items: center;
	width: 28px;
	height: 28px;
	flex-shrink: 0;
	border-radius: 6px;
	color: var(--ink-gray-5, #7c7c7c);
	transition: background-color 0.15s, color 0.15s;
}
.icon-btn:hover {
	background: var(--surface-gray-2, #f3f3f3);
	color: var(--ink-gray-9, #171717);
}

/* active item: soft brand background + brand text */
.nav-active {
	background: var(--brand-soft, #E9F6FF);
	color: var(--brand-text, #0A84D0);
}
.nav-active:hover {
	background: var(--brand-soft-2, #D2EDFF);
}

/* small accent bar on the active item */
.nav-item {
	position: relative;
}
.nav-item.is-active::before {
	content: "";
	position: absolute;
	left: -8px;
	top: 7px;
	bottom: 7px;
	width: 3px;
	border-radius: 0 3px 3px 0;
	background: var(--brand, #29ADFF);
}

/* slim scrollbar */
.nav-scroll {
	scrollbar-width: thin;
	scrollbar-color: transparent transparent;
}
.nav-scroll:hover {
	scrollbar-color: var(--outline-gray-3, #d4d4d4) transparent;
}
.nav-scroll::-webkit-scrollbar {
	width: 6px;
}
.nav-scroll::-webkit-scrollbar-thumb {
	border-radius: 999px;
	background: transparent;
}
.nav-scroll:hover::-webkit-scrollbar-thumb {
	background: var(--outline-gray-3, #d4d4d4);
}

/* menu animation */
.pop-enter-active,
.pop-leave-active {
	transition: opacity 0.12s ease, transform 0.12s ease;
}
.pop-enter-from,
.pop-leave-to {
	opacity: 0;
	transform: translateY(4px);
}
</style>

<!--
	Brand colour (ARK/Tactix brand blue #29ADFF), shared by the whole app.
	Not scoped on purpose: the dashboard, tasks page and frappe-ui dialogs use these too.
	(You can also move this block into your main CSS file.)
-->
<style>
:root {
	--brand: #29ADFF;
	--brand-hover: #0F9EF5;
	--brand-active: #0A8AD9;
	--brand-on: #ffffff; /* text on brand buttons */
	--brand-text: #0A84D0; /* blue text on white: darker shade of #29ADFF so it stays readable */
	--brand-soft: #E9F6FF;
	--brand-soft-2: #D2EDFF;
	--brand-border: #A6DCFF;
	--brand-ring: rgba(41, 173, 255, 0.35);
	--primary-color: #29ADFF;
}
[data-theme="dark"],
.dark {
	--brand: #29ADFF;
	--brand-hover: #4DBBFF;
	--brand-active: #0F9EF5;
	--brand-on: #04263b;
	--brand-text: #6CC6FF;
	--brand-soft: rgba(41, 173, 255, 0.14);
	--brand-soft-2: rgba(41, 173, 255, 0.24);
	--brand-border: rgba(41, 173, 255, 0.45);
	--brand-ring: rgba(41, 173, 255, 0.35);
	--primary-color: #29ADFF;
}

/* Primary button in brand blue — add class="brand-btn" to a frappe-ui <Button variant="solid"> */
.brand-btn {
	background-color: var(--brand) !important;
	border-color: transparent !important;
	color: var(--brand-on, #fff) !important;
}
.brand-btn:hover {
	background-color: var(--brand-hover) !important;
}
.brand-btn:active {
	background-color: var(--brand-active) !important;
}
.brand-btn:focus-visible {
	outline: none;
	box-shadow: 0 0 0 3px var(--brand-ring) !important;
}
.brand-btn:disabled,
.brand-btn[disabled] {
	opacity: 0.6;
}
</style>