<template>
  <div class="h-full overflow-y-auto p-2 space-y-6 custom-scrollbar bg-slate-50/50">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-4 gap-4">
      <div class="min-w-0">
        <h1 class="text-xl font-black text-slate-900 leading-tight">Master Data</h1>
        <p class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mt-1">Manage system record masters, projects, departments, customers, and teams</p>
      </div>
      <Button 
        variant="ghost" 
        class="!text-slate-600 hover:!bg-slate-100/50 self-start sm:self-auto shrink-0"
        @click="$router.back()"
      >
        <template #prefix><IconArrowLeft class="w-4 h-4" /></template>
        Back
      </Button>
    </div>

    <!-- Navigation Tabs (Frappe UI Tabs component) -->
    <Tabs :tabs="tabs" v-model="tabIndex">
      <template #tab-panel="{ tab }">
        <div class="pt-2 space-y-6 animate-fade-in">
          
          <!-- Master Lists (Project, Department, Tactix Dept, Tactix Customer, Tactix Team) -->
          <div class="space-y-4">
            <!-- Controls & Search -->
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-slate-100 shadow-sm">
              <div class="relative w-full sm:max-w-xs">
                <input 
                  type="text" 
                  v-model="searchQuery"
                  placeholder="Search records..."
                  class="w-full pl-8 pr-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/25 focus:border-blue-500 hover:bg-slate-100/30 transition-all"
                />
                <IconSearch class="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-slate-400" />
              </div>
              <div class="flex items-center gap-2 w-full sm:w-auto justify-end">
                <Dropdown
                  v-if="isAdmin && selectedRecords.size > 0"
                  :options="actionsOptions"
                >
                  <Button
                    variant="solid"
                    class="!bg-slate-800 !text-white !text-xs !px-4 !h-8 rounded-md hover:!bg-slate-900 transition-all font-medium"
                  >
                    Actions
                    <template #suffix><FeatherIcon name="chevron-down" class="w-3.5 h-3.5 shrink-0" /></template>
                  </Button>
                </Dropdown>

                <Button 
                  v-if="isAdmin"
                  variant="solid" 
                  class="!h-8 !px-3 font-semibold text-xs flex items-center gap-1 w-full sm:w-auto justify-center !bg-slate-800 hover:!bg-slate-900 !text-white transition-all"
                  @click="openCreateModal"
                >
                  <template #prefix><IconPlus class="w-3.5 h-3.5" /></template>
                  Create New {{ currentTabLabelSingular }}
                </Button>
              </div>
            </div>

            <!-- Master List Table -->
            <div class="bg-white rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col min-h-[420px] md:min-h-0 md:flex-1 md:overflow-hidden">
              <div v-if="loadingRecords" class="flex justify-center py-12">
                <div class="w-6 h-6 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
              </div>
              <div v-else-if="filteredRecords.length === 0" class="text-center py-12 text-slate-400 italic text-xs font-semibold">
                No records found.
              </div>
              <ListView
                v-else
                class="h-full flex flex-col min-h-0"
                :columns="columns"
                :rows="paginatedRecords || []"
                :options="{ selectable: isAdmin, showTooltip: true, resizeColumn: true, onRowClick: (row) => isAdmin && openEditModal(row) }"
                row-key="name"
                v-model:selections="selectedRecords"
              >
                <ListHeader class="shrink-0 bg-slate-50 border-b border-slate-200 shadow-sm">
                  <ListHeaderItem v-for="col in columns" :key="col.key" :item="col">
                    <template #prefix="{ item }">
                      <component :is="item.icon" class="size-3.5 text-slate-400" v-if="item.icon" />
                    </template>
                  </ListHeaderItem>
                </ListHeader>
                <div class="flex-grow md:flex-1 overflow-y-auto custom-scrollbar relative min-h-0 max-h-[480px] md:max-h-none">
                  <ListRows>
                    <ListRow v-for="row in (paginatedRecords || [])" :key="row.name" v-slot="{ column, item }" :row="row">
                      <ListRowItem :item="item">
                        <template v-if="column.key === 'name'">
                          <span class="font-semibold text-slate-800">{{ row.name }}</span>
                        </template>
                        <template v-if="column.key === 'project_name'">
                          <span class="text-slate-600">{{ row.project_name }}</span>
                        </template>
                        <template v-if="column.key === 'company'">
                          <span class="text-slate-600">{{ row.company }}</span>
                        </template>
                        <template v-if="column.key === 'department_name'">
                          <span class="text-slate-600">{{ row.department_name }}</span>
                        </template>
                        <template v-if="column.key === 'department_head'">
                          <span class="text-slate-600">{{ row.department_head || 'None' }}</span>
                        </template>
                        <template v-if="column.key === 'team_name'">
                          <span class="text-slate-600">{{ row.team_name }}</span>
                        </template>
                        <template v-if="column.key === 'team_lead'">
                          <span class="text-slate-600">{{ getUserLabel(row.team_lead) }}</span>
                        </template>
                        <template v-if="column.key === 'members'">
                          <div class="flex flex-wrap gap-1 max-w-xs items-center">
                            <Badge 
                              v-for="m in (row.members || []).slice(0, 3)" 
                              :key="m" 
                              theme="blue" 
                              variant="subtle" 
                              class="font-semibold text-[9px]"
                            >
                              {{ getUserLabel(m) }}
                            </Badge>
                            <span v-if="(row.members || []).length > 3" class="text-[10px] text-slate-400 font-bold pl-1">
                              +{{ (row.members || []).length - 3 }} more
                            </span>
                            <span v-if="!(row.members && row.members.length)" class="text-slate-400 text-xs">—</span>
                          </div>
                        </template>
                        <template v-if="column.key === 'actions'">
                          <div class="flex items-center justify-end space-x-1.5" v-if="isAdmin">
                            <Button 
                              variant="ghost" 
                              class="!text-slate-600 hover:!bg-slate-100 !p-1.5 rounded-lg"
                              @click.stop="openEditModal(row)"
                            >
                              <template #prefix><IconEdit class="w-3.5 h-3.5" /></template>
                            </Button>
                            <Button 
                              variant="ghost" 
                              class="!text-red-600 hover:!bg-red-50 !p-1.5 rounded-lg"
                              @click.stop="confirmSingleDelete(row.name)"
                            >
                              <template #prefix><IconTrash class="w-3.5 h-3.5" /></template>
                            </Button>
                          </div>
                        </template>
                      </ListRowItem>
                    </ListRow>
                  </ListRows>
                </div>
              </ListView>

              <!-- Pagination Bar -->
              <div class="flex items-center justify-between border-t border-slate-100 bg-white px-4 py-2 shrink-0">
                <div class="flex items-center gap-1">
                  <!-- First Page (<<) -->
                  <Button
                    variant="ghost"
                    size="sm"
                    :disabled="currentPage === 1"
                    @click="currentPage = 1"
                    title="First Page"
                    class="!p-1 !h-6 text-slate-500 hover:text-slate-800 disabled:opacity-30"
                  >
                    <template #prefix><IconChevronsLeft class="w-3.5 h-3.5" /></template>
                  </Button>

                  <!-- Previous Page (<) -->
                  <Button
                    variant="ghost"
                    size="sm"
                    :disabled="currentPage === 1"
                    @click="currentPage = Math.max(1, currentPage - 1)"
                    title="Previous Page"
                    class="!p-1 !h-6 text-slate-500 hover:text-slate-800 disabled:opacity-30"
                  >
                    <template #prefix><IconChevronLeft class="w-3.5 h-3.5" /></template>
                  </Button>

                  <!-- Compact Popover Page Selector -->
                  <Popover>
                    <template #target="{ togglePopover }">
                      <button
                        @click="togglePopover"
                        class="h-6 px-2 text-[11px] font-bold text-slate-700 hover:bg-slate-100 rounded border border-slate-200/80 transition-all flex items-center gap-1 cursor-pointer shrink-0"
                      >
                        <span>{{ currentPage }} / {{ totalPages }}</span>
                        <IconChevronDown class="w-3 h-3 text-slate-400" />
                      </button>
                    </template>
                    <template #body="{ close }">
                      <div class="p-1 max-h-48 overflow-y-auto w-32 bg-white rounded-lg shadow-lg border border-slate-200 custom-scrollbar">
                        <button
                          v-for="p in totalPages"
                          :key="p"
                          @click="currentPage = p; close()"
                          :class="[
                            'w-full text-left px-2 py-1 text-xs rounded transition-colors cursor-pointer flex items-center justify-between',
                            currentPage === p
                              ? 'bg-slate-900 text-white font-bold'
                              : 'text-slate-700 hover:bg-slate-100'
                          ]"
                        >
                          <span>Page {{ p }}</span>
                          <IconCheck v-if="currentPage === p" class="w-3 h-3" />
                        </button>
                      </div>
                    </template>
                  </Popover>

                  <!-- Next Page (>) -->
                  <Button
                    variant="ghost"
                    size="sm"
                    :disabled="currentPage >= totalPages"
                    @click="currentPage = Math.min(totalPages, currentPage + 1)"
                    title="Next Page"
                    class="!p-1 !h-6 text-slate-500 hover:text-slate-800 disabled:opacity-30"
                  >
                    <template #prefix><IconChevronRight class="w-3.5 h-3.5" /></template>
                  </Button>

                  <!-- Last Page (>>) -->
                  <Button
                    variant="ghost"
                    size="sm"
                    :disabled="currentPage >= totalPages"
                    @click="currentPage = totalPages"
                    title="Last Page"
                    class="!p-1 !h-6 text-slate-500 hover:text-slate-800 disabled:opacity-30"
                  >
                    <template #prefix><IconChevronsRight class="w-3.5 h-3.5" /></template>
                  </Button>
                </div>

                <div class="text-xs text-slate-500 font-medium">
                  Showing <span class="font-bold text-slate-800">{{ totalCount > 0 ? (currentPage - 1) * pageLength + 1 : 0 }} - {{ Math.min(currentPage * pageLength, totalCount) }}</span> of <span class="font-bold text-slate-800">{{ totalCount }}</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </template>
    </Tabs>

    <!-- Create/Edit Modal Dialog -->
    <Dialog v-model="modal.show" :options="dialogOptions">
      <template #body-content>
        <div class="space-y-4 py-1.5 text-left">
          <!-- Fields for Project -->
          <template v-if="activeTab === 'project'">
            <FormControl type="text" label="Project Name *" v-model="modal.form.project_name" placeholder="Enter project name" />
            <div class="space-y-1.5">
              <label class="block text-xs text-ink-gray-5">Company *</label>
              <Autocomplete
                ref="projectCompanyAutocomplete"
                :options="linkOptions.companies || []"
                :modelValue="modal.form.company"
                @update:modelValue="val => modal.form.company = val?.value || val || ''"
                :compare-fn="compareOption"
                :max-options="100"
              >
                <template #target>
                  <button
                    type="button"
                    @click="() => projectCompanyAutocomplete?.togglePopover()"
                    class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
                  >
                    <span class="truncate">{{ getCompanyLabel(modal.form.company) }}</span>
                    <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
                  </button>
                </template>
              </Autocomplete>
            </div>
          </template>

          <!-- Fields for Department -->
          <template v-if="activeTab === 'department'">
            <FormControl type="text" label="Department Name *" v-model="modal.form.department_name" placeholder="Enter department name" />
            <div class="space-y-1.5">
              <label class="block text-xs text-ink-gray-5">Company *</label>
              <Autocomplete
                ref="departmentCompanyAutocomplete"
                :options="linkOptions.companies || []"
                :modelValue="modal.form.company"
                @update:modelValue="val => modal.form.company = val?.value || val || ''"
                :compare-fn="compareOption"
                :max-options="100"
              >
                <template #target>
                  <button
                    type="button"
                    @click="() => departmentCompanyAutocomplete?.togglePopover()"
                    class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
                  >
                    <span class="truncate">{{ getCompanyLabel(modal.form.company) }}</span>
                    <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
                  </button>
                </template>
              </Autocomplete>
            </div>
          </template>

          <!-- Fields for Tactix Department -->
          <template v-if="activeTab === 'tactix_dept'">
            <FormControl type="text" label="Department Name *" v-model="modal.form.department_name" placeholder="Enter department name" />
            <div class="space-y-1.5">
              <label class="block text-xs text-ink-gray-5">Department Head</label>
              <Autocomplete
                ref="departmentHeadAutocomplete"
                :options="userOptions || []"
                :modelValue="modal.form.department_head"
                @update:modelValue="val => modal.form.department_head = val?.value || val || ''"
                :compare-fn="compareOption"
                :max-options="100"
              >
                <template #target>
                  <button
                    type="button"
                    @click="() => departmentHeadAutocomplete?.togglePopover()"
                    class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
                  >
                    <span class="truncate">{{ getUserLabel(modal.form.department_head) }}</span>
                    <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
                  </button>
                </template>
              </Autocomplete>
            </div>
          </template>

          <!-- Fields for Tactix Customer -->
          <template v-if="activeTab === 'tactix_cust'">
            <FormControl type="text" label="Customer Name / ID *" v-model="modal.form.name" :disabled="modal.isEdit" placeholder="Enter customer name" />
          </template>

          <!-- Fields for Tactix Team -->
          <template v-if="activeTab === 'tactix_team'">
            <FormControl type="text" label="Team Name *" v-model="modal.form.team_name" placeholder="Enter team name" />
            <div class="space-y-1.5">
              <label class="block text-xs text-ink-gray-5">Team Lead</label>
              <Autocomplete
                ref="teamLeadAutocomplete"
                :options="userOptions || []"
                :modelValue="modal.form.team_lead"
                @update:modelValue="val => modal.form.team_lead = val?.value || val || ''"
                :compare-fn="compareOption"
                :max-options="100"
              >
                <template #target>
                  <button
                    type="button"
                    @click="() => teamLeadAutocomplete?.togglePopover()"
                    class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
                  >
                    <span class="truncate">{{ getUserLabel(modal.form.team_lead) }}</span>
                    <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
                  </button>
                </template>
              </Autocomplete>
            </div>
            <div class="space-y-1">
              <label class="block text-xs font-medium text-slate-600">Team Members (Employees Only)</label>
              <MultiSelect
                :options="userOptions"
                v-model="modal.form.members"
                placeholder="Select team members"
              />
            </div>
          </template>
        </div>
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model="deleteConfirm.show" 
      :disable-outside-click-to-close="true"
      :options="{
        title: deleteConfirm.isBulk ? `Delete ${deleteConfirm.count} ${currentTabLabelSingular}(s)` : `Delete ${currentTabLabelSingular}`,
        size: 'sm',
        actions: [
          { label: 'Delete', variant: 'solid', theme: 'red', loading: deleteConfirm.loading, onClick: executeDelete },
          { label: 'Cancel', variant: 'ghost', onClick: () => (deleteConfirm.show = false) }
        ]
      }"
    >
      <template #body-content>
        <p class="text-sm text-slate-600 leading-relaxed py-2">
          <span v-if="deleteConfirm.isBulk">
            This will permanently remove <span class="font-bold text-slate-900">{{ deleteConfirm.count }}</span> selected {{ currentTabLabelSingular.toLowerCase() }}(s). This action cannot be undone.
          </span>
          <span v-else>
            This will permanently remove <span class="font-bold text-slate-900">{{ deleteConfirm.targetName }}</span>. This action cannot be undone.
          </span>
        </p>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import {
	Autocomplete,
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
import { computed, reactive, ref, watch } from "vue"

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
	if (!val) return "Select Company"
	const match = linkOptions.companies?.find((c) => (typeof c === "object" ? c.value === val : c === val))
	return match ? (typeof match === "object" ? match.label : match) : val
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

const tabIndex = ref(0)
const tabs = [
	{ label: "Projects", id: "project" },
	{ label: "Departments", id: "department" },
	{ label: "Tactix Departments", id: "tactix_dept" },
	{ label: "Tactix Customers", id: "tactix_cust" },
	{ label: "Tactix Teams", id: "tactix_team" },
]

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
		case "tactix_dept":
			return "Tactix Department"
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
		case "tactix_dept":
			return "Tactix Department"
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
				...(isAdmin.value ? [{ label: "Actions", key: "actions", width: "100px" }] : []),
			]
		case "department":
			return [
				{ label: "Name / ID", key: "name", width: "200px" },
				{ label: "Department Name", key: "department_name" },
				{ label: "Company", key: "company", width: "200px" },
				...(isAdmin.value ? [{ label: "Actions", key: "actions", width: "100px" }] : []),
			]
		case "tactix_dept":
			return [
				{ label: "Name / ID", key: "name", width: "200px" },
				{ label: "Department Name", key: "department_name" },
				{ label: "Head of Dept", key: "department_head", width: "250px" },
				...(isAdmin.value ? [{ label: "Actions", key: "actions", width: "100px" }] : []),
			]
		case "tactix_cust":
			return [
				{ label: "Name / ID", key: "name" },
				...(isAdmin.value ? [{ label: "Actions", key: "actions", width: "100px" }] : []),
			]
		case "tactix_team":
			return [
				{ label: "Name / ID", key: "name", width: "160px" },
				{ label: "Team Name", key: "team_name", width: "180px" },
				{ label: "Team Lead", key: "team_lead", width: "200px" },
				{ label: "Team Members", key: "members" },
				...(isAdmin.value ? [{ label: "Actions", key: "actions", width: "100px" }] : []),
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
	if (!userName) return "—"
	const match = usersResource.data?.find((u) => u.name === userName || u.value === userName)
	return match ? (match.full_name || match.label || userName) : userName
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
const fetchMasterRecords = async () => {
	loadingRecords.value = true
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
		masterRecords.value = data.message || []
	} catch (err) {
		console.error("Error fetching master records:", err)
		masterRecords.value = []
	} finally {
		loadingRecords.value = false
	}
}

