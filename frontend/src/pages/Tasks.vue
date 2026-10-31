<template>
  <div class="space-y-3 p-1 flex flex-col h-full overflow-hidden min-h-0">
	<div class="grid grid-cols-3 lg:grid-cols-6 gap-2 flex-shrink-0">
	  <div
		v-for="stat in kpiStats"
		:key="stat.label"
		role="button"
		tabindex="0"
		class="kpi text-left"
		:class="isStatActive(stat.label) && 'is-active'"
		:title="isStatActive(stat.label) && stat.label !== 'Total' ? 'Click to clear filter' : 'Filter by ' + stat.label"
		@click="filterByStat(stat.label)"
		@keydown.enter.prevent="filterByStat(stat.label)"
		@keydown.space.prevent="filterByStat(stat.label)"
	  >
		<div class="flex items-center justify-between gap-2">
		  <span class="truncate text-xs font-medium text-ink-gray-6">{{ stat.label }}</span>
		  <span class="h-2 w-2 shrink-0 rounded-full" :class="stat.dot"></span>
		</div>
		<div class="mt-1.5 flex h-7 items-center">
		  <div v-if="summaryLoading" class="skeleton h-5 w-10"></div>
		  <span v-else class="text-[22px] font-semibold leading-none tabular-nums text-ink-gray-9">{{ stat.value ?? 0 }}</span>
		</div>
	  </div>
	</div>

	<div class="toolbar-card flex flex-col gap-2.5 flex-shrink-0">
	  <!-- Top Row: Search & Actions -->
	  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 w-full pb-2 border-b border-outline-gray-1">
		<div class="relative w-full sm:w-80">
		  <IconSearch class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-ink-gray-4" />
		  <input
			ref="searchInputEl"
			v-model="searchQuery"
			type="text"
			placeholder="Search tasks by subject…"
			class="h-8 w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 pl-9 pr-9 text-[13px] text-ink-gray-8 outline-none transition focus:border-outline-gray-4 focus:bg-surface-white focus:ring-2 focus:ring-outline-gray-2"
		  />
		  <kbd v-if="!searchQuery" class="kbd absolute right-2 top-1/2 -translate-y-1/2" title="Press / to search">/</kbd>
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

		<div class="flex items-center gap-2 ml-auto sm:ml-0">
		  <!-- View Mode Toggle -->
		  <div class="flex bg-surface-gray-2 p-0.5 rounded-md border border-outline-gray-2">
			<button type="button" title="List view" @click="viewMode = 'list'" :class="viewBtnClass('list')">
			  <IconList class="w-3.5 h-3.5" />
			</button>
			<button type="button" title="Board view" @click="viewMode = 'board'" :class="viewBtnClass('board')">
			  <IconLayoutGrid class="w-3.5 h-3.5" />
			</button>
		  </div>

		  <!-- Group By Popover (Board view only) -->
		  <Popover v-if="viewMode === 'board'" placement="bottom-end">
			<template #target="{ open, togglePopover }">
			  <Button
				variant="outline"
				class="!text-ink-gray-6 !px-2.5 !h-8 border border-outline-gray-2 hover:bg-surface-gray-1 transition-all flex items-center gap-1.5 rounded-md text-xs font-medium"
				@click="togglePopover"
				title="Group By"
			  >
				<template #prefix><IconLayers class="w-3.5 h-3.5 text-ink-gray-5" /></template>
				<span>Group By: {{ getGroupByLabel(groupBy) }}</span>
			  </Button>
			</template>
			<template #body-main="{ close }">
			  <div class="w-36 p-1 bg-surface-white rounded-lg shadow-md border border-outline-gray-2 text-xs space-y-0.5">
				<button 
				  v-for="opt in GROUP_BY_OPTIONS" 
				  :key="opt.value"
				  @click="groupBy = opt.value; close()"
				  :class="[
					'w-full text-left px-2.5 py-1.5 rounded text-xs transition-colors cursor-pointer flex items-center justify-between',
					groupBy === opt.value
					  ? 'bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)] font-medium'
					  : 'text-ink-gray-7 hover:bg-surface-gray-1'
				  ]"
				>
				  <span>{{ opt.label }}</span>
				  <IconCheck v-if="groupBy === opt.value" class="w-3.5 h-3.5 text-[color:var(--brand-text,#0A84D0)]" />
				</button>
			  </div>
			</template>
		  </Popover>

		  <!-- Dynamic Multi-Field Filter Popover -->
		  <Popover placement="bottom-end">
			<template #target="{ open, togglePopover }">
			  <Button
				variant="outline"
				:class="[
				  '!px-2.5 !h-8 border transition-all flex items-center gap-1.5 rounded-md text-xs font-medium',
				  activeFilterCount > 0
					? 'border-[color:var(--brand,#29ADFF)] text-[color:var(--brand-text,#0A84D0)] bg-[color:var(--brand-soft,#E9F6FF)]'
					: '!text-ink-gray-6 border-outline-gray-2 hover:bg-surface-gray-1'
				]"
				@click="syncActiveFilterRules(); togglePopover()"
				title="Filter Tasks"
			  >
				<template #prefix><IconFilter class="w-3.5 h-3.5" :class="activeFilterCount > 0 ? 'text-[color:var(--brand-text,#0A84D0)]' : 'text-ink-gray-5'" /></template>
				<span>Filter</span>
				<span v-if="activeFilterCount > 0" class="bg-[color:var(--brand,#29ADFF)] text-white rounded-full text-[10px] font-bold px-1.5 py-0.2 leading-none">
				  {{ activeFilterCount }}
				</span>
			  </Button>
			</template>
			<template #body-main="{ close }">
			  <div class="w-80 p-3 bg-surface-white rounded-lg shadow-lg border border-outline-gray-2 text-xs space-y-3">
				<div class="flex items-center justify-between pb-2 border-b border-outline-gray-1">
				  <div class="flex items-center gap-1.5 font-semibold text-ink-gray-8 text-xs">
					<IconFilter class="w-3.5 h-3.5 text-[color:var(--brand-text,#0A84D0)]" />
					<span>Filter Tasks</span>
				  </div>
				  <button 
					v-if="hasActiveFilters"
					@click="clearFilters" 
					class="text-[11px] font-medium text-red-600 hover:text-red-700 flex items-center gap-1 cursor-pointer"
				  >
					<IconX class="w-3 h-3" /> Clear All
				  </button>
				</div>

				<!-- Dynamic Filter Rules -->
				<div class="space-y-2 max-h-60 overflow-y-auto custom-scrollbar pr-1">
				  <div 
					v-for="rule in activeFilterRules" 
					:key="rule.id"
					class="flex items-center gap-1.5 bg-surface-gray-1 p-1.5 rounded-md border border-outline-gray-2"
				  >
					<div class="w-1/3 shrink-0">
					  <Select 
						v-model="rule.field"
						:options="FILTERABLE_FIELDS"
						placeholder="Field"
						size="sm"
						variant="subtle"
						@update:modelValue="rule.value = ''"
					  />
					</div>

					<span class="text-[10px] font-semibold text-ink-gray-4 shrink-0">=</span>

					<div class="flex-1 min-w-0">
					  <Select
						v-model="rule.value"
						:options="getFieldOptionsForSelect(rule.field)"
						placeholder="Select value"
						size="sm"
						variant="subtle"
						class="w-full"
					  />
					</div>

					<button 
					  @click="removeFilterRule(rule.id)"
					  class="p-1 hover:bg-red-50 rounded text-ink-gray-4 hover:text-red-500 transition-colors shrink-0 cursor-pointer"
					  title="Remove Filter"
					>
					  <IconX class="w-3.5 h-3.5" />
					</button>
				  </div>
				</div>

				<div class="flex items-center justify-between pt-2 border-t border-outline-gray-1">
				  <button
					@click="addFilterRule"
					class="inline-flex items-center gap-1 text-xs font-medium text-[color:var(--brand-text,#0A84D0)] hover:text-[color:var(--brand-hover,#0F9EF5)] px-2 py-1 rounded transition-colors cursor-pointer"
				  >
					<IconPlus class="w-3.5 h-3.5" /> Add Filter
				  </button>

				  <Button 
					variant="solid" 
					class="brand-btn !px-3 !h-7 text-xs font-medium rounded-md"
					@click="applyFilterRules(); close()"
				  >
					Apply
				  </Button>
				</div>
			  </div>
			</template>
		  </Popover>

		  <!-- Column Picker Popover (Frappe UI Style) -->
		  <Popover v-if="viewMode === 'list'" placement="bottom-end">
			<template #target="{ open, togglePopover }">
			  <Button
				variant="outline"
				class="!text-ink-gray-6 !px-2.5 !h-8 border border-outline-gray-2 hover:bg-surface-gray-1 transition-all flex items-center gap-1.5 rounded-md text-xs font-medium"
				@click="togglePopover"
				title="Customize Columns"
			  >
				<template #prefix><IconSlidersHorizontal class="w-3.5 h-3.5 text-ink-gray-5" /></template>
				<span class="hidden md:inline">Columns</span>
			  </Button>
			</template>
			<template #body-main="{ close }">
			  <div class="w-60 p-3 bg-surface-white rounded-lg shadow-lg border border-outline-gray-2 text-xs space-y-2.5">
				<div class="flex items-center justify-between pb-2 border-b border-outline-gray-1">
				  <span class="font-semibold text-ink-gray-8 text-xs">Columns</span>
				  <button 
					@click="resetColumns" 
					class="text-[11px] font-medium text-[color:var(--brand-text,#0A84D0)] hover:text-[color:var(--brand-hover,#0F9EF5)] flex items-center gap-1 cursor-pointer"
					title="Reset to default columns"
				  >
					<IconRotateCcw class="w-3 h-3" /> Reset
				  </button>
				</div>

				<div class="relative">
				  <input
					v-model="columnSearchQuery"
					type="text"
					placeholder="Search columns..."
					class="w-full pl-7 pr-2 py-1 text-xs bg-surface-gray-1 border border-outline-gray-2 rounded-md focus:bg-surface-white focus:outline-none focus:ring-1 focus:ring-[color:var(--brand,#29ADFF)]"
				  />
				  <IconSearch class="w-3 h-3 absolute left-2 top-2 text-ink-gray-4" />
				</div>

				<div class="max-h-60 overflow-y-auto space-y-0.5 custom-scrollbar pr-1">
				  <div 
					v-for="(colKey, index) in activeColumnKeys" 
					:key="colKey"
					v-show="!columnSearchQuery || getColumnLabel(colKey).toLowerCase().includes(columnSearchQuery.toLowerCase())"
					class="flex items-center justify-between p-1 rounded hover:bg-surface-gray-1 group transition-all"
				  >
					<label class="flex items-center gap-2 cursor-pointer select-none truncate flex-1 mr-1">
					  <input
						type="checkbox"
						:checked="true"
						:disabled="colKey === 'subject'"
						@change="toggleColumn(colKey)"
						class="rounded text-[color:var(--brand-text,#0A84D0)] focus:ring-[color:var(--brand,#29ADFF)] h-3.5 w-3.5 cursor-pointer disabled:opacity-40"
					  />
					  <span :class="colKey === 'subject' ? 'font-semibold text-ink-gray-9' : 'text-ink-gray-7'" class="truncate">
						{{ getColumnLabel(colKey) }}
					  </span>
					  <span v-if="colKey === 'subject'" class="text-[9px] bg-surface-gray-2 text-ink-gray-4 px-1 rounded font-medium ml-auto">Fixed</span>
					</label>

					<div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
					  <button
						@click.stop="moveColumnUp(index)"
						:disabled="index === 0"
						class="p-0.5 hover:bg-surface-gray-3 rounded text-ink-gray-5 disabled:opacity-20 cursor-pointer"
						title="Move Up"
					  >
						<IconArrowUp class="w-3 h-3" />
					  </button>
					  <button
						@click.stop="moveColumnDown(index)"
						:disabled="index === activeColumnKeys.length - 1"
						class="p-0.5 hover:bg-surface-gray-3 rounded text-ink-gray-5 disabled:opacity-20 cursor-pointer"
						title="Move Down"
					  >
						<IconArrowDown class="w-3 h-3" />
					  </button>
					</div>
				  </div>

				  <!-- Inactive columns available to add -->
				  <div v-if="inactiveColumns.length > 0 && !columnSearchQuery" class="pt-2 border-t border-outline-gray-1 mt-1">
					<span class="text-[10px] font-medium text-ink-gray-4 uppercase tracking-wider block mb-1">More Columns</span>
					<div
					  v-for="col in inactiveColumns"
					  :key="col.key"
					  class="flex items-center justify-between p-1 rounded hover:bg-surface-gray-1 cursor-pointer"
					  @click="toggleColumn(col.key)"
					>
					  <label class="flex items-center gap-2 cursor-pointer select-none truncate">
						<input
						  type="checkbox"
						  :checked="false"
						  @change="toggleColumn(col.key)"
						  class="rounded text-[color:var(--brand-text,#0A84D0)] focus:ring-[color:var(--brand,#29ADFF)] h-3.5 w-3.5 cursor-pointer"
						/>
						<span class="text-ink-gray-5 truncate">{{ col.label }}</span>
					  </label>
					</div>
				  </div>
				</div>
			  </div>
			</template>
		  </Popover>

		  <!-- Refresh Button -->
		  <Button
			variant="outline"
			class="!text-ink-gray-6 !px-2.5 !h-8 border border-outline-gray-2 hover:bg-surface-gray-1 transition-all rounded-md"
			title="Refresh"
			@click="refreshAll()"
		  >
			<template #prefix><IconRefresh class="w-3.5 h-3.5 text-ink-gray-5" :class="tasksResource.loading && 'animate-spin'" /></template>
		  </Button>

		  <!-- Selection info -->
		  <div v-if="isAdmin && selectedTasks.size > 0" class="flex h-8 items-center gap-1 rounded-md bg-surface-gray-2 pl-2.5 pr-1 text-xs text-ink-gray-7">
			<span class="font-medium tabular-nums">{{ selectedTasks.size }} selected</span>
			<button type="button" class="rounded p-1 text-ink-gray-5 hover:bg-surface-gray-3 hover:text-ink-gray-8" title="Clear selection" @click="clearSelection">
			  <IconX class="h-3.5 w-3.5" />
			</button>
		  </div>

		  <!-- Actions Dropdown / New Task Button -->
		  <Dropdown
			v-slot="{ open }"
			v-if="isAdmin && selectedTasks.size > 0"
			:options="actionsOptions"
		  >
			<Button
			  variant="solid"
			  class="!text-xs !px-3 !h-8 rounded-md font-medium"
			>
			  Actions
			  <template #suffix><FeatherIcon name="chevron-down" class="w-3.5 h-3.5 shrink-0" /></template>
			</Button>
		  </Dropdown>

		  <Button
			v-else
			variant="solid"
			class="brand-btn !text-xs !px-4 !h-8 rounded-md font-medium"
			@click="openCreateDialog"
		>
			<template #prefix><IconPlus class="w-3.5 h-3.5" /></template>
			New Task
		</Button>

		</div>
	  </div>

	  <!-- Active Filter Chips Bar -->
	  <div v-if="hasActiveFilterChips" class="flex flex-wrap items-center gap-1.5 pt-1.5 border-t border-outline-gray-1">
		<span class="text-[10px] font-bold text-ink-gray-4 uppercase tracking-wider">Active Filters:</span>
		
		<span 
		  v-for="chip in activeFilterChips" 
		  :key="chip.key"
		  class="inline-flex items-center gap-1.5 bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)] border border-[color:var(--brand-border,#A6DCFF)] px-2 py-0.5 rounded-md text-xs font-medium transition-all"
		>
		  <span class="text-[color:var(--brand-text,#0A84D0)] font-normal">{{ chip.label }}:</span>
		  <span class="font-semibold">{{ chip.displayValue }}</span>
		  <button 
			@click="removeFilterByKey(chip.key)" 
			class="hover:bg-[color:var(--brand-border,#A6DCFF)] rounded p-0.5 text-[color:var(--brand-text,#0A84D0)] hover:text-[color:var(--brand-hover,#0F9EF5)] transition-colors ml-0.5 cursor-pointer"
			title="Remove filter"
		  >
			<IconX class="w-3 h-3" />
		  </button>
		</span>

		<button 
		  @click="clearFilters" 
		  class="text-xs font-bold text-red-500 hover:text-red-700 hover:underline px-1 py-0.5 cursor-pointer ml-1"
		>
		  Clear All
		</button>
	  </div>

	  <!-- Bottom Row: Quick Filter Bar -->
	  <div class="filter-row flex flex-nowrap overflow-x-auto pb-1 gap-2 w-full custom-scrollbar sm:flex-wrap sm:overflow-visible sm:pb-0 sm:items-center sm:gap-2">
		<!-- Quick Filter: Assigned to Me -->
		<button
		  type="button"
		  :class="['qf qf-auto', selectedFilters.assigned_to === session.user && 'on']"
		  title="Filter tasks assigned to me"
		  @click="toggleAssignedToMe"
		>
		  <IconUser class="h-3.5 w-3.5 shrink-0" />
		  <span>Assigned to Me</span>
		</button>
		<!-- Searchable non-static filter: Project -->
		<div class="w-36 shrink-0">
			<Autocomplete
			  ref="projectAutocomplete"
			  :options="projectResource?.data || []"
			  :modelValue="selectedFilters.project"
			  @update:modelValue="val => selectedFilters.project = val?.value ?? val ?? ''"
			  :compare-fn="compareOption"
			  :max-options="100"
			>
			  <template #target>
				<button
				  type="button"
				  @click="() => projectAutocomplete?.togglePopover()"
				  :class="['qf', selectedFilters.project !== '' && 'on']"
				>
				  <span class="truncate">{{ getProjectLabel(selectedFilters.project) }}</span>
				  <FeatherIcon name="chevron-down" class="size-3.5 opacity-60 ml-auto shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<!-- Searchable non-static filter: Department -->
		<div class="w-36 shrink-0">
			<Autocomplete
			  ref="departmentAutocomplete"
			  :options="departmentResource?.data || []"
			  :modelValue="selectedFilters.department"
			  @update:modelValue="val => selectedFilters.department = val?.value ?? val ?? ''"
			  :compare-fn="compareOption"
			  :max-options="100"
			>
			  <template #target>
				<button
				  type="button"
				  @click="() => departmentAutocomplete?.togglePopover()"
				  :class="['qf', selectedFilters.department !== '' && 'on']"
				>
				  <span class="truncate">{{ getDepartmentLabel(selectedFilters.department) }}</span>
				  <FeatherIcon name="chevron-down" class="size-3.5 opacity-60 ml-auto shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<!-- Searchable non-static filter: Status -->
		<div class="w-36 shrink-0">
			<Autocomplete
			  ref="statusAutocomplete"
			  :options="filterStatusOptions"
			  :modelValue="selectedFilters.status"
			  @update:modelValue="val => selectedFilters.status = val?.value ?? val ?? ''"
			  :compare-fn="compareOption"
			>
			  <template #target>
				<button
				  type="button"
				  @click="() => statusAutocomplete?.togglePopover()"
				  :class="['qf', selectedFilters.status !== '' && 'on']"
				>
				  <span class="truncate">{{ getStatusLabel(selectedFilters.status) }}</span>
				  <FeatherIcon name="chevron-down" class="size-3.5 opacity-60 ml-auto shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<!-- Searchable non-static filter: Priority -->
		<div class="w-36 shrink-0">
			<Autocomplete
			  ref="priorityAutocomplete"
			  :options="priorityOptions"
			  :modelValue="selectedFilters.priority"
			  @update:modelValue="val => selectedFilters.priority = val?.value ?? val ?? ''"
			  :compare-fn="compareOption"
			>
			  <template #target>
				<button
				  type="button"
				  @click="() => priorityAutocomplete?.togglePopover()"
				  :class="['qf', selectedFilters.priority !== '' && 'on']"
				>
				  <span class="truncate">{{ getPriorityLabel(selectedFilters.priority) }}</span>
				  <FeatherIcon name="chevron-down" class="size-3.5 opacity-60 ml-auto shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<!-- Searchable non-static filter: Assigned By -->
		<div class="w-36 shrink-0">
			<Autocomplete
			  ref="assignedByAutocomplete"
			  :options="userResource?.data || []"
			  :modelValue="selectedFilters.assigned_by"
			  @update:modelValue="val => selectedFilters.assigned_by = val?.value ?? val ?? ''"
			  :compare-fn="compareOption"
			  :max-options="100"
			>
			  <template #target>
				<button
				  type="button"
				  @click="() => assignedByAutocomplete?.togglePopover()"
				  :class="['qf', selectedFilters.assigned_by !== '' && 'on']"
				>
				  <span class="truncate">{{ getUserLabel(selectedFilters.assigned_by, 'Assigned By') }}</span>
				  <FeatherIcon name="chevron-down" class="size-3.5 opacity-60 ml-auto shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<!-- Searchable non-static filter: Assigned To -->
		<div class="w-36 shrink-0">
			<Autocomplete
			  ref="assignedToAutocomplete"
			  :options="userResource?.data || []"
			  :modelValue="selectedFilters.assigned_to"
			  @update:modelValue="val => selectedFilters.assigned_to = val?.value ?? val ?? ''"
			  :compare-fn="compareOption"
			  :max-options="100"
			>
			  <template #target>
				<button
				  type="button"
				  @click="() => assignedToAutocomplete?.togglePopover()"
				  :class="['qf', selectedFilters.assigned_to !== '' && 'on']"
				>
				  <span class="truncate">{{ getUserLabel(selectedFilters.assigned_to, 'Assigned To') }}</span>
				  <FeatherIcon name="chevron-down" class="size-3.5 opacity-60 ml-auto shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<!-- Searchable non-static filter: Deadline -->
		<div class="w-36 shrink-0">
			<Autocomplete
			  ref="deadlineAutocomplete"
			  :options="deadlineOptions.filter(d => d.value !== '')"
			  :modelValue="selectedFilters.deadline"
			  @update:modelValue="val => selectedFilters.deadline = val?.value ?? val ?? ''"
			  :compare-fn="compareOption"
			>
			  <template #target>
				<button
				  type="button"
				  @click="() => deadlineAutocomplete?.togglePopover()"
				  :class="['qf', selectedFilters.deadline !== '' && 'on']"
				>
				  <span class="truncate">{{ getDeadlineLabel(selectedFilters.deadline) }}</span>
				  <FeatherIcon name="chevron-down" class="size-3.5 opacity-60 ml-auto shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<Button 
		  v-if="hasActiveFilters"
		  variant="ghost" 
		  class="!text-red-500 hover:!bg-red-50 !px-2 !h-7 text-xs font-medium shrink-0"
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
	  <div v-if="viewMode === 'list'" class="relative bg-surface-white rounded-xl border border-outline-gray-2 shadow-sm flex flex-col min-h-[420px] md:min-h-0 md:flex-1 md:overflow-hidden">
		  <div v-if="tasksResource.loading" class="busy-bar" aria-hidden="true"></div>
		  <ListView
			class="h-full flex flex-col min-h-0"
			:columns="columns"
			:rows="filteredTasksData || []" 
			:options="{
			  selectable: isAdmin,
			  showTooltip: true,
			  resizeColumn: true,
			  onRowClick: (row) => openEditDialog(row),
			  emptyState: {
				title: hasActiveFilters ? 'No tasks match your filters' : 'No tasks yet',
				description: hasActiveFilters ? 'Try removing a filter or clearing the search.' : 'Create your first task with the New Task button.',
			  },
			}"
			row-key="name"
			v-model:selections="selectedTasks"
		  >
			<ListHeader class="shrink-0 bg-surface-gray-1 border-b border-outline-gray-2 shadow-sm">
			  <ListHeaderItem v-for="col in columns" :key="col.key" :item="col">
				<template #prefix="{ item }">
				  <component :is="item.icon" class="size-3.5 text-ink-gray-4" />
				</template>
			  </ListHeaderItem>
			</ListHeader>
			<div class="flex-grow md:flex-1 overflow-y-auto custom-scrollbar relative min-h-0 max-h-[480px] md:max-h-none">
			<ListRows>
			  <ListRow v-for="row in (filteredTasksData || [])" :key="row.name" v-slot="{ column, item }" :row="row">
				<ListRowItem :item="item">
				  <template v-if="column.key === 'subject'" #prefix>
					<div class="flex items-center -space-x-1.5 mr-2.5 isolate">
						<Avatar 
							v-for="(assignment, index) in (row.assigned_to || []).slice(0, 3)" 
							:key="index"
							:image="getUserAvatarImage(assignment)"
							:label="getUserLabel(assignment)"
							size="md"
							class="avatar-ring rounded-full"
							v-tooltip="getUserLabel(assignment)"
						/>
						
						<div 
							v-if="row.assigned_to?.length > 3" 
							class="avatar-ring flex items-center justify-center h-6 w-6 rounded-full bg-surface-gray-3 text-[10px] font-semibold text-ink-gray-6 z-10"
						>
							+{{ row.assigned_to.length - 3 }}
						</div>
					</div>					
				  </template>
				  <template v-if="column.key === 'priority'">
					<Badge :theme="getPriorityTheme(item)" variant="subtle" :label="item" />
				  </template>
				  <template v-if="column.key === 'status'">
					<div class="flex min-w-0 items-center gap-1.5">
						<span class="status-pill" :class="getStatusPillClass(item)">
							<span class="h-1.5 w-1.5 shrink-0 rounded-full" :class="getStatusColor(item)" />
							<span class="truncate">{{ item }}</span>
						</span>
						<span v-if="row.is_overdue && item !== 'Completed' && item !== 'Overdue'" class="text-[11px] font-medium text-ink-red-4">Overdue</span>
					</div>
				  </template>
				  <template v-if="column.key === 'description_for_list'">
					<div 
						class="max-w-[600px] truncate text-ink-gray-5 text-sm" 
						v-tooltip="item"
					>
						{{ item || '—' }}
					</div>
				  </template>
				  <template v-if="column.key === 'assigned_datetime'">
						<div class="flex items-center gap-2 text-ink-gray-5">
							<IconClock class="w-3.5 h-3.5" v-if="row.assigned_datetime"/>
							<span class="text-xs font-medium">
								{{ row.assigned_datetime ? formatDateTime(row.assigned_datetime) : '' }}
							</span>
						</div>
				  </template>
				  <template v-if="column.key === 'exp_end_date'">
						<span v-if="row.exp_end_date" class="inline-flex items-center gap-1.5 text-xs" :class="dueInfo(row).cls" :title="formatDate(row.exp_end_date)">
							<IconClock class="w-3.5 h-3.5 shrink-0" />{{ dueInfo(row).text }}
						</span>
						<span v-else class="text-xs text-ink-gray-4">—</span>
				  </template>
				  <template v-if="column.key === 'tactix_team'">
						<span class="text-xs text-ink-gray-6 font-medium truncate">
							{{ getTeamLabel(row.tactix_team) }}
						</span>
				  </template>
				  <template v-if="column.key === 'assigned_by'">
						<span class="text-xs text-ink-gray-6 font-medium truncate">
							{{ getUserLabel(row.assigned_by) }}
						</span>
				  </template>
				  <template v-if="column.key === 'completed_by'">
						<span class="text-xs text-ink-gray-6 font-medium truncate">
							{{ row.completed_by ? getUserLabel(row.completed_by) : '—' }}
						</span>
				  </template>
				  <template v-if="column.key === 'expected_time'">
						<span class="text-xs text-ink-gray-6 font-medium truncate">
							{{ row.expected_time ? row.expected_time + ' hrs' : '—' }}
						</span>
				  </template>
				  <template v-if="column.key === 'name'">
						<span class="font-mono text-[11px] font-medium text-ink-gray-6 bg-surface-gray-2 px-1.5 py-0.5 rounded">
							{{ row.name }}
						</span>
				  </template>
				  <template v-if="column.key === 'has_unseen_comments'">
					<div class="flex justify-end pr-2">
						<div 
							v-if="row.has_unseen_comments && row.has_unseen_comments > 0" 
							class="flex items-center gap-1 text-ink-red-4 bg-surface-red-1 px-1.5 py-0.5 rounded-md"
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
		<!-- Pagination Bar -->
		<div class="flex items-center justify-between border-t border-outline-gray-1 bg-surface-white px-4 py-2 shrink-0">
		  <div class="flex items-center gap-1">
			<!-- First Page (<<) -->
			<Button
			  variant="ghost"
			  size="sm"
			  :disabled="currentPage === 1"
			  @click="currentPage = 1"
			  title="First Page"
			  class="!p-1 !h-6 text-ink-gray-5 hover:text-ink-gray-8 disabled:opacity-30"
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
			  class="!p-1 !h-6 text-ink-gray-5 hover:text-ink-gray-8 disabled:opacity-30"
			>
			  <template #prefix><IconChevronLeft class="w-3.5 h-3.5" /></template>
			</Button>

			<!-- Compact Popover Page Selector -->
			<Popover>
			  <template #target="{ togglePopover }">
				<button
				  @click="togglePopover"
				  class="h-6 px-2 text-[11px] font-bold text-ink-gray-7 hover:bg-surface-gray-2 rounded border border-outline-gray-2 transition-all flex items-center gap-1 cursor-pointer shrink-0"
				>
				  <span>{{ currentPage }} / {{ totalPages }}</span>
				  <IconChevronDown class="w-3 h-3 text-ink-gray-4" />
				</button>
			  </template>
			  <template #body="{ close }">
				<div class="p-1 max-h-48 overflow-y-auto w-32 bg-surface-white rounded-lg shadow-lg border border-outline-gray-2 custom-scrollbar">
				  <button
					v-for="p in totalPages"
					:key="p"
					@click="currentPage = p; close()"
					:class="[
					  'w-full text-left px-2 py-1 text-xs rounded transition-colors cursor-pointer flex items-center justify-between',
					  currentPage === p
						? 'bg-[color:var(--brand,#29ADFF)] text-white font-semibold'
						: 'text-ink-gray-7 hover:bg-surface-gray-2'
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
			  class="!p-1 !h-6 text-ink-gray-5 hover:text-ink-gray-8 disabled:opacity-30"
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
			  class="!p-1 !h-6 text-ink-gray-5 hover:text-ink-gray-8 disabled:opacity-30"
			>
			  <template #prefix><IconChevronsRight class="w-3.5 h-3.5" /></template>
			</Button>
		  </div>

		  <div class="text-xs text-ink-gray-5 font-medium">
			Showing <span class="font-bold text-ink-gray-8">{{ totalCount > 0 ? (currentPage - 1) * pageLength + 1 : 0 }} - {{ Math.min(currentPage * pageLength, totalCount) }}</span> of <span class="font-bold text-ink-gray-8">{{ totalCount }}</span>
		  </div>
		</div>
	  </div>

	  <div v-if="viewMode === 'board'" class="flex-1 flex gap-3 overflow-x-auto pb-2 custom-scrollbar min-h-0">
		<div
			v-for="col in activeGroupColumns"
			:key="col.value"
			class="board-col"
			:class="hoveredColumn === col.value && 'is-over'"
			@dragover.prevent
			@dragenter.prevent="onDragEnter(col.value)"
			@dragleave="onDragLeave"
			@drop="onDrop($event, col.value)"
		>
		  <div class="flex items-center justify-between gap-2 px-1.5 pb-2.5 pt-0.5 shrink-0">
			<div class="flex min-w-0 items-center gap-2">
			  <span class="h-2 w-2 shrink-0 rounded-full" :class="groupDotClass(col.value)"></span>
			  <h3 class="truncate text-[13px] font-semibold text-ink-gray-8" :title="col.label">{{ col.label }}</h3>
			</div>
			<span class="rounded-full bg-surface-gray-3 px-1.5 text-[11px] font-semibold leading-5 tabular-nums text-ink-gray-6">
			  {{ filteredTasks(col.value).length }}{{ columnHasMore[col.value] ? '+' : '' }}
			</span>
		  </div>

		  <div class="flex-1 space-y-2 overflow-y-auto px-0.5 pb-1 custom-scrollbar min-h-0" @scroll="handleColumnScroll($event, col.value)">
			<div
			  v-for="task in filteredTasks(col.value)"
			  :key="task.name"
			  draggable="true"
			  class="board-card"
			  :class="draggedTask?.name === task.name && 'is-dragging'"
			  @click="openEditDialog(task)"
			  @dragstart="onDragStart($event, task)"
			  @dragend="onDragEnd"
			>
			  <div class="flex items-center justify-between gap-2">
				<span class="font-mono text-[10.5px] text-ink-gray-4">{{ task.name }}</span>
				<span
				  v-if="task.has_unseen_comments > 0"
				  class="flex items-center gap-1 rounded bg-surface-red-1 px-1 text-[10px] font-semibold text-ink-red-4"
				  title="Unseen comments"
				>
				  <IconMessageSquare class="h-3 w-3" />{{ task.has_unseen_comments }}
				</span>
			  </div>
			  <div class="mt-1 line-clamp-2 text-[13px] font-medium leading-snug text-ink-gray-9" :title="task.subject">{{ task.subject }}</div>
			  <div v-if="task.project_name || task.project" class="mt-1 truncate text-xs text-ink-gray-5">
				{{ task.project_name || getProjectLabel(task.project) }}
			  </div>

			  <div class="mt-3 flex items-center justify-between gap-2">
				<div class="flex items-center -space-x-1.5">
				  <Avatar
					v-for="(assignment, index) in (task.assigned_to || []).slice(0, 3)"
					:key="index"
					:image="getUserAvatarImage(assignment)"
					:label="getUserLabel(assignment)"
					size="sm"
					class="avatar-ring rounded-full"
					v-tooltip="getUserLabel(assignment)"
				  />
				  <span
					v-if="task.assigned_to?.length > 3"
					class="avatar-ring grid h-5 w-5 place-items-center rounded-full bg-surface-gray-3 text-[9px] font-semibold text-ink-gray-6"
				  >+{{ task.assigned_to.length - 3 }}</span>
				  <span v-if="!task.assigned_to?.length" class="text-[11px] text-ink-gray-4">Unassigned</span>
				</div>
				<div class="flex shrink-0 items-center gap-1">
				  <Badge v-if="groupBy !== 'status'" variant="subtle" :theme="getStatusTheme(task.status)" size="sm">{{ task.status }}</Badge>
				  <Badge v-if="groupBy !== 'priority' && task.priority" variant="subtle" :theme="getPriorityTheme(task.priority)" size="sm">{{ task.priority }}</Badge>
				</div>
			  </div>

			  <div v-if="task.exp_end_date" class="mt-2.5 flex items-center gap-1 border-t border-outline-gray-1 pt-2 text-[11px]" :class="dueInfo(task).cls">
				<IconClock class="h-3 w-3 shrink-0" /> {{ dueInfo(task).text }}
			  </div>
			</div>

			<template v-if="columnLoading[col.value]">
			  <div v-for="n in (filteredTasks(col.value).length ? 1 : 3)" :key="'sk' + n" class="board-card pointer-events-none space-y-2">
				<div class="skeleton h-2.5 w-16"></div>
				<div class="skeleton h-3.5 w-4/5"></div>
				<div class="skeleton h-3 w-1/2"></div>
			  </div>
			</template>

			<div
			  v-if="filteredTasks(col.value).length === 0 && !columnLoading[col.value]"
			  class="grid h-20 place-items-center rounded-lg border border-dashed border-outline-gray-2 text-xs text-ink-gray-4"
			>
			  {{ hoveredColumn === col.value ? 'Drop here' : 'No tasks' }}
			</div>
		  </div>
		</div>
	  </div>
	</div>

	<Dialog v-model="showBulkDeleteDialog" 
		:disable-outside-click-to-close="true"
		:options="bulkDeleteDialogOptions">
	  <template #body-content>
		<p class="text-sm text-ink-gray-6 leading-relaxed py-2">
		  Are you sure you want to permanently delete the <span class="font-bold text-ink-gray-9">{{ selectedTasks.size }}</span> selected task(s)? This action cannot be undone.
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
		:options="createTaskDialogOptions">
	  <template #body-content>
		<div v-if="showCreateDialog" class="space-y-6 py-2">
		  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
			<div class="space-y-4">
			  <FormControl type="text" label="Subject *" v-model="newTask.subject" />

			  <div class="space-y-1.5">
				<label class="block text-xs text-ink-gray-5">Project</label>
				<Autocomplete
				  ref="createProjectAutocomplete"
				  :options="projectResource.data || []"
				  :modelValue="newTask.project"
				  @update:modelValue="val => newTask.project = val?.value ?? val ?? ''"
				  :compare-fn="compareOption"
				  :max-options="100"
				>
				  <template #target>
					<button
					  type="button"
					  @click="() => createProjectAutocomplete?.togglePopover()"
					  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
					>
					  <span class="truncate">{{ getProjectLabel(newTask.project) }}</span>
					  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
					</button>
				  </template>
				</Autocomplete>
			  </div>

			  <div class="space-y-1.5">
				<label class="block text-xs text-ink-gray-5">Department</label>
				<Autocomplete
				  ref="createDepartmentAutocomplete"
				  :options="departmentResource.data || []"
				  :modelValue="newTask.department"
				  @update:modelValue="val => newTask.department = val?.value ?? val ?? ''"
				  :compare-fn="compareOption"
				  :max-options="100"
				>
				  <template #target>
					<button
					  type="button"
					  @click="() => createDepartmentAutocomplete?.togglePopover()"
					  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
					>
					  <span class="truncate">{{ getDepartmentLabel(newTask.department) }}</span>
					  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
					</button>
				  </template>
				</Autocomplete>
			  </div>

			  <div class="space-y-1.5">
				<label class="block text-xs text-ink-gray-5">Status</label>
				<Autocomplete
				  ref="createStatusAutocomplete"
				  :options="statusOptions"
				  :modelValue="newTask.status"
				  @update:modelValue="val => newTask.status = val?.value ?? val ?? ''"
				  :compare-fn="compareOption"
				>
				  <template #target>
					<button
					  type="button"
					  @click="() => createStatusAutocomplete?.togglePopover()"
					  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
					>
					  <span class="truncate">{{ getStatusLabel(newTask.status) }}</span>
					  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
					</button>
				  </template>
				</Autocomplete>
			  </div>
			</div>
			<div class="space-y-4">
			  <div class="space-y-1.5">
				<label class="block text-xs text-ink-gray-5">Priority</label>
				<Autocomplete
				  ref="createPriorityAutocomplete"
				  :options="priorityOptions"
				  :modelValue="newTask.priority"
				  @update:modelValue="val => newTask.priority = val?.value ?? val ?? ''"
				  :compare-fn="compareOption"
				>
				  <template #target>
					<button
					  type="button"
					  @click="() => createPriorityAutocomplete?.togglePopover()"
					  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
					>
					  <span class="truncate">{{ getPriorityLabel(newTask.priority) }}</span>
					  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
					</button>
				  </template>
				</Autocomplete>
			  </div>

			  <div class="space-y-1.5">
				<label class="block text-xs text-ink-gray-5">Team</label>
				<Autocomplete
				  ref="createTeamAutocomplete"
				  :options="tactixTeamResource.data || []"
				  :modelValue="newTask.tactix_team"
				  @update:modelValue="val => newTask.tactix_team = val?.value ?? val ?? ''"
				  :compare-fn="compareOption"
				  :max-options="100"
				>
				  <template #target>
					<button
					  type="button"
					  @click="() => createTeamAutocomplete?.togglePopover()"
					  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
					>
					  <span class="truncate">{{ getTeamLabel(newTask.tactix_team) }}</span>
					  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
					</button>
				  </template>
				</Autocomplete>
			  </div>

			  <DatePicker label="Start Date" v-model="newTask.assigned_date" />
			  <DatePicker label="Deadline" v-model="newTask.exp_end_date" />
			</div>
			<div class="space-y-4">
			  <div class="space-y-1.5">
				<label class="block text-xs text-ink-gray-5">Assigned By</label>
				<Autocomplete
				  ref="createAssignedByAutocomplete"
				  :options="userResource.data || []"
				  :modelValue="newTask.assigned_by"
				  @update:modelValue="val => newTask.assigned_by = val?.value ?? val ?? ''"
				  :compare-fn="compareOption"
				  :max-options="100"
				>
				  <template #target>
					<button
					  type="button"
					  :disabled="isFieldDisabled"
					  @click="() => createAssignedByAutocomplete?.togglePopover()"
					  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
					>
					  <span class="truncate">{{ getUserLabel(newTask.assigned_by, 'Select User') }}</span>
					  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
					</button>
				  </template>
				</Autocomplete>
			  </div>
			   	<label class="block text-xs text-ink-gray-5">Assigned To</label>
				<MultiSelect
					:options="assignedToOptions"
					v-model="newTask.assigned_to"
					style="margin-top: 5px;"
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
			<label class="text-xs font-medium text-ink-gray-6 uppercase">Attachments</label>
			<div class="border rounded-lg overflow-hidden border-outline-gray-2">
			  <table class="w-full text-left text-sm">
				<thead class="bg-surface-gray-1 border-b border-outline-gray-2">
				  <tr>
					<th class="px-4 py-2">File Name</th>
					<th class="px-4 py-2 text-right"></th>
				  </tr>
				</thead>
				<tbody class="divide-y divide-outline-gray-1 bg-surface-white">
				  <tr v-for="(file, index) in newTask.attachments" :key="index">
					<td class="px-4 py-2">
					  <a :href="file.file_url" target="_blank" class="text-[color:var(--brand-text,#0A84D0)] flex items-center gap-2">
						<IconPaperclip class="w-3.5 h-3.5" /> {{ file.file_name }}
					  </a>
					</td>
					<td class="px-4 py-2 text-right">
					  <Button variant="ghost" @click="removeAttachment(index)" class="!text-red-500">
						<IconX class="w-4 h-4" />
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
			  <label class="text-xs font-medium text-ink-gray-6 uppercase tracking-wider">Task Description</label>
			  <!-- Voice Controls -->
			  <div class="flex items-center gap-2">
				<!-- Speech-to-text Info -->
				<span v-if="activeEditorKey === 'dialog' && interimText" class="text-xs text-ink-gray-4 italic truncate max-w-[180px]">"{{ interimText }}..."</span>
				<span v-if="activeEditorKey === 'dialog' && voiceError" class="text-xs text-red-500">{{ voiceError }}</span>
				<span v-if="activeEditorKey === 'dialog' && justInserted" class="text-xs text-green-600 font-semibold">✓ Inserted</span>

				<!-- Audio recording Info -->
				<span v-if="activeAudioKey === 'dialog' && uploadingAudio" class="text-xs text-[color:var(--brand-text,#0A84D0)] flex items-center gap-1">
					<div class="w-3.5 h-3.5 border border-outline-gray-2 border-t-[color:var(--brand,#29ADFF)] rounded-full animate-spin"></div>
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
					  : 'bg-surface-white text-ink-gray-6 border-outline-gray-2 hover:border-[color:var(--brand,#29ADFF)] hover:text-[color:var(--brand-text,#0A84D0)]'
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
					  : 'bg-surface-white text-ink-gray-6 border-outline-gray-2 hover:border-orange-400 hover:text-orange-600'
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
			<div class="border rounded-lg bg-surface-white shadow-sm overflow-hidden editor-container">
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

	<Transition name="slide">
		<div v-if="showEditTask" class="fixed inset-0 flex justify-end z-50">
			<div class="absolute inset-0 bg-slate-900/20 backdrop-blur-[2px]" @click="showEditTask = false"></div>
			
			<div class="relative w-full md:max-w-7xl lg:max-w-7xl h-full bg-surface-white flex flex-col shadow-2xl border-l border-outline-gray-2 overflow-y-auto md:overflow-hidden">
				<!-- Spinner Loading State -->
				<div v-if="!editPanelReady" class="flex-1 grid place-items-center bg-surface-gray-1 min-h-0">
					<div class="flex items-center gap-3 text-ink-gray-5">
						<div class="w-5 h-5 border-2 border-outline-gray-2 border-t-[color:var(--brand,#29ADFF)] rounded-full animate-spin"></div>
						<span class="text-sm font-medium">Loading task details...</span>
					</div>
				</div>

				<template v-else>
					<!-- Top Header Bar -->
					<header class="flex items-center justify-between gap-3 border-b border-outline-gray-1 bg-surface-white px-4 py-3 sm:px-5 shrink-0 z-20">
						<div class="min-w-0 flex-1">
							<div class="flex flex-wrap items-center gap-1.5 text-xs text-ink-gray-5">
								<button type="button" class="hover:text-ink-gray-8" @click="showEditTask = false">Tasks</button>
								<IconChevronRight class="h-3 w-3 text-ink-gray-4" />
								<span v-if="newTask.name" class="font-mono text-ink-gray-7">{{ newTask.name }}</span>
								<span class="mx-1 h-3 w-px bg-surface-gray-4"></span>
								<span class="status-pill" :class="getStatusPillClass(newTask.status)">
									<span class="h-1.5 w-1.5 rounded-full" :class="getStatusColor(newTask.status)" />{{ newTask.status }}
								</span>
								<Badge v-if="newTask.priority" :theme="getPriorityTheme(newTask.priority)" variant="subtle" size="sm">{{ newTask.priority }}</Badge>
								<Badge v-if="newTask.is_overdue" theme="red" variant="subtle" size="sm">Overdue</Badge>
								<Badge v-if="newTask.fullfilled_in_display_text" theme="green" variant="subtle" size="sm">{{ newTask.fullfilled_in_display_text }}</Badge>
							</div>
							<h2 class="mt-1 truncate text-lg font-semibold text-ink-gray-9" :title="newTask.subject">
								{{ isEditMode ? (newTask.subject || 'Task Details') : 'New Task' }}
							</h2>
						</div>
						<div class="flex items-center gap-1.5 shrink-0">
							<span class="kbd hidden lg:inline-flex" title="Keyboard shortcut">Ctrl S</span>
							<Button variant="solid" class="brand-btn" :loading="saving" @click="handleSaveTask">
								{{ isEditMode ? 'Save Changes' : 'Create Task' }}
							</Button>
							<Button variant="ghost" title="Close" @click="showEditTask = false">
								<IconX class="h-4 w-4" />
							</Button>
						</div>
					</header>

					<!-- Main Split Body Container -->
					<div class="flex-1 flex flex-col md:flex-row min-h-0 overflow-y-auto md:overflow-hidden">
						
						<!-- Left Column (60% Width on Desktop): Subject, Description & Activity Timeline -->
						<div class="w-full md:w-[60%] flex flex-col bg-surface-white min-h-0 border-b md:border-b-0 md:border-r border-outline-gray-1 shrink-0">
							<!-- Scrollable Main Left Content Area -->
							<div class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 custom-scrollbar">
								<!-- Task Description Section with Voice Dictation -->
								<div class="space-y-2.5">
									<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
										<label class="section-title">Description</label>
										
										<!-- Voice Controls -->
										<div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
											<span v-if="activeEditorKey === 'panel' && interimText" class="text-xs text-ink-gray-4 italic truncate max-w-[140px] sm:max-w-[180px]">"{{ interimText }}..."</span>
											<span v-if="activeEditorKey === 'panel' && voiceError" class="text-xs text-red-500">{{ voiceError }}</span>
											<span v-if="activeEditorKey === 'panel' && justInserted" class="text-xs text-green-600 font-semibold">✓ Inserted</span>

											<span v-if="activeAudioKey === 'panel' && uploadingAudio" class="text-xs text-[color:var(--brand-text,#0A84D0)] flex items-center gap-1">
												<div class="w-3.5 h-3.5 border border-outline-gray-2 border-t-[color:var(--brand,#29ADFF)] rounded-full animate-spin"></div>
												Uploading...
											</span>
											<span v-if="activeAudioKey === 'panel' && audioError" class="text-xs text-red-500">{{ audioError }}</span>
											<span v-if="isRecordingAudio && activeAudioKey === 'panel'" class="text-xs text-red-500 font-medium flex items-center gap-1.5 animate-pulse">
												<span class="w-2 h-2 rounded-full bg-red-500"></span>
												{{ formatDuration(audioDuration) }}
											</span>

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
												  : 'bg-surface-white text-ink-gray-6 border-outline-gray-2 hover:border-[color:var(--brand,#29ADFF)] hover:text-[color:var(--brand-text,#0A84D0)]'
											  ]"
											>
											  <svg v-if="!(isRecording && activeEditorKey === 'panel')" xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
												<path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
												<path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
											  </svg>
											  <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
												<rect x="6" y="6" width="12" height="12" rx="2"/>
											  </svg>
											  {{ isRecording && activeEditorKey === 'panel' ? 'Stop' : 'Dictate' }}
											</button>

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
												  : 'bg-surface-white text-ink-gray-6 border-outline-gray-2 hover:border-orange-400 hover:text-orange-600'
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
									<div class="border border-outline-gray-2 rounded-xl bg-surface-white shadow-sm overflow-hidden focus-within:border-[color:var(--brand,#29ADFF)] focus-within:ring-2 focus-within:ring-[color:var(--brand-soft,#E9F6FF)] transition-all">
										<TextEditor
											ref="panelEditorRef"
											editor-class="prose-sm max-w-none p-3.5 sm:p-4 min-h-[200px] outline-none bg-surface-white"
											:content="newTask.description"
											@change="(val) => (newTask.description = val)"
											:fixed-menu="true"
											:extensions="[AudioExtension]"
										/>
									</div>
								</div>

								<!-- Discussion & Activity Timeline Section -->
								<div class="pt-6 border-t border-outline-gray-2 space-y-4">
									<div class="flex items-center justify-between">
										<div class="flex items-center gap-2">
											<IconMessageSquare class="w-4 h-4 text-ink-gray-5" />
											<h3 class="text-xs sm:text-sm font-bold text-ink-gray-8">Discussion & Activity</h3>
											<span class="text-xs bg-surface-gray-2 text-ink-gray-5 px-2.5 py-0.5 rounded-full font-semibold">
												{{ comments.data?.length || 0 }} updates
											</span>
										</div>
									</div>

									<div class="relative min-h-[50px] pb-2">
										<div v-if="comments.loading" class="flex justify-center py-8">
											<div class="w-6 h-6 border-2 border-outline-gray-2 border-t-[color:var(--brand,#29ADFF)] rounded-full animate-spin"></div>
										</div>

										<!-- Timeline Comments Feed -->
										<div v-else-if="comments.data && comments.data.length > 0" class="space-y-4 relative pl-10 sm:pl-12 before:absolute before:inset-y-0 before:left-[18px] sm:before:left-[22px] before:w-0.5 before:bg-surface-gray-3">
											<div v-for="comment in comments.data" :key="comment.name" class="relative group">
												<!-- Timeline Avatar -->
												<div class="absolute -left-[40px] sm:-left-[48px] top-1 z-10">
													<Avatar 
														:image="getUserAvatarImage(comment.comment_by)"
														:label="getUserLabel(comment.comment_by) || comment.comment_by || 'User'" 
														size="md" 
														class="ring-4 ring-white shadow-sm shrink-0" 
													/>
												</div>

												<!-- Message Bubble Card -->
												<div class="bg-surface-white rounded-xl border border-outline-gray-2 p-3.5 sm:p-4 shadow-sm hover:shadow-md transition-all duration-200">
													<div class="flex items-center justify-between mb-2">
														<div class="flex items-center gap-1.5 text-xs">
															<span class="font-bold text-ink-gray-8 truncate max-w-[140px] sm:max-w-none">{{ getUserLabel(comment.comment_by) || comment.comment_by }}</span>
															<span class="text-ink-gray-3">·</span>
															<span class="text-ink-gray-4 font-medium shrink-0">{{ formatTimeAgo(comment.creation) }}</span>
														</div>

														<div class="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity" v-if="comment.comment_by === session.user">
															<button 
																@click="startEditing(comment)"
																class="p-1 hover:bg-surface-gray-1 rounded text-ink-gray-4 hover:text-[color:var(--brand-text,#0A84D0)] transition-colors"
																title="Edit Comment"
															>
																<IconEdit3 class="w-3.5 h-3.5" />
															</button>
															<button 
																@click="handleDeleteComment(comment.name)"
																class="p-1 hover:bg-red-50 rounded text-ink-gray-4 hover:text-red-600 transition-colors"
																title="Delete Comment"
															>
																<IconTrash2 class="w-3.5 h-3.5" />
															</button>
														</div>
													</div>

													<div class="text-sm text-ink-gray-6 leading-relaxed">
														<div v-if="editingCommentName === comment.name" class="space-y-3">
															<FormControl 
																type="textarea"
																v-model="editContent" 
																class="w-full rounded-xl border border-outline-gray-2 p-2 text-sm focus:ring-1 focus:ring-[color:var(--brand,#29ADFF)] outline-none resize-none"
															/>
															<div class="flex justify-end gap-2">
																<Button size="sm" variant="ghost" @click="cancelEdit">Cancel</Button>
																<Button size="sm" variant="solid" class="brand-btn" @click="handleUpdateComment(comment.name)">Save</Button>
															</div>
														</div>
														<div v-else class="prose prose-sm max-w-none text-ink-gray-6" v-html="comment.content"></div>
													</div>
												</div>
											</div>
										</div>

										<!-- Empty State Placeholder -->
										<div v-else class="flex flex-col items-center justify-center py-8 sm:py-10 text-ink-gray-4 bg-surface-white rounded-xl border border-dashed border-outline-gray-2 mx-1 my-1 shadow-sm">
											<IconMessageSquare class="w-8 h-8 mb-2 opacity-25 text-ink-gray-5" />
											<p class="text-xs font-semibold italic text-ink-gray-4 text-center">No updates or comments yet. Start the conversation!</p>
										</div>
									</div>
								</div>
							</div>

							<!-- Docked Bottom Comment Box -->
							<div class="p-3 sm:p-4 bg-surface-white border-t shrink-0">
								<CommentBox
									v-model="commentText"
									:avatar="getUserAvatarImage(session.user)"
									:user="session.user"
									:userName="session.userFullName"
									placeholder="Type a message..."
									:loading="postingComment"
									@submit="handlePostComment"
								/>
							</div>
						</div>

						<!-- Right Column (40% Width on Desktop): Metadata Cards & Attachments Sidebar -->
						<div class="w-full md:w-[40%] md:shrink-0 flex flex-col bg-surface-gray-1 overflow-y-auto p-4 sm:p-6 space-y-5 custom-scrollbar min-h-0">
							<!-- Section 1: General Information Card -->
							<div class="bg-surface-white rounded-xl border border-outline-gray-2 p-3.5 sm:p-4 space-y-4 shadow-sm">
								<h4 class="section-title">General Information</h4>

								<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
									<div class="space-y-1.5">
										<label class="block text-xs text-ink-gray-5">Status</label>
										<Autocomplete
										  ref="editStatusAutocomplete"
										  :options="statusOptions"
										  :modelValue="newTask.status"
										  @update:modelValue="val => newTask.status = val?.value ?? val ?? ''"
										  :compare-fn="compareOption"
										>
										  <template #target>
											<button
											  type="button"
											  @click="() => editStatusAutocomplete?.togglePopover()"
											  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
											>
											  <span class="truncate">{{ getStatusLabel(newTask.status) }}</span>
											  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
											</button>
										  </template>
										</Autocomplete>
									</div>

									<div class="space-y-1.5">
										<label class="block text-xs text-ink-gray-5">Priority</label>
										<Autocomplete
										  ref="editPriorityAutocomplete"
										  :options="priorityOptions"
										  :modelValue="newTask.priority"
										  @update:modelValue="val => newTask.priority = val?.value ?? val ?? ''"
										  :compare-fn="compareOption"
										>
										  <template #target>
											<button
											  type="button"
											  :disabled="isFieldDisabled"
											  @click="() => editPriorityAutocomplete?.togglePopover()"
											  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
											>
											  <span class="truncate">{{ getPriorityLabel(newTask.priority) }}</span>
											  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
											</button>
										  </template>
										</Autocomplete>
									</div>
								</div>

								<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 border-t border-outline-gray-2 pt-3 sm:pt-4">
									<div class="space-y-1.5">
										<label class="block text-xs text-ink-gray-5">Project</label>
										<Autocomplete
										  ref="editProjectAutocomplete"
										  :options="projectResource.data || []"
										  :modelValue="newTask.project"
										  @update:modelValue="val => newTask.project = val?.value ?? val ?? ''"
										  :compare-fn="compareOption"
										  :max-options="100"
										>
										  <template #target>
											<button
											  type="button"
											  :disabled="isFieldDisabled"
											  @click="() => editProjectAutocomplete?.togglePopover()"
											  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
											>
											  <span class="truncate">{{ getProjectLabel(newTask.project) }}</span>
											  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
											</button>
										  </template>
										</Autocomplete>
									</div>

									<div class="space-y-1.5">
										<label class="block text-xs text-ink-gray-5">Department</label>
										<Autocomplete
										  ref="editDepartmentAutocomplete"
										  :options="departmentResource.data || []"
										  :modelValue="newTask.department"
										  @update:modelValue="val => newTask.department = val?.value ?? val ?? ''"
										  :compare-fn="compareOption"
										  :max-options="100"
										>
										  <template #target>
											<button
											  type="button"
											  :disabled="isFieldDisabled"
											  @click="() => editDepartmentAutocomplete?.togglePopover()"
											  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
											>
											  <span class="truncate">{{ getDepartmentLabel(newTask.department) }}</span>
											  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
											</button>
										  </template>
										</Autocomplete>
									</div>
								</div>
							</div>

							<!-- Section 2: Assignment & Schedule Card -->
							<div class="bg-surface-white rounded-xl border border-outline-gray-2 p-3.5 sm:p-4 space-y-4 shadow-sm">
								<h4 class="section-title">Assignment & Schedule</h4>

								<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
									<div class="space-y-1.5">
										<label class="block text-xs text-ink-gray-5">Assigned By</label>
										<Autocomplete
										  ref="editAssignedByAutocomplete"
										  :options="userResource.data || []"
										  :modelValue="newTask.assigned_by"
										  @update:modelValue="val => newTask.assigned_by = val?.value ?? val ?? ''"
										  :compare-fn="compareOption"
										  :max-options="100"
										>
										  <template #target>
											<button
											  type="button"
											  :disabled="isFieldDisabled"
											  @click="() => editAssignedByAutocomplete?.togglePopover()"
											  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
											>
											  <span class="truncate">{{ getUserLabel(newTask.assigned_by, 'Select User') }}</span>
											  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
											</button>
										  </template>
										</Autocomplete>
									</div>

									<div class="space-y-1.5">
										<label class="block text-xs text-ink-gray-5">Team</label>
										<Autocomplete
										  ref="editTeamAutocomplete"
										  :options="tactixTeamResource.data || []"
										  :modelValue="newTask.tactix_team"
										  @update:modelValue="val => newTask.tactix_team = val?.value ?? val ?? ''"
										  :compare-fn="compareOption"
										  :max-options="100"
										>
										  <template #target>
											<button
											  type="button"
											  :disabled="isFieldDisabled"
											  @click="() => editTeamAutocomplete?.togglePopover()"
											  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
											>
											  <span class="truncate">{{ getTeamLabel(newTask.tactix_team) }}</span>
											  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
											</button>
										  </template>
										</Autocomplete>
									</div>
								</div>

								<div class="space-y-1 border-t border-outline-gray-2 pt-3">
									<label class="text-xs font-medium text-ink-gray-6 block">Assigned To</label>
									<MultiSelect
										:options="assignedToOptions"
										v-model="newTask.assigned_to"
										:disabled="isFieldDisabled"
										class=""
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
								</div>

								<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 border-t border-outline-gray-2 pt-3">
									<DatePicker label="Deadline" v-model="newTask.exp_end_date" class="!mb-0" :disabled="isFieldDisabled" />
									<FormControl label="Expected Time (Hrs)" type="number" v-model="newTask.expected_time" class="!mb-0" :disabled="isFieldDisabled" />
								</div>

								<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 border-t border-outline-gray-2 pt-3">
									<FormControl label="Assigned Datetime" type="datetime-local" :model-value="formatForInput(newTask.assigned_datetime)" class="!mb-0" disabled="true" />
									<div v-if="newTask.completed_by" class="space-y-1.5">
										<label class="block text-xs text-ink-gray-5">Completed By</label>
										<Autocomplete
										  ref="editCompletedByAutocomplete"
										  :options="userResource.data || []"
										  :modelValue="newTask.completed_by"
										  @update:modelValue="val => newTask.completed_by = val?.value ?? val ?? ''"
										  :compare-fn="compareOption"
										  :max-options="100"
										>
										  <template #target>
											<button
											  type="button"
											  disabled="true"
											  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors border border-transparent text-ink-gray-8 cursor-not-allowed opacity-50"
											>
											  <span class="truncate">{{ getUserLabel(newTask.completed_by, 'Select User') }}</span>
											  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
											</button>
										  </template>
										</Autocomplete>
									</div>
								</div>
							</div>

							<!-- Section 3: Attachments Card -->
							<div class="bg-surface-white rounded-xl border border-outline-gray-2 p-3.5 sm:p-4 space-y-4">
								<h4 class="section-title">Attachments</h4>
								
								<FileUploader @success="handleFileUpload">
									<template #default="{ openFileSelector }">
										<button 
											@click="openFileSelector" 
											class="w-full flex items-center justify-center gap-2 border-2 border-dashed border-outline-gray-2 rounded-xl p-3.5 sm:p-4 text-ink-gray-5 hover:border-[color:var(--brand,#29ADFF)] hover:text-[color:var(--brand-text,#0A84D0)] hover:bg-[color:var(--brand-soft,#E9F6FF)] transition-all group"
										>
											<IconPaperclip class="w-4 h-4" />
											<span class="text-xs font-semibold">Add Files</span>
										</button>
									</template>
								</FileUploader>
								
								<div class="grid grid-cols-1 gap-2.5">
									<div 
										v-for="(file, idx) in newTask.attachments" 
										:key="idx" 
										class="group flex items-center justify-between bg-surface-gray-1 border border-outline-gray-2 rounded-xl hover:border-[color:var(--brand,#29ADFF)] hover:shadow transition-all overflow-hidden p-2"
									>
										<a 
											:href="file.file_url" 
											target="_blank" 
											class="flex flex-1 items-center gap-2.5 truncate"
										>
											<div class="h-8 w-8 rounded-lg bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)] flex items-center justify-center shrink-0">
												<IconPaperclip class="w-4 h-4" />
											</div>
											<div class="truncate text-left">
												<span class="block truncate font-semibold text-ink-gray-7 text-xs group-hover:text-[color:var(--brand-text,#0A84D0)] transition-colors">
													{{ file.file_name }}
												</span>
												<span class="text-[10px] text-ink-gray-4 font-semibold uppercase tracking-wider">{{ fileExt(file.file_name) }}</span>
											</div>
										</a>

										<button 
											@click.stop="removeAttachment(idx)" 
											class="p-2 ml-1 hover:bg-red-50 rounded-lg text-ink-gray-4 hover:text-red-500 transition-colors"
											title="Remove file"
										>
											<IconX class="w-4 h-4" />
										</button>
									</div>
								</div>
							</div>
						</div>
					</div>
				</template>
			</div>
		</div>
	</Transition>
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
	Popover,
	Select,
	TextEditor,
	createListResource,
	createResource,
} from "frappe-ui"
import {
	computed,
	h,
	nextTick,
	onMounted,
	onUnmounted,
	reactive,
	ref,
	watch,
} from "vue"
import { useRoute, useRouter } from "vue-router"
import CommentBox from "../components/CommentBox.vue"
import { session } from "../data/session"

