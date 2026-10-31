<template>
  <div class="flex flex-col h-full overflow-hidden font-sans min-h-0">
    <!-- KPI strip -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-2 p-1 flex-shrink-0">
      <div
        v-for="k in kpis"
        :key="k.label"
        :role="k.filter ? 'button' : undefined"
        :tabindex="k.filter ? 0 : undefined"
        class="kpi text-left"
        :class="[k.filter && 'is-clickable', k.filter && selectedStatus === k.filter && 'is-active']"
        :title="k.filter ? (selectedStatus === k.filter ? 'Click to clear filter' : 'Show ' + k.filter.toLowerCase() + ' timesheets') : undefined"
        @click="k.filter && toggleStatus(k.filter)"
        @keydown.enter.prevent="k.filter && toggleStatus(k.filter)"
        @keydown.space.prevent="k.filter && toggleStatus(k.filter)"
      >
        <div class="flex items-center justify-between gap-2">
          <span class="truncate text-xs font-medium text-ink-gray-6">{{ k.label }}</span>
          <span class="grid h-6 w-6 shrink-0 place-items-center rounded-md" :class="k.chip">
            <component :is="k.icon" class="h-3.5 w-3.5" />
          </span>
        </div>
        <div class="mt-1.5 flex h-7 items-end gap-1">
          <div v-if="timesheetsSummary.loading" class="skeleton h-5 w-12"></div>
          <template v-else>
            <span class="text-[22px] font-semibold leading-none tabular-nums text-ink-gray-9">{{ k.value }}</span>
            <span v-if="k.unit" class="pb-0.5 text-xs font-medium text-ink-gray-5">{{ k.unit }}</span>
          </template>
        </div>
      </div>
    </div>

    <!-- Actions & Filter Header -->
    <div class="toolbar-card flex flex-col gap-2.5 mx-1 my-2 flex-shrink-0">
      <!-- Top Row: Search & Actions -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 w-full pb-2 border-b border-outline-gray-1">

        <!-- Search Bar with Clear Icon -->
        <div class="relative w-full sm:w-80">
          <IconSearch class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-ink-gray-4" />
          <input
            ref="searchInputEl"
            v-model="searchQuery"
            type="text"
            placeholder="Search this page: ID, employee, status…"
            class="h-8 w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 pl-9 pr-9 text-[13px] text-ink-gray-8 outline-none transition focus:border-[color:var(--brand,#29ADFF)] focus:bg-surface-white focus:ring-2 focus:ring-[color:var(--brand-soft,#E9F6FF)]"
          />
          <kbd v-if="!searchQuery" class="kbd absolute right-2 top-1/2 -translate-y-1/2" title="Press / to search">/</kbd>
          <button
            v-if="searchQuery"
            title="Clear search"
            @click="searchQuery = ''"
            class="absolute right-2.5 top-1/2 -translate-y-1/2 text-ink-gray-4 hover:text-ink-gray-6 p-0.5 rounded-full border-none bg-transparent cursor-pointer"
          >
            <IconX class="w-3.5 h-3.5" />
          </button>
        </div>

        <!-- Right Side Action Group -->
        <div class="flex items-center gap-2 ml-auto sm:ml-0 flex-wrap justify-end">
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
                title="Filter Timesheets"
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
                    <span>Filter Timesheets</span>
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
                      class="p-1 hover:bg-red-50 dark:hover:bg-red-950/40 rounded text-ink-gray-4 hover:text-red-500 transition-colors shrink-0 cursor-pointer"
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

          <!-- Refresh Button -->
          <Button
            variant="outline"
            class="!text-ink-gray-6 !px-2.5 !h-8 border border-outline-gray-2 hover:bg-surface-gray-1 transition-all rounded-md"
            @click="reloadTimesheets"
            title="Refresh timesheets"
          >
            <template #prefix><IconRefresh class="w-3.5 h-3.5 text-ink-gray-5" :class="timesheets.loading && 'animate-spin'" /></template>
          </Button>

          <!-- Selection info -->
          <div v-if="employeeInfoResource.data?.is_system_manager && selectedTimesheets.size > 0" class="flex h-8 items-center gap-1 rounded-md bg-surface-gray-2 pl-2.5 pr-1 text-xs text-ink-gray-7">
            <span class="font-medium tabular-nums">{{ selectedTimesheets.size }} selected</span>
            <button type="button" class="rounded p-1 text-ink-gray-5 hover:bg-surface-gray-3 hover:text-ink-gray-8" title="Clear selection" @click="selectedTimesheets = new Set()">
              <IconX class="h-3.5 w-3.5" />
            </button>
          </div>

          <!-- Actions Dropdown -->
          <Dropdown
            v-if="employeeInfoResource.data?.is_system_manager && selectedTimesheets.size > 0"
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

          <!-- New Timesheet Button -->
          <Button
            variant="solid"
            class="brand-btn !text-xs !px-4 !h-8 rounded-md font-medium"
            @click="openCreateDialog"
          >
            <template #prefix><IconPlus class="w-3.5 h-3.5" /></template>
            New Timesheet
          </Button>
        </div>
      </div>

      <!-- Bottom Row: Quick Filter Bar -->
      <div class="filter-row flex flex-nowrap overflow-x-auto pb-1 gap-2 w-full custom-scrollbar sm:flex-wrap sm:overflow-visible sm:pb-0 sm:items-center sm:gap-2">
        <!-- Status Autocomplete Filter -->
        <div class="w-36 shrink-0">
          <Autocomplete
            ref="statusAutocomplete"
            :options="statusOptions"
            :modelValue="selectedStatus"
            @update:modelValue="val => selectedStatus = (val && typeof val === 'object') ? (val.value ?? '') : (val ?? '')"
            :compare-fn="compareOption"
          >
            <template #target>
              <button
                type="button"
                @click="() => statusAutocomplete?.togglePopover()"
                :class="['qf', selectedStatus !== '' && 'on']"
              >
                <span class="truncate">{{ getFilterLabel('selectedStatus', selectedStatus, 'Status') }}</span>
                <FeatherIcon name="chevron-down" class="size-3.5 opacity-60 ml-auto shrink-0" />
              </button>
            </template>
          </Autocomplete>
        </div>

        <!-- Timespan Autocomplete Filter -->
        <div class="w-36 shrink-0">
          <Autocomplete
            ref="timespanAutocomplete"
            :options="timespanOptions"
            :modelValue="selectedTimespan"
            @update:modelValue="val => selectedTimespan = (val && typeof val === 'object') ? (val.value ?? '') : (val ?? '')"
            :compare-fn="compareOption"
          >
            <template #target>
              <button
                type="button"
                @click="() => timespanAutocomplete?.togglePopover()"
                :class="['qf', selectedTimespan !== '' && 'on']"
              >
                <span class="truncate">{{ getFilterLabel('selectedTimespan', selectedTimespan, 'Timespan') }}</span>
                <FeatherIcon name="chevron-down" class="size-3.5 opacity-60 ml-auto shrink-0" />
              </button>
            </template>
          </Autocomplete>
        </div>

        <!-- Employee Autocomplete Filter -->
        <div v-if="employeeInfoResource.data?.is_system_manager" class="w-40 shrink-0">
          <Autocomplete
            ref="employeeAutocomplete"
            :options="employeeOptions"
            :modelValue="selectedEmployee"
            @update:modelValue="val => selectedEmployee = (val && typeof val === 'object') ? (val.value ?? '') : (val ?? '')"
            :compare-fn="compareOption"
            :max-options="100"
          >
            <template #target>
              <button
                type="button"
                @click="() => employeeAutocomplete?.togglePopover()"
                :class="['qf', selectedEmployee !== '' && 'on']"
              >
                <span class="truncate">{{ getFilterLabel('selectedEmployee', selectedEmployee, 'Employee') }}</span>
                <FeatherIcon name="chevron-down" class="size-3.5 opacity-60 ml-auto shrink-0" />
              </button>
            </template>
          </Autocomplete>
        </div>

        <!-- Clear Button -->
        <Button 
          v-if="hasActiveFilters"
          variant="ghost" 
          class="!text-red-500 hover:!bg-red-50 dark:hover:!bg-red-950/40 !px-2 !h-7 text-xs font-medium shrink-0"
          @click="resetFilters"
        >
          <template #prefix><IconX class="w-3.5 h-3.5" /></template>
          Clear
        </Button>
      </div>
    </div>

    <!-- Timesheets List Table -->
    <div class="flex-1 overflow-y-auto md:overflow-hidden px-1 pb-2 flex flex-col min-h-0">
      <p v-if="pageError" class="mb-2 flex items-center justify-between gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
        <span class="flex items-center gap-2"><IconAlertCircle class="h-4 w-4 shrink-0" />{{ pageError }}</span>
        <button type="button" class="opacity-60 hover:opacity-100" title="Dismiss" @click="pageError = ''"><IconX class="h-3.5 w-3.5" /></button>
      </p>
      <div class="relative bg-surface-white rounded-xl border border-outline-gray-2 shadow-sm flex-col overflow-hidden min-h-[420px] md:min-h-0 md:flex-1 md:overflow-hidden flex">
        <div v-if="timesheets.loading" class="busy-bar" aria-hidden="true"></div>
        <ListView
          class="h-full flex flex-col min-h-0"
          :columns="columns"
          :rows="filteredTimesheets || []"
          :options="{
            selectable: employeeInfoResource.data?.is_system_manager,
            showTooltip: true,
            resizeColumn: true,
            onRowClick: (row) => openTimesheetDetails(row),
            emptyState: {
              title: hasActiveFilters ? 'No timesheets match your filters' : 'No timesheets yet',
              description: hasActiveFilters ? 'Try another status or timespan, or clear the filters.' : 'Log your first hours with the New Timesheet button.',
            },
          }"
          row-key="name"
          v-model:selections="selectedTimesheets"
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
                v-for="row in filteredTimesheets"
                :key="row.name"
                :row="row"
              >
                <ListRowItem :item="item">
                  <template v-if="column.key === 'name'">
                    <span class="font-mono text-[12px] font-semibold text-[color:var(--brand-text,#0A84D0)]">#{{ row.name }}</span>
                  </template>

                  <template v-if="column.key === 'employee_name'">
                    <span class="truncate text-sm text-ink-gray-8">{{ row.employee_name || row.employee || '—' }}</span>
                  </template>

                  <template v-if="column.key === 'start_date'">
                    <span class="text-xs text-ink-gray-7 font-medium">
                      {{ row.start_date ? formatDate(row.start_date) : '' }}
                    </span>
                  </template>

                  <template v-if="column.key === 'total_hours'">
                    <span class="inline-flex items-center gap-1.5 text-xs font-semibold tabular-nums text-ink-gray-8">
                      <IconClock class="h-3.5 w-3.5 text-ink-gray-4" />{{ fmtHours(row.total_hours) }} hrs
                    </span>
                  </template>

                  <template v-if="column.key === 'status'">
                    <span class="status-pill" :class="row.status === 'Submitted' ? 'is-submitted' : row.status === 'Cancelled' ? 'is-cancelled' : 'is-draft'">
                      <span class="h-1.5 w-1.5 rounded-full bg-current"></span>{{ row.status }}
                    </span>
                  </template>

                  <template v-if="column.key === 'actions'">
                    <div class="flex items-center justify-end space-x-1.5" v-if="employeeInfoResource.data?.is_system_manager">
                      <Button 
                        variant="ghost" 
                        class="!text-red-600 hover:!bg-red-50 !p-1.5 rounded-lg"
                        title="Delete timesheet"
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

    <!-- Create Timesheet Dialog -->
    <Dialog v-model="showCreateDialog" :disable-outside-click-to-close="true" :options="{ title: dialogOptions.title, size: dialogOptions.size }">
      <template #body-content>
        <div class="space-y-6 py-2">
          <p v-if="formError" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-2.5 shadow-sm font-semibold flex items-center gap-2">
            <IconAlertCircle class="w-4 h-4 text-red-500 flex-shrink-0" /> {{ formError }}
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
            <!-- Date Picker -->
            <DatePicker 
              label="Timesheet Date *" 
              v-model="timesheetForm.date" 
            />
            <!-- Employee Info -->
            <template v-if="employeeInfoResource.data?.is_system_manager">
              <div class="space-y-1.5">
                <label class="block text-xs text-ink-gray-5">Employee *</label>
                <Autocomplete
                  ref="createEmployeeAutocomplete"
                  :options="[{label: 'Select Employee', value: ''}, ...(employeeOptionsResource.data || [])]"
                  :modelValue="timesheetForm.employee"
                  @update:modelValue="val => timesheetForm.employee = (val && typeof val === 'object') ? (val.value ?? '') : (val ?? '')"
                  :compare-fn="compareOption"
                  :max-options="100"
                >
                  <template #target>
                    <button
                      type="button"
                      @click="() => createEmployeeAutocomplete?.togglePopover()"
                      class="flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 text-xs transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-ink-gray-8 cursor-pointer"
                    >
                      <span class="truncate">{{ getEmployeeLabel(timesheetForm.employee) }}</span>
                      <FeatherIcon name="chevron-down" class="h-4 w-4 text-ink-gray-5 shrink-0" />
                    </button>
                  </template>
                </Autocomplete>
              </div>
            </template>
            <template v-else>
              <div class="space-y-1.5">
                <label class="block text-xs text-ink-gray-6 font-medium">Employee *</label>
                <div class="px-3 h-[2.25rem] bg-surface-gray-1 border border-outline-gray-2 rounded-lg text-xs text-ink-gray-8 font-medium flex items-center gap-2">
                  <div class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
                  {{ employeeInfoResource.data?.employee_name || 'Loading profile...' }}
                </div>
              </div>
            </template>
          </div>

          <!-- Dynamic Time Logs Table -->
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <label class="text-xs font-black text-ink-gray-5 uppercase tracking-widest flex items-center gap-1.5">
                <IconClock class="w-4 h-4 text-ink-gray-4" /> Time Log Rows
              </label>
              <Button
                variant="outline"
                size="sm"
                class="!text-[color:var(--brand-text,#0A84D0)] hover:!bg-[color:var(--brand-soft,#E9F6FF)] !px-4 !h-8 font-semibold border-[color:var(--brand-border,#A6DCFF)] hover:border-[color:var(--brand,#29ADFF)] rounded-lg transition-all"
                @click="addRow"
              >
                <template #prefix><IconPlus class="w-3.5 h-3.5" /></template> Add Task Row
              </Button>
            </div>

            <div class="border border-outline-gray-2 rounded-xl overflow-x-auto shadow-sm max-h-[300px] overflow-y-auto custom-scrollbar">
              <table class="w-full text-left text-xs border-collapse">
                <thead class="bg-surface-gray-1 border-b border-outline-gray-2 text-ink-gray-5 uppercase font-semibold sticky top-0 z-10">
                  <tr>
                    <th class="px-4 py-3 w-1/3">Task</th>
                    <th class="px-4 py-3 w-1/4">Activity *</th>
                    <th class="px-4 py-3 w-24 text-right">Hours</th>
                    <th class="px-4 py-3">Description</th>
                    <th class="px-4 py-3 w-10 text-right"></th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-outline-gray-1 bg-surface-white">
                  <tr v-for="(row, idx) in timesheetForm.time_logs" :key="idx" class="hover:bg-surface-gray-1 transition-colors">
                    <td class="px-2 py-2">
                      <Autocomplete
                        :ref="el => setTaskRef(el, idx)"
                        :options="taskOptionsWithDefault"
                        :modelValue="row.task"
                        @update:modelValue="val => row.task = (val && typeof val === 'object') ? (val.value ?? '') : (val ?? '')"
                        :compare-fn="compareOption"
                        :max-options="100"
                      >
                        <template #target>
                          <button
                            type="button"
                            @click="() => taskRowRefs[idx]?.togglePopover()"
                            class="flex h-9 w-full items-center justify-between gap-1.5 rounded-lg bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-surface-white border border-outline-gray-2 hover:border-outline-gray-3 focus:border-[color:var(--brand,#29ADFF)] focus:ring-2 focus:ring-[color:var(--brand,#29ADFF)] px-2.5 py-1.5 text-xs font-medium text-ink-gray-7 transition-all cursor-pointer"
                          >
                            <span class="truncate">{{ getTaskLabel(row.task) }}</span>
                            <FeatherIcon name="chevron-down" class="h-3.5 w-3.5 text-ink-gray-4 shrink-0 ml-1" />
                          </button>
                        </template>
                      </Autocomplete>
                    </td>
                    <td class="px-2 py-2">
                      <Autocomplete
                        :ref="el => setActivityRef(el, idx)"
                        :options="activityOptions"
                        :modelValue="row.activity_type"
                        @update:modelValue="val => row.activity_type = (val && typeof val === 'object') ? (val.value ?? '') : (val ?? '')"
                        :compare-fn="compareOption"
                      >
                        <template #target>
                          <button
                            type="button"
                            @click="() => activityRowRefs[idx]?.togglePopover()"
                            class="flex h-9 w-full items-center justify-between gap-1.5 rounded-lg bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-surface-white border border-outline-gray-2 hover:border-outline-gray-3 focus:border-[color:var(--brand,#29ADFF)] focus:ring-2 focus:ring-[color:var(--brand,#29ADFF)] px-2.5 py-1.5 text-xs font-medium text-ink-gray-7 transition-all cursor-pointer"
                          >
                            <span class="truncate">{{ row.activity_type || 'Select Activity' }}</span>
                            <FeatherIcon name="chevron-down" class="h-3.5 w-3.5 text-ink-gray-4 shrink-0 ml-1" />
                          </button>
                        </template>
                      </Autocomplete>
                    </td>
                    <td class="px-2 py-2">
                      <input 
                        v-model.number="row.hours" 
                        type="number" 
                        step="0.5" 
                        min="0.1" 
                        class="w-full h-9 px-2.5 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-surface-white border border-outline-gray-2 hover:border-outline-gray-3 focus:border-[color:var(--brand,#29ADFF)] focus:ring-2 focus:ring-[color:var(--brand,#29ADFF)] rounded-lg outline-none text-xs font-semibold text-ink-gray-8 text-right transition-all" 
                      />
                    </td>
                    <td class="px-2 py-2">
                      <input 
                        v-model="row.description" 
                        placeholder="Provide details..." 
                        class="w-full h-9 px-3 bg-surface-gray-1 hover:bg-surface-gray-2 focus:bg-surface-white border border-outline-gray-2 hover:border-outline-gray-3 focus:border-[color:var(--brand,#29ADFF)] focus:ring-2 focus:ring-[color:var(--brand,#29ADFF)] rounded-lg outline-none text-xs text-ink-gray-7 transition-all" 
                      />
                    </td>
                    <td class="px-2 py-2 text-right">
                      <button 
                        class="p-1.5 text-ink-gray-4 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                        type="button"
                        title="Remove row"
                        @click="removeRow(idx)"
                      >
                        <IconX class="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                  <tr v-if="timesheetForm.time_logs.length === 0">
                    <td colspan="6" class="px-4 py-8 text-center text-ink-gray-4 italic font-semibold">
                      No rows added yet. Add a row to get started.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="flex items-center justify-between p-3.5 bg-[color:var(--brand-soft,#E9F6FF)] rounded-xl border border-[color:var(--brand-border,#A6DCFF)] text-xs font-bold">
              <span class="text-[color:var(--brand-text,#0A84D0)] uppercase tracking-wider font-extrabold">Total Logged Hours</span>
              <span class="text-sm font-black text-[color:var(--brand-text,#0A84D0)] bg-[color:var(--brand-soft,#E9F6FF)] px-3.5 py-1 rounded-lg">{{ fmtHours(computedTotalHours) }} hrs</span>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="dialog-actions">
          <Button
            v-for="a in [...dialogOptions.actions].reverse()"
            :key="a.label"
            :variant="a.variant"
            :theme="a.theme"
            :loading="a.loading"
            :disabled="a.disabled"
            :class="a.class"
            @click="a.onClick"
          >
            {{ a.label }}
          </Button>
        </div>
      </template>
    </Dialog>

    <!-- View Timesheet Details Dialog -->
    <Dialog v-model="showViewDialog" :disable-outside-click-to-close="true" :options="{ title: viewDialogOptions.title, size: viewDialogOptions.size }">
      <template #body-content>
        <div class="space-y-6 py-2" v-if="selectedTimesheet">
          <p v-if="viewError" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-2.5 shadow-sm font-semibold flex items-center gap-2">
            <IconAlertCircle class="w-4 h-4 text-red-500 flex-shrink-0" /> {{ viewError }}
          </p>
          <!-- Summary Cards Row -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
            <!-- Date Card -->
            <div class="bg-[color:var(--brand-soft,#E9F6FF)] border border-[color:var(--brand-border,#A6DCFF)] rounded-xl p-2 flex flex-col justify-between shadow-sm">
              <div class="flex items-center justify-between mb-2">
                <span class="text-[10px] font-semibold text-[color:var(--brand-text,#0A84D0)] uppercase tracking-wider">Date</span>
                <div class="p-1.5 rounded-lg bg-[color:var(--brand-soft,#E9F6FF)]">
                  <IconCalendar class="w-3.5 h-3.5 text-[color:var(--brand-text,#0A84D0)]" />
                </div>
              </div>
              <div class="text-lg font-black text-[color:var(--brand-text,#0A84D0)] leading-none">
                {{ formatDate(selectedTimesheet.start_date) }}
              </div>
            </div>

            <!-- Employee Card -->
            <div class="bg-[color:var(--brand-soft,#E9F6FF)] border border-[color:var(--brand-border,#A6DCFF)] rounded-xl p-2 flex flex-col justify-between shadow-sm">
              <div class="flex items-center justify-between mb-2">
                <span class="text-[10px] font-semibold text-[color:var(--brand-text,#0A84D0)] uppercase tracking-wider">Employee</span>
                <div class="p-1.5 rounded-lg bg-[color:var(--brand-soft,#E9F6FF)]">
                  <IconUser class="w-3.5 h-3.5 text-[color:var(--brand-text,#0A84D0)]" />
                </div>
              </div>
              <div class="text-sm font-black text-[color:var(--brand-text,#0A84D0)] truncate leading-none">
                {{ selectedTimesheet.employee_name || selectedTimesheet.employee || '—' }}
              </div>
            </div>

            <!-- Total Hours Card -->
            <div class="bg-emerald-50/40 border border-emerald-100 rounded-xl p-2 flex flex-col justify-between shadow-sm">
              <div class="flex items-center justify-between mb-2">
                <span class="text-[10px] font-semibold text-emerald-600 uppercase tracking-wider">Total hours</span>
                <div class="p-1.5 rounded-lg bg-emerald-100/50">
                  <IconClock class="w-3.5 h-3.5 text-emerald-600" />
                </div>
              </div>
              <div class="text-lg font-black text-emerald-800 leading-none">
                {{ fmtHours(selectedTimesheet.total_hours) }} hrs
              </div>
            </div>
          </div>

          <!-- Time Logs Details Table -->
          <div class="border border-outline-gray-2 rounded-xl overflow-x-auto shadow-sm">
            <table class="w-full text-left text-xs border-collapse">
              <thead class="bg-surface-gray-1 border-b border-outline-gray-2 text-ink-gray-5 uppercase font-semibold">
                <tr>
                  <th class="px-4 py-3.5">Task</th>
                  <th class="px-4 py-3.5">Activity</th>
                  <th class="px-4 py-3.5 text-right w-24">Hours</th>
                  <th class="px-4 py-3.5">Description</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-outline-gray-1 bg-surface-white">
                <tr v-for="(log, idx) in selectedTimesheet.time_logs" :key="idx" class="hover:bg-surface-gray-1 transition-colors duration-150">
                  <td class="px-4 py-3.5 font-bold text-ink-gray-8">
                    {{ log.task ? (log.task_subject ? `${log.task_subject} (${log.task})` : log.task) : '—' }}
                  </td>
                  <td class="px-4 py-3.5">
                    <Badge theme="gray" variant="subtle" class="!px-2.5 !py-1 text-[11px] font-semibold">{{ log.activity_type }}</Badge>
                  </td>
                  <td class="px-4 py-3.5 text-right font-semibold tabular-nums text-ink-gray-7">{{ fmtHours(log.hours) }} hrs</td>
                  <td class="px-4 py-3.5 text-ink-gray-5 whitespace-pre-wrap leading-relaxed">{{ log.description || '—' }}</td>

                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="dialog-actions">
          <Button
            v-for="a in [...viewDialogOptions.actions].reverse()"
            :key="a.label"
            :variant="a.variant"
            :theme="a.theme"
            :loading="a.loading"
            :disabled="a.disabled"
            :class="a.class"
            @click="a.onClick"
          >
            {{ a.label }}
          </Button>
        </div>
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model="deleteConfirm.show" 
      :disable-outside-click-to-close="true"
      :options="{ title: deleteConfirm.isBulk ? 'Delete Selected Timesheets' : 'Delete Timesheet', size: 'sm' }"
    >
      <template #body-content>
        <p class="text-sm text-ink-gray-6 leading-relaxed py-2">
          <span v-if="deleteConfirm.isBulk">
            This will permanently remove <span class="font-bold text-ink-gray-9">{{ deleteConfirm.count }}</span> selected timesheet(s). This action cannot be undone.
          </span>
          <span v-else>
            This will permanently remove timesheet <span class="font-bold text-ink-gray-9">#{{ deleteConfirm.targetName }}</span>. This action cannot be undone.
          </span>
        </p>
        <p v-if="deleteConfirm.error" class="mt-1 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700 whitespace-pre-line">
          {{ deleteConfirm.error }}
        </p>
      </template>
      <template #actions>
        <div class="dialog-actions">
          <Button
            v-for="a in [...deleteDialogActions].reverse()"
            :key="a.label"
            :variant="a.variant"
            :theme="a.theme"
            :loading="a.loading"
            :disabled="a.disabled"
            :class="a.class"
            @click="a.onClick"
          >
            {{ a.label }}
          </Button>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import dayjs from "dayjs"
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
	Popover,
	Select,
	createResource,
} from "frappe-ui"
import { computed, onMounted, onUnmounted, reactive, ref, watch } from "vue"

