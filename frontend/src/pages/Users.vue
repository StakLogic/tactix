<template>
  <div class="flex h-full min-h-0 flex-col overflow-hidden">
    <!-- Header -->
    <div class="flex flex-shrink-0 items-center justify-between gap-3 px-1 pb-3 pt-1">
      <div class="flex min-w-0 items-center gap-3">
        <span class="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)]">
          <IconUsers class="h-5 w-5" />
        </span>
        <div class="min-w-0">
          <h1 class="text-base font-semibold leading-tight text-ink-gray-9">Users</h1>
          <p class="truncate text-xs text-ink-gray-5">Accounts, roles and teams</p>
        </div>
      </div>
      <Button variant="ghost" class="shrink-0" @click="$router.back()">
        <template #prefix><IconArrowLeft class="h-4 w-4" /></template>
        Back
      </Button>
    </div>

    <!-- Stats (click to filter) -->
    <div class="grid flex-shrink-0 grid-cols-2 gap-2 px-1 lg:grid-cols-4">
      <div
        v-for="s in stats"
        :key="s.key"
        class="kpi is-clickable"
        :class="statusFilter === s.key && 'is-active'"
        role="button"
        tabindex="0"
        @click="statusFilter = statusFilter === s.key && s.key !== 'all' ? 'all' : s.key"
        @keydown.enter.prevent="statusFilter = s.key"
      >
        <div class="flex items-center justify-between gap-2">
          <span class="truncate text-xs font-medium text-ink-gray-6">{{ s.label }}</span>
          <span class="h-2 w-2 shrink-0 rounded-full" :style="{ background: s.dot }"></span>
        </div>
        <div class="kpi-value">
          <div v-if="loading && !users.length" class="skeleton h-5 w-10"></div>
          <span v-else class="text-[22px] font-semibold leading-none tabular-nums text-ink-gray-9">{{ s.value }}</span>
        </div>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="toolbar-card mx-1 my-2 flex flex-shrink-0 flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:items-center">
        <div class="relative w-full sm:w-72">
          <IconSearch class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-ink-gray-4" />
          <input
            ref="searchInputEl"
            v-model="searchQuery"
            type="text"
            placeholder="Search name or email…"
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

        <!-- Role filter -->
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="r in displayRoles"
            :key="r"
            type="button"
            class="chip"
            :class="roleFilter === r && 'on'"
            @click="roleFilter = roleFilter === r ? '' : r"
          >
            {{ r }}
          </button>
        </div>
      </div>

      <div class="flex items-center justify-end gap-2">
        <template v-if="selectedUsers.size > 0">
          <div class="flex h-8 items-center gap-1 rounded-md bg-surface-gray-2 pl-2.5 pr-1 text-xs text-ink-gray-7">
            <span class="font-medium tabular-nums">{{ selectedUsers.size }} selected</span>
            <button type="button" class="rounded p-1 text-ink-gray-5 hover:bg-surface-gray-3 hover:text-ink-gray-8" title="Clear selection" @click="selectedUsers = new Set()">
              <IconX class="h-3.5 w-3.5" />
            </button>
          </div>
          <Button variant="outline" theme="red" class="!h-8 text-xs" @click="confirmBulkDelete">
            <template #prefix><IconTrash class="h-3.5 w-3.5" /></template>
            Delete
          </Button>
        </template>

        <Button variant="outline" class="!h-8 !px-2.5" title="Refresh" @click="fetchUsersData">
          <template #prefix><IconRefresh class="h-3.5 w-3.5" :class="loading && 'animate-spin'" /></template>
        </Button>
        <Button variant="solid" class="brand-btn !h-8 !px-3 text-xs" @click="openCreateModal">
          <template #prefix><IconPlus class="h-3.5 w-3.5" /></template>
          Add user
        </Button>
      </div>
    </div>

    <p v-if="pageError" class="mx-1 mb-2 flex items-center justify-between gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
      <span>{{ pageError }}</span>
      <button type="button" class="opacity-60 hover:opacity-100" title="Dismiss" @click="pageError = ''"><IconX class="h-3.5 w-3.5" /></button>
    </p>

    <!-- Table -->
    <div class="mx-1 mb-2 flex min-h-0 flex-1 flex-col">
      <div class="panel relative flex min-h-[420px] flex-1 flex-col overflow-hidden md:min-h-0">
        <div v-if="loading && users.length" class="busy-bar" aria-hidden="true"></div>

        <div v-if="loading && !users.length" class="divide-y divide-outline-gray-1">
          <div v-for="n in 6" :key="n" class="flex items-center gap-3 px-4 py-3">
            <div class="skeleton h-8 w-8 rounded-full"></div>
            <div class="flex-1 space-y-1.5">
              <div class="skeleton h-3.5 w-40"></div>
              <div class="skeleton h-3 w-56"></div>
            </div>
            <div class="skeleton h-5 w-16"></div>
          </div>
        </div>

        <div v-else-if="filteredUsers.length === 0" class="flex flex-1 flex-col items-center justify-center px-4 py-16 text-center">
          <span class="grid h-11 w-11 place-items-center rounded-full bg-surface-gray-2 text-ink-gray-5">
            <IconUsers class="h-5 w-5" />
          </span>
          <h3 class="mt-3 text-sm font-semibold text-ink-gray-8">No users found</h3>
          <p class="mt-1 max-w-xs text-xs text-ink-gray-5">
            {{ hasFilters ? 'Nothing matches your search or filters.' : 'Add the first user to get started.' }}
          </p>
          <Button v-if="hasFilters" variant="subtle" size="sm" class="mt-3" @click="clearFilters">Clear filters</Button>
        </div>

        <ListView
          v-else
          class="flex h-full min-h-0 flex-col"
          :columns="columns"
          :rows="paginatedUsers || []"
          :options="{ selectable: true, showTooltip: true, resizeColumn: true, onRowClick: (row) => openEditModal(row) }"
          row-key="email"
          v-model:selections="selectedUsers"
        >
          <ListHeader class="shrink-0 border-b border-outline-gray-2 bg-surface-gray-1">
            <ListHeaderItem v-for="col in columns" :key="col.key" :item="col" />
          </ListHeader>
          <div class="custom-scrollbar relative min-h-0 max-h-[480px] flex-grow overflow-y-auto md:max-h-none md:flex-1">
            <ListRows>
              <ListRow v-for="row in (paginatedUsers || [])" :key="row.email" v-slot="{ column, item }" :row="row" class="cursor-pointer">
                <ListRowItem :item="item">
                  <template v-if="column.key === 'user'">
                    <div class="flex min-w-0 items-center gap-3">
                      <Avatar :image="row.user_image" :label="row.first_name || row.email" size="md" class="shrink-0" />
                      <div class="flex min-w-0 flex-col">
                        <span class="flex items-center gap-1.5 truncate text-sm font-medium text-ink-gray-9">
                          {{ fullName(row) }}
                          <span v-if="row.email === currentUser" class="rounded bg-surface-gray-2 px-1 text-[10px] font-semibold text-ink-gray-6">You</span>
                        </span>
                        <span class="truncate text-xs text-ink-gray-5">{{ row.email }}</span>
                      </div>
                    </div>
                  </template>
                  <template v-if="column.key === 'status'">
                    <span class="status-pill" :class="row.enabled ? 'is-active' : 'is-disabled'">
                      <span class="h-1.5 w-1.5 rounded-full bg-current"></span>{{ row.enabled ? 'Active' : 'Disabled' }}
                    </span>
                  </template>
                  <template v-if="column.key === 'department'">
                    <span class="truncate text-xs" :class="row.department ? 'text-ink-gray-7' : 'text-ink-gray-4'">
                      {{ row.department || 'Unassigned' }}
                    </span>
                  </template>
                  <template v-if="column.key === 'roles'">
                    <div class="flex min-w-0 flex-wrap items-center gap-1">
                      <span v-for="role in mapDbToUiRoles(row.roles || []).slice(0, 3)" :key="role" class="role-tag">{{ role }}</span>
                      <span v-if="mapDbToUiRoles(row.roles || []).length > 3" class="text-[11px] text-ink-gray-5">
                        +{{ mapDbToUiRoles(row.roles || []).length - 3 }}
                      </span>
                      <span v-if="!mapDbToUiRoles(row.roles || []).length" class="text-xs text-ink-gray-4">No roles</span>
                    </div>
                  </template>
                  <template v-if="column.key === 'actions'">
                    <div class="flex items-center justify-end gap-0.5">
                      <button type="button" class="icon-btn" title="Edit" @click.stop="openEditModal(row)">
                        <IconEdit class="h-3.5 w-3.5" />
                      </button>
                      <button
                        type="button"
                        class="icon-btn danger"
                        :disabled="row.email === currentUser"
                        :title="row.email === currentUser ? 'You can\'t delete your own account' : 'Delete'"
                        @click.stop="confirmSingleDelete(row.email)"
                      >
                        <IconTrash class="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </template>
                </ListRowItem>
              </ListRow>
            </ListRows>
          </div>
        </ListView>

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

    <!-- Create / Edit user -->
    <Dialog v-model="modal.show" :disable-outside-click-to-close="true" :options="{ title: modal.isEdit ? 'Edit user' : 'Add user', size: 'xl' }">
      <template #body-content>
        <div class="space-y-5 py-1 text-left">
          <div v-if="modal.errorMessage" class="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
            <span class="flex-1 leading-relaxed">{{ modal.errorMessage }}</span>
            <button type="button" class="shrink-0 opacity-60 hover:opacity-100" title="Dismiss" @click="modal.errorMessage = ''"><IconX class="h-3.5 w-3.5" /></button>
          </div>

          <!-- Account -->
          <section class="space-y-3">
            <h4 class="section-title">Account</h4>
            <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
              <FormControl type="text" label="First name *" v-model="modal.form.first_name" placeholder="First name" />
              <FormControl type="text" label="Last name" v-model="modal.form.last_name" placeholder="Last name" />
            </div>
            <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
              <FormControl type="email" label="Email *" v-model="modal.form.email" :disabled="modal.isEdit" placeholder="user@example.com" />
              <FormControl type="password" :label="modal.isEdit ? 'New password (optional)' : 'Password *'" v-model="modal.form.password" :placeholder="modal.isEdit ? 'Leave empty to keep current' : 'Set a password'" autocomplete="new-password" />
            </div>
            <div class="rounded-lg border border-outline-gray-1 bg-surface-gray-1 p-2.5">
              <Switch v-model="modal.form.enabled" label="Account enabled" description="Disabled users can't sign in" size="md" />
            </div>
          </section>

          <!-- Roles -->
          <section class="space-y-3">
            <h4 class="section-title">Roles</h4>
            <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
              <button
                v-for="role in displayRoles"
                :key="role"
                type="button"
                class="role-card"
                :class="modal.form.roles.includes(role) && 'on'"
                :aria-pressed="modal.form.roles.includes(role)"
                @click="toggleRole(role)"
              >
                <span class="min-w-0 text-left">
                  <span class="block text-xs font-semibold">{{ role }}</span>
                  <span class="block truncate text-[11px] font-normal text-ink-gray-5">{{ ROLE_HINTS[role] }}</span>
                </span>
                <span class="tick"><IconCheck v-if="modal.form.roles.includes(role)" class="h-3 w-3" /></span>
              </button>
            </div>
          </section>

          <!-- Organisation -->
          <section class="space-y-3">
            <h4 class="section-title">{{ isTicketRaiserForm ? 'Customer' : 'Team & employee details' }}</h4>

            <div v-if="isTicketRaiserForm" class="space-y-1.5">
              <label class="block text-xs text-ink-gray-5">Customer *</label>
              <Autocomplete
                ref="customerAutocomplete"
                :options="customerOptions || []"
                :modelValue="modal.form.tactix_customer"
                @update:modelValue="val => modal.form.tactix_customer = val?.value ?? val ?? ''"
                :compare-fn="compareOption"
                :max-options="100"
              >
                <template #target>
                  <button type="button" class="field-btn" @click="() => customerAutocomplete?.togglePopover()">
                    <span class="truncate">{{ getCustomerLabel(modal.form.tactix_customer) }}</span>
                    <FeatherIcon name="chevron-down" class="h-4 w-4 shrink-0 text-ink-gray-5" />
                  </button>
                </template>
              </Autocomplete>
            </div>

            <template v-else>
              <div class="space-y-1.5">
                <label class="block text-xs text-ink-gray-5">Team / department</label>
                <Autocomplete
                  ref="departmentAutocomplete"
                  :options="departmentOptions || []"
                  :modelValue="modal.form.department"
                  @update:modelValue="val => modal.form.department = val?.value ?? val ?? ''"
                  :compare-fn="compareOption"
                  :max-options="100"
                >
                  <template #target>
                    <button type="button" class="field-btn" @click="() => departmentAutocomplete?.togglePopover()">
                      <span class="truncate">{{ getDepartmentLabel(modal.form.department) }}</span>
                      <FeatherIcon name="chevron-down" class="h-4 w-4 shrink-0 text-ink-gray-5" />
                    </button>
                  </template>
                </Autocomplete>
              </div>
              <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
                <div class="space-y-1.5">
                  <label class="block text-xs text-ink-gray-5">Gender *</label>
                  <Autocomplete
                    ref="genderAutocomplete"
                    :options="GENDERS"
                    :modelValue="modal.form.gender"
                    @update:modelValue="val => modal.form.gender = val?.value ?? val ?? ''"
                    :compare-fn="compareOption"
                  >
                    <template #target>
                      <button type="button" class="field-btn" @click="() => genderAutocomplete?.togglePopover()">
                        <span class="truncate">{{ getGenderLabel(modal.form.gender) }}</span>
                        <FeatherIcon name="chevron-down" class="h-4 w-4 shrink-0 text-ink-gray-5" />
                      </button>
                    </template>
                  </Autocomplete>
                </div>
                <FormControl type="text" label="GitHub username" v-model="modal.form.github_username" placeholder="e.g. octocat" />
              </div>
              <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
                <DatePicker label="Date of birth *" v-model="modal.form.date_of_birth" />
                <DatePicker label="Date of joining *" v-model="modal.form.date_of_joining" />
              </div>
            </template>
          </section>
        </div>
      </template>
      <template #actions>
        <div class="dialog-actions">
          <Button variant="solid" class="brand-btn" :loading="modal.saving" @click="saveUserRecord">
            {{ modal.isEdit ? 'Save changes' : 'Create user' }}
          </Button>
          <Button variant="ghost" @click="modal.show = false">Cancel</Button>
        </div>
      </template>
    </Dialog>

    <!-- Delete -->
    <Dialog
      v-model="deleteConfirm.show"
      :disable-outside-click-to-close="true"
      :options="{ title: deleteConfirm.isBulk ? `Delete ${deleteConfirm.count} user${deleteConfirm.count === 1 ? '' : 's'}` : 'Delete user', size: 'sm' }"
    >
      <template #body-content>
        <p class="py-2 text-sm leading-relaxed text-ink-gray-6">
          <template v-if="deleteConfirm.isBulk">
            This will permanently remove <b class="text-ink-gray-9">{{ deleteConfirm.count }}</b> user account{{ deleteConfirm.count === 1 ? '' : 's' }}. This can't be undone.
          </template>
          <template v-else>
            This will permanently remove <b class="break-all text-ink-gray-9">{{ deleteConfirm.targetEmail }}</b>. This can't be undone.
          </template>
        </p>
        <p v-if="deleteConfirm.skippedSelf" class="mb-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
          Your own account is selected and will be skipped.
        </p>
        <p v-if="deleteConfirm.error" class="whitespace-pre-line rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">{{ deleteConfirm.error }}</p>
      </template>
      <template #actions>
        <div class="dialog-actions">
          <Button variant="solid" theme="red" :loading="deleteConfirm.loading" @click="executeUserDelete">Delete</Button>
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
	Popover,
	Select,
	Switch,
	createResource,
} from "frappe-ui"
import { session } from "../data/session"

