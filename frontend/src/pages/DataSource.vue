<template>
  <div class="flex h-full min-h-0 flex-col overflow-hidden">
    <!-- Header -->
    <div class="flex flex-shrink-0 items-center justify-between gap-3 px-1 pb-3 pt-1">
      <div class="flex min-w-0 items-center gap-3">
        <span class="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)]">
          <IconDatabase class="h-5 w-5" />
        </span>
        <div class="min-w-0">
          <h1 class="text-base font-semibold leading-tight text-ink-gray-9">Master Data</h1>
          <p class="truncate text-xs text-ink-gray-5">Projects, departments, customers and teams used across Tactix</p>
        </div>
      </div>
      <Button variant="ghost" class="shrink-0" @click="$router.back()">
        <template #prefix><IconArrowLeft class="h-4 w-4" /></template>
        Back
      </Button>
    </div>

    <!-- Tabs -->
    <div class="flex flex-shrink-0 gap-1 overflow-x-auto border-b border-outline-gray-2 px-1" role="tablist">
      <button
        v-for="(t, i) in tabs"
        :key="t.id"
        type="button"
        role="tab"
        class="tab"
        :class="tabIndex === i && 'is-active'"
        :aria-selected="tabIndex === i"
        @click="tabIndex = i"
      >
        <component :is="t.icon" class="h-3.5 w-3.5" />
        {{ t.label }}
        <span v-if="tabIndex === i && !loadingRecords" class="count">{{ masterRecords.length }}</span>
      </button>
    </div>

    <!-- Toolbar -->
    <div class="toolbar-card mx-1 my-2 flex flex-shrink-0 flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
      <div class="relative w-full sm:w-80">
        <IconSearch class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-ink-gray-4" />
        <input
          ref="searchInputEl"
          v-model="searchQuery"
          type="text"
          :placeholder="`Search ${tabs[tabIndex].label.toLowerCase()}…`"
          class="h-8 w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 pl-9 pr-9 text-[13px] text-ink-gray-8 outline-none transition focus:border-[color:var(--brand,#29ADFF)] focus:bg-surface-white focus:ring-2 focus:ring-[color:var(--brand-soft,#E9F6FF)]"
        />
        <kbd v-if="!searchQuery" class="kbd absolute right-2 top-1/2 -translate-y-1/2">/</kbd>
        <button
          v-else
          type="button"
          class="absolute right-1.5 top-1/2 -translate-y-1/2 rounded p-1 text-ink-gray-4 hover:bg-surface-gray-2 hover:text-ink-gray-7"
          title="Clear search"
          @click="searchQuery = ''"
        >
          <IconX class="h-3.5 w-3.5" />
        </button>
      </div>

      <div class="flex items-center justify-end gap-2">
        <template v-if="isAdmin && selectedRecords.size > 0">
          <div class="flex h-8 items-center gap-1 rounded-md bg-surface-gray-2 pl-2.5 pr-1 text-xs text-ink-gray-7">
            <span class="font-medium tabular-nums">{{ selectedRecords.size }} selected</span>
            <button type="button" class="rounded p-1 text-ink-gray-5 hover:bg-surface-gray-3 hover:text-ink-gray-8" title="Clear selection" @click="selectedRecords = new Set()">
              <IconX class="h-3.5 w-3.5" />
            </button>
          </div>
          <Button variant="outline" theme="red" class="!h-8 text-xs" @click="confirmBulkDelete">
            <template #prefix><IconTrash class="h-3.5 w-3.5" /></template>
            Delete
          </Button>
        </template>

        <Button variant="outline" class="!h-8 !px-2.5" title="Refresh" @click="fetchMasterRecords">
          <template #prefix><IconRefresh class="h-3.5 w-3.5" :class="loadingRecords && 'animate-spin'" /></template>
        </Button>

        <Button v-if="isAdmin" variant="solid" class="brand-btn !h-8 !px-3 text-xs" @click="openCreateModal">
          <template #prefix><IconPlus class="h-3.5 w-3.5" /></template>
          New {{ currentTabLabelSingular }}
        </Button>
      </div>
    </div>

    <!-- Error -->
    <p v-if="loadError" class="mx-1 mb-2 flex items-center justify-between gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
      <span>{{ loadError }}</span>
      <button type="button" class="font-semibold underline" @click="fetchMasterRecords">Try again</button>
    </p>

    <!-- Table -->
    <div class="mx-1 mb-2 flex min-h-0 flex-1 flex-col">
      <div class="panel relative flex min-h-[420px] flex-1 flex-col overflow-hidden md:min-h-0">
        <div v-if="loadingRecords && masterRecords.length" class="busy-bar" aria-hidden="true"></div>

        <div v-if="loadingRecords && !masterRecords.length" class="divide-y divide-outline-gray-1">
          <div v-for="n in 6" :key="n" class="flex items-center gap-4 px-4 py-3">
            <div class="skeleton h-3.5 w-40"></div>
            <div class="skeleton h-3.5 flex-1"></div>
            <div class="skeleton h-3.5 w-24"></div>
          </div>
        </div>

        <div v-else-if="filteredRecords.length === 0" class="flex flex-1 flex-col items-center justify-center px-4 py-16 text-center">
          <span class="grid h-11 w-11 place-items-center rounded-full bg-surface-gray-2 text-ink-gray-5">
            <component :is="tabs[tabIndex].icon" class="h-5 w-5" />
          </span>
          <h3 class="mt-3 text-sm font-semibold text-ink-gray-8">
            {{ searchQuery ? 'No matches' : `No ${tabs[tabIndex].label.toLowerCase()} yet` }}
          </h3>
          <p class="mt-1 max-w-xs text-xs text-ink-gray-5">
            {{ searchQuery ? 'Try a different search term.' : isAdmin ? `Create the first ${currentTabLabelSingular.toLowerCase()} to get started.` : 'Nothing has been added here yet.' }}
          </p>
          <Button v-if="!searchQuery && isAdmin" variant="solid" class="brand-btn mt-3" @click="openCreateModal">
            <template #prefix><IconPlus class="h-3.5 w-3.5" /></template>
            New {{ currentTabLabelSingular }}
          </Button>
        </div>

        <ListView
          v-else
          class="flex h-full min-h-0 flex-col"
          :columns="columns"
          :rows="paginatedRecords || []"
          :options="{ selectable: isAdmin, showTooltip: true, resizeColumn: true, onRowClick: (row) => isAdmin && openEditModal(row) }"
          row-key="name"
          v-model:selections="selectedRecords"
        >
          <ListHeader class="shrink-0 border-b border-outline-gray-2 bg-surface-gray-1">
            <ListHeaderItem v-for="col in columns" :key="col.key" :item="col" />
          </ListHeader>
          <div class="custom-scrollbar relative min-h-0 max-h-[480px] flex-grow overflow-y-auto md:max-h-none md:flex-1">
            <ListRows>
              <ListRow v-for="row in (paginatedRecords || [])" :key="row.name" v-slot="{ column, item }" :row="row" :class="isAdmin && 'cursor-pointer'">
                <ListRowItem :item="item">
                  <template v-if="column.key === 'name'">
                    <span class="truncate font-mono text-[12px] font-medium text-ink-gray-8" :title="row.name">{{ row.name }}</span>
                  </template>
                  <template v-if="column.key === 'project_name'">
                    <span class="truncate text-sm text-ink-gray-8">{{ row.project_name || '—' }}</span>
                  </template>
                  <template v-if="column.key === 'company'">
                    <span class="truncate text-xs text-ink-gray-6">{{ row.company || '—' }}</span>
                  </template>
                  <template v-if="column.key === 'department_name'">
                    <span class="truncate text-sm text-ink-gray-8">{{ row.department_name || '—' }}</span>
                  </template>
                  <template v-if="column.key === 'department_head'">
                    <span class="truncate text-xs text-ink-gray-6">{{ row.department_head || '—' }}</span>
                  </template>
                  <template v-if="column.key === 'team_name'">
                    <span class="truncate text-sm font-medium text-ink-gray-8">{{ row.team_name || '—' }}</span>
                  </template>
                  <template v-if="column.key === 'team_lead'">
                    <span v-if="row.team_lead" class="flex min-w-0 items-center gap-2">
                      <Avatar :label="getUserLabel(row.team_lead)" size="sm" class="shrink-0" />
                      <span class="truncate text-xs text-ink-gray-7">{{ getUserLabel(row.team_lead) }}</span>
                    </span>
                    <span v-else class="text-xs text-ink-gray-4">No lead</span>
                  </template>
                  <template v-if="column.key === 'members'">
                    <div class="flex min-w-0 items-center gap-2">
                      <div class="flex -space-x-1.5">
                        <Avatar
                          v-for="m in (row.members || []).slice(0, 4)"
                          :key="m"
                          :label="getUserLabel(m)"
                          size="sm"
                          class="avatar-ring"
                          v-tooltip="getUserLabel(m)"
                        />
                      </div>
                      <span v-if="(row.members || []).length" class="text-xs text-ink-gray-5">
                        {{ row.members.length }} member{{ row.members.length === 1 ? '' : 's' }}
                      </span>
                      <span v-else class="text-xs text-ink-gray-4">No members</span>
                    </div>
                  </template>
                  <template v-if="column.key === 'actions'">
                    <div v-if="isAdmin" class="flex items-center justify-end gap-0.5">
                      <button type="button" class="icon-btn" title="Edit" @click.stop="openEditModal(row)">
                        <IconEdit class="h-3.5 w-3.5" />
                      </button>
                      <button type="button" class="icon-btn danger" title="Delete" @click.stop="confirmSingleDelete(row.name)">
                        <IconTrash class="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </template>
                </ListRowItem>
              </ListRow>
            </ListRows>
          </div>
        </ListView>

        <!-- Pagination -->
        <div v-if="totalCount > 0" class="flex shrink-0 items-center justify-between border-t border-outline-gray-1 px-4 py-2">
          <div class="flex items-center gap-1">
            <button type="button" class="pg-btn" :disabled="currentPage === 1" title="First page" @click="currentPage = 1"><IconChevronsLeft class="h-3.5 w-3.5" /></button>
            <button type="button" class="pg-btn" :disabled="currentPage === 1" title="Previous page" @click="currentPage = Math.max(1, currentPage - 1)"><IconChevronLeft class="h-3.5 w-3.5" /></button>
            <span class="px-2 text-[11px] font-semibold tabular-nums text-ink-gray-7">{{ currentPage }} / {{ totalPages }}</span>
            <button type="button" class="pg-btn" :disabled="currentPage >= totalPages" title="Next page" @click="currentPage = Math.min(totalPages, currentPage + 1)"><IconChevronRight class="h-3.5 w-3.5" /></button>
            <button type="button" class="pg-btn" :disabled="currentPage >= totalPages" title="Last page" @click="currentPage = totalPages"><IconChevronsRight class="h-3.5 w-3.5" /></button>
          </div>
          <div class="text-xs text-ink-gray-5">
            <b class="font-semibold tabular-nums text-ink-gray-8">{{ (currentPage - 1) * pageLength + 1 }}–{{ Math.min(currentPage * pageLength, totalCount) }}</b>
            of <b class="font-semibold tabular-nums text-ink-gray-8">{{ totalCount }}</b>
          </div>
        </div>
      </div>
    </div>

    <!-- Create / Edit -->
    <Dialog v-model="modal.show" :disable-outside-click-to-close="true" :options="{ title: dialogTitle, size: 'md' }">
      <template #body-content>
        <form class="space-y-4 py-1" @submit.prevent="submitModalForm">
          <p v-if="modal.error" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">{{ modal.error }}</p>

          <template v-if="activeTab === 'project'">
            <FormControl type="text" label="Project name *" v-model="modal.form.project_name" placeholder="e.g. Website revamp" />
            <div class="space-y-1.5">
              <label class="block text-xs text-ink-gray-5">Company *</label>
              <Autocomplete
                ref="projectCompanyAutocomplete"
                :options="linkOptions.companies || []"
                :modelValue="modal.form.company"
                @update:modelValue="val => modal.form.company = val?.value ?? val ?? ''"
                :compare-fn="compareOption"
                :max-options="100"
              >
                <template #target>
                  <button type="button" class="field-btn" @click="() => projectCompanyAutocomplete?.togglePopover()">
                    <span class="truncate">{{ getCompanyLabel(modal.form.company) }}</span>
                    <FeatherIcon name="chevron-down" class="h-4 w-4 shrink-0 text-ink-gray-5" />
                  </button>
                </template>
              </Autocomplete>
            </div>
          </template>

          <template v-if="activeTab === 'department'">
            <FormControl type="text" label="Department name *" v-model="modal.form.department_name" placeholder="e.g. Engineering" />
            <div class="space-y-1.5">
              <label class="block text-xs text-ink-gray-5">Company *</label>
              <Autocomplete
                ref="departmentCompanyAutocomplete"
                :options="linkOptions.companies || []"
                :modelValue="modal.form.company"
                @update:modelValue="val => modal.form.company = val?.value ?? val ?? ''"
                :compare-fn="compareOption"
                :max-options="100"
              >
                <template #target>
                  <button type="button" class="field-btn" @click="() => departmentCompanyAutocomplete?.togglePopover()">
                    <span class="truncate">{{ getCompanyLabel(modal.form.company) }}</span>
                    <FeatherIcon name="chevron-down" class="h-4 w-4 shrink-0 text-ink-gray-5" />
                  </button>
                </template>
              </Autocomplete>
            </div>
          </template>

          <template v-if="activeTab === 'tactix_cust'">
            <FormControl type="text" label="Customer name / ID *" v-model="modal.form.name" :disabled="modal.isEdit" placeholder="e.g. Acme Trading" />
            <p v-if="modal.isEdit" class="-mt-2 text-[11px] text-ink-gray-5">The customer ID can't be changed after it is created.</p>
          </template>

          <template v-if="activeTab === 'tactix_team'">
            <FormControl type="text" label="Team name *" v-model="modal.form.team_name" placeholder="e.g. Platform team" />
            <div class="space-y-1.5">
              <label class="block text-xs text-ink-gray-5">Team lead</label>
              <Autocomplete
                ref="teamLeadAutocomplete"
                :options="userOptions || []"
                :modelValue="modal.form.team_lead"
                @update:modelValue="val => modal.form.team_lead = val?.value ?? val ?? ''"
                :compare-fn="compareOption"
                :max-options="100"
              >
                <template #target>
                  <button type="button" class="field-btn" @click="() => teamLeadAutocomplete?.togglePopover()">
                    <span class="truncate">{{ modal.form.team_lead ? getUserLabel(modal.form.team_lead) : 'Select team lead' }}</span>
                    <FeatherIcon name="chevron-down" class="h-4 w-4 shrink-0 text-ink-gray-5" />
                  </button>
                </template>
              </Autocomplete>
            </div>
            <div class="space-y-1.5">
              <label class="block text-xs text-ink-gray-5">Team members <span class="text-ink-gray-4">(employees only)</span></label>
              <MultiSelect :options="userOptions" v-model="modal.form.members" placeholder="Select team members" />
            </div>
          </template>
          <button type="submit" class="hidden" aria-hidden="true"></button>
        </form>
      </template>
      <template #actions>
        <div class="dialog-actions">
          <Button variant="solid" class="brand-btn" :loading="modal.saving" @click="submitModalForm">
            {{ modal.isEdit ? 'Save changes' : `Create ${currentTabLabelSingular.toLowerCase()}` }}
          </Button>
          <Button variant="ghost" @click="modal.show = false">Cancel</Button>
        </div>
      </template>
    </Dialog>

    <!-- Delete -->
    <Dialog
      v-model="deleteConfirm.show"
      :disable-outside-click-to-close="true"
      :options="{ title: deleteConfirm.isBulk ? `Delete ${deleteConfirm.count} ${currentTabLabelSingular.toLowerCase()}${deleteConfirm.count === 1 ? '' : 's'}` : `Delete ${currentTabLabelSingular.toLowerCase()}`, size: 'sm' }"
    >
      <template #body-content>
        <p class="py-2 text-sm leading-relaxed text-ink-gray-6">
          <template v-if="deleteConfirm.isBulk">
            This will permanently remove <b class="text-ink-gray-9">{{ deleteConfirm.count }}</b> selected {{ currentTabLabelSingular.toLowerCase() }}{{ deleteConfirm.count === 1 ? '' : 's' }}. This can't be undone.
          </template>
          <template v-else>
            This will permanently remove <b class="break-all text-ink-gray-9">{{ deleteConfirm.targetName }}</b>. This can't be undone.
          </template>
        </p>
        <p v-if="deleteConfirm.error" class="whitespace-pre-line rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">{{ deleteConfirm.error }}</p>
      </template>
      <template #actions>
        <div class="dialog-actions">
          <Button variant="solid" theme="red" :loading="deleteConfirm.loading" @click="executeDelete">Delete</Button>
          <Button variant="ghost" @click="deleteConfirm.show = false">Cancel</Button>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import {
	Autocomplete,
	Avatar,
	Badge,
	Button,
	Card,
	Dialog,
	Dropdown,
	FeatherIcon,
	FormControl,
	ListHeader,
	ListHeaderItem,
	ListRow,
	ListRowItem,
	ListRows,
	ListView,
	MultiSelect,
	Popover,
	Select,
	Tabs,
	createResource,
} from "frappe-ui"
import { computed, onMounted, onUnmounted, reactive, ref, watch } from "vue"