import IconAlertCircle from "~icons/lucide/alert-circle"
import IconCalendar from "~icons/lucide/calendar"
import IconCheck from "~icons/lucide/check"
import IconCheckCircle from "~icons/lucide/check-circle"
import IconChevronDown from "~icons/lucide/chevron-down"
import IconChevronLeft from "~icons/lucide/chevron-left"
import IconChevronRight from "~icons/lucide/chevron-right"
import IconChevronsLeft from "~icons/lucide/chevrons-left"
import IconChevronsRight from "~icons/lucide/chevrons-right"
// Icons
import IconClock from "~icons/lucide/clock"
import IconFilter from "~icons/lucide/filter"
import IconHash from "~icons/lucide/hash"
import IconPlus from "~icons/lucide/plus"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconSearch from "~icons/lucide/search"
import IconTrash from "~icons/lucide/trash-2"
import IconUser from "~icons/lucide/user"
import IconX from "~icons/lucide/x"

// Local date as YYYY-MM-DD (toISOString is UTC and gives yesterday's date early in the morning)
function localToday() {
	return dayjs().format("YYYY-MM-DD")
}

// 7.5, 8, 0.25 — never 7.499999999
function fmtHours(h) {
	const n = Number(h) || 0
	return Number.isInteger(n) ? String(n) : n.toFixed(2).replace(/0$/, "")
}

