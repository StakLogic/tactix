<template>
  <div class="h-full overflow-y-auto p-6 space-y-6 custom-scrollbar bg-slate-50/50">
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
        <div class="pt-4 space-y-6 animate-fade-in">
          
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

            <!-- Master List Table -->
            <Card class="!shadow-sm bg-white border border-slate-200/60 overflow-hidden">
              <div v-if="loadingRecords" class="flex justify-center py-12">
                <div class="w-6 h-6 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
              </div>
              <div v-else-if="filteredRecords.length === 0" class="text-center py-12 text-slate-400 italic text-xs font-semibold">
                No records found.
              </div>
              <div v-else class="overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr class="bg-slate-50/50 border-b border-slate-100 text-[10px] font-black text-slate-400 uppercase tracking-wider">
                      <th class="p-4">Name / ID</th>
                      <th class="p-4" v-if="activeTab === 'project'">Project Name</th>
                      <th class="p-4" v-if="activeTab === 'project' || activeTab === 'department'">Company</th>
                      <th class="p-4" v-if="activeTab === 'department'">Department Name</th>
                      <th class="p-4" v-if="activeTab === 'tactix_dept'">Department Name</th>
                      <th class="p-4" v-if="activeTab === 'tactix_dept'">Head of Dept</th>
                      <th class="p-4" v-if="activeTab === 'tactix_team'">Team Name</th>
                      <th class="p-4" v-if="activeTab === 'tactix_team'">Team Lead</th>
                      <th class="p-4 text-right" v-if="isAdmin">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100">
                    <tr 
                      v-for="row in filteredRecords" 
                      :key="row.name" 
                      class="hover:bg-slate-50/40 transition-colors"
                    >
                      <td class="p-4 font-semibold text-slate-800">{{ row.name }}</td>
                      <td class="p-4 text-slate-600" v-if="activeTab === 'project'">{{ row.project_name }}</td>
                      <td class="p-4 text-slate-600" v-if="activeTab === 'project' || activeTab === 'department'">{{ row.company }}</td>
                      <td class="p-4 text-slate-600" v-if="activeTab === 'department'">{{ row.department_name }}</td>
                      <td class="p-4 text-slate-600" v-if="activeTab === 'tactix_dept'">{{ row.department_name }}</td>
                      <td class="p-4 text-slate-600" v-if="activeTab === 'tactix_dept'">{{ row.department_head || 'None' }}</td>
                      <td class="p-4 text-slate-600" v-if="activeTab === 'tactix_team'">{{ row.team_name }}</td>
                      <td class="p-4 text-slate-600" v-if="activeTab === 'tactix_team'">{{ row.team_lead || 'None' }}</td>
                      <td class="p-4 text-right space-x-1.5" v-if="isAdmin">
                        <Button 
                          variant="ghost" 
                          class="!text-slate-600 hover:!bg-slate-100 !p-1.5 rounded-lg"
                          @click="openEditModal(row)"
                        >
                          <template #prefix><IconEdit class="w-3.5 h-3.5" /></template>
                        </Button>
                        <Button 
                          variant="ghost" 
                          class="!text-red-600 hover:!bg-red-50 !p-1.5 rounded-lg"
                          @click="deleteRecord(row.name)"
                        >
                          <template #prefix><IconTrash class="w-3.5 h-3.5" /></template>
                        </Button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </Card>
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
            <FormControl type="select" label="Company *" v-model="modal.form.company" :options="linkOptions.companies" />
          </template>

          <!-- Fields for Department -->
          <template v-if="activeTab === 'department'">
            <FormControl type="text" label="Department Name *" v-model="modal.form.department_name" placeholder="Enter department name" />
            <FormControl type="select" label="Company *" v-model="modal.form.company" :options="linkOptions.companies" />
          </template>

          <!-- Fields for Tactix Department -->
          <template v-if="activeTab === 'tactix_dept'">
            <FormControl type="text" label="Department Name *" v-model="modal.form.department_name" placeholder="Enter department name" />
            <FormControl type="select" label="Department Head" v-model="modal.form.department_head" :options="userOptions" />
          </template>

          <!-- Fields for Tactix Customer -->
          <template v-if="activeTab === 'tactix_cust'">
            <FormControl type="text" label="Customer Name / ID *" v-model="modal.form.name" :disabled="modal.isEdit" placeholder="Enter customer name" />
          </template>

          <!-- Fields for Tactix Team -->
          <template v-if="activeTab === 'tactix_team'">
            <FormControl type="text" label="Team Name *" v-model="modal.form.team_name" placeholder="Enter team name" />
            <FormControl type="select" label="Team Lead" v-model="modal.form.team_lead" :options="userOptions" />
          </template>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import {
	Button,
	Card,
	Dialog,
	FormControl,
	Tabs,
	createResource,
} from "frappe-ui"
import { computed, reactive, ref, watch } from "vue"

// Icons
import IconArrowLeft from "~icons/lucide/arrow-left"
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
		label: `${u.full_name} (${u.name})`,
		value: u.name,
	}))
})

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
	modal.form = {}
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
	modal.form = { ...row }
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

async function deleteRecord(name) {
	if (!confirm(`Are you sure you want to delete ${name}?`)) return
	try {
		const res = await fetch(
			"/api/method/tactix.api.masters.save_master_record",
			{
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					action: "delete",
					doctype: currentTabDoctype.value,
					name,
				}),
			},
		)
		const data = await res.json()
		if (data.message?.status === "success") {
			fetchMasterRecords()
		} else {
			alert(data.message?.error || "Error deleting record")
		}
	} catch (err) {
		console.error("Error deleting record:", err)
		alert("Failed to delete record")
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