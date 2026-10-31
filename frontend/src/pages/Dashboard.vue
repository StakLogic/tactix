<template>
	<div class="custom-scrollbar h-full flex-1 overflow-y-auto">
		<div class="mx-auto max-w-[1440px] space-y-5 p-1 pb-6">
			<!-- Header -->
			<div class="flex flex-col gap-3 border-b border-outline-gray-1 pb-5 md:flex-row md:items-end md:justify-between">
				<div>
					<p class="text-xs font-medium text-ink-gray-5">{{ todayLabel }}</p>
					<h1 class="mt-1 text-2xl font-semibold tracking-tight text-ink-gray-9">
						{{ greeting }}<span v-if="firstName">, {{ firstName }}</span>
					</h1>
					<p class="mt-1 text-sm text-ink-gray-5">Here's what's happening across your workspace.</p>
				</div>
				<div class="flex items-center gap-2">
					<span v-if="lastUpdated" class="hidden text-xs text-ink-gray-4 sm:inline">Updated {{ lastUpdated }}</span>
					<Button variant="subtle" :disabled="anyLoading" @click="reloadDashboardData()">
						<template #prefix>
							<IconRefresh class="h-4 w-4" :class="anyLoading && 'animate-spin'" />
						</template>
						Refresh
					</Button>
					<Button variant="solid" class="brand-btn" @click="$router.push('/tasks')">
						<template #prefix><IconList class="h-4 w-4" /></template>
						Manage Tasks
					</Button>
				</div>
			</div>

			<!-- KPI row -->
			<section>
				<h2 class="section-label">Task Overview</h2>
				<div class="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-5">
					<button
						v-for="stat in taskStatsConfig"
						:key="stat.label"
						type="button"
						class="kpi group text-left"
						@click="$router.push(stat.route)"
					>
						<div class="flex items-center justify-between">
							<span class="text-[13px] font-medium text-ink-gray-6">{{ stat.label }}</span>
							<span class="grid h-7 w-7 place-items-center rounded-md" :class="stat.chip">
								<component :is="stat.icon" class="h-4 w-4" />
							</span>
						</div>
						<div class="mt-3 flex h-8 items-end gap-2">
							<div v-if="stat.loading" class="skeleton h-7 w-14"></div>
							<template v-else>
								<span class="text-[26px] font-semibold leading-none tabular-nums text-ink-gray-9">{{ stat.value }}</span>
								<span v-if="stat.hint" class="pb-0.5 text-xs font-medium" :class="stat.hintClass">{{ stat.hint }}</span>
							</template>
						</div>
					</button>
				</div>
			</section>

			<!-- Performance row -->
			<section>
				<h2 class="section-label">Performance &amp; Time Tracking</h2>
				<div class="grid grid-cols-1 gap-3 md:grid-cols-3">
					<!-- Hours -->
					<div class="panel p-4">
						<div class="flex items-center justify-between">
							<span class="text-[13px] font-medium text-ink-gray-6">Hours logged · this week</span>
							<span class="grid h-7 w-7 place-items-center rounded-md bg-surface-green-1 text-ink-green-3">
								<IconClock class="h-4 w-4" />
							</span>
						</div>
						<div class="mt-3 h-8">
							<div v-if="timesheetsSummary.loading" class="skeleton h-7 w-24"></div>
							<span v-else class="text-[26px] font-semibold leading-none tabular-nums text-ink-gray-9">
								{{ hoursThisWeek.toFixed(1) }}<span class="ml-1 text-sm font-medium text-ink-gray-5">hrs</span>
							</span>
						</div>
						<div class="mt-3">
							<div class="flex justify-between text-xs text-ink-gray-5">
								<span>Weekly target {{ WEEKLY_TARGET }} hrs</span>
								<span class="tabular-nums">{{ hoursPct }}%</span>
							</div>
							<div class="track mt-1.5"><div class="fill bg-[color:var(--brand,#29ADFF)]" :style="{ width: hoursPct + '%' }"></div></div>
						</div>
					</div>

					<!-- SLA -->
					<div class="panel p-4">
						<div class="flex items-center justify-between">
							<span class="text-[13px] font-medium text-ink-gray-6">Initial response SLA</span>
							<span class="grid h-7 w-7 place-items-center rounded-md" :class="sla.chip">
								<IconShieldAlert class="h-4 w-4" />
							</span>
						</div>
						<div class="mt-3 flex h-8 items-end gap-2">
							<div v-if="performanceResource.loading" class="skeleton h-7 w-28"></div>
							<template v-else>
								<span class="text-[26px] font-semibold leading-none text-ink-gray-9">{{ sla.grade }}</span>
								<span class="pb-0.5 text-sm font-medium" :class="sla.text">{{ sla.label }}</span>
							</template>
						</div>
						<p class="mt-3 text-xs text-ink-gray-5">
							Avg. first response:
							<b class="font-medium text-ink-gray-8">{{ formatDuration(avgResponse) }}</b>
							<span class="text-ink-gray-4"> · this month</span>
						</p>
					</div>

					<!-- Completion -->
					<div class="panel p-4">
						<div class="flex items-center justify-between">
							<span class="text-[13px] font-medium text-ink-gray-6">Completion rate</span>
							<span class="grid h-7 w-7 place-items-center rounded-md bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)]">
								<IconCheckCircle class="h-4 w-4" />
							</span>
						</div>
						<div class="mt-3 h-8">
							<div v-if="taskSummary.loading" class="skeleton h-7 w-16"></div>
							<span v-else class="text-[26px] font-semibold leading-none tabular-nums text-ink-gray-9">{{ completionPct }}%</span>
						</div>
						<div class="mt-3">
							<!-- status breakdown -->
							<div class="track flex">
								<div
									v-for="s in statusBreakdown"
									:key="s.label"
									class="h-full transition-all duration-500"
									:class="s.bar"
									:style="{ width: s.pct + '%' }"
									:title="`${s.label}: ${s.count}`"
								></div>
							</div>
							<div class="mt-2 flex flex-wrap gap-x-3 gap-y-1">
								<span v-for="s in statusBreakdown" :key="s.label" class="flex items-center gap-1.5 text-xs text-ink-gray-5">
									<span class="h-2 w-2 rounded-full" :class="s.bar"></span>
									{{ s.label }} <b class="font-medium tabular-nums text-ink-gray-8">{{ s.count }}</b>
								</span>
							</div>
						</div>
					</div>
				</div>
			</section>

			<!-- Main grid -->
			<div class="grid grid-cols-1 gap-4 lg:grid-cols-12">
				<!-- Recent tasks -->
				<div class="panel flex flex-col lg:col-span-8">
					<div class="flex items-center justify-between border-b border-outline-gray-1 px-4 py-3">
						<div>
							<h3 class="text-[15px] font-semibold text-ink-gray-9">Recent Activity</h3>
							<p class="text-xs text-ink-gray-5">Latest updated tasks</p>
						</div>
						<Button variant="ghost" size="sm" class="!text-[color:var(--brand-text,#0A84D0)]" @click="$router.push('/tasks')">
							View all
							<template #suffix><IconArrowRight class="h-3.5 w-3.5" /></template>
						</Button>
					</div>

					<div v-if="tasks.loading && !recentTasks.length" class="divide-y divide-outline-gray-1">
						<div v-for="n in 5" :key="n" class="flex items-center gap-3 px-4 py-3">
							<div class="skeleton h-8 w-8 rounded-full"></div>
							<div class="flex-1 space-y-1.5">
								<div class="skeleton h-3.5 w-1/2"></div>
								<div class="skeleton h-3 w-1/3"></div>
							</div>
							<div class="skeleton h-5 w-16"></div>
						</div>
					</div>

					<ul v-else-if="recentTasks.length" class="divide-y divide-outline-gray-1">
						<li
							v-for="task in recentTasks"
							:key="task.name"
							class="group flex cursor-pointer items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-gray-1"
							@click="$router.push('/tasks/' + task.name)"
						>
							<Avatar
								:image="getUserAvatarImage(task.assigned_by)"
								:label="getUserLabel(task.assigned_by)"
								size="md"
							/>
							<div class="min-w-0 flex-1">
								<h4 class="truncate text-sm font-medium text-ink-gray-9 group-hover:text-[color:var(--brand-text,#0A84D0)]" :title="task.subject">
									{{ task.subject }}
								</h4>
								<div class="mt-0.5 flex min-w-0 items-center gap-1.5 text-xs text-ink-gray-5">
									<span class="truncate">{{ task.project_name || "General" }}</span>
									<span class="text-ink-gray-3">·</span>
									<span class="shrink-0 font-mono text-[11px]">{{ task.name }}</span>
									<template v-if="task.priority">
										<span class="text-ink-gray-3">·</span>
										<span class="flex shrink-0 items-center gap-1">
											<span class="h-1.5 w-1.5 rounded-full" :class="priorityDot(task.priority)"></span>{{ task.priority }}
										</span>
									</template>
								</div>
							</div>
							<div class="flex shrink-0 flex-col items-end gap-1">
								<Badge variant="subtle" :theme="getStatusTheme(task.status)" size="sm">{{ task.status }}</Badge>
								<span class="text-[11px]" :class="dueInfo(task).cls" :title="task.exp_end_date || ''">
									{{ dueInfo(task).text }}
								</span>
							</div>
						</li>
					</ul>

					<div v-else class="flex flex-1 flex-col items-center justify-center px-4 py-14 text-center">
						<span class="grid h-10 w-10 place-items-center rounded-full bg-surface-gray-2 text-ink-gray-5">
							<IconList class="h-5 w-5" />
						</span>
						<p class="mt-3 text-sm font-medium text-ink-gray-8">No recent activity</p>
						<p class="mt-1 text-xs text-ink-gray-5">Tasks you create or are assigned to will show up here.</p>
					</div>
				</div>

				<!-- Right column -->
				<div class="space-y-4 lg:col-span-4">
					<!-- Workload -->
					<div class="panel">
						<div class="border-b border-outline-gray-1 px-4 py-3">
							<h3 class="text-[15px] font-semibold text-ink-gray-9">Workload Focus</h3>
							<p class="text-xs text-ink-gray-5">Tasks by priority</p>
						</div>
						<div class="space-y-4 p-4">
							<div v-for="p in priorityData" :key="p.label">
								<div class="flex items-center justify-between text-xs">
									<span class="flex items-center gap-2 font-medium text-ink-gray-7">
										<span class="h-2 w-2 rounded-full" :class="p.color"></span>{{ p.label }}
									</span>
									<span class="tabular-nums text-ink-gray-5">
										<b class="font-medium text-ink-gray-8">{{ p.count }}</b> · {{ p.pct }}%
									</span>
								</div>
								<div class="track mt-1.5"><div class="fill" :class="p.color" :style="{ width: p.pct + '%' }"></div></div>
							</div>
							<p v-if="!tasks.loading && !priorityTotal" class="text-center text-xs text-ink-gray-4">No tasks yet</p>
						</div>
					</div>

					<!-- Insight -->
					<div class="panel overflow-hidden">
						<div class="flex gap-3 p-4" :class="insight.bg">
							<span class="grid h-8 w-8 shrink-0 place-items-center rounded-md" :class="insight.chip">
								<component :is="insight.icon" class="h-4 w-4" />
							</span>
							<div class="min-w-0">
								<h4 class="text-sm font-semibold text-ink-gray-9">{{ insight.title }}</h4>
								<p class="mt-1 text-[13px] leading-relaxed text-ink-gray-6">{{ insightMessage }}</p>
								<Button variant="outline" size="sm" class="mt-3" @click="$router.push(insightButtonAction.route)">
									{{ insightButtonAction.label }}
									<template #suffix><IconArrowRight class="h-3.5 w-3.5" /></template>
								</Button>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import dayjs from "dayjs"
