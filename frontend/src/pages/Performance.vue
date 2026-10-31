<template>
  <div class="flex h-full min-h-0 flex-col overflow-hidden">
    <!-- Header + filters -->
    <div class="toolbar-card mx-1 mt-1 flex flex-shrink-0 flex-col gap-2.5">
      <div class="flex w-full flex-col justify-between gap-2.5 border-b border-outline-gray-1 pb-2.5 sm:flex-row sm:items-center">
        <div class="flex items-center gap-3">
          <span class="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-[color:var(--brand-soft,#E9F6FF)] text-[color:var(--brand-text,#0A84D0)]">
            <IconTrendingUp class="h-5 w-5" />
          </span>
          <div>
            <h1 class="text-base font-semibold leading-tight text-ink-gray-9">Performance</h1>
            <p class="text-xs text-ink-gray-5">
              {{ timespanLabel }}<template v-if="selectedEmployee"> · {{ getFilterLabel('selectedEmployee', selectedEmployee, '') }}</template>
            </p>
          </div>
        </div>

        <div class="ml-auto flex flex-wrap items-center justify-end gap-2 sm:ml-0">
          <!-- Filter popover -->
          <Popover placement="bottom-end">
            <template #target="{ togglePopover }">
              <Button
                variant="outline"
                :class="[
                  '!h-8 !px-2.5 text-xs font-medium',
                  activeFilterCount > 0 && '!border-[color:var(--brand,#29ADFF)] !bg-[color:var(--brand-soft,#E9F6FF)] !text-[color:var(--brand-text,#0A84D0)]',
                ]"
                title="Filter performance"
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
                  <span class="font-semibold text-ink-gray-8">Filter performance</span>
                  <button
                    v-if="hasActiveFilters"
                    type="button"
                    class="flex items-center gap-1 text-[11px] font-medium text-red-600 hover:text-red-700"
                    @click="resetFilters"
                  >
                    <IconX class="h-3 w-3" /> Reset
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

          <Button variant="outline" class="!h-8 !px-2.5" title="Refresh metrics" @click="fetchPerformance">
            <template #prefix><IconRefresh class="h-3.5 w-3.5" :class="performanceResource.loading && 'animate-spin'" /></template>
          </Button>
        </div>
      </div>

      <!-- Quick filters -->
      <div class="custom-scrollbar flex w-full flex-nowrap gap-2 overflow-x-auto pb-1 sm:flex-wrap sm:items-center sm:overflow-visible sm:pb-0">
        <!-- Timespan as segmented pills (the most-used filter) -->
        <div class="seg" role="tablist" aria-label="Timespan">
          <button
            v-for="t in QUICK_TIMESPANS"
            :key="t.value"
            type="button"
            role="tab"
            :aria-selected="selectedTimespan === t.value"
            :class="selectedTimespan === t.value && 'on'"
            @click="selectedTimespan = t.value"
          >
            {{ t.label }}
          </button>
        </div>

        <div class="w-36 shrink-0">
          <Autocomplete
            ref="timespanAutocomplete"
            :options="timespanOptions"
            :modelValue="selectedTimespan"
            @update:modelValue="val => selectedTimespan = (val && typeof val === 'object') ? (val.value ?? DEFAULT_TIMESPAN) : (val ?? DEFAULT_TIMESPAN)"
          >
            <template #target>
              <button
                type="button"
                :class="['qf', !isQuickTimespan && 'on']"
                @click="() => timespanAutocomplete?.togglePopover()"
              >
                <IconCalendar class="h-3.5 w-3.5 shrink-0 opacity-70" />
                <span class="flex-1 truncate text-left">{{ isQuickTimespan ? 'More…' : timespanLabel }}</span>
                <FeatherIcon name="chevron-down" class="size-3.5 shrink-0 opacity-60" />
              </button>
            </template>
          </Autocomplete>
        </div>

        <div v-if="employeeInfoResource.data?.is_system_manager" class="w-44 shrink-0">
          <Autocomplete
            ref="employeeAutocomplete"
            :options="employeeOptions"
            :modelValue="selectedEmployee"
            :max-options="100"
            @update:modelValue="val => selectedEmployee = (val && typeof val === 'object') ? (val.value ?? '') : (val ?? '')"
          >
            <template #target>
              <button type="button" :class="['qf', selectedEmployee !== '' && 'on']" @click="() => employeeAutocomplete?.togglePopover()">
                <IconUser class="h-3.5 w-3.5 shrink-0 opacity-70" />
                <span class="flex-1 truncate text-left">{{ getFilterLabel('selectedEmployee', selectedEmployee, 'All employees') }}</span>
                <FeatherIcon name="chevron-down" class="size-3.5 shrink-0 opacity-60" />
              </button>
            </template>
          </Autocomplete>
        </div>

        <button
          v-if="hasActiveFilters"
          type="button"
          class="inline-flex h-7 shrink-0 items-center gap-1 rounded-md px-2 text-xs font-medium text-red-500 hover:bg-red-50"
          @click="resetFilters"
        >
          <IconX class="h-3.5 w-3.5" /> Reset
        </button>
      </div>
    </div>

    <!-- Dashboard -->
    <div class="custom-scrollbar relative mt-2 min-h-0 flex-1 space-y-3 overflow-y-auto px-1 pb-3">
      <div v-if="performanceResource.loading && hasData" class="busy-bar" aria-hidden="true"></div>

      <!-- Error -->
      <div
        v-if="performanceResource.error && !performanceResource.loading"
        class="flex items-center justify-between gap-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700"
      >
        <span class="flex items-center gap-2"><IconAlertCircle class="h-4 w-4 shrink-0" />Couldn't load performance data. {{ errorText }}</span>
        <button type="button" class="font-semibold underline hover:no-underline" @click="fetchPerformance">Try again</button>
      </div>

      <!-- KPI cards -->
      <div class="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-5" :class="performanceResource.loading && hasData && 'opacity-60 transition-opacity'">
        <div v-for="k in kpiCards" :key="k.label" class="kpi">
          <div class="flex items-center justify-between gap-2">
            <span class="truncate text-xs font-medium text-ink-gray-6">{{ k.label }}</span>
            <span class="grid h-6 w-6 shrink-0 place-items-center rounded-md" :style="{ background: k.color + '1a', color: k.color }">
              <component :is="k.icon" class="h-3.5 w-3.5" />
            </span>
          </div>
          <div class="kpi-value">
            <div v-if="!hasData" class="skeleton h-6 w-16"></div>
            <template v-else>
              <span class="text-[24px] font-semibold leading-none tabular-nums text-ink-gray-9">{{ k.value }}</span>
              <span v-if="k.unit" class="text-xs font-medium text-ink-gray-5">{{ k.unit }}</span>
            </template>
          </div>
          <div class="mt-3">
            <div v-if="k.progress !== undefined" class="track">
              <div class="fill" :style="{ width: clamp(k.progress) + '%', background: k.color }"></div>
            </div>
            <div v-if="k.pill" class="mb-1">
              <span class="status-pill" :class="k.pill.cls">{{ k.pill.text }}</span>
            </div>
            <p class="mt-1.5 truncate text-[11px] text-ink-gray-5" :title="k.hint">{{ hasData ? k.hint : ' ' }}</p>
          </div>
        </div>
      </div>

      <!-- Trend + PR split -->
      <div class="grid grid-cols-1 gap-3 lg:grid-cols-3">
        <!-- Trend chart -->
        <div class="panel flex min-h-0 flex-col p-4 lg:col-span-2">
          <div class="flex flex-col justify-between gap-2 sm:flex-row sm:items-start">
            <div>
              <h2 class="panel-title">Activity trend</h2>
              <p class="text-xs text-ink-gray-5">Each line is scaled to its own peak so the shapes can be compared</p>
            </div>
            <div class="flex flex-wrap gap-1.5">
              <button
                v-for="s in SERIES"
                :key="s.key"
                type="button"
                class="legend-chip"
                :class="hiddenSeries[s.key] && 'is-off'"
                :title="(hiddenSeries[s.key] ? 'Show ' : 'Hide ') + s.label"
                @click="hiddenSeries[s.key] = !hiddenSeries[s.key]"
              >
                <span class="h-2 w-2 rounded-full" :style="{ background: s.color }"></span>{{ s.label }}
              </button>
            </div>
          </div>

          <div class="relative mt-3 min-h-[240px] flex-1">
            <div v-if="!hasData" class="skeleton absolute inset-0"></div>
            <div v-else-if="!pointsPrs.length" class="grid h-full min-h-[220px] place-items-center text-xs text-ink-gray-4">
              No activity in this period.
            </div>
            <template v-else>
              <div class="relative h-[220px]" @mouseleave="hoveredIndex = null">
                <svg :viewBox="`0 0 ${chartWidth} ${chartHeight}`" class="h-full w-full overflow-visible" preserveAspectRatio="none">
                  <defs>
                    <linearGradient v-for="s in SERIES" :id="'grad-' + s.key" :key="s.key" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" :stop-color="s.color" stop-opacity="0.16" />
                      <stop offset="100%" :stop-color="s.color" stop-opacity="0" />
                    </linearGradient>
                  </defs>

                  <g stroke-dasharray="3 3">
                    <line v-for="f in [0.25, 0.5, 0.75]" :key="f" x1="0" :y1="chartHeight * f" :x2="chartWidth" :y2="chartHeight * f" class="grid-line" vector-effect="non-scaling-stroke" />
                  </g>
                  <line x1="0" :y1="chartHeight - 0.5" :x2="chartWidth" :y2="chartHeight - 0.5" class="axis-line" vector-effect="non-scaling-stroke" />

                  <template v-for="s in SERIES" :key="s.key">
                    <g v-if="!hiddenSeries[s.key]">
                      <path :d="areaPaths[s.key]" :fill="`url(#grad-${s.key})`" />
                      <path
                        :d="linePaths[s.key]"
                        fill="none"
                        :stroke="s.color"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        vector-effect="non-scaling-stroke"
                      />
                    </g>
                  </template>

                  <line
                    v-if="hoveredIndex !== null"
                    :x1="pointsPrs[hoveredIndex]?.x || 0"
                    y1="0"
                    :x2="pointsPrs[hoveredIndex]?.x || 0"
                    :y2="chartHeight"
                    class="guide-line"
                    stroke-dasharray="3 3"
                    vector-effect="non-scaling-stroke"
                  />

                  <rect
                    v-for="(p, i) in pointsPrs"
                    :key="'hit-' + i"
                    :x="hitX(i)"
                    y="0"
                    :width="hitW"
                    :height="chartHeight"
                    fill="transparent"
                    class="cursor-crosshair"
                    @mouseenter="hoveredIndex = i"
                  />
                </svg>

                <!-- Hover dots (HTML so they stay round even though the SVG stretches) -->
                <template v-if="hoveredIndex !== null">
                  <span
                    v-for="s in visibleSeries"
                    :key="'dot-' + s.key"
                    class="dot"
                    :style="{
                      left: (seriesPoints[s.key][hoveredIndex]?.x / chartWidth) * 100 + '%',
                      top: (seriesPoints[s.key][hoveredIndex]?.y / chartHeight) * 100 + '%',
                      background: s.color,
                    }"
                  ></span>

                  <!-- Tooltip -->
                  <div class="chart-tip" :style="tipStyle">
                    <div class="mb-1 text-[11px] font-semibold text-ink-gray-8">{{ timeline.labels[hoveredIndex] }}</div>
                    <div v-for="s in visibleSeries" :key="'tip-' + s.key" class="flex items-center justify-between gap-4 text-[11px]">
                      <span class="flex items-center gap-1.5 text-ink-gray-6">
                        <span class="h-2 w-2 rounded-full" :style="{ background: s.color }"></span>{{ s.label }}
                      </span>
                      <span class="font-semibold tabular-nums text-ink-gray-9">{{ fmt(timeline[s.key][hoveredIndex]) }}{{ s.key === 'hours' ? ' h' : '' }}</span>
                    </div>
                  </div>
                </template>
              </div>

              <div class="mt-2 flex justify-between border-t border-outline-gray-1 pt-2 text-[10.5px] text-ink-gray-5">
                <span v-for="(l, i) in axisLabels" :key="i">{{ l }}</span>
              </div>
            </template>
          </div>
        </div>

        <!-- PR split -->
        <div class="panel flex flex-col p-4">
          <h2 class="panel-title flex items-center gap-1.5">Pull requests</h2>
          <p class="text-xs text-ink-gray-5">Merged, open and closed in this period</p>

          <div class="flex flex-1 items-center gap-5 py-4">
            <div class="relative h-32 w-32 shrink-0">
              <svg class="h-full w-full -rotate-90" viewBox="0 0 42 42">
                <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="var(--surface-gray-2, #f3f3f3)" stroke-width="4.5" />
                <circle
                  v-for="seg in prSegments"
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
                <span class="text-2xl font-semibold leading-none tabular-nums text-ink-gray-9">{{ gh.total_prs || 0 }}</span>
                <span class="mt-1 text-[10px] font-medium uppercase tracking-wider text-ink-gray-5">PRs</span>
              </div>
            </div>

            <ul class="flex-1 space-y-2.5">
              <li v-for="seg in PR_PARTS" :key="seg.key" class="flex items-center justify-between text-xs">
                <span class="flex items-center gap-2 text-ink-gray-7">
                  <span class="h-2.5 w-2.5 rounded-sm" :style="{ background: seg.color }"></span>{{ seg.label }}
                </span>
                <span class="tabular-nums text-ink-gray-5">
                  <b class="font-semibold text-ink-gray-9">{{ gh[seg.key] || 0 }}</b>
                  · {{ pctOfPrs(gh[seg.key]) }}%
                </span>
              </li>
            </ul>
          </div>

          <div class="grid grid-cols-2 gap-2 border-t border-outline-gray-1 pt-3 text-center">
            <div class="rounded-lg bg-surface-gray-1 p-2">
              <div class="text-[10.5px] font-medium uppercase tracking-wide text-ink-gray-5">Repositories</div>
              <div class="mt-0.5 text-base font-semibold tabular-nums text-ink-gray-9">{{ gh.repos_count || 0 }}</div>
            </div>
            <div class="rounded-lg bg-surface-gray-1 p-2">
              <div class="text-[10.5px] font-medium uppercase tracking-wide text-ink-gray-5">Review comments</div>
              <div class="mt-0.5 text-base font-semibold tabular-nums text-ink-gray-9">{{ gh.comments_count || 0 }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Hours by activity + SLA + tasks -->
      <div class="grid grid-cols-1 gap-3 lg:grid-cols-3">
        <div class="panel p-4 lg:col-span-2">
          <div class="flex items-start justify-between gap-2">
            <div>
              <h2 class="panel-title">Hours by activity</h2>
              <p class="text-xs text-ink-gray-5">Where logged time went, from timesheet entries</p>
            </div>
            <span v-if="hasData" class="rounded-full bg-surface-gray-2 px-2 py-0.5 text-xs font-semibold tabular-nums text-ink-gray-7">
              {{ fmt(ts.total_hours) }} hrs total
            </span>
          </div>

          <div class="mt-4 space-y-3.5">
            <div v-for="activity in resolvedActivities" :key="activity.name">
              <div class="flex items-center justify-between text-xs">
                <span class="flex items-center gap-2 font-medium text-ink-gray-7">
                  <span class="h-2 w-2 rounded-full" :style="{ background: activity.color }"></span>{{ activity.name }}
                </span>
                <span class="tabular-nums text-ink-gray-5">
                  <b class="font-semibold text-ink-gray-9">{{ fmt(activity.hours) }} hrs</b> · {{ activity.percentage }}%
                </span>
              </div>
              <div class="track mt-1.5">
                <div class="fill" :style="{ width: activity.percentage + '%', background: activity.color }"></div>
              </div>
            </div>
            <p v-if="hasData && resolvedActivities.length === 0" class="py-8 text-center text-xs text-ink-gray-4">
              No timesheet entries in this period.
            </p>
          </div>
        </div>

        <div class="space-y-3">
          <div class="panel p-4">
            <div class="flex items-center justify-between">
              <h2 class="panel-title">Ticket SLA</h2>
              <span class="status-pill" :class="sla.cls">{{ sla.text }}</span>
            </div>
            <dl class="mt-3 space-y-2.5 border-t border-outline-gray-1 pt-3 text-xs">
              <div class="flex justify-between">
                <dt class="text-ink-gray-5">Resolution rate</dt>
                <dd class="font-semibold tabular-nums text-ink-gray-9">{{ fmt(tk.resolution_rate) }}%</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-ink-gray-5">Avg first response</dt>
                <dd class="font-semibold tabular-nums text-ink-gray-9">{{ formatDuration(tk.avg_response_time) }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-ink-gray-5">Avg time to resolve</dt>
                <dd class="font-semibold tabular-nums text-ink-gray-9">{{ formatDuration(tk.avg_close_time) }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-ink-gray-5">Tickets</dt>
                <dd class="font-semibold tabular-nums text-ink-gray-9">{{ tk.total || 0 }}</dd>
              </div>
            </dl>
          </div>

          <div class="panel p-4">
            <h2 class="panel-title">Tasks</h2>
            <dl class="mt-3 space-y-2.5 border-t border-outline-gray-1 pt-3 text-xs">
              <div class="flex justify-between">
                <dt class="text-ink-gray-5">Assigned</dt>
                <dd class="font-semibold tabular-nums text-ink-gray-9">{{ tk_task.total || 0 }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-ink-gray-5">Completed</dt>
                <dd class="font-semibold tabular-nums text-green-600">{{ tk_task.completed || 0 }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-ink-gray-5">Overdue</dt>
                <dd class="font-semibold tabular-nums" :class="tk_task.overdue > 0 ? 'text-red-600' : 'text-ink-gray-9'">{{ tk_task.overdue || 0 }}</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
	Autocomplete,
	Badge,
	Button,
	Card,
	FeatherIcon,
	FormControl,
	Popover,
	Select,
	createResource,
} from "frappe-ui"
import { computed, reactive, ref, watch } from "vue"

import IconActivity from "~icons/lucide/activity"
import IconAlertCircle from "~icons/lucide/alert-circle"
import IconBriefcase from "~icons/lucide/briefcase"
import IconCalendar from "~icons/lucide/calendar"
import IconCheckSquare from "~icons/lucide/check-square"
import IconClock from "~icons/lucide/clock"
import IconFilter from "~icons/lucide/filter"
import IconGitPullRequest from "~icons/lucide/git-pull-request"
import IconPlus from "~icons/lucide/plus"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconShieldAlert from "~icons/lucide/shield-alert"
// Icons
import IconTrendingUp from "~icons/lucide/trending-up"
import IconUser from "~icons/lucide/user"
import IconX from "~icons/lucide/x"

// Filter values
const DEFAULT_TIMESPAN = "this_month"
const selectedTimespan = ref(DEFAULT_TIMESPAN)
const selectedEmployee = ref("")

// Filter options for Autocomplete dropdowns
const timespanOptions = [
	{ label: "All Time", value: "" },
	{ label: "Today", value: "today" },
	{ label: "Yesterday", value: "yesterday" },
	{ label: "This Week", value: "this_week" },
	{ label: "Last Week", value: "last_week" },
	{ label: "This Month", value: "this_month" },
	{ label: "Last Month", value: "last_month" },
	{ label: "This Year", value: "this_year" },
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

// Most-used timespans shown as one-click pills; the rest live under "More…"
const QUICK_TIMESPANS = [
	{ label: "This week", value: "this_week" },
	{ label: "This month", value: "this_month" },
	{ label: "Last month", value: "last_month" },
	{ label: "This year", value: "this_year" },
]
const isQuickTimespan = computed(() => QUICK_TIMESPANS.some((t) => t.value === selectedTimespan.value))
const timespanLabel = computed(
	() => timespanOptions.find((o) => o.value === selectedTimespan.value)?.label || "All Time",
)

// Popover refs for Autocomplete programmatic toggling
const timespanAutocomplete = ref(null)
const employeeAutocomplete = ref(null)

const FILTERABLE_FIELDS = computed(() => {
	const fields = [
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
			field: "selectedTimespan",
			value: "",
		})
	}
	activeFilterRules.value = newRules
}

function addFilterRule() {
	const unusedField = FILTERABLE_FIELDS.value.find(
		(f) => !activeFilterRules.value.some((r) => r.field === f.value),
	)
	const field = unusedField ? unusedField.value : "selectedTimespan"
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
		if (removed.field === "selectedTimespan") selectedTimespan.value = ""
		if (removed.field === "selectedEmployee") selectedEmployee.value = ""
	}
	if (activeFilterRules.value.length === 0) {
		activeFilterRules.value.push({
			id: "rule_" + Date.now(),
			field: "selectedTimespan",
			value: "",
		})
	}
}

function applyFilterRules() {
	FILTERABLE_FIELDS.value.forEach((f) => {
		const hasRule = activeFilterRules.value.some((r) => r.field === f.key)
		if (!hasRule) {
			if (f.key === "selectedTimespan") selectedTimespan.value = ""
			if (f.key === "selectedEmployee") selectedEmployee.value = ""
		}
	})
	activeFilterRules.value.forEach((r) => {
		if (r.field === "selectedTimespan") selectedTimespan.value = r.value
		if (r.field === "selectedEmployee") selectedEmployee.value = r.value
	})
}

function getFieldOptionsForSelect(fieldKey) {
	if (fieldKey === "selectedTimespan")
		return timespanOptions.filter((o) => o.value !== "")
	if (fieldKey === "selectedEmployee")
		return employeeOptions.value.filter((o) => o.value !== "")
	return []
}

function getFilterLabel(fieldKey, val, defaultText) {
	if (!val) return defaultText
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
	if (selectedTimespan.value !== DEFAULT_TIMESPAN) count++
	if (selectedEmployee.value) count++
	return count
})

const hasActiveFilters = computed(() => activeFilterCount.value > 0)

// back to the default view (this month, everyone) — previously this switched to "All Time"
function resetFilters() {
	selectedTimespan.value = DEFAULT_TIMESPAN
	selectedEmployee.value = ""
}

// API Resources
const employeeInfoResource = createResource({
	url: "tactix.api.timesheet.get_employee_info",
	initialData: {},
	auto: true,
})

const employeeOptionsResource = createResource({
	url: "tactix.api.timesheet.get_employees",
	initialData: [],
})

const performanceResource = createResource({
	url: "tactix.api.performance.get_performance_data",
	initialData: {},
})

// Trigger employee info loading options for admins
watch(
	() => employeeInfoResource.data,
	(val) => {
		if (val?.is_system_manager) {
			employeeOptionsResource.fetch()
		}
	},
	{ immediate: true },
)

// Main fetch performance logic
function fetchPerformance() {
	performanceResource.fetch({
		employee: selectedEmployee.value,
		timespan: selectedTimespan.value,
	})
}

// Watch filters
watch([selectedTimespan, selectedEmployee], () => {
	fetchPerformance()
})

// Initial fetch
fetchPerformance()

const performanceData = computed(() => performanceResource.data || {})

// true once real data has arrived (initialData is an empty object)
const hasData = computed(() => Object.keys(performanceData.value || {}).length > 0)

const errorText = computed(() => {
	const e = performanceResource.error
	if (!e) return ""
	return String(e.messages?.[0] || e.message || "").replace(/<[^>]*>/g, "")
})

const gh = computed(() => performanceData.value.github || {})
const ts = computed(() => performanceData.value.timesheet || {})
const tk = computed(() => performanceData.value.ticket || {})
const tk_task = computed(() => performanceData.value.task || {})

function num(v) {
	const n = Number(v)
	return Number.isFinite(n) ? n : 0
}
function fmt(v) {
	const n = num(v)
	return Number.isInteger(n) ? String(n) : n.toFixed(1)
}
function clamp(v) {
	return Math.max(0, Math.min(100, num(v)))
}

const DAILY_TARGET = 8

const kpiCards = computed(() => [
	{
		label: "Task completion",
		value: fmt(tk_task.value.completion_rate),
		unit: "%",
		icon: IconCheckSquare,
		color: "#29ADFF",
		progress: num(tk_task.value.completion_rate),
		hint: `${tk_task.value.completed || 0} of ${tk_task.value.total || 0} tasks completed`,
	},
	{
		label: "Avg first response",
		value: formatDuration(tk.value.avg_response_time),
		icon: IconClock,
		color: "#f59e0b",
		pill: sla.value,
		hint: `Based on ${tk.value.total || 0} tickets`,
	},
	{
		label: "Hours logged",
		value: fmt(ts.value.total_hours),
		unit: "hrs",
		icon: IconBriefcase,
		color: "#10b981",
		hint: `Across ${ts.value.active_days || 0} active days`,
	},
	{
		label: "Avg daily hours",
		value: fmt(ts.value.avg_daily_hours),
		unit: "hrs",
		icon: IconCalendar,
		color: "#f97316",
		progress: (num(ts.value.avg_daily_hours) / DAILY_TARGET) * 100,
		hint: `Target ${DAILY_TARGET} hrs a day`,
	},
	{
		label: "Pull requests",
		value: gh.value.total_prs || 0,
		icon: IconGitPullRequest,
		color: "#8250df",
		progress: num(gh.value.merged_rate),
		hint: `${Math.round(num(gh.value.merged_rate))}% merged`,
	},
])

const hoveredIndex = ref(null)

const chartWidth = 600
const chartHeight = 220

const timeline = computed(
	() =>
		performanceData.value?.timeline || {
			labels: [],
			prs: [],
			tasks: [],
			tickets: [],
			hours: [],
		},
)

const chartPointsFor = (metric) => {
	const vals = timeline.value[metric] || []
	const labels = timeline.value.labels
	if (!vals || vals.length === 0) return []
	const max = Math.max(...vals, 1)

	return vals.map((val, i) => {
		const x =
			labels.length > 1
				? (i / (labels.length - 1)) * chartWidth
				: chartWidth / 2
		const y = chartHeight - (val / max) * (chartHeight - 40) - 20
		return { x, y }
	})
}

const pointsPrs = computed(() => chartPointsFor("prs"))
const pointsTasks = computed(() => chartPointsFor("tasks"))
const pointsTickets = computed(() => chartPointsFor("tickets"))
const pointsHours = computed(() => chartPointsFor("hours"))

const pathFor = (points) => {
	if (points.length === 0) return ""
	return points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ")
}

const areaPathFor = (points) => {
	if (points.length === 0) return ""
	const path = pathFor(points)
	return `${path} L ${points[points.length - 1].x} ${chartHeight} L ${points[0].x} ${chartHeight} Z`
}

const linePathPrs = computed(() => pathFor(pointsPrs.value))
const linePathTasks = computed(() => pathFor(pointsTasks.value))
const linePathTickets = computed(() => pathFor(pointsTickets.value))
const linePathHours = computed(() => pathFor(pointsHours.value))

const areaPathPrs = computed(() => areaPathFor(pointsPrs.value))

const SERIES = [
	{ key: "prs", label: "PRs", color: "#8250df" },
	{ key: "tasks", label: "Tasks", color: "#29ADFF" },
	{ key: "tickets", label: "Tickets", color: "#f59e0b" },
	{ key: "hours", label: "Hours", color: "#10b981" },
]
const hiddenSeries = reactive({ prs: false, tasks: false, tickets: false, hours: false })
const visibleSeries = computed(() => SERIES.filter((s) => !hiddenSeries[s.key]))

const seriesPoints = computed(() => ({
	prs: pointsPrs.value,
	tasks: pointsTasks.value,
	tickets: pointsTickets.value,
	hours: pointsHours.value,
}))
const linePaths = computed(() => ({
	prs: linePathPrs.value,
	tasks: linePathTasks.value,
	tickets: linePathTickets.value,
	hours: linePathHours.value,
}))
const areaPaths = computed(() => ({
	prs: areaPathPrs.value,
	tasks: areaPathFor(pointsTasks.value),
	tickets: areaPathFor(pointsTickets.value),
	hours: areaPathFor(pointsHours.value),
}))

// hover columns centred on each point
const hitW = computed(() => {
	const n = pointsPrs.value.length
	return n > 1 ? chartWidth / (n - 1) : chartWidth
})
function hitX(i) {
	const n = pointsPrs.value.length
	if (n <= 1) return 0
	return Math.max(0, pointsPrs.value[i].x - hitW.value / 2)
}

// tooltip sits next to the hovered column, flipping to the left near the right edge
const tipStyle = computed(() => {
	if (hoveredIndex.value === null) return {}
	const x = (pointsPrs.value[hoveredIndex.value]?.x || 0) / chartWidth
	return x > 0.6
		? { right: (1 - x) * 100 + "%", marginRight: "12px", top: "8px" }
		: { left: x * 100 + "%", marginLeft: "12px", top: "8px" }
})

// up to 5 evenly spaced x-axis labels
const axisLabels = computed(() => {
	const l = timeline.value.labels || []
	if (l.length <= 5) return l
	const idx = [0, 0.25, 0.5, 0.75, 1].map((f) => Math.round(f * (l.length - 1)))
	return idx.map((i) => l[i])
})

const PR_PARTS = [
	{ key: "merged_prs", label: "Merged", color: "#8250df" },
	{ key: "open_prs", label: "Open", color: "#22c55e" },
	{ key: "closed_prs", label: "Closed", color: "#ef4444" },
]
function pctOfPrs(n) {
	const total = num(gh.value.total_prs)
	return total ? Math.round((num(n) / total) * 100) : 0
}
const prSegments = computed(() => {
	const total = Math.max(1, num(gh.value.total_prs))
	let offset = 0
	return PR_PARTS.map((p) => {
		const value = num(gh.value[p.key])
		const pct = (value / total) * 100
		const seg = { ...p, value, pct, offset }
		offset += pct
		return seg
	}).filter((s) => s.value > 0)
})

const sla = computed(() => {
	const s = num(tk.value.avg_response_time)
	if (!s) return { text: "No score yet", cls: "is-muted" }
	const hrs = s / 3600
	if (hrs < 2) return { text: "A+ · Elite", cls: "is-good" }
	if (hrs < 8) return { text: "A · Fast", cls: "is-good" }
	if (hrs < 24) return { text: "B · Compliant", cls: "is-brand" }
	return { text: "C · Warning", cls: "is-warn" }
})

// Format raw seconds into a friendly duration representation
function formatDuration(seconds) {
	if (!seconds || seconds <= 0) return "—"
	const sec = Number.parseFloat(seconds)
	if (sec < 60) {
		return `${Math.round(sec)} sec`
	}
	const min = sec / 60
	if (min < 60) {
		return `${Math.round(min)} min`
	}
	const hrs = min / 60
	if (hrs < 24) {
		return `${hrs.toFixed(1)} hrs`
	}
	const days = hrs / 24
	return `${days.toFixed(1)} days`
}

// SLA compliance color coding
function getSLARatingColor(seconds) {
	if (!seconds || seconds <= 0) return "gray"
	const hrs = seconds / 3600
	if (hrs < 2) return "green"
	if (hrs < 8) return "emerald"
	if (hrs < 24) return "blue"
	return "orange"
}

// SLA text labels
function getSLARatingText(seconds) {
	if (!seconds || seconds <= 0) return "No SLA Score"
	const hrs = seconds / 3600
	if (hrs < 2) return "Elite (SLA A+)"
	if (hrs < 8) return "Fast (SLA A)"
	if (hrs < 24) return "Compliant (SLA B)"
	return "Warning (SLA C)"
}

// Activity colours and percentages
const activityColors = {
	Execution: "#29ADFF",
	Planning: "#6366f1",
	Research: "#8250df",
	Communication: "#14b8a6",
	"Proposal Writing": "#f97316",
}

const resolvedActivities = computed(() => {
	const activities = ts.value.activities || {}
	const total = num(ts.value.total_hours)

	return Object.entries(activities)
		.map(([name, hours]) => ({
			name,
			hours: num(hours),
			percentage: total > 0 ? Math.round((num(hours) / total) * 100) : 0,
			color: activityColors[name] || "#94a3b8",
		}))
		.sort((a, b) => b.hours - a.hours)
})
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
.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink-gray-9, #171717);
}
.kpi {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
  padding: 12px 14px;
  border-radius: 10px;
}
.kpi-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  min-height: 30px;
  margin-top: 10px;
}