const projectCompanyAutocomplete = ref(null)
const departmentCompanyAutocomplete = ref(null)
const departmentHeadAutocomplete = ref(null)
const teamLeadAutocomplete = ref(null)

function compareOption(a, b) {
	const aVal = a && typeof a === "object" ? a.value : a
	const bVal = b && typeof b === "object" ? b.value : b
	return aVal === bVal
}

function getCompanyLabel(val) {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return "Select Company"
	const match = linkOptions.companies?.find((c) =>
		typeof c === "object" ? c.value === rawVal : c === rawVal,
	)
	return match ? (typeof match === "object" ? match.label : match) : rawVal
}

// Icons
import IconArrowLeft from "~icons/lucide/arrow-left"
import IconCheck from "~icons/lucide/check"
import IconChevronDown from "~icons/lucide/chevron-down"
import IconChevronLeft from "~icons/lucide/chevron-left"
import IconChevronRight from "~icons/lucide/chevron-right"
import IconChevronsLeft from "~icons/lucide/chevrons-left"
import IconChevronsRight from "~icons/lucide/chevrons-right"
import IconEdit from "~icons/lucide/pencil"
import IconPlus from "~icons/lucide/plus"
import IconSearch from "~icons/lucide/search"
import IconTrash from "~icons/lucide/trash-2"
import IconBriefcase from "~icons/lucide/briefcase"
import IconBuilding from "~icons/lucide/building-2"
import IconDatabase from "~icons/lucide/database"
import IconFolder from "~icons/lucide/folder-kanban"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconUsers from "~icons/lucide/users"
import IconX from "~icons/lucide/x"

