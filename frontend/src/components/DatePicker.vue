<template>
  <div :class="['date-picker-root flex flex-col space-y-1.5', $attrs.class]" :style="$attrs.style">
    <!-- Form Label -->
    <label
      v-if="computedLabel"
      :for="inputId"
      :class="[
        'block text-xs font-normal text-ink-gray-5 dark:text-slate-400 select-none',
        size === 'lg' ? 'text-sm' : 'text-xs'
      ]"
    >
      {{ computedLabel }}
      <span v-if="isRequired" class="text-ink-red-3 dark:text-red-400 ml-0.5" aria-hidden="true">*</span>
    </label>

    <!-- Popover Anchor / Trigger -->
    <Popover
      ref="popoverRef"
      :placement="placement"
      :disabled="disabled"
      class="w-full"
      @open="onPopoverOpen"
      @close="onPopoverClose"
    >
      <template #target="{ togglePopover, isOpen }">
        <div
          class="group relative flex items-center w-full transition-all duration-150"
          :class="[
            disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'
          ]"
        >
          <!-- Prefix Calendar Icon -->
          <div
            class="absolute left-0 inset-y-0 flex items-center pointer-events-none text-slate-400 dark:text-slate-400 group-hover:text-blue-500 transition-colors"
            :class="iconPaddingClasses.prefix"
          >
            <slot name="prefix">
              <IconCalendar class="w-3.5 h-3.5 shrink-0" />
            </slot>
          </div>

          <!-- Input Field -->
          <input
            :id="inputId"
            ref="inputRef"
            type="text"
            :value="inputValue"
            :placeholder="placeholder"
            :disabled="disabled"
            :readonly="readonly"
            :class="[
              inputClasses,
              iconPaddingClasses.input,
              error ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''
            ]"
            @focus="handleInputFocus(isOpen, togglePopover)"
            @click="handleInputClick(isOpen, togglePopover)"
            @input="handleTextInput"
            @blur="handleInputBlur"
            @keydown.enter.prevent="handleInputEnter(togglePopover)"
            @keydown.down.prevent="!isOpen && togglePopover()"
            @keydown.esc.prevent="isOpen && togglePopover()"
          />

          <!-- Suffix Action: Clear Button or Dropdown Chevron -->
          <div
            class="absolute right-0 inset-y-0 flex items-center gap-1 text-slate-400 dark:text-slate-500"
            :class="iconPaddingClasses.suffix"
          >
            <!-- Clear Button -->
            <button
              v-if="clearable && modelValue && !disabled && !readonly"
              type="button"
              class="p-0.5 rounded hover:bg-slate-200 dark:hover:bg-slate-700 hover:text-slate-700 dark:hover:text-slate-200 transition-colors cursor-pointer"
              title="Clear date"
              @click.stop="clearDate(togglePopover)"
              @mousedown.stop
            >
              <IconX class="w-3.5 h-3.5" />
            </button>

            <!-- Popover Toggle Chevron Icon -->
            <button
              v-else
              type="button"
              :disabled="disabled"
              tabindex="-1"
              class="p-0.5 rounded text-slate-400 group-hover:text-slate-600 dark:text-slate-500 dark:group-hover:text-slate-300 transition-transform duration-200 cursor-pointer"
              :class="{ 'rotate-180 text-blue-600 dark:text-blue-400': isOpen }"
              @click.stop="togglePopover"
            >
              <IconChevronDown class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </template>

      <!-- Popover Calendar Card Content -->
      <template #body="{ togglePopover }">
        <div
          ref="dropdownCardRef"
          class="date-picker-card bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 rounded-xl shadow-lg border border-slate-200/90 dark:border-slate-800 p-3 w-[280px] select-none transition-all animate-in fade-in zoom-in-95 duration-100"
          @mousedown.stop
        >
          <!-- Compact Quick Presets (Today, Tomorrow) -->
          <div
            v-if="showPresets && presets.length > 0"
            class="flex items-center gap-1.5 pb-2.5 mb-2.5 border-b border-slate-100 dark:border-slate-800"
          >
            <button
              v-for="preset in presets"
              :key="preset.label"
              type="button"
              :class="[
                'flex-1 text-center py-1 px-2 rounded-md text-xs font-medium transition-colors cursor-pointer border',
                isPresetActive(preset)
                  ? 'bg-blue-600 text-white border-blue-600 shadow-xs'
                  : 'bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-300 border-slate-200/60 dark:border-slate-700/60 hover:bg-slate-100 dark:hover:bg-slate-700'
              ]"
              @click="selectPreset(preset, togglePopover)"
            >
              {{ preset.label }}
            </button>
          </div>

          <!-- Calendar Header: Navigation & Month/Year Switcher -->
          <div class="flex items-center justify-between mb-2">
            <!-- Previous Button -->
            <button
              type="button"
              class="p-1 rounded-md text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
              :title="viewMode === 'year' ? 'Previous 12 Years' : viewMode === 'month' ? 'Previous Year' : 'Previous Month'"
              @click="navigatePrev"
            >
              <IconChevronLeft class="w-4 h-4" />
            </button>

            <!-- Center: Interactive View Mode Switcher Button -->
            <button
              type="button"
              class="px-2 py-1 rounded-md text-xs font-semibold text-slate-800 dark:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors flex items-center gap-1 cursor-pointer"
              @click="cycleViewMode"
            >
              <span v-if="viewMode === 'date'">
                {{ monthNames[currentMonth] }} {{ currentYear }}
              </span>
              <span v-else-if="viewMode === 'month'">
                {{ currentYear }}
              </span>
              <span v-else>
                {{ yearRangeStart }} - {{ yearRangeStart + 11 }}
              </span>
              <IconChevronDown
                class="w-3 h-3 text-slate-400 transition-transform duration-200"
                :class="{ 'rotate-180': viewMode !== 'date' }"
              />
            </button>

            <!-- Next Button -->
            <button
              type="button"
              class="p-1 rounded-md text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
              :title="viewMode === 'year' ? 'Next 12 Years' : viewMode === 'month' ? 'Next Year' : 'Next Month'"
              @click="navigateNext"
            >
              <IconChevronRight class="w-4 h-4" />
            </button>
          </div>

          <!-- 1. DATE VIEW (Calendar Grid) -->
          <div v-if="viewMode === 'date'" class="space-y-1">
            <!-- Weekday Header Row -->
            <div class="grid grid-cols-7 gap-1 text-center">
              <span
                v-for="(dayName, idx) in weekdayNames"
                :key="idx"
                class="text-[11px] font-medium text-slate-400 dark:text-slate-500 py-0.5"
              >
                {{ dayName }}
              </span>
            </div>

            <!-- Calendar Days (6x7 Grid) -->
            <div class="grid grid-cols-7 gap-1" role="grid">
              <button
                v-for="cell in calendarDays"
                :key="cell.key"
                type="button"
                :disabled="cell.isDisabled"
                :class="[
                  'h-8 w-8 mx-auto flex items-center justify-center text-xs rounded-md transition-colors cursor-pointer relative',
                  cell.isDisabled ? 'opacity-25 cursor-not-allowed pointer-events-none' : '',
                  cell.isSelected
                    ? 'bg-blue-600 text-white font-medium shadow-xs hover:bg-blue-700'
                    : cell.isToday
                    ? 'font-semibold text-blue-600 dark:text-blue-400 border border-blue-500/50 bg-blue-50/50 dark:bg-blue-950/20 hover:bg-blue-100/50'
                    : cell.inCurrentMonth
                    ? 'text-slate-700 dark:text-slate-200 font-normal hover:bg-slate-100 dark:hover:bg-slate-800'
                    : 'text-slate-300 dark:text-slate-600 hover:text-slate-500 dark:hover:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/40'
                ]"
                @click="selectDate(cell.date, togglePopover)"
              >
                {{ cell.dayNumber }}
              </button>
            </div>
          </div>

          <!-- 2. MONTH SELECTOR GRID VIEW -->
          <div v-else-if="viewMode === 'month'" class="grid grid-cols-3 gap-1.5 py-1">
            <button
              v-for="(monthName, index) in monthNames"
              :key="monthName"
              type="button"
              :class="[
                'py-2 px-1 text-xs font-medium rounded-md text-center transition-colors cursor-pointer',
                index === currentMonth
                  ? 'bg-blue-600 text-white shadow-xs font-semibold'
                  : isCurrentActualMonth(index)
                  ? 'border border-blue-500/50 text-blue-600 dark:text-blue-400 font-semibold hover:bg-blue-50 dark:hover:bg-slate-800'
                  : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
              ]"
              @click="selectMonth(index)"
            >
              {{ monthName }}
            </button>
          </div>

          <!-- 3. YEAR SELECTOR GRID VIEW -->
          <div v-else-if="viewMode === 'year'" class="grid grid-cols-3 gap-1.5 py-1">
            <button
              v-for="year in yearRange"
              :key="year"
              type="button"
              :class="[
                'py-2 px-1 text-xs font-medium rounded-md text-center transition-colors cursor-pointer',
                year === currentYear
                  ? 'bg-blue-600 text-white shadow-xs font-semibold'
                  : year === dayjs().year()
                  ? 'border border-blue-500/50 text-blue-600 dark:text-blue-400 font-semibold hover:bg-blue-50 dark:hover:bg-slate-800'
                  : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
              ]"
              @click="selectYear(year)"
            >
              {{ year }}
            </button>
          </div>

          <!-- Minimal Footer: Clear Action -->
          <div
            v-if="clearable && modelValue"
            class="flex items-center justify-between pt-2 mt-2 border-t border-slate-100 dark:border-slate-800 text-xs"
          >
            <button
              type="button"
              class="text-xs text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 transition-colors cursor-pointer font-medium"
              @click="jumpToToday(togglePopover)"
            >
              Today
            </button>
            <button
              type="button"
              class="text-xs text-slate-400 hover:text-red-500 dark:text-slate-500 dark:hover:text-red-400 transition-colors cursor-pointer font-medium"
              @click="clearDate(togglePopover)"
            >
              Clear
            </button>
          </div>
        </div>
      </template>
    </Popover>

    <!-- Error Message -->
    <p v-if="error" class="text-xs text-red-500 font-medium mt-0.5">
      {{ error }}
    </p>

    <!-- Description / Helper text -->
    <p v-else-if="description" class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
      {{ description }}
    </p>
  </div>