const searchInputEl = ref(null)
const pageError = ref("")

// State variables
const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const searchQuery = ref("")
const selectedStatus = ref("")
const selectedTimespan = ref("")
const selectedEmployee = ref("")
const currentPage = ref(1)
const pageLength = 20

// Filter options for Autocomplete dropdowns
const statusOptions = [
	{ label: "All Statuses", value: "" },
	{ label: "Draft", value: "Draft" },
	{ label: "Submitted", value: "Submitted" },
]

const timespanOptions = [
	{ label: "All Time", value: "" },
	{ label: "Today", value: "today" },
	{ label: "Yesterday", value: "yesterday" },
	{ label: "This Week", value: "this_week" },
	{ label: "Last Week", value: "last_week" },
	{ label: "This Month", value: "this_month" },
	{ label: "Last Month", value: "last_month" },
]

const employeeOptions = computed(() => {
	const opts = [{ label: "All Employees", value: "" }]
	if (
		employeeOptionsResource.data &&
		Array.isArray(employeeOptionsResource.data)
	) {
		return opts.concat(employeeOptionsResource.data)
	}
	return opts
})

// Popover refs for Autocomplete programmatic toggling
const statusAutocomplete = ref(null)
const timespanAutocomplete = ref(null)
const employeeAutocomplete = ref(null)
const createEmployeeAutocomplete = ref(null)

