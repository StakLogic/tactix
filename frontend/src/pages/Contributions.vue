<template>
  <div class="flex h-full min-h-0 flex-col gap-3 overflow-hidden p-1">
    <!-- Header -->
    <div class="flex flex-shrink-0 flex-col justify-between gap-3 md:flex-row md:items-center">
      <div class="flex items-center gap-3">
        <span class="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)]">
          <IconGitPullRequest class="h-5 w-5" />
        </span>
        <div>
          <h1 class="text-xl font-semibold tracking-tight text-ink-gray-9">Contributions</h1>
          <p class="text-xs text-ink-gray-5">Pull requests and engineering activity across the organization.</p>
        </div>
      </div>
      <span v-if="lastUpdated" class="text-xs text-ink-gray-4">Updated {{ lastUpdated }}</span>
    </div>

    <!-- Sample-data notice (GitHub unreachable) -->
    <div
      v-if="usingSampleData"
      class="flex flex-shrink-0 items-center justify-between gap-3 rounded-lg border border-amber-300/60 bg-amber-50 px-3 py-2 text-xs text-amber-800 dark:bg-amber-950/30 dark:text-amber-300"
    >
      <span><b>Couldn't load data from GitHub.</b> Showing sample pull requests for preview only.</span>
      <button type="button" class="font-semibold underline hover:no-underline" @click="fetchPullRequests">Try again</button>
    </div>

    <!-- KPI strip -->
    <div class="grid flex-shrink-0 grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
      <div
        v-for="stat in statsBreakdown"
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
          <span class="truncate text-xs font-medium text-ink-gray-6">{{ stat.label }}</span>
          <span class="h-2 w-2 shrink-0 rounded-full" :style="{ background: stat.dot }"></span>
        </div>
        <div class="mt-1.5 flex h-7 items-center">
          <div v-if="loading && !pullRequests.length" class="skeleton h-5 w-10"></div>
          <span v-else class="text-[22px] font-semibold leading-none tabular-nums text-ink-gray-9">{{ stat.value }}</span>
        </div>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="toolbar-card flex flex-shrink-0 flex-col gap-2.5">
      <div class="flex w-full flex-col justify-between gap-2.5 sm:flex-row sm:items-center">
        <!-- Search -->
        <div class="relative w-full sm:w-80">
          <IconSearch class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-ink-gray-4" />
          <input
            ref="searchInputEl"
            v-model="filters.search"
            type="text"
            placeholder="Search title, number or author…"
            class="h-8 w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 pl-9 pr-9 text-[13px] text-ink-gray-8 outline-none transition focus:border-[color:var(--brand,#29ADFF)] focus:bg-surface-white focus:ring-2 focus:ring-[color:var(--brand-soft,#E9F6FF)]"
          />
          <kbd v-if="!filters.search" class="kbd absolute right-2 top-1/2 -translate-y-1/2" title="Press / to search">/</kbd>
          <button
            v-else
            type="button"
            class="absolute right-1.5 top-1/2 -translate-y-1/2 rounded p-1 text-ink-gray-4 hover:bg-surface-gray-2 hover:text-ink-gray-7"
            title="Clear search"
            @click="filters.search = ''"
          >
            <IconX class="h-3.5 w-3.5" />
          </button>
        </div>

        <div class="ml-auto flex flex-wrap items-center justify-end gap-2 sm:ml-0">
          <!-- View tabs -->
          <div class="flex rounded-md border border-outline-gray-2 bg-surface-gray-2 p-0.5" role="tablist">
            <button
              type="button"
              role="tab"
              :aria-selected="activeTab === 'list'"
              :class="tabClass('list')"
              @click="activeTab = 'list'"
            >
              <IconList class="h-3.5 w-3.5" /> Pull Requests
            </button>
            <button
              type="button"
              role="tab"
              :aria-selected="activeTab === 'dashboard'"
              :class="tabClass('dashboard')"
              @click="activeTab = 'dashboard'"
            >
              <IconBarChart class="h-3.5 w-3.5" /> Analytics
            </button>
          </div>

          <!-- Filter popover -->
          <Popover placement="bottom-end">
            <template #target="{ togglePopover }">
              <Button
                variant="outline"
                :class="[
                  '!h-8 !px-2.5 text-xs font-medium',
                  activeFilterCount > 0 && '!border-[color:var(--brand,#29ADFF)] !bg-[color:var(--brand-soft,#E9F6FF)] !text-[color:var(--brand-text,#0A84D0)]',
                ]"
                title="Filter contributions"
                @click="syncActiveFilterRules(); togglePopover()"
              >
                <template #prefix><IconFilter class="h-3.5 w-3.5" /></template>
                <span>Filter</span>
                <span
                  v-if="activeFilterCount > 0"
                  class="ml-1 rounded-full bg-[color:var(--brand,#29ADFF)] px-1.5 text-[10px] font-bold leading-4 text-white"
                >{{ activeFilterCount }}</span>
              </Button>
            </template>
            <template #body-main="{ close }">
              <div class="w-80 space-y-3 rounded-lg border border-outline-gray-2 bg-surface-modal p-3 text-xs shadow-lg">
                <div class="flex items-center justify-between border-b border-outline-gray-1 pb-2">
                  <span class="font-semibold text-ink-gray-8">Filter contributions</span>
                  <button
                    v-if="hasActiveFilters"
                    type="button"
                    class="flex items-center gap-1 text-[11px] font-medium text-red-600 hover:text-red-700"
                    @click="clearFilters"
                  >
                    <IconX class="h-3 w-3" /> Clear all
                  </button>
                </div>

                <div class="custom-scrollbar max-h-60 space-y-2 overflow-y-auto pr-1">
                  <div
                    v-for="rule in activeFilterRules"
                    :key="rule.id"
                    class="flex items-center gap-1.5 rounded-md border border-outline-gray-1 bg-surface-gray-1 p-1.5"
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
                    <span class="shrink-0 text-[10px] font-semibold text-ink-gray-4">=</span>
                    <div class="min-w-0 flex-1">
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
                      type="button"
                      class="shrink-0 rounded p-1 text-ink-gray-4 transition-colors hover:bg-red-50 hover:text-red-500"
                      title="Remove filter"
                      @click="removeFilterRule(rule.id)"
                    >
                      <IconX class="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>

                <div class="flex items-center justify-between border-t border-outline-gray-1 pt-2">
                  <button
                    type="button"
                    class="inline-flex items-center gap-1 rounded px-2 py-1 text-xs font-medium text-[color:var(--brand-text,#0A84D0)] hover:bg-[color:var(--brand-soft,#E9F6FF)]"
                    @click="addFilterRule"
                  >
                    <IconPlus class="h-3.5 w-3.5" /> Add filter
                  </button>
                  <Button variant="solid" class="brand-btn !h-7 !px-3 text-xs" @click="applyFilterRules(); close()">Apply</Button>
                </div>
              </div>
            </template>
          </Popover>

          <!-- Refresh -->
          <Button variant="outline" class="!h-8 !px-2.5" :disabled="loading" title="Refresh" @click="fetchPullRequests">
            <template #prefix><IconRefresh class="h-3.5 w-3.5" :class="loading && 'animate-spin'" /></template>
          </Button>
        </div>
      </div>

      <!-- Quick filters -->
      <div class="custom-scrollbar flex w-full flex-nowrap gap-2 overflow-x-auto pb-1 sm:flex-wrap sm:items-center sm:overflow-visible sm:pb-0">
        <div class="w-48 shrink-0">
          <Autocomplete
            ref="repoAutocomplete"
            :options="repoOptions"
            :modelValue="filters.repo"
            :max-options="100"
            @update:modelValue="val => filters.repo = (val && typeof val === 'object') ? (val.value ?? '') : (val ?? '')"
          >
            <template #target>
              <button type="button" :class="['qf', filters.repo !== '' && 'on']" @click="() => repoAutocomplete?.togglePopover()">
                <IconFolder class="h-3.5 w-3.5 shrink-0 opacity-70" />
                <span class="flex-1 truncate text-left">{{ getFilterLabel('repo', filters.repo, 'Repository') }}</span>
                <FeatherIcon name="chevron-down" class="size-3.5 shrink-0 opacity-60" />
              </button>
            </template>
          </Autocomplete>
        </div>

        <div class="w-40 shrink-0">
          <Autocomplete
            ref="statusAutocomplete"
            :options="statusOptions"
            :modelValue="filters.status"
            @update:modelValue="val => filters.status = (val && typeof val === 'object') ? (val.value ?? 'all') : (val ?? 'all')"
          >
            <template #target>
              <button type="button" :class="['qf', filters.status !== 'all' && 'on']" @click="() => statusAutocomplete?.togglePopover()">
                <span class="flex-1 truncate text-left">{{ getFilterLabel('status', filters.status, 'Status') }}</span>
                <FeatherIcon name="chevron-down" class="size-3.5 shrink-0 opacity-60" />
              </button>
            </template>
          </Autocomplete>
        </div>

        <div class="w-40 shrink-0">
          <Autocomplete
            ref="authorAutocomplete"
            :options="authorOptions"
            :modelValue="filters.author"
            :max-options="100"
            @update:modelValue="val => filters.author = (val && typeof val === 'object') ? (val.value ?? '') : (val ?? '')"
          >
            <template #target>
              <button type="button" :class="['qf', filters.author !== '' && 'on']" @click="() => authorAutocomplete?.togglePopover()">
                <IconUser class="h-3.5 w-3.5 shrink-0 opacity-70" />
                <span class="flex-1 truncate text-left">{{ getFilterLabel('author', filters.author, 'Author') }}</span>
                <FeatherIcon name="chevron-down" class="size-3.5 shrink-0 opacity-60" />
              </button>
            </template>
          </Autocomplete>
        </div>

        <button
          v-if="hasActiveFilters"
          type="button"
          class="inline-flex h-7 shrink-0 items-center gap-1 rounded-md px-2 text-xs font-medium text-red-500 hover:bg-red-50"
          @click="clearFilters"
        >
          <IconX class="h-3.5 w-3.5" /> Clear
        </button>
      </div>
    </div>

    <!-- ===================== LIST ===================== -->
    <div v-if="activeTab === 'list'" class="panel relative flex min-h-[420px] flex-1 flex-col overflow-y-auto md:min-h-0 md:overflow-hidden">
      <div v-if="loading && pullRequests.length" class="busy-bar" aria-hidden="true"></div>

      <!-- first load -->
      <div v-if="loading && !pullRequests.length" class="divide-y divide-outline-gray-1">
        <div v-for="n in 6" :key="n" class="flex items-center gap-3 px-4 py-3">
          <div class="skeleton h-8 w-8 rounded-full"></div>
          <div class="flex-1 space-y-1.5">
            <div class="skeleton h-3.5 w-1/2"></div>
            <div class="skeleton h-3 w-1/4"></div>
          </div>
          <div class="skeleton h-5 w-16"></div>
        </div>
      </div>

      <div v-else-if="filteredPRs.length === 0" class="flex flex-1 flex-col items-center justify-center px-4 py-16 text-center">
        <span class="grid h-11 w-11 place-items-center rounded-full bg-surface-gray-2 text-ink-gray-5">
          <IconGitPullRequest class="h-5 w-5" />
        </span>
        <h3 class="mt-3 text-sm font-semibold text-ink-gray-8">No pull requests found</h3>
        <p class="mt-1 max-w-xs text-xs text-ink-gray-5">
          {{ hasActiveFilters ? 'Nothing matches your filters. Try removing one.' : 'Pull requests will appear here once they are raised.' }}
        </p>
        <Button v-if="hasActiveFilters" variant="subtle" size="sm" class="mt-3" @click="clearFilters">Clear filters</Button>
      </div>

      <ListView
        v-else
        class="flex h-full min-h-0 flex-col"
        :columns="columns"
        :rows="filteredPRs"
        row-key="id"
        :options="{ showTooltip: true, resizeColumn: true, selectable: false }"
      >
        <ListHeader class="shrink-0 border-b border-outline-gray-2 bg-surface-gray-1">
          <ListHeaderItem v-for="col in columns" :key="col.key" :item="col">
            <template #prefix="{ item }">
              <component :is="item.icon" class="size-3.5 text-ink-gray-4" />
            </template>
          </ListHeaderItem>
        </ListHeader>

        <div class="custom-scrollbar relative min-h-0 max-h-[480px] flex-grow overflow-y-auto md:max-h-none md:flex-1">
          <ListRows>
            <ListRow
              v-for="row in filteredPRs"
              :key="row.id"
              v-slot="{ column, item }"
              :row="row"
              class="group cursor-pointer"
              @click="openOnGitHub(row.html_url)"
            >
              <ListRowItem :item="item">
                <template v-if="column.key === 'title'">
                  <div class="flex min-w-0 items-center gap-3 overflow-hidden">
                    <span class="grid h-7 w-7 shrink-0 place-items-center rounded-md" :style="statusIconStyle(row)">
                      <IconGitPullRequest class="h-3.5 w-3.5" />
                    </span>
                    <div class="min-w-0 flex-1">
                      <div class="truncate text-sm font-medium text-ink-gray-9 group-hover:text-[color:var(--brand-text,#0A84D0)]" :title="row.title">
                        {{ row.title }}
                      </div>
                      <div class="mt-0.5 flex items-center gap-1.5 text-[11px] text-ink-gray-5">
                        <span class="font-mono">#{{ row.number }}</span>
                        <span class="text-ink-gray-3">·</span>
                        <span v-tooltip="formatFullDate(row.created_at)">opened {{ timeAgo(row.created_at) }}</span>
                      </div>
                    </div>
                  </div>
                </template>

                <template v-if="column.key === 'repo'">
                  <button
                    type="button"
                    class="block max-w-full truncate rounded bg-surface-gray-2 px-1.5 py-0.5 font-mono text-[11.5px] text-ink-gray-7 hover:bg-[color:var(--brand-soft,#E9F6FF)] hover:text-[color:var(--brand-text,#0A84D0)]"
                    :title="'Open ' + formatRepoName(row.repository_url) + ' on GitHub'"
                    @click.stop="openOnGitHub(getRepoHomeUrl(row.repository_url))"
                  >
                    {{ formatRepoName(row.repository_url) }}
                  </button>
                </template>

                <template v-if="column.key === 'user'">
                  <button
                    type="button"
                    class="flex min-w-0 max-w-full items-center gap-2 text-xs text-ink-gray-7 hover:text-[color:var(--brand-text,#0A84D0)]"
                    :title="'Open ' + row.user?.login + ' on GitHub'"
                    @click.stop="openOnGitHub('https://github.com/' + row.user?.login)"
                  >
                    <Avatar :image="row.user?.avatar_url" :label="row.user?.login" size="sm" class="shrink-0" />
                    <span class="truncate font-medium">{{ row.user?.login }}</span>
                  </button>
                </template>

                <template v-if="column.key === 'state'">
                  <span class="status-pill" :style="statusPillStyle(row)">
                    <span class="h-1.5 w-1.5 rounded-full" :style="{ background: statusColor(getPRStatusLabel(row)) }"></span>
                    {{ getPRStatusLabel(row) }}
                  </span>
                </template>

                <template v-if="column.key === 'comments'">
                  <div class="flex justify-end pr-2">
                    <span v-if="row.comments > 0" class="flex items-center gap-1 text-xs text-ink-gray-5" :title="row.comments + ' comments'">
                      <IconMessageSquare class="h-3.5 w-3.5" />
                      <span class="tabular-nums">{{ row.comments }}</span>
                    </span>
                  </div>
                </template>
              </ListRowItem>
            </ListRow>
          </ListRows>
        </div>
      </ListView>

      <!-- Pagination -->
      <div v-if="totalCount > 0" class="flex shrink-0 items-center justify-between border-t border-outline-gray-1 px-4 py-2">
        <div class="flex items-center gap-1">
          <button type="button" class="pg-btn" :disabled="currentPage === 1" title="First page" @click="currentPage = 1">
            <IconChevronsLeft class="h-3.5 w-3.5" />
          </button>
          <button type="button" class="pg-btn" :disabled="currentPage === 1" title="Previous page" @click="currentPage = Math.max(1, currentPage - 1)">
            <IconChevronLeft class="h-3.5 w-3.5" />
          </button>
          <Popover>
            <template #target="{ togglePopover }">
              <button
                type="button"
                class="flex h-6 shrink-0 items-center gap-1 rounded border border-outline-gray-2 px-2 text-[11px] font-semibold tabular-nums text-ink-gray-7 hover:bg-surface-gray-2"
                @click="togglePopover"
              >
                {{ currentPage }} / {{ totalPages }}
                <IconChevronDown class="h-3 w-3 text-ink-gray-4" />
              </button>
            </template>
            <template #body="{ close }">
              <div class="custom-scrollbar max-h-48 w-32 overflow-y-auto rounded-lg border border-outline-gray-2 bg-surface-modal p-1 shadow-lg">
                <button
                  v-for="p in totalPages"
                  :key="p"
                  type="button"
                  :class="[
                    'flex w-full items-center justify-between rounded px-2 py-1 text-left text-xs transition-colors',
                    currentPage === p
                      ? 'bg-[color:var(--brand,#29ADFF)] font-semibold text-white'
                      : 'text-ink-gray-7 hover:bg-surface-gray-2',
                  ]"
                  @click="currentPage = p; close()"
                >
                  <span>Page {{ p }}</span>
                  <IconCheck v-if="currentPage === p" class="h-3 w-3" />
                </button>
              </div>
            </template>
          </Popover>
          <button type="button" class="pg-btn" :disabled="currentPage >= totalPages" title="Next page" @click="currentPage = Math.min(totalPages, currentPage + 1)">
            <IconChevronRight class="h-3.5 w-3.5" />
          </button>
          <button type="button" class="pg-btn" :disabled="currentPage >= totalPages" title="Last page" @click="currentPage = totalPages">
            <IconChevronsRight class="h-3.5 w-3.5" />
          </button>
        </div>
        <div class="text-xs text-ink-gray-5">
          <b class="font-semibold tabular-nums text-ink-gray-8">{{ (currentPage - 1) * pageLength + 1 }}–{{ Math.min(currentPage * pageLength, totalCount) }}</b>
          of <b class="font-semibold tabular-nums text-ink-gray-8">{{ totalCount }}</b>
        </div>
      </div>
    </div>

    <!-- ===================== ANALYTICS ===================== -->
    <div v-else-if="activeTab === 'dashboard'" class="custom-scrollbar min-h-0 flex-1 overflow-y-auto">
      <div v-if="loading && !pullRequests.length" class="panel grid place-items-center p-16">
        <div class="h-6 w-6 animate-spin rounded-full border-2 border-outline-gray-2 border-t-[color:var(--brand,#29ADFF)]"></div>
      </div>

      <div v-else-if="authorStats.length === 0" class="panel flex flex-col items-center justify-center px-4 py-16 text-center">
        <span class="grid h-11 w-11 place-items-center rounded-full bg-surface-gray-2 text-ink-gray-5">
          <IconBarChart class="h-5 w-5" />
        </span>
        <h3 class="mt-3 text-sm font-semibold text-ink-gray-8">No data available</h3>
        <p class="mt-1 max-w-xs text-xs text-ink-gray-5">No pull request activity matches your filters.</p>
      </div>

      <div v-else class="grid min-h-0 grid-cols-1 gap-4 lg:grid-cols-12">
        <!-- Leaderboard -->
        <div class="panel flex min-h-[420px] flex-col overflow-hidden lg:col-span-7">
          <div class="flex items-center justify-between border-b border-outline-gray-1 px-4 py-3">
            <div>
              <h3 class="text-[15px] font-semibold text-ink-gray-9">Top contributors</h3>
              <p class="text-xs text-ink-gray-5">Ranked by pull requests raised</p>
            </div>
            <span class="rounded-full bg-[color:var(--brand-soft,#E9F6FF)] px-2 py-0.5 text-xs font-semibold text-[color:var(--brand-text,#0A84D0)]">
              {{ authorStats.length }} author{{ authorStats.length === 1 ? '' : 's' }}
            </span>
          </div>

          <ul class="custom-scrollbar flex-1 divide-y divide-outline-gray-1 overflow-y-auto">
            <li v-for="(author, idx) in authorStats" :key="author.username" class="flex items-center gap-3 px-4 py-3 hover:bg-surface-gray-1">
              <span class="rank" :class="idx < 3 && 'rank-' + (idx + 1)">{{ idx + 1 }}</span>
              <button type="button" class="shrink-0" :title="'Open ' + author.username + ' on GitHub'" @click="openOnGitHub('https://github.com/' + author.username)">
                <Avatar :image="author.avatar_url" :label="author.username" size="lg" />
              </button>
              <div class="min-w-0 flex-1">
                <button
                  type="button"
                  class="block max-w-full truncate text-left text-sm font-medium text-ink-gray-9 hover:text-[color:var(--brand-text,#0A84D0)]"
                  @click="openOnGitHub('https://github.com/' + author.username)"
                >
                  {{ author.username }}
                </button>
                <div class="mt-0.5 flex flex-wrap items-center gap-x-2.5 gap-y-0.5 text-[11px] text-ink-gray-5">
                  <span v-for="s in STATUS_KEYS" v-show="author[s.key] > 0" :key="s.key" class="flex items-center gap-1">
                    <span class="h-1.5 w-1.5 rounded-full" :style="{ background: s.color }"></span>{{ author[s.key] }} {{ s.label.toLowerCase() }}
                  </span>
                </div>
              </div>
              <div class="flex w-1/3 min-w-[120px] max-w-[200px] flex-col items-end gap-1.5">
                <span class="text-xs font-semibold tabular-nums text-ink-gray-8">{{ author.total }} PR{{ author.total === 1 ? '' : 's' }}</span>
                <div class="track flex">
                  <div
                    v-for="s in STATUS_KEYS"
                    :key="s.key"
                    class="h-full transition-all duration-500"
                    :style="{ width: (author[s.key] / author.total) * 100 + '%', background: s.color }"
                    :title="s.label + ': ' + author[s.key]"
                  ></div>
                </div>
              </div>
            </li>
          </ul>
        </div>

        <div class="flex min-h-0 flex-col gap-4 lg:col-span-5">
          <!-- Status donut -->
          <div class="panel p-4">
            <h3 class="text-[15px] font-semibold text-ink-gray-9">Status breakdown</h3>
            <p class="text-xs text-ink-gray-5">All pull requests in the current filters</p>

            <div class="mt-4 flex items-center gap-6">
              <div class="relative h-36 w-36 shrink-0">
                <svg class="h-full w-full -rotate-90" viewBox="0 0 42 42">
                  <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="var(--surface-gray-2, #f3f3f3)" stroke-width="4.5" />
                  <circle
                    v-for="seg in donutSegments"
                    :key="seg.key"
                    cx="21"
                    cy="21"
                    r="15.915"
                    fill="transparent"
                    :stroke="seg.color"
                    stroke-width="4.5"
                    :stroke-dasharray="`${seg.pct} ${100 - seg.pct}`"
                    :stroke-dashoffset="-seg.offset"
                    class="transition-all duration-700 ease-out"
                  >
                    <title>{{ seg.label }}: {{ seg.value }}</title>
                  </circle>
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center">
                  <span class="text-2xl font-semibold leading-none tabular-nums text-ink-gray-9">{{ overallDashboardTotals.total }}</span>
                  <span class="mt-1 text-[10px] font-medium uppercase tracking-wider text-ink-gray-5">Total PRs</span>
                </div>
              </div>

              <ul class="flex-1 space-y-2.5">
                <li v-for="s in STATUS_KEYS" :key="s.key" class="flex items-center justify-between text-xs">
                  <span class="flex items-center gap-2 text-ink-gray-7">
                    <span class="h-2.5 w-2.5 rounded-sm" :style="{ background: s.color }"></span>{{ s.label }}
                  </span>
                  <span class="tabular-nums text-ink-gray-5">
                    <b class="font-semibold text-ink-gray-9">{{ overallDashboardTotals[s.key] }}</b>
                    · {{ pctOf(overallDashboardTotals[s.key]) }}%
                  </span>
                </li>
              </ul>
            </div>
          </div>

          <!-- Repository share -->
          <div class="panel flex flex-1 flex-col overflow-hidden p-4">
            <div class="mb-4 flex items-center justify-between">
              <div>
                <h3 class="text-[15px] font-semibold text-ink-gray-9">Repository share</h3>
                <p class="text-xs text-ink-gray-5">Top {{ Math.min(5, repoStats.length) }} of {{ repoStats.length }} repositories</p>
              </div>
              <IconFolder class="h-4 w-4 text-ink-gray-4" />
            </div>

            <div class="custom-scrollbar flex-1 space-y-3.5 overflow-y-auto pr-1">
              <button
                v-for="repo in repoStats.slice(0, 5)"
                :key="repo.name"
                type="button"
                class="block w-full space-y-1.5 text-left"
                :title="'Show only ' + formatRepoName(repo.name)"
                @click="filters.repo = repo.name; activeTab = 'list'"
              >
                <div class="flex items-center justify-between gap-3 text-xs">
                  <span class="truncate font-mono text-ink-gray-7 hover:text-[color:var(--brand-text,#0A84D0)]">{{ formatRepoName(repo.name) }}</span>
                  <span class="shrink-0 tabular-nums text-ink-gray-5">
                    <b class="font-semibold text-ink-gray-9">{{ repo.total }}</b> · {{ pctOf(repo.total) }}%
                  </span>
                </div>
                <div class="track">
                  <div class="fill bg-[color:var(--brand,#29ADFF)]" :style="{ width: pctOf(repo.total) + '%' }"></div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Realtime PR notifications -->
    <TransitionGroup name="toast" tag="div" class="fixed bottom-5 right-5 z-50 w-full max-w-sm space-y-2">
      <div
        v-for="notif in activeNotifications"
        :key="notif.id"
        class="relative flex items-start gap-3 rounded-xl border border-outline-gray-2 bg-surface-modal p-3.5 shadow-xl"
      >
        <span class="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)]">
          <IconGitPullRequest class="h-4 w-4" />
        </span>
        <div class="min-w-0 flex-1 space-y-0.5 pr-5">
          <p class="text-[11px] font-semibold uppercase tracking-wide text-[color:var(--brand-text,#0A84D0)]">{{ notif.title }}</p>
          <p class="truncate font-mono text-xs text-ink-gray-7">{{ notif.repo }}</p>
          <p class="text-xs leading-snug text-ink-gray-6">
            #{{ notif.number }} {{ notif.titleText }} · by <b class="font-medium text-ink-gray-8">{{ notif.author }}</b>
          </p>
          <a
            :href="notif.url"
            target="_blank"
            rel="noopener"
            class="inline-flex items-center gap-1 pt-1 text-[11px] font-semibold text-[color:var(--brand-text,#0A84D0)] hover:underline"
          >
            Open pull request <IconExternalLink class="h-3 w-3" />
          </a>
        </div>
        <button
          type="button"
          class="absolute right-2.5 top-2.5 rounded p-0.5 text-ink-gray-4 hover:bg-surface-gray-2 hover:text-ink-gray-7"
          title="Dismiss"
          @click="activeNotifications = activeNotifications.filter(n => n.id !== notif.id)"
        >
          <IconX class="h-3.5 w-3.5" />
        </button>
      </div>
    </TransitionGroup>
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
import { computed, onMounted, onUnmounted, reactive, ref, watch } from "vue"