watch(activeTab, () => {
	selectedRecords.value.clear()
	fetchMasterRecords()
})

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
const totalPages = computed(() => Math.ceil(totalCount.value / pageLength.value) || 1)

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
	recordId: null,
	form: {},
})

const dialogOptions = computed(() => ({
	title: `${modal.isEdit ? "Edit" : "Create"} ${currentTabLabelSingular.value}`,
	size: "md",
	actions: [
		{
			label: modal.isEdit ? "Update" : "Save",
			variant: "solid",
			onClick: submitModalForm,
		},
	],
}))

function openCreateModal() {
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
	modal.isEdit = true
	modal.recordId = row.name
	modal.form = { ...row, members: row.members ? [...row.members] : [] }
	modal.show = true
}

async function submitModalForm() {
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

		const res = await fetch(
			"/api/method/tactix.api.masters.save_master_record",
			{
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(payload),
			},
		)
		const data = await res.json()
		if (data.message?.status === "success") {
			modal.show = false
			fetchMasterRecords()
		} else {
			alert(data.message?.error || "Error saving record")
		}
	} catch (err) {
		console.error("Error submitting form:", err)
		alert("Failed to submit form")
	}
}

function confirmSingleDelete(name) {
	deleteConfirm.isBulk = false
	deleteConfirm.targetName = name
	deleteConfirm.count = 1
	deleteConfirm.show = true
}