import relativeTime from "dayjs/plugin/relativeTime"
import { Avatar, Badge, Button, createListResource, createResource } from "frappe-ui"
import { computed, onBeforeUnmount, ref, watch } from "vue"

dayjs.extend(relativeTime)

// Icons
import IconAlertTriangle from "~icons/lucide/alert-triangle"
import IconArrowRight from "~icons/lucide/arrow-right"
import IconBriefcase from "~icons/lucide/briefcase"
import IconCheckCircle from "~icons/lucide/check-circle"
import IconClock from "~icons/lucide/clock"
import IconList from "~icons/lucide/list"
import IconLoader from "~icons/lucide/loader"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconShieldAlert from "~icons/lucide/shield-alert"
import IconSparkles from "~icons/lucide/sparkles"
import { session } from "../data/session"

const WEEKLY_TARGET = 40

const taskFilters = computed(() => ({}))

// auto: true already loads each resource once — no extra reload on mount
const tasks = createResource({
	url: "tactix.api.tasks.get_tasks",
	auto: true,
	params: { filters: taskFilters.value },
	initialData: [],
})

const taskSummary = createResource({
	url: "tactix.api.tasks.get_task_summary",
	auto: true,
	params: { filters: taskFilters.value },
	initialData: {
		total: 0,
		open: 0,
		in_progress: 0,
		completed: 0,
		overdue: 0,
		active_projects: 0,
	},
})

