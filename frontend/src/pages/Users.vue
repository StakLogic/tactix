<template>
  <div class="flex flex-col h-full overflow-hidden min-h-0 bg-slate-50/50">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-slate-100 pb-2.5 px-4 pt-4 flex-shrink-0">
      <div>
        <h1 class="text-xl font-black text-slate-900 leading-tight">User & Team Management</h1>
        <p class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mt-1">Administer user accounts, security roles, permissions, and team departments</p>
      </div>
      <Button 
        variant="ghost" 
        class="!text-slate-600 hover:!bg-slate-100/50"
        @click="$router.back()"
      >
        <template #prefix><IconArrowLeft class="w-4 h-4" /></template>
        Back
      </Button>
    </div>

    <!-- Controls & Search -->
    <div class="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white p-3 rounded-xl border border-slate-200 shadow-sm mx-2 my-2 flex-shrink-0">
      <div class="relative w-full sm:max-w-xs">
        <input 
          type="text" 
          v-model="searchQuery"
          placeholder="Search users by name or email..."
          class="w-full pl-8 pr-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/25 focus:border-blue-500 hover:bg-slate-100/30 transition-all"
        />
        <IconSearch class="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-slate-400" />
      </div>
      <div class="flex items-center gap-2">
        <Dropdown
          v-if="selectedUsers.size > 0"
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
          variant="solid" 
          class="!h-8 !px-3 font-semibold text-xs flex items-center gap-1 !bg-slate-800 hover:!bg-slate-900 !text-white transition-all"
          @click="openCreateModal"
        >
          <template #prefix><IconPlus class="w-3.5 h-3.5" /></template>
          Add New User
        </Button>
      </div>
    </div>

    <!-- Users Table -->
    <div class="flex-1 overflow-y-auto md:overflow-hidden px-2 pb-4 flex flex-col min-h-0">
      <div class="bg-white rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col overflow-hidden min-h-[420px] md:min-h-0 md:flex-1 md:overflow-hidden">
        <div v-if="loading" class="flex justify-center py-12">
          <div class="w-6 h-6 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
        </div>
        <div v-else-if="filteredUsers.length === 0" class="text-center py-12 text-slate-400 italic text-xs font-semibold">
          No users found.
        </div>
        <ListView
          v-else
          class="h-full flex flex-col min-h-0"
          :columns="columns"
          :rows="filteredUsers || []"
          :options="{ selectable: true, showTooltip: true, resizeColumn: true, onRowClick: (row) => openEditModal(row) }"
          row-key="email"
          v-model:selections="selectedUsers"
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
              <ListRow v-for="row in (filteredUsers || [])" :key="row.email" v-slot="{ column, item }" :row="row">
                <ListRowItem :item="item">
                  <template v-if="column.key === 'user'">
                    <div class="flex items-center gap-3 py-1">
                      <Avatar :image="row.user_image" :label="row.first_name || row.email" size="md" class="shadow-sm border border-slate-100 shrink-0" />
                      <div class="flex flex-col min-w-0">
                        <span class="font-semibold text-slate-800 truncate">{{ row.first_name }} {{ row.last_name || '' }}</span>
                        <span class="text-[10px] text-slate-400 font-medium truncate">{{ row.email }}</span>
                      </div>
                    </div>
                  </template>
                  <template v-if="column.key === 'status'">
                    <Badge 
                      :theme="row.enabled ? 'green' : 'gray'" 
                      variant="subtle" 
                      class="font-black text-[9px] uppercase tracking-wide px-2 py-0.5"
                    >
                      {{ row.enabled ? 'Active' : 'Disabled' }}
                    </Badge>
                  </template>
                  <template v-if="column.key === 'department'">
                    <span class="font-medium text-slate-600 text-xs">
                      {{ row.department || 'Unassigned' }}
                    </span>
                  </template>
                  <template v-if="column.key === 'roles'">
                    <div class="flex flex-wrap gap-1 max-w-sm">
                      <Badge 
                        v-for="role in mapDbToUiRoles(row.roles || []).slice(0, 3)" 
                        :key="role"
                        theme="blue" 
                        variant="subtle" 
                        class="font-bold text-[8px] uppercase tracking-wide px-1.5 py-px"
                      >
                        {{ role }}
                      </Badge>
                      <span v-if="mapDbToUiRoles(row.roles || []).length > 3" class="text-[9px] text-slate-400 font-bold self-center pl-1">
                        +{{ mapDbToUiRoles(row.roles || []).length - 3 }} more
                      </span>
                    </div>
                  </template>
                  <template v-if="column.key === 'actions'">
                    <div class="flex items-center justify-end space-x-1.5">
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
                        @click.stop="confirmSingleDelete(row.email)"
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
      </div>
    </div>

    <!-- Create/Edit User Modal Dialog -->
    <Dialog v-model="modal.show" :disable-outside-click-to-close="true" :options="dialogOptions">
      <template #body-content>
        <div class="space-y-4 py-1.5 text-left">
          <!-- General User Info -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormControl type="text" label="First Name *" v-model="modal.form.first_name" placeholder="First name" />
            <FormControl type="text" label="Last Name" v-model="modal.form.last_name" placeholder="Last name" />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormControl type="text" label="Email Address *" v-model="modal.form.email" :disabled="modal.isEdit" placeholder="user@example.com" />
            <FormControl type="password" :label="modal.isEdit ? 'Reset Password (Optional)' : 'Password *'" v-model="modal.form.password" placeholder="Enter password" />
          </div>

          <!-- Team / Department Selection -->
          <FormControl type="select" label="Team / Department" v-model="modal.form.department" :options="departmentOptions" />

          <!-- Employee Details (Hidden if Ticket Raiser) -->
          <div v-if="!modal.form.roles.includes('Ticker Raiser')" class="space-y-4 pt-2 border-t border-slate-100 text-left">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormControl 
                type="select" 
                label="Gender *" 
                v-model="modal.form.gender" 
                :options="[
                  { label: 'Male', value: 'Male' },
                  { label: 'Female', value: 'Female' },
                  { label: 'Other', value: 'Other' }
                ]" 
              />
              <FormControl type="text" label="GitHub Username" v-model="modal.form.github_username" placeholder="GitHub username" />
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormControl type="date" label="Date of Birth *" v-model="modal.form.date_of_birth" />
              <FormControl type="date" label="Date of Joining *" v-model="modal.form.date_of_joining" />
            </div>
          </div>

          <!-- Enabled switch using Frappe UI Switch component -->
          <div class="p-2 bg-slate-50 rounded-xl border border-slate-100">
            <Switch
              v-model="modal.form.enabled"
              label="User Account Enabled"
              description="Toggle login permissions for this user"
              size="md"
            />
          </div>

          <!-- Roles Selection Checklist -->
          <div class="space-y-2 text-left">
            <label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Security Roles & Permissions</label>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <button
                v-for="role in displayRoles"
                :key="role"
                type="button"
                @click="toggleRole(role)"
                :class="[
                  'flex items-center justify-between p-3 rounded-xl border text-xs font-semibold transition-all duration-200 text-left',
                  modal.form.roles.includes(role)
                    ? 'border-blue-500 bg-blue-50/50 text-blue-700 shadow-sm'
                    : 'border-slate-200 bg-white hover:bg-slate-50 text-slate-600'
                ]"
              >
                <span>{{ role }}</span>
                <span 
                  v-if="modal.form.roles.includes(role)" 
                  class="w-4 h-4 bg-blue-500 text-white rounded-full flex items-center justify-center text-[10px]"
                >
                  ✓
                </span>
                <span 
                  v-else 
                  class="w-4 h-4 border border-slate-300 rounded-full flex items-center justify-center text-[10px]"
                >
                </span>
              </button>
            </div>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model="deleteConfirm.show" 
      :disable-outside-click-to-close="true"
      :options="{
        title: deleteConfirm.isBulk ? 'Delete Selected Users' : 'Delete User Account',
        size: 'sm',
        actions: [
          { label: 'Delete', variant: 'solid', theme: 'red', loading: deleteConfirm.loading, onClick: executeUserDelete },
          { label: 'Cancel', variant: 'ghost', onClick: () => (deleteConfirm.show = false) }
        ]
      }"
    >
      <template #body-content>
        <p class="text-sm text-slate-600 leading-relaxed py-2">
          <span v-if="deleteConfirm.isBulk">
            This will permanently remove <span class="font-bold text-slate-900">{{ deleteConfirm.count }}</span> selected user account(s). This action cannot be undone.
          </span>
          <span v-else>
            This will permanently remove user account <span class="font-bold text-slate-900">{{ deleteConfirm.targetEmail }}</span>. This action cannot be undone.
          </span>
        </p>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import {
	Avatar,
	Badge,
	Button,
	Card,
	Checkbox,
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
	Switch,
	createResource,
} from "frappe-ui"