</template>

<script setup>
import dayjs from "dayjs"
import customParseFormat from "dayjs/plugin/customParseFormat"
import { Popover } from "frappe-ui"
import { computed, ref, watch } from "vue"

// Lucide Icons
import IconCalendar from "~icons/lucide/calendar"
import IconChevronDown from "~icons/lucide/chevron-down"
import IconChevronLeft from "~icons/lucide/chevron-left"
import IconChevronRight from "~icons/lucide/chevron-right"
import IconX from "~icons/lucide/x"

dayjs.extend(customParseFormat)

defineOptions({
	inheritAttrs: false,
})

const props = defineProps({
	modelValue: { type: [String, Number, Date], default: "" },
	value: { type: [String, Number, Date], default: "" },
	label: { type: String, default: "" },
	placeholder: { type: String, default: "Select date" },
	required: { type: Boolean, default: false },
	disabled: { type: Boolean, default: false },
	readonly: { type: Boolean, default: false },
	clearable: { type: Boolean, default: true },
	autoClose: { type: Boolean, default: true },
	format: { type: String, default: "MMM D, YYYY" },
	valueFormat: { type: String, default: "YYYY-MM-DD" },
	minDate: { type: [String, Date, Object], default: null },
	maxDate: { type: [String, Date, Object], default: null },
	size: { type: String, default: "sm" },
	variant: { type: String, default: "subtle" },
	placement: { type: String, default: "bottom-start" },
	error: { type: String, default: "" },
	description: { type: String, default: "" },
	showPresets: { type: Boolean, default: true },
	presets: {
		type: Array,
		default: () => [
			{ label: "Today", getValue: () => dayjs() },
			{ label: "Tomorrow", getValue: () => dayjs().add(1, "day") },
		],
	},
})

