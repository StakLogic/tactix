<template>
  <div class="h-full overflow-y-auto p-6 space-y-6 custom-scrollbar bg-slate-50/50">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-4 gap-4">
      <div class="min-w-0">
        <h1 class="text-xl font-black text-slate-900 leading-tight">Master Data & Integrations</h1>
        <p class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mt-1">Manage system configurations, data sources, and record masters</p>
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

    <!-- Navigation Tabs (Button-based group matching Performance page style) -->
    <div class="flex gap-1.5 border-b border-slate-200 pb-3 overflow-x-auto whitespace-nowrap">
      <Button 
        v-for="tab in tabs" 
        :key="tab.id"
        :variant="activeTab === tab.id ? 'subtle' : 'ghost'"
        class="!text-xs font-bold uppercase tracking-wider !px-3"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </Button>
    </div>

    <!-- Tab Contents -->
    <div class="space-y-6 animate-fade-in">
      
      <!-- Tab 1: GitHub Settings (Sync) -->
      <div v-if="activeTab === 'github'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card class="!shadow-sm bg-white border border-slate-200/60 p-6 space-y-6 lg:col-span-2 flex flex-col justify-between hover:shadow-md transition-all duration-300">
          <div class="space-y-4">
            <div class="flex items-start justify-between">
              <div class="flex items-center gap-3">
                <div class="p-2.5 rounded-xl bg-slate-50 text-slate-600 border border-slate-100">
                  <IconGitBranch class="w-6 h-6" />
                </div>
                <div>
                  <h3 class="text-sm font-black text-slate-800 uppercase tracking-wider">GitHub Integration Settings</h3>
                  <p class="text-xs text-slate-400 font-medium">Sync pull requests and reviewer contributions</p>
                </div>
              </div>
              <Badge 
                :theme="configResource.data?.has_token ? 'green' : 'gray'" 
                variant="subtle" 
                class="font-black text-[9px] uppercase tracking-wide px-2.5 py-0.5"
              >
                {{ configResource.data?.has_token ? 'Connected' : 'Disconnected' }}
              </Badge>
            </div>

            <!-- Configuration Form -->
            <div v-if="isAdmin" class="space-y-4 pt-2 border-t border-slate-100">
              <h4 class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Settings</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-1">
                  <label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Personal Access Token</label>
                  <input 
                    type="password"
                    v-model="githubForm.token"
                    placeholder="••••••••••••••••••••"
                    class="w-full px-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/25 focus:border-blue-500 hover:bg-slate-100/30 transition-all"
                  />
                </div>
                <div class="space-y-1">
                  <label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Organization Names</label>
                  <input 
                    type="text"
                    v-model="githubForm.organization_name"
                    placeholder="e.g. Teciza-Solutions"
                    class="w-full px-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/25 focus:border-blue-500 hover:bg-slate-100/30 transition-all"
                  />
                </div>
              </div>
              <div class="flex flex-wrap items-center gap-2 pt-2">
                <Button 
                  variant="solid" 
                  class="!h-8 !px-3 font-semibold text-xs flex-1 sm:flex-none justify-center !bg-slate-800 hover:!bg-slate-900 !text-white transition-all"
                  :loading="saving"
                  @click="saveGithubConfig"
                >
                  Save Config
                </Button>
                <Button 
                  variant="outline" 
                  class="!text-slate-600 !h-8 !px-3 border border-slate-200 hover:bg-slate-50 font-semibold text-xs flex-1 sm:flex-none justify-center"
                  :loading="syncing"
                  @click="syncPRs"
                >
                  <template #prefix><IconRefresh class="w-3.5 h-3.5" /></template>
                  Sync PRs Now
                </Button>
              </div>
              <p v-if="feedback" :class="`text-[10px] font-bold uppercase tracking-wider mt-1 ${feedback.type === 'success' ? 'text-green-600' : 'text-red-500'}`">
                {{ feedback.message }}
              </p>
            </div>
            <div v-else class="pt-4 border-t border-slate-100 text-xs text-slate-400 italic">
              GitHub settings are configured by system administrators. Only connected state is displayed.
            </div>
          </div>

          <!-- Webhook details -->
          <div class="mt-4 pt-4 border-t border-slate-100 space-y-2 text-xs">
            <div class="flex items-center gap-1.5 font-bold text-slate-700">
              <IconSettings class="w-3.5 h-3.5 text-slate-400" />
              <span>Webhook Integration Details</span>
            </div>
            <p class="text-[11px] text-slate-500 leading-relaxed">
              To enable real-time pull request notifications, register this Webhook URL in your GitHub repository/organization settings under the <b class="text-slate-700">pull_request</b> events scope:
            </p>
            <div class="bg-slate-50 border border-slate-100 p-2.5 rounded-xl font-mono text-[10px] text-slate-600 break-all select-all flex items-center justify-between gap-2">
              <span>{{ webhookUrl }}</span>
              <IconExternalLink class="w-3 h-3 text-slate-400 cursor-pointer hover:text-slate-700" @click="copyWebhook" />
            </div>
          </div>
        </Card>
      </div>

      <!-- Tab 2: Masters (Project, Department, Tactix Department, Tactix Customer) -->
      <div v-else class="space-y-4">
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
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import {
	Badge,
	Button,
	Card,
	Dialog,
	FormControl,
	createResource,
} from "frappe-ui"
import { computed, reactive, ref, watch } from "vue"

