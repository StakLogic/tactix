<template>
  <div class="flex flex-col h-full overflow-hidden font-sans min-h-0">
    <!-- Top Stats / KPIs Header -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 p-4 flex-shrink-0">
      <Card class="!shadow-sm bg-white border border-slate-100 hover:border-slate-200 transition-all duration-200">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Hours logged</span>
          <div class="p-1.5 rounded-lg bg-blue-50">
            <IconClock class="w-4 h-4 text-blue-500" />
          </div>
        </div>
        <div class="text-2xl font-black mt-2 text-slate-900 flex items-center h-8">
          <template v-if="timesheetsSummary.loading">
            <div class="w-4 h-4 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
          </template>
          <span v-else>{{ timesheetsSummary.data?.total_hours || 0 }} hrs</span>
        </div>
      </Card>

      <Card class="!shadow-sm bg-white border border-slate-100 hover:border-slate-200 transition-all duration-200">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Days Logged</span>
          <div class="p-1.5 rounded-lg bg-indigo-50">
            <IconCalendar class="w-4 h-4 text-indigo-500" />
          </div>
        </div>
        <div class="text-2xl font-black mt-2 text-slate-900 flex items-center h-8">
          <template v-if="timesheetsSummary.loading">
            <div class="w-4 h-4 border-2 border-slate-200 border-t-indigo-500 rounded-full animate-spin"></div>
          </template>
          <span v-else>{{ timesheetsSummary.data?.active_days || 0 }} days</span>
        </div>
      </Card>

      <Card class="!shadow-sm bg-white border border-slate-100 hover:border-slate-200 transition-all duration-200">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Submitted Timesheets</span>
          <div class="p-1.5 rounded-lg bg-green-50">
            <IconCheckCircle class="w-4 h-4 text-green-500" />
          </div>
        </div>
        <div class="text-2xl font-black mt-2 text-slate-900 flex items-center h-8">
          <template v-if="timesheetsSummary.loading">
            <div class="w-4 h-4 border-2 border-slate-200 border-t-green-500 rounded-full animate-spin"></div>
          </template>
          <span v-else>{{ timesheetsSummary.data?.submitted_count || 0 }}</span>
        </div>
      </Card>

      <Card class="!shadow-sm bg-white border border-slate-100 hover:border-slate-200 transition-all duration-200">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Draft Timesheets</span>
          <div class="p-1.5 rounded-lg bg-orange-50">
            <IconAlertCircle class="w-4 h-4 text-orange-500" />
          </div>
        </div>
        <div class="text-2xl font-black mt-2 text-slate-900 flex items-center h-8">
          <template v-if="timesheetsSummary.loading">
            <div class="w-4 h-4 border-2 border-slate-200 border-t-orange-500 rounded-full animate-spin"></div>
          </template>
          <span v-else>{{ timesheetsSummary.data?.draft_count || 0 }}</span>
        </div>
      </Card>
    </div>

    <!-- Actions & Filter Header -->
    <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3 mx-4 my-2 flex-shrink-0">
      <div class="filter-row flex flex-nowrap overflow-x-auto pb-1.5 gap-2 w-full custom-scrollbar sm:flex-wrap sm:overflow-visible sm:pb-0 sm:items-center sm:gap-2">
        <select 
          v-model="selectedStatus"
          :class="[
            'px-3 h-9 rounded-lg border text-xs font-semibold focus:outline-none cursor-pointer min-w-[130px] shrink-0 transition-all duration-200',
            selectedStatus !== ''
              ? 'border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/10 font-black shadow-sm ring-1 ring-[var(--primary-color)]/10 focus:ring-2 focus:ring-[var(--primary-color)]/20 dark:border-indigo-400 dark:text-indigo-300'
              : 'border-slate-200 bg-slate-50 text-slate-600 dark:text-slate-300 dark:bg-slate-900 dark:border-slate-700 focus:ring-2 focus:ring-blue-500/20'
          ]"
        >
          <option value="">All Statuses</option>
          <option value="Draft">Draft</option>
          <option value="Submitted">Submitted</option>
        </select>

        <select 
          v-model="selectedTimespan"
          :class="[
            'px-3 h-9 rounded-lg border text-xs font-semibold focus:outline-none cursor-pointer min-w-[130px] shrink-0 transition-all duration-200',
            selectedTimespan !== ''
              ? 'border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/10 font-black shadow-sm ring-1 ring-[var(--primary-color)]/10 focus:ring-2 focus:ring-[var(--primary-color)]/20 dark:border-indigo-400 dark:text-indigo-300'
              : 'border-slate-200 bg-slate-50 text-slate-600 dark:text-slate-300 dark:bg-slate-900 dark:border-slate-700 focus:ring-2 focus:ring-blue-500/20'
          ]"
        >
          <option value="">All Time</option>
          <option value="today">Today</option>
          <option value="yesterday">Yesterday</option>
          <option value="this_week">This Week</option>
          <option value="last_week">Last Week</option>
          <option value="this_month">This Month</option>
          <option value="last_month">Last Month</option>
        </select>

        <select 
          v-if="employeeInfoResource.data?.is_system_manager"
          v-model="selectedEmployee"
          :class="[
            'px-3 h-9 rounded-lg border text-xs font-semibold focus:outline-none cursor-pointer min-w-[150px] shrink-0 transition-all duration-200',
            selectedEmployee !== ''
              ? 'border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/10 font-black shadow-sm ring-1 ring-[var(--primary-color)]/10 focus:ring-2 focus:ring-[var(--primary-color)]/20 dark:border-indigo-400 dark:text-indigo-300'
              : 'border-slate-200 bg-slate-50 text-slate-600 dark:text-slate-300 dark:bg-slate-900 dark:border-slate-700 focus:ring-2 focus:ring-blue-500/20'
          ]"
        >
          <option value="">All Employees</option>
          <option v-for="emp in employeeOptionsResource.data" :key="emp.value" :value="emp.value">
            {{ emp.label }}
          </option>
        </select>
      </div>

      <div class="flex items-center gap-2">
        <Button
          variant="outline"
          class="!text-slate-600 !px-3 !h-9 border border-slate-200 hover:bg-slate-50 transition-all"
          @click="reloadTimesheets"
        >
          <template #prefix><IconRefresh class="w-4 h-4 text-slate-500" /></template>
        </Button>

        <Button
          variant="solid"
          class="!text-xs !px-5 !h-9 !shadow-md transition-all bg-blue-600 hover:bg-blue-700 text-white font-bold"
          @click="openCreateDialog"
        >
          <template #prefix><IconPlus class="w-4 h-4" /></template> New Timesheet
        </Button>
      </div>
    </div>

    <!-- Timesheets List Table -->
    <div class="flex-1 overflow-y-auto md:overflow-hidden px-4 pb-4 flex flex-col min-h-0">
      <div class="bg-white rounded-xl border border-slate-800 dark:border-slate-700 shadow-sm flex-col overflow-hidden min-h-[420px] md:min-h-0 md:flex-1 md:overflow-hidden flex">
        <ListView
          class="h-full flex flex-col min-h-0"
          :columns="columns"
          :rows="timesheets.data?.timesheets || []"
          :options="{
            selectable: false,
            showTooltip: true,
            resizeColumn: true,
            onRowClick: (row) => openTimesheetDetails(row)
          }"
          row-key="name"
        >
          <ListHeader class="shrink-0 bg-slate-50 border-b border-slate-200 shadow-sm">
            <ListHeaderItem v-for="col in columns" :key="col.key" :item="col">
              <template #prefix="{ item }">
                <component :is="item.icon" class="size-3.5 text-slate-400" />
              </template>
            </ListHeaderItem>
          </ListHeader>

          <div class="flex-grow md:flex-1 overflow-y-auto custom-scrollbar relative min-h-0 max-h-[480px] md:max-h-none">
            <ListRows>
              <ListRow
                v-slot="{ column, item }"
                v-for="row in (timesheets.data?.timesheets || [])"
                :key="row.name"
                :row="row"
              >
                <ListRowItem :item="item">
                  <template v-if="column.key === 'name'">
                    <span class="font-bold text-blue-600">#{{ row.name }}</span>
                  </template>

                  <template v-if="column.key === 'start_date'">
                    <span class="text-xs text-slate-700 font-medium">
                      {{ row.start_date ? formatDate(row.start_date) : '' }}
                    </span>
                  </template>

                  <template v-if="column.key === 'total_hours'">
                    <Badge theme="blue" variant="subtle" class="font-semibold !px-2.5 !py-1 text-xs">
                      {{ row.total_hours }} hrs
                    </Badge>
                  </template>

                  <template v-if="column.key === 'status'">
                    <Badge
                      :theme="row.status === 'Submitted' ? 'green' : 'orange'"
                      variant="subtle"
                      class="font-semibold !px-2.5 !py-1 text-xs"
                    >
                      {{ row.status }}
                    </Badge>
                  </template>
                </ListRowItem>
              </ListRow>
            </ListRows>
          </div>
        </ListView>

        <!-- Pagination -->
        <div class="flex items-center justify-between border-t border-slate-100 bg-white px-4 py-3 sm:px-6">
          <div class="flex flex-1 justify-between sm:hidden">
            <Button :disabled="currentPage === 1" @click="currentPage--" variant="ghost">Previous</Button>
            <Button :disabled="currentPage >= totalPages" @click="currentPage--" variant="ghost">Next</Button>
          </div>
          <div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
            <p class="text-xs text-slate-500">
              Showing
              <span class="font-bold text-slate-800">{{ totalCount > 0 ? (currentPage - 1) * pageLength + 1 : 0 }}</span>
              to
              <span class="font-bold text-slate-800">{{ Math.min(currentPage * pageLength, totalCount) }}</span>
              of
              <span class="font-bold text-slate-800">{{ totalCount }}</span>
              results
            </p>
            <nav class="isolate inline-flex -space-x-px rounded-lg bg-slate-50 p-1 border border-slate-200/50">
              <button
                @click="currentPage = Math.max(1, currentPage - 1)"
                :disabled="currentPage === 1"
                class="relative inline-flex items-center rounded-md p-1 text-slate-400 hover:bg-white hover:text-slate-700 disabled:opacity-50 transition-all mr-1"
              >
                <IconChevronLeft class="w-3.5 h-3.5" />
              </button>
              <button
                @click="currentPage = Math.min(totalPages, currentPage + 1)"
                :disabled="currentPage === totalPages"
                class="relative inline-flex items-center rounded-md p-1 text-slate-400 hover:bg-white hover:text-slate-700 disabled:opacity-50 transition-all ml-1"
              >
                <IconChevronRight class="w-3.5 h-3.5" />
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Timesheet Dialog -->
    <Dialog v-model="showCreateDialog" :disable-outside-click-to-close="true" :options="dialogOptions">
      <template #body-content>
        <div class="space-y-6 py-2">
          <p v-if="formError" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-2.5 shadow-sm font-semibold flex items-center gap-2">
            <IconAlertCircle class="w-4 h-4 text-red-500 flex-shrink-0" /> {{ formError }}
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Date Picker -->
            <FormControl 
              type="date" 
              label="Timesheet Date *" 
              v-model="timesheetForm.date" 
            />
            <!-- Employee Info -->
            <template v-if="employeeInfoResource.data?.is_system_manager">
              <FormControl 
                type="select" 
                label="Employee *" 
                v-model="timesheetForm.employee" 
                :options="[{label: 'Select Employee', value: ''}, ...employeeOptionsResource.data]" 
              />
            </template>
            <template v-else>
              <div class="space-y-1.5">
                <label class="block text-xs text-slate-600 font-medium">Employee *</label>
                <div class="px-3 h-[2.25rem] bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 font-medium flex items-center gap-2">
                  <div class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
                  {{ employeeInfoResource.data?.employee_name || 'Loading profile...' }}
                </div>
              </div>
            </template>
          </div>

          <!-- Dynamic Time Logs Table -->
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <label class="text-xs font-black text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                <IconClock class="w-4 h-4 text-slate-400" /> Time Log Rows
              </label>
              <Button
                variant="outline"
                size="sm"
                class="!text-blue-600 hover:!bg-blue-50 !px-4 !h-8 font-semibold border-blue-200 hover:border-blue-300 rounded-lg transition-all"
                @click="addRow"
              >
                <template #prefix><IconPlus class="w-3.5 h-3.5" /></template> Add Task Row
              </Button>
            </div>

            <div class="border border-slate-200 rounded-xl overflow-x-auto shadow-sm max-h-[300px] overflow-y-auto custom-scrollbar">
              <table class="w-full text-left text-xs border-collapse">
                <thead class="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-semibold sticky top-0 z-10">
                  <tr>
                    <th class="px-4 py-3 w-1/3">Task</th>
                    <th class="px-4 py-3 w-1/4">Activity *</th>
                    <th class="px-4 py-3 w-24 text-right">Hours</th>
                    <th class="px-4 py-3">Description</th>
                    <th class="px-4 py-3 w-10 text-right"></th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 bg-white">
                  <tr v-for="(row, idx) in timesheetForm.time_logs" :key="idx" class="hover:bg-slate-50/20 transition-colors">
                    <td class="px-2 py-2">
                      <select 
                        v-model="row.task" 
                        class="w-full h-9 px-2.5 bg-slate-50 hover:bg-slate-100/50 focus:bg-white border border-slate-200 hover:border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 rounded-lg outline-none text-xs font-medium text-slate-700 transition-all cursor-pointer"
                      >
                        <option value="">Select Task (Optional)</option>
                        <option v-for="t in taskOptionsResource.data" :key="t.value" :value="t.value">
                          {{ t.label }}
                        </option>
                      </select>
                    </td>
                    <td class="px-2 py-2">
                      <select 
                        v-model="row.activity_type" 
                        class="w-full h-9 px-2.5 bg-slate-50 hover:bg-slate-100/50 focus:bg-white border border-slate-200 hover:border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 rounded-lg outline-none text-xs font-medium text-slate-700 transition-all cursor-pointer"
                      >
                        <option value="Execution">Execution</option>
                        <option value="Planning">Planning</option>
                        <option value="Research">Research</option>
                        <option value="Communication">Communication</option>
                        <option value="Proposal Writing">Proposal Writing</option>
                      </select>
                    </td>
                    <td class="px-2 py-2">
                      <input 
                        v-model.number="row.hours" 
                        type="number" 
                        step="0.5" 
                        min="0.1" 
                        class="w-full h-9 px-2.5 bg-slate-50 hover:bg-slate-100/50 focus:bg-white border border-slate-200 hover:border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 rounded-lg outline-none text-xs font-semibold text-slate-800 text-right transition-all" 
                      />
                    </td>
                    <td class="px-2 py-2">
                      <input 
                        v-model="row.description" 
                        placeholder="Provide details..." 
                        class="w-full h-9 px-3 bg-slate-50 hover:bg-slate-100/50 focus:bg-white border border-slate-200 hover:border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 rounded-lg outline-none text-xs text-slate-700 transition-all" 
                      />
                    </td>
                    <td class="px-2 py-2 text-right">
                      <button 
                        class="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                        @click="removeRow(idx)"
                      >
                        <IconX class="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                  <tr v-if="timesheetForm.time_logs.length === 0">
                    <td colspan="6" class="px-4 py-8 text-center text-slate-400 italic font-semibold">
                      No rows added yet. Add a row to get started.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="flex items-center justify-between p-3.5 bg-blue-50/50 rounded-xl border border-blue-100/50 text-xs font-bold">
              <span class="text-blue-700 uppercase tracking-wider font-extrabold">Total Logged Hours</span>
              <span class="text-sm font-black text-blue-800 bg-blue-100/50 px-3.5 py-1 rounded-lg">{{ computedTotalHours }} hrs</span>
            </div>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- View Timesheet Details Dialog -->
    <Dialog v-model="showViewDialog" :disable-outside-click-to-close="true" :options="viewDialogOptions">
      <template #body-content>
        <div class="space-y-6 py-2" v-if="selectedTimesheet">
          <p v-if="viewError" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-2.5 shadow-sm font-semibold flex items-center gap-2">
            <IconAlertCircle class="w-4 h-4 text-red-500 flex-shrink-0" /> {{ viewError }}
          </p>
          <!-- Summary Cards Row -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <!-- Date Card -->
            <div class="bg-blue-50/40 border border-blue-100 rounded-xl p-4 flex flex-col justify-between shadow-sm">
              <div class="flex items-center justify-between mb-2">
                <span class="text-[10px] font-semibold text-blue-600 uppercase tracking-wider">Date</span>
                <div class="p-1.5 rounded-lg bg-blue-100/50">
                  <IconCalendar class="w-3.5 h-3.5 text-blue-600" />
                </div>
              </div>
              <div class="text-lg font-black text-blue-800 leading-none">
                {{ formatDate(selectedTimesheet.start_date) }}
              </div>
            </div>

            <!-- Employee Card -->
            <div class="bg-indigo-50/40 border border-indigo-100 rounded-xl p-4 flex flex-col justify-between shadow-sm">
              <div class="flex items-center justify-between mb-2">
                <span class="text-[10px] font-semibold text-indigo-600 uppercase tracking-wider">Employee</span>
                <div class="p-1.5 rounded-lg bg-indigo-100/50">
                  <IconUser class="w-3.5 h-3.5 text-indigo-600" />
                </div>
              </div>
              <div class="text-sm font-black text-indigo-800 truncate leading-none">
                {{ selectedTimesheet.employee_name || selectedTimesheet.employee || '—' }}
              </div>
            </div>

            <!-- Total Hours Card -->
            <div class="bg-emerald-50/40 border border-emerald-100 rounded-xl p-4 flex flex-col justify-between shadow-sm">
              <div class="flex items-center justify-between mb-2">
                <span class="text-[10px] font-semibold text-emerald-600 uppercase tracking-wider">Total hours</span>
                <div class="p-1.5 rounded-lg bg-emerald-100/50">
                  <IconClock class="w-3.5 h-3.5 text-emerald-600" />
                </div>
              </div>
              <div class="text-lg font-black text-emerald-800 leading-none">
                {{ selectedTimesheet.total_hours }} hrs
              </div>
            </div>
          </div>

          <!-- Time Logs Details Table -->
          <div class="border border-slate-200 rounded-xl overflow-x-auto shadow-sm">
            <table class="w-full text-left text-xs border-collapse">
              <thead class="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-semibold">
                <tr>
                  <th class="px-4 py-3.5">Task</th>
                  <th class="px-4 py-3.5">Activity</th>
                  <th class="px-4 py-3.5 text-right w-24">Hours</th>
                  <th class="px-4 py-3.5">Description</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 bg-white">
                <tr v-for="(log, idx) in selectedTimesheet.time_logs" :key="idx" class="hover:bg-slate-50/40 transition-colors duration-150">
                  <td class="px-4 py-3.5 font-bold text-slate-800">
                    {{ log.task ? (log.task_subject ? `${log.task_subject} (${log.task})` : log.task) : '—' }}
                  </td>
                  <td class="px-4 py-3.5">
                    <Badge theme="gray" variant="subtle" class="!px-2.5 !py-1 text-[11px] font-semibold">{{ log.activity_type }}</Badge>
                  </td>
                  <td class="px-4 py-3.5 text-right font-black text-slate-700">{{ log.hours }} hrs</td>
                  <td class="px-4 py-3.5 text-slate-500 whitespace-pre-wrap leading-relaxed">{{ log.description || '—' }}</td>

                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import dayjs from "dayjs"
