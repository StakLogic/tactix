<template>
  <div class="flex flex-col h-full overflow-hidden font-sans min-h-0">
    <!-- Top Stats / KPIs Header -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 p-1 flex-shrink-0">
      <Card class="!shadow-xs bg-white border border-slate-200/80 hover:border-slate-300 transition-all duration-150">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-slate-500">Total Hours logged</span>
          <IconClock class="w-4 h-4 text-blue-500" />
        </div>
        <div class="text-xl font-bold mt-1 text-slate-900 flex items-center h-7">
          <template v-if="timesheetsSummary.loading">
            <div class="w-4 h-4 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
          </template>
          <span v-else>{{ timesheetsSummary.data?.total_hours || 0 }} hrs</span>
        </div>
      </Card>

      <Card class="!shadow-xs bg-white border border-slate-200/80 hover:border-slate-300 transition-all duration-150">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-slate-500">Active Days Logged</span>
          <IconCalendar class="w-4 h-4 text-indigo-500" />
        </div>
        <div class="text-xl font-bold mt-1 text-slate-900 flex items-center h-7">
          <template v-if="timesheetsSummary.loading">
            <div class="w-4 h-4 border-2 border-slate-200 border-t-indigo-500 rounded-full animate-spin"></div>
          </template>
          <span v-else>{{ timesheetsSummary.data?.active_days || 0 }} days</span>
        </div>
      </Card>

      <Card class="!shadow-xs bg-white border border-slate-200/80 hover:border-slate-300 transition-all duration-150">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-slate-500">Submitted Timesheets</span>
          <IconCheckCircle class="w-4 h-4 text-green-500" />
        </div>
        <div class="text-xl font-bold mt-1 text-slate-900 flex items-center h-7">
          <template v-if="timesheetsSummary.loading">
            <div class="w-4 h-4 border-2 border-slate-200 border-t-green-500 rounded-full animate-spin"></div>
          </template>
          <span v-else>{{ timesheetsSummary.data?.submitted_count || 0 }}</span>
        </div>
      </Card>

      <Card class="!shadow-xs bg-white border border-slate-200/80 hover:border-slate-300 transition-all duration-150">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-slate-500">Draft Timesheets</span>
          <IconAlertCircle class="w-4 h-4 text-orange-500" />
        </div>
        <div class="text-xl font-bold mt-1 text-slate-900 flex items-center h-7">
          <template v-if="timesheetsSummary.loading">
            <div class="w-4 h-4 border-2 border-slate-200 border-t-orange-500 rounded-full animate-spin"></div>
          </template>
          <span v-else>{{ timesheetsSummary.data?.draft_count || 0 }}</span>
        </div>
      </Card>
    </div>

    <!-- Actions & Filter Header -->
    <div class="bg-white dark:bg-slate-900 p-3 rounded-lg border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col gap-2.5 mx-2 my-2 flex-shrink-0">
      <!-- Top Row: Search & Actions -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 w-full pb-2 border-b border-slate-100 dark:border-slate-800/80">

        <!-- Search Bar with Clear Icon -->
        <div class="relative w-full sm:w-80">
          <IconSearch class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 dark:text-slate-500" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search timesheets…"
            class="w-full pl-9 pr-8 py-1.5 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-md focus:bg-white dark:focus:bg-slate-900 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500"
          />
          <button
            v-if="searchQuery"
            @click="searchQuery = ''"
            class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-0.5 rounded-full border-none bg-transparent cursor-pointer"
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
                    ? 'border-blue-500 text-blue-600 bg-blue-50/50'
                    : '!text-slate-600 dark:!text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800'
                ]"
                @click="syncActiveFilterRules(); togglePopover()"
                title="Filter Timesheets"
              >
                <template #prefix><IconFilter class="w-3.5 h-3.5" :class="activeFilterCount > 0 ? 'text-blue-600' : 'text-slate-500'" /></template>
                <span>Filter</span>
                <span v-if="activeFilterCount > 0" class="bg-blue-600 text-white rounded-full text-[10px] font-bold px-1.5 py-0.2 leading-none">
                  {{ activeFilterCount }}
                </span>
              </Button>
            </template>
            <template #body-main="{ close }">
              <div class="w-80 p-3 bg-white dark:bg-slate-900 rounded-lg shadow-lg border border-slate-200 dark:border-slate-800 text-xs space-y-3">
                <div class="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
                  <div class="flex items-center gap-1.5 font-semibold text-slate-800 dark:text-slate-100 text-xs">
                    <IconFilter class="w-3.5 h-3.5 text-blue-600" />
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
                    class="flex items-center gap-1.5 bg-slate-50 dark:bg-slate-800 p-1.5 rounded-md border border-slate-200/80 dark:border-slate-700/80"
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
                      class="p-1 hover:bg-red-50 dark:hover:bg-red-950/40 rounded text-slate-400 hover:text-red-500 transition-colors shrink-0 cursor-pointer"
                      title="Remove Filter"
                    >
                      <IconX class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <div class="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800">
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

          <!-- Refresh Button -->
          <Button
            variant="outline"
            class="!text-slate-600 dark:!text-slate-200 !px-2.5 !h-8 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all rounded-md"
            @click="reloadTimesheets"
            title="Refresh timesheets"
          >
            <template #prefix><IconRefresh class="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" /></template>
          </Button>

          <!-- Actions Dropdown -->
          <Dropdown
            v-if="employeeInfoResource.data?.is_system_manager && selectedTimesheets.size > 0"
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

          <!-- New Timesheet Button -->
          <Button
            variant="solid"
            class="!text-xs !px-4 !h-8 rounded-md transition-all font-medium"
            style="background-color: var(--primary-color);"
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
                :class="[
                  'inline-flex items-center justify-between gap-2 outline-none text-xs rounded min-h-7 h-7 px-2 border transition-colors w-full cursor-pointer',
                  selectedStatus !== ''
                    ? 'border-blue-500 text-blue-600 bg-blue-50/50 font-medium dark:bg-blue-950/40 dark:text-blue-400'
                    : 'border-[--surface-gray-2] bg-surface-gray-2 hover:border-outline-gray-modals hover:bg-surface-gray-3 text-ink-gray-7 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-200'
                ]"
              >
                <span class="truncate">{{ getFilterLabel('selectedStatus', selectedStatus, 'Status') }}</span>
                <FeatherIcon name="chevron-down" class="size-4 text-ink-gray-4 ml-auto shrink-0" />
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
                :class="[
                  'inline-flex items-center justify-between gap-2 outline-none text-xs rounded min-h-7 h-7 px-2 border transition-colors w-full cursor-pointer',
                  selectedTimespan !== ''
                    ? 'border-blue-500 text-blue-600 bg-blue-50/50 font-medium dark:bg-blue-950/40 dark:text-blue-400'
                    : 'border-[--surface-gray-2] bg-surface-gray-2 hover:border-outline-gray-modals hover:bg-surface-gray-3 text-ink-gray-7 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-200'
                ]"
              >
                <span class="truncate">{{ getFilterLabel('selectedTimespan', selectedTimespan, 'Timespan') }}</span>
                <FeatherIcon name="chevron-down" class="size-4 text-ink-gray-4 ml-auto shrink-0" />
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
                :class="[
                  'inline-flex items-center justify-between gap-2 outline-none text-xs rounded min-h-7 h-7 px-2 border transition-colors w-full cursor-pointer',
                  selectedEmployee !== ''
                    ? 'border-blue-500 text-blue-600 bg-blue-50/50 font-medium dark:bg-blue-950/40 dark:text-blue-400'
                    : 'border-[--surface-gray-2] bg-surface-gray-2 hover:border-outline-gray-modals hover:bg-surface-gray-3 text-ink-gray-7 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-200'
                ]"
              >
                <span class="truncate">{{ getFilterLabel('selectedEmployee', selectedEmployee, 'Employee') }}</span>
                <FeatherIcon name="chevron-down" class="size-4 text-ink-gray-4 ml-auto shrink-0" />
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
    <div class="flex-1 overflow-y-auto md:overflow-hidden px-2 pb-4 flex flex-col min-h-0">
      <div class="bg-white rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex-col overflow-hidden min-h-[420px] md:min-h-0 md:flex-1 md:overflow-hidden flex">
        <ListView
          class="h-full flex flex-col min-h-0"
          :columns="columns"
          :rows="filteredTimesheets || []"
          :options="{
            selectable: employeeInfoResource.data?.is_system_manager,
            showTooltip: true,
            resizeColumn: true,
            onRowClick: (row) => openTimesheetDetails(row)
          }"
          row-key="name"
          v-model:selections="selectedTimesheets"
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
                v-for="row in (timesheets.data?.timesheets || [])"
                :key="row.name"
                :row="row"
              >
                <ListRowItem :item="item">
                  <template v-if="column.key === 'name'">
                    <span class="font-bold text-blue-600 font-medium">#{{ row.name }}</span>
                  </template>

                  <template v-if="column.key === 'start_date'">
                    <span class="text-xs text-slate-700 font-medium">
                      {{ row.start_date ? formatDate(row.start_date) : '' }}
                    </span>
                  </template>

                  <template v-if="column.key === 'total_hours'">
                    <Badge theme="blue" variant="subtle" class="font-semibold !px-2.5 !py-1 text-xs">
                      {{ row.total_hours }} hrs
                    </Badge>
                  </template>

                  <template v-if="column.key === 'status'">
                    <Badge
                      :theme="row.status === 'Submitted' ? 'green' : 'orange'"
                      variant="subtle"
                      class="font-semibold !px-2.5 !py-1 text-xs"
                    >
                      {{ row.status }}
                    </Badge>
                  </template>

                  <template v-if="column.key === 'actions'">
                    <div class="flex items-center justify-end space-x-1.5" v-if="employeeInfoResource.data?.is_system_manager">
                      <Button 
                        variant="ghost" 
                        class="!text-red-600 hover:!bg-red-50 !p-1.5 rounded-lg"
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

    <!-- Create Timesheet Dialog -->
    <Dialog v-model="showCreateDialog" :disable-outside-click-to-close="true" :options="dialogOptions">
      <template #body-content>
        <div class="space-y-6 py-2">
          <p v-if="formError" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-2.5 shadow-sm font-semibold flex items-center gap-2">
            <IconAlertCircle class="w-4 h-4 text-red-500 flex-shrink-0" /> {{ formError }}
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
            <!-- Date Picker -->
            <FormControl 
              type="date" 
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
                <label class="block text-xs text-slate-600 font-medium">Employee *</label>
                <div class="px-3 h-[2.25rem] bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 font-medium flex items-center gap-2">
                  <div class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
                  {{ employeeInfoResource.data?.employee_name || 'Loading profile...' }}
                </div>
              </div>
            </template>
          </div>

          <!-- Dynamic Time Logs Table -->
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <label class="text-xs font-black text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                <IconClock class="w-4 h-4 text-slate-400" /> Time Log Rows
              </label>
              <Button
                variant="outline"
                size="sm"
                class="!text-blue-600 hover:!bg-blue-50 !px-4 !h-8 font-semibold border-blue-200 hover:border-blue-300 rounded-lg transition-all"
                @click="addRow"
              >
                <template #prefix><IconPlus class="w-3.5 h-3.5" /></template> Add Task Row
              </Button>
            </div>

            <div class="border border-slate-200 rounded-xl overflow-x-auto shadow-sm max-h-[300px] overflow-y-auto custom-scrollbar">
              <table class="w-full text-left text-xs border-collapse">
                <thead class="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-semibold sticky top-0 z-10">
                  <tr>
                    <th class="px-4 py-3 w-1/3">Task</th>
                    <th class="px-4 py-3 w-1/4">Activity *</th>
                    <th class="px-4 py-3 w-24 text-right">Hours</th>
                    <th class="px-4 py-3">Description</th>
                    <th class="px-4 py-3 w-10 text-right"></th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 bg-white">
                  <tr v-for="(row, idx) in timesheetForm.time_logs" :key="idx" class="hover:bg-slate-50/20 transition-colors">
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
                            class="flex h-9 w-full items-center justify-between gap-1.5 rounded-lg bg-slate-50 hover:bg-slate-100/50 focus:bg-white border border-slate-200 hover:border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 px-2.5 py-1.5 text-xs font-medium text-slate-700 transition-all cursor-pointer"
                          >
                            <span class="truncate">{{ getTaskLabel(row.task) }}</span>
                            <FeatherIcon name="chevron-down" class="h-3.5 w-3.5 text-slate-400 shrink-0 ml-1" />
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
                            class="flex h-9 w-full items-center justify-between gap-1.5 rounded-lg bg-slate-50 hover:bg-slate-100/50 focus:bg-white border border-slate-200 hover:border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 px-2.5 py-1.5 text-xs font-medium text-slate-700 transition-all cursor-pointer"
                          >
                            <span class="truncate">{{ row.activity_type || 'Select Activity' }}</span>
                            <FeatherIcon name="chevron-down" class="h-3.5 w-3.5 text-slate-400 shrink-0 ml-1" />
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
                        class="w-full h-9 px-2.5 bg-slate-50 hover:bg-slate-100/50 focus:bg-white border border-slate-200 hover:border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 rounded-lg outline-none text-xs font-semibold text-slate-800 text-right transition-all" 
                      />
                    </td>
                    <td class="px-2 py-2">
                      <input 
                        v-model="row.description" 
                        placeholder="Provide details..." 
                        class="w-full h-9 px-3 bg-slate-50 hover:bg-slate-100/50 focus:bg-white border border-slate-200 hover:border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 rounded-lg outline-none text-xs text-slate-700 transition-all" 
                      />
                    </td>
                    <td class="px-2 py-2 text-right">
                      <button 
                        class="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                        @click="removeRow(idx)"
                      >
                        <IconX class="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                  <tr v-if="timesheetForm.time_logs.length === 0">
                    <td colspan="6" class="px-4 py-8 text-center text-slate-400 italic font-semibold">
                      No rows added yet. Add a row to get started.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="flex items-center justify-between p-3.5 bg-blue-50/50 rounded-xl border border-blue-100/50 text-xs font-bold">
              <span class="text-blue-700 uppercase tracking-wider font-extrabold">Total Logged Hours</span>
              <span class="text-sm font-black text-blue-800 bg-blue-100/50 px-3.5 py-1 rounded-lg">{{ computedTotalHours }} hrs</span>
            </div>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- View Timesheet Details Dialog -->
    <Dialog v-model="showViewDialog" :disable-outside-click-to-close="true" :options="viewDialogOptions">
      <template #body-content>
        <div class="space-y-6 py-2" v-if="selectedTimesheet">
          <p v-if="viewError" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-2.5 shadow-sm font-semibold flex items-center gap-2">
            <IconAlertCircle class="w-4 h-4 text-red-500 flex-shrink-0" /> {{ viewError }}
          </p>
          <!-- Summary Cards Row -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
            <!-- Date Card -->
            <div class="bg-blue-50/40 border border-blue-100 rounded-xl p-2 flex flex-col justify-between shadow-sm">
              <div class="flex items-center justify-between mb-2">
                <span class="text-[10px] font-semibold text-blue-600 uppercase tracking-wider">Date</span>
                <div class="p-1.5 rounded-lg bg-blue-100/50">
                  <IconCalendar class="w-3.5 h-3.5 text-blue-600" />
                </div>
              </div>
              <div class="text-lg font-black text-blue-800 leading-none">
                {{ formatDate(selectedTimesheet.start_date) }}
              </div>
            </div>

            <!-- Employee Card -->
            <div class="bg-indigo-50/40 border border-indigo-100 rounded-xl p-2 flex flex-col justify-between shadow-sm">
              <div class="flex items-center justify-between mb-2">
                <span class="text-[10px] font-semibold text-indigo-600 uppercase tracking-wider">Employee</span>
                <div class="p-1.5 rounded-lg bg-indigo-100/50">
                  <IconUser class="w-3.5 h-3.5 text-indigo-600" />
                </div>
              </div>
              <div class="text-sm font-black text-indigo-800 truncate leading-none">
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
                {{ selectedTimesheet.total_hours }} hrs
              </div>
            </div>
          </div>

          <!-- Time Logs Details Table -->
          <div class="border border-slate-200 rounded-xl overflow-x-auto shadow-sm">
            <table class="w-full text-left text-xs border-collapse">
              <thead class="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-semibold">
                <tr>
                  <th class="px-4 py-3.5">Task</th>
                  <th class="px-4 py-3.5">Activity</th>
                  <th class="px-4 py-3.5 text-right w-24">Hours</th>
                  <th class="px-4 py-3.5">Description</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 bg-white">
                <tr v-for="(log, idx) in selectedTimesheet.time_logs" :key="idx" class="hover:bg-slate-50/40 transition-colors duration-150">
                  <td class="px-4 py-3.5 font-bold text-slate-800">
                    {{ log.task ? (log.task_subject ? `${log.task_subject} (${log.task})` : log.task) : '—' }}
                  </td>
                  <td class="px-4 py-3.5">
                    <Badge theme="gray" variant="subtle" class="!px-2.5 !py-1 text-[11px] font-semibold">{{ log.activity_type }}</Badge>
                  </td>
                  <td class="px-4 py-3.5 text-right font-black text-slate-700">{{ log.hours }} hrs</td>
                  <td class="px-4 py-3.5 text-slate-500 whitespace-pre-wrap leading-relaxed">{{ log.description || '—' }}</td>

                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model="deleteConfirm.show" 
      :disable-outside-click-to-close="true"
      :options="{
        title: deleteConfirm.isBulk ? 'Delete Selected Timesheets' : 'Delete Timesheet',
        size: 'sm',
        actions: [
          { label: 'Delete', variant: 'solid', theme: 'red', loading: deleteConfirm.loading, onClick: executeTimesheetDelete },
          { label: 'Cancel', variant: 'ghost', onClick: () => (deleteConfirm.show = false) }
        ]
      }"
    >
      <template #body-content>
        <p class="text-sm text-slate-600 leading-relaxed py-2">
          <span v-if="deleteConfirm.isBulk">
            This will permanently remove <span class="font-bold text-slate-900">{{ deleteConfirm.count }}</span> selected timesheet(s). This action cannot be undone.
          </span>
          <span v-else>
            This will permanently remove timesheet <span class="font-bold text-slate-900">#{{ deleteConfirm.targetName }}</span>. This action cannot be undone.
          </span>
        </p>
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
import { computed, onMounted, reactive, ref, watch } from "vue"

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
	if (employeeOptionsResource.data && Array.isArray(employeeOptionsResource.data)) {
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
		fields.push({ label: "Employee", value: "selectedEmployee", key: "selectedEmployee" })
	}
	return fields
})

