<template>
  <div class="flex flex-col h-full overflow-hidden font-sans min-h-0">
    <!-- Top Filter Header -->
    <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3 mx-4 mt-4 flex-shrink-0">
      <div class="flex items-center gap-2">
        <div class="p-1.5 rounded-lg bg-blue-50">
          <IconTrendingUp class="w-5 h-5 text-blue-600" />
        </div>
        <div>
          <h1 class="text-base font-black text-slate-900 leading-tight">Performance Dashboard</h1>
          <p class="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Analytics & SLA insights</p>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <!-- Timespan Selector -->
        <select 
          v-model="selectedTimespan"
          class="px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-600 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 cursor-pointer min-w-[130px]"
        >
          <option value="">All Time</option>
          <option value="today">Today</option>
          <option value="yesterday">Yesterday</option>
          <option value="this_week">This Week</option>
          <option value="last_week">Last Week</option>
          <option value="this_month">This Month</option>
          <option value="last_month">Last Month</option>
          <option value="this_year">This Year</option>
        </select>

        <!-- Employee Selector (Admin only) -->
        <select 
          v-if="employeeInfoResource.data?.is_system_manager"
          v-model="selectedEmployee"
          class="px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-600 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 cursor-pointer min-w-[160px]"
        >
          <option value="">All Employees</option>
          <option v-for="emp in employeeOptionsResource.data" :key="emp.value" :value="emp.value">
            {{ emp.label }}
          </option>
        </select>

        <Button
          variant="outline"
          class="!text-slate-600 !px-3 !h-8 border border-slate-200 hover:bg-slate-50 transition-all"
          @click="fetchPerformance"
        >
          <template #prefix><IconRefresh class="w-4 h-4 text-slate-500" /></template>
        </Button>
      </div>
    </div>

    <!-- Main Dashboard Scrollable Area -->
    <div class="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar min-h-0">
      <!-- Loading Spinner -->
      <div v-if="performanceResource.loading" class="flex flex-col items-center justify-center py-20 space-y-3">
        <div class="w-8 h-8 border-4 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
        <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Aggregating Metrics...</p>
      </div>

      <template v-else-if="performanceData">
        <!-- KPI Metrics Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Task Completion Rate Card -->
          <Card class="!shadow-sm bg-white border border-slate-100 p-4">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Task Completion Rate</span>
              <div class="p-1.5 rounded-lg bg-blue-50">
                <IconCheckSquare class="w-4 h-4 text-blue-500" />
              </div>
            </div>
            <div class="text-2xl font-black mt-2 text-slate-900 leading-none">
              {{ performanceData.task?.completion_rate?.toFixed(1) || '0.0' }}%
            </div>
            <div class="mt-3">
              <div class="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                <div 
                  class="bg-blue-500 h-full rounded-full transition-all duration-500"
                  :style="{ width: `${performanceData.task?.completion_rate || 0}%` }"
                ></div>
              </div>
            </div>
            <div class="text-[10px] text-slate-400 font-semibold mt-2">
              {{ performanceData.task?.completed || 0 }} of {{ performanceData.task?.total || 0 }} tasks completed
            </div>
          </Card>

          <!-- Ticket SLA Response Card -->
          <Card class="!shadow-sm bg-white border border-slate-100 p-4">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Avg First Response</span>
              <div class="p-1.5 rounded-lg bg-indigo-50">
                <IconClock class="w-4 h-4 text-indigo-500" />
              </div>
            </div>
            <div class="text-2xl font-black mt-2 text-slate-900 leading-none">
              {{ formatDuration(performanceData.ticket?.avg_response_time) }}
            </div>
            <div class="mt-2.5">
              <Badge 
                :theme="getSLARatingColor(performanceData.ticket?.avg_response_time)" 
                variant="subtle" 
                class="font-black text-[10px] uppercase tracking-wide px-2 py-0.5"
              >
                {{ getSLARatingText(performanceData.ticket?.avg_response_time) }}
              </Badge>
            </div>
            <div class="text-[10px] text-slate-400 font-semibold mt-2">
              Based on {{ performanceData.ticket?.total || 0 }} tickets
            </div>
          </Card>

          <!-- Total Logged Hours Card -->
          <Card class="!shadow-sm bg-white border border-slate-100 p-4">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total logged Hours</span>
              <div class="p-1.5 rounded-lg bg-emerald-50">
                <IconClock class="w-4 h-4 text-emerald-500" />
              </div>
            </div>
            <div class="text-2xl font-black mt-2 text-slate-900 leading-none">
              {{ performanceData.timesheet?.total_hours?.toFixed(1) || '0.0' }} hrs
            </div>
            <div class="mt-4 text-[10px] text-slate-400 font-semibold">
              Across {{ performanceData.timesheet?.active_days || 0 }} active logging days
            </div>
          </Card>

          <!-- Avg Daily Logged Hours Card -->
          <Card class="!shadow-sm bg-white border border-slate-100 p-4">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Avg Daily Hours</span>
              <div class="p-1.5 rounded-lg bg-orange-50">
                <IconCalendar class="w-4 h-4 text-orange-500" />
              </div>
            </div>
            <div class="text-2xl font-black mt-2 text-slate-900 leading-none">
              {{ performanceData.timesheet?.avg_daily_hours?.toFixed(1) || '0.0' }} hrs
            </div>
            <div class="mt-3">
              <div class="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                <div 
                  class="bg-orange-500 h-full rounded-full transition-all duration-500"
                  :style="{ width: `${Math.min((performanceData.timesheet?.avg_daily_hours || 0) / 8 * 100, 100)}%` }"
                ></div>
              </div>
            </div>
            <div class="text-[10px] text-slate-400 font-semibold mt-2">
              Compared to 8 hrs daily benchmark
            </div>
          </Card>
        </div>

        <!-- Analytical Breakdown Sections -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Activity Distribution Card (2 Columns width on lg) -->
          <Card class="!shadow-sm bg-white border border-slate-100 p-6 lg:col-span-2 space-y-6">
            <div>
              <h2 class="text-sm font-black text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                <IconBriefcase class="w-4 h-4 text-slate-400" /> Logged Hours by Activity
              </h2>
              <p class="text-xs text-slate-400 font-medium">Workload distribution from timesheet details</p>
            </div>

            <div class="space-y-4">
              <div 
                v-for="activity in resolvedActivities" 
                :key="activity.name" 
                class="space-y-1.5"
              >
                <div class="flex justify-between text-xs font-bold text-slate-600">
                  <span>{{ activity.name }}</span>
                  <span class="font-black text-slate-900">{{ activity.hours?.toFixed(1) }} hrs ({{ activity.percentage }}%)</span>
                </div>
                <div class="w-full bg-slate-50 h-2.5 rounded-full overflow-hidden border border-slate-100">
                  <div 
                    class="h-full rounded-full transition-all duration-500"
                    :class="activity.barColor"
                    :style="{ width: `${activity.percentage}%` }"
                  ></div>
                </div>
              </div>
              <div v-if="resolvedActivities.length === 0" class="text-center py-10 text-slate-400 italic font-semibold">
                No active timesheet logs found in this period.
              </div>
            </div>
          </Card>

          <!-- Ticket Resolution & Overdues Column -->
          <div class="space-y-6">
            <!-- Ticket SLAs -->
            <Card class="!shadow-sm bg-white border border-slate-100 p-6 space-y-4">
              <div>
                <h2 class="text-sm font-black text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <IconShieldAlert class="w-4 h-4 text-slate-400" /> Ticket SLA Performance
                </h2>
                <p class="text-xs text-slate-400 font-medium">Speed metrics for customer satisfaction</p>
              </div>

              <div class="space-y-4 border-t pt-4 text-xs font-semibold text-slate-500">
                <div class="flex justify-between">
                  <span>Ticket Resolution Rate</span>
                  <span class="font-extrabold text-slate-800">{{ performanceData.ticket?.resolution_rate?.toFixed(1) || '0.0' }}%</span>
                </div>
                <div class="flex justify-between">
                  <span>Avg Initial Response Time</span>
                  <span class="font-extrabold text-slate-800">{{ formatDuration(performanceData.ticket?.avg_response_time) }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Avg Ticket Resolution Time</span>
                  <span class="font-extrabold text-slate-800">{{ formatDuration(performanceData.ticket?.avg_close_time) }}</span>
                </div>
              </div>
            </Card>

            <!-- Tasks Efficiency -->
            <Card class="!shadow-sm bg-white border border-slate-100 p-6 space-y-4">
              <div>
                <h2 class="text-sm font-black text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <IconAlertCircle class="w-4 h-4 text-slate-400" /> Task Status Efficiency
                </h2>
                <p class="text-xs text-slate-400 font-medium">Overdues and tracking ratios</p>
              </div>

              <div class="space-y-4 border-t pt-4 text-xs font-semibold text-slate-500">
                <div class="flex justify-between">
                  <span>Total Tasks Assigned</span>
                  <span class="font-extrabold text-slate-800">{{ performanceData.task?.total || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Completed Tasks</span>
                  <span class="font-extrabold text-green-600">{{ performanceData.task?.completed || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Overdue Tasks</span>
                  <span class="font-extrabold" :class="performanceData.task?.overdue > 0 ? 'text-red-500 font-black' : 'text-slate-800'">
                    {{ performanceData.task?.overdue || 0 }}
                  </span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button, Card, createResource } from "frappe-ui"
import { computed, ref, watch } from "vue"

// Icons
import IconTrendingUp from "~icons/lucide/trending-up"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconClock from "~icons/lucide/clock"
import IconCalendar from "~icons/lucide/calendar"
import IconCheckSquare from "~icons/lucide/check-square"
import IconBriefcase from "~icons/lucide/briefcase"
import IconShieldAlert from "~icons/lucide/shield-alert"
import IconAlertCircle from "~icons/lucide/alert-circle"
import IconUser from "~icons/lucide/user"

// Filter values
const selectedTimespan = ref("this_month")
const selectedEmployee = ref("")

// API Resources
const employeeInfoResource = createResource({
  url: "tactix.api.timesheet.get_employee_info",
  initialData: {},
  auto: true
})

const employeeOptionsResource = createResource({
  url: "tactix.api.timesheet.get_employees",
  initialData: []
})

const performanceResource = createResource({
  url: "tactix.api.performance.get_performance_data",
  initialData: {}
})

// Trigger employee info loading options for admins
watch(() => employeeInfoResource.data, (val) => {
  if (val && val.is_system_manager) {
    employeeOptionsResource.fetch()
  }
}, { immediate: true })

// Main fetch performance logic
function fetchPerformance() {
  performanceResource.fetch({
    employee: selectedEmployee.value,
    timespan: selectedTimespan.value
  })
}

// Watch filters
watch([selectedTimespan, selectedEmployee], () => {
  fetchPerformance()
})

// Initial fetch
fetchPerformance()

const performanceData = computed(() => performanceResource.data)

// Format raw seconds into a friendly duration representation
function formatDuration(seconds) {
  if (!seconds || seconds <= 0) return "—"
  const sec = parseFloat(seconds)
  if (sec < 60) {
    return `${Math.round(sec)} sec`
  }
  const min = sec / 60
  if (min < 60) {
    return `${Math.round(min)} min`
  }
  const hrs = min / 60
  if (hrs < 24) {
    return `${hrs.toFixed(1)} hrs`
  }
  const days = hrs / 24
  return `${days.toFixed(1)} days`
}

// SLA compliance color coding
function getSLARatingColor(seconds) {
  if (!seconds || seconds <= 0) return "gray"
  const hrs = seconds / 3600
  if (hrs < 2) return "green"
  if (hrs < 8) return "emerald"
  if (hrs < 24) return "blue"
  return "orange"
}

// SLA text labels
function getSLARatingText(seconds) {
  if (!seconds || seconds <= 0) return "No SLA Score"
  const hrs = seconds / 3600
  if (hrs < 2) return "Elite (SLA A+)"
  if (hrs < 8) return "Fast (SLA A)"
  if (hrs < 24) return "Compliant (SLA B)"
  return "Warning (SLA C)"
}

// Map activity hours to beautiful color codes and compute percentages
const activityColors = {
  Execution: { bar: "bg-blue-500" },
  Planning: { bar: "bg-indigo-500" },
  Research: { bar: "bg-purple-500" },
  Communication: { bar: "bg-teal-500" },
  "Proposal Writing": { bar: "bg-orange-500" }
}

const resolvedActivities = computed(() => {
  const activities = performanceData.value?.timesheet?.activities || {}
  const total = performanceData.value?.timesheet?.total_hours || 0
  
  return Object.entries(activities).map(([name, hours]) => {
    const percentage = total > 0 ? Math.round((hours / total) * 100) : 0
    const color = activityColors[name] || { bar: "bg-slate-400" }
    return {
      name,
      hours,
      percentage,
      barColor: color.bar
    }
  }).sort((a, b) => b.hours - a.hours)
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar,
:deep(*::-webkit-scrollbar) {
  height: 5px !important;
  width: 5px !important;
}
.custom-scrollbar::-webkit-scrollbar-thumb,
:deep(*::-webkit-scrollbar-thumb) {
  background: #cbd5e1 !important;
  border-radius: 10px !important;
}
:deep(*::-webkit-scrollbar-track) {
  background: transparent !important;
}
</style>