const taskRowRefs = ref([])
const activityRowRefs = ref([])

function setTaskRef(el, idx) {
	if (el) taskRowRefs.value[idx] = el
}
function setActivityRef(el, idx) {
	if (el) activityRowRefs.value[idx] = el
}

const taskOptionsWithDefault = computed(() => [
	{ label: "Select Task (Optional)", value: "" },
	...(taskOptionsResource.data || []),
])

const activityOptions = [
	{ label: "Execution", value: "Execution" },
	{ label: "Planning", value: "Planning" },
	{ label: "Research", value: "Research" },
	{ label: "Communication", value: "Communication" },
	{ label: "Proposal Writing", value: "Proposal Writing" },
]

function compareOption(a, b) {
	const aVal = a && typeof a === "object" ? a.value : a
	const bVal = b && typeof b === "object" ? b.value : b
	return aVal === bVal
}

function getEmployeeLabel(val) {
	const empVal = val && typeof val === "object" ? val.value : val
	if (!empVal) return "Select Employee"
	const match = employeeOptionsResource.data?.find((e) => e.value === empVal)
	return match ? match.label : empVal
}

function getTaskLabel(val) {
	const taskVal = val && typeof val === "object" ? val.value : val
	if (!taskVal) return "Select Task (Optional)"
	const match = taskOptionsResource.data?.find((t) => t.value === taskVal)
	return match ? match.label : taskVal
}

