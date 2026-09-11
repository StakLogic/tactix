<template>
  <div class="space-y-4 p-1 flex flex-col h-full overflow-hidden min-h-0 bg-slate-50 dark:bg-slate-900 transition-colors duration-300">
    
    <!-- Header Page Title -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-3 flex-shrink-0">
      <div>
        <h1 class="text-xl font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
          <IconGitPullRequest class="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
          Contributions
        </h1>
        <p class="text-xs text-slate-400 dark:text-slate-500">
          Monitor recent Pull Requests and engineering activity across Organization.
        </p>
      </div>
      
      <div class="flex items-center gap-3">
        <!-- Simulation Button -->
        <!-- <Button 
          variant="solid" 
          class="!bg-indigo-600 hover:!bg-indigo-700 !text-white !text-xs !h-9 !px-4 !shadow-sm" 
          @click="simulatePRRaised"
          :disabled="simulating"
        >
          <template #prefix>
            <IconGitPullRequest class="w-4 h-4 mr-1" />
          </template>
          Test PR Raised Notification
        </Button> -->

        <Button 
          variant="outline" 
          class="!text-slate-600 !px-3 !h-9 border border-slate-200 hover:bg-slate-50 transition-all dark:!text-slate-300 dark:border-slate-700" 
          @click="fetchPullRequests"
          :disabled="loading"
        >
          <template #prefix>
            <IconRefresh :class="['w-4 h-4', loading ? 'animate-spin' : '']" />
          </template>
        </Button>
      </div>
    </div>

    <!-- Stats Breakdown Overview Grid -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 flex-shrink-0">
      <Card 
        v-for="stat in statsBreakdown" 
        :key="stat.label" 
        :class="[
          '!shadow-xs bg-white dark:bg-slate-800 cursor-pointer transition-all duration-150 border active:scale-[0.98]',
          'border-slate-200/80 hover:border-slate-300 dark:hover:border-slate-700'
        ]"
        @click="filterByStat(stat.label)"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-slate-500">{{ stat.label }}</span>
          <component :is="stat.icon" class="w-4 h-4" :class="stat.color" />
        </div>
        <div class="text-xl font-bold mt-1 text-slate-900 dark:text-white flex items-center h-7">
          <template v-if="loading">
            <div class="w-4 h-4 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
          </template>
          <span v-else>{{ stat.value }}</span>
        </div>
      </Card>
    </div>

    <!-- Actions & Filter Header -->
    <div class="bg-white dark:bg-slate-800 p-3 rounded-lg border border-slate-200 dark:border-slate-700 shadow-xs flex flex-col gap-2.5 flex-shrink-0">
      <!-- Top Row: Search & Actions -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 w-full pb-2 border-b border-slate-100 dark:border-slate-700/80">

        <!-- Search input -->
        <div class="relative w-full sm:w-80">
          <IconSearch class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 dark:text-slate-500" />
          <input
            v-model="filters.search"
            type="text"
            placeholder="Search PR title, number or author…"
            class="w-full pl-9 pr-8 py-1.5 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-md focus:bg-white dark:focus:bg-slate-900 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500"
          />
          <button
            v-if="filters.search"
            @click="filters.search = ''"
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
                    : '!text-slate-600 dark:!text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
                ]"
                @click="syncActiveFilterRules(); togglePopover()"
                title="Filter Contributions"
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
                    <span>Filter Contributions</span>
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
            class="!text-slate-600 dark:!text-slate-300 !px-2.5 !h-8 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 transition-all rounded-md"
            @click="fetchPullRequests"
            :disabled="loading"
            title="Refresh contributions"
          >
            <template #prefix><IconRefresh class="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" :class="{ 'animate-spin': loading }" /></template>
          </Button>
        </div>
      </div>

      <!-- Bottom Row: Quick Filter Bar -->
      <div class="filter-row flex flex-nowrap overflow-x-auto pb-1 gap-2 w-full custom-scrollbar sm:flex-wrap sm:overflow-visible sm:pb-0 sm:items-center sm:gap-2">
        <!-- Repository Autocomplete Filter -->
        <div class="w-48 shrink-0">
          <Autocomplete
            ref="repoAutocomplete"
            :options="repoOptions"
            :modelValue="filters.repo"
            @update:modelValue="val => filters.repo = (val && typeof val === 'object') ? (val.value ?? '') : (val ?? '')"
            :max-options="100"
          >
            <template #target>
              <button
                type="button"
                @click="() => repoAutocomplete?.togglePopover()"
                :class="[
                  'inline-flex items-center justify-between gap-2 outline-none text-xs rounded min-h-7 h-7 px-2 border transition-colors w-full cursor-pointer',
                  filters.repo !== ''
                    ? 'border-blue-500 text-blue-600 bg-blue-50/50 font-medium dark:bg-blue-950/40 dark:text-blue-400'
                    : 'border-[--surface-gray-2] bg-surface-gray-2 hover:border-outline-gray-modals hover:bg-surface-gray-3 text-ink-gray-7 dark:bg-slate-900 dark:border-slate-700 dark:text-slate-200'
                ]"
              >
                <span class="truncate">{{ getFilterLabel('repo', filters.repo, 'Repository') }}</span>
                <FeatherIcon name="chevron-down" class="size-4 text-ink-gray-4 ml-auto shrink-0" />
              </button>
            </template>
          </Autocomplete>
        </div>

        <!-- Status Autocomplete Filter -->
        <div class="w-40 shrink-0">
          <Autocomplete
            ref="statusAutocomplete"
            :options="statusOptions"
            :modelValue="filters.status"
            @update:modelValue="val => filters.status = (val && typeof val === 'object') ? (val.value ?? 'all') : (val ?? 'all')"
          >
            <template #target>
              <button
                type="button"
                @click="() => statusAutocomplete?.togglePopover()"
                :class="[
                  'inline-flex items-center justify-between gap-2 outline-none text-xs rounded min-h-7 h-7 px-2 border transition-colors w-full cursor-pointer',
                  filters.status !== 'all'
                    ? 'border-blue-500 text-blue-600 bg-blue-50/50 font-medium dark:bg-blue-950/40 dark:text-blue-400'
                    : 'border-[--surface-gray-2] bg-surface-gray-2 hover:border-outline-gray-modals hover:bg-surface-gray-3 text-ink-gray-7 dark:bg-slate-900 dark:border-slate-700 dark:text-slate-200'
                ]"
              >
                <span class="truncate">{{ getFilterLabel('status', filters.status, 'Status') }}</span>
                <FeatherIcon name="chevron-down" class="size-4 text-ink-gray-4 ml-auto shrink-0" />
              </button>
            </template>
          </Autocomplete>
        </div>

        <!-- Author Autocomplete Filter -->
        <div class="w-40 shrink-0">
          <Autocomplete
            ref="authorAutocomplete"
            :options="authorOptions"
            :modelValue="filters.author"
            @update:modelValue="val => filters.author = (val && typeof val === 'object') ? (val.value ?? '') : (val ?? '')"
            :max-options="100"
          >
            <template #target>
              <button
                type="button"
                @click="() => authorAutocomplete?.togglePopover()"
                :class="[
                  'inline-flex items-center justify-between gap-2 outline-none text-xs rounded min-h-7 h-7 px-2 border transition-colors w-full cursor-pointer',
                  filters.author !== ''
                    ? 'border-blue-500 text-blue-600 bg-blue-50/50 font-medium dark:bg-blue-950/40 dark:text-blue-400'
                    : 'border-[--surface-gray-2] bg-surface-gray-2 hover:border-outline-gray-modals hover:bg-surface-gray-3 text-ink-gray-7 dark:bg-slate-900 dark:border-slate-700 dark:text-slate-200'
                ]"
              >
                <span class="truncate">{{ getFilterLabel('author', filters.author, 'Author') }}</span>
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
          @click="clearFilters"
        >
          <template #prefix><IconX class="w-3.5 h-3.5" /></template>
          Clear
        </Button>
      </div>
    </div>

    <!-- Tabs Switcher -->
    <div class="inline-flex p-1 bg-slate-100 dark:bg-slate-900 rounded-xl border border-slate-200/60 dark:border-slate-800/80 flex-shrink-0 self-start">
      <button 
        @click="activeTab = 'list'"
        :class="[
          'px-4 py-1.5 text-xs font-bold rounded-lg transition-all cursor-pointer outline-none focus:outline-none flex items-center gap-1.5',
          activeTab === 'list' 
            ? '!text-white shadow-sm' 
            : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'
        ]"
        :style="activeTab === 'list' ? { backgroundColor: 'var(--primary-color)' } : {}"
      >
        <IconGitPullRequest class="w-3.5 h-3.5" />
        All Pull Requests
      </button>
      <button 
        @click="activeTab = 'dashboard'"
        :class="[
          'px-4 py-1.5 text-xs font-bold rounded-lg transition-all cursor-pointer outline-none focus:outline-none flex items-center gap-1.5',
          activeTab === 'dashboard' 
            ? '!text-white shadow-sm' 
            : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'
        ]"
        :style="activeTab === 'dashboard' ? { backgroundColor: 'var(--primary-color)' } : {}"
      >
        <IconClock class="w-3.5 h-3.5" />
        Analytics Dashboard
      </button>
    </div>

    <!-- Main List Container (Pull Request ListView) -->
    <div v-if="activeTab === 'list'" class="flex-1 overflow-y-auto md:overflow-hidden flex flex-col min-h-0 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 shadow-sm min-h-[420px] md:min-h-0">
      <div v-if="loading && filteredPRs.length === 0" class="flex justify-center p-12 flex-1 items-center">
        <div class="w-6 h-6 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
      </div>

      <div v-else-if="filteredPRs.length === 0" class="text-center py-16 flex-1 flex flex-col items-center justify-center space-y-4">
        <div class="p-3 bg-indigo-50 dark:bg-indigo-950/40 rounded-2xl">
          <IconGitPullRequest class="w-10 h-10 text-indigo-600 dark:text-indigo-400" />
        </div>
        <div class="max-w-xs space-y-1">
          <h3 class="text-sm font-bold text-slate-800 dark:text-white">No Pull Requests Found</h3>
          <p class="text-slate-400 text-xs leading-relaxed">
            We couldn't find any pull requests matching your active filters.
          </p>
        </div>
      </div>

      <ListView
        v-else
        class="h-full flex flex-col min-h-0"
        :columns="columns"
        :rows="filteredPRs"
        row-key="id"
        :options="{ showTooltip: true, resizeColumn: true, selectable: false }"
      >
        <ListHeader class="shrink-0 bg-slate-50 border-b border-slate-200 dark:bg-slate-900 dark:border-slate-700">
          <ListHeaderItem v-for="col in columns" :key="col.key" :item="col" class="font-bold text-slate-500 text-xs">
            <template #prefix="{ item }">
              <component :is="item.icon" class="size-3.5 text-slate-400" />
            </template>
          </ListHeaderItem>
        </ListHeader>
        
        <div class="flex-grow md:flex-1 overflow-y-auto custom-scrollbar relative min-h-0 max-h-[480px] md:max-h-none divide-y divide-slate-100 dark:divide-slate-700 bg-white dark:bg-slate-800">
          <ListRows>
            <ListRow v-for="row in filteredPRs" :key="row.id" v-slot="{ column, item }" :row="row" class="cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700/50" @click="openOnGitHub(row.html_url)">
              <ListRowItem :item="item">
                
                <!-- PR Title column with User Avatar and opened metadata -->
                <template v-if="column.key === 'title'">
                  <div class="flex items-center gap-3 select-none min-w-0 overflow-hidden">
                    <Avatar :image="row.user.avatar_url" :label="row.user.login" size="md" class="ring-1 ring-slate-100 flex-shrink-0" />
                    <div class="truncate min-w-0 flex-1">
                      <div class="font-bold text-sm text-slate-800 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400 truncate">
                        {{ row.title }}
                        <span class="text-xs text-slate-400 font-mono ml-1">#{{ row.number }}</span>
                      </div>
                      <div class="text-[10px] text-slate-400 mt-0.5">
                        opened {{ timeAgo(row.created_at) }}
                      </div>
                    </div>
                  </div>
                </template>
                
                <!-- Repository name -->
                <template v-if="column.key === 'repo'">
                  <span 
                    class="text-xs font-bold text-indigo-600 hover:underline dark:text-indigo-400 truncate block max-w-full cursor-pointer"
                    @click.stop="openOnGitHub(getRepoHomeUrl(row.repository_url))"
                  >
                    {{ formatRepoName(row.repository_url) }}
                  </span>
                </template>
                
                <!-- Author -->
                <template v-if="column.key === 'user'">
                  <span 
                    class="text-xs font-bold text-indigo-600 hover:underline dark:text-indigo-400 truncate block max-w-full cursor-pointer"
                    @click.stop="openOnGitHub('https://github.com/' + row.user.login)"
                  >
                    {{ row.user.login }}
                  </span>
                </template>
                
                <!-- Status Badge -->
                <template v-if="column.key === 'state'">
                  <Badge 
                    v-if="getPRStatusLabel(row) === 'Merged'"
                    variant="subtle" 
                    size="sm" 
                    class="font-black uppercase text-[9px] px-2.5 py-1 tracking-wide border flex-shrink-0"
                    :style="{
                      backgroundColor: '#8250df15',
                      color: '#8250df',
                      borderColor: '#8250df35'
                    }"
                  >
                    Merged
                  </Badge>
                  <Badge 
                    v-else
                    variant="subtle" 
                    :theme="getPRStatusTheme(row)" 
                    size="sm" 
                    class="font-black uppercase text-[9px] px-2.5 py-1 tracking-wide flex-shrink-0"
                  >
                    {{ getPRStatusLabel(row) }}
                  </Badge>
                </template>
                
                <!-- Comments Column -->
                <template v-if="column.key === 'comments'">
                  <div class="flex justify-end pr-2">
                    <div 
                      v-if="row.comments > 0" 
                      class="flex items-center gap-1 text-slate-400 hover:text-slate-600 text-xs"
                      title="Comments"
                    >
                      <IconMessageSquare class="w-3.5 h-3.5" />
                      <span class="text-[10px] font-bold leading-none">
                        {{ row.comments }}
                      </span>
                    </div>
                  </div>
                </template>

              </ListRowItem>
            </ListRow>
          </ListRows>
        </div>
      </ListView>
      
      <!-- Pagination Bar -->
      <div class="flex items-center justify-between border-t border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2 shrink-0">
        <div class="flex items-center gap-1">
          <!-- First Page (<<) -->
          <Button
            variant="ghost"
            size="sm"
            :disabled="currentPage === 1"
            @click="currentPage = 1"
            title="First Page"
            class="!p-1 !h-6 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 disabled:opacity-30"
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
            class="!p-1 !h-6 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 disabled:opacity-30"
          >
            <template #prefix><IconChevronLeft class="w-3.5 h-3.5" /></template>
          </Button>

          <!-- Compact Popover Page Selector -->
          <Popover>
            <template #target="{ togglePopover }">
              <button
                @click="togglePopover"
                class="h-6 px-2 text-[11px] font-bold text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 rounded border border-slate-200/80 dark:border-slate-700 transition-all flex items-center gap-1 cursor-pointer shrink-0"
              >
                <span>{{ currentPage }} / {{ totalPages }}</span>
                <IconChevronDown class="w-3 h-3 text-slate-400" />
              </button>
            </template>
            <template #body="{ close }">
              <div class="p-1 max-h-48 overflow-y-auto w-32 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 custom-scrollbar">
                <button
                  v-for="p in totalPages"
                  :key="p"
                  @click="currentPage = p; close()"
                  :class="[
                    'w-full text-left px-2 py-1 text-xs rounded transition-colors cursor-pointer flex items-center justify-between',
                    currentPage === p
                      ? 'bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 font-bold'
                      : 'text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700'
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
            class="!p-1 !h-6 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 disabled:opacity-30"
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
            class="!p-1 !h-6 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 disabled:opacity-30"
          >
            <template #prefix><IconChevronsRight class="w-3.5 h-3.5" /></template>
          </Button>
        </div>

        <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">
          Showing <span class="font-bold text-slate-800 dark:text-slate-200">{{ totalCount > 0 ? (currentPage - 1) * pageLength + 1 : 0 }} - {{ Math.min(currentPage * pageLength, totalCount) }}</span> of <span class="font-bold text-slate-800 dark:text-slate-200">{{ totalCount }}</span>
        </div>
      </div>
    </div>

    <!-- Analytics Dashboard Tab Container -->
    <div v-else-if="activeTab === 'dashboard'" class="flex-1 overflow-y-auto custom-scrollbar min-h-0 space-y-6">
      <div v-if="loading && authorStats.length === 0" class="flex justify-center p-12 flex-1 items-center bg-white dark:bg-slate-800 rounded-xl border border-slate-200 shadow-sm">
        <div class="w-6 h-6 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
      </div>
      
      <div v-else-if="authorStats.length === 0" class="text-center py-16 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 shadow-sm flex flex-col items-center justify-center space-y-4">
        <div class="p-3 bg-indigo-50 dark:bg-indigo-950/40 rounded-2xl">
          <IconGitPullRequest class="w-10 h-10 text-indigo-600 dark:text-indigo-400" />
        </div>
        <div class="max-w-xs space-y-1">
          <h3 class="text-sm font-bold text-slate-800 dark:text-white">No Data Available</h3>
          <p class="text-slate-400 text-xs leading-relaxed">
            No pull request activity is registered matching your active filters.
          </p>
        </div>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-0">
        
        <!-- Left: Leaderboard & Author Rankings (7 cols on lg) -->
        <div class="lg:col-span-7 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700/80 shadow-sm overflow-hidden flex flex-col min-h-[450px]">
          <div class="p-4 border-b border-slate-100 dark:border-slate-700/60 bg-slate-50/50 dark:bg-slate-900/10 flex justify-between items-center">
            <div>
              <h3 class="text-sm font-black text-slate-800 dark:text-white uppercase tracking-wider">Top Contributors</h3>
              <p class="text-[10px] text-slate-400 dark:text-slate-500 font-medium">Ranked by volume of pull requests submitted</p>
            </div>
            <span class="text-xs font-mono font-bold bg-indigo-50 dark:bg-indigo-950/30 text-indigo-600 dark:text-indigo-400 px-2 py-0.5 rounded-lg border border-indigo-100/50 dark:border-indigo-900/30">
              {{ authorStats.length }} Authors
            </span>
          </div>

          <div class="p-5 divide-y divide-slate-100 dark:divide-slate-700/50 overflow-y-auto flex-1 custom-scrollbar">
            <div 
              v-for="(author, idx) in authorStats" 
              :key="author.username" 
              class="py-4 first:pt-0 last:pb-0 flex items-center justify-between gap-4 group transition-all"
            >
              <!-- Left Rank + Avatar + Name -->
              <div class="flex items-center gap-3.5 min-w-0 flex-1">
                <!-- Rank Badge -->
                <div class="flex-shrink-0 w-7 h-7 rounded-xl flex items-center justify-center text-xs font-black shadow-sm"
                  :class="[
                    idx === 0 ? 'bg-amber-100 text-amber-800 ring-2 ring-amber-300 dark:bg-amber-950/40 dark:text-amber-300 dark:ring-amber-900/40' : '',
                    idx === 1 ? 'bg-slate-100 text-slate-800 ring-2 ring-slate-300 dark:bg-slate-900/50 dark:text-slate-300 dark:ring-slate-800' : '',
                    idx === 2 ? 'bg-amber-50 text-amber-900 ring-2 ring-amber-200 dark:bg-amber-950/10 dark:text-amber-400 dark:ring-amber-900/20' : '',
                    idx > 2 ? 'bg-slate-50 border border-slate-200 text-slate-500 dark:bg-slate-900/60 dark:border-slate-700 dark:text-slate-400' : ''
                  ]"
                >
                  <span v-if="idx === 0">🏆</span>
                  <span v-else-if="idx === 1">🥈</span>
                  <span v-else-if="idx === 2">🥉</span>
                  <span v-else>{{ idx + 1 }}</span>
                </div>

                <Avatar 
                  :image="author.avatar_url" 
                  :label="author.username" 
                  size="lg" 
                  class="ring-2 ring-slate-100/50 dark:ring-slate-700/30 flex-shrink-0 cursor-pointer hover:opacity-90 transition-opacity" 
                  @click="openOnGitHub('https://github.com/' + author.username)"
                />
                
                <div class="min-w-0 flex-1">
                  <div 
                    class="font-bold text-sm text-slate-800 dark:text-white truncate hover:text-indigo-600 dark:hover:text-indigo-400 hover:underline cursor-pointer transition-colors"
                    @click="openOnGitHub('https://github.com/' + author.username)"
                  >
                    {{ author.username }}
                  </div>
                  <div class="text-[10px] text-slate-400 mt-1 flex items-center gap-2 flex-wrap">
                    <span class="flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-purple-500"></span>{{ author.merged }} merged</span>
                    <span>•</span>
                    <span class="flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-green-500"></span>{{ author.open }} open</span>
                    <span v-if="author.draft > 0">•</span>
                    <span v-if="author.draft > 0" class="flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span>{{ author.draft }} drafts</span>
                  </div>
                </div>
              </div>

              <!-- Right Visual Ratio Progress Bar -->
              <div class="flex flex-col items-end gap-1.5 w-1/3 min-w-[120px] max-w-[180px]">
                <div class="text-xs font-black text-slate-800 dark:text-white">
                  {{ author.total }} PR{{ author.total > 1 ? 's' : '' }}
                </div>
                <!-- Stacked Progress Bar Ratio -->
                <div class="h-2 w-full rounded-full bg-slate-100 dark:bg-slate-900 overflow-hidden flex relative shadow-inner">
                  <div 
                    :style="{ width: `${(author.merged / author.total) * 100}%` }"
                    class="bg-[#8250df] h-full transition-all duration-500" 
                    title="Merged"
                  />
                  <div 
                    :style="{ width: `${(author.open / author.total) * 100}%` }"
                    class="bg-green-500 h-full transition-all duration-500" 
                    title="Open"
                  />
                  <div 
                    :style="{ width: `${(author.draft / author.total) * 100}%` }"
                    class="bg-slate-400 h-full transition-all duration-500" 
                    title="Draft"
                  />
                  <div 
                    :style="{ width: `${(author.closed / author.total) * 100}%` }"
                    class="bg-red-500 h-full transition-all duration-500" 
                    title="Closed"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: SVG Donut Chart + Repo Splits (5 cols on lg) -->
        <div class="lg:col-span-5 space-y-6 flex flex-col min-h-0">
          
          <!-- Card 2: Interactive SVG Donut Status Chart -->
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700/80 shadow-sm p-5 flex flex-col items-center justify-center">
            <h3 class="text-sm font-black text-slate-800 dark:text-white uppercase tracking-wider w-full mb-4 text-left">
              Status Allocation
            </h3>
            
            <div class="flex items-center justify-between w-full gap-6">
              <!-- SVG Donut Chart -->
              <div class="relative w-36 h-36 flex-shrink-0 flex items-center justify-center">
                <svg class="w-full h-full transform -rotate-90" viewBox="0 0 42 42">
                  <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#f1f5f9" stroke-width="4.5" class="dark:stroke-slate-900"/>
                  
                  <!-- Merged Section (purple) -->
                  <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#8250df" stroke-width="4.5" 
                    :stroke-dasharray="`${(overallDashboardTotals.merged / Math.max(1, overallDashboardTotals.total)) * 100} ${100 - ((overallDashboardTotals.merged / Math.max(1, overallDashboardTotals.total)) * 100)}`"
                    stroke-dashoffset="0"
                    class="transition-all duration-1000 ease-out"
                  />
                  
                  <!-- Open Section (green) -->
                  <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#22c55e" stroke-width="4.5" 
                    :stroke-dasharray="`${(overallDashboardTotals.open / Math.max(1, overallDashboardTotals.total)) * 100} ${100 - ((overallDashboardTotals.open / Math.max(1, overallDashboardTotals.total)) * 100)}`"
                    :stroke-dashoffset="`${-((overallDashboardTotals.merged / Math.max(1, overallDashboardTotals.total)) * 100)}`"
                    class="transition-all duration-1000 ease-out"
                  />
                  
                  <!-- Draft Section (slate) -->
                  <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#94a3b8" stroke-width="4.5" 
                    :stroke-dasharray="`${(overallDashboardTotals.draft / Math.max(1, overallDashboardTotals.total)) * 100} ${100 - ((overallDashboardTotals.draft / Math.max(1, overallDashboardTotals.total)) * 100)}`"
                    :stroke-dashoffset="`${-(((overallDashboardTotals.merged + overallDashboardTotals.open) / Math.max(1, overallDashboardTotals.total)) * 100)}`"
                    class="transition-all duration-1000 ease-out"
                  />
                  
                  <!-- Closed Section (red) -->
                  <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#ef4444" stroke-width="4.5" 
                    :stroke-dasharray="`${(overallDashboardTotals.closed / Math.max(1, overallDashboardTotals.total)) * 100} ${100 - ((overallDashboardTotals.closed / Math.max(1, overallDashboardTotals.total)) * 100)}`"
                    :stroke-dashoffset="`${-(((overallDashboardTotals.merged + overallDashboardTotals.open + overallDashboardTotals.draft) / Math.max(1, overallDashboardTotals.total)) * 100)}`"
                    class="transition-all duration-1000 ease-out"
                  />
                </svg>
                
                <!-- Inner text displaying total PR count -->
                <div class="absolute flex flex-col items-center justify-center text-center">
                  <span class="text-2xl font-black text-slate-800 dark:text-white leading-none">
                    {{ overallDashboardTotals.total }}
                  </span>
                  <span class="text-[9px] text-slate-400 uppercase tracking-widest font-bold mt-1">Total PRs</span>
                </div>
              </div>

              <!-- Legends list -->
              <div class="flex-1 space-y-2.5">
                <div class="flex items-center justify-between text-xs">
                  <div class="flex items-center gap-2 font-bold text-slate-600 dark:text-slate-300">
                    <span class="w-2.5 h-2.5 rounded-md bg-[#8250df]"></span>
                    <span>Merged</span>
                  </div>
                  <span class="font-mono font-black text-slate-800 dark:text-white">
                    {{ overallDashboardTotals.merged }}
                  </span>
                </div>
                <div class="flex items-center justify-between text-xs">
                  <div class="flex items-center gap-2 font-bold text-slate-600 dark:text-slate-300">
                    <span class="w-2.5 h-2.5 rounded-md bg-green-500"></span>
                    <span>Open</span>
                  </div>
                  <span class="font-mono font-black text-slate-800 dark:text-white">
                    {{ overallDashboardTotals.open }}
                  </span>
                </div>
                <div class="flex items-center justify-between text-xs">
                  <div class="flex items-center gap-2 font-bold text-slate-600 dark:text-slate-300">
                    <span class="w-2.5 h-2.5 rounded-md bg-slate-400"></span>
                    <span>Draft</span>
                  </div>
                  <span class="font-mono font-black text-slate-800 dark:text-white">
                    {{ overallDashboardTotals.draft }}
                  </span>
                </div>
                <div class="flex items-center justify-between text-xs">
                  <div class="flex items-center gap-2 font-bold text-slate-600 dark:text-slate-300">
                    <span class="w-2.5 h-2.5 rounded-md bg-red-500"></span>
                    <span>Closed</span>
                  </div>
                  <span class="font-mono font-black text-slate-800 dark:text-white">
                    {{ overallDashboardTotals.closed }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Card 3: Repository Share Distribution Graph -->
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700/80 shadow-sm p-5 flex flex-col flex-1 overflow-hidden">
            <h3 class="text-sm font-black text-slate-800 dark:text-white uppercase tracking-wider mb-4 flex items-center justify-between">
              <span>Repository Share</span>
              <IconFolder class="w-4 h-4 text-indigo-500" />
            </h3>
            
            <div class="space-y-4 overflow-y-auto flex-1 custom-scrollbar pr-1">
              <div 
                v-for="repo in repoStats.slice(0, 5)" 
                :key="repo.name" 
                class="space-y-1.5 transition-all duration-200 hover:translate-x-0.5"
              >
                <div class="flex justify-between items-center text-xs font-bold text-slate-700 dark:text-slate-300">
                  <span class="truncate pr-4 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                    {{ formatRepoName(repo.name) }}
                  </span>
                  <span class="font-mono text-slate-800 dark:text-white font-black flex-shrink-0">
                    {{ repo.total }} ({{ Math.round((repo.total / overallDashboardTotals.total) * 100) }}%)
                  </span>
                </div>
                
                <!-- Progress Line Graph -->
                <div class="h-2 w-full rounded-full bg-slate-100 dark:bg-slate-900 overflow-hidden relative shadow-inner">
                  <div 
                    :style="{ width: `${(repo.total / overallDashboardTotals.total) * 100}%` }"
                    class="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-500"
                  />
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
    <!-- Realtime PR Notifications Toast Container -->
    <div class="fixed bottom-6 right-6 z-50 space-y-3 max-w-sm w-full">
      <div 
        v-for="notif in activeNotifications" 
        :key="notif.id"
        class="bg-white/95 dark:bg-slate-800/95 backdrop-blur-md rounded-2xl border-l-4 border-indigo-600 shadow-2xl p-4 flex items-start gap-3 transition-all duration-300 transform translate-y-0 animate-slide-in relative border border-slate-100 dark:border-slate-700"
      >
        <div class="p-2 bg-indigo-50 dark:bg-indigo-950/40 rounded-xl text-indigo-600 dark:text-indigo-400 flex-shrink-0">
          <IconGitPullRequest class="w-5 h-5" />
        </div>
        
        <div class="space-y-1 pr-6 flex-1 min-w-0">
          <h4 class="text-xs font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-widest">
            {{ notif.title }}
          </h4>
          <p class="text-xs font-bold text-slate-800 dark:text-white truncate">
            {{ notif.repo }}
          </p>
          <p class="text-xs text-slate-500 dark:text-slate-400 leading-snug">
            PR #{{ notif.number }}: '{{ notif.titleText }}' raised by <span class="font-bold text-slate-700 dark:text-slate-300">{{ notif.author }}</span>.
          </p>
          
          <div class="pt-2">
            <a 
              :href="notif.url" 
              target="_blank" 
              class="inline-flex items-center gap-1 text-[11px] font-black text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300"
            >
              Open Pull Request
              <IconExternalLink class="w-3 h-3" />
            </a>
          </div>
        </div>
        
        <button 
          @click="activeNotifications = activeNotifications.filter(n => n.id !== notif.id)"
          class="absolute top-3 right-3 text-slate-400 hover:text-slate-600 dark:hover:text-white"
        >
          <IconX class="w-3.5 h-3.5" />
        </button>
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
	FeatherIcon,
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

import { useSocket } from "@/socket"
import IconCheck from "~icons/lucide/check"
import IconChevronDown from "~icons/lucide/chevron-down"
import IconChevronLeft from "~icons/lucide/chevron-left"
import IconChevronRight from "~icons/lucide/chevron-right"
import IconChevronsLeft from "~icons/lucide/chevrons-left"
import IconChevronsRight from "~icons/lucide/chevrons-right"
import IconClock from "~icons/lucide/clock"
import IconExternalLink from "~icons/lucide/external-link"
import IconFilter from "~icons/lucide/filter"
import IconFolder from "~icons/lucide/folder"
// Lucide Icons
import IconGitPullRequest from "~icons/lucide/git-pull-request"
import IconMessageSquare from "~icons/lucide/message-square"
import IconPlus from "~icons/lucide/plus"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconSearch from "~icons/lucide/search"
import IconUser from "~icons/lucide/user"
import IconX from "~icons/lucide/x"

// Autocomplete filter options
const repoOptions = computed(() => {
	const opts = [{ label: "All Repositories", value: "" }]
	uniqueRepos.value.forEach((repo) => {
		opts.push({ label: formatRepoName(repo), value: repo })
	})
	return opts
})

const statusOptions = [
	{ label: "All PR Statuses", value: "all" },
	{ label: "Open", value: "open" },
	{ label: "Draft", value: "draft" },
	{ label: "Merged", value: "merged" },
	{ label: "Closed / Unmerged", value: "closed" },
]

const uniqueAuthors = computed(() => {
	const authors = pullRequests.value.map((pr) => pr.user?.login).filter(Boolean)
	return [...new Set(authors)]
})

const authorOptions = computed(() => {
	const opts = [{ label: "All Authors", value: "" }]
	uniqueAuthors.value.forEach((author) => {
		opts.push({ label: author, value: author })
	})
	return opts
})

// Popover refs for Autocomplete programmatic toggling
const repoAutocomplete = ref(null)
const statusAutocomplete = ref(null)
const authorAutocomplete = ref(null)

const FILTERABLE_FIELDS = [
	{ label: "Repository", value: "repo", key: "repo" },
	{ label: "Status", value: "status", key: "status" },
	{ label: "Author", value: "author", key: "author" },
]

const activeFilterRules = ref([])

function syncActiveFilterRules() {
	const newRules = []
	if (filters.repo) {
		newRules.push({ id: "rule_repo", field: "repo", value: filters.repo })
	}
	if (filters.status !== "all") {
		newRules.push({ id: "rule_status", field: "status", value: filters.status })
	}
	if (filters.author) {
		newRules.push({ id: "rule_author", field: "author", value: filters.author })
	}
	if (newRules.length === 0) {
		newRules.push({ id: "rule_" + Date.now(), field: "repo", value: "" })
	}
	activeFilterRules.value = newRules
}

function addFilterRule() {
	const unusedField = FILTERABLE_FIELDS.find(
		(f) => !activeFilterRules.value.some((r) => r.field === f.value)
	)
	const field = unusedField ? unusedField.value : "repo"
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
		if (removed.field === "repo") filters.repo = ""
		if (removed.field === "status") filters.status = "all"
		if (removed.field === "author") filters.author = ""
	}
	if (activeFilterRules.value.length === 0) {
		activeFilterRules.value.push({
			id: "rule_" + Date.now(),
			field: "repo",
			value: "",
		})
	}
}

