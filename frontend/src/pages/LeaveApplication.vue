<template>
  <div class="p-1 space-y-4 flex flex-col h-full overflow-hidden min-h-0">
    
    <!-- Header -->

    <!-- KPI -->

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 flex-shrink-0">
      <Card 
        v-for="stat in kpiStats" 
        :key="stat.label" 
        :class="[
          '!shadow-sm bg-white cursor-pointer transition-all duration-200 border active:scale-[0.98]',
          'border-slate-100 hover:border-slate-200'
        ]"
        @click="filterByStatus(stat.label)"
      >
      <div class="flex items-center justify-between">
        <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">{{ stat.label }}</span>
        <component :is="stat.icon" class="w-4 h-4" :class="stat.color" />
      </div>
      <div class="text-2xl font-black mt-2 text-slate-900 flex items-center h-8">
        <template v-if="leavesResource.loading">
          <div class="w-4 h-4 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
        </template>
        <span v-else>{{ stat.value }}</span>
      </div>
      </Card>
    </div>

    <!-- Filters -->
    <div class="filter-row bg-white p-3 rounded-xl border border-slate-100 flex gap-3 flex-shrink-0">
      <input 
        v-model="searchQuery"
        placeholder="Search..."
        class="flex-1 px-3 py-2 text-sm bg-slate-50 rounded-md outline-none focus:ring-1 focus:ring-blue-500"
      />

      <Select
        v-model="selectedStatus"
        :options="['All', 'Pending', 'Approved', 'Rejected']"
        placeholder="Status"
        class="!w-40"
      />
       <Button 
            variant="outline" 
            @click="leavesResource.reload()"
            class="!text-slate-600 !rounded-lg px-3 !h-9 border border-slate-200 hover:bg-slate-50 transition-all"
        >
            <template #prefix><IconRefresh class="w-4 h-4 text-slate-500" /></template>
       </Button>

      <Dropdown v-if="selectedLeaves.size > 0" :options="actionsOptions">
        <Button
          variant="solid"
          class="!bg-slate-800 !text-white !text-xs !px-5 !h-9 !shadow-md hover:!bg-slate-900 transition-all"
        >
          Actions
          <template #suffix><FeatherIcon name="chevron-down" class="w-4 h-4 shrink-0" /></template>
        </Button>
      </Dropdown>

      <Button
        v-else
        variant="solid"
        class="new-btn !text-xs !px-5 !h-9 !shadow-md transition-all"
        @click="openNewLeave"
      >
        <template #prefix><IconPlus class="w-4 h-4" /></template>
        New Leave
      </Button>
    </div>
    

    <!-- Table -->
    <div class="bg-white rounded-xl border border-slate-100 flex-1 flex flex-col overflow-hidden min-h-0">
  <ListView
    class="flex-1 flex flex-col min-h-0"
    :columns="columns"
    :rows="filteredLeaves"
    :loading="leavesResource.loading"
    row-key="name"
    v-model:selections="selectedLeaves"
    :options="{
      resizeColumn: true,
      selectable: true,
      onRowClick: (row) => openEditLeave(row)
    }"
  >
    <!-- Header -->
    <ListHeader class="shrink-0 bg-slate-50 border-b border-slate-100">
      <ListHeaderItem v-for="col in columns" :key="col.key" :item="col" />
    </ListHeader>

    <!-- Rows -->
    <div class="flex-1 overflow-y-auto min-h-0">
      <ListRows>
      <ListRow
        v-for="row in filteredLeaves"
        :key="row.name"
        v-slot="{ column, item }"
        :row="row"
        class="hover:bg-slate-50 cursor-pointer transition"
      >
        <ListRowItem :item="item">

          <!-- ID -->
          <template v-if="column.key === 'name'">
            <span class="font-semibold text-blue-600">{{ row.name }}</span>
          </template>

          <!-- User -->
          <template v-if="column.key === 'user'">
            <div class="flex items-center gap-2">
              <Avatar size="xs" :image="getUserAvatarImage(row.user)" :label="row.user" />
              <span class="text-sm">{{ row.user }}</span>
            </div>
          </template>

          <template v-if="column.key === 'remarks'">
            <div class="max-w-[420px] truncate text-sm text-slate-600" :title="stripHtml(row.remarks)">
              {{ stripHtml(row.remarks) || '—' }}
            </div>
          </template>

          <!-- Status -->
          <template v-if="column.key === 'status'">
            <Badge
              :theme="getStatusVariant(row.status)"
              variant="subtle" 
              class="px-2 py-0.5 text-xs rounded-md"
              :label="item"
            >
            </Badge>
          </template>

          <!-- Dates -->
          <template v-if="column.key === 'from_date'">
            <span class="text-sm text-slate-600">{{ row.from_date ? formatDateTime(row.from_date) : '' }}</span>
          </template>

          <template v-if="column.key === 'to_date'">
            <span class="text-sm text-slate-600">{{ row.to_date ? formatDateTime(row.to_date) : '' }}</span>
          </template>

        </ListRowItem>
      </ListRow>
      </ListRows>
    </div>

  </ListView>