const emit = defineEmits([
	"update:modelValue",
	"change",
	"clear",
	"open",
	"close",
])

// Generate unique id for form input
const inputId = `datepicker_${Math.random().toString(36).substr(2, 9)}`
const inputRef = ref(null)
const popoverRef = ref(null)
const dropdownCardRef = ref(null)

// Current raw value from props
const rawValue = computed(() => props.modelValue || props.value || "")

// Label & Required parsing
const computedLabel = computed(() => {
	if (!props.label) return ""
	return props.label.endsWith("*")
		? props.label.slice(0, -1).trim()
		: props.label
})

const isRequired = computed(() => {
	return props.required || (props.label ? props.label.endsWith("*") : false)
})

// View Modes: 'date' | 'month' | 'year'
const viewMode = ref("date")

// Internal navigation state for month & year
const currentYear = ref(dayjs().year())
const currentMonth = ref(dayjs().month()) // 0 to 11

// Constants
const weekdayNames = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
const monthNames = [
	"Jan",
	"Feb",
	"Mar",
	"Apr",
	"May",
	"Jun",
	"Jul",
	"Aug",
	"Sep",
	"Oct",
	"Nov",
	"Dec",
]

// Text input synchronization & manual typing
const inputValue = ref("")
const isTyping = ref(false)