const departmentAutocomplete = ref(null)
const genderAutocomplete = ref(null)
const customerAutocomplete = ref(null)

function compareOption(a, b) {
	const aVal = a && typeof a === "object" ? a.value : a
	const bVal = b && typeof b === "object" ? b.value : b
	return aVal === bVal
}

function getDepartmentLabel(val) {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return "Select Team / Department"
	const match = departmentOptions.value?.find((d) => d.value === rawVal)
	return match ? match.label : rawVal
}

function getGenderLabel(val) {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return "Select Gender"
	return rawVal
}

function getCustomerLabel(val) {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return "Select Tactix Customer"
	const match = customerOptions.value?.find((c) => c.value === rawVal)
	return match ? match.label : rawVal
}

const columns = [
	{ label: "User", key: "user", width: "300px" },
	{ label: "Status", key: "status", width: "120px" },
	{ label: "Team / Department", key: "department", width: "200px" },
	{ label: "Roles", key: "roles" },
	{ label: "", key: "actions", width: "90px" },
]

const GENDERS = [
	{ label: "Male", value: "Male" },
	{ label: "Female", value: "Female" },
	{ label: "Other", value: "Other" },
]
import { computed, onMounted, onUnmounted, reactive, ref, watch } from "vue"

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
import IconRefresh from "~icons/lucide/refresh-cw"
import IconSearch from "~icons/lucide/search"
import IconTrash from "~icons/lucide/trash-2"
import IconUsers from "~icons/lucide/users"
import IconX from "~icons/lucide/x"