import { useSocket } from "@/socket"

import IconAlertCircle from "~icons/lucide/alert-circle"
import IconArrowDown from "~icons/lucide/arrow-down"
import IconArrowUp from "~icons/lucide/arrow-up"
import IconBriefcase from "~icons/lucide/briefcase"
import IconCheck from "~icons/lucide/check"
import IconCheckCircle from "~icons/lucide/check-circle"
import IconChevronDown from "~icons/lucide/chevron-down"
import IconChevronLeft from "~icons/lucide/chevron-left"
import IconChevronRight from "~icons/lucide/chevron-right"
import IconChevronsLeft from "~icons/lucide/chevrons-left"
import IconChevronsRight from "~icons/lucide/chevrons-right"
import IconClock from "~icons/lucide/clock"
import IconEdit3 from "~icons/lucide/edit-3"
import IconFilter from "~icons/lucide/filter"
import IconFlag from "~icons/lucide/flag"
import IconLayers from "~icons/lucide/layers"
import IconLayoutGrid from "~icons/lucide/layout-grid"
import IconList from "~icons/lucide/list"
import IconMessageSquare from "~icons/lucide/message-square"
import IconPaperclip from "~icons/lucide/paperclip"
import IconPlus from "~icons/lucide/plus"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconRotateCcw from "~icons/lucide/rotate-ccw"
import IconSearch from "~icons/lucide/search"
import IconSlidersHorizontal from "~icons/lucide/sliders-horizontal"
import IconTrash2 from "~icons/lucide/trash-2"
import IconUser from "~icons/lucide/user"
import IconX from "~icons/lucide/x"