const FILTERABLE_FIELDS = computed(() => {
	const fields = [
		{ label: "Status", value: "selectedStatus", key: "selectedStatus" },
		{ label: "Timespan", value: "selectedTimespan", key: "selectedTimespan" },
	]
	if (employeeInfoResource.data?.is_system_manager) {
		fields.push({
			label: "Employee",
			value: "selectedEmployee",
			key: "selectedEmployee",
		})
	}
	return fields
})

const activeFilterRules = ref([])

function syncActiveFilterRules() {
	const newRules = []
	if (selectedStatus.value) {
		newRules.push({
			id: "rule_selectedStatus",
			field: "selectedStatus",
			value: selectedStatus.value,
		})
	}
	if (selectedTimespan.value) {
		newRules.push({
			id: "rule_selectedTimespan",
			field: "selectedTimespan",
			value: selectedTimespan.value,
		})
	}
	if (selectedEmployee.value && employeeInfoResource.data?.is_system_manager) {
		newRules.push({
			id: "rule_selectedEmployee",
			field: "selectedEmployee",
			value: selectedEmployee.value,
		})
	}
	if (newRules.length === 0) {
		newRules.push({
			id: "rule_" + Date.now(),
			field: "selectedStatus",
			value: "",
		})
	}
	activeFilterRules.value = newRules
}