import {
	Badge,
	Button,
	Card,
	Dialog,
	FormControl,
	ListHeader,
	ListHeaderItem,
	ListRow,
	ListRowItem,
	ListRows,
	ListView,
	createResource,
} from "frappe-ui"
import { computed, reactive, ref, watch } from "vue"

import IconAlertCircle from "~icons/lucide/alert-circle"
import IconCalendar from "~icons/lucide/calendar"
import IconCheckCircle from "~icons/lucide/check-circle"
import IconChevronLeft from "~icons/lucide/chevron-left"
import IconChevronRight from "~icons/lucide/chevron-right"
// Icons
import IconClock from "~icons/lucide/clock"
import IconHash from "~icons/lucide/hash"
import IconPlus from "~icons/lucide/plus"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconSearch from "~icons/lucide/search"
import IconUser from "~icons/lucide/user"
import IconX from "~icons/lucide/x"

// State variables
const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const selectedStatus = ref("")
const selectedTimespan = ref("")
const selectedEmployee = ref("")
const currentPage = ref(1)
const pageLength = 20
const saving = ref(false)
const formError = ref("")
const viewError = ref("")

// Selected timesheet for viewing
const selectedTimesheet = ref(null)

const parseError = (err) => {
	if (err.messages && err.messages.length > 0) {
		return err.messages
			.map((m) => {
				try {
					const parsed = JSON.parse(m)
					return parsed.message || m
				} catch {
					return m
				}
			})
			.join("\n")
	}

	if (err.exc) {
		try {
			const parsed = JSON.parse(err.exc)
			if (Array.isArray(parsed)) {
				return parsed
					.map((item) => (typeof item === "string" ? item : item.message))
					.join("\n")
			}
		} catch {
			// Not JSON
		}
	}

	return err.message || "An unexpected error occurred."
}