import { useSocket } from "@/socket"
import IconCheck from "~icons/lucide/check"
import IconChevronDown from "~icons/lucide/chevron-down"
import IconChevronLeft from "~icons/lucide/chevron-left"
import IconChevronRight from "~icons/lucide/chevron-right"
import IconChevronsLeft from "~icons/lucide/chevrons-left"
import IconChevronsRight from "~icons/lucide/chevrons-right"
import IconBarChart from "~icons/lucide/bar-chart-3"
import IconList from "~icons/lucide/list"
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
		(f) => !activeFilterRules.value.some((r) => r.field === f.value),
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
	if (fieldKey === "repo")
		return repoOptions.value.filter((o) => o.value !== "")
	if (fieldKey === "status")
		return statusOptions.filter((o) => o.value !== "all")
	if (fieldKey === "author")
		return authorOptions.value.filter((o) => o.value !== "")
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
		chips.push({
			key: "repo",
			label: "Repository",
			displayValue: getFilterLabel("repo", filters.repo),
		})
	}
	if (filters.status !== "all") {
		chips.push({
			key: "status",
			label: "Status",
			displayValue: getFilterLabel("status", filters.status),
		})
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
	if (filters.author !== "") count++
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

const usingSampleData = ref(false) // true when GitHub failed and the mock preview data is shown
const lastFetchedAt = ref(null)
const nowTick = ref(Date.now())
const lastUpdated = computed(() => {
	nowTick.value // re-evaluate every minute
	return lastFetchedAt.value ? timeAgo(lastFetchedAt.value) : ""
})

// Connect direct backend resource calling get_contributions whitelisted python endpoint
const contributionsResource = createResource({
	url: "tactix.api.github.get_contributions",
	auto: true,
	onSuccess(data) {
		lastFetchedAt.value = Date.now()
		if (data?.error) {
			usingSampleData.value = true
			console.warn(
				"Backend GitHub API failure, falling back to preview mock dataset:",
				data.error,
			)
			pullRequests.value = processPRs([...mockPRs])
			repositories.value = []
		} else {
			usingSampleData.value = false
			pullRequests.value = processPRs(data?.prs || [])
			repositories.value = data?.repos || []
		}
	},
	onError(error) {
		usingSampleData.value = true
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

function onPRNotification(data) {
		const id = Date.now() + Math.random()
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
}

// "/" focuses search when not typing
const searchInputEl = ref(null)
function handleSlashKey(e) {
	if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey) return
	const t = e.target
	if (t && (t.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(t.tagName))) return
	e.preventDefault()
	searchInputEl.value?.focus()
}

let tickTimer = null
onMounted(() => {
	// contributionsResource has auto: true, so it already loads once — no extra reload here
	socket?.on("github_pr_notification", onPRNotification)
	window.addEventListener("keydown", handleSlashKey)
	tickTimer = setInterval(() => (nowTick.value = Date.now()), 60000)
})

onUnmounted(() => {
	// without this, every visit added another listener and toasts showed up 2x, 3x…
	socket?.off("github_pr_notification", onPRNotification)
	window.removeEventListener("keydown", handleSlashKey)
	clearInterval(tickTimer)
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

const STAT_STATUS = {
	"Total PRs": "all",
	"Open PRs": "open",
	"Merged PRs": "merged",
	"Draft PRs": "draft",
	"Closed PRs": "closed",
}

function filterByStat(label) {
	const status = STAT_STATUS[label] || "all"
	// clicking the active card again goes back to all statuses
	filters.status = filters.status === status ? "all" : status
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
	if (label === "Closed PRs") {
		return filters.status === "closed"
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
			const matchesTitle = (pr.title || "").toLowerCase().includes(term)
			const matchesNumber = String(pr.number ?? "").includes(term)
			const matchesAuthor = (pr.user?.login || "").toLowerCase().includes(term)
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
	const closed = scopePRs.filter(
		(pr) => pr.state === "closed" && !pr.is_merged,
	).length

	return [
		{ label: "Total PRs", value: total, dot: "var(--brand, #29ADFF)" },
		{ label: "Open PRs", value: open, dot: STATUS_COLORS.Open },
		{ label: "Merged PRs", value: merged, dot: STATUS_COLORS.Merged },
		{ label: "Draft PRs", value: draft, dot: STATUS_COLORS.Draft },
		{ label: "Closed PRs", value: closed, dot: STATUS_COLORS.Closed },
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
			const matchesTitle = (pr.title || "").toLowerCase().includes(term)
			const matchesNumber = String(pr.number ?? "").includes(term)
			const matchesAuthor = (pr.user?.login || "").toLowerCase().includes(term)
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
	() => [filters.search, filters.repo, filters.status, filters.author],
	() => {
		currentPage.value = 1
	},
)
watch(totalPages, (n) => {
	if (currentPage.value > n) currentPage.value = n
})

// Dynamic Dashboard Analytics Computed Properties
const authorStats = computed(() => {
	const statsMap = {}

	for (const pr of allFilteredPRs.value) {
		const username = pr.user?.login
		if (!username) continue
		if (["Gee-thu2000", "Keerthana-tecize"].includes(username)) continue

		if (!statsMap[username]) {
			statsMap[username] = {
				username,
				avatar_url: pr.user?.avatar_url,
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

/* ---------------- UI helpers ---------------- */
const STATUS_COLORS = {
	Open: "#22c55e",
	Merged: "#8250df",
	Draft: "#94a3b8",
	Closed: "#ef4444",
}

const STATUS_KEYS = [
	{ key: "merged", label: "Merged", color: STATUS_COLORS.Merged },
	{ key: "open", label: "Open", color: STATUS_COLORS.Open },
	{ key: "draft", label: "Draft", color: STATUS_COLORS.Draft },
	{ key: "closed", label: "Closed", color: STATUS_COLORS.Closed },
]

function statusColor(label) {
	return STATUS_COLORS[label] || "#94a3b8"
}

// tinted pill (works in light & dark)
function statusPillStyle(pr) {
	const c = statusColor(getPRStatusLabel(pr))
	return { color: c, background: c + "1a", boxShadow: `inset 0 0 0 1px ${c}33` }
}

function statusIconStyle(pr) {
	const c = statusColor(getPRStatusLabel(pr))
	return { color: c, background: c + "14" }
}

function formatFullDate(dateString) {
	if (!dateString) return ""
	return new Date(dateString).toLocaleString(undefined, {
		day: "numeric",
		month: "short",
		year: "numeric",
		hour: "numeric",
		minute: "2-digit",
	})
}

function pctOf(n) {
	const total = overallDashboardTotals.value.total
	return total ? Math.round((n / total) * 100) : 0
}

const donutSegments = computed(() => {
	const t = overallDashboardTotals.value
	const total = Math.max(1, t.total)
	let offset = 0
	return STATUS_KEYS.map((s) => {
		const pct = (t[s.key] / total) * 100
		const seg = { ...s, value: t[s.key], pct, offset }
		offset += pct
		return seg
	}).filter((s) => s.value > 0)
})

function tabClass(tab) {
	return [
		"flex items-center gap-1.5 rounded px-2.5 py-1 text-xs font-medium transition-colors",
		activeTab.value === tab
			? "bg-surface-white text-[color:var(--brand-text,#0A84D0)] shadow-sm"
			: "text-ink-gray-5 hover:text-ink-gray-8",
	]
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

/* ---- Cards & panels ---- */
.panel,
.toolbar-card {
	border: 1px solid var(--outline-gray-1, #ededed);
	border-radius: 12px;
	background: var(--surface-cards, #fff);
	box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}
.toolbar-card {
	padding: 10px 12px;
	border-radius: 10px;
}
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
.qf {
	display: inline-flex;
	align-items: center;
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
	padding: 2px 8px;
	border-radius: 999px;
	font-size: 12px;
	font-weight: 500;
	line-height: 18px;
	white-space: nowrap;
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

/* ---- Analytics ---- */
.track {
	height: 6px;
	width: 100%;
	overflow: hidden;
	border-radius: 999px;
	background: var(--surface-gray-2, #f3f3f3);
}
.fill {
	height: 100%;
	border-radius: 999px;
	transition: width 0.5s ease;
}
.rank {
	display: grid;
	flex-shrink: 0;
	place-items: center;
	width: 24px;
	height: 24px;
	border-radius: 999px;
	background: var(--surface-gray-2, #f3f3f3);
	color: var(--ink-gray-6, #6b6b6b);
	font-size: 11px;
	font-weight: 700;
	font-variant-numeric: tabular-nums;
}
.rank-1 {
	background: #fef3c7;
	color: #b45309;
	box-shadow: 0 0 0 1px #fcd34d inset;
}
.rank-2 {
	background: #f1f5f9;
	color: #475569;
	box-shadow: 0 0 0 1px #cbd5e1 inset;
}
.rank-3 {
	background: #ffedd5;
	color: #c2410c;
	box-shadow: 0 0 0 1px #fdba74 inset;
}

/* ---- Toasts (only these animate in; the old rule animated every div on the page) ---- */
.toast-enter-active,
.toast-leave-active {
	transition: opacity 0.2s ease, transform 0.2s ease;
}
.toast-enter-from,
.toast-leave-to {
	opacity: 0;
	transform: translateY(8px);
}

/* ---- Scrollbars ---- */
.custom-scrollbar::-webkit-scrollbar,
:deep(*::-webkit-scrollbar) {
	height: 5px !important;
	width: 5px !important;
}
.custom-scrollbar::-webkit-scrollbar-thumb,
:deep(*::-webkit-scrollbar-thumb) {
	background: var(--outline-gray-3, #cbd5e1) !important;
	border-radius: 10px !important;
}
.custom-scrollbar::-webkit-scrollbar-track {
	background: transparent !important;
}

:global([data-radix-popper-content-wrapper]), :global([data-reka-popper-content-wrapper]), :global(.PopoverContent) { z-index: 100005 !important; }
</style>