function confirmBulkDelete() {
	deleteConfirm.isBulk = true
	deleteConfirm.targetName = null
	deleteConfirm.count = selectedRecords.value.size
	deleteConfirm.show = true
}

async function executeDelete() {
	deleteConfirm.loading = true
	try {
		if (deleteConfirm.isBulk) {
			for (const name of Array.from(selectedRecords.value)) {
				await fetch("/api/method/tactix.api.masters.save_master_record", {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({
						action: "delete",
						doctype: currentTabDoctype.value,
						name,
					}),
				})
			}
			selectedRecords.value.clear()
		} else if (deleteConfirm.targetName) {
			await fetch("/api/method/tactix.api.masters.save_master_record", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					action: "delete",
					doctype: currentTabDoctype.value,
					name: deleteConfirm.targetName,
				}),
			})
			selectedRecords.value.delete(deleteConfirm.targetName)
		}
		deleteConfirm.show = false
		fetchMasterRecords()
	} catch (err) {
		console.error("Error deleting record(s):", err)
		alert("Failed to delete record(s)")
	} finally {
		deleteConfirm.loading = false
	}
}
</script>

<style scoped>
.animate-fade-in {
	animation: fadeIn 0.2s ease-out forwards;
}
@keyframes fadeIn {
	from {
		opacity: 0;
		transform: translateY(4px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}
</style>