/* quick filters */
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
.seg {
  display: inline-flex;
  flex-shrink: 0;
  padding: 2px;
  border: 1px solid var(--outline-gray-2, #e2e2e2);
  border-radius: 7px;
  background: var(--surface-gray-2, #f3f3f3);
}
.seg button {
  height: 22px;
  padding: 0 10px;
  border-radius: 5px;
  color: var(--ink-gray-6, #6b6b6b);
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  transition: background-color 0.15s, color 0.15s;
}
.seg button:hover {
  color: var(--ink-gray-9, #171717);
}
.seg button.on {
  background: var(--surface-white, #fff);
  color: var(--brand-text, #0a84d0);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}

/* bars, pills */
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
.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 1px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  line-height: 18px;
  white-space: nowrap;
}
.status-pill.is-good { background: rgba(34, 197, 94, 0.12); color: #15803d; }
.status-pill.is-brand { background: var(--brand-soft, #e9f6ff); color: var(--brand-text, #0a84d0); }
.status-pill.is-warn { background: rgba(245, 158, 11, 0.14); color: #b45309; }
.status-pill.is-muted { background: var(--surface-gray-2, #f3f3f3); color: var(--ink-gray-5, #7c7c7c); }

/* chart */
.legend-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 24px;
  padding: 0 8px;
  border: 1px solid var(--outline-gray-2, #e2e2e2);
  border-radius: 999px;
  color: var(--ink-gray-7, #525252);
  font-size: 11.5px;
  font-weight: 500;
  transition: opacity 0.15s, background-color 0.15s;
}
.legend-chip:hover {
  background: var(--surface-gray-2, #f3f3f3);
}
.legend-chip.is-off {
  opacity: 0.45;
  text-decoration: line-through;
}
.grid-line {
  stroke: var(--outline-gray-1, #ededed);
  stroke-width: 1;
}
.axis-line {
  stroke: var(--outline-gray-2, #e2e2e2);
  stroke-width: 1;
}
.guide-line {
  stroke: var(--ink-gray-4, #a3a3a3);
  stroke-width: 1;
}
.dot {
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  box-shadow: 0 0 0 2px var(--surface-white, #fff);
  transform: translate(-50%, -50%);
  pointer-events: none;
}
.chart-tip {
  position: absolute;
  z-index: 5;
  min-width: 140px;
  padding: 8px 10px;
  border: 1px solid var(--outline-gray-2, #e2e2e2);
  border-radius: 8px;
  background: var(--surface-modal, #fff);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
  pointer-events: none;
}

/* loading */
.busy-bar {
  position: sticky;
  top: 0;
  z-index: 20;
  height: 2px;
  margin: 0 0 -2px;
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
  border-radius: 6px;
  background: var(--surface-gray-2, #f3f3f3);
  animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse {
  50% { opacity: 0.5; }
}

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
:deep(*::-webkit-scrollbar-track) {
  background: transparent !important;
}

:global([data-radix-popper-content-wrapper]), :global([data-reka-popper-content-wrapper]), :global(.PopoverContent) { z-index: 100005 !important; }
</style>