const tabIndex = ref(0)
const tabs = [
	{ label: "Projects", id: "project", icon: IconFolder },
	{ label: "Departments", id: "department", icon: IconBuilding },
	{ label: "Customers", id: "tactix_cust", icon: IconBriefcase },
	{ label: "Teams", id: "tactix_team", icon: IconUsers },
]

const searchInputEl = ref(null)
const loadError = ref("")

// POST helper: Frappe rejects POSTs from a logged-in session without the CSRF token
function getCsrfToken() {
	if (window.csrf_token && window.csrf_token !== "{{ csrf_token }}") return window.csrf_token
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	return cookies.get("csrf_token") || ""
}

// Turns a Frappe error response into readable text
function errorText(data, fallback) {
	if (!data) return fallback
	if (data.message?.error) return String(data.message.error)
	if (data._server_messages) {
		try {
			return JSON.parse(data._server_messages)
				.map((m) => {
					try {
						return JSON.parse(m).message || m
					} catch {
						return m
					}
				})
				.join(" ")
				.replace(/<[^>]*>/g, "")
		} catch {}
	}
	if (data.exception) return String(data.exception).split(":").slice(1).join(":").trim() || data.exception
	return fallback
}

async function postMaster(body) {
	const res = await fetch("/api/method/tactix.api.masters.save_master_record", {
		method: "POST",
		headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": getCsrfToken() },
		body: JSON.stringify(body),
	})
	let data = null
	try {
		data = await res.json()
	} catch {}
	const ok = res.ok && data?.message?.status !== "error" && !data?.exception
	return { ok, data }
}