const timesheetsSummary = createResource({
	url: "tactix.api.timesheet.get_timesheet_summary",
	auto: true,
	params: { filters: { timespan: "this_week" } },
	initialData: { total_hours: 0 },
})

const performanceResource = createResource({
	url: "tactix.api.performance.get_performance_data",
	auto: true,
	params: { timespan: "this_month" },
	initialData: {},
})

const userResource = createListResource({
	doctype: "User",
	fields: ["name", "full_name", "user_image"],
	filters: {
		enabled: 1,
		name: ["not in", ["Administrator", "Guest"]],
		tactix_customer: ["=", ""],
	},
	auto: true,
	transform: (users) =>
		users.map((user) => ({
			label: user.full_name || user.name,
			value: user.name,
			image: user.user_image || "",
		})),
	pageLength: 10000,
})

/* ---------------- Header ---------------- */
const greeting = computed(() => {
	const h = new Date().getHours()
	if (h < 12) return "Good morning"
	if (h < 17) return "Good afternoon"
	return "Good evening"
})
const firstName = computed(() => String(session.userFullName || "").trim().split(/\s+/)[0] || "")
const todayLabel = dayjs().format("dddd, D MMMM YYYY")

const anyLoading = computed(
	() => tasks.loading || taskSummary.loading || timesheetsSummary.loading || performanceResource.loading,
)