const searchInputEl = ref(null)

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
const statusAutocomplete = ref(null)
const priorityAutocomplete = ref(null)
const deadlineAutocomplete = ref(null)

const createProjectAutocomplete = ref(null)
const createDepartmentAutocomplete = ref(null)
const createStatusAutocomplete = ref(null)
const createPriorityAutocomplete = ref(null)
const createTeamAutocomplete = ref(null)
const createAssignedByAutocomplete = ref(null)

const editProjectAutocomplete = ref(null)
const editDepartmentAutocomplete = ref(null)
const editStatusAutocomplete = ref(null)
const editPriorityAutocomplete = ref(null)
const editTeamAutocomplete = ref(null)
const editAssignedByAutocomplete = ref(null)
const editCompletedByAutocomplete = ref(null)

function compareOption(a, b) {
	const aVal = a && typeof a === "object" ? a.value : a
	const bVal = b && typeof b === "object" ? b.value : b
	return aVal === bVal
}

function getProjectLabel(val) {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return "Project"
	const match = projectResource.data?.find((p) => p.value === rawVal)
	return match ? match.label : rawVal
}

function getDepartmentLabel(val) {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return "Department"
	const match = departmentResource.data?.find((d) => d.value === rawVal)
	return match ? match.label : rawVal
}

