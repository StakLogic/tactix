<template>
  <div class="space-y-3 p-1 flex flex-col h-full overflow-hidden font-sans min-h-0">
	<div class="grid grid-cols-3 lg:grid-cols-6 gap-2 flex-shrink-0">
		<div
			v-for="stat in kpiStats"
			:key="stat.label"
			role="button"
			tabindex="0"
			class="kpi text-left"
			:class="isCardActive(stat.label) && 'is-active'"
			@click="filterByStat(stat.label)"
			@keydown.enter.prevent="filterByStat(stat.label)"
			@keydown.space.prevent="filterByStat(stat.label)"
		>
			<div class="flex items-center justify-between gap-2">
				<span class="truncate text-xs font-medium text-ink-gray-6">{{ statTitle(stat.label) }}</span>
				<span class="h-2 w-2 shrink-0 rounded-full" :class="statDot(stat.label)"></span>
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
			placeholder="Search subject or ID…"
			class="h-8 w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 pl-9 pr-9 text-[13px] text-ink-gray-8 outline-none transition focus:border-[color:var(--brand,#29ADFF)] focus:bg-surface-white focus:ring-2 focus:ring-[color:var(--brand-soft,#E9F6FF)]"
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
				title="Filter Tickets"
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
		  <Popover placement="bottom-end">
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
			<template #prefix><IconRefresh class="w-3.5 h-3.5 text-ink-gray-5" :class="tickets.loading && 'animate-spin'" /></template>
		  </Button>

		  <!-- Selection info -->
		  <div v-if="isAdmin && selectedTickets.size > 0" class="flex h-8 items-center gap-1 rounded-md bg-surface-gray-2 pl-2.5 pr-1 text-xs text-ink-gray-7">
			<span class="font-medium tabular-nums">{{ selectedTickets.size }} selected</span>
			<button type="button" class="rounded p-1 text-ink-gray-5 hover:bg-surface-gray-3 hover:text-ink-gray-8" title="Clear selection" @click="clearSelection">
			  <IconX class="h-3.5 w-3.5" />
			</button>
		  </div>

		  <!-- Actions Dropdown / New Ticket Button -->
		  <Dropdown
			v-slot="{ open }"
			v-if="isAdmin && selectedTickets.size > 0"
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
			@click="isEditMode=false; resetForm(); customerResource.reload(); showCreateDialog=true"
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
				  :class="['qf', selectedFilters.customer !== '' && 'on']"
				>
				  <span class="truncate">{{ getClientLabel(selectedFilters.customer, 'Client') }}</span>
				  <FeatherIcon name="chevron-down" class="size-3.5 opacity-60 ml-auto shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<!-- Status Autocomplete Filter -->
		<div class="w-36 shrink-0">
			<Autocomplete
			  ref="statusAutocomplete"
			  :options="filterStatusSelectOptions"
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
				  <span class="truncate">{{ getStatusLabel(selectedFilters.status, 'Status') }}</span>
				  <FeatherIcon name="chevron-down" class="size-3.5 opacity-60 ml-auto shrink-0" />
				</button>
			  </template>
			</Autocomplete>
		</div>

		<!-- Priority Autocomplete Filter -->
		<div class="w-36 shrink-0">
			<Autocomplete
			  ref="priorityAutocomplete"
			  :options="priorityFilterSelectOptions"
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
				  <span class="truncate">{{ getPriorityLabel(selectedFilters.priority, 'Priority') }}</span>
				  <FeatherIcon name="chevron-down" class="size-3.5 opacity-60 ml-auto shrink-0" />
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
				  :class="['qf', selectedFilters.raised_by !== '' && 'on']"
				>
				  <span class="truncate">{{ getUserLabel(selectedFilters.raised_by, 'Raised By') }}</span>
				  <FeatherIcon name="chevron-down" class="size-3.5 opacity-60 ml-auto shrink-0" />
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
	  <div class="relative bg-surface-white rounded-xl border border-outline-gray-2 shadow-sm flex flex-col min-h-[420px] md:min-h-0 md:flex-1 md:overflow-hidden">
		  <div v-if="tickets.loading" class="busy-bar" aria-hidden="true"></div>
		  <ListView
		  class="h-full flex flex-col min-h-0"
		  :columns="columns"
		  :rows="tickets.data?.tickets || []" 
		  :options="{ 
			  selectable: isAdmin, 
			  showTooltip: true, 
			  resizeColumn: true, 
			  onRowClick: (row) => openEditDialog(row),
			  emptyState: {
				title: hasActiveFilters ? 'No tickets match your filters' : 'No tickets yet',
				description: hasActiveFilters ? 'Try removing a filter or clearing the search.' : 'New tickets will appear here.',
			  },
		  }"
		  row-key="name"
		  v-model:selections="selectedTickets"
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
			  <ListRow 
			  v-slot="{ column, item }" 
			  v-for="row in (tickets.data?.tickets || [])" 
			  :key="row.name" 
			  :row="row"
			  >
			<ListRowItem :item="item">
				
				<template v-if="column.key === 'name'">
				<span class="font-mono text-[12px] font-semibold text-[color:var(--brand-text,#0A84D0)]">#{{ row.name }}</span>
				</template>

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

				<template v-if="column.key === 'status'">
				<div class="flex min-w-0 items-center gap-1.5">
					<span class="status-pill" :class="getStatusPillClass(item)">
						<span class="h-1.5 w-1.5 shrink-0 rounded-full" :class="getStatusColor(item)" />
						<span class="truncate">{{ item }}</span>
					</span>
					<span v-if="row.is_overdue" class="text-[11px] font-medium text-ink-red-4">Overdue</span>
				</div>
				</template>

				<template v-if="column.key === 'priority'">
				<Badge :theme="getPriorityTheme(item)" variant="subtle" :label="item" />
				</template>

				<template v-if="column.key === 'raised_by'">
				<span class="text-xs text-ink-gray-6 font-medium truncate">
					{{ getUserLabel(row.raised_by) }}
				</span>
				</template>

				<template v-if="column.key === 'customer'">
				<span class="text-xs text-ink-gray-6 font-medium truncate">
					{{ getClientLabel(row.customer) }}
				</span>
				</template>



				<template v-if="column.key === 'creation'">
				<span v-if="row.creation" class="inline-flex items-center gap-1.5 whitespace-nowrap text-xs text-ink-gray-5" v-tooltip="formatDateTime(row.creation)">
					<IconClock class="w-3.5 h-3.5 shrink-0" />{{ dayjs(row.creation).fromNow() }}
				</span>
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
				<span v-else class="text-xs text-ink-gray-4 font-medium pl-2">—</span>
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
				<span v-else class="text-xs text-ink-gray-4 font-medium pl-2">—</span>
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
		<p class="text-sm text-ink-gray-6 leading-relaxed py-2">
		  Are you sure you want to permanently delete the <span class="font-bold text-ink-gray-9">{{ selectedTickets.size }}</span> selected ticket(s)? This action cannot be undone.
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
			  <FormControl label="Subject *" v-model="ticketForm.subject" />
			  <div class="space-y-1.5">
				<label class="block text-xs text-ink-gray-5">Customer *</label>
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
					  <span class="truncate">{{ getClientLabel(ticketForm.customer, 'Select Customer') }}</span>
					  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
					</button>
				  </template>
				</Autocomplete>
			  </div>
			  <div class="space-y-1.5">
				<label class="block text-xs text-ink-gray-5">Raised By *</label>
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
			</div>
		  </div>
		  <div class="space-y-2 border-t pt-4">
			<label class="text-xs font-medium text-ink-gray-6 uppercase tracking-wider">Description *</label>
			<div class="border border-outline-gray-2 rounded-lg bg-surface-white shadow-sm overflow-hidden min-h-[200px]">
			  <TextEditor
				editor-class="prose-sm max-w-none p-6 outline-none"
				:content="ticketForm.description"
				@change="(val) => (ticketForm.description = val)"
				:fixed-menu="true"
			  />
			</div>
		  </div>

		  <!-- Attachments Field -->
		  <div class="space-y-3 border-t pt-4">
			<label class="text-xs font-medium text-ink-gray-6 uppercase tracking-wider block">Attachments</label>
			<FileUploader @success="handleFileUploadTicket">
			  <template #default="{ openFileSelector }">
				<button 
				  type="button"
				  @click="openFileSelector" 
				  class="w-full flex items-center justify-center gap-2 border-2 border-dashed border-outline-gray-2 rounded-lg p-3 text-ink-gray-5 hover:border-[color:var(--brand,#29ADFF)] hover:text-[color:var(--brand-text,#0A84D0)] hover:bg-[color:var(--brand-soft,#E9F6FF)] transition-all cursor-pointer"
				>
				  <IconPaperclip class="w-4 h-4" />
				  <span class="text-xs font-semibold">Attach Files</span>
				</button>
			  </template>
			</FileUploader>
			
			<div v-if="ticketForm.attachments && ticketForm.attachments.length > 0" class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
			  <div 
				v-for="(file, idx) in ticketForm.attachments" 
				:key="idx" 
				class="flex items-center justify-between bg-surface-gray-2 border border-outline-gray-2 rounded-lg p-2 transition-all"
			  >
				<a 
				  :href="file.file_url" 
				  target="_blank" 
				  class="flex flex-1 items-center gap-2 truncate"
				>
				  <div class="h-7 w-7 rounded bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)] flex items-center justify-center shrink-0">
					<IconPaperclip class="w-3.5 h-3.5" />
				  </div>
				  <div class="truncate text-left">
					<span class="block truncate font-medium text-ink-gray-7 text-xs hover:text-[color:var(--brand-text,#0A84D0)] transition-colors">
					  {{ file.file_name }}
					</span>
				  </div>
				</a>

				<button 
				  type="button"
				  @click.stop="removeAttachmentTicket(idx)" 
				  class="p-1 ml-1 hover:bg-red-50 rounded text-ink-gray-4 hover:text-red-500 transition-colors"
				  title="Remove file"
				>
				  <IconX class="w-3.5 h-3.5" />
				</button>
			  </div>
			</div>
		  </div>
		</div>
	  </template>
	</Dialog>

	<Transition name="slide">
		<div v-if="showEditTicket" class="fixed inset-0 flex justify-end z-50">
			<div class="absolute inset-0 bg-slate-900/20 backdrop-blur-[2px]" @click="showEditTicket=false"></div>
			
			<div class="relative w-full md:max-w-8xl lg:max-w-8xl h-full bg-surface-white flex flex-col md:flex-row shadow-2xl border-l overflow-y-auto md:overflow-hidden">
				<div v-if="!editPanelReady" class="flex-1 grid place-items-center bg-surface-gray-1 min-h-0">
					<div class="flex items-center gap-3 text-ink-gray-5">
						<div class="w-5 h-5 border-2 border-outline-gray-2 border-t-[color:var(--brand,#29ADFF)] rounded-full animate-spin"></div>
						<span class="text-sm font-medium">Loading ticket details...</span>
					</div>
				</div>

				<div v-else class="flex w-full h-full flex-col md:flex-row">
					<!-- Left Column: Activity (Full Width) -->
					<div class="h-[400px] md:h-full md:w-[60%] flex flex-col bg-surface-white min-h-0 border-b md:border-b-0 md:border-r border-outline-gray-1 shrink-0">
						<header class="px-5 py-3.5 border-b bg-surface-white flex justify-between items-center shrink-0 shadow-xs z-10">
							<div class="flex items-center gap-2">
								<h3 class="text-sm font-bold text-ink-gray-8">Activity</h3>
								<span v-if="comments.data?.length" class="text-xs font-semibold px-2 py-0.5 rounded-full bg-surface-gray-2 text-ink-gray-6">
									{{ comments.data.length }}
								</span>
							</div>
							<div class="flex items-center gap-2 text-xs text-ink-gray-5">
								<span class="inline-block w-2 h-2 rounded-full bg-emerald-500"></span>
								<span class="font-medium text-[11px] text-ink-gray-4">Conversation feed</span>
							</div>
						</header>
						
						<div 
							ref="activityContainerRef" 
							class="flex-grow md:flex-1 overflow-y-auto p-4 md:p-6 space-y-4 custom-scrollbar bg-surface-gray-1"
						>
							<!-- Loading Spinner -->
							<div v-if="comments.loading && (!comments.data || comments.data.length === 0)" class="flex justify-center items-center py-12 text-ink-gray-4 gap-2">
								<div class="w-4 h-4 border-2 border-outline-gray-3 border-t-[color:var(--brand,#29ADFF)] rounded-full animate-spin"></div>
								<span class="text-xs">Loading activity...</span>
							</div>

							<!-- Timeline Activity Comments -->
							<div 
								v-for="c in comments.data || []" 
								:key="c.name" 
								class="flex items-start gap-2.5 group w-full"
								:class="isCommentOnRight(c) ? 'flex-row-reverse justify-start' : 'flex-row justify-start'"
							>
								<!-- Avatar -->
								<Avatar 
									:image="getUserAvatarImage(c.owner)"
									:label="getUserLabel(c.owner) || 'User'" 
									size="md" 
									class="ring-2 ring-white shadow-xs shrink-0 mt-0.5" 
								/>

								<!-- Bubble Card -->
								<div 
									class="w-fit max-w-[85%] sm:max-w-[78%] rounded-xl p-3.5 sm:p-4 bg-surface-white border border-outline-gray-2 shadow-xs hover:shadow-sm transition-all duration-200"
									:class="isCommentOnRight(c) ? 'rounded-tr-xs' : 'rounded-tl-xs'"
								>
									<!-- Header (Author, Badge, Time, Actions) -->
									<div class="flex items-center justify-between gap-3 mb-1.5 text-xs">
										<div class="flex items-center gap-1.5 flex-wrap">
											<span class="font-bold text-xs text-ink-gray-8">
												{{ c.owner === session.user ? (isCommentOnRight(c) ? 'You' : getUserLabel(c.owner)) : getUserLabel(c.owner) }}
											</span>
											<span 
												class="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded"
												:class="isCommentFromTicketRaiser(c) 
													? 'bg-amber-50 text-amber-700 border border-amber-200/60' 
													: 'bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)] border border-[color:var(--brand-border,#A6DCFF)]'"
											>
												{{ isCommentFromTicketRaiser(c) ? 'Ticket Raiser' : 'Support' }}
											</span>
											<span class="text-ink-gray-3">·</span>
											<span class="font-medium text-[11px] text-ink-gray-4">
												{{ dayjs(c.creation).fromNow() }}
											</span>
										</div>

										<!-- Comment Edit/Delete Actions -->
										<div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity" v-if="c.owner === session.user">
											<button 
												@click="startEditing(c)"
												class="p-1 rounded text-ink-gray-4 hover:text-[color:var(--brand-text,#0A84D0)] hover:bg-surface-gray-2 transition-colors"
												title="Edit Comment"
											>
												<IconEdit3 class="w-3.5 h-3.5" />
											</button>
											<button 
												@click="handleDeleteComment(c.name)"
												class="p-1 rounded text-ink-gray-4 hover:text-red-600 hover:bg-red-50 transition-colors"
												title="Delete Comment"
											>
												<IconTrash2 class="w-3.5 h-3.5" />
											</button>
										</div>
									</div>

									<!-- Body -->
									<div class="text-sm leading-relaxed">
										<div v-if="editingCommentName === c.name" class="space-y-3 min-w-[240px] sm:min-w-[300px]">
											<FormControl 
												type="textarea"
												v-model="editContent" 
												class="w-full rounded-xl border border-outline-gray-2 p-2.5 text-sm text-ink-gray-8 bg-surface-white focus:ring-1 focus:ring-[color:var(--brand,#29ADFF)] outline-none resize-none"
											/>
											<div class="flex justify-end gap-2">
												<Button size="sm" variant="ghost" @click="cancelEdit">Cancel</Button>
												<Button size="sm" variant="solid" class="brand-btn" :loading="editingCommentName === c.name && commentUpdating" @click="handleUpdateComment(c.name)">Save</Button>
											</div>
										</div>
										<div 
											v-else 
											class="prose prose-sm max-w-none break-words leading-relaxed text-ink-gray-7 [&_a]:text-[color:var(--brand-text,#0A84D0)] [&_a]:underline" 
											v-html="c.content"
										></div>
									</div>
								</div>
							</div>

							<!-- Empty State Placeholder -->
							<div v-if="!comments.loading && !(comments.data && comments.data.length > 0)" class="flex flex-col items-center justify-center py-12 text-ink-gray-4 bg-surface-white rounded-xl border border-dashed border-outline-gray-2 mx-2 my-2 shadow-xs">
								<div class="p-3 bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)] rounded-full mb-2.5">
									<IconMessageSquare class="w-6 h-6" />
								</div>
								<p class="text-xs font-semibold text-ink-gray-7">No messages yet</p>
								<p class="text-[11px] text-ink-gray-4 mt-0.5">Send a message below to start the conversation!</p>
							</div>
						</div>

						<div class="p-4 bg-surface-white border-t shrink-0">
							<p v-if="commentError" class="mb-2 flex items-center justify-between gap-2 rounded-md bg-red-50 px-3 py-1.5 text-xs text-red-600">
								<span>{{ commentError }}</span>
								<button type="button" class="text-red-400 hover:text-red-600" @click="commentError = ''"><IconX class="h-3.5 w-3.5" /></button>
							</p>
							<CommentBox
								v-model="newComment"
								:avatar="getUserAvatarImage(session.user)"
								:user="session.user"
								:userName="session.userFullName"
								placeholder="Type a message..."
								:loading="commentSubmitting"
								@submit="addComment"
							/>
						</div>
					</div>

					<!-- Right Column: Ticket Details Form (40% Width) -->
					<div class="w-full md:w-[40%] md:shrink-0 flex flex-col bg-surface-white min-h-0">
						<header class="p-4 border-b flex justify-between items-center bg-surface-white shrink-0 shadow-sm z-10">
							<div class="min-w-0 flex-1 mr-2">
								<div class="flex flex-wrap items-center gap-1.5">
									<span class="font-mono text-[11px] font-medium text-ink-gray-6 bg-surface-gray-2 rounded px-1.5 py-0.5">#{{ ticketForm.name }}</span>
									<span class="status-pill" :class="getStatusPillClass(ticketForm.status)">
										<span class="h-1.5 w-1.5 rounded-full" :class="getStatusColor(ticketForm.status)" />{{ ticketForm.status }}
									</span>
									<Badge v-if="ticketForm.priority" :theme="getPriorityTheme(ticketForm.priority)" variant="subtle" size="sm">{{ ticketForm.priority }}</Badge>
									<Badge v-if="ticketForm.first_responded_on" theme="blue" variant="subtle" class="font-semibold !px-2 !py-0.5 text-[10px]" v-tooltip="'First Response: ' + formatDateTime(ticketForm.first_responded_on)">
										Responded in {{ formatDuration(ticketForm.first_response_time) }}
									</Badge>
									<Badge v-if="ticketForm.closed_on" theme="green" variant="subtle" class="font-semibold !px-2 !py-0.5 text-[10px]" v-tooltip="'Closed on: ' + formatDateTime(ticketForm.closed_on)">
										Closed in {{ formatDuration(ticketForm.closed_time) }}
									</Badge>
								</div>
								<h2 class="font-semibold text-ink-gray-9 text-base md:text-lg mt-1.5 truncate max-w-full" :title="ticketForm.subject">{{ ticketForm.subject }}</h2>
							</div>
							<div class="flex items-center gap-1.5 shrink-0">
								<Button v-if="!isTicketRaiser" variant="outline" size="sm" @click="openTaskCreateDialog(ticketForm)" class="!px-2 sm:!px-3 text-xs">
									<template #prefix><IconPlus class="h-3.5 w-3.5" /></template>
									Create Task
								</Button>
								<Button variant="solid" size="sm" :loading="saving" @click="handleSaveTicket" class="brand-btn !px-2 sm:!px-3 text-xs" title="Save (Ctrl S)">Save</Button>
								<Button variant="ghost" size="sm" @click="showEditTicket=false" class="text-ink-gray-4 hover:text-ink-gray-6 !p-1" title="Close">
									<IconX class="w-4 h-4"/>
								</Button>
							</div>
						</header>

						<div class="flex-grow md:flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
							<!-- Metadata Card -->
							<div class="bg-surface-gray-1 rounded-xl border border-outline-gray-1 p-4 space-y-4 shadow-sm mb-6">
								<div class="grid grid-cols-2 gap-4">
									<div class="space-y-1.5">
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

									<div class="space-y-1.5">
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

								<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 border-t pt-4">
									<div class="space-y-1.5">
										<label class="block text-xs text-ink-gray-5">Customer *</label>
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
											  <span class="truncate">{{ getClientLabel(ticketForm.customer, 'Select Customer') }}</span>
											  <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
											</button>
										  </template>
										</Autocomplete>
									</div>

									<div class="space-y-1.5">
										<label class="block text-xs text-ink-gray-5">Raised By *</label>
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
								</div>
							</div>

							
							<!-- Description Field -->
							<div class="space-y-2 border-t pt-4">
								<label class="section-title">Description *</label>
								<div class="border border-outline-gray-2 rounded-xl bg-surface-white overflow-hidden min-h-[200px] focus-within:border-[color:var(--brand,#29ADFF)] focus-within:ring-2 focus-within:ring-[color:var(--brand-soft,#E9F6FF)] transition-all">
									<TextEditor
										editor-class="prose-sm max-w-none p-4 outline-none bg-surface-white min-h-[200px]"
										:content="ticketForm.description"
										@change="(val) => (ticketForm.description = val)"
										:fixed-menu="true"
									/>
								</div>
							</div>

							<!-- Resolution Field -->
							<div v-if="!isTicketRaiser" class="space-y-2 border-t pt-4 pb-2" >
								<label class="section-title">Resolution</label>
								<div class="border border-outline-gray-2 rounded-xl bg-surface-white overflow-hidden min-h-[200px] focus-within:border-[color:var(--brand,#29ADFF)] focus-within:ring-2 focus-within:ring-[color:var(--brand-soft,#E9F6FF)] transition-all">
									<TextEditor
										editor-class="prose-sm max-w-none p-4 outline-none bg-surface-white min-h-[200px]"
										:content="ticketForm.resolution_details"
										@change="(val) => (ticketForm.resolution_details = val)"
										:fixed-menu="true"
									/>
								</div>
							</div>

							<!-- Attachments Field -->
							<div class="pt-4 border-t border-outline-gray-2">
								<label class="section-title mb-3">
									Attachments
								</label>
								<div class="space-y-4">
									<FileUploader @success="handleFileUploadTicket">
										<template #default="{ openFileSelector }">
											<button 
												@click="openFileSelector" 
												class="w-full flex items-center justify-center gap-2 border-2 border-dashed border-outline-gray-2 rounded-xl p-4 text-ink-gray-5 hover:border-[color:var(--brand,#29ADFF)] hover:text-[color:var(--brand-text,#0A84D0)] hover:bg-[color:var(--brand-soft,#E9F6FF)] transition-all group"
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
											class="group flex items-center justify-between bg-surface-white border border-outline-gray-2 rounded-xl shadow-sm hover:border-[color:var(--brand,#29ADFF)] hover:shadow-md transition-all overflow-hidden p-2"
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
												@click.stop="removeAttachmentTicket(idx)" 
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
					</div>
				</div>
			</div>
		</div>
	</Transition>

	<Dialog v-model="showCreateTaskDialog" 
		:disable-outside-click-to-close="true"
		:options="createTaskDialogOptions">
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
			  <DatePicker label="Start Date" v-model="newTask.assigned_date" />
			  <DatePicker label="Deadline" v-model="newTask.exp_end_date" />
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

		  <div class="space-y-2 border-t pt-4">
			<label class="text-xs font-medium text-ink-gray-6 uppercase tracking-wider">Task Description</label>
			<div class="border rounded-lg bg-surface-white shadow-sm overflow-hidden editor-container">
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
function getClientLabel(val, defaultLabel = "Client") {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return defaultLabel
	const match = customerFilterOptions.value.find((c) => c.value === rawVal)
	return match ? match.label : rawVal
}

