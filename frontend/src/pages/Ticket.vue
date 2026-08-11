<template>
  <div class="space-y-3 p-1 flex flex-col h-full overflow-hidden font-sans min-h-0">
	<div class="grid grid-cols-2 lg:grid-cols-6 gap-3 flex-shrink-0">
		<Card 
			v-for="stat in kpiStats" 
			:key="stat.label" 
			:class="[
				'!shadow-xs bg-white cursor-pointer transition-all duration-150 border active:scale-[0.98]',
				'border-slate-200/80 hover:border-slate-300'
			]"
			@click="filterByStat(stat.label)"
		>
			<div class="flex items-center justify-between">
				<span class="text-xs font-medium text-slate-500">{{ stat.label }}</span>
				<component :is="stat.icon" class="w-4 h-4" :class="stat.color" />
			</div>

			<div class="text-xl font-bold mt-1 text-slate-900 flex items-center h-7">
				<template v-if="tickets.loading">
					<div class="w-4 h-4 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
				</template>
				<span v-else>{{ stat.value }}</span>
			</div>
		</Card>
	</div>

	<div class="bg-white p-3 rounded-lg border border-slate-200 shadow-xs flex flex-col gap-2.5 flex-shrink-0">
	  <!-- Top Row: Search & Actions -->
	  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 w-full pb-2 border-b border-slate-100">
		<div class="relative w-full sm:w-80">
		  <IconSearch class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
		  <input 
			v-model="searchQuery"
			type="text" 
			placeholder="Search subject or ID..." 
			class="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-md focus:bg-white focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
		  />
		</div>

		<div class="flex items-center gap-2 ml-auto sm:ml-0">
		  <!-- Dynamic Multi-Field Filter Popover -->
		  <Popover placement="bottom-end">
			<template #target="{ open, togglePopover }">
			  <Button
				variant="outline"
				:class="[
				  '!px-2.5 !h-8 border transition-all flex items-center gap-1.5 rounded-md text-xs font-medium',
				  activeFilterCount > 0
					? 'border-blue-500 text-blue-600 bg-blue-50/50'
					: '!text-slate-600 border-slate-200 hover:bg-slate-50'
				]"
				@click="syncActiveFilterRules(); togglePopover()"
				title="Filter Tickets"
			  >
				<template #prefix><IconFilter class="w-3.5 h-3.5" :class="activeFilterCount > 0 ? 'text-blue-600' : 'text-slate-500'" /></template>
				<span>Filter</span>
				<span v-if="activeFilterCount > 0" class="bg-blue-600 text-white rounded-full text-[10px] font-bold px-1.5 py-0.2 leading-none">
				  {{ activeFilterCount }}
				</span>
			  </Button>
			</template>
			<template #body-main="{ close }">
			  <div class="w-80 p-3 bg-white rounded-lg shadow-lg border border-slate-200 text-xs space-y-3">
				<div class="flex items-center justify-between pb-2 border-b border-slate-100">
				  <div class="flex items-center gap-1.5 font-semibold text-slate-800 text-xs">
					<IconFilter class="w-3.5 h-3.5 text-blue-600" />
					<span>Filter Tickets</span>
				  </div>
				  <button 
					v-if="hasActiveFilters"
					@click="resetFilters" 
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
					class="flex items-center gap-1.5 bg-slate-50 p-1.5 rounded-md border border-slate-200/80"
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

					<span class="text-[10px] font-semibold text-slate-400 shrink-0">=</span>

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
					  class="p-1 hover:bg-red-50 rounded text-slate-400 hover:text-red-500 transition-colors shrink-0 cursor-pointer"
					  title="Remove Filter"
					>
					  <IconX class="w-3.5 h-3.5" />
					</button>
				  </div>
				</div>

				<div class="flex items-center justify-between pt-2 border-t border-slate-100">
				  <button
					@click="addFilterRule"
					class="inline-flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-700 px-2 py-1 rounded transition-colors cursor-pointer"
				  >
					<IconPlus class="w-3.5 h-3.5" /> Add Filter
				  </button>

				  <Button 
					variant="solid" 
					class="!bg-blue-600 !text-white !px-3 !h-7 text-xs font-medium rounded-md shadow-xs"
					@click="applyFilterRules(); close()"
				  >
					Apply
				  </Button>
				</div>
			  </div>
			</template>
		  </Popover>

		  <!-- Column Picker Popover (Frappe UI Style) -->
		  <Popover placement="bottom-end">
			<template #target="{ open, togglePopover }">
			  <Button
				variant="outline"
				class="!text-slate-600 !px-2.5 !h-8 border border-slate-200 hover:bg-slate-50 transition-all flex items-center gap-1.5 rounded-md text-xs font-medium"
				@click="togglePopover"
				title="Customize Columns"
			  >
				<template #prefix><IconSlidersHorizontal class="w-3.5 h-3.5 text-slate-500" /></template>
				<span class="hidden md:inline">Columns</span>
			  </Button>
			</template>
			<template #body-main="{ close }">
			  <div class="w-60 p-3 bg-white rounded-lg shadow-lg border border-slate-200 text-xs space-y-2.5">
				<div class="flex items-center justify-between pb-2 border-b border-slate-100">
				  <span class="font-semibold text-slate-800 text-xs">Columns</span>
				  <button 
					@click="resetColumns" 
					class="text-[11px] font-medium text-blue-600 hover:text-blue-700 flex items-center gap-1 cursor-pointer"
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
					class="w-full pl-7 pr-2 py-1 text-xs bg-slate-50 border border-slate-200 rounded-md focus:bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
				  />
				  <IconSearch class="w-3 h-3 absolute left-2 top-2 text-slate-400" />
				</div>

				<div class="max-h-60 overflow-y-auto space-y-0.5 custom-scrollbar pr-1">
				  <div 
					v-for="(colKey, index) in activeColumnKeys" 
					:key="colKey"
					v-show="!columnSearchQuery || getColumnLabel(colKey).toLowerCase().includes(columnSearchQuery.toLowerCase())"
					class="flex items-center justify-between p-1 rounded hover:bg-slate-50 group transition-all"
				  >
					<label class="flex items-center gap-2 cursor-pointer select-none truncate flex-1 mr-1">
					  <input
						type="checkbox"
						:checked="true"
						:disabled="colKey === 'subject'"
						@change="toggleColumn(colKey)"
						class="rounded text-blue-600 focus:ring-blue-500 h-3.5 w-3.5 cursor-pointer disabled:opacity-40"
					  />
					  <span :class="colKey === 'subject' ? 'font-semibold text-slate-900' : 'text-slate-700'" class="truncate">
						{{ getColumnLabel(colKey) }}
					  </span>
					  <span v-if="colKey === 'subject'" class="text-[9px] bg-slate-100 text-slate-400 px-1 rounded font-medium ml-auto">Fixed</span>
					</label>

					<div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
					  <button
						@click.stop="moveColumnUp(index)"
						:disabled="index === 0"
						class="p-0.5 hover:bg-slate-200 rounded text-slate-500 disabled:opacity-20 cursor-pointer"
						title="Move Up"
					  >
						<IconArrowUp class="w-3 h-3" />
					  </button>
					  <button
						@click.stop="moveColumnDown(index)"
						:disabled="index === activeColumnKeys.length - 1"
						class="p-0.5 hover:bg-slate-200 rounded text-slate-500 disabled:opacity-20 cursor-pointer"
						title="Move Down"
					  >
						<IconArrowDown class="w-3 h-3" />
					  </button>
					</div>
				  </div>

				  <!-- Inactive columns available to add -->
				  <div v-if="inactiveColumns.length > 0 && !columnSearchQuery" class="pt-2 border-t border-slate-100 mt-1">
					<span class="text-[10px] font-medium text-slate-400 uppercase tracking-wider block mb-1">More Columns</span>
					<div
					  v-for="col in inactiveColumns"
					  :key="col.key"
					  class="flex items-center justify-between p-1 rounded hover:bg-slate-50 cursor-pointer"
					  @click="toggleColumn(col.key)"
					>
					  <label class="flex items-center gap-2 cursor-pointer select-none truncate">
						<input
						  type="checkbox"
						  :checked="false"
						  @change="toggleColumn(col.key)"
						  class="rounded text-blue-600 focus:ring-blue-500 h-3.5 w-3.5 cursor-pointer"
						/>
						<span class="text-slate-500 truncate">{{ col.label }}</span>
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
			class="!text-slate-600 !px-2.5 !h-8 border border-slate-200 hover:bg-slate-50 transition-all rounded-md"
			@click="tickets.reload()"
		  >
			<template #prefix><IconRefresh class="w-3.5 h-3.5 text-slate-500" /></template>
		  </Button>

		  <!-- Actions Dropdown / New Ticket Button -->
		  <Dropdown
			v-slot="{ open }"
			v-if="isAdmin && selectedTickets.size > 0"
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
			v-else
			variant="solid"
			class="!text-xs !px-4 !h-8 rounded-md transition-all font-medium"
			style="background-color: var(--primary-color);"
			@click="isEditMode=false; resetForm(); customerResource.reload(); departmentResource.reload(); showCreateDialog=true"
		>
			<template #prefix><IconPlus class="w-3.5 h-3.5" /></template> New Ticket
		</Button>
		</div>
	  </div>

	  <!-- Bottom Row: Quick Filter Bar -->
	  <div class="filter-row flex flex-nowrap overflow-x-auto pb-1 gap-2 w-full custom-scrollbar sm:flex-wrap sm:overflow-visible sm:pb-0 sm:items-center sm:gap-2">
		<!-- Client Autocomplete Filter -->
		<div class="w-36 shrink-0">
			<Autocomplete
			  ref="customerAutocomplete"
			  :options="customerFilterSelectOptions"
			  :modelValue="selectedFilters.customer"
			  @update:modelValue="val => selectedFilters.customer = val?.value ?? val ?? ''"
			  :compare-fn="compareOption"
			  :max-options="100"
			>
			  <template #target>
				<button
				  type="button"
				  @click="() => customerAutocomplete?.togglePopover()"
				  :class="[
					'inline-flex items-center justify-between gap-2 outline-none text-xs rounded min-h-7 h-7 px-2 border transition-colors w-full cursor-pointer',
					selectedFilters.customer !== ''
					  ? 'border-blue-500 text-blue-600 bg-blue-50/50 font-medium'
					  : 'border-[--surface-gray-2] bg-surface-gray-2 hover:border-outline-gray-modals hover:bg-surface-gray-3 text-ink-gray-7'
				  ]"
				>
				  <span class="truncate">{{ getClientLabel(selectedFilters.customer) }}</span>
				  <FeatherIcon name="chevron-down" class="size-4 text-ink-gray-4 ml-auto shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<!-- Department Autocomplete Filter -->
		<div class="w-36 shrink-0">
			<Autocomplete
			  ref="departmentAutocomplete"
			  :options="departmentFilterSelectOptions"
			  :modelValue="selectedFilters.department"
			  @update:modelValue="val => selectedFilters.department = val?.value ?? val ?? ''"
			  :compare-fn="compareOption"
			  :max-options="100"
			>
			  <template #target>
				<button
				  type="button"
				  @click="() => departmentAutocomplete?.togglePopover()"
				  :class="[
					'inline-flex items-center justify-between gap-2 outline-none text-xs rounded min-h-7 h-7 px-2 border transition-colors w-full cursor-pointer',
					selectedFilters.department !== ''
					  ? 'border-blue-500 text-blue-600 bg-blue-50/50 font-medium'
					  : 'border-[--surface-gray-2] bg-surface-gray-2 hover:border-outline-gray-modals hover:bg-surface-gray-3 text-ink-gray-7'
				  ]"
				>
				  <span class="truncate">{{ getDepartmentLabel(selectedFilters.department) }}</span>
				  <FeatherIcon name="chevron-down" class="size-4 text-ink-gray-4 ml-auto shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<!-- Status Autocomplete Filter -->
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
				  :class="[
					'inline-flex items-center justify-between gap-2 outline-none text-xs rounded min-h-7 h-7 px-2 border transition-colors w-full cursor-pointer',
					selectedFilters.status !== ''
					  ? 'border-blue-500 text-blue-600 bg-blue-50/50 font-medium'
					  : 'border-[--surface-gray-2] bg-surface-gray-2 hover:border-outline-gray-modals hover:bg-surface-gray-3 text-ink-gray-7'
				  ]"
				>
				  <span class="truncate">{{ getStatusLabel(selectedFilters.status) }}</span>
				  <FeatherIcon name="chevron-down" class="size-4 text-ink-gray-4 ml-auto shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<!-- Priority Autocomplete Filter -->
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
				  :class="[
					'inline-flex items-center justify-between gap-2 outline-none text-xs rounded min-h-7 h-7 px-2 border transition-colors w-full cursor-pointer',
					selectedFilters.priority !== ''
					  ? 'border-blue-500 text-blue-600 bg-blue-50/50 font-medium'
					  : 'border-[--surface-gray-2] bg-surface-gray-2 hover:border-outline-gray-modals hover:bg-surface-gray-3 text-ink-gray-7'
				  ]"
				>
				  <span class="truncate">{{ getPriorityLabel(selectedFilters.priority) }}</span>
				  <FeatherIcon name="chevron-down" class="size-4 text-ink-gray-4 ml-auto shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<!-- Raised By Autocomplete Filter -->
		<div class="w-36 shrink-0">
			<Autocomplete
			  ref="raisedByAutocomplete"
			  :options="raisedByFilterSelectOptions"
			  :modelValue="selectedFilters.raised_by"
			  @update:modelValue="val => selectedFilters.raised_by = val?.value ?? val ?? ''"
			  :compare-fn="compareOption"
			  :max-options="100"
			>
			  <template #target>
				<button
				  type="button"
				  @click="() => raisedByAutocomplete?.togglePopover()"
				  :class="[
					'inline-flex items-center justify-between gap-2 outline-none text-xs rounded min-h-7 h-7 px-2 border transition-colors w-full cursor-pointer',
					selectedFilters.raised_by !== ''
					  ? 'border-blue-500 text-blue-600 bg-blue-50/50 font-medium'
					  : 'border-[--surface-gray-2] bg-surface-gray-2 hover:border-outline-gray-modals hover:bg-surface-gray-3 text-ink-gray-7'
				  ]"
				>
				  <span class="truncate">{{ getUserLabel(selectedFilters.raised_by, 'Raised By') }}</span>
				  <FeatherIcon name="chevron-down" class="size-4 text-ink-gray-4 ml-auto shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<Button 
		  v-if="hasActiveFilters"
		  variant="ghost" 
		  class="!text-red-500 hover:!bg-red-50 !px-2 !h-7 text-xs font-medium shrink-0"
		  @click="resetFilters"
		>
		  <template #prefix><IconX class="w-3.5 h-3.5" /></template>
		  Clear
		</Button>
	  </div>
	</div>

	<div class="flex-1 overflow-y-auto md:overflow-hidden flex flex-col min-h-0">
	  <div class="bg-white rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col min-h-[420px] md:min-h-0 md:flex-1 md:overflow-hidden">
		  <ListView
		  class="h-full flex flex-col min-h-0"
		  :columns="columns"
		  :rows="tickets.data?.tickets || []" 
		  :options="{ 
			  selectable: isAdmin, 
			  showTooltip: true, 
			  resizeColumn: true, 
			  onRowClick: (row) => openEditDialog(row) 
		  }"
		  row-key="name"
		  v-model:selections="selectedTickets"
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
			  v-for="row in (tickets.data?.tickets || [])" 
			  :key="row.name" 
			  :row="row"
			  >
			<ListRowItem :item="item">
				
				<template v-if="column.key === 'name'">
				<span class="font-bold text-blue-600">#{{ row.name }}</span>
				</template>

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

				<template v-if="column.key === 'status'">
				<div class="flex items-center">
					<div class="h-2 w-2 rounded-full mr-2 shrink-0" :class="getStatusColor(item)" />
					<span class="text-sm truncate">
					{{ item }}
					<span v-if="row.is_overdue" class="text-red-500 font-bold ml-1 text-xs">
						- (Overdue)
					</span>
					</span>
				</div>
				</template>

				<template v-if="column.key === 'priority'">
				<Badge :theme="getPriorityTheme(item)" variant="subtle" :label="item" />
				</template>

				<template v-if="column.key === 'raised_by'">
				<span class="text-xs text-slate-600 font-medium truncate">
					{{ getUserLabel(row.raised_by) }}
				</span>
				</template>

				<template v-if="column.key === 'customer'">
				<span class="text-xs text-slate-600 font-medium truncate">
					{{ getClientLabel(row.customer) }}
				</span>
				</template>

				<template v-if="column.key === 'department'">
				<span class="text-xs text-slate-600 font-medium truncate">
					{{ getDepartmentLabel(row.department) }}
				</span>
				</template>

				<template v-if="column.key === 'creation'">
				<div class="flex items-center gap-2 text-slate-500 whitespace-nowrap">
					<IconClock class="w-3.5 h-3.5" v-if="row.creation"/>
					<span class="text-xs font-medium">
					{{ row.creation ? formatDateTime(row.creation) : '' }}
					</span>
				</div>
				</template>

				<template v-if="column.key === 'first_response_time'">
				<div v-if="row.first_responded_on" class="flex items-center" v-tooltip="formatDateTime(row.first_responded_on)">
					<Badge 
						theme="blue" 
						variant="subtle" 
						class="font-semibold !px-2.5 !py-1 text-xs shrink-0"
					>
						{{ formatDuration(row.first_response_time) }}
					</Badge>
				</div>
				<span v-else class="text-xs text-slate-400 font-medium pl-2">—</span>
				</template>

				<template v-if="column.key === 'closed_time'">
				<div v-if="row.closed_on" class="flex items-center" v-tooltip="formatDateTime(row.closed_on)">
					<Badge 
						theme="green" 
						variant="subtle" 
						class="font-semibold !px-2.5 !py-1 text-xs shrink-0"
					>
						{{ formatDuration(row.closed_time) }}
					</Badge>
				</div>
				<span v-else class="text-xs text-slate-400 font-medium pl-2">—</span>
				</template>

			</ListRowItem>
			</ListRow>
		  </ListRows>
		  </div>
		  </ListView>
		<!-- Pagination controls -->
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

	<Dialog v-model="showBulkDeleteDialog" 
		:disable-outside-click-to-close="true"
		:options="{ 
		title: 'Delete Selected Tickets', 
		size: 'sm',
		actions: [
			{ label: 'Delete', variant: 'solid', theme: 'red', loading: saving, onClick: executeBulkDelete },
			{ label: 'Cancel', variant: 'ghost', onClick: () => (showBulkDeleteDialog = false) }
		] 
		}">
	  <template #body-content>
		<p class="text-sm text-slate-600 leading-relaxed py-2">
		  Are you sure you want to permanently delete the <span class="font-bold text-slate-900">{{ selectedTickets.size }}</span> selected ticket(s)? This action cannot be undone.
		</p>
	  </template>
	</Dialog>

	<Dialog v-model="showErrorDialog" 
		:disable-outside-click-to-close="true"
		:options="{ 
		title: 'Cannot Delete', 
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

	<Dialog v-model="showCreateDialog" :disable-outside-click-to-close="true" :options="dialogOptions">
	  <template #body-content>
		<div class="space-y-6 py-2">
		  <p v-if="ticketFormError" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
			{{ ticketFormError }}
		  </p>
		  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<div class="space-y-4">
			  <div :class="['rounded-lg transition-all', { 'field-invalid-blink': ticketInvalidFields.subject }]">
				<FormControl label="Subject *" v-model="ticketForm.subject" />
			  </div>
			  <div class="space-y-1.5">
				<label class="block text-xs text-ink-gray-5">Customer</label>
				<Autocomplete
				  ref="createCustomerAutocomplete"
				  :options="customerFilterSelectOptions"
				  :modelValue="ticketForm.customer"
				  @update:modelValue="val => ticketForm.customer = val?.value ?? val ?? ''"
				  :compare-fn="compareOption"
				  :max-options="100"
				>
				  <template #target>
					<button
					  type="button"
					  @click="() => createCustomerAutocomplete?.togglePopover()"
					  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
					>
					  <span class="truncate">{{ getClientLabel(ticketForm.customer) }}</span>
					  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
					</button>
				  </template>
				</Autocomplete>
			  </div>
			  <div class="space-y-1.5">
				<label class="block text-xs text-ink-gray-5">Raised By</label>
				<Autocomplete
				  ref="createRaisedByAutocomplete"
				  :options="raisedByFilterOptions"
				  :modelValue="ticketForm.raised_by"
				  @update:modelValue="val => ticketForm.raised_by = val?.value ?? val ?? ''"
				  :compare-fn="compareOption"
				  :max-options="100"
				>
				  <template #target>
					<button
					  type="button"
					  :disabled="isFieldDisabled"
					  @click="() => createRaisedByAutocomplete?.togglePopover()"
					  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
					>
					  <span class="truncate">{{ getUserLabel(ticketForm.raised_by, 'Select User') }}</span>
					  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
					</button>
				  </template>
				</Autocomplete>
			  </div>
			</div>
			<div class="space-y-4">
			  <div class="grid grid-cols-2 gap-4">
				<div class="space-y-1.5">
				  <label class="block text-xs text-ink-gray-5">Type</label>
				  <Autocomplete
					ref="createTicketTypeAutocomplete"
					:options="['Bug', 'Support', 'Technical']"
					:modelValue="ticketForm.ticket_type"
					@update:modelValue="val => ticketForm.ticket_type = val?.value ?? val ?? ''"
					:compare-fn="compareOption"
				  >
					<template #target>
					  <button
						type="button"
						@click="() => createTicketTypeAutocomplete?.togglePopover()"
						class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
					  >
						<span class="truncate">{{ ticketForm.ticket_type || 'Type' }}</span>
						<FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
					  </button>
					</template>
				  </Autocomplete>
				</div>
				<div class="space-y-1.5">
				  <label class="block text-xs text-ink-gray-5">Priority</label>
				  <Autocomplete
					ref="createPriorityAutocomplete"
					:options="['Low', 'Medium', 'High', 'Urgent']"
					:modelValue="ticketForm.priority"
					@update:modelValue="val => ticketForm.priority = val?.value ?? val ?? ''"
					:compare-fn="compareOption"
				  >
					<template #target>
					  <button
						type="button"
						@click="() => createPriorityAutocomplete?.togglePopover()"
						class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
					  >
						<span class="truncate">{{ getPriorityLabel(ticketForm.priority) }}</span>
						<FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
					  </button>
					</template>
				  </Autocomplete>
				</div>
			  </div>
			  <div class="space-y-1.5">
				<label class="block text-xs text-ink-gray-5">Department</label>
				<Autocomplete
				  ref="createDepartmentAutocomplete"
				  :options="departmentFilterSelectOptions"
				  :modelValue="ticketForm.department"
				  @update:modelValue="val => ticketForm.department = val?.value ?? val ?? ''"
				  :compare-fn="compareOption"
				  :max-options="100"
				>
				  <template #target>
					<button
					  type="button"
					  @click="() => createDepartmentAutocomplete?.togglePopover()"
					  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
					>
					  <span class="truncate">{{ getDepartmentLabel(ticketForm.department) }}</span>
					  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
					</button>
				  </template>
				</Autocomplete>
			  </div>
			</div>
		  </div>
		  <div class="space-y-2 border-t pt-4">
			<label class="text-xs font-medium text-slate-600 uppercase tracking-wider">Description</label>
			<div class="border rounded-lg bg-white shadow-sm overflow-hidden min-h-[200px]">
			  <TextEditor
				editor-class="prose-sm max-w-none p-6 outline-none"
				:content="ticketForm.description"
				@change="(val) => (ticketForm.description = val)"
				:fixed-menu="true"
			  />
			</div>
		  </div>
		</div>
	  </template>
	</Dialog>

	<Transition name="slide">
		<div v-if="showEditTicket" class="fixed inset-0 flex justify-end z-50">
			<div class="absolute inset-0 bg-slate-900/20 backdrop-blur-[2px]" @click="showEditTicket=false"></div>
			
			<div class="relative w-full md:max-w-8xl lg:max-w-8xl h-full bg-white flex flex-col md:flex-row shadow-2xl border-l overflow-y-auto md:overflow-hidden">
				<div v-if="!editPanelReady" class="flex-1 grid place-items-center bg-slate-50/30 min-h-0">
					<div class="flex items-center gap-3 text-slate-500">
						<div class="w-5 h-5 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
						<span class="text-sm font-medium">Loading ticket details...</span>
					</div>
				</div>

				<div v-else class="flex w-full h-full flex-col md:flex-row">
					<!-- Left Column: Activity (Full Width) -->
					<div class="h-[400px] md:h-full md:w-[60%] flex flex-col bg-white min-h-0 border-b md:border-b-0 md:border-r border-slate-100 shrink-0">
						<header class="p-4 border-b bg-white flex justify-between items-center shrink-0 shadow-sm z-10">
							<h3 class="text-sm font-bold text-slate-800">Activity</h3>
						</header>
						
						<div class="flex-grow md:flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar relative before:absolute before:inset-y-0 before:left-[40px] before:w-0.5 before:bg-slate-200/50">
							<!-- Timeline Activity Comments -->
							<div v-for="c in comments.data || []" :key="c.name" class="relative pl-12 group">
								<!-- Timeline Avatar absolute aligned on the rail line -->
								<div class="absolute left-0 top-1 z-10">
									<Avatar 
										:image="getUserAvatarImage(c.owner)"
										:label="getUserLabel(c.owner) || 'User'" 
										size="md" 
										class="ring-4 ring-white shadow-sm shrink-0" 
									/>
								</div>

								<!-- Comment Card -->
								<div class="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm hover:shadow-md transition-all duration-200">
									<div class="flex items-center justify-between mb-2">
										<div class="flex items-center gap-1.5 text-xs">
											<span class="font-bold text-slate-800">{{ getUserLabel(c.owner) }}</span>
											<span class="text-slate-300">·</span>
											<span class="text-slate-400 font-medium">{{ dayjs(c.creation).fromNow() }}</span>
										</div>

										<!-- Comment Edit/Delete Actions -->
										<div class="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity" v-if="c.owner === session.user">
											<button 
												@click="startEditing(c)"
												class="p-1 hover:bg-slate-50 rounded text-slate-400 hover:text-blue-600 transition-colors"
												title="Edit Comment"
											>
												<IconEdit3 class="w-3.5 h-3.5" />
											</button>
											<button 
												@click="handleDeleteComment(c.name)"
												class="p-1 hover:bg-red-50 rounded text-slate-400 hover:text-red-600 transition-colors"
												title="Delete Comment"
											>
												<IconTrash2 class="w-3.5 h-3.5" />
											</button>
										</div>
									</div>

									<div class="text-sm text-slate-600 leading-relaxed">
										<div v-if="editingCommentName === c.name" class="space-y-3">
											<FormControl 
												type="textarea"
												v-model="editContent" 
												class="w-full rounded-xl border border-slate-200 p-2 text-sm focus:ring-1 focus:ring-blue-500 outline-none resize-none"
											/>
											<div class="flex justify-end gap-2">
												<Button size="sm" variant="ghost" @click="cancelEdit">Cancel</Button>
												<Button size="sm" variant="solid" @click="handleUpdateComment(c.name)" class="!bg-blue-600">Save</Button>
											</div>
										</div>
										<div v-else class="prose prose-sm max-w-none text-slate-600" v-html="c.content"></div>
									</div>
								</div>
							</div>

							<!-- Empty State Placeholder -->
							<div v-if="!(comments.data && comments.data.length > 0)" class="flex flex-col items-center justify-center py-8 text-slate-400 bg-white rounded-2xl border border-dashed border-slate-200/60 mx-2 my-2 shadow-sm">
								<IconMessageSquare class="w-8 h-8 mb-2 opacity-25 text-slate-500" />
								<p class="text-[11px] font-semibold italic text-slate-400">No comments yet. Start the conversation!</p>
							</div>
						</div>

						<div class="p-4 bg-white border-t shrink-0">
							<CommentBox
								v-model="newComment"
								:avatar="getUserAvatarImage(session.user)"
								:user="session.user"
								:userName="session.userFullName"
								placeholder="Type a message..."
								:loading="comments.loading"
								@submit="addComment"
							/>
						</div>
					</div>

					<!-- Right Column: Ticket Details Form (40% Width) -->
					<div class="w-full md:w-[40%] md:shrink-0 flex flex-col bg-white min-h-0">
						<header class="p-4 border-b flex justify-between items-center bg-white shrink-0 shadow-sm z-10">
							<div class="min-w-0 flex-1 mr-2">
								<div class="flex flex-wrap items-center gap-1.5">
									<span class="text-[10px] font-bold text-blue-600 bg-blue-50 border border-blue-100 rounded-md px-2 py-0.5 uppercase tracking-wider">{{ ticketForm.name }}</span>
									<Badge v-if="ticketForm.first_responded_on" theme="blue" variant="subtle" class="font-semibold !px-2 !py-0.5 text-[10px]" v-tooltip="'First Response: ' + formatDateTime(ticketForm.first_responded_on)">
										Responded in {{ formatDuration(ticketForm.first_response_time) }}
									</Badge>
									<Badge v-if="ticketForm.closed_on" theme="green" variant="subtle" class="font-semibold !px-2 !py-0.5 text-[10px]" v-tooltip="'Closed on: ' + formatDateTime(ticketForm.closed_on)">
										Closed in {{ formatDuration(ticketForm.closed_time) }}
									</Badge>
								</div>
								<h2 class="font-extrabold text-slate-900 text-base md:text-lg mt-2 truncate max-w-full" :title="ticketForm.subject">{{ ticketForm.subject }}</h2>
							</div>
							<div class="flex items-center gap-1.5 shrink-0">
								<Button variant="solid" size="sm" theme="blue" :loading="saving" @click="openTaskCreateDialog(ticketForm)" class="shadow-sm !px-2 sm:!px-3 text-xs">Create Task</Button>
								<Button variant="solid" size="sm" :loading="saving" @click="handleSaveTicket" class="shadow-sm !px-2 sm:!px-3 text-xs">Save</Button>
								<Button variant="ghost" size="sm" @click="showEditTicket=false" class="text-slate-400 hover:text-slate-600 !p-1">
									<IconX class="w-4 h-4"/>
								</Button>
							</div>
						</header>

						<div class="flex-grow md:flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
							<!-- Metadata Card -->
							<div class="bg-slate-50/50 rounded-2xl border border-slate-100 p-4 space-y-4 shadow-sm mb-6">
								<div class="grid grid-cols-2 gap-4">
									<div class="space-y-1.5 shadow-sm">
										<label class="block text-xs text-ink-gray-5">Status</label>
										<Autocomplete
										  ref="editStatusAutocomplete"
										  :options="ticketStatusOptions"
										  :modelValue="ticketForm.status"
										  @update:modelValue="val => ticketForm.status = val?.value ?? val ?? ''"
										  :compare-fn="compareOption"
										>
										  <template #target>
											<button
											  type="button"
											  @click="() => editStatusAutocomplete?.togglePopover()"
											  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
											>
											  <span class="truncate">{{ getStatusLabel(ticketForm.status) }}</span>
											  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
											</button>
										  </template>
										</Autocomplete>
									</div>

									<div class="space-y-1.5 shadow-sm">
										<label class="block text-xs text-ink-gray-5">Priority</label>
										<Autocomplete
										  ref="editPriorityAutocomplete"
										  :options="['Low','Medium','High','Urgent']"
										  :modelValue="ticketForm.priority"
										  @update:modelValue="val => ticketForm.priority = val?.value ?? val ?? ''"
										  :compare-fn="compareOption"
										>
										  <template #target>
											<button
											  type="button"
											  @click="() => editPriorityAutocomplete?.togglePopover()"
											  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
											>
											  <span class="truncate">{{ getPriorityLabel(ticketForm.priority) }}</span>
											  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
											</button>
										  </template>
										</Autocomplete>
									</div>
								</div>

								<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 border-t pt-4">
									<div class="space-y-1.5 shadow-sm">
										<label class="block text-xs text-ink-gray-5">Customer</label>
										<Autocomplete
										  ref="editCustomerAutocomplete"
										  :options="customerFilterOptions"
										  :modelValue="ticketForm.customer"
										  @update:modelValue="val => ticketForm.customer = val?.value ?? val ?? ''"
										  :compare-fn="compareOption"
										  :max-options="100"
										>
										  <template #target>
											<button
											  type="button"
											  @click="() => editCustomerAutocomplete?.togglePopover()"
											  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
											>
											  <span class="truncate">{{ getClientLabel(ticketForm.customer) }}</span>
											  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
											</button>
										  </template>
										</Autocomplete>
									</div>

									<div class="space-y-1.5 shadow-sm">
										<label class="block text-xs text-ink-gray-5">Raised By</label>
										<Autocomplete
										  ref="editRaisedByAutocomplete"
										  :options="raisedByFilterOptions"
										  :modelValue="ticketForm.raised_by"
										  @update:modelValue="val => ticketForm.raised_by = val?.value ?? val ?? ''"
										  :compare-fn="compareOption"
										  :max-options="100"
										>
										  <template #target>
											<button
											  type="button"
											  :disabled="isFieldDisabled"
											  @click="() => editRaisedByAutocomplete?.togglePopover()"
											  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
											>
											  <span class="truncate">{{ getUserLabel(ticketForm.raised_by, 'Select User') }}</span>
											  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
											</button>
										  </template>
										</Autocomplete>
									</div>

									<div class="space-y-1.5 shadow-sm">
										<label class="block text-xs text-ink-gray-5">Department</label>
										<Autocomplete
										  ref="editDepartmentAutocomplete"
										  :options="departmentFilterOptions"
										  :modelValue="ticketForm.department"
										  @update:modelValue="val => ticketForm.department = val?.value ?? val ?? ''"
										  :compare-fn="compareOption"
										  :max-options="100"
										>
										  <template #target>
											<button
											  type="button"
											  @click="() => editDepartmentAutocomplete?.togglePopover()"
											  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
											>
											  <span class="truncate">{{ getDepartmentLabel(ticketForm.department) }}</span>
											  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
											</button>
										  </template>
										</Autocomplete>
									</div>
								</div>
							</div>

							
							<!-- Description Field -->
							<div class="space-y-2 border-t pt-4">
								<label class="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest block">Description</label>
								<div class="border border-slate-200 rounded-2xl bg-white shadow-sm overflow-hidden min-h-[200px] focus-within:border-blue-300 focus-within:ring-2 focus-within:ring-blue-100/50 transition-all">
									<TextEditor
										editor-class="prose-sm max-w-none p-4 outline-none bg-white min-h-[200px]"
										:content="ticketForm.description"
										@change="(val) => (ticketForm.description = val)"
										:fixed-menu="true"
									/>
								</div>
							</div>

							<!-- Resolution Field -->
							<div class="space-y-2 border-t pt-4 pb-2" >
								<label class="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest block">Resolution</label>
								<div class="border border-slate-200 rounded-2xl bg-white shadow-sm overflow-hidden min-h-[200px] focus-within:border-blue-300 focus-within:ring-2 focus-within:ring-blue-100/50 transition-all">
									<TextEditor
										editor-class="prose-sm max-w-none p-4 outline-none bg-white min-h-[200px]"
										:content="ticketForm.resolution_details"
										@change="(val) => (ticketForm.resolution_details = val)"
										:fixed-menu="true"
									/>
								</div>
							</div>

							<!-- Attachments Field -->
							<div class="pt-4 border-t border-slate-200">
								<label class="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest block mb-3">
									Attachments
								</label>
								<div class="space-y-4">
									<FileUploader @success="handleFileUploadTicket">
										<template #default="{ openFileSelector }">
											<button 
												@click="openFileSelector" 
												class="w-full flex items-center justify-center gap-2 border-2 border-dashed border-slate-200 rounded-2xl p-4 text-slate-500 hover:border-blue-400 hover:text-blue-500 hover:bg-blue-50/30 transition-all group"
											>
												<IconPaperclip class="w-4 h-4" />
												<span class="text-xs font-semibold">Add Files</span>
											</button>
										</template>
									</FileUploader>
									
									<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
										<div 
											v-for="(file, idx) in ticketForm.attachments" 
											:key="idx" 
											class="group flex items-center justify-between bg-white border border-slate-200 rounded-xl shadow-sm hover:border-blue-300 hover:shadow-md transition-all overflow-hidden p-2"
										>
											<a 
												:href="file.file_url" 
												target="_blank" 
												class="flex flex-1 items-center gap-2.5 truncate"
											>
												<div class="h-8 w-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
													<IconBriefcase class="w-4 h-4" /> 
												</div>
												<div class="truncate text-left">
													<span class="block truncate font-semibold text-slate-700 text-xs group-hover:text-blue-600 transition-colors">
														{{ file.file_name }}
													</span>
													<span class="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Attachment</span>
												</div>
											</a>

											<button 
												@click.stop="removeAttachmentTicket(idx)" 
												class="p-2 ml-1 hover:bg-red-50 rounded-lg text-slate-400 hover:text-red-500 transition-colors"
												title="Remove file"
											>
												<IconX class="w-4 h-4" />
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
	</Transition>

	<Dialog v-model="showCreateTaskDialog" 
		:disable-outside-click-to-close="true"
		:options="{ 
		title: 'Create Task', 
		size: '4xl',
		actions: [
			{ label: 'Create Task', variant: 'solid', loading: taskSaving, onClick: handleSaveTask },
			{ label: 'Cancel', variant: 'ghost', onClick: () => (showCreateTaskDialog = false) }
		] 
		}">
	  <template #body-content>
		<div class="space-y-6 py-2">
		  <p v-if="taskFormError" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
			{{ taskFormError }}
		  </p>
		  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
			<div class="space-y-4">
			  <div :class="['rounded-lg transition-all', { 'field-invalid-blink': taskInvalidFields.subject }]">
				<FormControl type="text" label="Subject *" v-model="newTask.subject" />
			  </div>
			  <div class="space-y-1.5">
				<label class="block text-xs text-ink-gray-5">Project</label>
				<Autocomplete
				  ref="taskProjectAutocomplete"
				  :options="projectResource.data || []"
				  :modelValue="newTask.project"
				  @update:modelValue="val => newTask.project = val?.value ?? val ?? ''"
				  :compare-fn="compareOption"
				  :max-options="100"
				>
				  <template #target>
					<button
					  type="button"
					  @click="() => taskProjectAutocomplete?.togglePopover()"
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
				  ref="taskDepartmentAutocomplete"
				  :options="departmentResourceTask.data || []"
				  :modelValue="newTask.department"
				  @update:modelValue="val => newTask.department = val?.value ?? val ?? ''"
				  :compare-fn="compareOption"
				  :max-options="100"
				>
				  <template #target>
					<button
					  type="button"
					  @click="() => taskDepartmentAutocomplete?.togglePopover()"
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
				  ref="taskStatusAutocomplete"
				  :options="statusOptions"
				  :modelValue="newTask.status"
				  @update:modelValue="val => newTask.status = val?.value ?? val ?? ''"
				  :compare-fn="compareOption"
				>
				  <template #target>
					<button
					  type="button"
					  @click="() => taskStatusAutocomplete?.togglePopover()"
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
				  ref="taskPriorityAutocomplete"
				  :options="priorityOptions"
				  :modelValue="newTask.priority"
				  @update:modelValue="val => newTask.priority = val?.value ?? val ?? ''"
				  :compare-fn="compareOption"
				>
				  <template #target>
					<button
					  type="button"
					  @click="() => taskPriorityAutocomplete?.togglePopover()"
					  class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
					>
					  <span class="truncate">{{ getPriorityLabel(newTask.priority) }}</span>
					  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
					</button>
				  </template>
				</Autocomplete>
			  </div>
			  <FormControl type="date" label="Start Date" v-model="newTask.assigned_date" />
			  <FormControl type="date" label="Deadline" v-model="newTask.exp_end_date" />
			  <FormControl type="number" label="Expected Time (In Hrs)" v-model="newTask.expected_time" />
			</div>
			<div class="space-y-4">
			  <div class="space-y-1.5">
				<label class="block text-xs text-ink-gray-5">Assigned By</label>
				<Autocomplete
				  ref="taskAssignedByAutocomplete"
				  :options="userResourceTask.data || []"
				  :modelValue="newTask.assigned_by"
				  @update:modelValue="val => newTask.assigned_by = val?.value ?? val ?? ''"
				  :compare-fn="compareOption"
				  :max-options="100"
				>
				  <template #target>
					<button
					  type="button"
					  :disabled="isTaskFieldDisabled"
					  @click="() => taskAssignedByAutocomplete?.togglePopover()"
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
					:options="assignedToOptionsTask"
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

		  <div class="space-y-2 border-t pt-4">
			<label class="text-xs font-medium text-slate-600 uppercase tracking-wider">Task Description</label>
			<div class="border rounded-lg bg-white shadow-sm overflow-hidden editor-container">
			  <TextEditor
				editor-class="prose-sm max-w-none p-6 outline-none infinite-editor"
				:content="newTask.description"
				@change="(val) => (newTask.description = val)"
				:bubbleMenu="true"
				:fixed-menu="true"
			  />
			</div>
		  </div>
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
	FileUploader,
	FormControl,
	ListHeader,
	ListHeaderItem,
	ListRow,
	ListRowItem,
	ListView,
	MultiSelect,
	Popover,
	Select,
	TextEditor,
	createListResource,
	createResource,
} from "frappe-ui"
import {
	computed,
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
import { useSocket } from "../socket"

// Popover refs for Autocomplete programmatic toggling
const customerAutocomplete = ref(null)
const departmentAutocomplete = ref(null)
const raisedByAutocomplete = ref(null)
const statusAutocomplete = ref(null)
const priorityAutocomplete = ref(null)

const createCustomerAutocomplete = ref(null)
const createRaisedByAutocomplete = ref(null)
const createTicketTypeAutocomplete = ref(null)
const createPriorityAutocomplete = ref(null)
const createDepartmentAutocomplete = ref(null)

const editStatusAutocomplete = ref(null)
const editPriorityAutocomplete = ref(null)
const editCustomerAutocomplete = ref(null)
const editRaisedByAutocomplete = ref(null)
const editDepartmentAutocomplete = ref(null)

const taskProjectAutocomplete = ref(null)
const taskDepartmentAutocomplete = ref(null)
const taskStatusAutocomplete = ref(null)
const taskPriorityAutocomplete = ref(null)
const taskAssignedByAutocomplete = ref(null)

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

// Friendly labels for Autocomplete dropdowns
function getClientLabel(val) {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return "Client"
	const match = customerFilterOptions.value.find((c) => c.value === rawVal)
	return match ? match.label : rawVal
}

function getDepartmentLabel(val) {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return "Department"
	const match = departmentFilterOptions.value.find((d) => d.value === rawVal)
	return match ? match.label : rawVal
}

function getUserLabel(val, defaultLabel = "User") {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return defaultLabel
	const match = raisedByFilterOptions.value.find((u) => u.value === rawVal)
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
import IconHash from "~icons/lucide/hash"
import IconList from "~icons/lucide/list"
import IconMessageSquare from "~icons/lucide/message-square"
// Icons
import IconPlus from "~icons/lucide/plus"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconRotateCcw from "~icons/lucide/rotate-ccw"
import IconSearch from "~icons/lucide/search"
import IconSlidersHorizontal from "~icons/lucide/sliders-horizontal"
import IconTrash2 from "~icons/lucide/trash-2"
import IconUser from "~icons/lucide/user"
import IconX from "~icons/lucide/x"
import IconXCircle from "~icons/lucide/x-circle"

import dayjs from "dayjs"
import relativeTime from "dayjs/plugin/relativeTime"
import utc from "dayjs/plugin/utc"

dayjs.extend(relativeTime)
dayjs.extend(utc)

/* STATE */
const showCreateDialog = ref(false)
const showEditTicket = ref(false)
const isEditMode = ref(false)
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
const taskSaving = ref(false)
const activeSidebarTab = ref(0)
const newComment = ref("")
const editingCommentName = ref(null)
const editContent = ref("")
const showCreateTaskDialog = ref(false)
const ticketFormError = ref("")
const taskFormError = ref("")

const ticketInvalidFields = reactive({
	subject: false,
})

const taskInvalidFields = reactive({
	subject: false,
})

const selectedTickets = ref(new Set())
const showBulkDeleteDialog = ref(false)
const showErrorDialog = ref(false)
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
	if (selectedTickets.value.size === 0) return
	const names = Array.from(selectedTickets.value)

	saving.value = true
	let failed = false
	const succeeded = []

	for (const name of names) {
		try {
			await createResource({
				url: "frappe.client.delete",
				params: {
					doctype: "Tactix Ticket",
					name: name,
				},
			}).submit()
			succeeded.push(name)
		} catch (e) {
			failed = true
			console.error(`Failed to delete ticket ${name}`, e)
		}
	}

	// Clear succeeded selections
	for (const name of succeeded) {
		selectedTickets.value.delete(name)
	}

	tickets.reload()

	if (failed) {
		errorMessage.value =
			"This ticket cannot be deleted because it is linked with other documents."
		showErrorDialog.value = true
	} else {
		showBulkDeleteDialog.value = false
	}
	saving.value = false
}

const isAdmin = session.isAdmin
const isTicketRaiser = session.isTicketRaiser
const isEmployeeOnly = computed(() => {
	const userRoles = session.roles || []
	return userRoles.includes("Employee") && !session.isAdmin
})

const isCreator = computed(() => {
	if (!isEditMode.value) return true
	return (
		ticketForm.owner === session.user || ticketForm.raised_by === session.user
	)
})

const isFieldDisabled = computed(() => {
	return isEmployeeOnly.value && !isCreator.value
})

const ticketStatusOptions = computed(() => {
	const base = ['Open', 'Replied', 'Resolved', 'Closed']
	if (session.isTicketRaiser && localStorage.getItem("tactix_allow_ticket_raiser_to_close_tickets") === "0") {
		return ['Open', 'Replied', 'Resolved']
	}
	return base
})

const isTaskCreatorOrOwner = computed(() => {
	return (
		ticketForm.owner === session.user || ticketForm.raised_by === session.user
	)
})

const isTaskFieldDisabled = computed(() => {
	return isEmployeeOnly.value && !isTaskCreatorOrOwner.value
})

const assignedToOptionsTask = computed(() => {
	if (isTaskFieldDisabled.value) {
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
	return userResourceTask.data || []
})
const ticketCustomerId = session.ticketCustomerId
const tactixDepartment = session.tactixDepartment
const isTactixDeptHead = session.isTactixDeptHead

const selectedFilters = reactive({
	status: "",
	priority: "",
	customer: "",
	raised_by: "",
	department: "",
})

/* RESOURCES */
const ticketFilters = computed(() => {
	const f = {}
	if (debouncedSearchQuery.value) f.subject = ["like", `%${debouncedSearchQuery.value}%`]
	if (selectedFilters.status) f.status = selectedFilters.status
	if (selectedFilters.priority) f.priority = selectedFilters.priority
	if (selectedFilters.customer) f.customer = selectedFilters.customer
	if (selectedFilters.raised_by) f.raised_by_user = selectedFilters.raised_by
	if (selectedFilters.department) f.department = selectedFilters.department
	return f
})

const currentPage = ref(1)
const pageLength = 20

const tickets = createResource({
	url: "tactix.api.ticket.get_tickets",
	initialData: { tickets: [], total_count: 0 },
	transform: (data) => {
		if (Array.isArray(data)) {
			return { tickets: data, total_count: data.length }
		}
		return data || { tickets: [], total_count: 0 }
	},
})

const ticketsSummaryResource = createResource({
	url: "tactix.api.ticket.get_ticket_summary",
	initialData: {
		total: 0,
		open: 0,
		replied: 0,
		resolved: 0,
		closed: 0,
		urgent: 0,
	},
	transform: (data) =>
		data || {
			total: 0,
			open: 0,
			replied: 0,
			resolved: 0,
			closed: 0,
			urgent: 0,
		},
})

function fetchTickets() {
	tickets.fetch({
		filters: ticketFilters.value,
		start: (currentPage.value - 1) * pageLength,
		page_length: pageLength,
	})
}

function fetchTicketSummary() {
	ticketsSummaryResource.fetch({
		filters: ticketFilters.value,
	})
}

// Initial fetch
fetchTickets()
fetchTicketSummary()

onMounted(() => {
	fetchTickets()
	fetchTicketSummary()
})

// Watch filters and reset current page to 1
watch(
	ticketFilters,
	() => {
		currentPage.value = 1
		fetchTickets()
		fetchTicketSummary()
	},
	{ deep: true },
)

// Watch page change to fetch tickets
watch(currentPage, () => {
	fetchTickets()
})

const totalCount = computed(() => tickets.data?.total_count || 0)
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
	}
	return pages
})