function getUserLabel(val, defaultLabel = "User") {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return defaultLabel
	const match = userResource.data?.find((u) => u.value === rawVal)
	return match ? match.label : rawVal
}

function getStatusLabel(val) {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return "Status"
	const match = filterStatusOptions.find((s) => s.value === rawVal)
	return match ? match.label : rawVal
}

function getPriorityLabel(val) {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return "Priority"
	const match = priorityOptions.find((p) => p.value === rawVal)
	return match ? match.label : rawVal
}

function getDeadlineLabel(val) {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return "Deadline"
	const match = deadlineOptions.find((d) => d.value === rawVal)
	return match ? match.label : rawVal
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
	fetchTaskSummary()
	if (viewMode.value === "board") fetchAllColumns()

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
	tactix_team: "",
})

const FILTERABLE_FIELDS = [
	{ label: "Project", value: "project", key: "project" },
	{ label: "Department", value: "department", key: "department" },
	{ label: "Status", value: "status", key: "status" },
	{ label: "Priority", value: "priority", key: "priority" },
	{ label: "Assigned By", value: "assigned_by", key: "assigned_by" },
	{ label: "Assigned To", value: "assigned_to", key: "assigned_to" },
	{ label: "Deadline", value: "deadline", key: "deadline" },
	{ label: "Team", value: "tactix_team", key: "tactix_team" },
]