function addFilterRule() {
	const unusedField = FILTERABLE_FIELDS.value.find(
		(f) => !activeFilterRules.value.some((r) => r.field === f.value),
	)
	const field = unusedField ? unusedField.value : "selectedStatus"
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
		if (removed.field === "selectedStatus") selectedStatus.value = ""
		if (removed.field === "selectedTimespan") selectedTimespan.value = ""
		if (removed.field === "selectedEmployee") selectedEmployee.value = ""
	}
	if (activeFilterRules.value.length === 0) {
		activeFilterRules.value.push({
			id: "rule_" + Date.now(),
			field: "selectedStatus",
			value: "",
		})
	}
}

function applyFilterRules() {
	FILTERABLE_FIELDS.value.forEach((f) => {
		const hasRule = activeFilterRules.value.some((r) => r.field === f.key)
		if (!hasRule) {
			if (f.key === "selectedStatus") selectedStatus.value = ""
			if (f.key === "selectedTimespan") selectedTimespan.value = ""
			if (f.key === "selectedEmployee") selectedEmployee.value = ""
		}
	})
	activeFilterRules.value.forEach((r) => {
		if (r.field === "selectedStatus") selectedStatus.value = r.value
		if (r.field === "selectedTimespan") selectedTimespan.value = r.value
		if (r.field === "selectedEmployee") selectedEmployee.value = r.value
	})
}

function getFieldOptionsForSelect(fieldKey) {
	if (fieldKey === "selectedStatus")
		return statusOptions.filter((o) => o.value !== "")
	if (fieldKey === "selectedTimespan")
		return timespanOptions.filter((o) => o.value !== "")
	if (fieldKey === "selectedEmployee")
		return employeeOptions.value.filter((o) => o.value !== "")
	return []
}

function getFilterLabel(fieldKey, val, defaultText) {
	if (!val) return defaultText
	if (fieldKey === "selectedStatus") {
		const found = statusOptions.find((o) => o.value === val)
		return found ? found.label : val
	}
	if (fieldKey === "selectedTimespan") {
		const found = timespanOptions.find((o) => o.value === val)
		return found ? found.label : val
	}
	if (fieldKey === "selectedEmployee") {
		const found = employeeOptions.value.find((o) => o.value === val)
		return found ? found.label : val
	}
	return val
}

const activeFilterCount = computed(() => {
	let count = 0
	if (selectedStatus.value) count++
	if (selectedTimespan.value) count++
	if (selectedEmployee.value) count++
	return count
})

const hasActiveFilters = computed(() => {
	return (
		searchQuery.value !== "" ||
		selectedStatus.value !== "" ||
		selectedTimespan.value !== "" ||
		selectedEmployee.value !== ""
	)
})

function resetFilters() {
	searchQuery.value = ""
	selectedStatus.value = ""
	selectedTimespan.value = ""
	selectedEmployee.value = ""
}

const filteredTimesheets = computed(() => {
	const raw = timesheets.data?.timesheets || []
	if (!searchQuery.value) return raw
	const q = searchQuery.value.toLowerCase()
	return raw.filter((row) => {
		return (
			(row.name && row.name.toLowerCase().includes(q)) ||
			(row.employee_name && row.employee_name.toLowerCase().includes(q)) ||
			(row.status && row.status.toLowerCase().includes(q)) ||
			(row.start_date && row.start_date.toLowerCase().includes(q))
		)
	})
})
const saving = ref(false)
const formError = ref("")
const viewError = ref("")

const selectedTimesheets = ref(new Set())
const deleteConfirm = reactive({
	show: false,
	isBulk: false,
	targetName: null,
	count: 0,
	loading: false,
	error: "",
})

const actionsOptions = computed(() => [
	{
		label: `Delete Selected (${selectedTimesheets.value.size})`,
		icon: "trash-2",
		onClick: confirmBulkDelete,
	},
])

const deleteDialogActions = computed(() => [
	{
		label: deleteConfirm.isBulk ? `Delete ${deleteConfirm.count} timesheets` : "Delete",
		variant: "solid",
		theme: "red",
		loading: deleteConfirm.loading,
		onClick: executeTimesheetDelete,
	},
	{ label: "Cancel", variant: "ghost", onClick: () => (deleteConfirm.show = false) },
])

function confirmSingleDelete(name) {
	deleteConfirm.error = ""
	deleteConfirm.isBulk = false
	deleteConfirm.targetName = name
	deleteConfirm.count = 1
	deleteConfirm.show = true
}

function confirmBulkDelete() {
	deleteConfirm.error = ""
	deleteConfirm.isBulk = true
	deleteConfirm.targetName = null
	deleteConfirm.count = selectedTimesheets.value.size
	deleteConfirm.show = true
}

async function executeTimesheetDelete() {
	deleteConfirm.loading = true
	deleteConfirm.error = ""
	const names = deleteConfirm.isBulk
		? Array.from(selectedTimesheets.value)
		: deleteConfirm.targetName
			? [deleteConfirm.targetName]
			: []
	const failed = []
	for (const name of names) {
		try {
			await createResource({
				url: "frappe.client.delete",
				params: { doctype: "Timesheet", name },
			}).submit()
			selectedTimesheets.value.delete(name)
		} catch (err) {
			console.error("Error deleting timesheet", name, err)
			failed.push(`#${name}: ${parseError(err)}`)
		}
	}
	selectedTimesheets.value = new Set(selectedTimesheets.value)
	timesheets.reload()
	timesheetsSummary.reload()
	deleteConfirm.loading = false
	if (failed.length) {
		deleteConfirm.error = `Could not delete ${failed.length} of ${names.length}:\n` + failed.join("\n")
	} else {
		deleteConfirm.show = false
	}
}

