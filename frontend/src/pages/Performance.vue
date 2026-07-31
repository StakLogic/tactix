<template>
  <div class="flex flex-col h-full overflow-hidden font-sans min-h-0 bg-slate-50/50">
    <!-- Top Filter Header -->
    <div class="bg-white p-2 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3 mx-4 mt-2 flex-shrink-0">
      <div class="flex items-center gap-3">
        <div class="p-2.5 rounded-xl bg-blue-50 text-blue-600">
          <IconTrendingUp class="w-5 h-5" />
        </div>
        <div>
          <h1 class="text-base font-black text-slate-900 leading-tight">Performance Dashboard</h1>
          <p class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Analytics & SLA insights</p>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <!-- Timespan Selector -->
        <select 
          v-model="selectedTimespan"
          class="px-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-600 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 cursor-pointer min-w-[130px] hover:bg-slate-100/50 transition-all"
        >
          <option value="">All Time</option>
          <option value="today">Today</option>
          <option value="yesterday">Yesterday</option>
          <option value="this_week">This Week</option>
          <option value="last_week">Last Week</option>
          <option value="this_month">This Month</option>
          <option value="last_month">Last Month</option>
          <option value="this_year">This Year</option>
        </select>

        <!-- Employee Selector (Admin only) -->
        <select 
          v-if="employeeInfoResource.data?.is_system_manager"
          v-model="selectedEmployee"
          class="px-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-600 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 cursor-pointer min-w-[160px] hover:bg-slate-100/50 transition-all"
        >
          <option value="">All Employees</option>
          <option v-for="emp in employeeOptionsResource.data" :key="emp.value" :value="emp.value">
            {{ emp.label }}
          </option>
        </select>

        <Button
          variant="outline"
          class="!text-slate-600 !px-3 !h-8 border border-slate-200 hover:bg-slate-50 transition-all"
          @click="fetchPerformance"
        >
          <template #prefix><IconRefresh class="w-4 h-4 text-slate-500" /></template>
        </Button>
      </div>
    </div>

    <!-- Main Dashboard Scrollable Area -->
    <div class="flex-1 overflow-y-auto p-2 space-y-6 custom-scrollbar min-h-0">
      <!-- Loading Spinner -->
      <div v-if="performanceResource.loading" class="flex flex-col items-center justify-center py-20 space-y-3">
        <div class="w-10 h-10 border-4 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
        <p class="text-xs font-extrabold text-slate-400 uppercase tracking-widest">Aggregating Metrics...</p>
      </div>

      <template v-else-if="performanceData">
        <!-- KPI Metrics Grid (5 Column Layout) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2">
          <!-- Task Completion Rate Card -->
          <Card class="!shadow-sm bg-white border border-slate-100 p-2 flex flex-col justify-between hover:shadow-md hover:scale-[1.01] transition-all duration-300">
            <div>
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Task Completion</span>
                <div class="p-1.5 rounded-lg bg-blue-50 text-blue-500">
                  <IconCheckSquare class="w-4 h-4" />
                </div>
              </div>
              <div class="text-2xl font-black mt-2 text-slate-900 leading-none">
                {{ performanceData.task?.completion_rate?.toFixed(1) || '0.0' }}%
              </div>
            </div>
            <div class="mt-4">
              <div class="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                <div 
                  class="bg-blue-500 h-full rounded-full transition-all duration-500"
                  :style="{ width: `${performanceData.task?.completion_rate || 0}%` }"
                ></div>
              </div>
              <div class="text-[10px] text-slate-400 font-semibold mt-2">
                {{ performanceData.task?.completed || 0 }} of {{ performanceData.task?.total || 0 }} tasks completed
              </div>
            </div>
          </Card>

          <!-- Ticket SLA Response Card -->
          <Card class="!shadow-sm bg-white border border-slate-100 p-2 flex flex-col justify-between hover:shadow-md hover:scale-[1.01] transition-all duration-300">
            <div>
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Avg First Response</span>
                <div class="p-1.5 rounded-lg bg-indigo-50 text-indigo-500">
                  <IconClock class="w-4 h-4" />
                </div>
              </div>
              <div class="text-2xl font-black mt-2 text-slate-900 leading-none">
                {{ formatDuration(performanceData.ticket?.avg_response_time) }}
              </div>
            </div>
            <div class="mt-3.5">
              <Badge 
                :theme="getSLARatingColor(performanceData.ticket?.avg_response_time)" 
                variant="subtle" 
                class="font-black text-[9px] uppercase tracking-wide px-2 py-0.5"
              >
                {{ getSLARatingText(performanceData.ticket?.avg_response_time) }}
              </Badge>
              <div class="text-[10px] text-slate-400 font-semibold mt-2">
                Based on {{ performanceData.ticket?.total || 0 }} tickets
              </div>
            </div>
          </Card>

          <!-- Total Logged Hours Card -->
          <Card class="!shadow-sm bg-white border border-slate-100 p-2 flex flex-col justify-between hover:shadow-md hover:scale-[1.01] transition-all duration-300">
            <div>
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Logged Hours</span>
                <div class="p-1.5 rounded-lg bg-emerald-50 text-emerald-500">
                  <IconClock class="w-4 h-4" />
                </div>
              </div>
              <div class="text-2xl font-black mt-2 text-slate-900 leading-none">
                {{ performanceData.timesheet?.total_hours?.toFixed(1) || '0.0' }} hrs
              </div>
            </div>
            <div class="mt-4 text-[10px] text-slate-400 font-semibold">
              Across {{ performanceData.timesheet?.active_days || 0 }} active logging days
            </div>
          </Card>

          <!-- Avg Daily Logged Hours Card -->
          <Card class="!shadow-sm bg-white border border-slate-100 p-2 flex flex-col justify-between hover:shadow-md hover:scale-[1.01] transition-all duration-300">
            <div>
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Avg Daily Hours</span>
                <div class="p-1.5 rounded-lg bg-orange-50 text-orange-500">
                  <IconCalendar class="w-4 h-4" />
                </div>
              </div>
              <div class="text-2xl font-black mt-2 text-slate-900 leading-none">
                {{ performanceData.timesheet?.avg_daily_hours?.toFixed(1) || '0.0' }} hrs
              </div>
            </div>
            <div class="mt-4">
              <div class="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                <div 
                  class="bg-orange-500 h-full rounded-full transition-all duration-500"
                  :style="{ width: `${Math.min((performanceData.timesheet?.avg_daily_hours || 0) / 8 * 100, 100)}%` }"
                ></div>
              </div>
              <div class="text-[10px] text-slate-400 font-semibold mt-2">
                Compared to 8 hrs benchmark
              </div>
            </div>
          </Card>

          <!-- Pull Requests & Contributions Card (New!) -->
          <Card class="!shadow-sm bg-white border border-slate-100 p-2 flex flex-col justify-between hover:shadow-md hover:scale-[1.01] transition-all duration-300">
            <div>
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">PRs & Contributions</span>
                <div class="p-1.5 rounded-lg bg-purple-50 text-purple-500">
                  <IconGitPullRequest class="w-4 h-4" />
                </div>
              </div>
              <div class="text-2xl font-black mt-2 text-slate-900 leading-none">
                {{ performanceData.github?.total_prs || 0 }}
              </div>
            </div>
            <div class="mt-4">
              <div class="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                <div 
                  class="bg-purple-500 h-full rounded-full transition-all duration-500"
                  :style="{ width: `${performanceData.github?.merged_rate || 0}%` }"
                ></div>
              </div>
              <div class="text-[10px] text-slate-400 font-semibold mt-2">
                {{ performanceData.github?.merged_rate?.toFixed(0) || 0 }}% merged rate
              </div>
            </div>
          </Card>
        </div>

        <!-- Interactive SVG Trend Chart & Donut Allocation Section -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Trends Area Chart Card -->
          <Card class="!shadow-sm bg-white border border-slate-100 p-6 lg:col-span-2 space-y-4 flex flex-col min-h-0 hover:shadow-md transition-all duration-300">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <h2 class="text-sm font-black text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <IconActivity class="w-4 h-4 text-slate-400" /> Performance Activity Trends
                </h2>
                <p class="text-xs text-slate-400 font-medium">Timeline metrics across selected timespan</p>
              </div>
              <!-- Legend showing different series and colors -->
              <div class="flex flex-wrap gap-3 text-[10px] font-black uppercase tracking-wider text-slate-500">
                <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded bg-[#8250df]"></span>PRs</span>
                <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded bg-[#3b82f6]"></span>Tasks</span>
                <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded bg-[#6366f1]"></span>Tickets</span>
                <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded bg-[#10b981]"></span>Hours</span>
              </div>
            </div>

            <!-- Hover Details Banner -->
            <div class="h-8 flex items-center justify-between border-b pb-2 border-slate-100">
              <div v-if="hoveredIndex === null" class="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                <IconActivity class="w-3.5 h-3.5 animate-pulse" /> Hover over the chart to view details
              </div>
              <div v-else class="flex flex-wrap gap-x-4 gap-y-1 text-[11px] font-bold text-slate-700 bg-slate-50 px-3 py-1 rounded-xl border border-slate-100/80 animate-fade-in w-full">
                <span class="text-slate-400 font-black uppercase mr-2">{{ timeline.labels[hoveredIndex] }}</span>
                <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-[#8250df]"></span>{{ timeline.prs[hoveredIndex] }} PRs</span>
                <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-[#3b82f6]"></span>{{ timeline.tasks[hoveredIndex] }} Tasks</span>
                <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-[#6366f1]"></span>{{ timeline.tickets[hoveredIndex] }} Tickets</span>
                <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-[#10b981]"></span>{{ timeline.hours[hoveredIndex] }} hrs</span>
              </div>
            </div>

            <!-- Chart Container -->
            <div class="relative flex-1 min-h-[220px] flex flex-col justify-between mt-2">
              <div v-if="!pointsPrs.length" class="text-center py-10 text-slate-400 italic font-semibold">
                No trend data available for this period.
              </div>
              <template v-else>
                <!-- Custom SVG Chart -->
                <svg :viewBox="`0 0 ${chartWidth} ${chartHeight}`" class="w-full h-full overflow-visible" preserveAspectRatio="none">
                  <!-- Gradients Definitions -->
                  <defs>
                    <linearGradient id="grad-prs" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="#8250df" stop-opacity="0.15"/>
                      <stop offset="100%" stop-color="#8250df" stop-opacity="0.0"/>
                    </linearGradient>
                  </defs>

                  <!-- Horizontal Grid Lines -->
                  <g class="stroke-slate-100 stroke-1" stroke-dasharray="3 3">
                    <line x1="0" :y1="chartHeight * 0.25" :x2="chartWidth" :y2="chartHeight * 0.25" />
                    <line x1="0" :y1="chartHeight * 0.5" :x2="chartWidth" :y2="chartHeight * 0.5" />
                    <line x1="0" :y1="chartHeight * 0.75" :x2="chartWidth" :y2="chartHeight * 0.75" />
                    <line x1="0" :y1="chartHeight - 1" :x2="chartWidth" :y2="chartHeight - 1" class="stroke-slate-200 stroke-2" />
                  </g>

                  <!-- PRs Area Gradient -->
                  <path :d="areaPathPrs" fill="url(#grad-prs)" />

                  <!-- PRs Trend Line (Purple) -->
                  <path :d="linePathPrs" fill="none" stroke="#8250df" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />

                  <!-- Tasks Trend Line (Blue) -->
                  <path :d="linePathTasks" fill="none" stroke="#3b82f6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />

                  <!-- Tickets Trend Line (Indigo) -->
                  <path :d="linePathTickets" fill="none" stroke="#6366f1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />

                  <!-- Hours Logged Trend Line (Emerald) -->
                  <path :d="linePathHours" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />

                  <!-- Hover Vertical Dotted Guide Line -->
                  <line
                    v-if="hoveredIndex !== null"
                    :x1="pointsPrs[hoveredIndex]?.x || 0"
                    y1="0"
                    :x2="pointsPrs[hoveredIndex]?.x || 0"
                    :y2="chartHeight"
                    stroke="#cbd5e1"
                    stroke-width="1.5"
                    stroke-dasharray="2 2"
                    class="pointer-events-none"
                  />

                  <!-- Hover circles at active coordinate points -->
                  <g v-if="hoveredIndex !== null">
                    <circle v-if="pointsPrs[hoveredIndex]" :cx="pointsPrs[hoveredIndex].x" :cy="pointsPrs[hoveredIndex].y" r="5" fill="#8250df" stroke="#ffffff" stroke-width="1.5" />
                    <circle v-if="pointsTasks[hoveredIndex]" :cx="pointsTasks[hoveredIndex].x" :cy="pointsTasks[hoveredIndex].y" r="5" fill="#3b82f6" stroke="#ffffff" stroke-width="1.5" />
                    <circle v-if="pointsTickets[hoveredIndex]" :cx="pointsTickets[hoveredIndex].x" :cy="pointsTickets[hoveredIndex].y" r="5" fill="#6366f1" stroke="#ffffff" stroke-width="1.5" />
                    <circle v-if="pointsHours[hoveredIndex]" :cx="pointsHours[hoveredIndex].x" :cy="pointsHours[hoveredIndex].y" r="5" fill="#10b981" stroke="#ffffff" stroke-width="1.5" />
                  </g>

                  <!-- Hitboxes for hover column target detection -->
                  <g>
                    <rect
                      v-for="(p, i) in pointsPrs"
                      :key="'hit-' + i"
                      :x="i === 0 ? 0 : p.x - (chartWidth / Math.max(1, pointsPrs.length - 1)) / 2"
                      y="0"
                      :width="pointsPrs.length > 1 ? (chartWidth / (pointsPrs.length - 1)) : chartWidth"
                      :height="chartHeight"
                      fill="transparent"
                      class="cursor-crosshair"
                      @mouseenter="hoveredIndex = i"
                      @mouseleave="hoveredIndex = null"
                    />
                  </g>
                </svg>

                <!-- X-Axis Labels -->
                <div class="flex justify-between text-[9px] text-slate-400 font-bold uppercase tracking-wider px-2 mt-2 border-t pt-2 border-slate-100">
                  <span>{{ timeline.labels[0] }}</span>
                  <span>{{ timeline.labels[Math.floor(timeline.labels.length / 2)] }}</span>
                  <span>{{ timeline.labels[timeline.labels.length - 1] }}</span>
                </div>
              </template>
            </div>
          </Card>

          <!-- GitHub Pull Request Donut Splits Card -->
          <Card class="!shadow-sm bg-white border border-slate-100 p-6 flex flex-col justify-between hover:shadow-md transition-all duration-300">
            <div>
              <h2 class="text-sm font-black text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                <IconGitPullRequest class="w-4 h-4 text-purple-500" /> PR Allocation
              </h2>
              <p class="text-xs text-slate-400 font-medium">PR distribution and code review merges</p>
            </div>

            <!-- Donut Container -->
            <div class="flex items-center justify-between w-full gap-2 py-4">
              <!-- SVG Donut Chart -->
              <div class="relative w-32 h-32 flex-shrink-0 flex items-center justify-center">
                <svg class="w-full h-full transform -rotate-90" viewBox="0 0 42 42">
                  <!-- Background track -->
                  <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#f1f5f9" stroke-width="4.5"/>
                  
                  <!-- Merged Section (purple) -->
                  <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#8250df" stroke-width="4.5" 
                    :stroke-dasharray="`${(performanceData.github?.merged_prs / Math.max(1, performanceData.github?.total_prs)) * 100} ${100 - ((performanceData.github?.merged_prs / Math.max(1, performanceData.github?.total_prs)) * 100)}`"
                    stroke-dashoffset="0"
                    class="transition-all duration-1000 ease-out"
                  />
                  
                  <!-- Open Section (green) -->
                  <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#22c55e" stroke-width="4.5" 
                    :stroke-dasharray="`${(performanceData.github?.open_prs / Math.max(1, performanceData.github?.total_prs)) * 100} ${100 - ((performanceData.github?.open_prs / Math.max(1, performanceData.github?.total_prs)) * 100)}`"
                    :stroke-dashoffset="`${-((performanceData.github?.merged_prs / Math.max(1, performanceData.github?.total_prs)) * 100)}`"
                    class="transition-all duration-1000 ease-out"
                  />
                  
                  <!-- Closed Section (red) -->
                  <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#ef4444" stroke-width="4.5" 
                    :stroke-dasharray="`${(performanceData.github?.closed_prs / Math.max(1, performanceData.github?.total_prs)) * 100} ${100 - ((performanceData.github?.closed_prs / Math.max(1, performanceData.github?.total_prs)) * 100)}`"
                    :stroke-dashoffset="`${-(((performanceData.github?.merged_prs + performanceData.github?.open_prs) / Math.max(1, performanceData.github?.total_prs)) * 100)}`"
                    class="transition-all duration-1000 ease-out"
                  />
                </svg>
                
                <!-- Center count -->
                <div class="absolute flex flex-col items-center justify-center text-center">
                  <span class="text-2xl font-black text-slate-800 leading-none">
                    {{ performanceData.github?.total_prs || 0 }}
                  </span>
                  <span class="text-[8px] text-slate-400 uppercase tracking-widest font-black mt-0.5">Total PRs</span>
                </div>
              </div>

              <!-- Legends -->
              <div class="flex-1 space-y-2.5">
                <div class="flex items-center justify-between text-[11px] font-semibold text-slate-500">
                  <span class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-md bg-[#8250df]"></span>
                    <span>Merged</span>
                  </span>
                  <span class="font-extrabold text-slate-800">{{ performanceData.github?.merged_prs || 0 }}</span>
                </div>
                <div class="flex items-center justify-between text-[11px] font-semibold text-slate-500">
                  <span class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-md bg-green-500"></span>
                    <span>Open</span>
                  </span>
                  <span class="font-extrabold text-slate-800">{{ performanceData.github?.open_prs || 0 }}</span>
                </div>
                <div class="flex items-center justify-between text-[11px] font-semibold text-slate-500">
                  <span class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 rounded-md bg-red-500"></span>
                    <span>Closed</span>
                  </span>
                  <span class="font-extrabold text-slate-800">{{ performanceData.github?.closed_prs || 0 }}</span>
                </div>
              </div>
            </div>

            <!-- Extra Stats Footer inside Donut Card -->
            <div class="grid grid-cols-2 gap-2.5 border-t pt-4 text-center mt-2">
              <div class="bg-slate-50 p-2 rounded-xl border border-slate-100">
                <div class="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Repositories</div>
                <div class="text-base font-black text-slate-800 mt-0.5">{{ performanceData.github?.repos_count || 0 }}</div>
              </div>
              <div class="bg-slate-50 p-2 rounded-xl border border-slate-100">
                <div class="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Comments Recv</div>
                <div class="text-base font-black text-slate-800 mt-0.5">{{ performanceData.github?.comments_count || 0 }}</div>
              </div>
            </div>
          </Card>
        </div>

        <!-- Analytical Breakdown Sections (Logged Hours by Activity, SLA and Efficiency) -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Activity Distribution Card (2 Columns width on lg) -->
          <Card class="!shadow-sm bg-white border border-slate-100 p-6 lg:col-span-2 space-y-6 hover:shadow-md transition-all duration-300">
            <div>
              <h2 class="text-sm font-black text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                <IconBriefcase class="w-4 h-4 text-slate-400" /> Logged Hours by Activity
              </h2>
              <p class="text-xs text-slate-400 font-medium">Workload distribution from timesheet details</p>
            </div>

            <div class="space-y-4">
              <div 
                v-for="activity in resolvedActivities" 
                :key="activity.name" 
                class="space-y-1.5 group"
              >
                <div class="flex justify-between text-xs font-bold text-slate-600">
                  <span>{{ activity.name }}</span>
                  <span class="font-black text-slate-900 group-hover:text-blue-600 transition-colors">{{ activity.hours?.toFixed(1) }} hrs ({{ activity.percentage }}%)</span>
                </div>
                <div class="w-full bg-slate-50 h-2.5 rounded-full overflow-hidden border border-slate-100">
                  <div 
                    class="h-full rounded-full transition-all duration-500 ease-out"
                    :class="activity.barColor"
                    :style="{ width: `${activity.percentage}%` }"
                  ></div>
                </div>
              </div>
              <div v-if="resolvedActivities.length === 0" class="text-center py-10 text-slate-400 italic font-semibold">
                No active timesheet logs found in this period.
              </div>
            </div>
          </Card>

          <!-- Ticket Resolution & Overdues Column -->
          <div class="space-y-6">
            <!-- Ticket SLAs -->
            <Card class="!shadow-sm bg-white border border-slate-100 p-6 space-y-4 hover:shadow-md transition-all duration-300">
              <div>
                <h2 class="text-sm font-black text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <IconShieldAlert class="w-4 h-4 text-slate-400" /> Ticket SLA Performance
                </h2>
                <p class="text-xs text-slate-400 font-medium">Speed metrics for customer satisfaction</p>
              </div>

              <div class="space-y-4 border-t pt-4 text-xs font-semibold text-slate-500">
                <div class="flex justify-between">
                  <span>Ticket Resolution Rate</span>
                  <span class="font-extrabold text-slate-800">{{ performanceData.ticket?.resolution_rate?.toFixed(1) || '0.0' }}%</span>
                </div>
                <div class="flex justify-between">
                  <span>Avg Initial Response Time</span>
                  <span class="font-extrabold text-slate-800">{{ formatDuration(performanceData.ticket?.avg_response_time) }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Avg Ticket Resolution Time</span>
                  <span class="font-extrabold text-slate-800">{{ formatDuration(performanceData.ticket?.avg_close_time) }}</span>
                </div>
              </div>
            </Card>

            <!-- Tasks Efficiency -->
            <Card class="!shadow-sm bg-white border border-slate-100 p-6 space-y-4 hover:shadow-md transition-all duration-300">
              <div>
                <h2 class="text-sm font-black text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <IconAlertCircle class="w-4 h-4 text-slate-400" /> Task Status Efficiency
                </h2>
                <p class="text-xs text-slate-400 font-medium">Overdues and tracking ratios</p>
              </div>

              <div class="space-y-4 border-t pt-4 text-xs font-semibold text-slate-500">
                <div class="flex justify-between">
                  <span>Total Tasks Assigned</span>
                  <span class="font-extrabold text-slate-800">{{ performanceData.task?.total || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Completed Tasks</span>
                  <span class="font-extrabold text-green-600">{{ performanceData.task?.completed || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Overdue Tasks</span>
                  <span class="font-extrabold" :class="performanceData.task?.overdue > 0 ? 'text-red-500 font-black' : 'text-slate-800'">
                    {{ performanceData.task?.overdue || 0 }}
                  </span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button, Card, createResource } from "frappe-ui"
import { computed, ref, watch } from "vue"

import IconActivity from "~icons/lucide/activity"
import IconAlertCircle from "~icons/lucide/alert-circle"
import IconBriefcase from "~icons/lucide/briefcase"
import IconCalendar from "~icons/lucide/calendar"
import IconCheckSquare from "~icons/lucide/check-square"
import IconClock from "~icons/lucide/clock"
import IconGitPullRequest from "~icons/lucide/git-pull-request"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconShieldAlert from "~icons/lucide/shield-alert"
// Icons
import IconTrendingUp from "~icons/lucide/trending-up"
import IconUser from "~icons/lucide/user"

// Filter values
const selectedTimespan = ref("this_month")
const selectedEmployee = ref("")

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

const performanceData = computed(() => performanceResource.data)

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

// Map activity hours to beautiful color codes and compute percentages
const activityColors = {
	Execution: { bar: "bg-blue-500" },
	Planning: { bar: "bg-indigo-500" },
	Research: { bar: "bg-purple-500" },
	Communication: { bar: "bg-teal-500" },
	"Proposal Writing": { bar: "bg-orange-500" },
}

const resolvedActivities = computed(() => {
	const activities = performanceData.value?.timesheet?.activities || {}
	const total = performanceData.value?.timesheet?.total_hours || 0

	return Object.entries(activities)
		.map(([name, hours]) => {
			const percentage = total > 0 ? Math.round((hours / total) * 100) : 0
			const color = activityColors[name] || { bar: "bg-slate-400" }
			return {
				name,
				hours,
				percentage,
				barColor: color.bar,
			}
		})
		.sort((a, b) => b.hours - a.hours)
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
</style>