function applyFilterRules() {
	FILTERABLE_FIELDS.forEach((f) => {
		const hasRule = activeFilterRules.value.some((r) => r.field === f.key)
		if (!hasRule) {
			if (f.key === "repo") filters.repo = ""
			if (f.key === "status") filters.status = "all"
			if (f.key === "author") filters.author = ""
		}
	})
	activeFilterRules.value.forEach((r) => {
		if (r.field === "repo") filters.repo = r.value
		if (r.field === "status") filters.status = r.value
		if (r.field === "author") filters.author = r.value
	})
}

function getFieldOptionsForSelect(fieldKey) {
	if (fieldKey === "repo") return repoOptions.value.filter((o) => o.value !== "")
	if (fieldKey === "status") return statusOptions.filter((o) => o.value !== "all")
	if (fieldKey === "author") return authorOptions.value.filter((o) => o.value !== "")
	return []
}

function getFilterLabel(fieldKey, val, defaultText) {
	if (!val || val === "all") return defaultText
	if (fieldKey === "repo") {
		const found = repoOptions.value.find((o) => o.value === val)
		return found ? found.label : val
	}
	if (fieldKey === "status") {
		const found = statusOptions.find((o) => o.value === val)
		return found ? found.label : val
	}
	if (fieldKey === "author") {
		const found = authorOptions.value.find((o) => o.value === val)
		return found ? found.label : val
	}
	return val
}