const userResource = createListResource({
	doctype: "User",
	fields: ["name", "full_name", "user_image"],
	filters: { enabled: 1, name: ["not in", ["Administrator", "Guest"]], tactix_customer: ["is", "set"] },
	auto: true,
	transform: (users) =>
		users.map((u) => ({
			label: u.full_name || u.name,
			value: u.name,
			image: u.user_image || "",
		})),
	pageLength: 10000,
})

const userResourceTask = createListResource({
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

const customerResource = createListResource({
	doctype: "Tactix Customer",
	fields: ["name"],
	auto: true,
	transform: (customers) => {
		// Be tolerant to multiple response shapes coming from the API.
		// Possible shapes:
		// - [{ name: 'X' }]
		// - [{ label: 'X', value: 'X' }]
		// - [{ customer_name: 'X' }]
		const customerRows = Array.isArray(customers)
			? customers
			: Array.isArray(customers?.message)
				? customers.message
				: Array.isArray(customers?.message?.message)
					? customers.message.message
					: Array.isArray(customers?.data)
						? customers.data
						: Array.isArray(customers?.data?.message)
							? customers.data.message
							: []

		if (!customerRows.length) return []

		return customerRows
			.map((c) => {
				if (c == null) return null
				// already in {label, value} form
				if (
					Object.prototype.hasOwnProperty.call(c, "label") &&
					Object.prototype.hasOwnProperty.call(c, "value")
				) {
					return { label: c.label, value: String(c.value) }
				}
				// common fallback fields
				const name =
					c.name ?? c.customer_name ?? c.customer ?? c.label ?? c.value
				if (name == null) return null
				return { label: String(name), value: String(name) }
			})
			.filter((opt) => opt && opt.value !== "" && opt.value != null)
	},
	pageLength: 10000,
})

function getUserAvatarImage(userName) {
	if (!userName) return ""
	const match = userResource.data?.find((user) => user.value === userName)
	return match?.image || ""
}

const departmentResource = createListResource({
	doctype: "Tactix Department",
	fields: ["name"],
	auto: true,
	transform: (departments) => {
		const departmentRows = Array.isArray(departments)
			? departments
			: Array.isArray(departments?.message)
				? departments.message
				: Array.isArray(departments?.message?.message)
					? departments.message.message
					: Array.isArray(departments?.data)
						? departments.data
						: Array.isArray(departments?.data?.message)
							? departments.data.message
							: []

		if (!departmentRows.length) return []

		return departmentRows
			.map((d) => {
				if (d == null) return null
				if (
					Object.prototype.hasOwnProperty.call(d, "label") &&
					Object.prototype.hasOwnProperty.call(d, "value")
				) {
					return { label: d.label, value: String(d.value) }
				}
				const name =
					d.name ?? d.department_name ?? d.department ?? d.label ?? d.value
				if (name == null) return null
				return { label: String(name), value: String(name) }
			})
			.filter((opt) => opt && opt.value !== "" && opt.value != null)
	},
	pageLength: 10000,
})

const departmentResourceTask = createListResource({
	doctype: "Department",
	fields: ["name"],
	auto: true,
	transform: (departments) =>
		departments.map((d) => ({ label: d.name, value: d.name })),
	pageLength: 10000,
})

const unwrapListPayload = (payload) => {
	if (Array.isArray(payload)) return payload
	if (!payload || typeof payload !== "object") return []

	if (Array.isArray(payload.message)) return payload.message
	if (payload.message && Array.isArray(payload.message.message))
		return payload.message.message
	if (Array.isArray(payload.data)) return payload.data
	if (payload.data && Array.isArray(payload.data.message))
		return payload.data.message

	return []
}

const toOption = (row, primaryKeys = ["name"]) => {
	if (row == null) return null

	if (typeof row === "string" || typeof row === "number") {
		const val = String(row)
		return { label: val, value: val }
	}

	if (
		Object.prototype.hasOwnProperty.call(row, "label") &&
		Object.prototype.hasOwnProperty.call(row, "value")
	) {
		return {
			label: String(row.label),
			value: String(row.value),
			image: row.image || row.user_image || "",
		}
	}

	let value = ""
	for (const key of [...primaryKeys, "name", "value", "id"]) {
		if (row[key] != null && row[key] !== "") {
			value = String(row[key])
			break
		}
	}
	if (!value) return null

	return {
		label: String(row.full_name || row.label || value),
		value,
		image: row.image || row.user_image || "",
	}
}

const normalizeOptions = (payload, primaryKeys = ["name"]) => {
	return unwrapListPayload(payload)
		.map((row) => toOption(row, primaryKeys))
		.filter((opt) => opt?.value)
}

const customerFilterOptions = computed(() =>
	normalizeOptions(customerResource.data, [
		"name",
		"customer_name",
		"customer",
	]),
)
const departmentFilterOptions = computed(() =>
	normalizeOptions(departmentResource.data, [
		"name",
		"department_name",
		"department",
	]),
)
const raisedByFilterOptions = computed(() => {
	if (session.isTicketRaiser) {
		const currentUserName = session.userFullName || session.user
		return [
			{
				label: currentUserName,
				value: session.user,
				image: session.userImage || "",
			},
		]
	}
	return normalizeOptions(userResource.data, ["name"])
})
const customerFilterSelectOptions = computed(() => [
	{ label: "Client", value: "" },
	...customerFilterOptions.value,
])
const departmentFilterSelectOptions = computed(() => [
	{ label: "Department", value: "" },
	...departmentFilterOptions.value,
])
const raisedByFilterSelectOptions = computed(() => [
	{ label: "Raised By", value: "" },
	...raisedByFilterOptions.value,
])

const projectResource = createListResource({
	doctype: "Project",
	fields: ["project_name", "name"],
	auto: true,
	transform: (projects) =>
		projects.map((p) => ({ label: p.project_name, value: p.name })),
	pageLength: 10000,
})

const statusOptions = [
	{ label: "Open", value: "Open" },
	{ label: "Working", value: "Working" },
	{ label: "Pending Review", value: "Pending Review" },
	{ label: "Completed", value: "Completed" },
	{ label: "Cancelled", value: "Cancelled" },
]

const priorityOptions = [
	{ label: "Low", value: "Low" },
	{ label: "Medium", value: "Medium" },
	{ label: "High", value: "High" },
	{ label: "Urgent", value: "Urgent" },
]

const comments = createResource({
	url: "tactix.api.ticket.get_comments",
	initialData: [],
	auto: false,
})

/* DIALOG CONFIG */
const dialogOptions = computed(() => ({
	title: isEditMode.value ? "Edit Ticket" : "Create New Ticket",
	size: "4xl",
	actions: [
		{
			label: isEditMode.value ? "Save Changes" : "Create Ticket",
			variant: "solid",
			loading: saving.value,
			onClick: handleSaveTicket,
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

/* FORM LOGIC */
const emptyTicket = () => ({
	name: "",
	subject: "",
	raised_by: isTicketRaiser ? session.user : "",
	raised_by_user: "",
	status: "Open",
	priority: localStorage.getItem("tactix_default_ticket_priority") || "Medium",
	ticket_type: "Support",
	department: isTicketRaiser && tactixDepartment ? tactixDepartment : "",
	agent_group: "",
	description: "",
	customer: isTicketRaiser && ticketCustomerId ? ticketCustomerId : "",
	resolution_details: "",
	attachments: [],
})

const ticketForm = reactive(emptyTicket())
const resetForm = () => {
	Object.assign(ticketForm, emptyTicket())
	ticketFormError.value = ""
	ticketInvalidFields.subject = false
}

const initialForm = {
	name: "",
	subject: "",
	project: "",
	priority: localStorage.getItem("tactix_default_ticket_priority") || "Medium",
	status: "Open",
	ticket: "",
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
}

const newTask = reactive({ ...initialForm })

function removeAttachment(index) {
	newTask.attachments.splice(index, 1)
}

function handleFileUpload(file) {
	if (!newTask.attachments) newTask.attachments = []
	newTask.attachments.push({
		file_name: file.file_name,
		file_url: file.file_url,
		file_size: file.file_size,
	})
}

function handleFileUploadTicket(file) {
	if (!ticketForm.attachments) ticketForm.attachments = []
	ticketForm.attachments.push({
		file_name: file.file_name,
		file_url: file.file_url,
		file_size: file.file_size,
	})
}

function removeAttachmentTicket(index) {
	ticketForm.attachments.splice(index, 1)
}

function openEditDialog(ticket) {
	isEditMode.value = true
	showEditTicket.value = true
	editPanelReady.value = false
	nextTick(() => {
		Object.assign(ticketForm, ticket)
		if (!ticketForm.attachments) {
			ticketForm.attachments = []
		}
		activeSidebarTab.value = 0
		comments.submit({ ticket: ticket.name })
		editPanelReady.value = true
		if (route.params.name !== ticket.name) {
			router.push({ path: `/tickets/${ticket.name}` })
		}
	})
}

async function handleSaveTicket() {
	ticketFormError.value = ""
	ticketInvalidFields.subject = false

	if (!ticketForm.subject?.trim()) {
		ticketInvalidFields.subject = true
		ticketFormError.value = "Please fill all mandatory fields: Subject."
		setTimeout(() => {
			ticketInvalidFields.subject = false
		}, 700)
		return
	}

	ticketForm.raised_by_user = ticketForm.raised_by
	saving.value = true
	try {
		const url = isEditMode.value
			? "tactix.api.ticket.edit_ticket"
			: "tactix.api.ticket.create_ticket"
		const params = isEditMode.value
			? { name: ticketForm.name, doc: ticketForm }
			: { doc: ticketForm }
		await createResource({ url, params }).submit()
		tickets.reload()
		showCreateDialog.value = false
		showEditTicket.value = false
		resetForm()
	} finally {
		saving.value = false
	}
}

function openTaskCreateDialog(ticket) {
	Object.assign(newTask, {
		...initialForm,
		attachments: [],
		assigned_by: session.user,
		assigned_to:
			isTaskFieldDisabled.value || isEmployeeOnly.value ? [session.user] : [],
	})

	newTask.project = ticket.customer || ""
	newTask.subject = `Task for Ticket #${ticket.name}: ${ticket.subject}`
	newTask.priority = ticket.priority || "Medium"
	newTask.description = ticket.description || ""
	newTask.ticket = ticket.name

	showCreateTaskDialog.value = true
	showEditTicket.value = false
}

const createTaskAPI = createResource({ url: "tactix.api.tasks.create_task" })

const handleSaveTask = async () => {
	taskFormError.value = ""
	taskInvalidFields.subject = false

	if (!newTask.subject?.trim()) {
		taskInvalidFields.subject = true
		taskFormError.value = "Please fill all mandatory fields: Subject."
		setTimeout(() => {
			taskInvalidFields.subject = false
		}, 700)
		return
	}

	taskSaving.value = true
	try {
		const payload = { ...newTask }
		await createTaskAPI.submit({ doc: payload })
		showCreateTaskDialog.value = false
	} catch (e) {
		console.error(e)
	} finally {
		taskSaving.value = false
	}
}

/* DYNAMIC FILTER RULES & ACTIVE CHIPS */
const FILTERABLE_FIELDS = [
	{ label: "Client", value: "customer", key: "customer" },
	{ label: "Department", value: "department", key: "department" },
	{ label: "Status", value: "status", key: "status" },
	{ label: "Priority", value: "priority", key: "priority" },
	{ label: "Raised By", value: "raised_by", key: "raised_by" },
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

function toggleRaisedByMe() {
	if (selectedFilters.raised_by === session.user) {
		selectedFilters.raised_by = ""
	} else {
		selectedFilters.raised_by = session.user
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
	if (fieldKey === "customer") return customerFilterSelectOptions.value.filter(c => c.value !== "")
	if (fieldKey === "department") return departmentFilterSelectOptions.value.filter(d => d.value !== "")
	if (fieldKey === "raised_by") return raisedByFilterSelectOptions.value.filter(u => u.value !== "")
	return []
}

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
							"rule_" + Date.now() + "_" + Math.random().toString(36).substr(2, 4),
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
			if (key === "customer") displayVal = getClientLabel(val)
			else if (key === "department") displayVal = getDepartmentLabel(val)
			else if (key === "raised_by") displayVal = getUserLabel(val)
			else if (key === "status" || key === "priority") displayVal = val
			chips.push({ key, label: fieldLabel, displayValue: displayVal })
		}
	})
	return chips
})

const hasActiveFilterChips = computed(() => activeFilterChips.value.length > 0)

function removeFilterByKey(key) {
	if (key in selectedFilters) {
		selectedFilters[key] = ""
	}
}

const filterStatusOptions = [
	{ label: "Open", value: "Open" },
	{ label: "Replied", value: "Replied" },
	{ label: "Resolved", value: "Resolved" },
	{ label: "Closed", value: "Closed" },
]

/* COLUMN PICKER & LISTVIEW CONFIG */
const ALL_COLUMNS = [
	{ label: "Subject", key: "subject", icon: IconList, width: "3.5fr", mandatory: true },
	{ label: "Ticket ID", key: "name", icon: IconHash, width: "140px" },
	{ label: "Client", key: "customer", icon: IconBriefcase, width: "160px" },
	{ label: "Department", key: "department", icon: IconBriefcase, width: "200px" },
	{ label: "Status", key: "status", icon: IconAlertCircle, width: "130px" },
	{ label: "Priority", key: "priority", icon: IconBriefcase, width: "130px" },
	{ label: "Raised By", key: "raised_by", icon: IconUser, width: "200px" },
	{ label: "Raised On", key: "creation", icon: IconClock, width: "180px" },
	{ label: "First Response Time", key: "first_response_time", icon: IconClock, width: "180px" },
	{ label: "Closed Time", key: "closed_time", icon: IconClock, width: "180px" },
	{ label: "Ticket Type", key: "ticket_type", icon: IconBriefcase, width: "140px" },
	{ label: "Agent Group", key: "agent_group", icon: IconUser, width: "160px" },
]

const DEFAULT_COLUMN_KEYS = [
	"name",
	"subject",
	"customer",
	"department",
	"status",
	"priority",
	"raised_by",
	"creation",
	"first_response_time",
	"closed_time",
]

const STORAGE_KEY = "tactix_tickets_columns_config"

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
	return activeColumnKeys.value
		.map((key) => map.get(key))
		.filter(Boolean)
})

const hasActiveFilters = computed(() => {
	if (debouncedSearchQuery.value) return true
	return Object.values(selectedFilters).some((value) => value !== "")
})

const resetFilters = () => {
	searchQuery.value = ""
	debouncedSearchQuery.value = ""
	selectedFilters.status = ""
	selectedFilters.priority = ""
	selectedFilters.raised_by = ""
	selectedFilters.customer = ""
	selectedFilters.department = ""
	activeFilterRules.value = []
}

function filterByStat(label) {
	const normalized = label.toUpperCase()
	if (normalized === "TOTAL") {
		selectedFilters.status = ""
		selectedFilters.priority = ""
	} else if (normalized === "URGENT") {
		selectedFilters.priority = "Urgent"
		selectedFilters.status = ""
	} else {
		selectedFilters.status =
			label.charAt(0).toUpperCase() + label.slice(1).toLowerCase()
		selectedFilters.priority = ""
	}
}

function isCardActive(label) {
	const normalized = label.toUpperCase()
	if (normalized === "TOTAL") {
		return !selectedFilters.status && !selectedFilters.priority
	}
	if (normalized === "URGENT") {
		return selectedFilters.priority === "Urgent"
	}
	const expectedStatus =
		label.charAt(0).toUpperCase() + label.slice(1).toLowerCase()
	return selectedFilters.status === expectedStatus
}

const formatDateTime = (dateStr) => {
	if (!dateStr) return "—"
	return dayjs(dateStr).format("MMM D, YYYY h:mm A")
}

const formatDuration = (seconds) => {
	if (seconds === null || seconds === undefined || seconds === "") return "—"
	const totalSeconds = Math.round(seconds)
	const d = Math.floor(totalSeconds / 86400)
	const h = Math.floor((totalSeconds % 86400) / 3600)
	const m = Math.floor((totalSeconds % 3600) / 60)

	const parts = []
	if (d > 0) parts.push(`${d}d`)
	if (h > 0) parts.push(`${h}h`)
	if (m > 0) parts.push(`${m}m`)
	if (parts.length === 0) {
		const s = Math.floor(totalSeconds % 60)
		if (s > 0) parts.push(`${s}s`)
	}
	return parts.join(" ") || "0m"
}

const kpiStats = computed(() => {
	const summary = ticketsSummaryResource.data || {
		total: 0,
		open: 0,
		replied: 0,
		resolved: 0,
		closed: 0,
		urgent: 0,
	}
	return [
		{
			label: "TOTAL",
			value: summary.total,
			icon: IconList,
			color: "text-indigo-500",
			bg: "bg-indigo-50",
		},
		{
			label: "OPEN",
			value: summary.open,
			icon: IconClock,
			color: "text-blue-500",
			bg: "bg-blue-50",
		},
		{
			label: "REPLIED",
			value: summary.replied,
			icon: IconMessageSquare,
			color: "text-orange-500",
			bg: "bg-orange-50",
		},
		{
			label: "RESOLVED",
			value: summary.resolved,
			icon: IconCheckCircle,
			color: "text-green-500",
			bg: "bg-green-50",
		},
		{
			label: "CLOSED",
			value: summary.closed,
			icon: IconXCircle,
			color: "text-slate-500",
			bg: "bg-slate-50",
		},
		{
			label: "URGENT",
			value: summary.urgent,
			icon: IconAlertCircle,
			color: "text-red-500",
			bg: "bg-red-50",
		},
	]
})

function getStatusColor(status) {
	return {
		Open: "bg-blue-400",
		Replied: "bg-orange-400",
		Resolved: "bg-green-500",
		Closed: "bg-green-500",
	}[status]
}

function getPriorityTheme(p) {
	return (
		{ High: "red", Medium: "orange", Low: "gray", Urgent: "red" }[p] || "gray"
	)
}

async function addComment() {
	if (!newComment.value) return
	await createResource({
		url: "tactix.api.ticket.add_comment",
		params: { ticket: ticketForm.name, content: newComment.value },
	}).submit()
	newComment.value = ""
	comments.submit({ ticket: ticketForm.name })
}

function startEditing(comment) {
	editingCommentName.value = comment.name
	editContent.value = comment.content.replace(/<[^>]*>?/gm, "")
}

function cancelEdit() {
	editingCommentName.value = null
	editContent.value = ""
}

async function handleUpdateComment(name) {
	if (!editContent.value.trim()) return
	try {
		await createResource({
			url: "tactix.api.ticket.edit_comment",
			params: {
				name: name,
				content: editContent.value,
			},
		}).submit()
		editingCommentName.value = null
		comments.submit({ ticket: ticketForm.name })
	} catch (e) {
		console.error("Update failed", e)
	}
}

async function handleDeleteComment(name) {
	try {
		await createResource({
			url: "tactix.api.ticket.delete_comment",
			params: {
				name: name,
			},
		}).submit()
		comments.submit({ ticket: ticketForm.name })
	} catch (e) {
		console.error("Delete failed", e)
	}
}

const route = useRoute()
const router = useRouter()

async function openTicketByName(ticketName) {
	if (!ticketName) return
	if (showEditTicket.value && ticketForm.name === ticketName) return

	// Check if ticket is already in the loaded tickets list to avoid redundant API call
	if (tickets.data?.tickets) {
		const found = tickets.data.tickets.find((t) => t.name === ticketName)
		if (found) {
			openEditDialog(found)
			return
		}
	}

	try {
		// Fetch using get_tickets API to get pre-formatted attachments and avoid frappe.client.get call
		const res = await createResource({
			url: "tactix.api.ticket.get_tickets",
			params: {
				filters: { name: ticketName },
			},
		}).submit()

		const ticketList = res?.tickets || (Array.isArray(res) ? res : [])
		if (ticketList && ticketList.length > 0) {
			openEditDialog(ticketList[0])
		}
	} catch (e) {
		console.error("Failed to load ticket for notification", e)
	}
}

watch(
	() => route.params.name,
	(newName) => {
		if (newName) {
			openTicketByName(newName)
		} else {
			showEditTicket.value = false
		}
	},
	{ immediate: true },
)

function handleGlobalKeydown(e) {
	const isCmdOrCtrl = e.metaKey || e.ctrlKey
	if (isCmdOrCtrl && e.key.toLowerCase() === "s") {
		e.preventDefault()
		handleSaveTicket()
	}
}

watch([showEditTicket, showCreateDialog], ([editOpen, createOpen]) => {
	if (editOpen || createOpen) {
		window.addEventListener("keydown", handleGlobalKeydown)
	} else {
		window.removeEventListener("keydown", handleGlobalKeydown)
	}
})

watch(showEditTicket, (val) => {
	if (!val) {
		if (route.params.name) {
			router.push({ path: "/tickets" })
		}
	}
})

watch(showCreateDialog, (val) => {
	if (!val) {
		ticketFormError.value = ""
		ticketInvalidFields.subject = false
	}
})

watch(showCreateTaskDialog, (val) => {
	if (!val) {
		taskFormError.value = ""
		taskInvalidFields.subject = false
	}
})

const socket = useSocket()

function onTicketRaised(payload) {
	if (!payload) return
	// If a new ticket is raised, reload tickets and summary to reflect change in real time
	tickets.reload()
	ticketsSummaryResource.reload()
}

onMounted(() => {
	if (socket) {
		socket.on("tactix_ticket_raised", onTicketRaised)
	}
})

onUnmounted(() => {
	window.removeEventListener("keydown", handleGlobalKeydown)
	if (socket) {
		socket.off("tactix_ticket_raised", onTicketRaised)
	}
})
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
.slide-enter-active, .slide-leave-active { transition: transform .3s cubic-bezier(0.4, 0, 0.2, 1); }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }

/* Ensure frappe-ui dialogs are always above page-level filters and sticky elements. */
:global(.dialog-overlay) { z-index: 1200; }
:global(.dialog-content) { position: relative; z-index: 1201; }
/* Keep autocomplete/select popovers above dialogs so dropdowns are usable inside modals. */
:global([data-radix-popper-content-wrapper]), :global([data-reka-popper-content-wrapper]), :global(.PopoverContent), :global(.ticket-modal-autocomplete) { z-index: 100005 !important; }
/* Ensure list-view filter dropdowns render above cards/list containers as well. */
:global(.ticket-filter-autocomplete) { z-index: 100005 !important; }

.field-invalid-blink {
	border: 1px solid #ef4444;
	box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
	animation: fieldBlink 0.7s ease-out 1;
}

@keyframes fieldBlink {
	0% { opacity: 1; transform: translateY(0); }
	30% { opacity: 0.85; transform: translateY(-1px); }
	100% { opacity: 1; transform: translateY(0); }
}
</style>