<template>
	<div class="space-y-4 p-1 overflow-y-auto h-full flex-1 custom-scrollbar">
		<div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-6">
			<div>
				<h1 class="text-2xl font-semibold text-slate-900">Workspace Overview</h1>
				<p class="text-sm text-slate-500 mt-1">Real-time performance metrics and recent task updates.</p>
			</div>
			<div class="flex gap-3">
					<Button variant="ghost" class="!text-slate-600" @click="reloadDashboardData()">
					<template #prefix><IconRefresh class="w-4 h-4" /></template>
					Refresh
				</Button>
				<Button variant="solid" class="!bg-slate-800 hover:!bg-slate-900 !text-white transition-all" @click="$router.push('/tasks')">Manage Tasks</Button>
			</div>
		</div>

		<!-- Section: Task Overview -->
		<div class="space-y-2">
			<label class="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest block">Task Overview</label>
			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
				<Card v-for="stat in taskStatsConfig" :key="stat.label" class="!shadow-sm border border-slate-100 bg-white hover:border-slate-200 transition-colors">
					<div class="flex flex-col gap-1">
						<span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{{ stat.label }}</span>
						<div class="flex items-center justify-between mt-1">
							<div class="text-xl font-black text-slate-900 truncate">
								<template v-if="stat.loading">
									<div class="w-4 h-4 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
								</template>
								<span v-else>{{ stat.value }}</span>
							</div>
							<div :class="`p-2 rounded-lg ${stat.bg} ${stat.color} flex-shrink-0`">
								<component :is="stat.icon" class="w-5 h-5" />
							</div>
						</div>
					</div>
				</Card>
			</div>
		</div>

		<!-- Section: Performance & Time Tracking -->
		<div class="space-y-2 pt-2">
			<label class="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest block">Performance & Time Tracking</label>
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
				<Card v-for="stat in performanceStatsConfig" :key="stat.label" class="!shadow-sm border border-slate-100 bg-white hover:border-slate-200 transition-colors">
					<div class="flex flex-col gap-1">
						<span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{{ stat.label }}</span>
						<div class="flex items-center justify-between mt-1">
							<div class="text-xl font-black text-slate-900 truncate">
								<template v-if="stat.loading">
									<div class="w-4 h-4 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
								</template>
								<span v-else>{{ stat.value }}</span>
							</div>
							<div :class="`p-2 rounded-lg ${stat.bg} ${stat.color} flex-shrink-0`">
								<component :is="stat.icon" class="w-5 h-5" />
							</div>
						</div>
					</div>
				</Card>
			</div>
		</div>

		<div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
			<div class="lg:col-span-8">
				<Card title="Recent Activity" class="!shadow-sm border border-slate-100 h-full">
					<div class="space-y-1 mt-4">
						<div v-if="tasks.loading" class="flex justify-center py-8">
							<div class="w-6 h-6 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
						</div>
						
						<div v-for="task in recentTasks" :key="task.name" 
							class="flex items-center justify-between p-2 rounded-xl hover:bg-slate-50 transition-colors group border-b border-transparent last:border-0 cursor-pointer"
							@click="$router.push('/tasks/' + task.name)"
						>
							<div class="flex items-center gap-4">
								<Avatar :image="getUserAvatarImage(task.assigned_by)" :label="task.assigned_by || 'U'" size="md" class="ring-2 ring-white shadow-sm" />
								<div>
									<h4 class="text-sm font-semibold text-slate-800 group-hover:text-blue-600 transition-colors">
										{{ task.subject }}
									</h4>
									<div class="flex items-center gap-2 mt-1 text-xs text-slate-400">
										<span class="font-medium text-slate-500">{{ task.project_name || 'General' }}</span>
										<span>•</span>
										<span>{{ task.name }}</span>
									</div>
								</div>
							</div>
							<div class="flex flex-col items-end gap-2">
								<Badge variant="subtle" :theme="getStatusTheme(task.status)" size="sm" class="font-bold">
									{{ task.status }}
								</Badge>
								<span class="text-[10px] text-slate-400 font-medium italic">{{ task.exp_end_date || 'No due date' }}</span>
							</div>
						</div>

						<div v-if="!tasks.loading && !recentTasks.length" class="text-center py-12">
							<p class="text-sm text-slate-400">No recent activity found in the last 30 days.</p>
						</div>
					</div>
				</Card>
			</div>

			<div class="lg:col-span-4 space-y-6">
				<Card title="Workload Focus" class="!shadow-sm border border-slate-100">
					<div class="space-y-6 mt-4">
						<div v-for="p in priorityData" :key="p.label" class="space-y-2">
							<div class="flex justify-between items-center">
								<span class="text-xs font-bold text-slate-600">{{ p.label }} Priority</span>
								<span class="text-xs font-mono text-slate-400">{{ p.count }}</span>
							</div>
							<div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
								<div 
									:class="`h-full transition-all duration-500 ${p.color}`" 
									:style="{ width: `${totalTasksCount ? (p.count / totalTasksCount) * 100 : 0}%` }"
								></div>
							</div>
						</div>
					</div>
				</Card>

				<div :class="`rounded-2xl p-6 text-white shadow-lg transition-all duration-300 ${insightThemeClass}`">
					<h4 class="text-sm font-bold opacity-90 uppercase tracking-wider">System Insights</h4>
					<p class="mt-3 text-sm leading-relaxed opacity-85">
						{{ insightMessage }}
					</p>
					<Button 
						variant="ghost" 
						class="mt-4 !text-white !bg-white/10 hover:!bg-white/20 !border-none"
						@click="$router.push(insightButtonAction.route)"
					>
						{{ insightButtonAction.label }}
					</Button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import dayjs from "dayjs"