// KPI cards (Submitted / Draft also act as a status filter)
const kpis = computed(() => {
	const d = timesheetsSummary.data || {}
	return [
		{ label: "Total hours logged", value: fmtHours(d.total_hours), unit: "hrs", icon: IconClock, chip: "bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)]" },
		{ label: "Active days", value: d.active_days || 0, unit: "days", icon: IconCalendar, chip: "bg-surface-gray-2 text-ink-gray-6" },
		{ label: "Submitted", value: d.submitted_count || 0, icon: IconCheckCircle, chip: "bg-green-50 text-green-600", filter: "Submitted" },
		{ label: "Draft", value: d.draft_count || 0, icon: IconAlertCircle, chip: "bg-amber-50 text-amber-600", filter: "Draft" },
	]
})

function toggleStatus(status) {
	selectedStatus.value = selectedStatus.value === status ? "" : status
}

// Selected timesheet for viewing
const selectedTimesheet = ref(null)

const parseError = (err) => {
	if (err.messages && err.messages.length > 0) {
		return err.messages
			.map((m) => {
				try {
					const parsed = JSON.parse(m)
					return parsed.message || m
				} catch {
					return m
				}
			})
			.join("\n")
	}

	if (err.exc) {
		try {
			const parsed = JSON.parse(err.exc)
			if (Array.isArray(parsed)) {
				return parsed
					.map((item) => (typeof item === "string" ? item : item.message))
					.join("\n")
			}
		} catch {
			// Not JSON
		}
	}

	return err.message || "An unexpected error occurred."
}

// Form states
const timesheetForm = reactive({
	date: localToday(),
	employee: "",
	time_logs: [],
})

// Initialize filters
const timesheetFilters = computed(() => {
	const f = {}
	if (selectedStatus.value) {
		f.status = selectedStatus.value
	}
	if (selectedTimespan.value) {
		f.timespan = selectedTimespan.value
	}
	if (selectedEmployee.value && employeeInfoResource.data?.is_system_manager) {
		f.employee = selectedEmployee.value
	}
	return f
})

// Columns
const columns = computed(() => [
	{ label: "Timesheet ID", key: "name", width: "160px", icon: IconHash },
	{ label: "Date", key: "start_date", width: "160px", icon: IconCalendar },
	{ label: "Employee", key: "employee_name", width: "2.5fr", icon: IconUser },
	{ label: "Total Hours", key: "total_hours", width: "150px", icon: IconClock },
	{ label: "Status", key: "status", width: "130px", icon: IconAlertCircle },
	...(employeeInfoResource.data?.is_system_manager
		? [{ label: "Actions", key: "actions", width: "100px" }]
		: []),
])

// API Resources
const timesheets = createResource({
	url: "tactix.api.timesheet.get_timesheets",
	initialData: { timesheets: [], total_count: 0 },
	transform: (data) => {
		if (Array.isArray(data)) {
			return { timesheets: data, total_count: data.length }
		}
		return data || { timesheets: [], total_count: 0 }
	},
})

const timesheetsSummary = createResource({
	url: "tactix.api.timesheet.get_timesheet_summary",
	initialData: {
		total_hours: 0,
		submitted_count: 0,
		draft_count: 0,
		active_days: 0,
	},
})

const taskOptionsResource = createResource({
	url: "tactix.api.timesheet.get_tasks_options",
	initialData: [],
	auto: true,
})

const employeeInfoResource = createResource({
	url: "tactix.api.timesheet.get_employee_info",
	initialData: {},
	auto: true,
})

const employeeOptionsResource = createResource({
	url: "tactix.api.timesheet.get_employees",
	initialData: [],
})

watch(
	() => employeeInfoResource.data,
	(val) => {
		if (val && val.is_system_manager) {
			employeeOptionsResource.fetch()
		}
	},
	{ immediate: true },
)

// Methods
function fetchTimesheets() {
	timesheets.fetch({
		filters: timesheetFilters.value,
		start: (currentPage.value - 1) * pageLength,
		page_length: pageLength,
	})
}

function fetchSummary() {
	timesheetsSummary.fetch({
		filters: timesheetFilters.value,
	})
}

function reloadTimesheets() {
	fetchTimesheets()
	fetchSummary()
}

function handleSlashKey(e) {
	if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey) return
	const t = e.target
	if (t && (t.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(t.tagName))) return
	if (showCreateDialog.value || showViewDialog.value || deleteConfirm.show) return
	e.preventDefault()
	searchInputEl.value?.focus()
}

// Initial fetch
onMounted(() => {
	reloadTimesheets()
	window.addEventListener("keydown", handleSlashKey)
})

onUnmounted(() => {
	window.removeEventListener("keydown", handleSlashKey)
})

// Watch filters
watch(
	timesheetFilters,
	() => {
		fetchSummary()
		if (currentPage.value !== 1) currentPage.value = 1 // the page watcher fetches
		else fetchTimesheets()
	},
	{ deep: true },
)

watch(currentPage, () => {
	fetchTimesheets()
})

const totalCount = computed(() => timesheets.data?.total_count || 0)
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

// Form logic
function addRow() {
	timesheetForm.time_logs.push({
		task: "",
		activity_type: "Execution",
		hours: 1.0,
		description: "",
		is_billable: 0,
	})
}

function removeRow(idx) {
	timesheetForm.time_logs.splice(idx, 1)
}

const computedTotalHours = computed(() => {
	return timesheetForm.time_logs.reduce(
		(sum, row) => sum + (Number.parseFloat(row.hours) || 0),
		0,
	)
})

const isEditMode = ref(false)
const editTimesheetName = ref("")

function openCreateDialog() {
	isEditMode.value = false
	editTimesheetName.value = ""
	formError.value = ""
	viewError.value = ""
	timesheetForm.date = localToday()
	timesheetForm.employee = employeeInfoResource.data?.name || ""
	timesheetForm.time_logs = []
	addRow()
	showCreateDialog.value = true
}