const columns = [
	{ label: "User", key: "user", width: "280px" },
	{ label: "Status", key: "status", width: "130px" },
	{ label: "Team / Department", key: "department", width: "200px" },
	{ label: "Assigned Roles", key: "roles" },
	{ label: "Actions", key: "actions", width: "100px" },
]
import { computed, reactive, ref, watch } from "vue"

// Icons
import IconArrowLeft from "~icons/lucide/arrow-left"
import IconEdit from "~icons/lucide/pencil"
import IconPlus from "~icons/lucide/plus"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconSearch from "~icons/lucide/search"
import IconTrash from "~icons/lucide/trash-2"

const searchQuery = ref("")
const loading = ref(false)
const users = ref([])
const roles = ref([])
const departments = ref([])

const selectedUsers = ref(new Set())
const deleteConfirm = reactive({
	show: false,
	isBulk: false,
	targetEmail: null,
	count: 0,
	loading: false,
})

const actionsOptions = computed(() => [
	{
		label: `Delete Selected (${selectedUsers.value.size})`,
		icon: "trash-2",
		onClick: confirmBulkDelete,
	},
])

const displayRoles = [
	"Employee (Developer)",
	"System Manager",
	"Code Reviewer",
	"Support Team",
	"Ticker Raiser"
]

function mapDbToUiRoles(dbRoles) {
	const mapped = []
	if (!dbRoles) return mapped
	if (dbRoles.includes("Employee")) mapped.push("Employee (Developer)")
	if (dbRoles.includes("System Manager")) mapped.push("System Manager")
	if (dbRoles.includes("Code Reviewer")) mapped.push("Code Reviewer")
	if (dbRoles.includes("Support Team")) mapped.push("Support Team")
	if (dbRoles.includes("Tactix Ticket Raiser")) mapped.push("Ticker Raiser")
	return mapped
}