// Form states
const timesheetForm = reactive({
	date: new Date().toISOString().split("T")[0],
	employee: "",
	time_logs: [],
})

// Initialize filters
const timesheetFilters = computed(() => {
	const f = {}
	if (selectedStatus.value) {
		f.status = selectedStatus.value
	}
	if (selectedTimespan.value) {
		f.timespan = selectedTimespan.value
	}
	if (selectedEmployee.value && employeeInfoResource.data?.is_system_manager) {
		f.employee = selectedEmployee.value
	}
	return f
})

// Columns
const columns = [
	{ label: "Timesheet ID", key: "name", width: "160px", icon: IconHash },
	{ label: "Date", key: "start_date", width: "160px", icon: IconCalendar },
	{ label: "Employee", key: "employee_name", width: "2.5fr", icon: IconUser },
	{ label: "Total Hours", key: "total_hours", width: "150px", icon: IconClock },
	{ label: "Status", key: "status", width: "130px", icon: IconAlertCircle },
]

// API Resources
const timesheets = createResource({
	url: "tactix.api.timesheet.get_timesheets",
	initialData: { timesheets: [], total_count: 0 },
	transform: (data) => {
		if (Array.isArray(data)) {
			return { timesheets: data, total_count: data.length }
		}
		return data || { timesheets: [], total_count: 0 }
	},
})