// Icons
import IconArrowLeft from "~icons/lucide/arrow-left"
import IconExternalLink from "~icons/lucide/external-link"
import IconGitBranch from "~icons/lucide/git-branch"
import IconEdit from "~icons/lucide/pencil"
import IconPlus from "~icons/lucide/plus"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconSearch from "~icons/lucide/search"
import IconSettings from "~icons/lucide/settings"
import IconTrash from "~icons/lucide/trash-2"

const tabs = [
	{ id: "github", label: "GitHub Sync" },
	{ id: "project", label: "Projects" },
	{ id: "department", label: "Departments" },
	{ id: "tactix_dept", label: "Tactix Departments" },
	{ id: "tactix_cust", label: "Tactix Customers" },
]

const activeTab = ref("github")
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

// GitHub Settings
const configResource = createResource({
	url: "tactix.api.github.get_github_config",
	initialData: { has_token: false, organization_name: "" },
	auto: true,
})

const githubForm = reactive({
	token: "",
	organization_name: "",
})

watch(
	() => configResource.data,
	(data) => {
		if (data) {
			githubForm.token = data.has_token ? "******" : ""
			githubForm.organization_name = data.organization_name || ""
		}
	},
	{ immediate: true },
)

const saving = ref(false)
const syncing = ref(false)
const feedback = ref(null)

const webhookUrl = computed(() => {
	return `${window.location.origin}/api/method/tactix.api.github.handle_webhook`
})

async function saveGithubConfig() {
	saving.value = true
	feedback.value = null
	try {
		const res = await fetch(
			"/api/method/tactix.api.github.save_github_config",
			{
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(githubForm),
			},
		)
		const data = await res.json()
		if (data.message?.status === "success") {
			feedback.value = {
				type: "success",
				message: "Configuration saved successfully!",
			}
			configResource.reload()
		} else {
			feedback.value = {
				type: "error",
				message: "Failed to save configuration.",
			}
		}
	} catch (err) {
		feedback.value = {
			type: "error",
			message: "An error occurred while saving.",
		}
	} finally {
		saving.value = false
	}
}

async function syncPRs() {
	syncing.value = true
	feedback.value = null
	try {
		const res = await fetch(
			"/api/method/tactix.api.github.sync_all_pull_requests",
			{
				method: "POST",
			},
		)
		const data = await res.json()
		if (data.message?.status === "success") {
			feedback.value = {
				type: "success",
				message: "Synchronized pull requests successfully!",
			}
		} else if (data.message?.error) {
			feedback.value = {
				type: "error",
				message: `Sync error: ${data.message.error}`,
			}
		} else {
			feedback.value = {
				type: "success",
				message: "Sync job dispatched successfully in background!",
			}
		}
	} catch (err) {
		feedback.value = {
			type: "error",
			message: "An error occurred while synchronizing.",
		}
	} finally {
		syncing.value = false
	}
}