const activeFilterRules = ref([])

function syncActiveFilterRules() {
	const newRules = []
	FILTERABLE_FIELDS.forEach((f) => {
		const val = selectedFilters[f.value]
		if (val) {
			newRules.push({
				id: "rule_" + f.value,
				field: f.value,
				value: val,
			})
		}
	})
	if (newRules.length === 0) {
		newRules.push({
			id: "rule_" + Date.now(),
			field: "status",
			value: "",
		})
	}
	activeFilterRules.value = newRules
}

function toggleAssignedToMe() {
	if (selectedFilters.assigned_to === session.user) {
		selectedFilters.assigned_to = ""
	} else {
		selectedFilters.assigned_to = session.user
	}
}

function addFilterRule() {
	const unusedField = FILTERABLE_FIELDS.find(
		(f) => !activeFilterRules.value.some((r) => r.field === f.value),
	)
	const field = unusedField ? unusedField.value : "status"
	activeFilterRules.value.push({
		id: "rule_" + Date.now() + "_" + Math.random().toString(36).substr(2, 4),
		field,
		value: "",
	})
}

function removeFilterRule(id) {
	const idx = activeFilterRules.value.findIndex((r) => r.id === id)
	if (idx > -1) {
		const removed = activeFilterRules.value[idx]
		activeFilterRules.value.splice(idx, 1)
		if (removed.field in selectedFilters) {
			selectedFilters[removed.field] = ""
		}
	}
	if (activeFilterRules.value.length === 0) {
		activeFilterRules.value.push({
			id: "rule_" + Date.now(),
			field: "status",
			value: "",
		})
	}
}