const activeTab = computed(() => tabs[tabIndex.value]?.id || "project")
const searchQuery = ref("")
const loadingRecords = ref(false)
const masterRecords = ref([])
const selectedRecords = ref(new Set())

const currentPage = ref(1)
const pageLength = ref(20)

watch([activeTab, searchQuery], () => {
	currentPage.value = 1
})

const deleteConfirm = reactive({
	show: false,
	isBulk: false,
	targetName: null,
	count: 0,
	loading: false,
	error: "",
})

const actionsOptions = computed(() => [
	{
		label: `Delete Selected (${selectedRecords.value.size})`,
		icon: "trash-2",
		onClick: confirmBulkDelete,
	},
])

const currentTabLabelSingular = computed(() => {
	switch (activeTab.value) {
		case "project":
			return "Project"
		case "department":
			return "Department"
		case "tactix_cust":
			return "Tactix Customer"
		case "tactix_team":
			return "Tactix Team"
		default:
			return ""
	}
})

const currentTabDoctype = computed(() => {
	switch (activeTab.value) {
		case "project":
			return "Project"
		case "department":
			return "Department"
		case "tactix_cust":
			return "Tactix Customer"
		case "tactix_team":
			return "Tactix Team"
		default:
			return ""
	}
})

const columns = computed(() => {
	switch (activeTab.value) {
		case "project":
			return [
				{ label: "Name / ID", key: "name", width: "200px" },
				{ label: "Project Name", key: "project_name" },
				{ label: "Company", key: "company", width: "200px" },
				...(isAdmin.value
					? [{ label: "Actions", key: "actions", width: "100px" }]
					: []),
			]
		case "department":
			return [
				{ label: "Name / ID", key: "name", width: "200px" },
				{ label: "Department Name", key: "department_name" },
				{ label: "Company", key: "company", width: "200px" },
				...(isAdmin.value
					? [{ label: "Actions", key: "actions", width: "100px" }]
					: []),
			]
		case "tactix_cust":
			return [
				{ label: "Name / ID", key: "name" },
				...(isAdmin.value
					? [{ label: "Actions", key: "actions", width: "100px" }]
					: []),
			]
		case "tactix_team":
			return [
				{ label: "Name / ID", key: "name", width: "160px" },
				{ label: "Team Name", key: "team_name", width: "180px" },
				{ label: "Team Lead", key: "team_lead", width: "200px" },
				{ label: "Team Members", key: "members" },
				...(isAdmin.value
					? [{ label: "Actions", key: "actions", width: "100px" }]
					: []),
			]
		default:
			return []
	}
})