function openEditDialog(timesheetDoc) {
	isEditMode.value = true
	editTimesheetName.value = timesheetDoc.name
	formError.value = ""
	viewError.value = ""
	timesheetForm.date = timesheetDoc.start_date
	timesheetForm.employee = timesheetDoc.employee
	timesheetForm.time_logs = timesheetDoc.time_logs.map((log) => ({
		task: log.task || "",
		activity_type: log.activity_type || "Execution",
		hours: log.hours || 1.0,
		description: log.description || "",
		is_billable: log.is_billable || 0,
	}))
	showCreateDialog.value = true
}

// Create / Edit timesheet action
async function saveTimesheet(submitOption = false) {
	formError.value = ""

	if (!timesheetForm.date) {
		formError.value = "Timesheet Date is required."
		return
	}

	if (!timesheetForm.employee) {
		formError.value = "Employee selection is required."
		return
	}

	if (timesheetForm.time_logs.length === 0) {
		formError.value = "At least one log entry is required."
		return
	}

	for (const log of timesheetForm.time_logs) {
		if (!log.activity_type) {
			formError.value = "Activity Type is required for all rows."
			return
		}
		if ((Number.parseFloat(log.hours) || 0) <= 0) {
			formError.value = "Hours must be greater than zero."
			return
		}
	}

	saving.value = true
	try {
		const payload = {
			date: timesheetForm.date,
			employee: timesheetForm.employee,
			time_logs: timesheetForm.time_logs,
			submit: submitOption,
		}

		const url = isEditMode.value
			? "tactix.api.timesheet.edit_timesheet"
			: "tactix.api.timesheet.create_timesheet"

		const params = isEditMode.value
			? { name: editTimesheetName.value, doc: payload }
			: { doc: payload }

		await createResource({
			url,
			params,
		}).submit()

		showCreateDialog.value = false
		reloadTimesheets()
	} catch (err) {
		formError.value = parseError(err)
	} finally {
		saving.value = false
	}
}

// View Timesheet
async function openTimesheetDetails(row) {
	viewError.value = ""
	try {
		const res = await createResource({
			url: "tactix.api.timesheet.get_timesheet_detail",
			params: {
				name: row.name,
			},
		}).submit()

		selectedTimesheet.value = res
		showViewDialog.value = true
	} catch (err) {
		console.error("Failed to load timesheet details", err)
		pageError.value = "Could not open timesheet #" + row.name + ": " + parseError(err)
	}
}

async function submitTimesheet(name) {
	viewError.value = ""
	saving.value = true
	try {
		await createResource({
			url: "frappe.client.submit",
			params: {
				doctype: "Timesheet",
				docname: name,
			},
		}).submit()
		showViewDialog.value = false
		reloadTimesheets()
	} catch (err) {
		viewError.value = parseError(err)
	} finally {
		saving.value = false
	}
}

// Dialog definitions
const dialogOptions = computed(() => {
	const actions = []
	const hasSubmitPermission = employeeInfoResource.data?.has_submit_permission

	if (hasSubmitPermission) {
		actions.push({
			label: isEditMode.value ? "Submit Changes" : "Submit Timesheet",
			variant: "solid",
			class: "brand-btn",
			loading: saving.value,
			onClick: () => saveTimesheet(true),
		})
	}

	actions.push({
		label: isEditMode.value ? "Save Draft" : "Save as Draft",
		variant: hasSubmitPermission ? "outline" : "solid",
		class: hasSubmitPermission ? undefined : "brand-btn",
		loading: saving.value,
		onClick: () => saveTimesheet(false),
	})

	actions.push({
		label: "Cancel",
		variant: "ghost",
		onClick: () => (showCreateDialog.value = false),
	})

	return {
		title: isEditMode.value ? "Edit Timesheet" : "Create Timesheet",
		size: "5xl",
		actions,
	}
})

const viewDialogOptions = computed(() => {
	const actions = []
	if (selectedTimesheet.value && selectedTimesheet.value.docstatus === 0) {
		actions.push({
			label: "Edit",
			variant: "outline",
			onClick: () => {
				showViewDialog.value = false
				openEditDialog(selectedTimesheet.value)
			},
		})
		if (selectedTimesheet.value.has_submit_permission) {
			actions.push({
				label: "Submit",
				variant: "solid",
				class: "brand-btn",
				loading: saving.value,
				onClick: () => submitTimesheet(selectedTimesheet.value.name),
			})
		}
	}
	actions.push({
		label: "Close",
		variant: "ghost",
		onClick: () => (showViewDialog.value = false),
	})
	return {
		title: `Timesheet Details`,
		size: "4xl",
		actions,
	}
})

const formatDate = (dateStr) => {
	if (!dateStr) return "—"
	return dayjs(dateStr).format("MMM D, YYYY")
}
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

/* Dialog footer: buttons in one row on the right — primary action right-most */
.dialog-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.kpi {
  padding: 10px 12px;
  border: 1px solid var(--outline-gray-1, #ededed);
  border-radius: 10px;
  background: var(--surface-cards, #fff);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  transition: border-color 0.15s, box-shadow 0.15s, background-color 0.15s;
}
.kpi.is-clickable {
  cursor: pointer;
}
.kpi.is-clickable:hover {
  border-color: var(--brand-border, #a6dcff);
}
.kpi.is-active {
  border-color: var(--brand, #29adff);
  background: var(--brand-soft, #e9f6ff);
  box-shadow: 0 0 0 1px var(--brand, #29adff) inset;
}
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
.status-pill.is-submitted { background: rgba(34, 197, 94, 0.12); color: #15803d; }
.status-pill.is-draft { background: rgba(245, 158, 11, 0.14); color: #b45309; }
.status-pill.is-cancelled { background: rgba(239, 68, 68, 0.12); color: #b91c1c; }
:global(.dark) .status-pill.is-submitted,
:global([data-theme="dark"]) .status-pill.is-submitted { color: #4ade80; }
:global(.dark) .status-pill.is-draft,
:global([data-theme="dark"]) .status-pill.is-draft { color: #fbbf24; }
:global(.dark) .status-pill.is-cancelled,
:global([data-theme="dark"]) .status-pill.is-cancelled { color: #f87171; }
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

:global([data-radix-popper-content-wrapper]), :global([data-reka-popper-content-wrapper]), :global(.PopoverContent) { z-index: 100005 !important; }
</style>