function applyFilterRules() {
	FILTERABLE_FIELDS.forEach((f) => {
		const hasRule = activeFilterRules.value.some((r) => r.field === f.key)
		if (!hasRule) {
			selectedFilters[f.key] = ""
		}
	})
	activeFilterRules.value.forEach((r) => {
		if (r.field in selectedFilters) {
			selectedFilters[r.field] = r.value
		}
	})
}

function getFieldOptionsForSelect(fieldKey) {
	if (fieldKey === "status") return filterStatusOptions
	if (fieldKey === "priority") return priorityOptions
	if (fieldKey === "deadline")
		return deadlineOptions.filter((d) => d.value !== "")
	if (fieldKey === "tactix_team") return tactixTeamResource.data || []
	if (fieldKey === "project") return projectResource.data || []
	if (fieldKey === "department") return departmentResource.data || []
	if (fieldKey === "assigned_by" || fieldKey === "assigned_to")
		return userResource.data || []
	return []
}

const projectOptions = computed(() => [
	{ label: "All Projects", value: "all" },
	...(projectResource.data || []),
])

function getRuleDisplayLabel(rule) {
	if (!rule.value) return "Select value"
	if (rule.field === "project") return getProjectLabel(rule.value)
	if (rule.field === "department") return getDepartmentLabel(rule.value)
	if (rule.field === "assigned_by" || rule.field === "assigned_to")
		return getUserLabel(rule.value)
	return rule.value
}

const departmentOptions = computed(() => [
	{ label: "All Departments", value: "all" },
	...(departmentResource.data || []),
])

const statusFilterOptionsList = computed(() => [
	{ label: "All Statuses", value: "all" },
	...filterStatusOptions,
])

const priorityFilterOptionsList = computed(() => [
	{ label: "All Priorities", value: "all" },
	...priorityOptions,
])

const assignedByOptions = computed(() => [
	{ label: "Assigned By", value: "all" },
	...(userResource.data || []),
])

const assignedToOptionsList = computed(() => [
	{ label: "Assigned To", value: "all" },
	...(userResource.data || []),
])

const deadlineOptionsList = computed(() => [
	{ label: "All Deadlines", value: "all" },
	...deadlineOptions.filter((d) => d.value !== ""),
])

const projectFilterValue = computed({
	get: () => selectedFilters.project || "all",
	set: (val) => {
		selectedFilters.project = val === "all" ? "" : val
	},
})

const departmentFilterValue = computed({
	get: () => selectedFilters.department || "all",
	set: (val) => {
		selectedFilters.department = val === "all" ? "" : val
	},
})

const statusFilterValue = computed({
	get: () => selectedFilters.status || "all",
	set: (val) => {
		selectedFilters.status = val === "all" ? "" : val
	},
})

const priorityFilterValue = computed({
	get: () => selectedFilters.priority || "all",
	set: (val) => {
		selectedFilters.priority = val === "all" ? "" : val
	},
})

const assignedByFilterValue = computed({
	get: () => selectedFilters.assigned_by || "all",
	set: (val) => {
		selectedFilters.assigned_by = val === "all" ? "" : val
	},
})

const assignedToFilterValue = computed({
	get: () => selectedFilters.assigned_to || "all",
	set: (val) => {
		selectedFilters.assigned_to = val === "all" ? "" : val
	},
})

const deadlineFilterValue = computed({
	get: () => selectedFilters.deadline || "all",
	set: (val) => {
		selectedFilters.deadline = val === "all" ? "" : val
	},
})

watch(
	selectedFilters,
	(newFilters) => {
		Object.entries(newFilters).forEach(([key, val]) => {
			if (val) {
				const rule = activeFilterRules.value.find((r) => r.field === key)
				if (rule) {
					rule.value = val
				} else {
					activeFilterRules.value.push({
						id:
							"rule_" +
							Date.now() +
							"_" +
							Math.random().toString(36).substr(2, 4),
						field: key,
						value: val,
					})
				}
			} else {
				const idx = activeFilterRules.value.findIndex((r) => r.field === key)
				if (idx > -1) {
					activeFilterRules.value.splice(idx, 1)
				}
			}
		})
	},
	{ deep: true },
)

const activeFilterCount = computed(() => {
	return Object.values(selectedFilters).filter((v) => v !== "").length
})

const activeFilterChips = computed(() => {
	const chips = []
	Object.entries(selectedFilters).forEach(([key, val]) => {
		if (val) {
			const fieldObj = FILTERABLE_FIELDS.find((f) => f.key === key)
			const fieldLabel = fieldObj ? fieldObj.label : key
			let displayVal = val
			if (key === "project") displayVal = getProjectLabel(val)
			else if (key === "department") displayVal = getDepartmentLabel(val)
			else if (key === "assigned_by" || key === "assigned_to")
				displayVal = getUserLabel(val)
			else if (key === "tactix_team") displayVal = getTeamLabel(val)
			else if (key === "status" || key === "priority") displayVal = val
			else if (key === "deadline") {
				const match = deadlineOptions.find((d) => d.value === val)
				displayVal = match ? match.label : val
			}
			chips.push({ key, label: fieldLabel, displayValue: displayVal })
		}
	})
	return chips
})