const employeeInfoResource = createResource({
	url: "tactix.api.timesheet.get_employee_info",
	initialData: {},
	auto: true,
})

const isAdmin = computed(() => employeeInfoResource.data?.is_system_manager)

// Link Options for Dropdowns
const linkOptions = reactive({
	companies: [],
})

const usersResource = createResource({
	url: "tactix.api.generic.get_users_list",
	auto: true,
})

const userOptions = computed(() => {
	if (!usersResource.data) return []
	return usersResource.data.map((u) => ({
		label: u.full_name ? `${u.full_name} (${u.name})` : u.name,
		value: u.name,
	}))
})

function getUserLabel(userName) {
	const rawVal =
		userName && typeof userName === "object" ? userName.value : userName
	if (!rawVal) return "—"
	const match = usersResource.data?.find(
		(u) => u.name === rawVal || u.value === rawVal,
	)
	return match ? match.full_name || match.label || rawVal : rawVal
}

// Fetch Link Options
const fetchLinkOptions = async () => {
	try {
		const res = await fetch("/api/method/tactix.api.masters.get_link_options")
		const data = await res.json()
		if (data.message) {
			linkOptions.companies = (data.message.companies || []).map((c) => ({
				label: c,
				value: c,
			}))
		}
	} catch (err) {
		console.error("Error fetching link options:", err)
	}
}