const lastUpdatedAt = ref(null)
const tick = ref(0)
const lastUpdated = computed(() => {
	tick.value // re-evaluate every minute
	return lastUpdatedAt.value ? dayjs(lastUpdatedAt.value).fromNow() : ""
})
watch(anyLoading, (v) => {
	if (!v) lastUpdatedAt.value = new Date()
})
const tickTimer = setInterval(() => tick.value++, 60000)
onBeforeUnmount(() => clearInterval(tickTimer))

function reloadDashboardData() {
	tasks.reload()
	taskSummary.reload()
	timesheetsSummary.reload()
	performanceResource.reload()
}

/* ---------------- Users ---------------- */
function findUser(userName) {
	if (!userName) return null
	return userResource.data?.find((user) => user.value === userName) || null
}
function getUserAvatarImage(userName) {
	return findUser(userName)?.image || ""
}
function getUserLabel(userName) {
	return findUser(userName)?.label || userName || "U"
}

/* ---------------- KPIs ---------------- */
const summary = computed(() => taskSummary.data || {})
const totalTasksCount = computed(() => summary.value.total || 0)
const inProgressCount = computed(() => summary.value.in_progress || 0)
const completedCount = computed(() => summary.value.completed || 0)
const overdueCount = computed(() => summary.value.overdue || 0)
const activeProjectsCount = computed(() => summary.value.active_projects || 0)

const completionPct = computed(() =>
	totalTasksCount.value ? Math.round((completedCount.value / totalTasksCount.value) * 100) : 0,
)