const timesheetsSummary = createResource({
	url: "tactix.api.timesheet.get_timesheet_summary",
	initialData: {
		total_hours: 0,
		submitted_count: 0,
		draft_count: 0,
		active_days: 0,
	},
})

const taskOptionsResource = createResource({
	url: "tactix.api.timesheet.get_tasks_options",
	initialData: [],
	auto: true,
})

const employeeInfoResource = createResource({
	url: "tactix.api.timesheet.get_employee_info",
	initialData: {},
	auto: true,
})

const employeeOptionsResource = createResource({
	url: "tactix.api.timesheet.get_employees",
	initialData: [],
})

watch(
	() => employeeInfoResource.data,
	(val) => {
		if (val && val.is_system_manager) {
			employeeOptionsResource.fetch()
		}
	},
	{ immediate: true },
)

// Methods
function fetchTimesheets() {
	timesheets.fetch({
		filters: timesheetFilters.value,
		start: (currentPage.value - 1) * pageLength,
		page_length: pageLength,
	})
}

function fetchSummary() {
	timesheetsSummary.fetch({
		filters: timesheetFilters.value,
	})
}

function reloadTimesheets() {
	fetchTimesheets()
	fetchSummary()
}

// Initial fetch
fetchTimesheets()
fetchSummary()