const hasActiveFilterChips = computed(() => activeFilterChips.value.length > 0)

const activeFilterChips = computed(() => {
	const chips = []
	if (filters.repo) {
		chips.push({ key: "repo", label: "Repository", displayValue: getFilterLabel("repo", filters.repo) })
	}
	if (filters.status !== "all") {
		chips.push({ key: "status", label: "Status", displayValue: getFilterLabel("status", filters.status) })
	}
	return chips
})

function removeFilterByKey(key) {
	if (key === "repo") filters.repo = ""
	if (key === "status") filters.status = "all"
}

const activeFilterCount = computed(() => {
	let count = 0
	if (filters.repo !== "") count++
	if (filters.status !== "all") count++
	return count
})

// High Fidelity Mock Data Fallback
const mockPRs = [
	{
		id: 1001,
		title: "feat: add advanced timesheet analytics dashboards",
		number: 412,
		state: "open",
		draft: false,
		created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
		html_url: "https://github.com/organization/tactix/pull/412",
		repository_url: "https://api.github.com/repos/organization/tactix",
		user: {
			login: "john-doe",
			avatar_url:
				"https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&h=150",
		},
		labels: [],
	},
	{
		id: 1002,
		title: "fix: resolve draft status validation on leave applications",
		number: 398,
		state: "closed",
		is_merged: true,
		created_at: new Date(Date.now() - 3600000 * 6).toISOString(),
		html_url: "https://github.com/organization/tactix/pull/398",
		repository_url: "https://api.github.com/repos/organization/tactix",
		user: {
			login: "jane-smith",
			avatar_url:
				"https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&h=150",
		},
		labels: [],
	},
	{
		id: 1003,
		title: "perf: optimize sqlite and mariadb connection pooling",
		number: 88,
		state: "closed",
		is_merged: true,
		created_at: new Date(Date.now() - 3600000 * 24).toISOString(),
		html_url: "https://github.com/organization/core/pull/88",
		repository_url: "https://api.github.com/repos/organization/core",
		user: {
			login: "alice-dev",
			avatar_url:
				"https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=150&h=150",
		},
		labels: [],
	},
]