function mapUiToDbRoles(uiRoles) {
	const mapped = []
	if (!uiRoles) return mapped
	if (uiRoles.includes("Employee (Developer)")) mapped.push("Employee")
	if (uiRoles.includes("System Manager")) mapped.push("System Manager")
	if (uiRoles.includes("Code Reviewer")) mapped.push("Code Reviewer")
	if (uiRoles.includes("Support Team")) mapped.push("Support Team")
	if (uiRoles.includes("Ticker Raiser")) mapped.push("Tactix Ticket Raiser")
	return mapped
}

function toggleRole(role) {
	const idx = modal.form.roles.indexOf(role)
	if (idx > -1) {
		modal.form.roles.splice(idx, 1)
	} else {
		modal.form.roles.push(role)
	}
}

const departmentOptions = computed(() => [
	{ label: "No Department (Unassigned)", value: "" },
	...departments.value.map((d) => ({ label: d, value: d })),
])

// Fetch raw user data
async function fetchUsersData() {
	loading.value = true
	try {
		const res = await fetch("/api/method/tactix.api.users.get_users_data")
		const data = await res.json()
		if (data.message) {
			users.value = data.message.users || []
			roles.value = data.message.roles || []
			departments.value = data.message.departments || []
		}
	} catch (err) {
		console.error("Failed to load user management details", err)
	} finally {
		loading.value = false
	}
}

const filteredUsers = computed(() => {
	const query = searchQuery.value.toLowerCase().trim()
	if (!query) return users.value

	return users.value.filter((u) => {
		const name = `${u.first_name || ""} ${u.last_name || ""}`.toLowerCase()
		const email = (u.email || "").toLowerCase()
		return name.includes(query) || email.includes(query)
	})
})