import relativeTime from "dayjs/plugin/relativeTime"
import {
	Avatar,
	Badge,
	Button,
	Card,
	LoadingIndicator,
	createListResource,
	createResource,
} from "frappe-ui"
import { computed, onMounted, reactive, watch } from "vue"

dayjs.extend(relativeTime)

// Icons
import IconBriefcase from "~icons/lucide/briefcase"
import IconCheckCircle from "~icons/lucide/check-circle"
import IconClock from "~icons/lucide/clock"
import IconList from "~icons/lucide/list"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconShieldAlert from "~icons/lucide/shield-alert"
import { session } from "../data/session"

const taskFilters = computed(() => {
	return {}
})

const tasks = createResource({
	url: "tactix.api.tasks.get_tasks",
	auto: true,
	params: {
		filters: taskFilters.value,
	},
	initialData: [],
})

const taskSummary = createResource({
	url: "tactix.api.tasks.get_task_summary",
	auto: true,
	params: {
		filters: taskFilters.value,
	},
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
	params: {
		filters: { timespan: "this_week" },
	},
	initialData: { total_hours: 0 },
})

const performanceResource = createResource({
	url: "tactix.api.performance.get_performance_data",
	auto: true,
	params: {
		timespan: "this_month",
	},
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

onMounted(() => {
	tasks.reload()
	taskSummary.reload()
	timesheetsSummary.reload()
	performanceResource.reload()
})

function getUserAvatarImage(userName) {
	if (!userName) return ""
	const match = userResource.data?.find((user) => user.value === userName)
	return match?.image || ""
}

const totalTasksCount = computed(() => taskSummary.data?.total || 0)
const inProgressCount = computed(() => taskSummary.data?.in_progress || 0)
const activeProjectsCount = computed(
	() => taskSummary.data?.active_projects || 0,
)

const taskStatsConfig = computed(() => [
	{
		label: "Active Projects",
		value: activeProjectsCount.value,
		icon: IconBriefcase,
		color: "text-blue-600",
		bg: "bg-blue-50",
		loading: tasks.loading,
	},
	{
		label: "Total Tasks",
		value: totalTasksCount.value,
		icon: IconList,
		color: "text-indigo-600",
		bg: "bg-indigo-50",
		loading: tasks.loading,
	},
	{
		label: "In Progress",
		value: inProgressCount.value,
		icon: IconClock,
		color: "text-orange-600",
		bg: "bg-orange-50",
		loading: tasks.loading,
	},
	{
		label: "Completed",
		value: taskSummary.data?.completed || 0,
		icon: IconCheckCircle,
		color: "text-green-600",
		bg: "bg-green-50",
		loading: tasks.loading,
	},
])

const performanceStatsConfig = computed(() => [
	{
		label: "Hours Logged (This Week)",
		value: `${timesheetsSummary.data?.total_hours?.toFixed(1) || "0.0"} hrs`,
		icon: IconClock,
		color: "text-emerald-600",
		bg: "bg-emerald-50",
		loading: timesheetsSummary.loading,
	},
	{
		label: "Initial Response SLA",
		value: getSLARatingText(
			performanceResource.data?.ticket?.avg_response_time,
		),
		icon: IconShieldAlert,
		color: getSLARatingColorClass(
			performanceResource.data?.ticket?.avg_response_time,
		),
		bg: getSLARatingBgClass(
			performanceResource.data?.ticket?.avg_response_time,
		),
		loading: performanceResource.loading,
	},
])

function reloadDashboardData() {
	tasks.reload()
	taskSummary.reload()
	timesheetsSummary.reload()
	performanceResource.reload()
}

function getSLARatingText(seconds) {
	if (!seconds || seconds <= 0) return "No Score"
	const hrs = seconds / 3600
	if (hrs < 2) return "A+ Elite"
	if (hrs < 8) return "A Fast"
	if (hrs < 24) return "B Compliant"
	return "C Warning"
}

function getSLARatingColorClass(seconds) {
	if (!seconds || seconds <= 0) return "text-slate-500"
	const hrs = seconds / 3600
	if (hrs < 8) return "text-green-600"
	if (hrs < 24) return "text-blue-600"
	return "text-orange-600"
}

function getSLARatingBgClass(seconds) {
	if (!seconds || seconds <= 0) return "bg-slate-50"
	const hrs = seconds / 3600
	if (hrs < 8) return "bg-green-50"
	if (hrs < 24) return "bg-blue-50"
	return "bg-orange-50"
}

const recentTasks = computed(() => [...(tasks.data?.tasks || [])].slice(0, 5))

const priorityData = computed(() => {
	const priorities = ["High", "Medium", "Low"]
	const colors = {
		High: "bg-red-500",
		Medium: "bg-amber-400",
		Low: "bg-slate-300",
	}
	return priorities.map((p) => ({
		label: p,
		count: tasks.data?.tasks?.filter((t) => t.priority === p).length || 0,
		color: colors[p],
	}))
})

const insightMessage = computed(() => {
	const overdue = taskSummary.data?.overdue || 0
	const avgResponse = performanceResource.data?.ticket?.avg_response_time || 0
	const hrs = avgResponse / 3600

	if (overdue > 0) {
		return `You have ${overdue} overdue task${overdue > 1 ? "s" : ""}. Consider rescheduling their deadlines to maintain a healthy project timeline.`
	}
	if (hrs >= 24) {
		return "Average first response time is currently slow (SLA Warning). Please check and assign unaddressed customer tickets."
	}
	return `You currently have ${inProgressCount.value} active task${inProgressCount.value !== 1 ? "s" : ""}. Current workload is well within capacity.`
})

const insightThemeClass = computed(() => {
	const overdue = taskSummary.data?.overdue || 0
	const avgResponse = performanceResource.data?.ticket?.avg_response_time || 0
	const hrs = avgResponse / 3600

	if (overdue > 0) {
		return "bg-red-600 shadow-red-100"
	}
	if (hrs >= 24) {
		return "bg-amber-600 shadow-amber-100"
	}
	return "bg-blue-600 shadow-blue-100"
})

const insightButtonAction = computed(() => {
	const overdue = taskSummary.data?.overdue || 0
	const avgResponse = performanceResource.data?.ticket?.avg_response_time || 0
	const hrs = avgResponse / 3600

	if (overdue > 0) {
		return { label: "Manage Tasks", route: "/tasks" }
	}
	if (hrs >= 24) {
		return { label: "View Performance", route: "/performance" }
	}
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