// Data State
const pullRequests = ref([])
const repositories = ref([])
const activeTab = ref("list")

// Filters State
const filters = reactive({
	search: "",
	repo: "",
	status: "all",
	author: "",
})

// ListView Column Configuration matching tasks list
const columns = [
	{
		key: "title",
		label: "Pull Request",
		width: "3fr",
		icon: IconGitPullRequest,
	},
	{
		key: "repo",
		label: "Repository",
		width: "1.5fr",
		icon: IconFolder,
	},
	{
		key: "user",
		label: "Author",
		width: "1fr",
		icon: IconUser,
	},
	{
		key: "state",
		label: "Status",
		width: "1fr",
		icon: IconClock,
	},
	{
		key: "comments",
		label: "",
		width: "0.5fr",
		icon: IconMessageSquare,
	},
]

function processPRs(prs) {
	if (!prs) return []
	return prs.map((pr) => {
		return {
			...pr,
			user: {
				...pr.user,
			},
		}
	})
}

// Connect direct backend resource calling get_contributions whitelisted python endpoint
const contributionsResource = createResource({
	url: "tactix.api.github.get_contributions",
	auto: true,
	onSuccess(data) {
		if (data?.error) {
			console.warn(
				"Backend GitHub API failure, falling back to preview mock dataset:",
				data.error,
			)
			pullRequests.value = processPRs([...mockPRs])
			repositories.value = []
		} else {
			pullRequests.value = processPRs(data?.prs || [])
			repositories.value = data?.repos || []
		}
	},
	onError(error) {
		console.error(
			"Backend GitHub API failure, falling back to preview mock dataset:",
			error,
		)
		pullRequests.value = processPRs([...mockPRs])
		repositories.value = []
	},
})