// Modal Dialog state
const dialogOptions = computed(() => ({
	title: modal.isEdit ? "Edit User Details" : "Create New User",
	size: "lg",
	actions: [
		{
			label: "Save User",
			variant: "solid",
			loading: modal.saving,
			onClick: saveUserRecord,
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

const modal = reactive({
	show: false,
	isEdit: false,
	saving: false,
	form: {
		first_name: "",
		last_name: "",
		email: "",
		password: "",
		department: "",
		enabled: 1,
		roles: [],
		gender: "",
		date_of_birth: "",
		date_of_joining: "",
		github_username: "",
	},
})

function openCreateModal() {
	modal.show = true
	modal.isEdit = false
	modal.form = {
		first_name: "",
		last_name: "",
		email: "",
		password: "",
		department: "",
		enabled: 1,
		roles: ["Employee (Developer)"], // Default role setup
		gender: "",
		date_of_birth: "",
		date_of_joining: "",
		github_username: "",
	}
}

function openEditModal(user) {
	modal.show = true
	modal.isEdit = true
	modal.form = {
		first_name: user.first_name,
		last_name: user.last_name || "",
		email: user.email,
		password: "",
		department: user.department || "",
		enabled: user.enabled === 1 || user.enabled === true ? 1 : 0,
		roles: mapDbToUiRoles(user.roles || []),
		gender: user.gender || "",
		date_of_birth: user.date_of_birth || "",
		date_of_joining: user.date_of_joining || "",
		github_username: user.github_username || "",
	}
}

async function saveUserRecord() {
	if (!modal.form.first_name || (!modal.isEdit && !modal.form.email)) {
		alert("First Name and Email are mandatory fields.")
		return
	}
	if (!modal.isEdit && !modal.form.password) {
		alert("Password is required for new users.")
		return
	}

	const isTicketRaiser = modal.form.roles.includes("Ticker Raiser")
	if (!isTicketRaiser) {
		if (!modal.form.gender || !modal.form.date_of_birth || !modal.form.date_of_joining) {
			alert("Gender, Date of Birth, and Date of Joining are mandatory fields.")
			return
		}
	}

	const payload = {
		...modal.form,
		roles: mapUiToDbRoles(modal.form.roles || []),
	}

	modal.saving = true
	try {
		const res = await fetch("/api/method/tactix.api.users.save_user", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				email: modal.isEdit ? modal.form.email : null,
				doc_data: JSON.stringify(payload),
			}),
		})
		const data = await res.json()
		if (data.message?.status === "success") {
			modal.show = false
			fetchUsersData()
		} else {
			alert(
				data.message?.error ||
					"Failed to save user. Verify entries or check duplicate email errors.",
			)
		}
	} catch (err) {
		alert("An error occurred while saving the user.")
	} finally {
		modal.saving = false
	}
}

function confirmSingleDelete(email) {
	deleteConfirm.isBulk = false
	deleteConfirm.targetEmail = email
	deleteConfirm.count = 1
	deleteConfirm.show = true
}

function confirmBulkDelete() {
	deleteConfirm.isBulk = true
	deleteConfirm.targetEmail = null
	deleteConfirm.count = selectedUsers.value.size
	deleteConfirm.show = true
}

async function executeUserDelete() {
	deleteConfirm.loading = true
	try {
		if (deleteConfirm.isBulk) {
			for (const email of Array.from(selectedUsers.value)) {
				await fetch("/api/method/tactix.api.users.delete_user", {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({ email }),
				})
			}
			selectedUsers.value.clear()
		} else if (deleteConfirm.targetEmail) {
			await fetch("/api/method/tactix.api.users.delete_user", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ email: deleteConfirm.targetEmail }),
			})
			selectedUsers.value.delete(deleteConfirm.targetEmail)
		}
		deleteConfirm.show = false
		fetchUsersData()
	} catch (err) {
		console.error("Failed to delete user account(s):", err)
		alert("Failed to delete user account(s).")
	} finally {
		deleteConfirm.loading = false
	}
}

// Initial fetch
fetchUsersData()
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