</div>

    <Dialog
      v-model="showBulkDeleteDialog"
      :options="{
        title: 'Delete Selected Leaves',
        size: 'sm',
        actions: [
          { label: 'Delete', variant: 'solid', theme: 'red', loading: bulkDeleting, onClick: executeBulkDelete },
          { label: 'Cancel', variant: 'ghost', onClick: () => (showBulkDeleteDialog = false) }
        ]
      }"
    >
      <template #body-content>
        <p class="text-sm text-slate-600 leading-relaxed py-2">
          Are you sure you want to permanently delete the <span class="font-bold text-slate-900">{{ selectedLeaves.size }}</span> selected leave application(s)? This action cannot be undone.
        </p>
      </template>
    </Dialog>

    <Dialog
      v-model="showErrorDialog"
      :options="{
        title: 'Cannot Delete',
        size: 'sm',
        actions: [
          { label: 'Close', variant: 'solid', onClick: () => (showErrorDialog = false) }
        ]
      }"
    >
      <template #body-content>
        <p class="text-sm text-red-600 leading-relaxed py-2">
          {{ errorMessage }}
        </p>
      </template>
    </Dialog>

    <!-- Dialog -->
    <Dialog v-model="showLeaveDialog" :options="leaveDialogOptions">
      
      <template #body-content>
        <div class="space-y-4">

          <div class="grid grid-cols-2 gap-3">
            <FormControl 
              label="User"
              type="select" 
              :options="[...(userResource?.data || [])]"
              v-model="leaveForm.user" 
            />

            <FormControl 
              label="Status"
              type="select"
              :options="['Pending','Approved','Rejected']"
              v-model="leaveForm.status"
              :disabled="!isAdmin"
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <FormControl label="From" type="date" v-model="leaveForm.from_date" />
            <FormControl label="To" type="date" v-model="leaveForm.to_date" />
          </div>

          <FormControl 
            label="Posting Date"
            type="date"
            v-model="leaveForm.posting_date"
            disabled
          />

          <!-- Editor -->
          <div>
            <label class="text-xs text-slate-500 mb-1 block">Remarks *</label>
            <div class="border rounded-md overflow-hidden bg-white">
              <TextEditor
                editor-class="p-3 text-sm min-h-[120px]"
                :content="leaveForm.remarks"
                @change="val => leaveForm.remarks = val"
              />
            </div>
          </div>

        </div>
      </template>

      <template #actions>
        <div class="flex gap-2 w-full">
          <Button
            variant="solid"
            class="flex-1 save-btn !h-9"
            :loading="leaveSaving"
            @click="handleSaveLeave"
          >
            {{ isEditLeave ? 'Update' : 'Create' }}
          </Button>

          <Button
            variant="ghost"
            class="flex-1"
            @click="showLeaveDialog = false"
          >
            Cancel
          </Button>
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
	Dropdown,
	FeatherIcon,
	FormControl,
	ListHeader,
	ListHeaderItem,
	ListRow,
	ListRowItem,
	ListView,
	Select,
	TextEditor,
	createListResource,
	createResource,
} from "frappe-ui"
import { computed, reactive, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { session } from "../data/session"

import IconCheckCircle from "~icons/lucide/check-circle"
import IconClock from "~icons/lucide/clock"
import IconFileText from "~icons/lucide/file-text"
// Icons
import IconPlus from "~icons/lucide/plus"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconXCircle from "~icons/lucide/x-circle"

/* STATE */
const isAdmin = session.isAdmin
const searchQuery = ref("")
const selectedStatus = ref("")
const showLeaveDialog = ref(false)
const isEditLeave = ref(false)
const leaveSaving = ref(false)
const selectedLeaves = ref(new Set())
const showBulkDeleteDialog = ref(false)
const showErrorDialog = ref(false)
const errorMessage = ref("")
const bulkDeleting = ref(false)

const formatDateTime = (dateStr) => {
	if (!dateStr) return "—"
	return dayjs(dateStr).format("MMM D, YYYY")
}

/* FORM */
const emptyLeave = () => ({
	name: "",
	user: session.user,
	from_date: dayjs().format("YYYY-MM-DD"),
	to_date: dayjs().add(1, "day").format("YYYY-MM-DD"),
	posting_date: dayjs().format("YYYY-MM-DD"),
	status: "Pending",
	remarks: "",
})

const leaveForm = reactive(emptyLeave())

/* RESOURCE */
const leavesResource = createResource({
	url: "frappe.client.get_list",
	params: {
		doctype: "Tactix Leave Application",
		fields: ["*"],
		order_by: "modified desc",
	},
	auto: true,
	initialData: [],
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
		users.map((u) => ({
			label: u.full_name || u.name,
			value: u.name,
			image: u.user_image || "",
		})),
	pageLength: 10000,
})

function getUserAvatarImage(userName) {
	if (!userName) return ""
	const match = userResource.data?.find((user) => user.value === userName)
	return match?.image || ""
}

function filterByStatus(label) {
	if (label === "Total") {
		selectedStatus.value = "All"
	} else {
		selectedStatus.value = label
	}
}

function isCardActive(label) {
	if (label === "Total") {
		return !selectedStatus.value || selectedStatus.value === "All"
	}
	return selectedStatus.value === label
}

/* FILTER */
const filteredLeaves = computed(() => {
	let list = leavesResource.data || []

	if (searchQuery.value) {
		const q = searchQuery.value.toLowerCase()
		list = list.filter(
			(l) =>
				l.user?.toLowerCase().includes(q) ||
				l.remarks?.toLowerCase().includes(q),
		)
	}

	if (selectedStatus.value) {
		if (selectedStatus.value === "All") {
			return list
		}
		list = list.filter((l) => l.status === selectedStatus.value)
	}

	return list
})

/* KPI */
const kpiStats = computed(() => {
	const data = filteredLeaves.value
	return [
		{
			label: "Total",
			value: data.length,
			icon: IconFileText,
			color: "text-blue-500",
		},
		{
			label: "Pending",
			value: data.filter((l) => l.status === "Pending").length,
			icon: IconClock,
			color: "text-amber-500",
		},
		{
			label: "Approved",
			value: data.filter((l) => l.status === "Approved").length,
			icon: IconCheckCircle,
			color: "text-green-500",
		},
		{
			label: "Rejected",
			value: data.filter((l) => l.status === "Rejected").length,
			icon: IconXCircle,
			color: "text-red-500",
		},
	]
})

const actionsOptions = computed(() => [
	{
		label: "Delete",
		onClick: () => {
			showBulkDeleteDialog.value = true
		},
	},
])

/* DIALOG */
const leaveDialogOptions = computed(() => ({
	title: isEditLeave.value ? "Edit Leave" : "New Leave",
	size: "lg",
}))

const openNewLeave = () => {
	isEditLeave.value = false
	Object.assign(leaveForm, emptyLeave())
	showLeaveDialog.value = true
}

const openEditLeave = (row) => {
	isEditLeave.value = true
	Object.assign(leaveForm, { ...row })
	showLeaveDialog.value = true
}

/* SAVE */
async function handleSaveLeave() {
	if (!leaveForm.remarks) return

	leaveSaving.value = true

	try {
		if (isEditLeave.value) {
			await createResource({
				url: "frappe.client.set_value",
				params: {
					doctype: "Tactix Leave Application",
					name: leaveForm.name,
					fieldname: {
						from_date: leaveForm.from_date,
						to_date: leaveForm.to_date,
						status: leaveForm.status,
						remarks: leaveForm.remarks,
					},
				},
			}).submit()
		} else {
			await createResource({
				url: "frappe.client.insert",
				params: {
					doc: {
						doctype: "Tactix Leave Application",
						...leaveForm,
					},
				},
			}).submit()
		}

		leavesResource.reload()
		showLeaveDialog.value = false
	} finally {
		leaveSaving.value = false
	}
}

async function executeBulkDelete() {
	if (selectedLeaves.value.size === 0) return
	const names = Array.from(selectedLeaves.value)

	bulkDeleting.value = true
	let failed = false
	const succeeded = []

	for (const name of names) {
		try {
			await createResource({
				url: "frappe.client.delete",
				params: {
					doctype: "Tactix Leave Application",
					name,
				},
			}).submit()
			succeeded.push(name)
		} catch (e) {
			failed = true
			console.error(`Failed to delete leave application ${name}`, e)
		}
	}

	for (const name of succeeded) {
		selectedLeaves.value.delete(name)
	}

	leavesResource.reload()

	if (failed) {
		errorMessage.value =
			"This leave application cannot be deleted because it is linked with other documents."
		showErrorDialog.value = true
	} else {
		showBulkDeleteDialog.value = false
	}

	bulkDeleting.value = false
}

function stripHtml(html) {
	if (!html) return ""
	const div = document.createElement("div")
	div.innerHTML = html
	return div.textContent || div.innerText || ""
}

/* TABLE */
const columns = [
	{ label: "ID", key: "name", width: "120px" },
	{ label: "User", key: "user" },
	{ label: "Remarks", key: "remarks" },
	{ label: "From", key: "from_date", width: "120px" },
	{ label: "To", key: "to_date", width: "120px" },
	{ label: "Status", key: "status", width: "120px" },
]

/* UI HELPERS */
function getStatusVariant(status) {
	return {
		Pending: "orange",
		Approved: "green",
		Rejected: "red",
	}[status]
}

const route = useRoute()
const router = useRouter()

async function openLeaveByName(leaveName) {
	if (!leaveName) return
	try {
		const res = await createResource({
			url: "frappe.client.get",
			params: {
				doctype: "Leave Application",
				name: leaveName,
			},
		}).submit()
		if (res) {
			openEditLeave(res)
		}
	} catch (e) {
		console.error("Failed to load leave for notification", e)
	}
}

watch(
	() => route.query.name,
	(newName) => {
		if (newName) {
			openLeaveByName(newName)
		}
	},
	{ immediate: true },
)

watch(showLeaveDialog, (val) => {
	if (!val) {
		if (route.query.name) {
			router.replace({ query: { ...route.query, name: undefined } })
		}
	}
})
</script>

<style scoped>
.filter-row :deep(.new-btn),
.filter-row :deep(.new-btn:hover) {
  background-color: #061d43 !important;
  color: #ffffff !important;
  border-color: #061d43 !important;
  box-shadow: 0 4px 6px -1px #061d4333 !important;
}

.filter-row :deep(.new-btn:hover) {
  background-color: #0a2d63 !important;
}

:deep(.save-btn) {
  background-color: #061d43 !important;
  color: #ffffff !important;
  border-color: #061d43 !important;
}

:deep(.save-btn:hover) {
  background-color: #0a2d63 !important;
}
</style>