// Coerce input string to Dayjs object
function parseDate(val) {
	if (!val) return null
	const s = String(val).trim()
	if (!s) return null

	// Try standard emitted format
	const dStandard = dayjs(s, props.valueFormat, true)
	if (dStandard.isValid()) return dStandard

	// Try display format
	if (props.format) {
		const dFormat = dayjs(s, props.format, true)
		if (dFormat.isValid()) return dFormat
	}

	// Common international formats
	const commonFormats = [
		"YYYY-MM-DD",
		"YYYY/MM/DD",
		"DD-MM-YYYY",
		"DD/MM/YYYY",
		"MM/DD/YYYY",
		"MM-DD-YYYY",
		"MMM D, YYYY",
		"MMMM D, YYYY",
		"D MMM YYYY",
		"D MMMM YYYY",
	]
	for (const fmt of commonFormats) {
		const dFmt = dayjs(s, fmt, true)
		if (dFmt.isValid()) return dFmt
	}

	// Natural language parsing helpers
	const lower = s.toLowerCase()
	if (lower === "today") return dayjs()
	if (lower === "tomorrow") return dayjs().add(1, "day")
	if (lower === "yesterday") return dayjs().subtract(1, "day")

	// Loose fallback
	const dLoose = dayjs(s)
	if (dLoose.isValid()) return dLoose

	return null
}

function formatDateForDisplay(d) {
	if (!d || !d.isValid()) return ""
	return d.format(props.format)
}

function syncFromProps() {
	const parsed = parseDate(rawValue.value)
	if (parsed && parsed.isValid()) {
		currentYear.value = parsed.year()
		currentMonth.value = parsed.month()
		if (!isTyping.value) {
			inputValue.value = formatDateForDisplay(parsed)
		}
	} else {
		const today = dayjs()
		currentYear.value = today.year()
		currentMonth.value = today.month()
		if (!isTyping.value) {
			inputValue.value = rawValue.value ? String(rawValue.value) : ""
		}
	}
}

// Watch prop changes
watch(
	() => [props.modelValue, props.value],
	() => {
		syncFromProps()
	},
	{ immediate: true },
)

