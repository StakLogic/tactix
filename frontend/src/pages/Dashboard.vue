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
				<Button variant="solid" @click="$router.push('/tasks')">Manage Tasks</Button>
			</div>
		</div>

		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
			<Card v-for="stat in statsConfig" :key="stat.label" class="!shadow-sm border border-slate-100 bg-white hover:border-slate-200 transition-colors">
				<div class="flex flex-col gap-1">
					<span class="text-[11px] font-bold text-slate-400 uppercase tracking-widest">{{ stat.label }}</span>
					<div class="flex items-center justify-between">
						<div class="text-3xl font-bold text-slate-900">
							<template v-if="tasks.loading">
								<div class="w-4 h-4 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
							</template>
							<span v-else>{{ stat.value }}</span>
						</div>
						<div :class="`p-2 rounded-lg ${stat.bg} ${stat.color}`">
							<component :is="stat.icon" class="w-5 h-5" />
						</div>
					</div>
				</div>
			</Card>
		</div>

		<div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
			<div class="lg:col-span-8">
				<Card title="Recent Activity" class="!shadow-sm border border-slate-100 h-full">
					<div class="space-y-1 mt-4">
						<div v-if="tasks.loading" class="flex justify-center"><LoadingIndicator /></div>
						
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
				<Card title="Upcoming Leaves" class="!shadow-sm border border-slate-100">
					<template #actions>
						<select 
							v-model="leavesFilters.range" 
							class="text-[11px] border border-slate-200 rounded-lg bg-white px-2.5 py-1 outline-none text-slate-500 font-semibold focus:ring-1 focus:ring-blue-500 cursor-pointer transition-all hover:bg-slate-50 font-sans"
						>
							<option value="7">Next 7 Days</option>
							<option value="14">Next 14 Days</option>
							<option value="30">Next 30 Days</option>
							<option value="custom">Custom Range</option>
						</select>
					</template>
					<div class="space-y-4 mt-4">
						<!-- Custom Date Pickers -->
						<div v-if="leavesFilters.range === 'custom'" class="flex gap-2 items-center pb-3 border-b border-slate-100/60">
							<div class="flex-1">
								<label class="text-[9px] font-bold text-slate-400 uppercase tracking-widest block mb-1">From</label>
								<input 
									type="date" 
									v-model="leavesFilters.from_date" 
									class="w-full text-xs border border-slate-200 rounded-lg bg-slate-50/50 px-2.5 py-1.5 outline-none text-slate-600 focus:ring-1 focus:ring-blue-500 transition-all font-sans"
								/>
							</div>
							<div class="flex-1">
								<label class="text-[9px] font-bold text-slate-400 uppercase tracking-widest block mb-1">To</label>
								<input 
									type="date" 
									v-model="leavesFilters.to_date" 
									class="w-full text-xs border border-slate-200 rounded-lg bg-slate-50/50 px-2.5 py-1.5 outline-none text-slate-600 focus:ring-1 focus:ring-blue-500 transition-all font-sans"
								/>
							</div>
						</div>

						<div v-if="upcomingLeaves.loading" class="flex justify-center py-6">
							<LoadingIndicator />
						</div>

						<div v-else-if="!upcomingLeaves.data || !upcomingLeaves.data.length" class="text-center py-8">
							<div class="flex justify-center mb-2 text-slate-300">
								<IconCalendar class="w-8 h-8 opacity-60" />
							</div>
							<p class="text-xs text-slate-400 font-medium">Everyone is available</p>
						</div>

						<div v-else class="space-y-3">
							<div v-for="leave in upcomingLeaves.data" :key="leave.name" 
								class="flex items-center justify-between p-2 rounded-xl hover:bg-slate-50 border border-transparent hover:border-slate-100 transition-all group cursor-pointer"
								@click="$router.push('/leave-applications')"
							>
								<div class="flex items-center gap-3">
									<Avatar :image="getUserAvatarImage(leave.user)" :label="leave.full_name || leave.user" size="md" class="ring-2 ring-white shadow-sm" />
									<div class="min-w-0">
										<h4 class="text-sm font-semibold text-slate-800 group-hover:text-blue-600 transition-colors flex items-center gap-1.5 truncate">
											<span class="truncate">{{ leave.full_name }}</span>
											<span v-if="leave.status === 'Approved'" class="text-[9px] font-bold px-1.5 py-0.2 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-100 flex-shrink-0">
												Approved
											</span>
											<span v-else-if="leave.status === 'Pending'" class="text-[9px] font-bold px-1.5 py-0.2 rounded-full bg-amber-50 text-amber-700 border border-amber-100 flex-shrink-0">
												Pending
											</span>
										</h4>
										<p class="text-[11px] text-slate-400 font-medium mt-0.5">
											{{ formatLeaveDates(leave.from_date, leave.to_date) }}
										</p>
									</div>
								</div>
								<div>
									<Badge variant="subtle" :theme="getLeaveStatusTheme(leave.from_date, leave.to_date)" size="sm" class="font-bold">
										{{ getRelativeLeaveStatus(leave.from_date, leave.to_date) }}
									</Badge>
								</div>
							</div>
						</div>
					</div>
				</Card>

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

				<div class="bg-blue-600 rounded-2xl p-6 text-white shadow-lg shadow-blue-100">
					<h4 class="text-sm font-bold opacity-90 uppercase tracking-wider">System Insights</h4>
					<p class="mt-3 text-sm leading-relaxed opacity-80">
						You currently have <b>{{ inProgressCount }}</b> active tasks. 
						{{ inProgressCount > 5 ? 'Try delegating some items to improve project velocity.' : 'Current workload is well within capacity.' }}
					</p>
					<Button variant="ghost" class="mt-4 !text-white !bg-white/10 hover:!bg-white/20 !border-none">
						View Reports
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
import { computed, reactive, watch } from "vue"