const loading = computed(() => contributionsResource.loading)

const socket = useSocket()
const activeNotifications = ref([])
const simulating = ref(false)

onMounted(() => {
	contributionsResource.reload()

	// Realtime notification listeners when a new pull request is raised
	socket.on("github_pr_notification", (data) => {
		const id = Date.now()
		activeNotifications.value.push({
			id,
			title: data.title,
			repo: data.repo,
			author: data.author,
			number: data.number,
			titleText: data.title_text,
			url: data.url,
		})

		// Auto-dismiss toast notification after 10 seconds
		setTimeout(() => {
			activeNotifications.value = activeNotifications.value.filter(
				(n) => n.id !== id,
			)
		}, 10000)
	})
})

// Trigger Pull Request fetch refresh
function fetchPullRequests() {
	contributionsResource.reload()
}

// Trigger simulation whitelisted API to verify realtime socket notifications
async function simulatePRRaised() {
	simulating.value = true
	try {
		const res = await fetch(
			"/api/method/tactix.api.github.simulate_pr_raised",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-Frappe-CSRF-Token": window.csrf_token,
				},
			},
		)
		if (!res.ok) {
			throw new Error(`Simulation request failure: status ${res.status}`)
		}
	} catch (error) {
		console.error("Realtime simulation error:", error)
	} finally {
		simulating.value = false
	}
}