// Fetch Master Records based on activeTab
let loadSeq = 0
const fetchMasterRecords = async () => {
	const seq = ++loadSeq
	loadingRecords.value = true
	loadError.value = ""
	try {
		const doctype = currentTabDoctype.value
		if (!doctype) {
			masterRecords.value = []
			return
		}
		const res = await fetch(
			`/api/method/tactix.api.masters.get_master_records?doctype=${encodeURIComponent(doctype)}`,
		)
		const data = await res.json()
		if (seq !== loadSeq) return // user already switched to another tab
		if (!res.ok) throw new Error(errorText(data, "Request failed"))
		masterRecords.value = data.message || []
	} catch (err) {
		if (seq !== loadSeq) return
		console.error("Error fetching master records:", err)
		loadError.value = `Couldn't load ${tabs[tabIndex.value].label.toLowerCase()}. ${err.message || ""}`
	} finally {
		if (seq === loadSeq) loadingRecords.value = false
	}
}

watch(activeTab, () => {
	selectedRecords.value = new Set()
	masterRecords.value = []
	fetchMasterRecords()
})

function handleSlashKey(e) {
	if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey) return
	const t = e.target
	if (t && (t.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(t.tagName))) return
	if (modal.show || deleteConfirm.show) return
	e.preventDefault()
	searchInputEl.value?.focus()
}
onMounted(() => window.addEventListener("keydown", handleSlashKey))
onUnmounted(() => window.removeEventListener("keydown", handleSlashKey))

watch(
	isAdmin,
	(val) => {
		if (val) {
			fetchLinkOptions()
		}
	},
	{ immediate: true },
)

fetchMasterRecords()

// Filtered Records based on Search Query
const filteredRecords = computed(() => {
	if (!searchQuery.value) return masterRecords.value
	const q = searchQuery.value.toLowerCase()
	return masterRecords.value.filter((r) => {
		return (
			(r.name && r.name.toLowerCase().includes(q)) ||
			(r.project_name && r.project_name.toLowerCase().includes(q)) ||
			(r.company && r.company.toLowerCase().includes(q)) ||
			(r.department_name && r.department_name.toLowerCase().includes(q)) ||
			(r.department_head && r.department_head.toLowerCase().includes(q)) ||
			(r.team_name && r.team_name.toLowerCase().includes(q)) ||
			(r.team_lead && r.team_lead.toLowerCase().includes(q))
		)
	})
})

const totalCount = computed(() => filteredRecords.value.length)
const totalPages = computed(
	() => Math.ceil(totalCount.value / pageLength.value) || 1,
)

const pageOptions = computed(() =>
	Array.from({ length: totalPages.value }, (_, i) => ({
		label: `${i + 1} / ${totalPages.value}`,
		value: i + 1,
	})),
)
const paginatedRecords = computed(() =>
	filteredRecords.value.slice(
		(currentPage.value - 1) * pageLength.value,
		currentPage.value * pageLength.value,
	),
)

const paginationPages = computed(() => {
	const current = currentPage.value
	const total = totalPages.value
	if (total <= 7) {
		return Array.from({ length: total }, (_, i) => i + 1)
	}

	const pages = [1]
	if (current > 3) {
		pages.push("...")
	}

	const start = Math.max(2, current - 1)
	const end = Math.min(total - 1, current + 1)

	for (let i = start; i <= end; i++) {
		pages.push(i)
	}

	if (current < total - 2) {
		pages.push("...")
	}
	pages.push(total)

	return pages
})

// Modal State
const modal = reactive({
	show: false,
	isEdit: false,
	saving: false,
	recordId: null,
	error: "",
	form: {},
})

const dialogTitle = computed(
	() => `${modal.isEdit ? "Edit" : "New"} ${currentTabLabelSingular.value.toLowerCase()}`,
)

const REQUIRED = {
	project: [["project_name", "Project name"], ["company", "Company"]],
	department: [["department_name", "Department name"], ["company", "Company"]],
	tactix_cust: [["name", "Customer name"]],
	tactix_team: [["team_name", "Team name"]],
}

const dialogOptions = computed(() => ({
	title: `${modal.isEdit ? "Edit" : "Create"} ${currentTabLabelSingular.value}`,
	size: "md",
	actions: [
		{
			label: modal.isEdit ? "Update" : "Save",
			variant: "solid",
			loading: modal.saving,
			onClick: submitModalForm,
		},
	],
}))