const searchQuery = ref("")
const statusFilter = ref("all") // all | active | disabled | raisers
const roleFilter = ref("")
const pageError = ref("")
const searchInputEl = ref(null)
const currentUser = computed(() => session.user)

function fullName(u) {
	return `${u.first_name || ""} ${u.last_name || ""}`.trim() || u.email
}

// POSTs need the CSRF token, otherwise Frappe rejects them for logged-in users
function getCsrfToken() {
	if (window.csrf_token && window.csrf_token !== "{{ csrf_token }}") return window.csrf_token
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	return cookies.get("csrf_token") || ""
}
function postJSON(url, body) {
	return fetch(url, {
		method: "POST",
		headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": getCsrfToken() },
		body: JSON.stringify(body),
	})
}
const loading = ref(false)
const users = ref([])
const roles = ref([])
const departments = ref([])
const customers = ref([])

const currentPage = ref(1)
const pageLength = ref(20)

watch([searchQuery, statusFilter, roleFilter], () => {
	currentPage.value = 1
})

const selectedUsers = ref(new Set())
const deleteConfirm = reactive({
	show: false,
	isBulk: false,
	targetEmail: null,
	count: 0,
	loading: false,
	error: "",
	skippedSelf: false,
})

const actionsOptions = computed(() => [
	{
		label: `Delete Selected (${selectedUsers.value.size})`,
		icon: "trash-2",
		onClick: confirmBulkDelete,
	},
])