// Extract repository names from URL
function formatRepoName(repoUrlOrString) {
	if (!repoUrlOrString) return ""
	if (repoUrlOrString.includes("api.github.com/repos/")) {
		return repoUrlOrString.split("/repos/")[1]
	}
	return repoUrlOrString
}

// Dynamic unique repository lists compiled from fetched PRs and backend organization repo lists
const uniqueRepos = computed(() => {
	const reposFromPRs = pullRequests.value.map((pr) =>
		formatRepoName(pr.repository_url),
	)
	const reposFromBackend = repositories.value.map(
		(repo) => repo.full_name || repo.name,
	)
	return [...new Set([...reposFromPRs, ...reposFromBackend])].filter(Boolean)
})

// Active filtering verification
const hasActiveFilters = computed(() => {
	return (
		filters.search !== "" ||
		filters.repo !== "" ||
		filters.status !== "all" ||
		filters.author !== ""
	)
})

// Clear filter conditions
function clearFilters() {
	filters.search = ""
	filters.repo = ""
	filters.status = "all"
	filters.author = ""
}

function filterByStat(label) {
	if (label === "Total PRs") {
		filters.status = "all"
	} else if (label === "Open PRs") {
		filters.status = "open"
	} else if (label === "Merged PRs") {
		filters.status = "merged"
	} else if (label === "Draft PRs") {
		filters.status = "draft"
	}
}