function openCreateModal() {
	modal.error = ""
	modal.isEdit = false
	modal.recordId = null
	modal.form = { members: [] }
	if (activeTab.value === "project") {
		if (linkOptions.companies.length > 0) {
			modal.form.company = linkOptions.companies[0].value
		}
	} else if (activeTab.value === "department") {
		if (linkOptions.companies.length > 0) {
			modal.form.company = linkOptions.companies[0].value
		}
	}
	modal.show = true
}

function openEditModal(row) {
	modal.error = ""
	modal.isEdit = true
	modal.recordId = row.name
	modal.form = { ...row, members: row.members ? [...row.members] : [] }
	modal.show = true
}

async function submitModalForm() {
	if (modal.saving) return
	modal.error = ""
	const missing = (REQUIRED[activeTab.value] || [])
		.filter(([key]) => !String(modal.form[key] ?? "").trim())
		.map(([, label]) => label)
	if (missing.length) {
		modal.error = `Please fill in: ${missing.join(", ")}.`
		return
	}
	modal.saving = true
	try {
		const action = modal.isEdit ? "update" : "create"
		const payload = {
			action,
			doctype: currentTabDoctype.value,
			data: { ...modal.form },
		}
		if (modal.isEdit) {
			payload.name = modal.recordId
		}

		const { ok, data } = await postMaster(payload)
		if (ok && data?.message?.status === "success") {
			modal.show = false
			fetchMasterRecords()
		} else {
			modal.error = errorText(data, "Couldn't save the record.")
		}
	} catch (err) {
		console.error("Error submitting form:", err)
		modal.error = "Couldn't reach the server. Please try again."
	} finally {
		modal.saving = false
	}
}

function confirmSingleDelete(name) {
	deleteConfirm.error = ""
	deleteConfirm.isBulk = false
	deleteConfirm.targetName = name
	deleteConfirm.count = 1
	deleteConfirm.show = true
}

function confirmBulkDelete() {
	deleteConfirm.error = ""
	deleteConfirm.isBulk = true
	deleteConfirm.targetName = null
	deleteConfirm.count = selectedRecords.value.size
	deleteConfirm.show = true
}

async function executeDelete() {
	if (deleteConfirm.loading) return
	deleteConfirm.loading = true
	deleteConfirm.error = ""
	const names = deleteConfirm.isBulk
		? Array.from(selectedRecords.value)
		: deleteConfirm.targetName
			? [deleteConfirm.targetName]
			: []
	const failed = []
	for (const name of names) {
		try {
			const { ok, data } = await postMaster({ action: "delete", doctype: currentTabDoctype.value, name })
			if (ok) selectedRecords.value.delete(name)
			else failed.push(`${name}: ${errorText(data, "could not be deleted")}`)
		} catch (err) {
			failed.push(`${name}: network error`)
		}
	}
	selectedRecords.value = new Set(selectedRecords.value)
	deleteConfirm.loading = false
	fetchMasterRecords()
	if (failed.length) {
		deleteConfirm.error = `Couldn't delete ${failed.length} of ${names.length}:` + String.fromCharCode(10) + failed.join(String.fromCharCode(10))
	} else {
		deleteConfirm.show = false
	}
}
</script>