function removeFilterByKey(key) {
	if (key in selectedFilters) {
		selectedFilters[key] = ""
	}
}

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

const STORAGE_KEY_GROUPBY = "tactix_tasks_groupby_config"

function loadSavedGroupBy() {
	try {
		const saved = localStorage.getItem(STORAGE_KEY_GROUPBY)
		if (
			saved &&
			["status", "project", "priority", "department", "tactix_team"].includes(
				saved,
			)
		) {
			return saved
		}
	} catch (e) {
		console.error("Failed to load groupby settings", e)
	}
	return "status"
}

const groupBy = ref(loadSavedGroupBy())

watch(groupBy, (newVal) => {
	try {
		localStorage.setItem(STORAGE_KEY_GROUPBY, newVal)
	} catch (e) {
		console.error("Failed to save groupby settings", e)
	}
})

const GROUP_BY_OPTIONS = [
	{ label: "Status", value: "status", icon: IconAlertCircle },
	{ label: "Project", value: "project", icon: IconBriefcase },
	{ label: "Priority", value: "priority", icon: IconFlag },
	{ label: "Department", value: "department", icon: IconBriefcase },
	{ label: "Team", value: "tactix_team", icon: IconBriefcase },
]

function getGroupByLabel(key) {
	const opt = GROUP_BY_OPTIONS.find((o) => o.value === key)
	return opt ? opt.label : key
}

const activeGroupColumns = computed(() => {
	if (groupBy.value === "project") {
		const list = (projectResource.data || []).map((p) => ({
			label: p.label || p.value,
			value: p.value,
		}))
		return [...list, { label: "No Project", value: "__none__" }]
	}
	if (groupBy.value === "priority") {
		return [
			{ label: "Urgent", value: "Urgent" },
			{ label: "High", value: "High" },
			{ label: "Medium", value: "Medium" },
			{ label: "Low", value: "Low" },
			{ label: "No Priority", value: "__none__" },
		]
	}
	if (groupBy.value === "department") {
		const list = (departmentResource.data || []).map((d) => ({
			label: d.label || d.value,
			value: d.value,
		}))
		return [...list, { label: "No Department", value: "__none__" }]
	}
	if (groupBy.value === "tactix_team") {
		const list = (tactixTeamResource.data || []).map((t) => ({
			label: t.label || t.value,
			value: t.value,
		}))
		return [...list, { label: "No Team", value: "__none__" }]
	}
	return statusOptions
})

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

const tactixTeamResource = createListResource({
	doctype: "Tactix Team",
	fields: ["team_name", "name"],
	auto: true,
	transform: (teams) =>
		teams.map((t) => ({ label: t.team_name || t.name, value: t.name })),
	pageLength: 10000,
})

const ALL_COLUMNS = [
	{
		label: "Task Name",
		key: "subject",
		icon: IconCheckCircle,
		width: "280px",
		mandatory: true,
	},
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
	{ label: "Assigned DateTime", key: "assigned_datetime", icon: IconClock },
	{ label: "Priority", key: "priority", icon: IconFlag },
	{ label: "Status", key: "status", icon: IconAlertCircle },
	{ label: "Deadline", key: "exp_end_date", icon: IconClock },
	{ label: "Task ID", key: "name", icon: IconCheckCircle },
	{ label: "Team", key: "tactix_team", icon: IconBriefcase },
	{ label: "Assigned By", key: "assigned_by", icon: IconClock },
	{ label: "Completed By", key: "completed_by", icon: IconCheck },
	{ label: "Expected Time", key: "expected_time", icon: IconClock },
	{
		label: "Comments",
		key: "has_unseen_comments",
		icon: IconMessageSquare,
		width: "90px",
	},
]

const DEFAULT_COLUMN_KEYS = [
	"subject",
	"description_for_list",
	"project_name",
	"department",
	"assigned_datetime",
	"priority",
	"status",
	"exp_end_date",
	"name",
	"has_unseen_comments",
]

const STORAGE_KEY = "tactix_tasks_columns_config"

function loadSavedColumns() {
	try {
		const saved = localStorage.getItem(STORAGE_KEY)
		if (saved) {
			const parsed = JSON.parse(saved)
			if (Array.isArray(parsed) && parsed.length > 0) {
				const validKeys = parsed.filter((k) =>
					ALL_COLUMNS.some((c) => c.key === k),
				)
				if (!validKeys.includes("subject")) {
					validKeys.unshift("subject")
				}
				if (validKeys.length > 0) return validKeys
			}
		}
	} catch (e) {
		console.error("Failed to load column settings", e)
	}
	return [...DEFAULT_COLUMN_KEYS]
}

const activeColumnKeys = ref(loadSavedColumns())
const columnSearchQuery = ref("")

watch(
	activeColumnKeys,
	(newVal) => {
		try {
			localStorage.setItem(STORAGE_KEY, JSON.stringify(newVal))
		} catch (e) {
			console.error("Failed to save column settings", e)
		}
	},
	{ deep: true },
)

function getColumnLabel(key) {
	const col = ALL_COLUMNS.find((c) => c.key === key)
	return col ? col.label : key
}

function getTeamLabel(val) {
	if (!val) return "—"
	const match = tactixTeamResource.data?.find((t) => t.value === val)
	return match ? match.label : val
}

const inactiveColumns = computed(() => {
	return ALL_COLUMNS.filter((c) => !activeColumnKeys.value.includes(c.key))
})

function resetColumns() {
	activeColumnKeys.value = [...DEFAULT_COLUMN_KEYS]
}

function toggleColumn(key) {
	if (key === "subject") return
	const idx = activeColumnKeys.value.indexOf(key)
	if (idx > -1) {
		activeColumnKeys.value.splice(idx, 1)
	} else {
		activeColumnKeys.value.push(key)
	}
}

function moveColumnUp(index) {
	if (index <= 0) return
	const temp = activeColumnKeys.value[index]
	activeColumnKeys.value[index] = activeColumnKeys.value[index - 1]
	activeColumnKeys.value[index - 1] = temp
}

function moveColumnDown(index) {
	if (index >= activeColumnKeys.value.length - 1) return
	const temp = activeColumnKeys.value[index]
	activeColumnKeys.value[index] = activeColumnKeys.value[index + 1]
	activeColumnKeys.value[index + 1] = temp
}

const columns = computed(() => {
	const map = new Map(ALL_COLUMNS.map((c) => [c.key, c]))
	return activeColumnKeys.value.map((key) => map.get(key)).filter(Boolean)
})

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

	if (debouncedSearchQuery.value)
		f.subject = ["like", `%${debouncedSearchQuery.value}%`]
	if (selectedFilters.project) f.project = selectedFilters.project
	if (selectedFilters.status) f.status = selectedFilters.status
	if (selectedFilters.priority) f.priority = selectedFilters.priority
	if (selectedFilters.assigned_by) f.assigned_by = selectedFilters.assigned_by
	if (selectedFilters.assigned_to) f.assigned_to = selectedFilters.assigned_to
	if (selectedFilters.department) f.department = selectedFilters.department
	if (selectedFilters.tactix_team) f.tactix_team = selectedFilters.tactix_team

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
	selectedFilters.tactix_team = ""
	syncActiveFilterRules()
}