function isCardActive(label) {
	if (label === "Total PRs") {
		return filters.status === "all"
	}
	if (label === "Open PRs") {
		return filters.status === "open"
	}
	if (label === "Merged PRs") {
		return filters.status === "merged"
	}
	if (label === "Draft PRs") {
		return filters.status === "draft"
	}
	return false
}

// Format opened relative durations
function timeAgo(dateString) {
	const date = new Date(dateString)
	const now = new Date()
	const seconds = Math.floor((now - date) / 1000)

	if (seconds < 60) return "just now"
	const minutes = Math.floor(seconds / 60)
	if (minutes < 60) return `${minutes}m ago`
	const hours = Math.floor(minutes / 60)
	if (hours < 24) return `${hours}h ago`
	const days = Math.floor(hours / 24)
	if (days < 30) return `${days}d ago`

	return date.toLocaleDateString(undefined, {
		month: "short",
		day: "numeric",
		year: "numeric",
	})
}

// Map pull request status labels
function getPRStatusLabel(pr) {
	if (pr.state === "open") {
		return pr.draft ? "Draft" : "Open"
	}
	if (pr.state === "closed") {
		return pr.is_merged ? "Merged" : "Closed"
	}
	return pr.state
}

// Map custom status badge theme colors
function getPRStatusTheme(pr) {
	const status = getPRStatusLabel(pr)
	if (status === "Open") return "green"
	if (status === "Draft") return "gray"
	if (status === "Merged") return "purple"
	if (status === "Closed") return "red"
	return "gray"
}

// External redirect action
function openOnGitHub(url) {
	if (url) window.open(url, "_blank")
}

// Get Repository Home Page URL from repository URL or string
function getRepoHomeUrl(repositoryUrl) {
	const repoName = formatRepoName(repositoryUrl)
	return repoName ? `https://github.com/${repoName}` : ""
}