// Calendar Month Grid Generation (6 weeks = 42 cells)
const calendarDays = computed(() => {
	const days = []
	const firstDayOfMonth = dayjs()
		.year(currentYear.value)
		.month(currentMonth.value)
		.date(1)
	const startDayOfWeek = firstDayOfMonth.day() // 0 (Sun) to 6 (Sat)
	const selectedDayjs = parseDate(rawValue.value)
	const today = dayjs()

	// Start grid from the preceding Sunday
	const startDate = firstDayOfMonth.subtract(startDayOfWeek, "day")

	const minD = props.minDate ? parseDate(String(props.minDate)) : null
	const maxD = props.maxDate ? parseDate(String(props.maxDate)) : null

	for (let i = 0; i < 42; i++) {
		const dateObj = startDate.add(i, "day")
		const inCurrentMonth = dateObj.month() === currentMonth.value
		const isToday = dateObj.isSame(today, "day")
		const isSelected = selectedDayjs
			? dateObj.isSame(selectedDayjs, "day")
			: false

		let isDisabled = false
		if (minD && dateObj.isBefore(minD, "day")) isDisabled = true
		if (maxD && dateObj.isAfter(maxD, "day")) isDisabled = true

		days.push({
			key: dateObj.format("YYYY-MM-DD"),
			dayNumber: dateObj.date(),
			date: dateObj,
			inCurrentMonth,
			isToday,
			isSelected,
			isDisabled,
		})
	}

	return days
})

// Year Range for 12-Year Grid
const yearRangeStart = computed(() => {
	return currentYear.value - (currentYear.value % 12)
})

const yearRange = computed(() => {
	return Array.from({ length: 12 }, (_, i) => yearRangeStart.value + i)
})

function isCurrentActualMonth(monthIndex) {
	return currentYear.value === dayjs().year() && monthIndex === dayjs().month()
}

// Presets Check
function isPresetActive(preset) {
	if (!rawValue.value) return false
	const target = preset.getValue()
	const d = typeof target === "string" ? parseDate(target) : target
	const selected = parseDate(rawValue.value)
	if (!d || !selected) return false
	return d.isSame(selected, "day")
}

function selectPreset(preset, togglePopover) {
	const target = preset.getValue()
	const d = typeof target === "string" ? parseDate(target) : target
	if (d && d.isValid()) {
		commitDate(d)
		if (props.autoClose) togglePopover()
	}
}

// View Navigation Handlers
function cycleViewMode() {
	if (viewMode.value === "date") viewMode.value = "month"
	else if (viewMode.value === "month") viewMode.value = "year"
	else viewMode.value = "date"
}

function navigatePrev() {
	if (viewMode.value === "date") {
		if (currentMonth.value === 0) {
			currentMonth.value = 11
			currentYear.value -= 1
		} else {
			currentMonth.value -= 1
		}
	} else if (viewMode.value === "month") {
		currentYear.value -= 1
	} else {
		currentYear.value -= 12
	}
}

function navigateNext() {
	if (viewMode.value === "date") {
		if (currentMonth.value === 11) {
			currentMonth.value = 0
			currentYear.value += 1
		} else {
			currentMonth.value += 1
		}
	} else if (viewMode.value === "month") {
		currentYear.value += 1
	} else {
		currentYear.value += 12
	}
}

function selectMonth(monthIndex) {
	currentMonth.value = monthIndex
	viewMode.value = "date"
}

function selectYear(year) {
	currentYear.value = year
	viewMode.value = "month"
}

// Date selection & committing
function commitDate(d) {
	currentYear.value = d.year()
	currentMonth.value = d.month()
	const formattedVal = d.format(props.valueFormat)
	inputValue.value = formatDateForDisplay(d)
	isTyping.value = false

	emit("update:modelValue", formattedVal)
	emit("change", formattedVal)
}

function selectDate(date, togglePopover) {
	commitDate(date)
	if (props.autoClose) {
		togglePopover()
	}
}

function jumpToToday(togglePopover) {
	const today = dayjs()
	selectDate(today, togglePopover)
}

function clearDate(togglePopover) {
	inputValue.value = ""
	isTyping.value = false
	emit("update:modelValue", "")
	emit("change", "")
	emit("clear")
	if (togglePopover && props.autoClose) {
		togglePopover()
	}
}

// User input typing & blur handlers
function handleInputFocus(isOpen, togglePopover) {
	isTyping.value = true
	if (!isOpen && !props.disabled && !props.readonly) {
		togglePopover()
	}
}

function handleInputClick(isOpen, togglePopover) {
	if (!isOpen && !props.disabled && !props.readonly) {
		togglePopover()
	}
}