const taskStatsConfig = computed(() => [
	{
		label: "Active Projects",
		value: activeProjectsCount.value,
		icon: IconBriefcase,
		chip: "bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)]",
		route: "/tasks",
		loading: taskSummary.loading,
	},
	{
		label: "Total Tasks",
		value: totalTasksCount.value,
		icon: IconList,
		chip: "bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)]",
		route: "/tasks",
		loading: taskSummary.loading,
	},
	{
		label: "In Progress",
		value: inProgressCount.value,
		icon: IconLoader,
		chip: "bg-surface-amber-1 text-ink-amber-3",
		route: "/tasks",
		loading: taskSummary.loading,
	},
	{
		label: "Completed",
		value: completedCount.value,
		icon: IconCheckCircle,
		chip: "bg-surface-green-1 text-ink-green-3",
		hint: totalTasksCount.value ? `${completionPct.value}%` : "",
		hintClass: "text-ink-green-3",
		route: "/tasks",
		loading: taskSummary.loading,
	},
	{
		label: "Overdue",
		value: overdueCount.value,
		icon: IconAlertTriangle,
		chip: overdueCount.value ? "bg-surface-red-1 text-ink-red-4" : "bg-surface-gray-2 text-ink-gray-5",
		hint: overdueCount.value ? "Needs attention" : "All on track",
		hintClass: overdueCount.value ? "text-ink-red-4" : "text-ink-gray-5",
		route: "/tasks",
		loading: taskSummary.loading,
	},
])

const statusBreakdown = computed(() => {
	const total = totalTasksCount.value
	const list = [
		{ label: "Open", count: summary.value.open || 0, bar: "bg-[color:var(--brand,#29ADFF)]" },
		{ label: "In progress", count: inProgressCount.value, bar: "bg-surface-amber-3" },
		{ label: "Completed", count: completedCount.value, bar: "bg-surface-green-3" },
		{ label: "Overdue", count: overdueCount.value, bar: "bg-surface-red-4" },
	]
	return list.map((s) => ({ ...s, pct: total ? (s.count / total) * 100 : 0 }))
})

/* ---------------- Time & SLA ---------------- */
const hoursThisWeek = computed(() => Number(timesheetsSummary.data?.total_hours) || 0)
const hoursPct = computed(() => Math.min(100, Math.round((hoursThisWeek.value / WEEKLY_TARGET) * 100)))

const avgResponse = computed(() => Number(performanceResource.data?.ticket?.avg_response_time) || 0)

const sla = computed(() => {
	const s = avgResponse.value
	if (!s || s <= 0) return { grade: "—", label: "No score yet", text: "text-ink-gray-5", chip: "bg-surface-gray-2 text-ink-gray-5" }
	const hrs = s / 3600
	if (hrs < 2) return { grade: "A+", label: "Elite", text: "text-ink-green-3", chip: "bg-surface-green-1 text-ink-green-3" }
	if (hrs < 8) return { grade: "A", label: "Fast", text: "text-ink-green-3", chip: "bg-surface-green-1 text-ink-green-3" }
	if (hrs < 24) return { grade: "B", label: "Compliant", text: "text-[color:var(--brand-text,#0A84D0)]", chip: "bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)]" }
	return { grade: "C", label: "Warning", text: "text-ink-amber-3", chip: "bg-surface-amber-1 text-ink-amber-3" }
})

function formatDuration(seconds) {
	if (!seconds || seconds <= 0) return "—"
	const m = Math.round(seconds / 60)
	if (m < 60) return `${m}m`
	const h = Math.floor(m / 60)
	if (h < 24) return `${h}h ${m % 60}m`
	return `${Math.floor(h / 24)}d ${h % 24}h`
}

/* ---------------- Recent tasks ---------------- */
const taskList = computed(() => (Array.isArray(tasks.data?.tasks) ? tasks.data.tasks : []))

// Newest first when the API returns a modified/creation timestamp; otherwise keep the API order
const recentTasks = computed(() => {
	const list = [...taskList.value]
	const key = (t) => t.modified || t.creation || ""
	if (list.some((t) => key(t))) list.sort((a, b) => String(key(b)).localeCompare(String(key(a))))
	return list.slice(0, 6)
})

function dueInfo(task) {
	if (!task.exp_end_date) return { text: "No due date", cls: "text-ink-gray-4" }
	const due = dayjs(task.exp_end_date).startOf("day")
	const today = dayjs().startOf("day")
	const diff = due.diff(today, "day")
	if (task.status === "Completed") return { text: `Due ${due.format("D MMM")}`, cls: "text-ink-gray-4" }
	if (diff < 0) return { text: `Overdue ${due.from(today, true)}`, cls: "font-medium text-ink-red-4" }
	if (diff === 0) return { text: "Due today", cls: "font-medium text-ink-amber-3" }
	if (diff === 1) return { text: "Due tomorrow", cls: "text-ink-amber-3" }
	return { text: `Due ${due.format("D MMM")}`, cls: "text-ink-gray-5" }
}