const ROLE_HINTS = {
	"Employee (Developer)": "Tasks, timesheets, drive",
	"System Manager": "Full admin access",
	"Code Reviewer": "Reviews contributions",
	"Support Team": "Handles customer tickets",
	"Ticket Raiser": "External customer, tickets only",
}

const displayRoles = [
	"Employee (Developer)",
	"System Manager",
	"Code Reviewer",
	"Support Team",
	"Ticket Raiser",
]

function mapDbToUiRoles(dbRoles) {
	const mapped = []
	if (!dbRoles) return mapped
	if (dbRoles.includes("Employee")) mapped.push("Employee (Developer)")
	if (dbRoles.includes("System Manager")) mapped.push("System Manager")
	if (dbRoles.includes("Code Reviewer")) mapped.push("Code Reviewer")
	if (dbRoles.includes("Support Team")) mapped.push("Support Team")
	if (dbRoles.includes("Tactix Ticket Raiser")) mapped.push("Ticket Raiser")
	return mapped
}

function mapUiToDbRoles(uiRoles) {
	const mapped = []
	if (!uiRoles) return mapped
	if (uiRoles.includes("Employee (Developer)")) mapped.push("Employee")
	if (uiRoles.includes("System Manager")) mapped.push("System Manager")
	if (uiRoles.includes("Code Reviewer")) mapped.push("Code Reviewer")
	if (uiRoles.includes("Support Team")) mapped.push("Support Team")
	if (uiRoles.includes("Ticket Raiser")) mapped.push("Tactix Ticket Raiser")
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

const customerOptions = computed(() => [
	{ label: "Select Tactix Customer", value: "" },
	...customers.value.map((c) => ({
		label: typeof c === "object" ? c.name : c,
		value: typeof c === "object" ? c.name : c,
	})),
])

// Fetch raw user data
async function fetchUsersData() {
	loading.value = true
	pageError.value = ""
	try {
		const res = await fetch("/api/method/tactix.api.users.get_users_data")
		const data = await res.json()
		if (!res.ok) throw new Error(extractErrorMessage(data))
		if (data.message) {
			users.value = data.message.users || []
			roles.value = data.message.roles || []
			departments.value = data.message.departments || []
			customers.value = data.message.customers || []
		}
	} catch (err) {
		console.error("Failed to load user management details", err)
		pageError.value = "Couldn't load users. " + (err.message || "")
	} finally {
		loading.value = false
	}
}

const isRaiser = (u) => (u.roles || []).includes("Tactix Ticket Raiser")

const stats = computed(() => [
	{ key: "all", label: "All users", value: users.value.length, dot: "var(--brand, #29ADFF)" },
	{ key: "active", label: "Active", value: users.value.filter((u) => u.enabled).length, dot: "#22c55e" },
	{ key: "disabled", label: "Disabled", value: users.value.filter((u) => !u.enabled).length, dot: "#94a3b8" },
	{ key: "raisers", label: "Customers (ticket raisers)", value: users.value.filter(isRaiser).length, dot: "#f59e0b" },
])

const hasFilters = computed(() => !!searchQuery.value.trim() || statusFilter.value !== "all" || !!roleFilter.value)

function clearFilters() {
	searchQuery.value = ""
	statusFilter.value = "all"
	roleFilter.value = ""
}

const filteredUsers = computed(() => {
	const query = searchQuery.value.toLowerCase().trim()
	return users.value.filter((u) => {
		if (statusFilter.value === "active" && !u.enabled) return false
		if (statusFilter.value === "disabled" && u.enabled) return false
		if (statusFilter.value === "raisers" && !isRaiser(u)) return false
		if (roleFilter.value && !mapDbToUiRoles(u.roles || []).includes(roleFilter.value)) return false
		if (!query) return true
		const name = `${u.first_name || ""} ${u.last_name || ""}`.toLowerCase()
		const email = (u.email || "").toLowerCase()
		return name.includes(query) || email.includes(query)
	})
})

const totalCount = computed(() => filteredUsers.value.length)
const totalPages = computed(
	() => Math.ceil(totalCount.value / pageLength.value) || 1,
)

const pageOptions = computed(() =>
	Array.from({ length: totalPages.value }, (_, i) => ({
		label: `${i + 1} / ${totalPages.value}`,
		value: i + 1,
	})),
)
const paginatedUsers = computed(() =>
	filteredUsers.value.slice(
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
	errorMessage: "",
	form: {
		first_name: "",
		last_name: "",
		email: "",
		password: "",
		department: "",
		tactix_customer: "",
		enabled: 1,
		roles: [],
		gender: "",
		date_of_birth: "",
		date_of_joining: "",
		github_username: "",
	},
})

const isTicketRaiserForm = computed(() => (modal.form.roles || []).includes("Ticket Raiser"))

function extractErrorMessage(data) {
	if (!data) return "An unknown error occurred while processing your request."
	if (data.message?.error) return data.message.error
	if (typeof data.message === "string") return data.message
	if (data._server_messages) {
		try {
			const serverMsgs = JSON.parse(data._server_messages)
			const parsedMsgs = serverMsgs.map((m) => {
				try {
					const obj = JSON.parse(m)
					return obj.message || m
				} catch {
					return m
				}
			})
			const text = parsedMsgs
				.join(" ")
				.replace(/<[^>]*>/g, "")
				.trim()
			if (text) return text
		} catch (e) {
			// ignore JSON parse error
		}
	}
	if (data.exception) {
		const parts = data.exception.split(":")
		return parts.length > 1 ? parts.slice(1).join(":").trim() : data.exception
	}
	return "Failed to save user. Verify entries or check duplicate email errors."
}

function openCreateModal() {
	modal.show = true
	modal.isEdit = false
	modal.errorMessage = ""
	modal.form = {
		first_name: "",
		last_name: "",
		email: "",
		password: "",
		department: "",
		tactix_customer: "",
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
	modal.errorMessage = ""
	modal.form = {
		first_name: user.first_name,
		last_name: user.last_name || "",
		email: user.email,
		password: "",
		department: user.department || "",
		tactix_customer: user.tactix_customer || "",
		enabled: user.enabled === 1 || user.enabled === true ? 1 : 0,
		roles: mapDbToUiRoles(user.roles || []),
		gender: user.gender || "",
		date_of_birth: user.date_of_birth || "",
		date_of_joining: user.date_of_joining || "",
		github_username: user.github_username || "",
	}
}

async function saveUserRecord() {
	if (modal.saving) return
	modal.errorMessage = ""

	if (!modal.form.first_name || (!modal.isEdit && !modal.form.email)) {
		modal.errorMessage = "First Name and Email are mandatory fields."
		return
	}
	if (!modal.isEdit && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(modal.form.email.trim())) {
		modal.errorMessage = "Please enter a valid email address."
		return
	}
	if (!modal.form.roles.length) {
		modal.errorMessage = "Select at least one role."
		return
	}
	if (!modal.isEdit && !modal.form.password) {
		modal.errorMessage = "Password is required for new users."
		return
	}

	const isTicketRaiser = modal.form.roles.includes("Ticket Raiser")
	if (isTicketRaiser) {
		if (!modal.form.tactix_customer) {
			modal.errorMessage =
				"Tactix Customer is mandatory for Ticket Raiser users."
			return
		}
	} else {
		if (
			!modal.form.gender ||
			!modal.form.date_of_birth ||
			!modal.form.date_of_joining
		) {
			modal.errorMessage =
				"Gender, Date of Birth, and Date of Joining are mandatory fields."
			return
		}
	}

	const payload = {
		...modal.form,
		roles: mapUiToDbRoles(modal.form.roles || []),
	}

	modal.saving = true
	try {
		const res = await postJSON("/api/method/tactix.api.users.save_user", {
			email: modal.isEdit ? modal.form.email : null,
			doc_data: JSON.stringify(payload),
		})
		const data = await res.json()
		if (res.ok && data.message?.status === "success") {
			modal.show = false
			fetchUsersData()
		} else {
			modal.errorMessage = extractErrorMessage(data)
		}
	} catch (err) {
		modal.errorMessage =
			"An error occurred while communicating with the server."
	} finally {
		modal.saving = false
	}
}

function confirmSingleDelete(email) {
	if (email === currentUser.value) return
	deleteConfirm.error = ""
	deleteConfirm.skippedSelf = false
	deleteConfirm.isBulk = false
	deleteConfirm.targetEmail = email
	deleteConfirm.count = 1
	deleteConfirm.show = true
}

function confirmBulkDelete() {
	deleteConfirm.error = ""
	deleteConfirm.skippedSelf = selectedUsers.value.has(currentUser.value)
	deleteConfirm.isBulk = true
	deleteConfirm.targetEmail = null
	deleteConfirm.count = [...selectedUsers.value].filter((e) => e !== currentUser.value).length
	deleteConfirm.show = true
}

async function executeUserDelete() {
	if (deleteConfirm.loading) return
	deleteConfirm.loading = true
	deleteConfirm.error = ""
	const emails = (deleteConfirm.isBulk ? Array.from(selectedUsers.value) : [deleteConfirm.targetEmail]).filter(
		(e) => e && e !== currentUser.value,
	)
	const failed = []
	for (const email of emails) {
		try {
			const res = await postJSON("/api/method/tactix.api.users.delete_user", { email })
			let data = null
			try {
				data = await res.json()
			} catch {}
			if (res.ok && data?.message?.status !== "error") selectedUsers.value.delete(email)
			else failed.push(`${email}: ${extractErrorMessage(data)}`)
		} catch (err) {
			failed.push(`${email}: network error`)
		}
	}
	selectedUsers.value = new Set(selectedUsers.value)
	deleteConfirm.loading = false
	fetchUsersData()
	if (failed.length) {
		deleteConfirm.error = `Couldn't delete ${failed.length} of ${emails.length}:` + String.fromCharCode(10) + failed.join(String.fromCharCode(10))
	} else {
		deleteConfirm.show = false
	}
}

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

// Initial fetch
fetchUsersData()
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