const activeFilterRules = ref([])

function syncActiveFilterRules() {
	const newRules = []
	if (selectedStatus.value) {
		newRules.push({ id: "rule_selectedStatus", field: "selectedStatus", value: selectedStatus.value })
	}
	if (selectedTimespan.value) {
		newRules.push({ id: "rule_selectedTimespan", field: "selectedTimespan", value: selectedTimespan.value })
	}
	if (selectedEmployee.value && employeeInfoResource.data?.is_system_manager) {
		newRules.push({ id: "rule_selectedEmployee", field: "selectedEmployee", value: selectedEmployee.value })
	}
	if (newRules.length === 0) {
		newRules.push({ id: "rule_" + Date.now(), field: "selectedStatus", value: "" })
	}
	activeFilterRules.value = newRules
}

function addFilterRule() {
	const unusedField = FILTERABLE_FIELDS.value.find(
		(f) => !activeFilterRules.value.some((r) => r.field === f.value)
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
	if (fieldKey === "selectedStatus") return statusOptions.filter((o) => o.value !== "")
	if (fieldKey === "selectedTimespan") return timespanOptions.filter((o) => o.value !== "")
	if (fieldKey === "selectedEmployee") return employeeOptions.value.filter((o) => o.value !== "")
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
})

const actionsOptions = computed(() => [
	{
		label: `Delete Selected (${selectedTimesheets.value.size})`,
		icon: "trash-2",
		onClick: confirmBulkDelete,
	},
])