function priorityDot(p) {
	return { High: "bg-surface-red-4", Medium: "bg-surface-amber-3", Low: "bg-surface-gray-4" }[p] || "bg-surface-gray-4"
}

/* ---------------- Workload ---------------- */
// Percentages use the same task list the counts come from, so the bars always add up
const priorityTotal = computed(() => taskList.value.filter((t) => ["High", "Medium", "Low"].includes(t.priority)).length)

const priorityData = computed(() => {
	const colors = { High: "bg-surface-red-4", Medium: "bg-surface-amber-3", Low: "bg-surface-gray-4" }
	return ["High", "Medium", "Low"].map((p) => {
		const count = taskList.value.filter((t) => t.priority === p).length
		return {
			label: p,
			count,
			pct: priorityTotal.value ? Math.round((count / priorityTotal.value) * 100) : 0,
			color: colors[p],
		}
	})
})

/* ---------------- Insight ---------------- */
const insightKind = computed(() => {
	if (overdueCount.value > 0) return "overdue"
	if (avgResponse.value / 3600 >= 24) return "sla"
	return "ok"
})

const insight = computed(() => {
	if (insightKind.value === "overdue")
		return { title: "Overdue tasks", icon: IconAlertTriangle, bg: "bg-surface-red-1", chip: "bg-surface-white text-ink-red-4" }
	if (insightKind.value === "sla")
		return { title: "Response time is slow", icon: IconShieldAlert, bg: "bg-surface-amber-1", chip: "bg-surface-white text-ink-amber-3" }
	return { title: "Workload looks healthy", icon: IconSparkles, bg: "bg-[color:var(--brand-soft,#E9F6FF)]", chip: "bg-surface-white text-[color:var(--brand-text,#0A84D0)]" }
})

const insightMessage = computed(() => {
	const overdue = overdueCount.value
	if (insightKind.value === "overdue") {
		return `You have ${overdue} overdue task${overdue > 1 ? "s" : ""}. Consider rescheduling their deadlines to maintain a healthy project timeline.`
	}
	if (insightKind.value === "sla") {
		return "Average first response time is above 24 hours (SLA warning). Check and assign unaddressed customer tickets."
	}
	return `You currently have ${inProgressCount.value} active task${inProgressCount.value !== 1 ? "s" : ""}. Current workload is well within capacity.`
})

const insightButtonAction = computed(() => {
	if (insightKind.value === "overdue") return { label: "Manage Tasks", route: "/tasks" }
	if (insightKind.value === "sla") return { label: "View Performance", route: "/performance" }
	return { label: "View Reports", route: "/performance" }
})

function getStatusTheme(status) {
	const themes = {
		Open: "blue",
		Working: "orange",
		Completed: "green",
		Overdue: "red",
	}
	return themes[status] || "gray"
}
</script>

<style scoped>
.section-label {
	margin-bottom: 8px;
	font-size: 11px;
	font-weight: 600;
	letter-spacing: 0.06em;
	text-transform: uppercase;
	color: var(--ink-gray-5, #7c7c7c);
}
.panel {
	border: 1px solid var(--outline-gray-1, #ededed);
	border-radius: 12px;
	background: var(--surface-cards, #fff);
	box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}
.kpi {
	padding: 14px 16px;
	border: 1px solid var(--outline-gray-1, #ededed);
	border-radius: 12px;
	background: var(--surface-cards, #fff);
	box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
	transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
}
.kpi:hover {
	border-color: var(--brand-border, #A6DCFF);
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.track {
	height: 6px;
	width: 100%;
	overflow: hidden;
	border-radius: 999px;
	background: var(--surface-gray-2, #f3f3f3);
}
.fill {
	height: 100%;
	border-radius: 999px;
	transition: width 0.5s ease;
}
.skeleton {
	border-radius: 6px;
	background: var(--surface-gray-2, #f3f3f3);
	animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse {
	50% {
		opacity: 0.5;
	}
}
</style>