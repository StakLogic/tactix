<template>
  <div class="space-y-4 p-1 flex flex-col h-full overflow-hidden min-h-0">
	<div class="grid grid-cols-2 lg:grid-cols-6 gap-3 md:gap-4 flex-shrink-0">
	  <Card 
		v-for="stat in kpiStats" 
		:key="stat.label" 
		:class="[
			'!shadow-sm bg-white cursor-pointer transition-all duration-200 border active:scale-[0.98]',
			'border-slate-100 hover:border-slate-200'
		]"
		@click="filterByStat(stat.label)"
	  >
		<div class="flex items-center justify-between">
		  <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">{{ stat.label }}</span>
		  <component :is="stat.icon" class="w-4 h-4" :class="stat.color" />
		</div>
		<div class="text-2xl font-black mt-2 text-slate-900 flex items-center h-8">
			<template v-if="tasksResource.loading">
				<div class="w-4 h-4 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
			</template>
			<span v-else>{{ stat.value }}</span>
		</div>
	  </Card>
	</div>

	<div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm flex flex-col gap-3 flex-shrink-0">
	  <!-- Top Row: Search & Actions -->
	  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 w-full pb-2 border-b border-slate-100">
		<div class="relative w-full sm:w-80">
		  <IconSearch class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
		  <input 
			v-model="searchQuery"
			type="text" 
			placeholder="Search subject, description..." 
			class="w-full pl-9 pr-3 py-1.5 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
		  />
		</div>

		<div class="flex items-center gap-2 ml-auto sm:ml-0">
		  <!-- View Mode Toggle -->
		  <div class="flex bg-slate-100 p-1 rounded-lg border border-slate-200/50">
			<button @click="viewMode = 'list'" :class="viewBtnClass('list')">
			  <IconList class="w-4 h-4" />
			</button>
			<button @click="viewMode = 'board'" :class="viewBtnClass('board')">
			  <IconLayoutGrid class="w-4 h-4" />
			</button>
		  </div>

		  <!-- Refresh Button -->
		  <Button
			variant="outline"
			class="!text-slate-600 !px-3 !h-9 border border-slate-200 hover:bg-slate-50 transition-all"
			@click="tasksResource.reload()"
		  >
			<template #prefix><IconRefresh class="w-4 h-4 text-slate-500" /></template>
		  </Button>

		  <!-- Actions Dropdown / New Task Button -->
		  <Dropdown
			v-slot="{ open }"
			v-if="isAdmin && selectedTasks.size > 0"
			:options="actionsOptions"
		  >
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
			class="!text-xs !px-5 !h-9 !shadow-md transition-all"
			style="background-color: var(--primary-color); box-shadow: 0 4px 6px -1px var(--primary-color-shadow);"
			@click="openCreateDialog"
		>
			<template #prefix><IconPlus class="w-4 h-4" /></template>
			New Task
		</Button>

		  
		</div>
	  </div>

	  <!-- Bottom Row: Filters -->
	  <div class="filter-row flex flex-nowrap overflow-x-auto pb-1.5 gap-2 w-full custom-scrollbar sm:flex-wrap sm:overflow-visible sm:pb-0 sm:items-center sm:gap-2">
		<div class="w-32 shrink-0">
			<Autocomplete
			  ref="projectAutocomplete"
			  :options="projectResource?.data || []"
			  :modelValue="selectedFilters.project"
			  @update:modelValue="val => selectedFilters.project = val?.value || val || ''"
			  :max-options="100"
			>
			  <template #target>
				<button
				  type="button"
				  @click="() => projectAutocomplete?.togglePopover()"
				  :class="[
					'inline-flex items-center justify-between gap-2 outline-none text-xs font-semibold transition-colors w-full cursor-pointer h-9 px-3 rounded-lg border',
					selectedFilters.project !== ''
					  ? 'border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/10 font-black shadow-sm ring-1 ring-[var(--primary-color)]/10 focus:ring-2 focus:ring-[var(--primary-color)]/20 dark:border-indigo-400 dark:text-indigo-300 dark:bg-[var(--primary-color)]/20'
					  : 'border-slate-200 bg-slate-50 text-slate-600 dark:text-slate-300 border-slate-200 dark:bg-slate-900 dark:border-slate-700 hover:bg-slate-100 hover:border-slate-300'
				  ]"
				>
				  <span class="truncate">{{ getProjectLabel(selectedFilters.project) }}</span>
				  <FeatherIcon name="chevron-down" class="h-3.5 w-3.5 text-slate-400 shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<div class="w-32 shrink-0">
			<Autocomplete
			  ref="departmentAutocomplete"
			  :options="departmentResource?.data || []"
			  :modelValue="selectedFilters.department"
			  @update:modelValue="val => selectedFilters.department = val?.value || val || ''"
			  :max-options="100"
			>
			  <template #target>
				<button
				  type="button"
				  @click="() => departmentAutocomplete?.togglePopover()"
				  :class="[
					'inline-flex items-center justify-between gap-2 outline-none text-xs font-semibold transition-colors w-full cursor-pointer h-9 px-3 rounded-lg border',
					selectedFilters.department !== ''
					  ? 'border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/10 font-black shadow-sm ring-1 ring-[var(--primary-color)]/10 focus:ring-2 focus:ring-[var(--primary-color)]/20 dark:border-indigo-400 dark:text-indigo-300 dark:bg-[var(--primary-color)]/20'
					  : 'border-slate-200 bg-slate-50 text-slate-600 dark:text-slate-300 border-slate-200 dark:bg-slate-900 dark:border-slate-700 hover:bg-slate-100 hover:border-slate-300'
				  ]"
				>
				  <span class="truncate">{{ getDepartmentLabel(selectedFilters.department) }}</span>
				  <FeatherIcon name="chevron-down" class="h-3.5 w-3.5 text-slate-400 shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<select 
		  v-model="selectedFilters.status"
		  :class="[
			'px-3 h-9 rounded-lg border text-xs font-semibold focus:outline-none cursor-pointer min-w-[120px] shrink-0 transition-all duration-200',
			selectedFilters.status !== ''
			  ? 'border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/10 font-black shadow-sm ring-1 ring-[var(--primary-color)]/10 focus:ring-2 focus:ring-[var(--primary-color)]/20 dark:border-indigo-400 dark:text-indigo-300'
			  : 'border-slate-200 bg-slate-50 text-slate-600 dark:text-slate-300 dark:bg-slate-900 dark:border-slate-700 focus:ring-2 focus:ring-blue-500/20'
		  ]"
		>
		  <option value="">Status</option>
		  <option v-for="opt in filterStatusOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
		</select>

		<select 
		  v-model="selectedFilters.priority"
		  :class="[
			'px-3 h-9 rounded-lg border text-xs font-semibold focus:outline-none cursor-pointer min-w-[120px] shrink-0 transition-all duration-200',
			selectedFilters.priority !== ''
			  ? 'border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/10 font-black shadow-sm ring-1 ring-[var(--primary-color)]/10 focus:ring-2 focus:ring-[var(--primary-color)]/20 dark:border-indigo-400 dark:text-indigo-300'
			  : 'border-slate-200 bg-slate-50 text-slate-600 dark:text-slate-300 dark:bg-slate-900 dark:border-slate-700 focus:ring-2 focus:ring-blue-500/20'
		  ]"
		>
		  <option value="">Priority</option>
		  <option v-for="opt in priorityOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
		</select>

		<div class="w-32 shrink-0">
			<Autocomplete
			  ref="assignedByAutocomplete"
			  :options="userResource?.data || []"
			  :modelValue="selectedFilters.assigned_by"
			  @update:modelValue="val => selectedFilters.assigned_by = val?.value || val || ''"
			  :max-options="100"
			>
			  <template #target>
				<button
				  type="button"
				  @click="() => assignedByAutocomplete?.togglePopover()"
				  :class="[
					'inline-flex items-center justify-between gap-2 outline-none text-xs font-semibold transition-colors w-full cursor-pointer h-9 px-3 rounded-lg border',
					selectedFilters.assigned_by !== ''
					  ? 'border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/10 font-black shadow-sm ring-1 ring-[var(--primary-color)]/10 focus:ring-2 focus:ring-[var(--primary-color)]/20 dark:border-indigo-400 dark:text-indigo-300 dark:bg-[var(--primary-color)]/20'
					  : 'border-slate-200 bg-slate-50 text-slate-600 dark:text-slate-300 border-slate-200 dark:bg-slate-900 dark:border-slate-700 hover:bg-slate-100 hover:border-slate-300'
				  ]"
				>
				  <span class="truncate">{{ getUserLabel(selectedFilters.assigned_by, 'Assigned By') }}</span>
				  <FeatherIcon name="chevron-down" class="h-3.5 w-3.5 text-slate-400 shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<div class="w-32 shrink-0">
			<Autocomplete
			  ref="assignedToAutocomplete"
			  :options="userResource?.data || []"
			  :modelValue="selectedFilters.assigned_to"
			  @update:modelValue="val => selectedFilters.assigned_to = val?.value || val || ''"
			  :max-options="100"
			>
			  <template #target>
				<button
				  type="button"
				  @click="() => assignedToAutocomplete?.togglePopover()"
				  :class="[
					'inline-flex items-center justify-between gap-2 outline-none text-xs font-semibold transition-colors w-full cursor-pointer h-9 px-3 rounded-lg border',
					selectedFilters.assigned_to !== ''
					  ? 'border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/10 font-black shadow-sm ring-1 ring-[var(--primary-color)]/10 focus:ring-2 focus:ring-[var(--primary-color)]/20 dark:border-indigo-400 dark:text-indigo-300 dark:bg-[var(--primary-color)]/20'
					  : 'border-slate-200 bg-slate-50 text-slate-600 dark:text-slate-300 border-slate-200 dark:bg-slate-900 dark:border-slate-700 hover:bg-slate-100 hover:border-slate-300'
				  ]"
				>
				  <span class="truncate">{{ getUserLabel(selectedFilters.assigned_to, 'Assigned To') }}</span>
				  <FeatherIcon name="chevron-down" class="h-3.5 w-3.5 text-slate-400 shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<select 
		  v-model="selectedFilters.deadline"
		  :class="[
			'px-3 h-9 rounded-lg border text-xs font-semibold focus:outline-none cursor-pointer min-w-[120px] shrink-0 transition-all duration-200',
			selectedFilters.deadline !== ''
			  ? 'border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/10 font-black shadow-sm ring-1 ring-[var(--primary-color)]/10 focus:ring-2 focus:ring-[var(--primary-color)]/20 dark:border-indigo-400 dark:text-indigo-300'
			  : 'border-slate-200 bg-slate-50 text-slate-600 dark:text-slate-300 dark:bg-slate-900 dark:border-slate-700 focus:ring-2 focus:ring-blue-500/20'
		  ]"
		>
		  <option v-for="opt in deadlineOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
		</select>

		<Button 
		  v-if="hasActiveFilters"
		  variant="ghost" 
		  class="!text-red-500 hover:!bg-red-50 !px-2.5 !h-9 shrink-0"
		  @click="clearFilters"
		>
		  <template #prefix><IconX class="w-3.5 h-3.5" /></template>
		  Clear
		</Button>
	  </div>
	</div>

	<div v-if="tasksResource.loading && !filteredTasksData" class="flex justify-center p-12">
	  <LoadingIndicator />
	</div>

	<div v-else class="flex-1 overflow-y-auto md:overflow-hidden flex flex-col min-h-0">
	  <div v-if="viewMode === 'list'" class="bg-white rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col min-h-[420px] md:min-h-0 md:flex-1 md:overflow-hidden">
		  <ListView
			class="h-full flex flex-col min-h-0"
			:columns="columns"
			:rows="filteredTasksData || []" 
			:options="{ selectable: isAdmin, showTooltip: true, resizeColumn: true, onRowClick: (row) => openEditDialog(row), }"
			row-key="name"
			v-model:selections="selectedTasks"
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
			  <ListRow v-for="row in (filteredTasksData || [])" :key="row.name" v-slot="{ column, item }" :row="row">
				<ListRowItem :item="item">
				  <template v-if="column.key === 'subject'" #prefix>
					<div class="flex items-center -space-x-2 mr-4 isolate">
						<Avatar 
							v-for="(assignment, index) in (row.assigned_to || []).slice(0, 3)" 
							:key="index"
							:image="getUserAvatarImage(assignment)"
							:label="assignment" 
							size="lg" 
							class="border-2 border-white ring-1 ring-gray-100 rounded-full"
							v-tooltip="assignment"
						/>
						
						<div 
							v-if="row.assigned_to?.length > 3" 
							class="flex items-center justify-center h-7 w-7 rounded-full bg-gray-100 border-2 border-white text-[10px] font-medium text-gray-600 ring-1 ring-gray-100 z-10"
						>
							+{{ row.assigned_to.length - 3 }}
						</div>
					</div>					
				  </template>
				  <template v-if="column.key === 'priority'">
					<Badge :theme="getPriorityTheme(item)" variant="subtle" :label="item" />
				  </template>
				  <template v-if="column.key === 'status'">
					<div class="flex items-center">
						<div class="h-2 w-2 rounded-full mr-2 shrink-0" :class="getStatusColor(item)" />
						
						<span class="text-sm truncate">
						{{ item }}
						<span v-if="row.is_overdue" class="text-red-500 font-medium ml-1">
							- (Overdue)
						</span>
						</span>
					</div>
				  </template>
				  <template v-if="column.key === 'description_for_list'">
					<div 
						class="max-w-[600px] truncate text-slate-500 text-sm" 
						v-tooltip="item"
					>
						{{ item || '—' }}
					</div>
				  </template>
				  <template v-if="column.key === 'assigned_datetime'">
						<div class="flex items-center gap-2 text-slate-500">
							<IconClock class="w-3.5 h-3.5" v-if="row.assigned_datetime"/>
							<span class="text-xs font-medium">
								{{ row.assigned_datetime ? formatDateTime(row.assigned_datetime) : '' }}
							</span>
						</div>
				  </template>
				  <template v-if="column.key === 'exp_end_date'">
						<div class="flex items-center gap-2 text-slate-500">
							<IconClock class="w-3.5 h-3.5" v-if="row.exp_end_date"/>
							<span class="text-xs font-medium">
								{{ row.exp_end_date ? formatDate(row.exp_end_date) : '' }}
							</span>
						</div>
				  </template>
				  <template v-if="column.key === 'has_unseen_comments'">
					<div class="flex justify-end pr-2">
						<div 
							v-if="row.has_unseen_comments && row.has_unseen_comments > 0" 
							class="flex items-center gap-1 text-red-600 bg-red-50 px-2 py-0.5 rounded-md border border-red-100 shadow-sm"
							title="Unseen Comments"
						>
							<IconMessageSquare class="w-3.5 h-3.5" />
							<span class="text-[10px] font-bold leading-none">
								{{ row.has_unseen_comments }}
							</span>
						</div>
					</div>
					</template>
				</ListRowItem>
			  </ListRow>
			</ListRows>
			</div>
		  </ListView>
		<!-- Pagination controls -->
		<div class="flex items-center justify-between border-t border-slate-100 bg-white px-4 py-3 sm:px-6">
		  <div class="flex flex-1 justify-between sm:hidden">
			<Button 
			  :disabled="currentPage === 1" 
			  @click="currentPage--"
			  variant="ghost"
			>
			  Previous
			</Button>
			<Button 
			  :disabled="currentPage >= totalPages" 
			  @click="currentPage++"
			  variant="ghost"
			>
			  Next
			</Button>
		  </div>
		  <div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
			<div>
			  <p class="text-xs text-slate-500">
				Showing
				<span class="font-bold text-slate-800">{{ totalCount > 0 ? (currentPage - 1) * pageLength + 1 : 0 }}</span>
				to
				<span class="font-bold text-slate-800">{{ Math.min(currentPage * pageLength, totalCount) }}</span>
				of
				<span class="font-bold text-slate-800">{{ totalCount }}</span>
				results
			  </p>
			</div>
			<div>
			  <nav class="isolate inline-flex -space-x-px rounded-lg bg-slate-50 p-1 border border-slate-200/50" aria-label="Pagination">
				<button 
				  @click="currentPage = Math.max(1, currentPage - 1)"
				  :disabled="currentPage === 1"
				  class="relative inline-flex items-center rounded-md p-1 text-slate-400 hover:bg-white hover:text-slate-700 disabled:opacity-50 disabled:hover:bg-transparent transition-all mr-1"
				>
				  <span class="sr-only">Previous</span>
				  <IconChevronLeft class="w-3.5 h-3.5" />
				</button>
				
				<template v-for="(page, idx) in paginationPages" :key="idx">
				  <button 
					v-if="page !== '...'"
					@click="currentPage = page"
					:class="[
					  'relative inline-flex items-center justify-center rounded-md text-[11px] font-bold transition-all px-2.5 py-1 min-w-[28px]',
					  currentPage === page 
						? 'bg-blue-600 text-white shadow-sm' 
						: 'text-slate-600 hover:bg-white hover:text-slate-900'
					]"
				  >
					{{ page }}
				  </button>
				  <span 
					v-else 
					class="relative inline-flex items-center justify-center text-[11px] font-semibold text-slate-400 px-1.5 py-1"
				  >
					...
				  </span>
				</template>

				<button 
				  @click="currentPage = Math.min(totalPages, currentPage + 1)"
				  :disabled="currentPage === totalPages"
				  class="relative inline-flex items-center rounded-md p-1 text-slate-400 hover:bg-white hover:text-slate-700 disabled:opacity-50 disabled:hover:bg-transparent transition-all ml-1"
				>
				  <span class="sr-only">Next</span>
				  <IconChevronRight class="w-3.5 h-3.5" />
				</button>
			  </nav>
			</div>
		  </div>
		</div>
	  </div>

	  <div v-if="viewMode === 'board'" class="flex-1 flex gap-6 overflow-x-auto pb-4 custom-scrollbar px-1 min-h-0">
		<div 
			v-for="status in statusOptions" 
			:key="status.value" 
			class="min-w-[300px] flex-shrink-0 flex flex-col h-full min-h-0 rounded-2xl p-2 transition-all"
			:class="[hoveredColumn === status.value ? 'bg-blue-50/40 ring-2 ring-dashed ring-blue-200 shadow-inner' : '']"
			@dragover.prevent
			@dragenter.prevent="onDragEnter(status.value)"
			@dragleave="onDragLeave"
			@drop="onDrop($event, status.value)"
		>
		  <div class="flex items-center justify-between mb-4 px-1 flex-shrink-0">
			<h3 class="text-sm font-bold text-slate-700">{{ status.label }}</h3>
			<Badge variant="subtle" theme="gray" size="sm">{{ filteredTasks(status.value).length }}</Badge>
		  </div>
		  <div class="flex-1 space-y-3 overflow-y-auto pr-1 custom-scrollbar min-h-0" @scroll="handleColumnScroll($event, status.value)">
			<Card
			  v-for="task in filteredTasks(status.value)"
			  :key="task.name"
			  @click="openEditDialog(task)"
			  draggable="true"
			  @dragstart="onDragStart($event, task)"
			  @dragend="onDragEnd"
			  class="!p-4 border border-slate-200 hover:border-blue-400 cursor-pointer transition-colors shadow-sm bg-white mb-3 select-none active:opacity-40"
			  :class="[draggedTask?.name === task.name ? 'opacity-40 border-dashed border-blue-300' : '']"
			>
			  <div class="space-y-3">
				<div class="font-bold text-sm text-slate-800 leading-snug">{{ task.subject }}</div>
				<div class="flex items-center">
				  <Avatar 
						v-for="(assignment, index) in (task.assigned_to || []).slice(0, 3)" 
						:key="index"
						:image="getUserAvatarImage(assignment)"
						:label="assignment" 
						size="lg" 
						class="border-2 border-white ring-1 ring-gray-100 rounded-full"
						v-tooltip="assignment"
					/>
					
					<div 
						v-if="task.assigned_to?.length > 3" 
						class="flex items-center justify-center h-7 w-7 rounded-full bg-gray-100 border-2 border-white text-[10px] font-medium text-gray-600 ring-1 ring-gray-100 z-10"
					>
						+{{ task.assigned_to.length - 3 }}
					</div>
				</div>
				<div class="flex justify-between items-center pt-1">
				  <Badge :theme="getPriorityTheme(task.priority)" variant="subtle">{{ task.priority }}</Badge>
				  <span class="text-[10px] font-bold text-slate-400 flex items-center gap-1">
					<IconClock class="w-3 h-3" /> {{ task.exp_end_date || 'No date' }}
				  </span>
				</div>
			  </div>
			</Card>
			
			<div v-if="columnLoading[status.value]" class="py-3 flex justify-center">
			  <div class="w-5 h-5 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
			</div>

			<div v-if="filteredTasks(status.value).length === 0 && !columnLoading[status.value]" class="h-24 border-2 border-dashed border-slate-200 rounded-xl flex items-center justify-center text-xs text-slate-400">
			  No tasks
			</div>
		  </div>
		</div>
	  </div>
	</div>

	<Dialog v-model="showBulkDeleteDialog" 
		:disable-outside-click-to-close="true"
		:options="{ 
		title: 'Delete Selected Tasks', 
		size: 'sm',
		actions: [
			{ label: 'Delete', variant: 'solid', theme: 'red', loading: saving, onClick: executeBulkDelete },
			{ label: 'Cancel', variant: 'ghost', onClick: () => (showBulkDeleteDialog = false) }
		] 
		}">
	  <template #body-content>
		<p class="text-sm text-slate-600 leading-relaxed py-2">
		  Are you sure you want to permanently delete the <span class="font-bold text-slate-900">{{ selectedTasks.size }}</span> selected task(s)? This action cannot be undone.
		</p>
	  </template>
	</Dialog>

	<Dialog v-model="showErrorDialog" 
		:disable-outside-click-to-close="true"
		:options="{ 
		title: errorDialogTitle, 
		size: 'sm',
		actions: [
			{ label: 'Close', variant: 'solid', onClick: () => (showErrorDialog = false) }
		] 
		}">
	  <template #body-content>
		<p class="text-sm text-red-600 leading-relaxed py-2">
		  {{ errorMessage }}
		</p>
	  </template>
	</Dialog>

	<Dialog v-model="showCreateDialog" 
		:disable-outside-click-to-close="true"
		:options="{ 
		title: isEditMode ? 'Edit Task' : 'Create Task', 
		size: '4xl',
		actions: [
			{ label: isEditMode ? 'Save Changes' : 'Create Task', variant: 'solid', loading: saving, onClick: handleSaveTask },
			{ label: 'Cancel', variant: 'ghost', onClick: () => (showCreateDialog = false) }
		] 
		}">
	  <template #body-content>
		<div v-if="showCreateDialog" class="space-y-6 py-2">
		  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
			<div class="space-y-4">
			  <FormControl type="text" label="Subject *" v-model="newTask.subject" />
			  <FormControl type="select" label="Project" v-model="newTask.project" :options="projectResource.data" />
			  <FormControl type="select" label="Department" v-model="newTask.department" :options="departmentResource.data" />
			  <FormControl type="select" label="Status" v-model="newTask.status" :options="statusOptions.map(s => s.value)" />
			</div>
			<div class="space-y-4">
			  <FormControl type="select" label="Priority" v-model="newTask.priority" :options="priorityOptions" />
			  <FormControl type="select" label="Security Impact" v-model="newTask.security_impact" :options="securityImpactOptions" />
			  <FormControl type="date" label="Start Date" v-model="newTask.assigned_date" />
			  <FormControl type="date" label="Deadline" v-model="newTask.exp_end_date" />
			</div>
			<div class="space-y-4">
			  <FormControl type="select" label="Assigned By" v-model="newTask.assigned_by" :options="userResource.data" :disabled="isFieldDisabled" />
			   	<label class="block text-xs text-ink-gray-5">Assigned To</label>
				<MultiSelect
					:options="assignedToOptions"
					v-model="newTask.assigned_to"
				>
					<template #footer="{ clearAll, selectAll }">
					<div class="flex justify-between my-2">
						<Button theme="red" @click="clearAll">
							<template #prefix>
								<LucideTrash class="size-4" />
							</template>
							Clear All
							</Button>

							<Button @click="selectAll">
							<template #prefix>
								<LucideCheck class="size-4" />
							</template>
							Select All
						</Button>
					</div>
					</template>
				</MultiSelect>
				<FormControl type="number" label="Expected Time (In Hrs)" v-model="newTask.expected_time" />
			  <FileUploader @success="handleFileUpload">
				<template #default="{ openFileSelector }">
				  <FormControl type="button" label="Attachments" @click="openFileSelector">
					<template #prefix><IconPaperclip class="w-4 h-4" /></template>
				  </FormControl>
				</template>
			  </FileUploader>
			</div>
		  </div>

		  <div v-if="newTask.attachments && newTask.attachments.length > 0" class="space-y-2">
			<label class="text-xs font-medium text-slate-600 uppercase">Attachments</label>
			<div class="border rounded-lg overflow-hidden border-slate-200">
			  <table class="w-full text-left text-sm">
				<thead class="bg-slate-50 border-b border-slate-200">
				  <tr>
					<th class="px-4 py-2">File Name</th>
					<th class="px-4 py-2 text-right"></th>
				  </tr>
				</thead>
				<tbody class="divide-y divide-slate-100 bg-white">
				  <tr v-for="(file, index) in newTask.attachments" :key="index">
					<td class="px-4 py-2">
					  <a :href="file.file_url" target="_blank" class="text-blue-600 flex items-center gap-2">
						<IconBriefcase class="w-3.5 h-3.5" /> {{ file.file_name }}
					  </a>
					</td>
					<td class="px-4 py-2 text-right">
					  <Button variant="ghost" @click="removeAttachment(index)" class="!text-red-500">
						<IconPlus class="w-4 h-4 rotate-45" />
					  </Button>
					</td>
				  </tr>
				</tbody>
			  </table>
			</div>
		  </div>

		  <!-- ── Dialog: Task Description with Voice Input ── -->
		  <div class="space-y-2 border-t pt-4">
			<div class="flex items-center justify-between">
			  <label class="text-xs font-medium text-slate-600 uppercase tracking-wider">Task Description</label>
			  <!-- Voice Controls -->
			  <div class="flex items-center gap-2">
				<!-- Speech-to-text Info -->
				<span v-if="activeEditorKey === 'dialog' && interimText" class="text-xs text-slate-400 italic truncate max-w-[180px]">"{{ interimText }}..."</span>
				<span v-if="activeEditorKey === 'dialog' && voiceError" class="text-xs text-red-500">{{ voiceError }}</span>
				<span v-if="activeEditorKey === 'dialog' && justInserted" class="text-xs text-green-600 font-semibold">✓ Inserted</span>

				<!-- Audio recording Info -->
				<span v-if="activeAudioKey === 'dialog' && uploadingAudio" class="text-xs text-blue-500 flex items-center gap-1">
					<div class="w-3.5 h-3.5 border border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
					Uploading...
				</span>
				<span v-if="activeAudioKey === 'dialog' && audioError" class="text-xs text-red-500">{{ audioError }}</span>
				<span v-if="isRecordingAudio && activeAudioKey === 'dialog'" class="text-xs text-red-500 font-medium flex items-center gap-1.5 animate-pulse">
					<span class="w-2 h-2 rounded-full bg-red-500"></span>
					{{ formatDuration(audioDuration) }}
				</span>

				<!-- Dictate Button -->
				<button
				  v-if="!isRecordingAudio || activeAudioKey !== 'dialog'"
				  @click="toggleVoice('dialog')"
				  :disabled="isRecordingAudio || uploadingAudio"
				  type="button"
				  :title="isRecording && activeEditorKey === 'dialog' ? 'Stop dictating' : 'Start dictating (Voice to Text)'"
				  :class="[
					'flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border transition-all select-none disabled:opacity-50 disabled:cursor-not-allowed',
					isRecording && activeEditorKey === 'dialog'
					  ? 'bg-red-500 text-white border-red-500 animate-pulse shadow'
					  : 'bg-white text-slate-600 border-slate-200 hover:border-blue-400 hover:text-blue-600'
				  ]"
				>
				  <!-- Mic icon -->
				  <svg v-if="!(isRecording && activeEditorKey === 'dialog')" xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
					<path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
					<path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
				  </svg>
				  <!-- Stop icon -->
				  <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
					<rect x="6" y="6" width="12" height="12" rx="2"/>
				  </svg>
				  {{ isRecording && activeEditorKey === 'dialog' ? 'Stop' : 'Dictate' }}
				</button>

				<!-- Record Audio Button -->
				<button
				  v-if="!isRecording || activeEditorKey !== 'dialog'"
				  @click="toggleAudioRecording('dialog')"
				  :disabled="isRecording || uploadingAudio"
				  type="button"
				  :title="isRecordingAudio && activeAudioKey === 'dialog' ? 'Stop recording' : 'Record audio file'"
				  :class="[
					'flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border transition-all select-none disabled:opacity-50 disabled:cursor-not-allowed',
					isRecordingAudio && activeAudioKey === 'dialog'
					  ? 'bg-red-600 text-white border-red-600 animate-pulse shadow'
					  : 'bg-white text-slate-600 border-slate-200 hover:border-orange-400 hover:text-orange-600'
				  ]"
				>
				  <svg v-if="!(isRecordingAudio && activeAudioKey === 'dialog')" xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
					<path d="M19 10v1a7 7 0 0 1-14 0v-1M12 19v4M8 23h8"/>
				  </svg>
				  <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
					<rect x="6" y="6" width="12" height="12" rx="2"/>
				  </svg>
				  {{ isRecordingAudio && activeAudioKey === 'dialog' ? 'Stop' : 'Record Audio' }}
				</button>
			  </div>
			</div>
			<div class="border rounded-lg bg-white shadow-sm overflow-hidden editor-container">
			  <TextEditor
				ref="dialogEditorRef"
				editor-class="prose-sm max-w-none p-6 outline-none infinite-editor"
				:content="newTask.description"
				@change="(val) => (newTask.description = val)"
				:bubbleMenu="true"
				:fixed-menu="true"
				:extensions="[AudioExtension]"
			  />
			</div>
		  </div>
		</div>
	  </template>
	</Dialog>

	<div 
		v-if="showEditTask" 
		class="fixed inset-0 flex justify-end bg-slate-900/40 backdrop-blur-sm transition-opacity z-50"
		@click.self="showEditTask = false"
	>
		<div class="w-full max-w-7xl bg-white h-full md:h-[calc(100vh-30px)] my-0 mr-0 ml-0 md:my-[15px] md:mr-[15px] md:ml-[15px] rounded-none md:rounded-2xl shadow-2xl flex flex-col animate-slide-in overflow-y-auto md:overflow-hidden">
			<div class="bg-white border-b px-2 py-2 flex items-center justify-between z-10">
				<div class="flex items-center gap-3">
					<Badge :theme="getPriorityTheme(newTask.priority)" variant="subtle" size="md">
					{{ newTask.priority }}
					</Badge>
					<h2 class="text-lg font-bold text-slate-900 truncate">
					{{ isEditMode ? 'Task Details' : 'New Task' }}
					</h2>
				</div>
				<div class="flex items-center gap-2">
					<Button variant="solid" :loading="saving" @click="handleSaveTask" class="!bg-blue-600">
					{{ isEditMode ? 'Save Changes' : 'Create Task' }}
					</Button>
					<Button variant="ghost" class="!px-2" @click="showEditTask = false">
						<IconX class="w-5 h-5" />
					</Button>
				</div>
				</div>

				<div v-if="!editPanelReady" class="flex-1 grid place-items-center bg-slate-50/30">
					<div class="flex items-center gap-3 text-slate-500">
						<div class="w-5 h-5 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
						<span class="text-sm font-medium">Loading task details...</span>
					</div>
				</div>

				<div v-else class="flex-1 flex flex-col md:overflow-hidden md:min-h-0">
				<div class="flex-grow md:flex-1 min-w-0 flex flex-col md:flex-row md:overflow-hidden md:min-h-0">
				
				<div class="w-full flex flex-col md:flex-1 md:min-h-0 bg-slate-50/20">
					<!-- Scrollable Content Area -->
					<div class="p-6 space-y-6 w-full flex-grow md:flex-1 md:overflow-y-auto custom-scrollbar md:min-h-0">
						<div class="space-y-6">
							<input 
								v-model="newTask.subject" 
								:disabled="isFieldDisabled"
								class="text-3xl font-black text-slate-900 w-full border-none focus:ring-0 p-0 placeholder-slate-300 mb-2 bg-transparent disabled:opacity-75 disabled:cursor-not-allowed" 
								placeholder="Task Subject..."
							/>
							
							<!-- ── Edit Panel: Task Description with Voice Input ── -->
							<div class="space-y-2">
								<div class="flex items-center justify-between">
									<label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">Description</label>
									<!-- Voice Controls -->
									<div class="flex items-center gap-2">
										<!-- Speech-to-text Info -->
										<span v-if="activeEditorKey === 'panel' && interimText" class="text-xs text-slate-400 italic truncate max-w-[180px]">"{{ interimText }}..."</span>
										<span v-if="activeEditorKey === 'panel' && voiceError" class="text-xs text-red-500">{{ voiceError }}</span>
										<span v-if="activeEditorKey === 'panel' && justInserted" class="text-xs text-green-600 font-semibold">✓ Inserted</span>

										<!-- Audio recording Info -->
										<span v-if="activeAudioKey === 'panel' && uploadingAudio" class="text-xs text-blue-500 flex items-center gap-1">
											<div class="w-3.5 h-3.5 border border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
											Uploading...
										</span>
										<span v-if="activeAudioKey === 'panel' && audioError" class="text-xs text-red-500">{{ audioError }}</span>
										<span v-if="isRecordingAudio && activeAudioKey === 'panel'" class="text-xs text-red-500 font-medium flex items-center gap-1.5 animate-pulse">
											<span class="w-2 h-2 rounded-full bg-red-500"></span>
											{{ formatDuration(audioDuration) }}
										</span>

										<!-- Dictate Button -->
										<button
										  v-if="!isRecordingAudio || activeAudioKey !== 'panel'"
										  @click="toggleVoice('panel')"
										  :disabled="isRecordingAudio || uploadingAudio"
										  type="button"
										  :title="isRecording && activeEditorKey === 'panel' ? 'Stop dictating' : 'Start dictating (Voice to Text)'"
										  :class="[
											'flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border transition-all select-none disabled:opacity-50 disabled:cursor-not-allowed',
											isRecording && activeEditorKey === 'panel'
											  ? 'bg-red-500 text-white border-red-500 animate-pulse shadow'
											  : 'bg-white text-slate-600 border-slate-200 hover:border-blue-400 hover:text-blue-600'
										  ]"
										>
										  <!-- Mic icon -->
										  <svg v-if="!(isRecording && activeEditorKey === 'panel')" xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
											<path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
											<path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
										  </svg>
										  <!-- Stop icon -->
										  <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
											<rect x="6" y="6" width="12" height="12" rx="2"/>
										  </svg>
										  {{ isRecording && activeEditorKey === 'panel' ? 'Stop' : 'Dictate' }}
										</button>

										<!-- Record Audio Button -->
										<button
										  v-if="!isRecording || activeEditorKey !== 'panel'"
										  @click="toggleAudioRecording('panel')"
										  :disabled="isRecording || uploadingAudio"
										  type="button"
										  :title="isRecordingAudio && activeAudioKey === 'panel' ? 'Stop recording' : 'Record audio file'"
										  :class="[
											'flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border transition-all select-none disabled:opacity-50 disabled:cursor-not-allowed',
											isRecordingAudio && activeAudioKey === 'panel'
											  ? 'bg-red-600 text-white border-red-600 animate-pulse shadow'
											  : 'bg-white text-slate-600 border-slate-200 hover:border-orange-400 hover:text-orange-600'
										  ]"
										>
										  <svg v-if="!(isRecordingAudio && activeAudioKey === 'panel')" xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
											<path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
											<path d="M19 10v1a7 7 0 0 1-14 0v-1M12 19v4M8 23h8"/>
										  </svg>
										  <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
											<rect x="6" y="6" width="12" height="12" rx="2"/>
										  </svg>
										  {{ isRecordingAudio && activeAudioKey === 'panel' ? 'Stop' : 'Record Audio' }}
										</button>
									</div>
								</div>
								<div class="border border-slate-200 rounded-xl bg-white shadow-sm overflow-hidden focus-within:border-blue-300 focus-within:ring-2 focus-within:ring-blue-100/50 transition-all">
									<TextEditor
										ref="panelEditorRef"
										editor-class="prose-sm max-w-none p-4 min-h-[220px] outline-none bg-white"
										:content="newTask.description"
										@change="(val) => (newTask.description = val)"
										:fixed-menu="true"
										:extensions="[AudioExtension]"
									/>
								</div>
							</div>
						</div>

						<!-- Premium Discussion & Activity Timeline (Inline, no double-scrollbars!) -->
						<div class="pt-8 border-t border-slate-200 mt-8 space-y-6">
							<div class="flex items-center justify-between">
								<div class="flex items-center gap-2">
									<IconMessageSquare class="w-4 h-4 text-slate-500" />
									<h3 class="text-sm font-bold text-slate-800">Discussion & Activity</h3>
									<span class="text-xs bg-slate-100 text-slate-500 px-2.5 py-0.5 rounded-full font-semibold">
										{{ comments.data?.length || 0 }} updates
									</span>
								</div>
							</div>

							<div class="relative min-h-[50px] pb-6">
								<div v-if="comments.loading" class="flex justify-center py-8">
									<div class="w-6 h-6 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
								</div>

								<div v-else-if="comments.data && comments.data.length > 0" class="relative pl-6 border-l-2 border-slate-100 ml-4 space-y-6">
									<div v-for="comment in comments.data" :key="comment.name" class="relative group">
										<!-- Timeline Avatar absolute on rail -->
										<div class="absolute -left-[37px] top-1 z-10">
											<Avatar 
												:image="getUserAvatarImage(comment.comment_by)"
												:label="comment.comment_by || 'User'" 
												size="sm" 
												class="ring-4 ring-white shadow-sm" 
											/>
										</div>

										<!-- Modern Message Bubble Card -->
										<div class="bg-white border border-slate-200/60 rounded-2xl rounded-tl-none p-4 shadow-sm hover:shadow-md hover:border-slate-200 transition-all duration-200">
											<div class="flex items-center justify-between mb-2">
												<div class="flex items-center gap-2">
													<span class="text-xs font-bold text-slate-800">{{ comment.comment_by }}</span>
													<span class="text-[10px] text-slate-400 font-medium">{{ formatTimeAgo(comment.creation) }}</span>
												</div>

												<!-- Comment Edit/Delete Actions -->
												<div class="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity" v-if="comment.comment_by === session.user">
													<button 
														@click="startEditing(comment)"
														class="p-1 hover:bg-slate-50 rounded text-slate-400 hover:text-blue-600 transition-colors"
														title="Edit Comment"
													>
														<IconEdit3 class="w-3.5 h-3.5" />
													</button>
													<button 
														@click="handleDeleteComment(comment.name)"
														class="p-1 hover:bg-red-50 rounded text-slate-400 hover:text-red-600 transition-colors"
														title="Delete Comment"
													>
														<IconTrash2 class="w-3.5 h-3.5" />
													</button>
												</div>
											</div>

											<div class="text-sm text-slate-600 leading-relaxed">
												<div v-if="editingCommentName === comment.name" class="space-y-3">
													<FormControl 
														type="textarea"
														v-model="editContent" 
														class="w-full rounded-xl border border-slate-200 p-2 text-sm focus:ring-1 focus:ring-blue-500 outline-none resize-none"
													/>
													<div class="flex justify-end gap-2">
														<Button size="sm" variant="ghost" @click="cancelEdit">Cancel</Button>
														<Button size="sm" variant="solid" @click="handleUpdateComment(comment.name)" class="!bg-blue-600">Save</Button>
													</div>
												</div>
												<div v-else class="prose prose-sm max-w-none text-slate-600" v-html="comment.content"></div>
											</div>
										</div>
									</div>
								</div>

								<div v-else class="flex flex-col items-center justify-center py-12 text-slate-400 bg-white rounded-2xl border border-dashed border-slate-200">
									<IconMessageSquare class="w-8 h-8 mb-2 opacity-25 text-slate-500" />
									<p class="text-xs font-semibold italic">No updates or comments yet. Start the conversation!</p>
								</div>
							</div>
						</div>
					</div>

					<!-- Stuck/Docked discussion composer at the bottom -->
					<div class="p-4 bg-white border">
						<CommentBox
							v-model="commentText"
							:avatar="getUserAvatarImage(session.user)"
							:user="session.user"
							:userName="session.userFullName"
							placeholder="Type a message..."
							:loading="comments.loading"
							@submit="handlePostComment"
						/>
					</div>
				</div>

				<div class="w-full md:w-80 md:min-w-80 md:shrink-0 border-t md:border-t-0 md:border-l bg-slate-50/50 p-3 pb-28 space-y-4 overflow-y-auto custom-scrollbar">
					<div v-if="newTask.fullfilled_in_display_text" class="flex items-center justify-between bg-emerald-50/50 border border-emerald-100/50 rounded-lg p-2 mb-2">
						<span class="text-[10px] font-bold text-emerald-600 uppercase tracking-tight">Fulfilled In</span>
						<Badge 
							theme="green" 
							variant="subtle" 
							:label="newTask.fullfilled_in_display_text"
						>
						</Badge>
					</div>
					<Badge theme="red" variant="subtle" v-if="newTask.is_overdue" label="Overdue">
					</Badge>
					<div class="space-y-2">
						<DetailItem label="Status">
							<FormControl type="select" :options="statusOptions.map(s => s.value)" v-model="newTask.status" class="!mb-0 shadow-sm"/>
						</DetailItem>

						<DetailItem label="Project">
							<FormControl type="select" :options="projectResource.data" v-model="newTask.project" class="!mb-0 shadow-sm" :disabled="isFieldDisabled"/>
						</DetailItem>

						<DetailItem label="Department">
							<FormControl type="select" :options="departmentResource.data" v-model="newTask.department" class="!mb-0 shadow-sm" :disabled="isFieldDisabled"/>
						</DetailItem>

						<DetailItem label="Priority">
							<FormControl type="select" :options="priorityOptions" v-model="newTask.priority" class="!mb-0 shadow-sm" :disabled="isFieldDisabled"/>
						</DetailItem>
						
						<DetailItem label="Security Impact">
							<FormControl type="select" :options="securityImpactOptions" v-model="newTask.security_impact" class="!mb-0 shadow-sm" :disabled="isFieldDisabled"/>
						</DetailItem>

						<DetailItem label="Assigned By">
							<FormControl type="select" v-model="newTask.assigned_by" :options="userResource.data" :disabled="isFieldDisabled"/>
						</DetailItem>

						<DetailItem label="Assigned To">
							<MultiSelect
								:options="assignedToOptions"
								v-model="newTask.assigned_to"
								:disabled="isFieldDisabled"
							>
								<template #footer="{ clearAll, selectAll }">
									<div class="flex justify-between my-2">
										<Button theme="red" @click="clearAll">
											<template #prefix>
												<LucideTrash class="size-4" />
											</template>
										Clear All
										</Button>

										<Button @click="selectAll">
											<template #prefix>
												<LucideCheck class="size-4" />
											</template>
										Select All
										</Button>
									</div>
								</template>
							</MultiSelect>
						</DetailItem>

						<DetailItem label="Assigned Datetime">
							<FormControl type="datetime-local" :model-value="formatForInput(newTask.assigned_datetime)" class="shadow-sm" disabled="true"/>
						</DetailItem>

						<DetailItem label="Deadline">
							<FormControl type="date" v-model="newTask.exp_end_date" class="shadow-sm" :disabled="isFieldDisabled" />
						</DetailItem>

						<DetailItem label="Completed By" v-if="newTask.completed_by">
							<FormControl type="select" v-model="newTask.completed_by" :options="userResource.data" disabled="true" />
						</DetailItem>

						<DetailItem label="Expected Time (In Hrs)">
							<FormControl type="number" v-model="newTask.expected_time" class="shadow-sm" :disabled="isFieldDisabled"/>
						</DetailItem>

						<div class="pt-4 border-t border-slate-200">
						<label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-3">
							Attachments
						</label>
						<div class="space-y-2">
							<FileUploader @success="handleFileUpload">
							<template #default="{ openFileSelector }">
								<button 
								@click="openFileSelector" 
								class="w-full flex items-center justify-center gap-2 border-2 border-dashed border-slate-200 rounded-xl p-4 text-slate-500 hover:border-blue-400 hover:text-blue-500 hover:bg-blue-50/30 transition-all group"
								>
								<IconPaperclip class="w-4 h-4" />
								<span class="text-xs font-semibold">Add Files</span>
								</button>
							</template>
							</FileUploader>
							
							<div class="grid grid-cols-1 gap-2">
							<div 
								v-for="(file, idx) in newTask.attachments" 
								:key="idx" 
								class="group flex items-center justify-between bg-white border border-slate-200 rounded-lg shadow-sm hover:border-blue-300 transition-all overflow-hidden"
							>
								<a 
								:href="file.file_url" 
								target="_blank" 
								class="flex flex-1 items-center gap-2 p-2 cursor-pointer hover:bg-blue-50/50 transition-colors truncate"
								>
								<IconBriefcase class="w-3.5 h-3.5 text-blue-500 shrink-0" /> 
								<span class="truncate font-medium text-slate-700 text-[11px] group-hover:text-blue-600 transition-colors">
									{{ file.file_name }}
								</span>
								<LucideExternalLink class="w-3 h-3 text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity" />
								</a>

								<button 
								@click.stop="removeAttachment(idx)" 
								class="p-2 mr-1 hover:bg-red-50 rounded-md text-slate-400 hover:text-red-500 transition-colors"
								title="Remove file"
								>
								<IconX class="w-3.5 h-3.5" />
								</button>
							</div>
							</div>
						</div>
						
						</div>
					</div>
				</div>
			</div>
				</div>
	  	</div>
	</div>
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
	FileUploader,
	FormControl,
	ListHeader,
	ListHeaderItem,
	ListRow,
	ListRowItem,
	ListRows,
	ListView,
	LoadingIndicator,
	MultiSelect,
	TextEditor,
	createListResource,
	createResource,
} from "frappe-ui"
import { computed, h, nextTick, onUnmounted, reactive, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import CommentBox from "../components/CommentBox.vue"
import { session } from "../data/session"

import { useSocket } from "@/socket"

import IconAlertCircle from "~icons/lucide/alert-circle"
import IconBriefcase from "~icons/lucide/briefcase"
import IconCheck from "~icons/lucide/check"
import IconCheckCircle from "~icons/lucide/check-circle"
import IconChevronLeft from "~icons/lucide/chevron-left"
import IconChevronRight from "~icons/lucide/chevron-right"
import IconClock from "~icons/lucide/clock"
import IconEdit3 from "~icons/lucide/edit-3"
import IconFlag from "~icons/lucide/flag"
import IconLayoutGrid from "~icons/lucide/layout-grid"
import IconList from "~icons/lucide/list"
import IconMessageSquare from "~icons/lucide/message-square"
import IconPaperclip from "~icons/lucide/paperclip"
import IconPlus from "~icons/lucide/plus"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconSearch from "~icons/lucide/search"
import IconTrash2 from "~icons/lucide/trash-2"
import IconX from "~icons/lucide/x"

import dayjs from "dayjs"
import relativeTime from "dayjs/plugin/relativeTime"
import utc from "dayjs/plugin/utc"

dayjs.extend(relativeTime)
dayjs.extend(utc)

const formatTimeAgo = (date) => {
	if (!date) return ""
	return dayjs(date).fromNow()
}

// ── Audio File Support ─────────────────────────────────────────────────────────
import { AudioExtension } from "@/extensions/audio"

const isRecordingAudio = ref(false)
const uploadingAudio = ref(false)
const audioDuration = ref(0)
const audioError = ref("")
const activeAudioKey = ref(null) // 'dialog' | 'panel' | null
const savedSelectionPosition = ref(null)

let mediaRecorder = null
let audioChunks = []
let audioTimer = null

function formatDuration(sec) {
	const minutes = Math.floor(sec / 60)
	const seconds = sec % 60
	return `${minutes}:${seconds.toString().padStart(2, "0")}`
}

function toggleAudioRecording(key) {
	if (isRecordingAudio.value && activeAudioKey.value === key) {
		stopAudioRecording()
	} else {
		if (isRecordingAudio.value) stopAudioRecording()
		if (isRecording.value) stopVoice()
		startAudioRecording(key)
	}
}

function getCsrfToken() {
	if (window.csrf_token) return window.csrf_token
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	return cookies.get("system_csrf_token") || ""
}

async function uploadRecordedAudio(blob) {
	const csrfToken = getCsrfToken()
	const formData = new FormData()
	const extension = mediaRecorder?.mimeType?.includes("mp4") ? "mp4" : "webm"
	const filename = `voice_recording_${Date.now()}.${extension}`
	const file = new File([blob], filename, { type: blob.type })
	formData.append("file", file)
	formData.append("is_private", 0)
	if (newTask.name) {
		formData.append("doctype", "Task")
		formData.append("docname", newTask.name)
	}

	const response = await fetch("/api/method/upload_file", {
		method: "POST",
		headers: {
			"X-Frappe-CSRF-Token": csrfToken,
		},
		body: formData,
	})
	if (!response.ok) {
		let errorText = "Upload failed"
		try {
			const errJson = await response.json()
			if (errJson._server_messages) {
				const msgs = JSON.parse(errJson._server_messages)
				errorText = msgs.map((m) => JSON.parse(m).message).join(", ")
			} else if (errJson.exception) {
				errorText = errJson.exception
			}
		} catch (_) {
			try {
				errorText = await response.text()
			} catch (_) {}
		}
		throw new Error(errorText)
	}
	const resJson = await response.json()
	return resJson.message.file_url
}

async function startAudioRecording(key) {
	audioError.value = ""
	const editorRef = getEditorRef(key)
	const tiptap = editorRef.value?.editor || editorRef.value?.editor?.value
	if (tiptap) {
		savedSelectionPosition.value = tiptap.state.selection.anchor
	}
	try {
		const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
		activeAudioKey.value = key

		let options = {}
		if (MediaRecorder.isTypeSupported("audio/webm")) {
			options = { mimeType: "audio/webm" }
		} else if (MediaRecorder.isTypeSupported("audio/mp4")) {
			options = { mimeType: "audio/mp4" }
		}

		mediaRecorder = new MediaRecorder(stream, options)
		audioChunks = []

		mediaRecorder.ondataavailable = (e) => {
			if (e.data && e.data.size > 0) {
				audioChunks.push(e.data)
			}
		}

		mediaRecorder.onstop = async () => {
			uploadingAudio.value = true
			try {
				const blob = new Blob(audioChunks, {
					type: mediaRecorder.mimeType || "audio/webm",
				})
				const fileUrl = await uploadRecordedAudio(blob)
				insertAudioIntoEditor(key, fileUrl)
			} catch (err) {
				console.error(err)
				audioError.value = `Upload failed: ${err.message || err}`
			} finally {
				uploadingAudio.value = false
				activeAudioKey.value = null
				stream.getTracks().forEach((track) => track.stop())
			}
		}

		mediaRecorder.start(1000)
		isRecordingAudio.value = true
		audioDuration.value = 0
		audioTimer = setInterval(() => {
			audioDuration.value++
		}, 1000)
	} catch (err) {
		console.error(err)
		audioError.value = "Mic permission denied."
		isRecordingAudio.value = false
		activeAudioKey.value = null
	}
}

function stopAudioRecording(discard = false) {
	if (mediaRecorder && mediaRecorder.state !== "inactive") {
		if (discard) {
			mediaRecorder.onstop = null
		}
		mediaRecorder.stop()
	}
	isRecordingAudio.value = false
	if (audioTimer) {
		clearInterval(audioTimer)
		audioTimer = null
	}
}

function insertAudioIntoEditor(key, fileUrl) {
	const editorRef = getEditorRef(key)
	const tiptap = editorRef.value?.editor
	if (tiptap) {
		if (savedSelectionPosition.value !== null) {
			const pos = Math.min(
				savedSelectionPosition.value,
				tiptap.state.doc.content.size,
			)
			tiptap.commands.setTextSelection(pos)
			savedSelectionPosition.value = null
		} else {
			tiptap.commands.focus("end")
		}
		tiptap
			.chain()
			.focus()
			.insertContent({
				type: "audio",
				attrs: { src: fileUrl },
			})
			.run()
		return
	}

	const frappeEditor = editorRef.value?.editor?.value
	if (frappeEditor) {
		if (savedSelectionPosition.value !== null) {
			const pos = Math.min(
				savedSelectionPosition.value,
				frappeEditor.state.doc.content.size,
			)
			frappeEditor.commands.setTextSelection(pos)
			savedSelectionPosition.value = null
		} else {
			frappeEditor.commands.focus("end")
		}
		frappeEditor
			.chain()
			.focus()
			.insertContent({
				type: "audio",
				attrs: { src: fileUrl },
			})
			.run()
		return
	}

	const proseMirror =
		editorRef.value?.$el?.querySelector(".ProseMirror") ||
		editorRef.value?.$el?.querySelector("[contenteditable]")
	if (proseMirror) {
		proseMirror.focus()
		const html = `<audio src="${fileUrl}" controls class="w-full my-2"></audio>`
		document.execCommand("insertHTML", false, html)
	}
}

// ── Voice Input ───────────────────────────────────────────────────────────────
const dialogEditorRef = ref(null)
const panelEditorRef = ref(null)

const isRecording = ref(false)
const interimText = ref("")
const voiceError = ref("")
const justInserted = ref(false)
// Which editor is currently being dictated into: 'dialog' | 'panel' | null
const activeEditorKey = ref(null)

let recognition = null

function getEditorRef(key) {
	return key === "dialog" ? dialogEditorRef : panelEditorRef
}

function toggleVoice(key) {
	if (isRecording.value && activeEditorKey.value === key) {
		stopVoice()
	} else {
		// If recording in the other editor, stop that first
		if (isRecording.value) stopVoice()
		startVoice(key)
	}
}

function startVoice(key) {
	voiceError.value = ""
	const SR = window.SpeechRecognition || window.webkitSpeechRecognition
	if (!SR) {
		voiceError.value = "Not supported. Use Chrome or Edge."
		return
	}

	activeEditorKey.value = key
	const editorRef = getEditorRef(key)
	const tiptap = editorRef.value?.editor || editorRef.value?.editor?.value
	if (tiptap) {
		savedSelectionPosition.value = tiptap.state.selection.anchor
	}
	recognition = new SR()
	recognition.lang = "en-US" // change to 'ar-AE', 'ml-IN', etc. as needed
	recognition.continuous = true
	recognition.interimResults = true

	recognition.onstart = () => {
		isRecording.value = true
	}

	recognition.onresult = (event) => {
		let interim = ""
		let final = ""
		for (let i = event.resultIndex; i < event.results.length; i++) {
			const t = event.results[i][0].transcript
			if (event.results[i].isFinal) final += t + " "
			else interim += t
		}
		interimText.value = interim

		if (final) {
			insertTextIntoEditor(key, final)
			justInserted.value = true
			setTimeout(() => {
				justInserted.value = false
			}, 1500)
		}
	}

	recognition.onerror = (e) => {
		voiceError.value =
			e.error === "not-allowed" ? "Mic permission denied." : `Error: ${e.error}`
		stopVoice()
	}

	recognition.onend = () => {
		isRecording.value = false
		interimText.value = ""
		activeEditorKey.value = null
	}

	recognition.start()
}

function stopVoice() {
	recognition?.stop()
	recognition = null
	isRecording.value = false
	interimText.value = ""
	activeEditorKey.value = null
}

function insertTextIntoEditor(key, text) {
	const editorRef = getEditorRef(key)

	// Strategy 1: TipTap editor instance (preferred)
	const tiptap = editorRef.value?.editor
	if (tiptap) {
		if (savedSelectionPosition.value !== null) {
			const pos = Math.min(
				savedSelectionPosition.value,
				tiptap.state.doc.content.size,
			)
			tiptap.commands.setTextSelection(pos)
			savedSelectionPosition.value = pos + text.length
		}
		tiptap.chain().focus().insertContent(text).run()
		return
	}

	// Strategy 2: Frappe TextEditor exposes `editor` differently
	const frappeEditor = editorRef.value?.editor?.value
	if (frappeEditor) {
		if (savedSelectionPosition.value !== null) {
			const pos = Math.min(
				savedSelectionPosition.value,
				frappeEditor.state.doc.content.size,
			)
			frappeEditor.commands.setTextSelection(pos)
			savedSelectionPosition.value = pos + text.length
		}
		frappeEditor.chain().focus().insertContent(text).run()
		return
	}

	// Strategy 3: DOM fallback — find the ProseMirror contenteditable div
	const proseMirror =
		editorRef.value?.$el?.querySelector(".ProseMirror") ||
		editorRef.value?.$el?.querySelector("[contenteditable]")
	if (proseMirror) {
		proseMirror.focus()
		// Use execCommand as a last resort (deprecated but widely supported)
		document.execCommand("insertText", false, text)
	}
}
// ─────────────────────────────────────────────────────────────────────────────

// Dynamic limited option lists for native selects
const limitedProjects = computed(() => {
	const data = projectResource.data || []
	if (data.length <= 100) return data
	const sliced = data.slice(0, 100)
	if (
		selectedFilters.project &&
		!sliced.some((x) => x.value === selectedFilters.project)
	) {
		const match = data.find((x) => x.value === selectedFilters.project)
		if (match) sliced.push(match)
	}
	return sliced
})

const limitedDepartments = computed(() => {
	const data = departmentResource.data || []
	if (data.length <= 100) return data
	const sliced = data.slice(0, 100)
	if (
		selectedFilters.department &&
		!sliced.some((x) => x.value === selectedFilters.department)
	) {
		const match = data.find((x) => x.value === selectedFilters.department)
		if (match) sliced.push(match)
	}
	return sliced
})

const limitedUsersAssignedBy = computed(() => {
	const data = userResource.data || []
	if (data.length <= 100) return data
	const sliced = data.slice(0, 100)
	if (
		selectedFilters.assigned_by &&
		!sliced.some((x) => x.value === selectedFilters.assigned_by)
	) {
		const match = data.find((x) => x.value === selectedFilters.assigned_by)
		if (match) sliced.push(match)
	}
	return sliced
})

// Popover refs for Autocomplete
const projectAutocomplete = ref(null)
const departmentAutocomplete = ref(null)
const assignedByAutocomplete = ref(null)
const assignedToAutocomplete = ref(null)

function getProjectLabel(val) {
	if (!val) return "Project"
	const match = projectResource.data?.find((p) => p.value === val)
	return match ? match.label : val
}

function getDepartmentLabel(val) {
	if (!val) return "Department"
	const match = departmentResource.data?.find((d) => d.value === val)
	return match ? match.label : val
}

function getUserLabel(val, defaultLabel = "User") {
	if (!val) return defaultLabel
	const match = userResource.data?.find((u) => u.value === val)
	return match ? match.label : val
}

// State
const viewMode = ref("list")
const showCreateDialog = ref(false)
const isEditMode = ref(false)
const showEditTask = ref(false)
const editPanelReady = ref(false)
const searchQuery = ref("")
const debouncedSearchQuery = ref("")

let searchTimeout = null
watch(searchQuery, (val) => {
	clearTimeout(searchTimeout)
	searchTimeout = setTimeout(() => {
		debouncedSearchQuery.value = val
	}, 350)
})
const saving = ref(false)
const commentText = ref("")
const editingCommentName = ref(null)
const editContent = ref("")
const isActivityExpanded = ref(false)

const selectedTasks = ref(new Set())
const showBulkDeleteDialog = ref(false)
const showErrorDialog = ref(false)
const errorDialogTitle = ref("Error")
const errorMessage = ref("")

const actionsOptions = computed(() => [
	{
		label: "Delete",
		onClick: () => {
			showBulkDeleteDialog.value = true
		},
	},
])

async function executeBulkDelete() {
	if (selectedTasks.value.size === 0) return
	const names = Array.from(selectedTasks.value)

	saving.value = true
	let failed = false
	const succeeded = []

	for (const name of names) {
		try {
			await createResource({
				url: "frappe.client.delete",
				params: { doctype: "Task", name },
			}).submit()
			succeeded.push(name)
		} catch (e) {
			failed = true
			console.error(`Failed to delete task ${name}`, e)
		}
	}

	for (const name of succeeded) {
		selectedTasks.value.delete(name)
	}

	fetchTasks()

	if (failed) {
		errorDialogTitle.value = "Cannot Delete"
		errorMessage.value =
			"This task cannot be deleted because it is linked with other documents."
		showErrorDialog.value = true
	} else {
		showBulkDeleteDialog.value = false
	}
	saving.value = false
}

const socket = useSocket()

const isEmployeeOnly = computed(() => {
	const userRoles = session.roles || []
	return userRoles.includes("Employee") && !session.isAdmin
})

const isAdmin = computed(() => session.isAdmin)

const isCreator = computed(() => {
	if (!isEditMode.value) return true
	return newTask.owner === session.user || newTask.assigned_by === session.user
})

const isFieldDisabled = computed(() => {
	return isEmployeeOnly.value && !isCreator.value
})

const assignedToOptions = computed(() => {
	if (isFieldDisabled.value) {
		return [
			{ label: session.userFullName || session.user, value: session.user },
		]
	}
	if (isEmployeeOnly.value) {
		return [
			{
				label: session.userFullName || session.user,
				value: session.user,
				image: session.userImage || "",
			},
		]
	}
	return userResource.data || []
})

const DetailItem = (props, { slots }) => {
	return h("div", { class: "space-y-1.5" }, [
		h(
			"label",
			{ class: "text-[11px] font-semibold text-slate-500" },
			props.label,
		),
		slots.default(),
	])
}

const selectedFilters = reactive({
	project: "",
	department: "",
	status: "",
	priority: "",
	assigned_by: "",
	assigned_to: "",
	deadline: "",
})

const statusOptions = [
	{ label: "Open", value: "Open" },
	{ label: "Working", value: "Working" },
	{ label: "Pending Review", value: "Pending Review" },
	{ label: "Completed", value: "Completed" },
	{ label: "Cancelled", value: "Cancelled" },
]

const filterStatusOptions = [
	{ label: "Open", value: "Open" },
	{ label: "Working", value: "Working" },
	{ label: "Pending Review", value: "Pending Review" },
	{ label: "Completed", value: "Completed" },
	{ label: "Overdue", value: "Overdue" },
	{ label: "Cancelled", value: "Cancelled" },
]

const priorityOptions = [
	{ label: "Low", value: "Low" },
	{ label: "Medium", value: "Medium" },
	{ label: "High", value: "High" },
	{ label: "Urgent", value: "Urgent" },
]

const deadlineOptions = [
	{ label: "Deadline", value: "" },
	{ label: "Today", value: "today" },
	{ label: "Tomorrow", value: "tomorrow" },
	{ label: "Next 7 Days", value: "next_7_days" },
	{ label: "Next 30 Days", value: "next_30_days" },
	{ label: "Yesterday", value: "yesterday" },
	{ label: "Last 7 Days", value: "last_7_days" },
	{ label: "Last 30 Days", value: "last_30_days" },
	{ label: "This Week", value: "this_week" },
	{ label: "Last Week", value: "last_week" },
	{ label: "This Month", value: "this_month" },
	{ label: "Last Month", value: "last_month" },
	{ label: "This Year", value: "this_year" },
	{ label: "Last Year", value: "last_year" },
]

const securityImpactOptions = [
	{ label: "Yes", value: "Yes" },
	{ label: "No", value: "No" },
	{ label: "Not Applicable", value: "Not Applicable" },
]

const columns = [
	{ label: "Task Name", key: "subject", icon: IconCheckCircle, width: "280px" },
	{
		label: "Description",
		key: "description_for_list",
		icon: IconCheckCircle,
		width: "3.5fr",
	},
	{
		label: "Project",
		key: "project_name",
		icon: IconBriefcase,
		width: "150px",
	},
	{ label: "Department", key: "department", icon: IconBriefcase },
	{ label: "Assigned DateTime", key: "assigned_datetime", icon: IconBriefcase },
	{ label: "Priority", key: "priority", icon: IconFlag },
	{ label: "Status", key: "status", icon: IconAlertCircle },
	{ label: "Deadline", key: "exp_end_date", icon: IconClock },
	{ label: "Task ID", key: "name", icon: IconCheckCircle },
	{
		label: "",
		key: "has_unseen_comments",
		icon: IconMessageSquare,
		width: "90px",
	},
]

// Resources
const userResource = createResource({
	url: "tactix.api.generic.get_users_excluding_ticket_users",
	auto: true,
	transform: (users) =>
		users.map((u) => ({
			label: u.full_name || u.name,
			value: u.name,
			image: u.user_image || "",
		})),
})

function getUserAvatarImage(userName) {
	if (!userName) return ""
	const match = userResource.data?.find((user) => user.value === userName)
	return match?.image || ""
}

const projectResource = createListResource({
	doctype: "Project",
	fields: ["project_name", "name"],
	auto: true,
	transform: (projects) =>
		projects.map((p) => ({ label: p.project_name, value: p.name })),
	pageLength: 10000,
})

const departmentResource = createListResource({
	doctype: "Department",
	fields: ["name"],
	auto: true,
	transform: (departments) =>
		departments.map((d) => ({ label: d.name, value: d.name })),
	pageLength: 10000,
})

// Unified Filter Logic
const taskFilters = computed(() => {
	const f = {}

	if (debouncedSearchQuery.value) f.subject = ["like", `%${debouncedSearchQuery.value}%`]
	if (selectedFilters.project) f.project = selectedFilters.project
	if (selectedFilters.status) f.status = selectedFilters.status
	if (selectedFilters.priority) f.priority = selectedFilters.priority
	if (selectedFilters.assigned_by) f.assigned_by = selectedFilters.assigned_by
	if (selectedFilters.assigned_to) f.assigned_to = selectedFilters.assigned_to
	if (selectedFilters.department) f.department = selectedFilters.department

	if (selectedFilters.deadline) {
		const today = dayjs().format("YYYY-MM-DD")
		const tomorrow = dayjs().add(1, "day").format("YYYY-MM-DD")
		const yesterday = dayjs().subtract(1, "day").format("YYYY-MM-DD")

		switch (selectedFilters.deadline) {
			case "yesterday":
				f.exp_end_date = yesterday
				break
			case "last_7_days":
				f.exp_end_date = [
					"between",
					[dayjs().subtract(7, "day").format("YYYY-MM-DD"), today],
				]
				break
			case "last_30_days":
				f.exp_end_date = [
					"between",
					[dayjs().subtract(30, "day").format("YYYY-MM-DD"), today],
				]
				break
			case "last_week":
				f.exp_end_date = [
					"between",
					[
						dayjs().subtract(1, "week").startOf("week").format("YYYY-MM-DD"),
						dayjs().subtract(1, "week").endOf("week").format("YYYY-MM-DD"),
					],
				]
				break
			case "last_month":
				f.exp_end_date = [
					"between",
					[
						dayjs().subtract(1, "month").startOf("month").format("YYYY-MM-DD"),
						dayjs().subtract(1, "month").endOf("month").format("YYYY-MM-DD"),
					],
				]
				break
			case "last_year":
				f.exp_end_date = [
					"between",
					[
						dayjs().subtract(1, "year").startOf("year").format("YYYY-MM-DD"),
						dayjs().subtract(1, "year").endOf("year").format("YYYY-MM-DD"),
					],
				]
				break
			case "today":
				f.exp_end_date = today
				break
			case "tomorrow":
				f.exp_end_date = tomorrow
				break
			case "next_3_days":
				f.exp_end_date = [
					"between",
					[today, dayjs().add(3, "day").format("YYYY-MM-DD")],
				]
				break
			case "next_7_days":
				f.exp_end_date = [
					"between",
					[today, dayjs().add(7, "day").format("YYYY-MM-DD")],
				]
				break
			case "next_30_days":
				f.exp_end_date = [
					"between",
					[today, dayjs().add(30, "day").format("YYYY-MM-DD")],
				]
				break
			case "this_week":
				f.exp_end_date = [
					"between",
					[
						dayjs().startOf("week").format("YYYY-MM-DD"),
						dayjs().endOf("week").format("YYYY-MM-DD"),
					],
				]
				break
			case "this_month":
				f.exp_end_date = [
					"between",
					[
						dayjs().startOf("month").format("YYYY-MM-DD"),
						dayjs().endOf("month").format("YYYY-MM-DD"),
					],
				]
				break
			case "this_year":
				f.exp_end_date = [
					"between",
					[
						dayjs().startOf("year").format("YYYY-MM-DD"),
						dayjs().endOf("year").format("YYYY-MM-DD"),
					],
				]
				break
		}
	}

	return f
})

const hasActiveFilters = computed(() => {
	if (debouncedSearchQuery.value) return true
	return Object.values(selectedFilters).some((value) => value !== "")
})

function clearFilters() {
	searchQuery.value = ""
	debouncedSearchQuery.value = ""
	selectedFilters.project = ""
	selectedFilters.department = ""
	selectedFilters.status = ""
	selectedFilters.priority = ""
	selectedFilters.assigned_by = ""
	selectedFilters.assigned_to = ""
	selectedFilters.deadline = ""
}

function filterByStat(label) {
	if (label === "Total") selectedFilters.status = ""
	else if (label === "In Progress") selectedFilters.status = "Working"
	else selectedFilters.status = label
}

const currentPage = ref(1)
const pageLength = 20

const tasksResource = createResource({
	url: "tactix.api.tasks.get_tasks",
	initialData: { tasks: [], total_count: 0 },
	transform: (data) => {
		if (Array.isArray(data)) return { tasks: data, total_count: data.length }
		return data || { tasks: [], total_count: 0 }
	},
})

const tasksSummaryResource = createResource({
	url: "tactix.api.tasks.get_task_summary",
	initialData: {
		total: 0,
		open: 0,
		working: 0,
		pending_review: 0,
		completed: 0,
		overdue: 0,
	},
	transform: (data) =>
		data || {
			total: 0,
			open: 0,
			working: 0,
			pending_review: 0,
			completed: 0,
			overdue: 0,
		},
})

function fetchTasks() {
	tasksResource.fetch({
		filters: taskFilters.value,
		start: (currentPage.value - 1) * pageLength,
		page_length: pageLength,
	})
}

function fetchTaskSummary() {
	tasksSummaryResource.fetch({ filters: taskFilters.value })
}

fetchTasks()
fetchTaskSummary()

watch(
	taskFilters,
	() => {
		currentPage.value = 1
		fetchTasks()
		fetchTaskSummary()
		if (viewMode.value === "board") fetchAllColumns()
	},
	{ deep: true },
)

watch(currentPage, () => {
	fetchTasks()
})

const totalCount = computed(() => tasksResource.data?.total_count || 0)
const totalPages = computed(() =>
	Math.max(1, Math.ceil(totalCount.value / pageLength)),
)

const paginationPages = computed(() => {
	const current = currentPage.value
	const total = totalPages.value
	const pages = []

	if (total <= 7) {
		for (let i = 1; i <= total; i++) pages.push(i)
	} else {
		pages.push(1)
		if (current > 3) pages.push("...")
		const start = Math.max(2, current - 1)
		const end = Math.min(total - 1, current + 1)
		for (let i = start; i <= end; i++) pages.push(i)
		if (current < total - 2) pages.push("...")
		pages.push(total)
	}
	return pages
})

const filteredTasksData = computed(() => tasksResource.data?.tasks || [])

const comments = createResource({
	url: "tactix.api.tasks.get_comments",
	initialData: [],
})

watch(
	() => comments.data,
	(newComments) => {
		isActivityExpanded.value = !!(newComments && newComments.length > 0)
	},
	{ immediate: true },
)

const createTaskAPI = createResource({ url: "tactix.api.tasks.create_task" })
const editTaskAPI = createResource({ url: "tactix.api.tasks.edit_task" })
const updateTaskStatusAPI = createResource({
	url: "tactix.api.tasks.update_task_status",
})

const draggedTask = ref(null)
const hoveredColumn = ref(null)

function onDragStart(event, task) {
	draggedTask.value = task
	if (event.dataTransfer) {
		event.dataTransfer.effectAllowed = "move"
		event.dataTransfer.setData("text/plain", task.name)
	}
}

function onDragEnd() {
	draggedTask.value = null
	hoveredColumn.value = null
}
function onDragEnter(statusValue) {
	hoveredColumn.value = statusValue
}
function onDragLeave() {
	/* intentionally empty */
}

async function onDrop(event, targetStatus) {
	const task = draggedTask.value
	hoveredColumn.value = null
	if (!task || task.status === targetStatus) return

	const oldStatus = task.status
	task.status = targetStatus

	const taskIndex = columnTasks[oldStatus]?.findIndex(
		(t) => t.name === task.name,
	)
	if (taskIndex !== undefined && taskIndex > -1) {
		const [movedTask] = columnTasks[oldStatus].splice(taskIndex, 1)
		if (!columnTasks[targetStatus]) columnTasks[targetStatus] = []
		columnTasks[targetStatus].unshift(movedTask)
	}

	if (tasksSummaryResource.data) {
		if (oldStatus === "Open" && tasksSummaryResource.data.open > 0)
			tasksSummaryResource.data.open--
		else if (oldStatus === "Working" && tasksSummaryResource.data.working > 0)
			tasksSummaryResource.data.working--
		else if (
			oldStatus === "Pending Review" &&
			tasksSummaryResource.data.pending_review > 0
		)
			tasksSummaryResource.data.pending_review--
		else if (
			oldStatus === "Completed" &&
			tasksSummaryResource.data.completed > 0
		)
			tasksSummaryResource.data.completed--

		if (targetStatus === "Open") tasksSummaryResource.data.open++
		else if (targetStatus === "Working") tasksSummaryResource.data.working++
		else if (targetStatus === "Pending Review")
			tasksSummaryResource.data.pending_review++
		else if (targetStatus === "Completed") tasksSummaryResource.data.completed++
	}

	try {
		await updateTaskStatusAPI.submit({ name: task.name, status: targetStatus })
		tasksResource.reload()
		fetchTaskSummary()
	} catch (e) {
		console.error("Failed to save task status drop", e)
		errorDialogTitle.value = "Permission Denied"
		let msg = "You do not have permission to update this task status."
		if (e.message) msg = e.message
		else if (typeof e === "string") msg = e
		if (msg.includes("PermissionError")) msg = msg.split("PermissionError")[1]
		else if (msg.includes("Error:")) msg = msg.split("Error:")[1]
		errorMessage.value = msg.replace(/<[^>]*>/g, "").trim()
		showErrorDialog.value = true
		task.status = oldStatus
		tasksResource.reload()
		fetchTaskSummary()
	}
}

const initialForm = {
	name: "",
	subject: "",
	project: "",
	priority: "Medium",
	status: "Open",
	exp_end_date: "",
	assigned_to: [],
	assigned_date: new Date().toISOString().split("T")[0],
	is_overdue: 0,
	assigned_by: "",
	description: "",
	attachments: [],
	assigned_datetime: "",
	completed_by: "",
	expected_time: "",
	department: "",
	security_impact: "",
}

const newTask = reactive({ ...initialForm })

const kpiStats = computed(() => {
	const summary = tasksSummaryResource.data || {
		total: 0,
		open: 0,
		working: 0,
		pending_review: 0,
		completed: 0,
		overdue: 0,
	}
	return [
		{
			label: "Total",
			value: summary.total,
			icon: IconList,
			color: "text-blue-500",
		},
		{
			label: "Open",
			value: summary.open,
			icon: IconClock,
			color: "text-orange-500",
		},
		{
			label: "In Progress",
			value: summary.working,
			icon: IconClock,
			color: "text-orange-500",
		},
		{
			label: "Pending Review",
			value: summary.pending_review,
			icon: IconClock,
			color: "text-amber-500",
		},
		{
			label: "Completed",
			value: summary.completed,
			icon: IconCheckCircle,
			color: "text-green-500",
		},
		{
			label: "Overdue",
			value: summary.overdue,
			icon: IconAlertCircle,
			color: "text-red-500",
		},
	]
})

const columnTasks = reactive({
	Open: [],
	Working: [],
	"Pending Review": [],
	Completed: [],
	Cancelled: [],
})
const columnPages = reactive({
	Open: 1,
	Working: 1,
	"Pending Review": 1,
	Completed: 1,
	Cancelled: 1,
})
const columnHasMore = reactive({
	Open: true,
	Working: true,
	"Pending Review": true,
	Completed: true,
	Cancelled: true,
})
const columnLoading = reactive({
	Open: false,
	Working: false,
	"Pending Review": false,
	Completed: false,
	Cancelled: false,
})

async function fetchColumnTasks(status, reset = false) {
	if (columnLoading[status]) return
	if (!reset && !columnHasMore[status]) return

	columnLoading[status] = true
	if (reset) {
		columnPages[status] = 1
		columnTasks[status] = []
		columnHasMore[status] = true
	}

	try {
		const filters = { ...taskFilters.value, status }
		const limit = 20
		const start = (columnPages[status] - 1) * limit

		const res = await createResource({
			url: "tactix.api.tasks.get_tasks",
			params: { filters, start, page_length: limit },
		}).submit()

		const tasksList = res?.tasks || []
		columnTasks[status].push(...tasksList)

		if (tasksList.length < limit) columnHasMore[status] = false
		else columnPages[status]++
	} catch (error) {
		console.error(`Failed to fetch tasks for column ${status}:`, error)
	} finally {
		columnLoading[status] = false
	}
}

function fetchAllColumns() {
	for (const opt of statusOptions) fetchColumnTasks(opt.value, true)
}

function handleColumnScroll(e, status) {
	const { scrollTop, scrollHeight, clientHeight } = e.target
	if (scrollHeight - scrollTop - clientHeight < 20) fetchColumnTasks(status)
}

function filteredTasks(status) {
	if (viewMode.value === "board") return columnTasks[status] || []
	return (filteredTasksData.value || []).filter((t) => t.status === status)
}

watch(
	viewMode,
	(newMode) => {
		if (newMode === "board") fetchAllColumns()
	},
	{ immediate: true },
)

watch(
	() => tasksResource.data,
	() => {
		if (viewMode.value === "board") fetchAllColumns()
	},
)

function openCreateDialog() {
	isEditMode.value = false
	Object.assign(newTask, {
		...initialForm,
		attachments: [],
		assigned_by: session.user,
		assigned_to: isFieldDisabled.value ? [session.user] : [],
	})
	showCreateDialog.value = true
}

function openEditDialog(task) {
	isEditMode.value = true
	showEditTask.value = true
	editPanelReady.value = false
	nextTick(() => {
		Object.assign(newTask, { ...task, attachments: task.attachments || [] })
		comments.update({ params: { task: task.name } })
		comments.fetch()
		editPanelReady.value = true
		if (route.params.name !== task.name) {
			router.push({ path: `/tasks/${task.name}` })
		}
	})
}

function handleFileUpload(file) {
	if (!newTask.attachments) newTask.attachments = []
	newTask.attachments.push({
		file_name: file.file_name,
		file_url: file.file_url,
		file_size: file.file_size,
	})
}

function removeAttachment(index) {
	newTask.attachments.splice(index, 1)
}

const handleSaveTask = async () => {
	if (!newTask.subject) return
	saving.value = true
	try {
		const payload = { ...newTask }
		if (isEditMode.value)
			await editTaskAPI.submit({ name: newTask.name, doc: payload })
		else await createTaskAPI.submit({ doc: payload })
		tasksResource.reload()
		showCreateDialog.value = false
		showEditTask.value = false
	} catch (e) {
		console.error(e)
	} finally {
		saving.value = false
	}
}

const formatForInput = (dateStr) => {
	if (!dateStr) return ""
	return dayjs(dateStr).format("YYYY-MM-DDTHH:mm")
}

const formatDateTime = (dateStr) => {
	if (!dateStr) return "—"
	return dayjs(dateStr).format("MMM D, YYYY h:mm A")
}

function startEditing(comment) {
	editingCommentName.value = comment.name
	editContent.value = comment.content.replace(/<[^>]*>?/gm, "")
}

function cancelEdit() {
	editingCommentName.value = null
	editContent.value = ""
}

async function handlePostComment() {
	if (!commentText.value.trim()) return
	try {
		createResource({
			url: "tactix.api.tasks.add_comment",
			params: { task: newTask.name, content: commentText.value },
			auto: true,
			async onSuccess() {
				commentText.value = ""
				await comments.fetch()
			},
		})
	} catch (error) {
		console.error("Failed to post comment:", error)
	}
}

async function handleUpdateComment(name) {
	if (!editContent.value.trim()) return
	try {
		createResource({
			url: "tactix.api.tasks.edit_comment",
			params: { name, content: editContent.value },
			auto: true,
			async onSuccess() {
				editingCommentName.value = null
				await comments.reload()
			},
		})
	} catch (e) {
		console.error("Update failed", e)
	}
}

async function handleDeleteComment(name) {
	try {
		createResource({
			url: "tactix.api.tasks.delete_comment",
			params: { name },
			auto: true,
			async onSuccess() {
				await comments.reload()
			},
		})
	} catch (e) {
		console.error("Delete failed", e)
	}
}

function getPriorityTheme(p) {
	return (
		{ High: "red", Medium: "orange", Low: "gray", Urgent: "red" }[p] || "gray"
	)
}

function getStatusColor(status) {
	return (
		{
			Open: "bg-blue-400",
			Working: "bg-orange-400",
			Completed: "bg-green-500",
			Overdue: "bg-red-500",
			"Pending Review": "bg-red-500",
		}[status] || "bg-slate-200"
	)
}

function viewBtnClass(mode) {
	return [
		"p-1.5 rounded-md transition-all",
		viewMode.value === mode
			? "bg-white shadow-sm text-blue-600"
			: "text-slate-400",
	]
}

function formatDate(dateString) {
	const date = new Date(dateString)
	if (Number.isNaN(date.getTime())) return dateString
	return date.toLocaleDateString("en-US", {
		year: "numeric",
		month: "short",
		day: "numeric",
	})
}

socket.on("test_socket_io", (data) => {
	console.log(data, "Socket IO Worked")
})

const route = useRoute()
const router = useRouter()

async function openTaskByName(taskName) {
	if (!taskName) return
	if (showEditTask.value && newTask.name === taskName) return
	try {
		const res = await createResource({
			url: "frappe.client.get",
			params: { doctype: "Task", name: taskName },
		}).submit()
		if (res) openEditDialog(res)
	} catch (e) {
		console.error("Failed to load task for notification", e)
	}
}

watch(
	() => route.params.name,
	(newName) => {
		if (newName) openTaskByName(newName)
		else showEditTask.value = false
	},
	{ immediate: true },
)

function handleGlobalKeydown(e) {
	const isCmdOrCtrl = e.metaKey || e.ctrlKey
	if (isCmdOrCtrl && e.key.toLowerCase() === "s") {
		e.preventDefault()
		handleSaveTask()
	}
}

watch(showEditTask, (val) => {
	if (val) {
		window.addEventListener("keydown", handleGlobalKeydown)
	} else {
		window.removeEventListener("keydown", handleGlobalKeydown)
		if (route.params.name) router.push({ path: "/tasks" })
		stopVoice()
		stopAudioRecording(true)
	}
})

watch(showCreateDialog, (val) => {
	if (!val) {
		stopVoice()
		stopAudioRecording(true)
	}
})

onMounted(() => {
	fetchTasks()
	fetchTaskSummary()
	if (viewMode.value === "board") fetchAllColumns()
})

onUnmounted(() => {
	window.removeEventListener("keydown", handleGlobalKeydown)
	stopVoice()
	stopAudioRecording(true)
})
</script>

<style scoped>
.animate-slide-in {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

:deep(.ProseMirror) {
  min-height: 250px;
  outline: none;
}

:deep(.ProseMirror audio),
.editor-container :deep(audio) {
	display: block;
	max-width: 250px;
	height: 32px;
	border-radius: 9999px;
	border: 1px solid #e2e8f0;
	background-color: #f8fafc;
	outline: none;
	padding: 0;
	margin: 0.5rem 0;
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

:deep(.ProseMirror audio::-webkit-media-controls-panel),
.editor-container :deep(audio::-webkit-media-controls-panel) {
	background-color: #f8fafc;
	display: flex;
	align-items: center;
	padding: 0 8px;
}

:deep(.ProseMirror audio::-webkit-media-controls-play-button),
.editor-container :deep(audio::-webkit-media-controls-play-button) {
	background-color: #eff6ff;
	border: 1px solid #bfdbfe;
	border-radius: 50%;
	width: 22px;
	height: 22px;
	margin-right: 4px;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.2s ease;
	cursor: pointer;
}

:deep(.ProseMirror audio::-webkit-media-controls-play-button:hover),
.editor-container :deep(audio::-webkit-media-controls-play-button:hover) {
	background-color: #dbeafe;
	border-color: #93c5fd;
	transform: scale(1.05);
}

:deep(.ProseMirror audio::-webkit-media-controls-current-time-display),
.editor-container :deep(audio::-webkit-media-controls-current-time-display),
:deep(.ProseMirror audio::-webkit-media-controls-time-remaining-display),
.editor-container :deep(audio::-webkit-media-controls-time-remaining-display) {
	color: #64748b;
	font-family: ui-sans-serif, system-ui, sans-serif;
	font-size: 9px;
	font-weight: 700;
}

:deep(.ProseMirror audio::-webkit-media-controls-timeline),
.editor-container :deep(audio::-webkit-media-controls-timeline) {
	background-color: #f1f5f9;
	border-radius: 9999px;
	height: 4px;
	padding: 0;
	margin: 0 6px;
}

:deep(.ProseMirror audio::-webkit-media-controls-volume-slider),
.editor-container :deep(audio::-webkit-media-controls-volume-slider) {
	background-color: #f1f5f9;
	border-radius: 9999px;
	height: 4px;
	max-width: 40px;
}

.editor-container :deep(img),
.editor-container :deep(video),
.editor-container :deep(iframe),
.editor-container :deep(table) {
	max-width: 100% !important;
}

.editor-container :deep(img) {
	height: auto !important;
	display: block;
}

.editor-container :deep(table) {
	display: block;
	overflow-x: auto;
}

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