function copyWebhook() {
	navigator.clipboard.writeText(webhookUrl.value)
	alert("Webhook URL copied to clipboard!")
}

// Master Data Management Logic
const linkOptions = reactive({
	companies: [],
	users: [],
})

const userOptions = computed(() => [
	{ label: "No Head of Dept", value: "" },
	...linkOptions.users.map((u) => ({ label: u, value: u })),
])

async function fetchLinkOptions() {
	try {
		const res = await fetch("/api/method/tactix.api.masters.get_link_options")
		const data = await res.json()
		if (data.message) {
			linkOptions.companies = data.message.companies || []
			linkOptions.users = data.message.users || []
		}
	} catch (err) {
		console.error("Failed to load options", err)
	}
}

async function fetchMasterRecords() {
	if (activeTab.value === "github") return
	loadingRecords.value = true
	try {
		const res = await fetch(
			`/api/method/tactix.api.masters.get_master_records?doctype=${currentTabDoctype.value}`,
		)
		const data = await res.json()
		masterRecords.value = data.message || []
	} catch (err) {
		console.error("Failed to load master records", err)
	} finally {
		loadingRecords.value = false
	}
}

watch(activeTab, () => {
	searchQuery.value = ""
	fetchMasterRecords()
})

const filteredRecords = computed(() => {
	const query = searchQuery.value.toLowerCase().trim()
	if (!query) return masterRecords.value

	return masterRecords.value.filter((row) => {
		return Object.values(row).some((val) =>
			String(val).toLowerCase().includes(query),
		)
	})
})

const dialogOptions = computed(() => ({
	title: `${modal.isEdit ? "Edit" : "Create New"} ${currentTabLabelSingular.value}`,
	size: "md",
	actions: [
		{
			label: "Save Record",
			variant: "solid",
			loading: modal.saving,
			onClick: saveRecord,
		},
		{
			label: "Cancel",
			variant: "ghost",
			onClick: () => {
				modal.show = false
			},
		},
	],
}))

// Modal & Actions Setup
const modal = reactive({
	show: false,
	isEdit: false,
	saving: false,
	name: "",
	form: {},
})

function openCreateModal() {
	modal.show = true
	modal.isEdit = false
	modal.name = ""
	modal.form = {
		project_name: "",
		company: linkOptions.companies[0] || "",
		department_name: "",
		department_head: "",
		name: "",
	}
}

function openEditModal(row) {
	modal.show = true
	modal.isEdit = true
	modal.name = row.name
	modal.form = { ...row }
}

async function saveRecord() {
	modal.saving = true
	try {
		let url = "/api/method/tactix.api.masters.create_master_record"
		const body = {
			doctype: currentTabDoctype.value,
			doc_data: JSON.stringify(modal.form),
		}

		if (modal.isEdit) {
			url = "/api/method/tactix.api.masters.update_master_record"
			body.name = modal.name
		}

		const res = await fetch(url, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(body),
		})
		const data = await res.json()
		if (data.message?.status === "success") {
			modal.show = false
			fetchMasterRecords()
		} else {
			alert(
				data.message?.error ||
					"Failed to save record. Ensure required fields are correct.",
			)
		}
	} catch (err) {
		alert("An error occurred while saving the record.")
	} finally {
		modal.saving = false
	}
}

async function deleteRecord(name) {
	if (!confirm("Are you sure you want to delete this record?")) return
	try {
		const res = await fetch(
			"/api/method/tactix.api.masters.delete_master_record",
			{
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					doctype: currentTabDoctype.value,
					name,
				}),
			},
		)
		const data = await res.json()
		if (data.message?.status === "success") {
			fetchMasterRecords()
		} else {
			alert("Failed to delete record.")
		}
	} catch (err) {
		alert("An error occurred while deleting the record.")
	}
}

// Initial triggers
fetchLinkOptions()
</script>

<style scoped>
.animate-fade-in {
	animation: fadeIn 0.4s ease-out;
}
@keyframes fadeIn {
	from {
		opacity: 0;
		transform: translateY(8px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}
</style>