function filterByStat(label) {
	const status = STAT_STATUS[label] ?? label
	// clicking the active card again clears the status filter
	selectedFilters.status = selectedFilters.status === status ? "" : status
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

watch(
	taskFilters,
	() => {
		fetchTaskSummary()
		// board columns are refreshed by the board watcher below
		if (currentPage.value !== 1) currentPage.value = 1
		else fetchTasks()
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

const pageOptions = computed(() =>
	Array.from({ length: totalPages.value }, (_, i) => ({
		label: `${i + 1} / ${totalPages.value}`,
		value: i + 1,
	})),
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
function onDragEnter(colValue) {
	hoveredColumn.value = colValue
}
function onDragLeave() {
	/* intentionally empty */
}

async function onDrop(event, targetValue) {
	const task = draggedTask.value
	hoveredColumn.value = null
	if (!task) return

	const groupKey = groupBy.value
	const currentTaskVal =
		(groupKey === "status" ? task.status : task[groupKey]) || "__none__"
	if (currentTaskVal === targetValue) return

	const oldVal = task[groupKey]
	const newVal = targetValue === "__none__" ? "" : targetValue

	const oldKey = currentTaskVal
	const taskIndex = columnTasks[oldKey]?.findIndex((t) => t.name === task.name)
	if (taskIndex !== undefined && taskIndex > -1) {
		const [movedTask] = columnTasks[oldKey].splice(taskIndex, 1)
		if (!columnTasks[targetValue]) columnTasks[targetValue] = []
		columnTasks[targetValue].unshift(movedTask)
	}

	task[groupKey] = newVal

	if (groupKey === "status" && tasksSummaryResource.data) {
		if (oldVal === "Open" && tasksSummaryResource.data.open > 0)
			tasksSummaryResource.data.open--
		else if (oldVal === "Working" && tasksSummaryResource.data.working > 0)
			tasksSummaryResource.data.working--
		else if (
			oldVal === "Pending Review" &&
			tasksSummaryResource.data.pending_review > 0
		)
			tasksSummaryResource.data.pending_review--
		else if (oldVal === "Completed" && tasksSummaryResource.data.completed > 0)
			tasksSummaryResource.data.completed--

		if (newVal === "Open") tasksSummaryResource.data.open++
		else if (newVal === "Working") tasksSummaryResource.data.working++
		else if (newVal === "Pending Review")
			tasksSummaryResource.data.pending_review++
		else if (newVal === "Completed") tasksSummaryResource.data.completed++
	}

	try {
		if (groupKey === "status") {
			await updateTaskStatusAPI.submit({ name: task.name, status: newVal })
		} else {
			await editTaskAPI.submit({
				name: task.name,
				doc: { subject: task.subject, [groupKey]: newVal },
			})
		}
		tasksResource.reload()
		fetchTaskSummary()
	} catch (e) {
		console.error("Failed to save task drop", e)
		errorDialogTitle.value = "Permission Denied"
		let msg = "You do not have permission to update this task."
		if (e.message) msg = e.message
		else if (typeof e === "string") msg = e
		if (msg.includes("PermissionError")) msg = msg.split("PermissionError")[1]
		else if (msg.includes("Error:")) msg = msg.split("Error:")[1]
		errorMessage.value = msg.replace(/<[^>]*>/g, "").trim()
		showErrorDialog.value = true
		task[groupKey] = oldVal
		if (viewMode.value === "board") fetchAllColumns()
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
	tactix_team: "",
}

const newTask = reactive({ ...initialForm })

const kpiStats = computed(() => {
	const summary = tasksSummaryResource.data || {}
	return [
		{ label: "Total", value: summary.total, dot: "bg-slate-400" },
		{ label: "Open", value: summary.open, dot: "bg-blue-500" },
		{ label: "In Progress", value: summary.working, dot: "bg-orange-400" },
		{ label: "Pending Review", value: summary.pending_review, dot: "bg-violet-500" },
		{ label: "Completed", value: summary.completed, dot: "bg-green-500" },
		{ label: "Overdue", value: summary.overdue, dot: "bg-red-500" },
	]
})

const summaryLoading = computed(() => tasksSummaryResource.loading)

// KPI label -> status filter value
const STAT_STATUS = {
	Total: "",
	Open: "Open",
	"In Progress": "Working",
	"Pending Review": "Pending Review",
	Completed: "Completed",
	Overdue: "Overdue",
}

function isStatActive(label) {
	return (selectedFilters.status || "") === (STAT_STATUS[label] ?? label)
}

const columnTasks = reactive({})
const columnPages = reactive({})
const columnHasMore = reactive({})
const columnLoading = reactive({})

const columnReq = {}

async function fetchColumnTasks(colVal, reset = false) {
	if (!reset && (columnLoading[colVal] || columnHasMore[colVal] === false)) return

	const req = (columnReq[colVal] = (columnReq[colVal] || 0) + 1)
	columnLoading[colVal] = true
	if (reset) {
		columnPages[colVal] = 1
		columnTasks[colVal] = []
		columnHasMore[colVal] = true
	}

	try {
		const filters = { ...taskFilters.value }
		if (groupBy.value === "status") {
			filters.status = colVal
		} else {
			filters[groupBy.value] =
				colVal === "__none__" ? ["is", "not set"] : colVal
		}
		const limit = 20
		const start = ((columnPages[colVal] || 1) - 1) * limit

		const res = await createResource({
			url: "tactix.api.tasks.get_tasks",
			params: { filters, start, page_length: limit },
		}).submit()

		if (req !== columnReq[colVal]) return // a newer request replaced this one

		const tasksList = res?.tasks || []
		if (!columnTasks[colVal]) columnTasks[colVal] = []
		columnTasks[colVal].push(...tasksList)

		if (tasksList.length < limit) columnHasMore[colVal] = false
		else columnPages[colVal] = (columnPages[colVal] || 1) + 1
	} catch (error) {
		console.error(`Failed to fetch tasks for column ${colVal}:`, error)
	} finally {
		if (req === columnReq[colVal]) columnLoading[colVal] = false
	}
}

function fetchAllColumns() {
	for (const opt of activeGroupColumns.value) fetchColumnTasks(opt.value, true)
}

function handleColumnScroll(e, colVal) {
	const { scrollTop, scrollHeight, clientHeight } = e.target
	if (scrollHeight - scrollTop - clientHeight < 20) fetchColumnTasks(colVal)
}

function filteredTasks(colVal) {
	if (viewMode.value === "board") return columnTasks[colVal] || []
	if (groupBy.value === "status")
		return (filteredTasksData.value || []).filter((t) => t.status === colVal)
	if (colVal === "__none__")
		return (filteredTasksData.value || []).filter((t) => !t[groupBy.value])
	return (filteredTasksData.value || []).filter(
		(t) => t[groupBy.value] === colVal,
	)
}

watch(
	[viewMode, groupBy, activeGroupColumns, taskFilters],
	() => {
		if (viewMode.value === "board") fetchAllColumns()
	},
	{ immediate: true, deep: true },
)


function openCreateDialog() {
	isEditMode.value = false
	Object.assign(newTask, {
		...initialForm,
		attachments: [],
		assigned_date: dayjs().format("YYYY-MM-DD"),
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

const bulkDeleteDialogOptions = computed(() => ({
	title: "Delete Selected Tasks",
	size: "sm",
	actions: [
		{
			label: "Delete",
			variant: "solid",
			theme: "red",
			loading: saving.value,
			onClick: executeBulkDelete,
		},
		{
			label: "Cancel",
			variant: "ghost",
			onClick: () => {
				showBulkDeleteDialog.value = false
			},
		},
	],
}))

const createTaskDialogOptions = computed(() => ({
	title: isEditMode.value ? "Edit Task" : "Create Task",
	size: "4xl",
	actions: [
		{
			label: isEditMode.value ? "Save Changes" : "Create Task",
			variant: "solid",
			class: "brand-btn",
			loading: saving.value,
			onClick: handleSaveTask,
		},
		{
			label: "Cancel",
			variant: "ghost",
			onClick: () => {
				showCreateDialog.value = false
			},
		},
	],
}))

const handleSaveTask = async () => {
	if (!newTask.subject || !newTask.subject.trim()) {
		showError("Task subject is required.", "Missing subject")
		return
	}
	saving.value = true
	try {
		const payload = { ...newTask }
		let res
		if (isEditMode.value) {
			res = await editTaskAPI.submit({ name: newTask.name, doc: payload })
		} else {
			res = await createTaskAPI.submit({ doc: payload })
		}
		if (res?.error) {
			showError(res.error, "Could not save task")
			return
		}
		fetchTasks()
		tasksSummaryResource.reload()
		if (viewMode.value === "board") fetchAllColumns()
		showCreateDialog.value = false
		showEditTask.value = false
	} catch (e) {
		console.error("Failed to save task:", e)
		showError(e?.message || "An error occurred while saving the task.", "Could not save task")
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

const postingComment = ref(false)

function handlePostComment() {
	if (!commentText.value.trim() || postingComment.value || !newTask.name) return
	postingComment.value = true
	createResource({
		url: "tactix.api.tasks.add_comment",
		params: { task: newTask.name, content: commentText.value },
		auto: true,
		async onSuccess() {
			commentText.value = ""
			await comments.fetch()
			postingComment.value = false
		},
		onError(e) {
			postingComment.value = false
			showError(e?.message || "Could not post the comment.", "Comment not posted")
		},
	})
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
	if (!window.confirm("Delete this comment?")) return
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
			Open: "bg-blue-500",
			Working: "bg-orange-400",
			"Pending Review": "bg-violet-500",
			Completed: "bg-green-500",
			Overdue: "bg-red-500",
			Cancelled: "bg-slate-400",
		}[status] || "bg-slate-300"
	)
}

function getStatusPillClass(status) {
	return (
		{
			Open: "bg-surface-blue-1 text-ink-blue-3",
			Working: "bg-surface-amber-1 text-ink-amber-3",
			"Pending Review": "bg-surface-gray-2 text-ink-gray-8",
			Completed: "bg-surface-green-1 text-ink-green-3",
			Overdue: "bg-surface-red-1 text-ink-red-4",
			Cancelled: "bg-surface-gray-2 text-ink-gray-5",
		}[status] || "bg-surface-gray-2 text-ink-gray-6"
	)
}

function getStatusTheme(status) {
	return (
		{ Open: "blue", Working: "orange", "Pending Review": "gray", Completed: "green", Overdue: "red" }[status] ||
		"gray"
	)
}

// Board column header dot
function groupDotClass(value) {
	if (groupBy.value === "status") return getStatusColor(value)
	if (groupBy.value === "priority")
		return { Urgent: "bg-red-600", High: "bg-red-400", Medium: "bg-amber-400", Low: "bg-slate-300" }[value] || "bg-slate-300"
	return value === "__none__" ? "bg-slate-300" : "bg-blue-400"
}

// Deadline text: "Overdue 3 days", "Due today", "Due tomorrow", "Due 12 Nov"
function dueInfo(task) {
	if (!task?.exp_end_date) return { text: "No date", cls: "text-ink-gray-4" }
	const due = dayjs(task.exp_end_date).startOf("day")
	const today = dayjs().startOf("day")
	const diff = due.diff(today, "day")
	const label = due.year() === today.year() ? due.format("D MMM") : due.format("D MMM YYYY")
	if (task.status === "Completed" || task.status === "Cancelled") return { text: label, cls: "text-ink-gray-5" }
	if (diff < 0) return { text: `Overdue ${due.from(today, true)}`, cls: "font-medium text-ink-red-4" }
	if (diff === 0) return { text: "Due today", cls: "font-medium text-ink-amber-3" }
	if (diff === 1) return { text: "Due tomorrow", cls: "text-ink-amber-3" }
	return { text: label, cls: "text-ink-gray-5" }
}

function fileExt(name) {
	const m = /\.([a-z0-9]+)$/i.exec(name || "")
	return m ? m[1].toUpperCase() : "File"
}

function showError(msg, title = "Error") {
	errorDialogTitle.value = title
	errorMessage.value = String(msg || "Something went wrong.").replace(/<[^>]*>/g, "").trim()
	showErrorDialog.value = true
}

function clearSelection() {
	selectedTasks.value = new Set()
}

function refreshAll() {
	fetchTasks()
	fetchTaskSummary()
	if (viewMode.value === "board") fetchAllColumns()
}

function viewBtnClass(mode) {
	return [
		"p-1.5 rounded-md transition-all",
		viewMode.value === mode
			? "bg-surface-white shadow-sm text-[color:var(--brand-text,#0A84D0)]"
			: "text-ink-gray-5 hover:text-ink-gray-8",
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

	if (tasksResource.data?.tasks) {
		const found = tasksResource.data.tasks.find((t) => t.name === taskName)
		if (found) {
			openEditDialog(found)
			return
		}
	}

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
	if (isCmdOrCtrl && e.key.toLowerCase() === "s" && (showEditTask.value || showCreateDialog.value)) {
		e.preventDefault()
		if (!saving.value) handleSaveTask()
		return
	}
	const t = e.target
	const typing = t && (t.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(t.tagName))
	if (e.key === "/" && !typing && !isCmdOrCtrl && !showEditTask.value && !showCreateDialog.value) {
		e.preventDefault()
		searchInputEl.value?.focus()
	}
}

watch(showEditTask, (val) => {
	if (!val) {
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
	window.addEventListener("keydown", handleGlobalKeydown)
	fetchTasks()
	fetchTaskSummary()
	// board columns load through the board watcher (immediate)
})

onUnmounted(() => {
	window.removeEventListener("keydown", handleGlobalKeydown)
	stopVoice()
	stopAudioRecording(true)
})
</script>

<style scoped>
.kpi[role="button"] {
	cursor: pointer;
	user-select: none;
}
.kpi[role="button"]:focus-visible {
	outline: 2px solid var(--brand, #29adff);
	outline-offset: 2px;
}

/* ---- KPI strip ---- */
.kpi {
	padding: 10px 12px;
	border: 1px solid var(--outline-gray-1, #ededed);
	border-radius: 10px;
	background: var(--surface-cards, #fff);
	box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
	transition: border-color 0.15s, box-shadow 0.15s;
}
.kpi:hover {
	border-color: var(--brand-border, #A6DCFF);
}
.kpi.is-active {
	border-color: var(--brand, #29ADFF);
	background: var(--brand-soft, #E9F6FF);
	box-shadow: 0 0 0 1px var(--brand, #29ADFF) inset;
}

/* ---- Toolbar ---- */
.toolbar-card {
	padding: 10px 12px;
	border: 1px solid var(--outline-gray-1, #ededed);
	border-radius: 10px;
	background: var(--surface-cards, #fff);
	box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}
.qf {
	display: inline-flex;
	align-items: center;
	justify-content: space-between;
	gap: 6px;
	width: 100%;
	height: 28px;
	padding: 0 8px;
	border: 1px dashed var(--outline-gray-3, #d4d4d4);
	border-radius: 6px;
	background: transparent;
	color: var(--ink-gray-6, #6b6b6b);
	font-size: 12px;
	cursor: pointer;
	transition: background-color 0.15s, border-color 0.15s, color 0.15s;
}
.qf:hover {
	background: var(--surface-gray-2, #f3f3f3);
	color: var(--ink-gray-8, #383838);
}
.qf.on {
	border-style: solid;
	border-color: var(--brand-border, #A6DCFF);
	background: var(--brand-soft, #E9F6FF);
	color: var(--brand-text, #0A84D0);
	font-weight: 500;
}
.qf-auto {
	width: auto;
	flex-shrink: 0;
	justify-content: flex-start;
}
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

/* ---- List ---- */
.status-pill {
	display: inline-flex;
	align-items: center;
	gap: 5px;
	max-width: 100%;
	padding: 2px 8px;
	border-radius: 999px;
	font-size: 12px;
	font-weight: 500;
	line-height: 18px;
	white-space: nowrap;
}
.avatar-ring {
	box-shadow: 0 0 0 2px var(--surface-white, #fff);
}
.busy-bar {
	position: absolute;
	inset: 0 0 auto 0;
	z-index: 20;
	height: 2px;
	overflow: hidden;
	border-radius: 12px 12px 0 0;
}
.busy-bar::after {
	content: "";
	position: absolute;
	inset: 0;
	width: 35%;
	background: var(--brand, #29ADFF);
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

/* ---- Board ---- */
.board-col {
	display: flex;
	flex-direction: column;
	flex-shrink: 0;
	width: 290px;
	height: 100%;
	min-height: 0;
	padding: 10px 8px 8px;
	border: 1px solid var(--outline-gray-1, #ededed);
	border-radius: 12px;
	background: var(--surface-gray-1, #f8f8f8);
	transition: background-color 0.15s, border-color 0.15s;
}
.board-col.is-over {
	border-style: dashed;
	border-color: var(--brand, #29ADFF);
	background: var(--brand-soft, #E9F6FF);
}
.board-card {
	padding: 10px 12px;
	border: 1px solid var(--outline-gray-2, #e2e2e2);
	border-radius: 9px;
	background: var(--surface-cards, #fff);
	box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
	cursor: pointer;
	user-select: none;
	transition: border-color 0.15s, box-shadow 0.15s;
}
.board-card:hover {
	border-color: var(--brand-border, #A6DCFF);
	box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
}
.board-card.is-dragging {
	opacity: 0.4;
	border-style: dashed;
}

/* ---- Drawer ---- */
/* checkboxes (column picker, selection) in brand blue */
input[type="checkbox"] {
	accent-color: var(--brand, #29ADFF);
}

.section-title {
	display: block;
	font-size: 11px;
	font-weight: 600;
	letter-spacing: 0.06em;
	text-transform: uppercase;
	color: var(--ink-gray-5, #7c7c7c);
}

.slide-enter-active, .slide-leave-active { transition: transform .3s cubic-bezier(0.4, 0, 0.2, 1); }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }

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
	font-family: "Inter", ui-sans-serif, system-ui, sans-serif;
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