// Watch filters
watch(
	timesheetFilters,
	() => {
		currentPage.value = 1
		fetchTimesheets()
		fetchSummary()
	},
	{ deep: true },
)

watch(currentPage, () => {
	fetchTimesheets()
})

const totalCount = computed(() => timesheets.data?.total_count || 0)
const totalPages = computed(() =>
	Math.max(1, Math.ceil(totalCount.value / pageLength)),
)

// Form logic
function addRow() {
	timesheetForm.time_logs.push({
		task: "",
		activity_type: "Execution",
		hours: 1.0,
		description: "",
		is_billable: 0,
	})
}

function removeRow(idx) {
	timesheetForm.time_logs.splice(idx, 1)
}

const computedTotalHours = computed(() => {
	return timesheetForm.time_logs.reduce(
		(sum, row) => sum + (Number.parseFloat(row.hours) || 0),
		0,
	)
})

const isEditMode = ref(false)
const editTimesheetName = ref("")

function openCreateDialog() {
	isEditMode.value = false
	editTimesheetName.value = ""
	formError.value = ""
	viewError.value = ""
	timesheetForm.date = new Date().toISOString().split("T")[0]
	timesheetForm.employee = employeeInfoResource.data?.name || ""
	timesheetForm.time_logs = []
	addRow()
	showCreateDialog.value = true
}