function getUserLabel(val, defaultLabel = "User") {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return defaultLabel
	const match = raisedByFilterOptions.value.find((u) => u.value === rawVal)
	return match ? match.label : rawVal
}

function getStatusLabel(val, defaultLabel = "Status") {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return defaultLabel
	const match = filterStatusOptions.find((s) => s.value === rawVal)
	return match ? match.label : rawVal
}

function getPriorityLabel(val, defaultLabel = "Priority") {
	const rawVal = val && typeof val === "object" ? val.value : val
	if (!rawVal) return defaultLabel
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

const searchInputEl = ref(null)
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
	customer: false,
	raised_by: false,
	description: false,
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
	ticketsSummaryResource.reload()

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
	const base = ["Open", "Replied", "Resolved", "Closed"]
	if (
		session.isTicketRaiser &&
		localStorage.getItem("tactix_allow_ticket_raiser_to_close_tickets") === "0"
	) {
		return ["Open", "Replied", "Resolved"]
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

const selectedFilters = reactive({
	status: "",
	priority: "",
	customer: "",
	raised_by: "",
})

/* RESOURCES */
const ticketFilters = computed(() => {
	const f = {}
	if (debouncedSearchQuery.value)
		f.subject = ["like", `%${debouncedSearchQuery.value}%`]
	if (selectedFilters.status) f.status = selectedFilters.status
	if (selectedFilters.priority) f.priority = selectedFilters.priority
	if (selectedFilters.customer) f.customer = selectedFilters.customer
	if (selectedFilters.raised_by) f.raised_by_user = selectedFilters.raised_by
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


// Watch filters and reset current page to 1
watch(
	ticketFilters,
	() => {
		fetchTicketSummary()
		if (currentPage.value !== 1) currentPage.value = 1 // the page watcher fetches
		else fetchTickets()
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
	filters: {
		enabled: 1,
		name: ["not in", ["Administrator", "Guest"]],
		tactix_customer: ["is", "set"],
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

const customerFilterOptions = computed(() => {
	const allOptions = normalizeOptions(customerResource.data, [
		"name",
		"customer_name",
		"customer",
	])
	if (session.isTicketRaiser) {
		const userCust =
			session.ticketCustomerId || session.userInfo.data?.tactix_customer
		if (userCust) {
			const match = allOptions.find((c) => c.value === userCust)
			return [match || { label: userCust, value: userCust }]
		}
		return []
	}
	return allOptions
})

const customerFilterSelectOptions = computed(() => {
	if (session.isTicketRaiser) {
		return customerFilterOptions.value
	}
	return [{ label: "Client", value: "" }, ...customerFilterOptions.value]
})

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

const filterStatusSelectOptions = computed(() => [
	{ label: "Status", value: "" },
	...filterStatusOptions,
])

const priorityFilterSelectOptions = computed(() => [
	{ label: "Priority", value: "" },
	...priorityOptions,
])

const comments = createResource({
	url: "tactix.api.ticket.get_comments",
	initialData: [],
	auto: false,
	onSuccess: () => {
		scrollToBottom()
	},
})

/* DIALOG CONFIG */
const dialogOptions = computed(() => ({
	title: isEditMode.value ? "Edit Ticket" : "Create New Ticket",
	size: "4xl",
	actions: [
		{
			label: isEditMode.value ? "Save Changes" : "Create Ticket",
			variant: "solid",
			class: "brand-btn",
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
const emptyTicket = () => {
	const userCust =
		session.ticketCustomerId || session.userInfo.data?.tactix_customer || ""
	return {
		name: "",
		subject: "",
		raised_by: session.isTicketRaiser ? session.user : "",
		raised_by_user: "",
		status: "Open",
		priority:
			localStorage.getItem("tactix_default_ticket_priority") || "Medium",
		ticket_type: "Support",
		agent_group: "",
		description: "",
		customer: session.isTicketRaiser ? userCust : "",
		resolution_details: "",
		attachments: [],
	}
}

const ticketForm = reactive(emptyTicket())
const resetForm = () => {
	Object.assign(ticketForm, emptyTicket())
	ticketFormError.value = ""
	ticketInvalidFields.subject = false
	ticketInvalidFields.customer = false
	ticketInvalidFields.raised_by = false
	ticketInvalidFields.description = false
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
	assigned_date: dayjs().format("YYYY-MM-DD"),
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
		scrollToBottom(false)
		if (route.params.name !== ticket.name) {
			router.push({ path: `/tickets/${ticket.name}` })
		}
	})
}

async function handleSaveTicket() {
	ticketFormError.value = ""

	const missingFields = []

	if (!ticketForm.subject?.trim()) {
		missingFields.push("Subject")
	}

	if (!ticketForm.customer?.trim()) {
		missingFields.push("Customer")
	}

	if (!ticketForm.raised_by?.trim()) {
		missingFields.push("Raised By")
	}

	const descText = (ticketForm.description || "").replace(/<[^>]*>/g, "").trim()
	if (!descText) {
		missingFields.push("Description")
	}

	if (missingFields.length > 0) {
		ticketFormError.value = `Please fill all mandatory fields: ${missingFields.join(", ")}.`
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
		const res = await createResource({ url, params }).submit()
		if (res?.error) {
			ticketFormError.value = res.error
			return
		}
		tickets.reload()
		ticketsSummaryResource.reload()
		showCreateDialog.value = false
		showEditTicket.value = false
		resetForm()
	} catch (err) {
		console.error("Failed to save ticket", err)
		ticketFormError.value =
			err?.message || "An error occurred while saving the ticket."
	} finally {
		saving.value = false
	}
}

function openTaskCreateDialog(ticket) {
	Object.assign(newTask, {
		...initialForm,
		attachments: [],
		assigned_date: dayjs().format("YYYY-MM-DD"),
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

const createTaskDialogOptions = computed(() => ({
	title: "Create Task",
	size: "4xl",
	actions: [
		{
			label: "Create Task",
			variant: "solid",
			class: "brand-btn",
			loading: taskSaving.value,
			onClick: handleSaveTask,
		},
		{
			label: "Cancel",
			variant: "ghost",
			onClick: () => {
				showCreateTaskDialog.value = false
			},
		},
	],
}))

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
		taskFormError.value = (e?.message || "Could not create the task.").replace(/<[^>]*>/g, "").trim()
	} finally {
		taskSaving.value = false
	}
}

/* DYNAMIC FILTER RULES & ACTIVE CHIPS */
const FILTERABLE_FIELDS = [
	{ label: "Client", value: "customer", key: "customer" },
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
	if (fieldKey === "customer")
		return customerFilterSelectOptions.value.filter((c) => c.value !== "")
	if (fieldKey === "department")
		return departmentFilterSelectOptions.value.filter((d) => d.value !== "")
	if (fieldKey === "raised_by")
		return raisedByFilterSelectOptions.value.filter((u) => u.value !== "")
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
	{
		label: "Subject",
		key: "subject",
		icon: IconList,
		width: "3.5fr",
		mandatory: true,
	},
	{ label: "Ticket ID", key: "name", icon: IconHash, width: "140px" },
	{ label: "Client", key: "customer", icon: IconBriefcase, width: "160px" },
	{ label: "Status", key: "status", icon: IconAlertCircle, width: "130px" },
	{ label: "Priority", key: "priority", icon: IconBriefcase, width: "130px" },
	{ label: "Raised By", key: "raised_by", icon: IconUser, width: "200px" },
	{ label: "Raised On", key: "creation", icon: IconClock, width: "180px" },
	{
		label: "First Response Time",
		key: "first_response_time",
		icon: IconClock,
		width: "180px",
	},
	{ label: "Closed Time", key: "closed_time", icon: IconClock, width: "180px" },
	{
		label: "Ticket Type",
		key: "ticket_type",
		icon: IconBriefcase,
		width: "140px",
	},
	{ label: "Agent Group", key: "agent_group", icon: IconUser, width: "160px" },
]

const DEFAULT_COLUMN_KEYS = [
	"name",
	"subject",
	"customer",
	"status",
	"priority",
	"raised_by",
	"creation",
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
	return activeColumnKeys.value.map((key) => map.get(key)).filter(Boolean)
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
	return (
		{
			Open: "bg-blue-500",
			Replied: "bg-orange-400",
			Resolved: "bg-green-500",
			Closed: "bg-slate-400",
		}[status] || "bg-slate-300"
	)
}

function getStatusPillClass(status) {
	return (
		{
			Open: "bg-surface-blue-1 text-ink-blue-3",
			Replied: "bg-surface-amber-1 text-ink-amber-3",
			Resolved: "bg-surface-green-1 text-ink-green-3",
			Closed: "bg-surface-gray-2 text-ink-gray-6",
		}[status] || "bg-surface-gray-2 text-ink-gray-6"
	)
}

const summaryLoading = computed(() => ticketsSummaryResource.loading)

function statTitle(label) {
	return label.charAt(0) + label.slice(1).toLowerCase()
}

function statDot(label) {
	return (
		{
			TOTAL: "bg-slate-400",
			OPEN: "bg-blue-500",
			REPLIED: "bg-orange-400",
			RESOLVED: "bg-green-500",
			CLOSED: "bg-slate-400",
			URGENT: "bg-red-500",
		}[label] || "bg-slate-300"
	)
}

function fileExt(name) {
	const m = /\.([a-z0-9]+)$/i.exec(name || "")
	return m ? m[1].toUpperCase() : "File"
}

function clearSelection() {
	selectedTickets.value = new Set()
}

function refreshAll() {
	fetchTickets()
	fetchTicketSummary()
}

// "/" focuses the search box (when not typing and no panel/dialog is open)
function handleSlashKey(e) {
	if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey) return
	const t = e.target
	const typing = t && (t.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(t.tagName))
	if (typing || showEditTicket.value || showCreateDialog.value || showCreateTaskDialog.value) return
	e.preventDefault()
	searchInputEl.value?.focus()
}

function getPriorityTheme(p) {
	return (
		{ High: "red", Medium: "orange", Low: "gray", Urgent: "red" }[p] || "gray"
	)
}

const activityContainerRef = ref(null)

function scrollToBottom(smooth = true) {
	nextTick(() => {
		if (activityContainerRef.value) {
			activityContainerRef.value.scrollTo({
				top: activityContainerRef.value.scrollHeight,
				behavior: smooth ? "smooth" : "auto",
			})
		}
	})
}

const isCurrentViewerTicketRaiser = computed(() => {
	if (session.isTicketRaiser) return true
	if (ticketForm.raised_by && ticketForm.raised_by === session.user) return true
	if (ticketForm.raised_by_user && ticketForm.raised_by_user === session.user)
		return true
	return false
})

function isCommentFromTicketRaiser(c) {
	if (!c) return false
	const author = c.owner || c.comment_by
	if (!author) return false

	if (ticketForm.raised_by && author === ticketForm.raised_by) return true
	if (ticketForm.raised_by_user && author === ticketForm.raised_by_user)
		return true

	if (session.isTicketRaiser && author === session.user) return true

	if (userResource.data && userResource.data.some((u) => u.value === author)) {
		return true
	}

	if (
		ticketForm.owner &&
		author === ticketForm.owner &&
		!userResourceTask.data?.some((u) => u.value === author) &&
		author !== "Administrator"
	) {
		return true
	}

	return false
}

function isCommentOnRight(c) {
	if (!c) return false
	const fromRaiser = isCommentFromTicketRaiser(c)
	if (isCurrentViewerTicketRaiser.value) {
		// When ticket raiser is messaging he should see his message on right side
		return fromRaiser || c.owner === session.user
	} else {
		// When support team opens their activity should show right side and ticket raiser activity should show left side
		if (c.owner === session.user) return true
		return !fromRaiser
	}
}

watch(
	() => comments.data,
	() => {
		scrollToBottom()
	},
	{ deep: true },
)

const commentSubmitting = ref(false)
const commentError = ref("")
const commentUpdating = ref(false)

async function addComment() {
	if (!newComment.value || commentSubmitting.value) return
	commentError.value = ""
	commentSubmitting.value = true
	try {
		await createResource({
			url: "tactix.api.ticket.add_comment",
			params: { ticket: ticketForm.name, content: newComment.value },
		}).submit()
		newComment.value = ""
		await comments.submit({ ticket: ticketForm.name })
		scrollToBottom()
	} catch (e) {
		console.error("Add comment failed", e)
		commentError.value = "Message not sent. " + (e?.message || "Please try again.").replace(/<[^>]*>/g, "")
	} finally {
		commentSubmitting.value = false
	}
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
	commentUpdating.value = true
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
		commentError.value = "Could not update the message."
	} finally {
		commentUpdating.value = false
	}
}

async function handleDeleteComment(name) {
	if (!window.confirm("Delete this message?")) return
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
		commentError.value = "Could not delete the message."
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
	window.addEventListener("keydown", handleSlashKey)
	if (socket) {
		socket.on("tactix_ticket_raised", onTicketRaised)
	}
})

onUnmounted(() => {
	window.removeEventListener("keydown", handleGlobalKeydown)
	window.removeEventListener("keydown", handleSlashKey)
	if (socket) {
		socket.off("tactix_ticket_raised", onTicketRaised)
	}
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
	transition: border-color 0.15s, box-shadow 0.15s, background-color 0.15s;
}
.kpi:hover {
	border-color: var(--brand-border, #a6dcff);
}
.kpi.is-active {
	border-color: var(--brand, #29adff);
	background: var(--brand-soft, #e9f6ff);
	box-shadow: 0 0 0 1px var(--brand, #29adff) inset;
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
	border-color: var(--brand-border, #a6dcff);
	background: var(--brand-soft, #e9f6ff);
	color: var(--brand-text, #0a84d0);
	font-weight: 500;
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

/* ---- Ticket panel ---- */
.section-title {
	display: block;
	font-size: 11px;
	font-weight: 600;
	letter-spacing: 0.06em;
	text-transform: uppercase;
	color: var(--ink-gray-5, #7c7c7c);
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
.slide-enter-active, .slide-leave-active { transition: transform .3s cubic-bezier(0.4, 0, 0.2, 1); }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }

/* Ensure frappe-ui dialogs are always above page-level filters and sticky elements. */
:global(.dialog-overlay) { z-index: 1200; }
:global(.dialog-content) { position: relative; z-index: 1201; }
/* Keep autocomplete/select popovers above dialogs so dropdowns are usable inside modals. */
:global([data-radix-popper-content-wrapper]), :global([data-reka-popper-content-wrapper]), :global(.PopoverContent), :global(.ticket-modal-autocomplete) { z-index: 100005 !important; }
/* Ensure list-view filter dropdowns render above cards/list containers as well. */
:global(.ticket-filter-autocomplete) { z-index: 100005 !important; }
</style>