function handleTextInput(e) {
	inputValue.value = e.target.value
	isTyping.value = true
}

function handleInputBlur(e) {
	const nextTarget = e?.relatedTarget
	if (nextTarget && dropdownCardRef.value?.contains(nextTarget)) {
		return
	}

	isTyping.value = false
	const raw = inputValue.value.trim()
	if (!raw) {
		if (props.clearable) {
			clearDate()
		} else {
			syncFromProps()
		}
		return
	}

	const parsed = parseDate(raw)
	if (parsed && parsed.isValid()) {
		commitDate(parsed)
	} else {
		// Revert to valid prop value if invalid text entered
		syncFromProps()
	}
}

function handleInputEnter(togglePopover) {
	isTyping.value = false
	const raw = inputValue.value.trim()
	if (!raw) {
		if (props.clearable) {
			clearDate(togglePopover)
		}
		return
	}

	const parsed = parseDate(raw)
	if (parsed && parsed.isValid()) {
		commitDate(parsed)
		if (props.autoClose) togglePopover()
	} else {
		syncFromProps()
	}
}

function onPopoverOpen() {
	viewMode.value = "date"
	syncFromProps()
	emit("open")
}

function onPopoverClose() {
	viewMode.value = "date"
	if (isTyping.value) {
		handleInputBlur()
	}
	emit("close")
}

// Classes and styling
const inputClasses = computed(() => {
	const sizeClasses =
		{
			sm: "text-xs rounded h-7",
			md: "text-sm rounded-md h-8",
			lg: "text-base rounded-lg h-10",
		}[props.size] || "text-xs rounded h-7"

	const variantClasses =
		{
			subtle:
				"border border-transparent bg-surface-gray-2 dark:bg-slate-800 text-ink-gray-8 dark:text-slate-100 placeholder-ink-gray-4 dark:placeholder-slate-500 hover:bg-surface-gray-3 dark:hover:bg-slate-700/70 focus:bg-surface-white dark:focus:bg-slate-900 focus:border-outline-gray-4 dark:focus:border-slate-600 focus:ring-2 focus:ring-outline-gray-3/20 dark:focus:ring-slate-700 focus:outline-none",
			outline:
				"border border-outline-gray-2 dark:border-slate-700 bg-white dark:bg-slate-900 text-ink-gray-8 dark:text-slate-100 placeholder-ink-gray-4 dark:placeholder-slate-500 hover:border-outline-gray-3 dark:hover:border-slate-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none",
			ghost:
				"border-transparent bg-transparent text-ink-gray-8 dark:text-slate-100 placeholder-ink-gray-4 dark:placeholder-slate-500 hover:bg-surface-gray-2 dark:hover:bg-slate-800 focus:bg-surface-white dark:focus:bg-slate-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none",
		}[props.variant] ||
		"border border-transparent bg-surface-gray-2 dark:bg-slate-800 text-ink-gray-8 dark:text-slate-100 placeholder-ink-gray-4 dark:placeholder-slate-500 hover:bg-surface-gray-3 dark:hover:bg-slate-700/70 focus:bg-surface-white dark:focus:bg-slate-900 focus:border-outline-gray-4 dark:focus:border-slate-600 focus:ring-2 focus:ring-outline-gray-3/20 dark:focus:ring-slate-700 focus:outline-none"

	return [sizeClasses, variantClasses, "w-full transition-all font-normal"]
})

const iconPaddingClasses = computed(() => {
	return (
		{
			sm: {
				prefix: "pl-2",
				suffix: "pr-2",
				input: "pl-7 pr-8",
			},
			md: {
				prefix: "pl-2.5",
				suffix: "pr-2.5",
				input: "pl-8 pr-9",
			},
			lg: {
				prefix: "pl-3",
				suffix: "pr-3",
				input: "pl-9 pr-10",
			},
		}[props.size] || {
			prefix: "pl-2",
			suffix: "pr-2",
			input: "pl-7 pr-8",
		}
	)
})

defineExpose({
	inputRef,
	clear: clearDate,
	jumpToToday,
})
</script>

<style scoped>
.date-picker-card {
  user-select: none;
}
</style>