<style scoped>
.toolbar-card,
.panel,
.kpi {
  border: 1px solid var(--outline-gray-1, #ededed);
  background: var(--surface-cards, #fff);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}
.toolbar-card {
  padding: 10px 12px;
  border-radius: 10px;
}
.panel {
  border-radius: 12px;
}

/* stat cards */
.kpi {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
  min-height: 72px;
  padding: 10px 12px;
  border-radius: 10px;
  text-align: left;
  transition: border-color 0.15s, background-color 0.15s, box-shadow 0.15s;
}
.kpi-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  min-height: 28px;
  margin-top: 8px;
}
.kpi.is-clickable {
  cursor: pointer;
  user-select: none;
}
.kpi.is-clickable:hover {
  border-color: var(--brand-border, #a6dcff);
}
.kpi.is-clickable:focus-visible {
  outline: 2px solid var(--brand, #29adff);
  outline-offset: 2px;
}
.kpi.is-active {
  border-color: var(--brand, #29adff);
  background: var(--brand-soft, #e9f6ff);
  box-shadow: 0 0 0 1px var(--brand, #29adff) inset;
}

/* tabs */
.tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: -1px;
  padding: 8px 12px;
  border-bottom: 2px solid transparent;
  color: var(--ink-gray-5, #7c7c7c);
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  transition: color 0.15s, border-color 0.15s;
}
.tab:hover {
  color: var(--ink-gray-8, #383838);
}
.tab.is-active {
  border-bottom-color: var(--brand, #29adff);
  color: var(--brand-text, #0a84d0);
}
.tab .count {
  min-width: 20px;
  padding: 0 6px;
  border-radius: 999px;
  background: var(--brand-soft, #e9f6ff);
  color: var(--brand-text, #0a84d0);
  font-size: 11px;
  font-weight: 700;
  line-height: 18px;
  text-align: center;
}

/* search hint, chips */
.kbd {
  display: inline-flex;
  align-items: center;
  height: 18px;
  padding: 0 5px;
  border: 1px solid var(--outline-gray-2, #e2e2e2);
  border-radius: 4px;
  background: var(--surface-gray-1, #f8f8f8);
  color: var(--ink-gray-5, #7c7c7c);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 10.5px;
  line-height: 1;
  pointer-events: none;
}
.chip {
  height: 26px;
  padding: 0 9px;
  border: 1px dashed var(--outline-gray-3, #d4d4d4);
  border-radius: 999px;
  color: var(--ink-gray-6, #6b6b6b);
  font-size: 12px;
  white-space: nowrap;
  transition: background-color 0.15s, border-color 0.15s, color 0.15s;
}
.chip:hover {
  background: var(--surface-gray-2, #f3f3f3);
}
.chip.on {
  border-style: solid;
  border-color: var(--brand-border, #a6dcff);
  background: var(--brand-soft, #e9f6ff);
  color: var(--brand-text, #0a84d0);
  font-weight: 500;
}

/* table bits */
.icon-btn {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  color: var(--ink-gray-5, #7c7c7c);
  transition: background-color 0.15s, color 0.15s;
}
.icon-btn:hover:not(:disabled) {
  background: var(--surface-gray-2, #f3f3f3);
  color: var(--ink-gray-9, #171717);
}
.icon-btn.danger:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}
.icon-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
.pg-btn {
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  border-radius: 5px;
  color: var(--ink-gray-5, #7c7c7c);
}
.pg-btn:hover:not(:disabled) {
  background: var(--surface-gray-2, #f3f3f3);
  color: var(--ink-gray-8, #383838);
}
.pg-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  line-height: 18px;
  white-space: nowrap;
}
.status-pill.is-active { background: rgba(34, 197, 94, 0.12); color: #15803d; }
.status-pill.is-disabled { background: var(--surface-gray-2, #f3f3f3); color: var(--ink-gray-5, #7c7c7c); }
.role-tag {
  padding: 1px 7px;
  border-radius: 5px;
  background: var(--brand-soft, #e9f6ff);
  color: var(--brand-text, #0a84d0);
  font-size: 11px;
  font-weight: 500;
  line-height: 18px;
  white-space: nowrap;
}
.avatar-ring {
  box-shadow: 0 0 0 2px var(--surface-white, #fff);
}

/* dialogs */
.section-title {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--ink-gray-5, #7c7c7c);
}
.field-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  width: 100%;
  height: 28px;
  padding: 4px 8px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: var(--surface-gray-2, #f3f3f3);
  color: var(--ink-gray-8, #383838);
  font-size: 13px;
  text-align: left;
  transition: background-color 0.15s, border-color 0.15s;
}
.field-btn:hover {
  background: var(--surface-gray-3, #ededed);
}
.field-btn:focus-visible {
  outline: none;
  border-color: var(--brand, #29adff);
  box-shadow: 0 0 0 2px var(--brand-soft, #e9f6ff);
}
.role-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 9px 11px;
  border: 1px solid var(--outline-gray-2, #e2e2e2);
  border-radius: 9px;
  color: var(--ink-gray-8, #383838);
  transition: border-color 0.15s, background-color 0.15s;
}
.role-card:hover {
  background: var(--surface-gray-1, #f8f8f8);
}
.role-card.on {
  border-color: var(--brand, #29adff);
  background: var(--brand-soft, #e9f6ff);
  color: var(--brand-text, #0a84d0);
}
.role-card .tick {
  display: grid;
  flex-shrink: 0;
  place-items: center;
  width: 18px;
  height: 18px;
  border: 1.5px solid var(--outline-gray-3, #c7c7c7);
  border-radius: 999px;
  color: #fff;
}
.role-card.on .tick {
  border-color: var(--brand, #29adff);
  background: var(--brand, #29adff);
}
/* dialog footer: buttons on the right, main action right-most */
.dialog-actions {
  display: flex;
  flex-direction: row-reverse;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  width: 100%;
}

/* loading */
.busy-bar {
  position: absolute;
  inset: 0 0 auto 0;
  z-index: 20;
  height: 2px;
  overflow: hidden;
}
.busy-bar::after {
  content: "";
  position: absolute;
  inset: 0;
  width: 35%;
  background: var(--brand, #29adff);
  animation: busy 1s ease-in-out infinite;
}
@keyframes busy {
  from { transform: translateX(-100%); }
  to { transform: translateX(300%); }
}
.skeleton {
  border-radius: 5px;
  background: var(--surface-gray-2, #f3f3f3);
  animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse {
  50% { opacity: 0.5; }
}
input[type="checkbox"] {
  accent-color: var(--brand, #29adff);
}
</style>