dayjs.extend(relativeTime)

// Icons
import IconBriefcase from "~icons/lucide/briefcase"
import IconCalendar from "~icons/lucide/calendar"
import IconCheckCircle from "~icons/lucide/check-circle"
import IconClock from "~icons/lucide/clock"
import IconList from "~icons/lucide/list"
import IconRefresh from "~icons/lucide/refresh-cw"
import { session } from "../data/session"

const leavesFilters = reactive({
	range: "7", // "7", "14", "30", "custom"
	from_date: dayjs().format("YYYY-MM-DD"),
	to_date: dayjs().add(7, "day").format("YYYY-MM-DD"),
})

const upcomingLeaves = createResource({
	url: "tactix.api.generic.get_upcoming_leaves",
	auto: true,
	params: {
		from_date: leavesFilters.from_date,
		to_date: leavesFilters.to_date,
	},
	initialData: [],
})

watch(
	() => leavesFilters.range,
	(newRange) => {
		if (newRange !== "custom") {
			const days = Number.parseInt(newRange) || 7
			leavesFilters.from_date = dayjs().format("YYYY-MM-DD")
			leavesFilters.to_date = dayjs().add(days, "day").format("YYYY-MM-DD")
		}
	},
)

watch(
	() => [leavesFilters.from_date, leavesFilters.to_date],
	([newFrom, newTo]) => {
		upcomingLeaves.params = {
			from_date: newFrom,
			to_date: newTo,
		}
		upcomingLeaves.reload()
	},
)

function getRelativeLeaveStatus(fromDate, toDate) {
	const today = dayjs().startOf("day")
	const start = dayjs(fromDate).startOf("day")
	const end = dayjs(toDate).startOf("day")

	if (today.isAfter(end)) {
		return "Ended"
	}
	if (
		today.isSame(start) ||
		(today.isAfter(start) && today.isBefore(end)) ||
		today.isSame(end)
	) {
		return "Active Today"
	}
	const diffDays = start.diff(today, "day")
	if (diffDays === 1) {
		return "Tomorrow"
	}
	return `In ${diffDays} days`
}

function getLeaveStatusTheme(fromDate, toDate) {
	const today = dayjs().startOf("day")
	const start = dayjs(fromDate).startOf("day")
	const end = dayjs(toDate).startOf("day")

	if (today.isAfter(end)) {
		return "gray"
	}
	if (
		today.isSame(start) ||
		(today.isAfter(start) && today.isBefore(end)) ||
		today.isSame(end)
	) {
		return "green"
	}
	const diffDays = start.diff(today, "day")
	if (diffDays === 1) {
		return "orange"
	}
	return "blue"
}

function formatLeaveDates(fromDate, toDate) {
	const start = dayjs(fromDate)
	const end = dayjs(toDate)
	if (start.year() === end.year()) {
		return `${start.format("MMM D")} - ${end.format("MMM D, YYYY")}`
	}
	return `${start.format("MMM D, YYYY")} - ${end.format("MMM D, YYYY")}`
}

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

const statsConfig = computed(() => [
	{
		label: "Active Projects",
		value: activeProjectsCount.value,
		icon: IconBriefcase,
		color: "text-blue-600",
		bg: "bg-blue-50",
	},
	{
		label: "Total Tasks",
		value: totalTasksCount.value,
		icon: IconList,
		color: "text-indigo-600",
		bg: "bg-indigo-50",
	},
	{
		label: "In Progress",
		value: inProgressCount.value,
		icon: IconClock,
		color: "text-orange-600",
		bg: "bg-orange-50",
	},
	{
		label: "Completed",
		value: taskSummary.data?.completed || 0,
		icon: IconCheckCircle,
		color: "text-green-600",
		bg: "bg-green-50",
	},
])

function reloadDashboardData() {
	tasks.reload()
	taskSummary.reload()
	upcomingLeaves.reload()
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