// Aggregate metrics computed properties
const statsBreakdown = computed(() => {
	// Apply all filters except status so cards act as a true overview breakdown of the search/repo scope!
	const scopePRs = pullRequests.value.filter((pr) => {
		if (filters.search) {
			const term = filters.search.toLowerCase()
			const matchesTitle = pr.title.toLowerCase().includes(term)
			const matchesNumber = pr.number.toString().includes(term)
			const matchesAuthor = pr.user.login.toLowerCase().includes(term)
			if (!matchesTitle && !matchesNumber && !matchesAuthor) return false
		}
		if (filters.repo) {
			const repoPath = formatRepoName(pr.repository_url)
			if (repoPath !== filters.repo) return false
		}
		return true
	})

	const total = scopePRs.length
	const open = scopePRs.filter((pr) => pr.state === "open" && !pr.draft).length
	const draft = scopePRs.filter((pr) => pr.state === "open" && pr.draft).length
	const merged = scopePRs.filter(
		(pr) => pr.state === "closed" && pr.is_merged,
	).length

	return [
		{
			label: "Total PRs",
			value: total,
			icon: IconGitPullRequest,
			color: "text-indigo-600 dark:text-indigo-400",
		},
		{
			label: "Open PRs",
			value: open,
			icon: IconClock,
			color: "text-green-600 dark:text-green-400",
		},
		{
			label: "Merged PRs",
			value: merged,
			icon: IconClock,
			color: "text-[#8250df] dark:text-[#8250df]",
		},
		{
			label: "Draft PRs",
			value: draft,
			icon: IconClock,
			color: "text-slate-600 dark:text-slate-400",
		},
	]
})

// Pagination State
const currentPage = ref(1)
const pageLength = 20

const totalCount = computed(() => allFilteredPRs.value.length)
const totalPages = computed(() =>
	Math.max(1, Math.ceil(totalCount.value / pageLength)),
)

const pageOptions = computed(() =>
	Array.from({ length: totalPages.value }, (_, i) => ({
		label: `${i + 1} / ${totalPages.value}`,
		value: i + 1,
	})),
)

// computed property for all filtered PRs (before pagination slicing)
const allFilteredPRs = computed(() => {
	return pullRequests.value.filter((pr) => {
		if (filters.search) {
			const term = filters.search.toLowerCase()
			const matchesTitle = pr.title.toLowerCase().includes(term)
			const matchesNumber = pr.number.toString().includes(term)
			const matchesAuthor = pr.user.login.toLowerCase().includes(term)
			if (!matchesTitle && !matchesNumber && !matchesAuthor) return false
		}

		if (filters.repo) {
			const repoPath = formatRepoName(pr.repository_url)
			if (repoPath !== filters.repo) return false
		}

		if (filters.author) {
			if (pr.user?.login !== filters.author) return false
		}

		if (filters.status !== "all") {
			const statusLabel = getPRStatusLabel(pr).toLowerCase()
			if (filters.status === "open" && statusLabel !== "open") return false
			if (filters.status === "draft" && statusLabel !== "draft") return false
			if (filters.status === "merged" && statusLabel !== "merged") return false
			if (filters.status === "closed" && statusLabel !== "closed") return false
		}

		return true
	})
})

// Sliced list of PRs for current page display
const filteredPRs = computed(() => {
	const start = (currentPage.value - 1) * pageLength
	const end = start + pageLength
	return allFilteredPRs.value.slice(start, end)
})

// pagination page buttons list
const paginationPages = computed(() => {
	const total = totalPages.value
	const current = currentPage.value
	const pages = []

	if (total <= 7) {
		for (let i = 1; i <= total; i++) pages.push(i)
	} else {
		pages.push(1)
		if (current > 4) {
			pages.push("...")
		}
		const start = Math.max(2, current - 2)
		const end = Math.min(total - 1, current + 2)
		for (let i = start; i <= end; i++) {
			pages.push(i)
		}
		if (current < total - 3) {
			pages.push("...")
		}
		pages.push(total)
	}
	return pages
})

// Watch filters to reset page to 1
watch(
	() => [filters.search, filters.repo, filters.status],
	() => {
		currentPage.value = 1
	},
)

// Dynamic Dashboard Analytics Computed Properties
const authorStats = computed(() => {
	const statsMap = {}

	for (const pr of allFilteredPRs.value) {
		const username = pr.user.login
		if (["Gee-thu2000", "Keerthana-tecize"].includes(username)) continue

		if (!statsMap[username]) {
			statsMap[username] = {
				username,
				avatar_url: pr.user.avatar_url,
				total: 0,
				merged: 0,
				open: 0,
				draft: 0,
				closed: 0,
				repos: new Set(),
			}
		}

		statsMap[username].total++
		const statusLabel = getPRStatusLabel(pr).toLowerCase()
		if (statusLabel === "merged") statsMap[username].merged++
		else if (statusLabel === "open") statsMap[username].open++
		else if (statusLabel === "draft") statsMap[username].draft++
		else if (statusLabel === "closed") statsMap[username].closed++

		statsMap[username].repos.add(formatRepoName(pr.repository_url))
	}

	return Object.values(statsMap)
		.map((stat) => ({
			...stat,
			repos: Array.from(stat.repos),
		}))
		.sort((a, b) => b.total - a.total)
})

const repoStats = computed(() => {
	const statsMap = {}

	for (const pr of allFilteredPRs.value) {
		const repoName = formatRepoName(pr.repository_url)
		if (!repoName) continue

		if (!statsMap[repoName]) {
			statsMap[repoName] = {
				name: repoName,
				total: 0,
				merged: 0,
				open: 0,
				draft: 0,
				closed: 0,
			}
		}

		statsMap[repoName].total++
		const statusLabel = getPRStatusLabel(pr).toLowerCase()
		if (statusLabel === "merged") statsMap[repoName].merged++
		else if (statusLabel === "open") statsMap[repoName].open++
		else if (statusLabel === "draft") statsMap[repoName].draft++
		else if (statusLabel === "closed") statsMap[repoName].closed++
	}

	return Object.values(statsMap).sort((a, b) => b.total - a.total)
})

const overallDashboardTotals = computed(() => {
	const total = allFilteredPRs.value.length
	const merged = allFilteredPRs.value.filter(
		(pr) => getPRStatusLabel(pr).toLowerCase() === "merged",
	).length
	const open = allFilteredPRs.value.filter(
		(pr) => getPRStatusLabel(pr).toLowerCase() === "open",
	).length
	const draft = allFilteredPRs.value.filter(
		(pr) => getPRStatusLabel(pr).toLowerCase() === "draft",
	).length
	const closed = allFilteredPRs.value.filter(
		(pr) => getPRStatusLabel(pr).toLowerCase() === "closed",
	).length

	return {
		total,
		merged,
		open,
		draft,
		closed,
	}
})
</script>

<style scoped>
div {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
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
.custom-scrollbar::-webkit-scrollbar-track {
	background: transparent !important;
}

:global([data-radix-popper-content-wrapper]), :global([data-reka-popper-content-wrapper]), :global(.PopoverContent) { z-index: 100005 !important; }
</style>