function openEditDialog(timesheetDoc) {
	isEditMode.value = true
	editTimesheetName.value = timesheetDoc.name
	formError.value = ""
	viewError.value = ""
	timesheetForm.date = timesheetDoc.start_date
	timesheetForm.employee = timesheetDoc.employee
	timesheetForm.time_logs = timesheetDoc.time_logs.map((log) => ({
		task: log.task || "",
		activity_type: log.activity_type || "Execution",
		hours: log.hours || 1.0,
		description: log.description || "",
		is_billable: log.is_billable || 0,
	}))
	showCreateDialog.value = true
}

// Create / Edit timesheet action
async function saveTimesheet(submitOption = false) {
	formError.value = ""

	if (!timesheetForm.date) {
		formError.value = "Timesheet Date is required."
		return
	}

	if (!timesheetForm.employee) {
		formError.value = "Employee selection is required."
		return
	}

	if (timesheetForm.time_logs.length === 0) {
		formError.value = "At least one log entry is required."
		return
	}

	for (const log of timesheetForm.time_logs) {
		if (!log.activity_type) {
			formError.value = "Activity Type is required for all rows."
			return
		}
		if ((Number.parseFloat(log.hours) || 0) <= 0) {
			formError.value = "Hours must be greater than zero."
			return
		}
	}

	saving.value = true
	try {
		const payload = {
			date: timesheetForm.date,
			employee: timesheetForm.employee,
			time_logs: timesheetForm.time_logs,
			submit: submitOption,
		}

		const url = isEditMode.value
			? "tactix.api.timesheet.edit_timesheet"
			: "tactix.api.timesheet.create_timesheet"

		const params = isEditMode.value
			? { name: editTimesheetName.value, doc: payload }
			: { doc: payload }

		await createResource({
			url,
			params,
		}).submit()

		showCreateDialog.value = false
		reloadTimesheets()
	} catch (err) {
		formError.value = parseError(err)
	} finally {
		saving.value = false
	}
}