function confirmSingleDelete(name) {
	deleteConfirm.isBulk = false
	deleteConfirm.targetName = name
	deleteConfirm.count = 1
	deleteConfirm.show = true
}

function confirmBulkDelete() {
	deleteConfirm.isBulk = true
	deleteConfirm.targetName = null
	deleteConfirm.count = selectedTimesheets.value.size
	deleteConfirm.show = true
}

async function executeTimesheetDelete() {
	deleteConfirm.loading = true
	try {
		if (deleteConfirm.isBulk) {
			for (const name of Array.from(selectedTimesheets.value)) {
				await createResource({
					url: "frappe.client.delete",
					params: { doctype: "Timesheet", name },
				}).submit()
			}
			selectedTimesheets.value.clear()
		} else if (deleteConfirm.targetName) {
			await createResource({
				url: "frappe.client.delete",
				params: { doctype: "Timesheet", name: deleteConfirm.targetName },
			}).submit()
			selectedTimesheets.value.delete(deleteConfirm.targetName)
		}
		deleteConfirm.show = false
		timesheets.reload()
		timesheetsSummary.reload()
	} catch (err) {
		console.error("Error deleting timesheet(s):", err)
		alert("Failed to delete timesheet(s).")
	} finally {
		deleteConfirm.loading = false
	}
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
	date: new Date().toISOString().split("T")[0],
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
	...(employeeInfoResource.data?.is_system_manager ? [{ label: "Actions", key: "actions", width: "100px" }] : []),
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

// Initial fetch
onMounted(() => {
	reloadTimesheets()
})

// Watch filters
watch(
	timesheetFilters,
	() => {
		currentPage.value = 1
		fetchTimesheets()
		fetchSummary()
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
	timesheetForm.date = new Date().toISOString().split("T")[0]
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
			loading: saving.value,
			onClick: () => saveTimesheet(true),
		})
	}

	actions.push({
		label: isEditMode.value ? "Save Draft" : "Save as Draft",
		variant: hasSubmitPermission ? "outline" : "solid",
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
				theme: "green",
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