// View Timesheet
async function openTimesheetDetails(row) {
	viewError.value = ""
	try {
		const res = await createResource({
			url: "tactix.api.timesheet.get_timesheet_detail",
			params: {
				name: row.name,
			},
		}).submit()

		selectedTimesheet.value = res
		showViewDialog.value = true
	} catch (err) {
		console.error("Failed to load timesheet details", err)
	}
}

async function submitTimesheet(name) {
	viewError.value = ""
	saving.value = true
	try {
		await createResource({
			url: "frappe.client.submit",
			params: {
				doctype: "Timesheet",
				docname: name,
			},
		}).submit()
		showViewDialog.value = false
		reloadTimesheets()
	} catch (err) {
		viewError.value = parseError(err)
	} finally {
		saving.value = false
	}
}

// Dialog definitions
const dialogOptions = computed(() => {
	const actions = []
	const hasSubmitPermission = employeeInfoResource.data?.has_submit_permission

	if (hasSubmitPermission) {
		actions.push({
			label: isEditMode.value ? "Submit Changes" : "Submit Timesheet",
			variant: "solid",
			loading: saving.value,
			onClick: () => saveTimesheet(true),
		})
	}

	actions.push({
		label: isEditMode.value ? "Save Draft" : "Save as Draft",
		variant: hasSubmitPermission ? "outline" : "solid",
		loading: saving.value,
		onClick: () => saveTimesheet(false),
	})

	actions.push({
		label: "Cancel",
		variant: "ghost",
		onClick: () => (showCreateDialog.value = false),
	})

	return {
		title: isEditMode.value ? "Edit Timesheet" : "Create Timesheet",
		size: "5xl",
		actions,
	}
})

const viewDialogOptions = computed(() => {
	const actions = []
	if (selectedTimesheet.value && selectedTimesheet.value.docstatus === 0) {
		actions.push({
			label: "Edit",
			variant: "outline",
			onClick: () => {
				showViewDialog.value = false
				openEditDialog(selectedTimesheet.value)
			},
		})
		if (selectedTimesheet.value.has_submit_permission) {
			actions.push({
				label: "Submit",
				variant: "solid",
				theme: "green",
				loading: saving.value,
				onClick: () => submitTimesheet(selectedTimesheet.value.name),
			})
		}
	}
	actions.push({
		label: "Close",
		variant: "ghost",
		onClick: () => (showViewDialog.value = false),
	})
	return {
		title: `Timesheet Details`,
		size: "4xl",
		actions,
	}
})

const formatDate = (dateStr) => {
	if (!dateStr) return "—"
	return dayjs(dateStr).format("MMM D, YYYY")
}
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