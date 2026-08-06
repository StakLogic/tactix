<template>
  <div class="h-full w-full min-h-0 flex flex-col">
    <!-- Access Restricted View for External Clients (Ticket Raisers) -->
    <div v-if="session.isTicketRaiser" class="flex flex-col items-center justify-center h-full p-8 text-center bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/80 dark:border-slate-800 m-2 shadow-xs">
    <div class="p-4 bg-rose-50 dark:bg-rose-950/40 rounded-3xl mb-4 border border-rose-100 dark:border-rose-900/40">
      <IconLock class="w-12 h-12 text-rose-500" />
    </div>
    <h2 class="text-base font-bold text-slate-800 dark:text-slate-100">Access Restricted</h2>
    <p class="text-xs text-slate-500 dark:text-slate-400 max-w-sm mt-1 leading-relaxed">
      The Document Drive is available exclusively for internal organization members.
    </p>
  </div>

  <div
    v-else
    class="space-y-3 p-2 flex flex-col h-full overflow-hidden min-h-0 relative select-none"
    @dragenter.prevent="onWindowDragEnter"
  >
    <!-- Window Drag & Drop Overlay (Strict Z-index: z-40, hidden during preview/modal) -->
    <div
      v-if="dragActive && !previewModal.show && !shareModal.show && !deleteConfirm.show && !showNewFolderModal"
      class="fixed inset-0 z-40 bg-blue-600/15 backdrop-blur-md border-4 border-dashed border-blue-500 rounded-3xl m-3 flex flex-col items-center justify-center transition-all duration-300 cursor-pointer pointer-events-auto"
      @dragleave.prevent="onWindowDragLeave"
      @dragover.prevent
      @drop.prevent="handleDrop"
    >
      <div class="p-8 bg-white dark:bg-slate-900 rounded-3xl shadow-2xl flex flex-col items-center gap-4 text-center max-w-sm pointer-events-none">
        <div class="p-4 bg-blue-50 dark:bg-blue-950/60 rounded-2xl">
          <IconUploadCloud class="w-12 h-12 text-blue-600 dark:text-blue-400 animate-bounce" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-slate-900 dark:text-white">Drop files to upload to Drive</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
            Files will be stored securely in <span class="font-bold text-blue-600 dark:text-blue-400">{{ currentPathName }}</span>
          </p>
        </div>
      </div>
    </div>

    <!-- Top Action & Filter Bar -->
    <div class="bg-white dark:bg-slate-900 p-3 rounded-lg border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col gap-2.5 flex-shrink-0">
      <!-- Top Row: Search & Actions -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 w-full pb-2 border-b border-slate-100 dark:border-slate-800/80">

        <!-- Search Bar with Clear Icon -->
        <div class="relative w-full sm:w-80">
          <IconSearch class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 dark:text-slate-500" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search files and folders in Drive…"
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

        <!-- Right Side Action Group: Upload File, New Folder, View Mode & Refresh -->
        <div class="flex items-center gap-2 ml-auto sm:ml-0 flex-wrap justify-end">
          <!-- View Mode Toggle -->
          <div class="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-md border border-slate-200/60 dark:border-slate-700">
            <button
              @click="viewMode = 'grid'"
              :class="viewBtnClass('grid')"
              title="Grid View"
            >
              <IconLayoutGrid class="w-3.5 h-3.5" />
            </button>
            <button
              @click="viewMode = 'list'"
              :class="viewBtnClass('list')"
              title="List View"
            >
              <IconList class="w-3.5 h-3.5" />
            </button>
          </div>

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
                title="Filter Drive Files"
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
                    <span>Filter Drive Files</span>
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
            @click="refresh"
            title="Refresh drive"
          >
            <template #prefix><IconRefreshCcw class="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" :class="{ 'animate-spin': loading }" /></template>
          </Button>

          <!-- Up Button -->
          <Button
            v-if="currentPath !== '/'"
            variant="outline"
            class="!text-slate-600 dark:!text-slate-200 !px-2.5 !h-8 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all rounded-md text-xs font-medium"
            @click="navigateUp"
          >
            <template #prefix><IconArrowLeft class="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" /></template>
            Up
          </Button>

          <!-- New Folder Button -->
          <Button
            v-if="uploadAllowed"
            variant="outline"
            class="!text-slate-600 dark:!text-slate-200 !px-2.5 !h-8 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all rounded-md text-xs font-medium"
            @click="showNewFolderModal = true"
          >
            <template #prefix><IconFolderPlus class="w-3.5 h-3.5 text-amber-500" /></template>
            New Folder
          </Button>

          <!-- Primary Upload Button -->
          <Button
            v-if="uploadAllowed"
            variant="solid"
            class="!text-xs !px-4 !h-8 rounded-md transition-all font-medium"
            style="background-color: var(--primary-color);"
            @click="fileInput.click()"
          >
            <template #prefix><IconUploadCloud class="w-3.5 h-3.5" /></template>
            Upload File
          </Button>
        </div>
      </div>

      <!-- Bottom Row: Quick Filter Bar -->
      <div class="filter-row flex flex-nowrap overflow-x-auto pb-1 gap-2 w-full custom-scrollbar sm:flex-wrap sm:overflow-visible sm:pb-0 sm:items-center sm:gap-2">
        <!-- Searchable Filter: File Type Autocomplete -->
        <div class="w-36 shrink-0">
          <Autocomplete
            ref="fileTypeAutocomplete"
            :options="fileTypeOptions"
            :modelValue="fileTypeFilter"
            @update:modelValue="val => fileTypeFilter = val?.value || val || 'All'"
          >
            <template #target>
              <button
                type="button"
                @click="() => fileTypeAutocomplete?.togglePopover()"
                :class="[
                  'inline-flex items-center justify-between gap-2 outline-none text-xs rounded min-h-7 h-7 px-2 border transition-colors w-full cursor-pointer',
                  fileTypeFilter !== 'All'
                    ? 'border-blue-500 text-blue-600 bg-blue-50/50 font-medium dark:bg-blue-950/40 dark:text-blue-400'
                    : 'border-[--surface-gray-2] bg-surface-gray-2 hover:border-outline-gray-modals hover:bg-surface-gray-3 text-ink-gray-7 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-200'
                ]"
              >
                <span class="truncate">{{ getFilterLabel('fileTypeFilter', fileTypeFilter, 'File Type') }}</span>
                <FeatherIcon name="chevron-down" class="size-4 text-ink-gray-4 ml-auto shrink-0" />
              </button>
            </template>
          </Autocomplete>
        </div>

        <!-- Searchable Filter: Source Autocomplete -->
        <div class="w-36 shrink-0">
          <Autocomplete
            ref="sourceAutocomplete"
            :options="sourceOptions"
            :modelValue="sourceFilter"
            @update:modelValue="val => sourceFilter = val?.value || val || 'All'"
          >
            <template #target>
              <button
                type="button"
                @click="() => sourceAutocomplete?.togglePopover()"
                :class="[
                  'inline-flex items-center justify-between gap-2 outline-none text-xs rounded min-h-7 h-7 px-2 border transition-colors w-full cursor-pointer',
                  sourceFilter !== 'All'
                    ? 'border-blue-500 text-blue-600 bg-blue-50/50 font-medium dark:bg-blue-950/40 dark:text-blue-400'
                    : 'border-[--surface-gray-2] bg-surface-gray-2 hover:border-outline-gray-modals hover:bg-surface-gray-3 text-ink-gray-7 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-200'
                ]"
              >
                <span class="truncate">{{ getFilterLabel('sourceFilter', sourceFilter, 'Source') }}</span>
                <FeatherIcon name="chevron-down" class="size-4 text-ink-gray-4 ml-auto shrink-0" />
              </button>
            </template>
          </Autocomplete>
        </div>

        <!-- Searchable Filter: Access Level Autocomplete -->
        <div class="w-36 shrink-0">
          <Autocomplete
            ref="accessAutocomplete"
            :options="accessOptions"
            :modelValue="accessFilter"
            @update:modelValue="val => accessFilter = val?.value || val || 'All'"
          >
            <template #target>
              <button
                type="button"
                @click="() => accessAutocomplete?.togglePopover()"
                :class="[
                  'inline-flex items-center justify-between gap-2 outline-none text-xs rounded min-h-7 h-7 px-2 border transition-colors w-full cursor-pointer',
                  accessFilter !== 'All'
                    ? 'border-blue-500 text-blue-600 bg-blue-50/50 font-medium dark:bg-blue-950/40 dark:text-blue-400'
                    : 'border-[--surface-gray-2] bg-surface-gray-2 hover:border-outline-gray-modals hover:bg-surface-gray-3 text-ink-gray-7 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-200'
                ]"
              >
                <span class="truncate">{{ getFilterLabel('accessFilter', accessFilter, 'Access') }}</span>
                <FeatherIcon name="chevron-down" class="size-4 text-ink-gray-4 ml-auto shrink-0" />
              </button>
            </template>
          </Autocomplete>
        </div>

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

    <!-- Hidden Input for File Upload -->
    <input ref="fileInput" type="file" class="hidden" multiple @change="handleFileSelect" />

    <!-- Breadcrumb Trail & Storage Details Header Bar -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl px-4 py-2 flex-shrink-0 shadow-xs">
      <div class="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-400 font-semibold overflow-x-auto whitespace-nowrap custom-scrollbar">
        <button
          class="flex items-center gap-1.5 hover:text-blue-600 dark:hover:text-blue-400 font-bold tracking-wide text-xs px-2 py-1 rounded-xl hover:bg-blue-50 dark:hover:bg-blue-950/40 transition-colors border-none bg-transparent cursor-pointer"
          @click="fetchPath('/')"
        >
          <IconHome class="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
          Organization Drive
        </button>

        <template v-for="(part, idx) in rawPathParts" :key="idx">
          <IconChevronRight class="w-3.5 h-3.5 text-slate-300 dark:text-slate-600 shrink-0" />
          <button
            class="hover:text-blue-600 dark:hover:text-blue-400 font-semibold px-2 py-1 rounded-xl hover:bg-blue-50 dark:hover:bg-blue-950/40 text-xs transition-colors border-none bg-transparent cursor-pointer"
            :class="{ 'text-slate-900 dark:text-white font-bold bg-slate-100 dark:bg-slate-800': idx === rawPathParts.length - 1 }"
            @click="navigateToBreadcrumb(idx)"
          >
            {{ getCleanName(part) }}
          </button>
        </template>
      </div>

      <div class="flex items-center gap-3 text-xs font-semibold text-slate-600 dark:text-slate-400 shrink-0">
        <span v-if="!loading" class="flex items-center gap-1.5">
          <IconFolder class="w-3.5 h-3.5 text-amber-500" />
          {{ folders.length }} {{ folders.length === 1 ? 'folder' : 'folders' }}
        </span>
        <span v-if="!loading" class="text-slate-300 dark:text-slate-700">•</span>
        <span v-if="!loading" class="flex items-center gap-1.5">
          <IconFile class="w-3.5 h-3.5 text-blue-500" />
          {{ filteredFiles.length }} {{ filteredFiles.length === 1 ? 'file' : 'files' }}
        </span>
        <button
          @click="toggleDetailsPanel"
          class="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 border-none bg-transparent cursor-pointer transition-colors ml-1"
          :class="{ 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40': selectedItem }"
          title="Toggle Details Panel"
        >
          <IconInfo class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Main Workspace Split Container -->
    <div class="flex-1 flex gap-3 min-h-0 overflow-hidden">
      <!-- Main Content Explorer Area -->
      <div class="flex-1 overflow-y-auto space-y-4 pr-1 custom-scrollbar">

        <!-- Loading Spinner -->
        <div v-if="loading" class="flex flex-col items-center justify-center py-24 gap-3">
          <LoadingIndicator class="w-8 h-8 text-blue-600" />
          <span class="text-xs font-semibold text-slate-400 dark:text-slate-500">Loading Drive items…</span>
        </div>

        <div v-else class="space-y-5">
          <!-- Folders Section -->
          <div v-if="folders.length > 0" class="space-y-2.5">
            <h3 class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider px-1">
              Folders ({{ folders.length }})
            </h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-3">
              <div
                v-for="folder in folders"
                :key="folder.path"
                class="group relative flex items-center justify-between p-3.5 rounded-2xl bg-white dark:bg-slate-800/90 border border-slate-200/80 dark:border-slate-700/70 hover:border-blue-400 dark:hover:border-blue-500 hover:shadow-md transition-all duration-200 cursor-pointer select-none"
                :class="{ 'ring-2 ring-blue-500 border-transparent bg-blue-50/20 dark:bg-blue-950/30': selectedItem?.path === folder.path }"
                @click="selectItem(folder)"
                @dblclick="fetchPath(folder.path)"
              >
                <div class="flex items-center gap-3 min-w-0 flex-1">
                  <div class="p-2.5 rounded-xl shrink-0 transition-transform group-hover:scale-105" :class="getFolderIconColorClass(folder.path)">
                    <IconFolder class="w-5 h-5" />
                  </div>
                  <div class="min-w-0 flex-1">
                    <div class="text-xs font-bold text-slate-800 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors truncate" :title="folder.name">
                      {{ folder.name }}
                    </div>
                    <div class="text-[10px] text-slate-400 dark:text-slate-500 font-medium truncate mt-0.5">
                      {{ getFolderTypeLabel(folder.path) }} Folder
                    </div>
                  </div>
                </div>

                <div class="p-1.5 rounded-xl bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-200 group-hover:text-blue-600 dark:group-hover:text-blue-400 group-hover:bg-blue-50 dark:group-hover:bg-blue-950 transition-colors">
                  <IconArrowLeft class="w-3.5 h-3.5 rotate-180" />
                </div>
              </div>
            </div>
          </div>

          <!-- Files Section -->
          <div class="space-y-3">
            <!-- Multi-Select Action Banner -->
            <transition name="slide-up">
              <div v-if="selectedItems && selectedItems.length > 0" class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-blue-600 text-white p-3.5 rounded-2xl shadow-lg mb-4">
                <div class="flex items-center gap-3">
                  <div class="w-2.5 h-2.5 rounded-full bg-white animate-ping"></div>
                  <span class="text-xs font-bold">
                    {{ selectedItems ? selectedItems.length : 0 }} {{ selectedItems?.length === 1 ? 'file' : 'files' }} selected
                  </span>
                </div>
                <div class="flex items-center gap-2 w-full sm:w-auto justify-end">
                  <button class="px-3 py-1.5 bg-white/20 hover:bg-white/30 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors border-none cursor-pointer" @click="openBulkShareModal">
                    <IconShare2 class="w-3.5 h-3.5" />
                    Share
                  </button>
                  <button class="px-3 py-1.5 bg-rose-500 hover:bg-rose-600 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors border-none cursor-pointer" @click="promptBulkDelete">
                    <IconTrash2 class="w-3.5 h-3.5" />
                    Delete
                  </button>
                  <button class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded-xl text-xs font-medium border-none cursor-pointer" @click="clearSelection">
                    Deselect
                  </button>
                </div>
              </div>
            </transition>

            <div class="flex items-center justify-between px-1">
              <h3 class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Files ({{ filteredFiles.length }})
              </h3>
            </div>

            <!-- Empty File Explorer Card -->
            <div v-if="filteredFiles.length === 0" class="flex flex-col items-center justify-center py-16 px-4 bg-white dark:bg-slate-800 border border-dashed border-slate-200 dark:border-slate-700 rounded-3xl text-center">
              <div class="p-4 bg-slate-50 dark:bg-slate-900 rounded-3xl mb-3">
                <IconFile class="w-10 h-10 text-slate-300 dark:text-slate-600" />
              </div>
              <h4 class="text-sm font-bold text-slate-700 dark:text-slate-200">No files in this location</h4>
              <p class="text-xs text-slate-400 max-w-sm mt-1">
                {{ searchQuery ? 'No files matched your search or filters.' : 'Drag & drop files here to upload them to Drive.' }}
              </p>
              <button v-if="uploadAllowed" @click="fileInput.click()" class="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl text-xs font-bold transition-colors border-none cursor-pointer flex items-center gap-2">
                <IconUploadCloud class="w-4 h-4" />
                Upload files
              </button>
            </div>

            <!-- Files Grid / List View -->
            <div v-else>
              <!-- Google Drive Style Grid Cards -->
              <div v-if="viewMode === 'grid'" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-4">
                <div
                  v-for="file in filteredFiles"
                  :key="file.name"
                  class="group relative flex flex-col bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl overflow-hidden hover:shadow-xl hover:border-blue-400 dark:hover:border-blue-500 transition-all duration-200 cursor-pointer select-none"
                  :class="{ 'ring-2 ring-blue-500 border-transparent bg-blue-50 dark:bg-blue-950': selectedItem?.name === file.name || isSelected(file.name) }"
                  @click="selectItem(file)"
                  @dblclick="openPreview(file)"
                >
                  <!-- Google Drive Checkbox (Only visible on hover/selection, completely unmounted when modals/dialogs are active) -->
                  <div
                    v-if="!previewModal.show && !shareModal.show && !deleteConfirm.show && !showNewFolderModal"
                    class="absolute top-2.5 left-2.5 z-10 transition-opacity duration-200"
                    :class="selectedItems.length > 0 || isSelected(file.name) ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'"
                    @click.stop
                  >
                    <input
                      type="checkbox"
                      :checked="isSelected(file.name)"
                      @change="toggleSelect(file.name)"
                      class="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300 dark:border-slate-600 dark:bg-slate-900 cursor-pointer shadow-sm"
                    />
                  </div>

                  <!-- Google Drive Card Top Thumbnail Region -->
                  <div class="h-32 bg-slate-50 dark:bg-slate-900 border-b border-slate-100 dark:border-slate-700 relative flex items-center justify-center overflow-hidden group-hover:bg-slate-100 dark:group-hover:bg-slate-900 transition-colors">

                    <!-- Image File Thumbnail Preview -->
                    <template v-if="isImage(file.file_name)">
                      <img
                        :src="file.file_url"
                        :alt="file.file_name"
                        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        loading="lazy"
                        @error="file.imgError = true"
                      />
                    </template>

                    <!-- Non-Image File Icon Card Illustration -->
                    <template v-else>
                      <div class="p-4 rounded-2xl flex flex-col items-center justify-center gap-1.5 transition-transform group-hover:scale-105" :class="getFileIconBg(file.file_name)">
                        <component
                          :is="getFileIcon(file.file_name)"
                          class="w-8 h-8"
                          :class="getFileIconColor(file.file_name)"
                        />
                        <span class="text-[9px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400">
                          {{ getExtensionLabel(file.file_name) }}
                        </span>
                      </div>
                    </template>

                    <!-- Hover Quick Action Bar (Solid Theme Backgrounds) -->
                    <div
                      v-if="!previewModal.show && !shareModal.show && !deleteConfirm.show && !showNewFolderModal"
                      class="absolute top-2 right-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10"
                      @click.stop
                    >
                      <button
                        class="p-1.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950 dark:hover:text-blue-400 transition-colors cursor-pointer shadow-md"
                        title="Preview File"
                        @click="openPreview(file)"
                      >
                        <IconEye class="w-3.5 h-3.5" />
                      </button>
                      <button
                        v-if="file.can_share"
                        class="p-1.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950 dark:hover:text-blue-400 transition-colors cursor-pointer shadow-md"
                        title="Share File"
                        @click="openShareModal(file)"
                      >
                        <IconShare2 class="w-3.5 h-3.5" />
                      </button>
                      <a
                        :href="file.file_url"
                        target="_blank"
                        download
                        class="p-1.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950 dark:hover:text-blue-400 transition-colors cursor-pointer shadow-md flex items-center justify-center"
                        title="Download File"
                      >
                        <IconDownload class="w-3.5 h-3.5" />
                      </a>
                      <button
                        v-if="isDeletable(file)"
                        class="p-1.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950 dark:hover:text-rose-400 transition-colors cursor-pointer shadow-md"
                        title="Delete File"
                        @click="promptDelete(file)"
                      >
                        <IconTrash2 class="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  <!-- Card Footer / File Details -->
                  <div class="p-3 flex flex-col gap-2">
                    <div class="flex items-center gap-2 min-w-0">
                      <component
                        :is="getFileIcon(file.file_name)"
                        class="w-4 h-4 shrink-0"
                        :class="getFileIconColor(file.file_name)"
                      />
                      <span class="text-xs font-bold text-slate-800 dark:text-slate-100 truncate group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" :title="file.file_name">
                        {{ file.file_name }}
                      </span>
                    </div>

                    <div class="flex items-center justify-between gap-1 pt-1 border-t border-slate-100 dark:border-slate-700/40 text-[10px] text-slate-400 font-medium">
                      <span class="font-mono">{{ formatBytes(file.file_size) }}</span>
                      <div class="flex items-center gap-1">
                        <span
                          class="font-bold px-1.5 py-0.5 rounded-md text-[8px] uppercase"
                          :class="getSourceBadgeClass(file.source)"
                        >
                          {{ file.source }}
                        </span>
                        <Avatar :image="file.owner_image" :label="file.owner_full_name" size="xs" class="ring-1 ring-white dark:ring-slate-800 shrink-0" :title="file.owner_full_name" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- List View -->
              <div v-else class="bg-white dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700/70 rounded-2xl overflow-hidden shadow-xs">
                <table class="w-full text-left border-collapse table-fixed">
                  <thead>
                    <tr class="bg-slate-50/80 dark:bg-slate-900/60 border-b border-slate-200/80 dark:border-slate-700 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                      <th class="w-10 py-3 pl-4 pr-1 text-center">
                        <input
                          type="checkbox"
                          :checked="isAllSelected"
                          @change="toggleSelectAll"
                          class="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300 dark:border-slate-700 dark:bg-slate-900 cursor-pointer"
                        />
                      </th>
                      <th class="w-1/2 py-3 px-4">Name</th>
                      <th class="w-1/6 py-3 px-4">Owner</th>
                      <th class="w-1/6 py-3 px-4">Size</th>
                      <th class="w-1/6 py-3 px-4">Date</th>
                      <th class="w-24 py-3 px-4 text-right pr-6">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100 dark:divide-slate-700/50 text-xs font-medium text-slate-700 dark:text-slate-300">
                    <tr
                      v-for="file in filteredFiles"
                      :key="file.name"
                      class="hover:bg-blue-50/40 dark:hover:bg-blue-950/20 transition-colors cursor-pointer group"
                      :class="{ 'bg-blue-50/50 dark:bg-blue-950/30': selectedItem?.name === file.name || isSelected(file.name) }"
                      @click="selectItem(file)"
                      @dblclick="openPreview(file)"
                    >
                      <td class="py-3 pl-4 pr-1 text-center" @click.stop>
                        <input
                          type="checkbox"
                          :checked="isSelected(file.name)"
                          @change="toggleSelect(file.name)"
                          class="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300 dark:border-slate-700 dark:bg-slate-900 cursor-pointer"
                        />
                      </td>
                      <td class="py-3 px-4 flex items-center gap-3 min-w-0">
                        <div class="p-2 rounded-xl shrink-0" :class="getFileIconBg(file.file_name)">
                          <component
                            :is="getFileIcon(file.file_name)"
                            class="w-4 h-4 shrink-0"
                            :class="getFileIconColor(file.file_name)"
                          />
                        </div>
                        <div class="min-w-0 flex-1">
                          <div class="font-bold text-slate-800 dark:text-slate-100 truncate group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" :title="file.file_name">
                            {{ file.file_name }}
                          </div>
                        </div>
                      </td>

                      <td class="py-3 px-4">
                        <div class="flex items-center gap-2">
                          <Avatar :image="file.owner_image" :label="file.owner_full_name" size="xs" />
                          <span class="text-xs font-medium text-slate-600 dark:text-slate-300 truncate max-w-[8rem]">{{ file.owner_full_name }}</span>
                        </div>
                      </td>

                      <td class="py-3 px-4 text-slate-500 dark:text-slate-400 font-mono text-xs">
                        {{ formatBytes(file.file_size) }}
                      </td>

                      <td class="py-3 px-4 text-slate-500 dark:text-slate-400 text-xs">
                        {{ formatDate(file.creation) }}
                      </td>

                      <td class="py-3 px-4 text-right pr-6" @click.stop>
                        <div class="flex items-center justify-end gap-1">
                          <button
                            class="p-1.5 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950/40 transition-colors border-none bg-transparent cursor-pointer"
                            title="Preview File"
                            @click="openPreview(file)"
                          >
                            <IconEye class="w-4 h-4" />
                          </button>
                          <button
                            v-if="file.can_share"
                            class="p-1.5 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950/40 transition-colors border-none bg-transparent cursor-pointer"
                            title="Share File"
                            @click="openShareModal(file)"
                          >
                            <IconShare2 class="w-4 h-4" />
                          </button>
                          <a
                            :href="file.file_url"
                            target="_blank"
                            download
                            class="p-1.5 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950/40 transition-colors border border-transparent"
                            title="Download File"
                          >
                            <IconDownload class="w-4 h-4" />
                          </a>
                          <button
                            v-if="isDeletable(file)"
                            class="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors border-none bg-transparent cursor-pointer"
                            title="Delete File"
                            @click="promptDelete(file)"
                          >
                            <IconTrash2 class="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Details & Metadata Drawer -->
      <div
        v-if="selectedItem"
        class="w-80 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl flex flex-col p-5 flex-shrink-0 relative overflow-y-auto hidden lg:flex custom-scrollbar shadow-xs space-y-5"
      >
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
          <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">File Details</span>
          <button @click="selectedItem = null" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 border-none bg-transparent cursor-pointer rounded-lg">
            <IconX class="w-4 h-4" />
          </button>
        </div>

        <!-- Preview Thumbnail Header in Details Panel -->
        <div class="flex flex-col items-center text-center p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-750">
          <template v-if="!selectedItem.is_folder && isImage(selectedItem.file_name)">
            <img :src="selectedItem.file_url" class="max-h-36 max-w-full rounded-xl object-contain shadow-sm mb-2" />
          </template>
          <template v-else>
            <div class="p-4 rounded-2xl mb-2" :class="selectedItem.is_folder ? getFolderIconColorClass(selectedItem.path) : getFileIconBg(selectedItem.file_name)">
              <component
                :is="selectedItem.is_folder ? IconFolder : getFileIcon(selectedItem.file_name)"
                class="w-8 h-8"
                :class="selectedItem.is_folder ? '' : getFileIconColor(selectedItem.file_name)"
              />
            </div>
          </template>

          <h4 class="text-xs font-bold text-slate-800 dark:text-slate-100 break-all mt-2 w-full px-1">
            {{ selectedItem.is_folder ? selectedItem.name : selectedItem.file_name }}
          </h4>
          <span
            v-if="!selectedItem.is_folder"
            class="text-[9px] font-bold px-2 py-0.5 rounded-full uppercase mt-2 shrink-0"
            :class="getSourceBadgeClass(selectedItem.source)"
          >
            {{ selectedItem.source }} Upload
          </span>
        </div>

        <div class="space-y-3 text-xs font-medium">
          <div class="flex justify-between items-center py-2 border-b border-slate-100 dark:border-slate-800">
            <span class="text-slate-400">Path</span>
            <span class="text-slate-700 dark:text-slate-300 font-semibold truncate max-w-[10rem]">{{ selectedItem.path || currentPath }}</span>
          </div>

          <template v-if="!selectedItem.is_folder">
            <div class="flex justify-between items-center py-2 border-b border-slate-100 dark:border-slate-800">
              <span class="text-slate-400">Size</span>
              <span class="text-slate-700 dark:text-slate-300 font-mono">{{ formatBytes(selectedItem.file_size) }}</span>
            </div>

            <div class="flex justify-between items-center py-2 border-b border-slate-100 dark:border-slate-800">
              <span class="text-slate-400">Created</span>
              <span class="text-slate-700 dark:text-slate-300">{{ formatDate(selectedItem.creation) }}</span>
            </div>

            <div class="flex justify-between items-center py-2 border-b border-slate-100 dark:border-slate-800">
              <span class="text-slate-400">Uploaded By</span>
              <div class="flex items-center gap-1.5">
                <Avatar :image="selectedItem.owner_image" :label="selectedItem.owner_full_name" size="xs" />
                <span class="text-slate-700 dark:text-slate-300 font-semibold truncate max-w-[8rem]">{{ selectedItem.owner_full_name }}</span>
              </div>
            </div>

            <div class="pt-2 space-y-2">
              <button
                @click="openPreview(selectedItem)"
                class="flex items-center justify-center gap-2 w-full rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold py-2.5 transition-colors shadow-xs border-none cursor-pointer"
              >
                <IconEye class="w-4 h-4" />
                Preview File
              </button>
              <a
                :href="selectedItem.file_url"
                target="_blank"
                download
                class="flex items-center justify-center gap-2 w-full rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-750 text-slate-700 dark:text-slate-200 text-xs font-bold py-2.5 transition-colors border-none text-center cursor-pointer shadow-xs"
              >
                <IconDownload class="w-4 h-4" />
                Download
              </a>
              <button
                v-if="selectedItem.can_share"
                @click="openShareModal(selectedItem)"
                class="flex items-center justify-center gap-2 w-full rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-750 text-slate-700 dark:text-slate-200 text-xs font-bold py-2.5 transition-colors border-none cursor-pointer shadow-xs"
              >
                <IconShare2 class="w-4 h-4 text-blue-600 dark:text-blue-400" />
                Share Access ({{ selectedItem.shares_count || 0 }})
              </button>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- Centered Spacious Lightbox Preview Modal Box (White Theme / Dark Theme Adaptive) -->
    <div
      v-if="previewModal.show && previewModal.file"
      class="fixed inset-0 z-[60] bg-slate-900/60 dark:bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4 animate-fade-in select-none"
      @click.self="closePreview"
    >
      <!-- Spacious Modal Window Container (Width: 94vw, Height: 92vh) -->
      <div class="relative w-[96vw] max-w-[94vw] h-[92vh] max-h-[94vh] bg-white dark:bg-slate-900 text-slate-900 dark:text-white rounded-3xl border border-slate-200/90 dark:border-slate-800 shadow-2xl flex flex-col overflow-hidden">

        <!-- Preview Header Bar (Clean light/dark adaptive header with full contrast) -->
        <div class="px-6 py-3.5 bg-slate-50 dark:bg-slate-950 border-b border-slate-200/80 dark:border-slate-800 flex items-center justify-between shrink-0">
          <div class="flex items-center gap-3 min-w-0">
            <div class="p-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-xs shrink-0">
              <component
                :is="getFileIcon(previewModal.file.file_name)"
                class="w-5 h-5"
                :class="getFileIconColor(previewModal.file.file_name)"
              />
            </div>
            <div class="min-w-0">
              <h3 class="text-sm font-bold text-slate-900 dark:text-white truncate max-w-sm sm:max-w-lg" :title="previewModal.file.file_name">
                {{ previewModal.file.file_name }}
              </h3>
              <div class="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2 mt-0.5">
                <span class="font-mono font-semibold">{{ formatBytes(previewModal.file.file_size) }}</span>
                <span v-if="imageDimensions" class="font-mono text-blue-600 dark:text-blue-400 font-bold">• {{ imageDimensions }}</span>
                <span>•</span>
                <span class="truncate">Uploaded by <strong class="text-slate-700 dark:text-slate-200">{{ previewModal.file.owner_full_name }}</strong></span>
              </div>
            </div>
          </div>

          <!-- Image Control Toolbar (Zoom & Rotate for images) -->
          <div v-if="isImage(previewModal.file.file_name)" class="hidden md:flex items-center gap-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl px-2 py-1 shadow-xs">
            <button @click="zoomOut" class="p-1.5 text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors border-none bg-transparent cursor-pointer" title="Zoom Out (-)">
              <IconMinus class="w-4 h-4" />
            </button>
            <span class="text-xs font-mono font-bold px-2 text-slate-700 dark:text-slate-200 select-none">{{ Math.round(imageZoom * 100) }}%</span>
            <button @click="zoomIn" class="p-1.5 text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors border-none bg-transparent cursor-pointer" title="Zoom In (+)">
              <IconPlus class="w-4 h-4" />
            </button>
            <button @click="rotateImage" class="p-1.5 text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors border-none bg-transparent cursor-pointer ml-1 border-l border-slate-200 dark:border-slate-700 pl-2" title="Rotate 90°">
              <IconRotateCw class="w-4 h-4" />
            </button>
            <button @click="resetZoom" class="text-[10px] font-bold text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white px-2 py-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors border-none bg-transparent cursor-pointer">
              Reset
            </button>
          </div>

          <!-- Action Tools (Details Toggle, Download, Share, Close) -->
          <div class="flex items-center gap-2 shrink-0">
            <button
              @click="previewShowDetails = !previewShowDetails"
              class="p-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-750 transition-colors cursor-pointer"
              :class="{ '!bg-blue-600 !text-white !border-blue-600': previewShowDetails }"
              title="Toggle File Info Sidebar"
            >
              <IconInfo class="w-4 h-4" />
            </button>
            <a
              :href="previewModal.file.file_url"
              target="_blank"
              download
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold flex items-center gap-2 transition-colors shadow-xs border-none cursor-pointer"
            >
              <IconDownload class="w-4 h-4" />
              <span class="hidden sm:inline">Download</span>
            </a>
            <button
              v-if="previewModal.file.can_share"
              @click="openShareModal(previewModal.file)"
              class="p-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-750 rounded-xl transition-colors cursor-pointer"
              title="Share File"
            >
              <IconShare2 class="w-4 h-4" />
            </button>
            <button
              @click="closePreview"
              class="p-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-950/40 rounded-xl transition-colors cursor-pointer ml-1"
              title="Close Preview (Esc)"
            >
              <IconX class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- Preview Body Canvas (Spacious preview area) -->
        <div class="flex-1 flex min-h-0 overflow-hidden relative">
          <!-- Navigation Prev Button -->
          <button
            v-if="filteredFiles.length > 1"
            @click="prevPreview"
            class="absolute left-4 sm:left-6 top-1/2 -translate-y-1/2 z-30 p-3.5 bg-white text-slate-800 border border-slate-200 dark:bg-slate-800 dark:text-white dark:border-slate-700 shadow-2xl hover:bg-blue-600 hover:text-white dark:hover:bg-blue-600 dark:hover:text-white rounded-full transition-all cursor-pointer hover:scale-110 active:scale-95"
            title="Previous file (Left arrow)"
          >
            <IconChevronLeft class="w-6 h-6" />
          </button>

          <!-- Center Stage Container (Spacious light/dark background) -->
          <div class="flex-1 flex items-center justify-center p-6 overflow-auto min-h-0 bg-slate-100 dark:bg-slate-950 relative custom-scrollbar">
            <!-- Image Viewer with Large Height & Width Constraints -->
            <template v-if="isImage(previewModal.file.file_name)">
              <div class="flex items-center justify-center min-h-full min-w-full">
                <img
                  :src="previewModal.file.file_url"
                  :alt="previewModal.file.file_name"
                  class="max-h-[76vh] max-w-full object-contain rounded-2xl shadow-xl transition-transform duration-200 ease-out border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900"
                  :style="{ transform: `scale(${imageZoom}) rotate(${imageRotation}deg)` }"
                  @load="onImageLoad"
                />
              </div>
            </template>

            <!-- PDF Viewer -->
            <template v-else-if="isPdf(previewModal.file.file_name)">
              <iframe
                :src="previewModal.file.file_url"
                class="w-full h-[76vh] rounded-2xl bg-white border border-slate-200 dark:border-slate-800 shadow-xl"
              ></iframe>
            </template>

            <!-- Code / Text File Viewer -->
            <template v-else-if="isTextFile(previewModal.file.file_name)">
              <div class="w-full h-[76vh] bg-slate-900 text-slate-100 rounded-2xl border border-slate-800 shadow-xl p-6 flex flex-col font-mono text-xs overflow-hidden">
                <div class="flex items-center justify-between pb-3 border-b border-slate-800 text-slate-400 text-[11px]">
                  <span class="font-bold uppercase tracking-wider text-blue-400">{{ getExtensionLabel(previewModal.file.file_name) }} Source Code</span>
                  <span>{{ textPreviewContent.length }} characters</span>
                </div>
                <div v-if="loadingTextPreview" class="flex-1 flex items-center justify-center text-slate-400">
                  <LoadingIndicator class="w-6 h-6 text-blue-500 animate-spin mr-2" />
                  <span>Loading text preview…</span>
                </div>
                <pre v-else class="flex-1 overflow-auto p-4 bg-slate-950 rounded-xl text-slate-200 custom-scrollbar leading-relaxed whitespace-pre-wrap break-all mt-3">{{ textPreviewContent }}</pre>
              </div>
            </template>

            <!-- Video Viewer -->
            <template v-else-if="isVideo(previewModal.file.file_name)">
              <video
                :src="previewModal.file.file_url"
                controls
                autoplay
                class="max-h-[76vh] max-w-full rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800"
              ></video>
            </template>

            <!-- Audio Viewer -->
            <template v-else-if="isAudio(previewModal.file.file_name)">
              <div class="p-10 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl flex flex-col items-center gap-5 text-center min-w-[22rem]">
                <div class="p-6 bg-amber-500/10 rounded-full border border-amber-500/20">
                  <IconFileAudio class="w-16 h-16 text-amber-500" />
                </div>
                <div>
                  <h4 class="text-base font-bold text-slate-900 dark:text-white max-w-sm truncate">{{ previewModal.file.file_name }}</h4>
                  <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 font-mono">{{ formatBytes(previewModal.file.file_size) }}</p>
                </div>
                <audio :src="previewModal.file.file_url" controls class="w-72 mt-2"></audio>
              </div>
            </template>

            <!-- Generic Fallback Card -->
            <template v-else>
              <div class="p-10 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl flex flex-col items-center gap-4 text-center max-w-md">
                <div class="p-6 bg-blue-600/10 rounded-3xl border border-blue-500/20">
                  <component
                    :is="getFileIcon(previewModal.file.file_name)"
                    class="w-16 h-16"
                    :class="getFileIconColor(previewModal.file.file_name)"
                  />
                </div>
                <div>
                  <h4 class="text-base font-bold text-slate-900 dark:text-white break-all">{{ previewModal.file.file_name }}</h4>
                  <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">No direct inline viewer available for this document format.</p>
                </div>
                <a
                  :href="previewModal.file.file_url"
                  target="_blank"
                  download
                  class="mt-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-2xl text-xs flex items-center gap-2 shadow-md transition-colors border-none cursor-pointer"
                >
                  <IconDownload class="w-4 h-4" />
                  Download Document
                </a>
              </div>
            </template>
          </div>

          <!-- Navigation Next Button -->
          <button
            v-if="filteredFiles.length > 1"
            @click="nextPreview"
            class="absolute right-4 sm:right-6 top-1/2 -translate-y-1/2 z-30 p-3.5 bg-white text-slate-800 border border-slate-200 dark:bg-slate-800 dark:text-white dark:border-slate-700 shadow-2xl hover:bg-blue-600 hover:text-white dark:hover:bg-blue-600 dark:hover:text-white rounded-full transition-all cursor-pointer hover:scale-110 active:scale-95"
            title="Next file (Right arrow)"
          >
            <IconChevronRight class="w-6 h-6" />
          </button>

          <!-- Toggleable Info Sidebar inside Lightbox Box -->
          <div
            v-if="previewShowDetails"
            class="w-80 bg-slate-50 dark:bg-slate-950 border-l border-slate-200/80 dark:border-slate-800 p-6 flex flex-col gap-5 overflow-y-auto custom-scrollbar animate-fade-in shrink-0 text-slate-800 dark:text-slate-200"
          >
            <div class="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
              <h4 class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">File Information</h4>
              <button @click="previewShowDetails = false" class="text-slate-400 hover:text-slate-600 dark:hover:text-white p-1 border-none bg-transparent cursor-pointer">
                <IconX class="w-4 h-4" />
              </button>
            </div>

            <div class="space-y-4 text-xs font-medium">
              <div>
                <span class="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-bold">File Name</span>
                <span class="text-slate-900 dark:text-slate-100 font-bold break-all mt-0.5 block">{{ previewModal.file.file_name }}</span>
              </div>

              <div>
                <span class="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-bold">File Size</span>
                <span class="text-slate-800 dark:text-slate-200 font-mono mt-0.5 block font-semibold">{{ formatBytes(previewModal.file.file_size) }}</span>
              </div>

              <div v-if="imageDimensions">
                <span class="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-bold">Resolution</span>
                <span class="text-blue-600 dark:text-blue-400 font-mono mt-0.5 block font-bold">{{ imageDimensions }}</span>
              </div>

              <div>
                <span class="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-bold">Uploaded By</span>
                <div class="flex items-center gap-2 mt-1">
                  <Avatar :image="previewModal.file.owner_image" :label="previewModal.file.owner_full_name" size="xs" />
                  <span class="text-slate-800 dark:text-slate-200 font-semibold">{{ previewModal.file.owner_full_name }}</span>
                </div>
              </div>

              <div>
                <span class="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-bold">Created Date</span>
                <span class="text-slate-800 dark:text-slate-200 mt-0.5 block font-medium">{{ formatDate(previewModal.file.creation) }}</span>
              </div>

              <div>
                <span class="text-slate-400 dark:text-slate-500 block text-[10px] uppercase font-bold">Upload Source</span>
                <span class="text-slate-800 dark:text-slate-200 font-bold px-2.5 py-1 rounded-md text-[9px] uppercase bg-slate-200 dark:bg-slate-800 mt-1 inline-block">
                  {{ previewModal.file.source }} Upload
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Preview Footer Bar inside modal -->
        <div class="px-6 py-3 bg-slate-50 dark:bg-slate-950 border-t border-slate-200/80 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 shrink-0">
          <span class="font-medium">File {{ previewModal.index + 1 }} of {{ filteredFiles.length }}</span>
          <span>Use <kbd class="px-1.5 py-0.5 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700 font-mono text-[10px] shadow-xs">←</kbd> <kbd class="px-1.5 py-0.5 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700 font-mono text-[10px] shadow-xs">→</kbd> to navigate, <kbd class="px-1.5 py-0.5 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700 font-mono text-[10px] shadow-xs">Esc</kbd> to close</span>
        </div>
      </div>
    </div>

    <!-- Floating Upload Queue Widget (Strict Z-index: z-40) -->
    <div
      v-if="uploadQueue.length > 0"
      class="fixed bottom-5 right-5 z-40 w-80 md:w-96 bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden text-xs transition-all duration-300"
    >
      <div class="bg-slate-900 text-white px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-2.5 font-bold">
          <LoadingIndicator v-if="uploading" class="w-4 h-4 text-blue-400 animate-spin" />
          <IconCheck v-else class="w-4 h-4 text-emerald-400" />
          <span>{{ uploading ? `Uploading ${uploadQueue.filter(x => x.status === 'uploading').length} items…` : 'Uploads complete' }}</span>
        </div>

        <div class="flex items-center gap-1">
          <button
            @click="uploadWidgetMinimized = !uploadWidgetMinimized"
            class="p-1 text-slate-400 hover:text-white border-none bg-transparent cursor-pointer rounded-lg"
          >
            <component :is="uploadWidgetMinimized ? IconMaximize2 : IconMinimize2" class="w-4 h-4" />
          </button>
          <button
            @click="clearUploadQueue"
            class="p-1 text-slate-400 hover:text-white border-none bg-transparent cursor-pointer rounded-lg"
          >
            <IconX class="w-4 h-4" />
          </button>
        </div>
      </div>

      <div v-if="!uploadWidgetMinimized" class="max-h-56 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800 custom-scrollbar p-2">
        <div v-for="item in uploadQueue" :key="item.id" class="p-2.5 flex items-center gap-3">
          <component :is="getFileIcon(item.name)" class="w-5 h-5 shrink-0 text-blue-500" />
          <div class="min-w-0 flex-1">
            <div class="font-bold text-slate-800 dark:text-slate-100 truncate" :title="item.name">{{ item.name }}</div>
            <div class="w-full bg-slate-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
              <div
                class="bg-blue-600 h-full rounded-full transition-all duration-300"
                :style="{ width: `${item.progress}%` }"
                :class="{ '!bg-emerald-500': item.status === 'completed', '!bg-rose-500': item.status === 'error' }"
              ></div>
            </div>
          </div>

          <div class="shrink-0 text-right">
            <IconCheck v-if="item.status === 'completed'" class="w-4 h-4 text-emerald-500" />
            <IconAlertCircle v-else-if="item.status === 'error'" class="w-4 h-4 text-rose-500" />
            <span v-else class="font-mono text-[10px] font-bold text-slate-400">{{ item.progress }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirm File / Bulk Deletion Dialog (Teleported to Body for absolute top Z-index) -->
    <Teleport to="body">
      <Dialog
        v-model="deleteConfirm.show"
        :disable-outside-click-to-close="true"
        class="frappe-dialog-overlay-top"
        :options="{
          title: deleteConfirm.isBulk ? 'Delete Selected Files' : 'Delete File Permanently?',
          size: 'sm',
          actions: [
            {
              label: deleteConfirm.isBulk ? 'Delete Files' : 'Delete File',
              variant: 'solid',
              theme: 'red',
              onClick: deleteConfirm.isBulk ? confirmBulkDelete : confirmDelete
            },
            {
              label: 'Cancel',
              variant: 'ghost',
              onClick: () => (deleteConfirm.show = false)
            }
          ]
        }"
      >
        <template #body-content>
          <p class="text-sm text-slate-600 dark:text-slate-300 leading-relaxed py-2">
            <span v-if="deleteConfirm.isBulk">
              Are you sure you want to permanently delete <span class="font-bold text-slate-900 dark:text-white">{{ deleteConfirm.count }}</span> selected file(s)? This action cannot be undone.
            </span>
            <span v-else>
              Are you sure you want to permanently delete <b class="text-slate-900 dark:text-white break-all">"{{ deleteConfirm.file?.file_name }}"</b>? It will be removed from Drive.
            </span>
          </p>
        </template>
      </Dialog>

      <!-- New Folder Dialog -->
      <Dialog
        v-model="showNewFolderModal"
        :disable-outside-click-to-close="true"
        class="frappe-dialog-overlay-top"
        :options="{
          title: 'Create New Folder',
          size: 'sm',
          actions: [
            {
              label: 'Create Folder',
              variant: 'solid',
              loading: creatingFolder,
              disabled: !newFolderName.trim(),
              onClick: createFolder
            },
            {
              label: 'Cancel',
              variant: 'ghost',
              onClick: () => { showNewFolderModal = false; newFolderName = ''; }
            }
          ]
        }"
      >
        <template #body-content>
          <div class="space-y-4 py-2">
            <FormControl
              type="text"
              label="Folder Name *"
              v-model="newFolderName"
              placeholder="Enter folder name…"
              @keyup.enter="createFolder"
            />
          </div>
        </template>
      </Dialog>

      <!-- Share File Dialog -->
      <Dialog
        v-model="shareModal.show"
        :disable-outside-click-to-close="true"
        class="frappe-dialog-overlay-top"
        :options="{
          title: shareModal.isBulk ? `Share ${shareModal.selectedCount} Selected Files` : 'Share File Access',
          size: 'lg',
          actions: [
            {
              label: 'Share Access',
              variant: 'solid',
              loading: shareModal.submitting,
              disabled: !shareModal.targetUser,
              onClick: () => (shareModal.isBulk ? executeBulkShare() : executeShare())
            },
            {
              label: 'Cancel',
              variant: 'ghost',
              onClick: () => (shareModal.show = false)
            }
          ]
        }"
      >
        <template #body-content>
          <div class="space-y-5 py-2">
            <div v-if="!shareModal.isBulk && shareModal.file" class="p-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center gap-2">
              <IconFile class="w-4 h-4 text-blue-600 dark:text-blue-400 shrink-0" />
              <span class="text-xs font-bold text-slate-800 dark:text-slate-100 truncate" :title="shareModal.file.file_name">
                {{ shareModal.file.file_name }}
              </span>
            </div>

            <div v-else-if="shareModal.isBulk" class="p-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl">
              <span class="text-xs font-bold text-slate-700 dark:text-slate-300">
                Sharing {{ selectedItems ? selectedItems.length : 0 }} selected file(s)
              </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
              <div class="md:col-span-2">
                <FormControl
                  type="select"
                  label="Team Member *"
                  v-model="shareModal.targetUser"
                  :options="availableShareUserOptions"
                  placeholder="Select team member..."
                />
              </div>
              <div>
                <FormControl
                  type="select"
                  label="Access Level *"
                  v-model="shareModal.permission"
                  :options="permissionOptions"
                />
              </div>
            </div>
          </div>
        </template>
      </Dialog>
    </Teleport>
  </div>
</div>
</template>

<script setup>
import dayjs from "dayjs"
import { Autocomplete, Avatar, Badge, Button, Dialog, FeatherIcon, FormControl, LoadingIndicator, Popover, Select, Tabs, createResource } from "frappe-ui"
import { computed, reactive, ref, watch, onMounted, onUnmounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { session } from "../data/session"

import IconAlertCircle from "~icons/lucide/alert-circle"
import IconArrowLeft from "~icons/lucide/arrow-left"
import IconBriefcase from "~icons/lucide/briefcase"
import IconCheck from "~icons/lucide/check"
import IconChevronLeft from "~icons/lucide/chevron-left"
import IconChevronRight from "~icons/lucide/chevron-right"
import IconDownload from "~icons/lucide/download"
import IconEye from "~icons/lucide/eye"
import IconFile from "~icons/lucide/file"
import IconFileArchive from "~icons/lucide/file-archive"
import IconFileAudio from "~icons/lucide/file-audio"
import IconFileImage from "~icons/lucide/file-image"
import IconFileSpreadsheet from "~icons/lucide/file-spreadsheet"
import IconFileText from "~icons/lucide/file-text"
import IconFileVideo from "~icons/lucide/file-video"
import IconFilter from "~icons/lucide/filter"
import IconFolder from "~icons/lucide/folder"
import IconFolderOpen from "~icons/lucide/folder-open"
import IconFolderPlus from "~icons/lucide/folder-plus"
import IconHome from "~icons/lucide/home"
import IconInfo from "~icons/lucide/info"
import IconLayoutGrid from "~icons/lucide/layout-grid"
import IconList from "~icons/lucide/list"
import IconLock from "~icons/lucide/lock"
import IconMaximize2 from "~icons/lucide/maximize-2"
import IconMinimize2 from "~icons/lucide/minimize-2"
import IconMinus from "~icons/lucide/minus"
import IconPlus from "~icons/lucide/plus"
import IconRefreshCcw from "~icons/lucide/refresh-ccw"
import IconRotateCw from "~icons/lucide/rotate-cw"
import IconSearch from "~icons/lucide/search"
import IconShare2 from "~icons/lucide/share-2"
import IconTicket from "~icons/lucide/ticket"
import IconTrash2 from "~icons/lucide/trash-2"
import IconUploadCloud from "~icons/lucide/upload-cloud"
import IconUser from "~icons/lucide/user"
import IconX from "~icons/lucide/x"

const router = useRouter()
const route = useRoute()

// Reactive States
const currentPath = ref("/")
const folders = ref([])
const files = ref([])
const selectedItems = ref([])
const loading = ref(false)

const searchQuery = ref("")
const fileTypeTabIndex = ref(0)
const fileTypeTabs = [
	{ label: "All Types", value: "All" },
	{ label: "Documents", value: "Documents" },
	{ label: "Images", value: "Images" },
	{ label: "Audio/Video", value: "Audio/Video" },
	{ label: "Others", value: "Others" },
]
const fileTypeFilter = ref("All")
const sourceFilter = ref("All")
const accessFilter = ref("All")

watch(fileTypeFilter, (val) => {
	const idx = fileTypeTabs.findIndex((t) => t.value === val)
	fileTypeTabIndex.value = idx !== -1 ? idx : 0
})

watch(fileTypeTabIndex, (idx) => {
	fileTypeFilter.value = fileTypeTabs[idx]?.value || "All"
})

// Filter options for Autocomplete dropdowns
const fileTypeOptions = [
	{ label: "All Types", value: "All" },
	{ label: "Documents", value: "Documents" },
	{ label: "Images", value: "Images" },
	{ label: "Audio/Video", value: "Audio/Video" },
	{ label: "Others", value: "Others" },
]

const sourceOptions = [
	{ label: "All Sources", value: "All" },
	{ label: "Direct Upload", value: "Direct" },
	{ label: "Ticket Attachment", value: "Ticket" },
	{ label: "Task Attachment", value: "Task" },
]

const accessOptions = [
	{ label: "All Accessible", value: "All" },
	{ label: "My Files", value: "My" },
	{ label: "Shared With Me", value: "Shared" },
]

// Popover refs for Autocomplete programmatic toggling
const fileTypeAutocomplete = ref(null)
const sourceAutocomplete = ref(null)
const accessAutocomplete = ref(null)

const FILTERABLE_FIELDS = [
	{ label: "File Type", value: "fileTypeFilter", key: "fileTypeFilter" },
	{ label: "Source", value: "sourceFilter", key: "sourceFilter" },
	{ label: "Access Level", value: "accessFilter", key: "accessFilter" },
]

const activeFilterRules = ref([])

function syncActiveFilterRules() {
	const newRules = []
	if (fileTypeFilter.value !== "All") {
		newRules.push({ id: "rule_fileTypeFilter", field: "fileTypeFilter", value: fileTypeFilter.value })
	}
	if (sourceFilter.value !== "All") {
		newRules.push({ id: "rule_sourceFilter", field: "sourceFilter", value: sourceFilter.value })
	}
	if (accessFilter.value !== "All") {
		newRules.push({ id: "rule_accessFilter", field: "accessFilter", value: accessFilter.value })
	}
	if (newRules.length === 0) {
		newRules.push({ id: "rule_" + Date.now(), field: "fileTypeFilter", value: "" })
	}
	activeFilterRules.value = newRules
}

function addFilterRule() {
	const unusedField = FILTERABLE_FIELDS.find(
		(f) => !activeFilterRules.value.some((r) => r.field === f.value)
	)
	const field = unusedField ? unusedField.value : "fileTypeFilter"
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
		if (removed.field === "fileTypeFilter") fileTypeFilter.value = "All"
		if (removed.field === "sourceFilter") sourceFilter.value = "All"
		if (removed.field === "accessFilter") accessFilter.value = "All"
	}
	if (activeFilterRules.value.length === 0) {
		activeFilterRules.value.push({
			id: "rule_" + Date.now(),
			field: "fileTypeFilter",
			value: "",
		})
	}
}

function applyFilterRules() {
	FILTERABLE_FIELDS.forEach((f) => {
		const hasRule = activeFilterRules.value.some((r) => r.field === f.key)
		if (!hasRule) {
			if (f.key === "fileTypeFilter") fileTypeFilter.value = "All"
			if (f.key === "sourceFilter") sourceFilter.value = "All"
			if (f.key === "accessFilter") accessFilter.value = "All"
		}
	})
	activeFilterRules.value.forEach((r) => {
		if (r.field === "fileTypeFilter" && r.value) fileTypeFilter.value = r.value
		if (r.field === "sourceFilter" && r.value) sourceFilter.value = r.value
		if (r.field === "accessFilter" && r.value) accessFilter.value = r.value
	})
}

function getFieldOptionsForSelect(fieldKey) {
	if (fieldKey === "fileTypeFilter") return fileTypeOptions.filter((o) => o.value !== "All")
	if (fieldKey === "sourceFilter") return sourceOptions.filter((o) => o.value !== "All")
	if (fieldKey === "accessFilter") return accessOptions.filter((o) => o.value !== "All")
	return []
}

function getFilterLabel(fieldKey, val, defaultText) {
	if (!val || val === "All") return defaultText
	if (fieldKey === "fileTypeFilter") {
		const found = fileTypeOptions.find((o) => o.value === val)
		return found ? found.label : val
	}
	if (fieldKey === "sourceFilter") {
		const found = sourceOptions.find((o) => o.value === val)
		return found ? found.label : val
	}
	if (fieldKey === "accessFilter") {
		const found = accessOptions.find((o) => o.value === val)
		return found ? found.label : val
	}
	return val
}

const activeFilterCount = computed(() => {
	let count = 0
	if (fileTypeFilter.value !== "All") count++
	if (sourceFilter.value !== "All") count++
	if (accessFilter.value !== "All") count++
	return count
})

const hasActiveFilters = computed(() => {
	return (
		searchQuery.value !== "" ||
		fileTypeFilter.value !== "All" ||
		sourceFilter.value !== "All" ||
		accessFilter.value !== "All"
	)
})

const hasActiveFilterChips = computed(() => activeFilterChips.value.length > 0)

const activeFilterChips = computed(() => {
	const chips = []
	if (fileTypeFilter.value !== "All") {
		chips.push({ key: "fileTypeFilter", label: "File Type", displayValue: getFilterLabel("fileTypeFilter", fileTypeFilter.value) })
	}
	if (sourceFilter.value !== "All") {
		chips.push({ key: "sourceFilter", label: "Source", displayValue: getFilterLabel("sourceFilter", sourceFilter.value) })
	}
	if (accessFilter.value !== "All") {
		chips.push({ key: "accessFilter", label: "Access Level", displayValue: getFilterLabel("accessFilter", accessFilter.value) })
	}
	return chips
})

function removeFilterByKey(key) {
	if (key === "fileTypeFilter") fileTypeFilter.value = "All"
	if (key === "sourceFilter") sourceFilter.value = "All"
	if (key === "accessFilter") accessFilter.value = "All"
}

function toggleMyFiles() {
	if (accessFilter.value === "My") {
		accessFilter.value = "All"
	} else {
		accessFilter.value = "My"
	}
}

const viewMode = ref("grid")

function viewBtnClass(mode) {
	return [
		"p-1 rounded-md transition-all cursor-pointer",
		viewMode.value === mode
			? "bg-white dark:bg-slate-700 shadow-xs text-blue-600 dark:text-blue-400 font-medium"
			: "text-slate-400 hover:text-slate-600 dark:hover:text-slate-300",
	]
}

const shareableUsers = ref([])
const shareModal = reactive({
	show: false,
	file: null,
	loading: false,
	submitting: false,
	targetUser: "",
	permission: "read",
	owner: null,
	shares: [],
	isBulk: false,
	selectedCount: 0,
})

const selectedItem = ref(null)

const toast = ref({ show: false, message: "", type: "success" })
const deleteConfirm = ref({ show: false, file: null, isBulk: false, count: 0 })

const showNewFolderModal = ref(false)
const newFolderName = ref("")
const creatingFolder = ref(false)

const fileInput = ref(null)
const dragActive = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadingFileName = ref("")
const uploadQueue = ref([])
const uploadWidgetMinimized = ref(false)

// Lightbox Preview Modal & Zoom States
const previewModal = reactive({
	show: false,
	file: null,
	index: -1,
})
const imageZoom = ref(1)
const imageRotation = ref(0)
const imageDimensions = ref("")
const previewShowDetails = ref(false)
const textPreviewContent = ref("")
const loadingTextPreview = ref(false)

function zoomIn() {
	if (imageZoom.value < 3) imageZoom.value = Math.round((imageZoom.value + 0.25) * 100) / 100
}

function zoomOut() {
	if (imageZoom.value > 0.5) imageZoom.value = Math.round((imageZoom.value - 0.25) * 100) / 100
}

function resetZoom() {
	imageZoom.value = 1
	imageRotation.value = 0
	imageDimensions.value = ""
	textPreviewContent.value = ""
}

function rotateImage() {
	imageRotation.value = (imageRotation.value + 90) % 360
}

function onImageLoad(e) {
	if (e?.target) {
		imageDimensions.value = `${e.target.naturalWidth} × ${e.target.naturalHeight} px`
	}
}

function isTextFile(filename) {
	if (!filename) return false
	const ext = filename.split(".").pop().toLowerCase()
	return ["txt", "md", "csv", "json", "py", "js", "html", "css", "log", "xml", "yml", "yaml"].includes(ext)
}

async function fetchTextPreview(url) {
	textPreviewContent.value = ""
	loadingTextPreview.value = true
	try {
		const res = await fetch(url)
		if (res.ok) {
			const txt = await res.text()
			textPreviewContent.value = txt.slice(0, 50000)
		} else {
			textPreviewContent.value = "Unable to load text preview."
		}
	} catch (e) {
		textPreviewContent.value = "Failed to load text preview content."
	} finally {
		loadingTextPreview.value = false
	}
}

// Clear Filters handler
function resetFilters() {
	searchQuery.value = ""
	fileTypeFilter.value = "All"
	sourceFilter.value = "All"
	accessFilter.value = "All"
}

// Lightbox Preview Control Functions
function openPreview(file) {
	if (!file || file.is_folder) return
	const idx = filteredFiles.value.findIndex((f) => f.name === file.name)
	previewModal.file = file
	previewModal.index = idx !== -1 ? idx : 0
	previewModal.show = true
	resetZoom()
	if (isTextFile(file.file_name)) {
		fetchTextPreview(file.file_url)
	}
}

function closePreview() {
	previewModal.show = false
	previewModal.file = null
	previewModal.index = -1
	resetZoom()
}

function nextPreview() {
	if (!filteredFiles.value || filteredFiles.value.length === 0) return
	previewModal.index = (previewModal.index + 1) % filteredFiles.value.length
	previewModal.file = filteredFiles.value[previewModal.index]
	resetZoom()
	if (isTextFile(previewModal.file.file_name)) {
		fetchTextPreview(previewModal.file.file_url)
	}
}

function prevPreview() {
	if (!filteredFiles.value || filteredFiles.value.length === 0) return
	previewModal.index = (previewModal.index - 1 + filteredFiles.value.length) % filteredFiles.value.length
	previewModal.file = filteredFiles.value[previewModal.index]
	resetZoom()
	if (isTextFile(previewModal.file.file_name)) {
		fetchTextPreview(previewModal.file.file_url)
	}
}

function handleKeydown(e) {
	if (!previewModal.show) return
	if (e.key === "Escape") closePreview()
	if (e.key === "ArrowRight") nextPreview()
	if (e.key === "ArrowLeft") prevPreview()
}

onMounted(() => {
	window.addEventListener("keydown", handleKeydown)
	if (!session.isTicketRaiser) {
		loadPathContents(currentPath.value)
	}
})

onUnmounted(() => {
	window.removeEventListener("keydown", handleKeydown)
})

// Path Parts Helper for Breadcrumbs
const rawPathParts = computed(() => {
	if (currentPath.value === "/") return []
	return currentPath.value.split("/").filter((x) => x !== "")
})

function getCleanName(name) {
	if (name && name.includes("__")) {
		return name.split("__")[0]
	}
	return name
}

const currentPathName = computed(() => {
	const parts = rawPathParts.value
	if (parts.length === 0) return "Drive"
	return getCleanName(parts[parts.length - 1])
})

const uploadAllowed = computed(() => {
	if (session.isTicketRaiser) return false
	const p = currentPath.value
	if (p === "/" || p === "/Clients" || p === "/Departments") {
		return false
	}
	return true
})

const dbFolder = ref("Home")

// API resources
const folderContentsResource = createResource({
	url: "tactix.api.drive.get_folder_contents",
	onSuccess(data) {
		folders.value = data.folders || []
		files.value = data.files || []
		currentPath.value = data.current_path || "/"
		dbFolder.value = data.db_folder || "Home"
	},
})

const deleteFileResource = createResource({
	url: "tactix.api.drive.delete_explorer_file",
})

const createFolderResource = createResource({
	url: "tactix.api.drive.create_explorer_folder",
})

const getShareableUsersResource = createResource({
	url: "tactix.api.drive.get_shareable_users",
	onSuccess(data) {
		shareableUsers.value = data || []
	},
})

const getFileSharesResource = createResource({
	url: "tactix.api.drive.get_file_shares",
})

const shareFileResource = createResource({
	url: "tactix.api.drive.share_file",
})

const unshareFileResource = createResource({
	url: "tactix.api.drive.unshare_file",
})

const availableShareUsers = computed(() => {
	if (!shareModal.owner) return shareableUsers.value
	const existingUsers = new Set([
		shareModal.owner.user,
		...shareModal.shares.map((s) => s.user),
	])
	return shareableUsers.value.filter((u) => !existingUsers.has(u.name))
})

const availableShareUserOptions = computed(() => {
	return availableShareUsers.value.map((u) => ({
		label: `${u.full_name} (${u.primary_role})`,
		value: u.name,
	}))
})

const permissionOptions = [
	{ label: "Can View", value: "read" },
	{ label: "Can Edit", value: "write" },
]

function isSelected(name) {
	return selectedItems.value.includes(name)
}

function toggleSelect(name) {
	if (isSelected(name)) {
		selectedItems.value = selectedItems.value.filter((id) => id !== name)
	} else {
		selectedItems.value.push(name)
	}
}

const isAllSelected = computed(() => {
	if (filteredFiles.value.length === 0) return false
	return filteredFiles.value.every((f) => selectedItems.value.includes(f.name))
})

function toggleSelectAll() {
	if (isAllSelected.value) {
		selectedItems.value = []
	} else {
		selectedItems.value = filteredFiles.value.map((f) => f.name)
	}
}

function clearSelection() {
	selectedItems.value = []
}

function toggleDetailsPanel() {
	if (selectedItem.value) {
		selectedItem.value = null
	} else if (filteredFiles.value.length > 0) {
		selectedItem.value = filteredFiles.value[0]
	}
}

const shareMultipleFilesResource = createResource({
	url: "tactix.api.drive.share_multiple_files",
})

const deleteMultipleFilesResource = createResource({
	url: "tactix.api.drive.delete_multiple_files",
})

async function openBulkShareModal() {
	if (selectedItems.value.length === 0) return
	shareModal.isBulk = true
	shareModal.selectedCount = selectedItems.value.length
	shareModal.file = null
	shareModal.show = true
	shareModal.loading = false
	shareModal.targetUser = ""
	shareModal.permission = "read"
	shareModal.shares = []
	shareModal.owner = null

	if (shareableUsers.value.length === 0) {
		getShareableUsersResource.fetch()
	}
}

async function executeBulkShare() {
	if (selectedItems.value.length === 0 || !shareModal.targetUser) return
	shareModal.submitting = true
	try {
		await shareMultipleFilesResource.submit({
			file_names: JSON.stringify(selectedItems.value),
			target_user: shareModal.targetUser,
			permission: shareModal.permission,
		})
		showToast(`Shared ${selectedItems.value.length} files successfully`, "success")
		shareModal.show = false
		clearSelection()
		loadPathContents(currentPath.value)
	} catch (err) {
		showToast(err.message || "Failed to share files", "error")
	} finally {
		shareModal.submitting = false
	}
}

async function promptBulkDelete() {
	if (selectedItems.value.length === 0) return
	deleteConfirm.value = {
		show: true,
		isBulk: true,
		count: selectedItems.value.length,
	}
}

async function openShareModal(file) {
	shareModal.isBulk = false
	shareModal.selectedCount = 1
	shareModal.file = file
	shareModal.show = true
	shareModal.loading = true
	shareModal.targetUser = ""
	shareModal.permission = "read"

	if (shareableUsers.value.length === 0) {
		getShareableUsersResource.fetch()
	}

	try {
		const res = await getFileSharesResource.fetch({ file_name: file.name })
		shareModal.owner = res.owner
		shareModal.shares = res.shares || []
	} catch (err) {
		showToast(err.message || "Failed to load file access permissions", "error")
	} finally {
		shareModal.loading = false
	}
}

async function executeShare() {
	if (!shareModal.file || !shareModal.targetUser) return
	shareModal.submitting = true
	try {
		await shareFileResource.submit({
			file_name: shareModal.file.name,
			target_user: shareModal.targetUser,
			permission: shareModal.permission,
		})
		showToast("File shared successfully", "success")
		shareModal.targetUser = ""
		const res = await getFileSharesResource.fetch({ file_name: shareModal.file.name })
		shareModal.owner = res.owner
		shareModal.shares = res.shares || []
		loadPathContents(currentPath.value)
	} catch (err) {
		showToast(err.message || "Failed to share file", "error")
	} finally {
		shareModal.submitting = false
	}
}

async function createFolder() {
	if (!newFolderName.value || !newFolderName.value.trim()) return
	creatingFolder.value = true
	try {
		await createFolderResource.submit({
			path: currentPath.value,
			folder_name: newFolderName.value.trim(),
		})
		showToast(`Folder "${newFolderName.value}" created successfully`, "success")
		newFolderName.value = ""
		showNewFolderModal.value = false
		loadPathContents(currentPath.value)
	} catch (err) {
		showToast(err.message || "Failed to create folder", "error")
	} finally {
		creatingFolder.value = false
	}
}

function loadPathContents(path) {
	if (session.isTicketRaiser) return
	loading.value = true
	selectedItem.value = null
	selectedItems.value = []
	folderContentsResource
		.fetch({ path })
		.then(() => {
			loading.value = false
		})
		.catch((err) => {
			loading.value = false
			showToast(err.message || "Failed to load directory items", "error")
		})
}

function fetchPath(path) {
	const clean = path.startsWith("/") ? path.slice(1) : path
	router.push(`/drive/${clean}`)
}

function refresh() {
	loadPathContents(currentPath.value)
}

watch(
	() => route.params.folderPath,
	(newVal) => {
		if (session.isTicketRaiser || !route.path.includes("drive")) return
		let path = "/"
		if (newVal) {
			path = Array.isArray(newVal) ? "/" + newVal.join("/") : "/" + newVal
		}
		currentPath.value = path
		loadPathContents(path)
	},
	{ immediate: true },
)

function getFolderIconColorClass(folderPath) {
	if (folderPath?.startsWith("/Shared")) {
		return "bg-amber-500/10 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400"
	}
	if (folderPath?.startsWith("/Clients")) {
		return "bg-blue-500/10 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400"
	}
	if (folderPath?.startsWith("/Departments")) {
		return "bg-emerald-500/10 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400"
	}
	return "bg-slate-500/10 text-slate-600 dark:bg-slate-500/20 dark:text-slate-400"
}

function getFolderTypeLabel(folderPath) {
	if (folderPath?.startsWith("/Shared")) return "Shared"
	if (folderPath?.startsWith("/Clients")) return "Client"
	if (folderPath?.startsWith("/Departments")) return "Dept"
	return "Standard"
}

function getFileIconBg(filename) {
	if (!filename) return "bg-slate-100 dark:bg-slate-800"
	const ext = filename.split(".").pop().toLowerCase()
	if (["pdf"].includes(ext)) return "bg-rose-50 dark:bg-rose-950/40 border border-rose-100 dark:border-rose-900/40"
	if (["png", "jpg", "jpeg", "gif", "svg", "webp"].includes(ext))
		return "bg-sky-50 dark:bg-sky-950/40 border border-sky-100 dark:border-sky-900/40"
	if (["xls", "xlsx", "csv", "ods"].includes(ext))
		return "bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-100 dark:border-emerald-900/40"
	if (["mp4", "webm", "mkv", "avi", "mov"].includes(ext))
		return "bg-purple-50 dark:bg-purple-950/40 border border-purple-100 dark:border-purple-900/40"
	if (["mp3", "wav", "ogg", "aac", "flac"].includes(ext))
		return "bg-amber-50 dark:bg-amber-950/40 border border-amber-100 dark:border-amber-900/40"
	if (["zip", "tar", "gz", "rar", "7z"].includes(ext))
		return "bg-orange-50 dark:bg-orange-950/40 border border-orange-100 dark:border-orange-900/40"
	return "bg-blue-50 dark:bg-blue-950/40 border border-blue-100 dark:border-blue-900/40"
}

function getExtensionLabel(filename) {
	if (!filename) return "FILE"
	return filename.split(".").pop().toUpperCase()
}

function selectItem(item) {
	selectedItem.value = item
}

function navigateUp() {
	const path = currentPath.value
	if (path === "/") return
	const parts = path.split("/").filter((x) => x !== "")
	parts.pop()
	const parent = "/" + parts.join("/")
	fetchPath(parent)
}

function navigateToBreadcrumb(idx) {
	const parts = rawPathParts.value.slice(0, idx + 1)
	const target = "/" + parts.join("/")
	fetchPath(target)
}

function getCsrfToken() {
	if (window.csrf_token) return window.csrf_token
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	return cookies.get("system_csrf_token") || ""
}

function onWindowDragEnter() {
	if (uploadAllowed.value && !previewModal.show && !shareModal.show && !deleteConfirm.show && !showNewFolderModal.value) {
		dragActive.value = true
	}
}

function onWindowDragLeave(e) {
	if (e.clientX <= 0 || e.clientY <= 0 || e.clientX >= window.innerWidth || e.clientY >= window.innerHeight) {
		dragActive.value = false
	}
}

function handleDrop(e) {
	dragActive.value = false
	if (!uploadAllowed.value) return
	const filesList = e.dataTransfer.files
	if (filesList && filesList.length > 0) {
		uploadFiles(filesList)
	}
}

function handleFileSelect(e) {
	const filesList = e.target.files
	if (filesList && filesList.length > 0) {
		uploadFiles(filesList)
	}
}

async function uploadFiles(filesList) {
	const path = currentPath.value
	let doctype = "File"
	let docname = "Company Shared"

	if (path.startsWith("/Clients/")) {
		doctype = "Tactix Customer"
		const parts = path.split("/").filter((x) => x)
		docname = parts[1]
	} else if (path.startsWith("/Departments/")) {
		doctype = "Tactix Department"
		const parts = path.split("/").filter((x) => x)
		docname = parts[1]
	} else if (path.startsWith("/Shared")) {
		doctype = "User"
		docname = "Administrator"
	}

	uploading.value = true
	uploadWidgetMinimized.value = false

	for (let i = 0; i < filesList.length; i++) {
		const fileObj = filesList[i]
		const queueItem = reactive({
			id: Math.random().toString(36).substring(7),
			name: fileObj.name,
			size: fileObj.size,
			progress: 10,
			status: "uploading",
		})
		uploadQueue.value.unshift(queueItem)
		uploadingFileName.value = fileObj.name

		const formData = new FormData()
		formData.append("file", fileObj)
		formData.append("is_private", 0)
		formData.append("doctype", doctype)
		formData.append("docname", docname)
		formData.append("folder", dbFolder.value || "Home")

		try {
			const csrfToken = getCsrfToken()
			queueItem.progress = 50

			const response = await fetch("/api/method/upload_file", {
				method: "POST",
				headers: {
					"X-Frappe-CSRF-Token": csrfToken,
				},
				body: formData,
			})

			if (!response.ok) {
				throw new Error("File upload failed.")
			}

			queueItem.progress = 100
			queueItem.status = "completed"
			showToast(`Uploaded "${fileObj.name}"`, "success")
		} catch (err) {
			queueItem.status = "error"
			showToast(`Failed uploading "${fileObj.name}"`, "error")
		}
	}

	uploading.value = false
	uploadingFileName.value = ""

	loadPathContents(currentPath.value)
}

function clearUploadQueue() {
	uploadQueue.value = []
}

function promptDelete(file) {
	deleteConfirm.value = {
		show: true,
		file,
		isBulk: false,
		count: 1,
	}
}

async function confirmDelete() {
	if (!deleteConfirm.value.file) return
	const fileName = deleteConfirm.value.file.name
	deleteConfirm.value.show = false
	loading.value = true

	try {
		await deleteFileResource.submit({ file_name: fileName })
		showToast("File deleted successfully", "success")
		loadPathContents(currentPath.value)
	} catch (err) {
		loading.value = false
		showToast(err.message || "Failed to delete file", "error")
	}
}

async function confirmBulkDelete() {
	if (selectedItems.value.length === 0) return
	deleteConfirm.value.show = false
	loading.value = true

	try {
		await deleteMultipleFilesResource.submit({
			file_names: JSON.stringify(selectedItems.value),
		})
		showToast(`Deleted ${selectedItems.value.length} files`, "success")
		clearSelection()
		loadPathContents(currentPath.value)
	} catch (err) {
		loading.value = false
		showToast(err.message || "Failed to delete selected files", "error")
	}
}

function showToast(message, type = "success") {
	toast.value = {
		show: true,
		message,
		type,
	}
	setTimeout(() => {
		toast.value.show = false
	}, 4000)
}

function formatBytes(bytes) {
	if (!bytes) return "0 B"
	const k = 1024
	const sizes = ["Bytes", "KB", "MB", "GB"]
	const i = Math.floor(Math.log(bytes) / Math.log(k))
	return `${Number.parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

function formatDate(creation) {
	if (!creation) return ""
	return dayjs(creation).format("MMM DD, YYYY")
}

function getFileIconColor(filename) {
	if (!filename) return "text-slate-400"
	const ext = filename.split(".").pop().toLowerCase()
	if (["pdf"].includes(ext)) return "text-rose-500"
	if (["png", "jpg", "jpeg", "gif", "svg", "webp"].includes(ext)) return "text-sky-500"
	if (["xls", "xlsx", "csv", "ods"].includes(ext)) return "text-emerald-500"
	if (["mp4", "webm", "mkv", "avi", "mov"].includes(ext)) return "text-purple-500"
	if (["mp3", "wav", "ogg", "aac", "flac"].includes(ext)) return "text-amber-500"
	if (["zip", "tar", "gz", "rar", "7z"].includes(ext)) return "text-orange-500"
	return "text-blue-500"
}

function getFileIcon(filename) {
	if (!filename) return IconFile
	const ext = filename.split(".").pop().toLowerCase()
	if (["pdf", "doc", "docx", "txt", "rtf", "odt"].includes(ext)) return IconFileText
	if (["png", "jpg", "jpeg", "gif", "svg", "webp"].includes(ext)) return IconFileImage
	if (["xls", "xlsx", "csv", "ods"].includes(ext)) return IconFileSpreadsheet
	if (["mp4", "webm", "mkv", "avi", "mov"].includes(ext)) return IconFileVideo
	if (["mp3", "wav", "ogg", "aac", "flac"].includes(ext)) return IconFileAudio
	if (["zip", "tar", "gz", "rar", "7z"].includes(ext)) return IconFileArchive
	return IconFile
}

function isImage(filename) {
	if (!filename) return false
	const ext = filename.split(".").pop().toLowerCase()
	return ["png", "jpg", "jpeg", "gif", "svg", "webp"].includes(ext)
}

function isPdf(filename) {
	if (!filename) return false
	const ext = filename.split(".").pop().toLowerCase()
	return ext === "pdf"
}

function isVideo(filename) {
	if (!filename) return false
	const ext = filename.split(".").pop().toLowerCase()
	return ["mp4", "webm", "mkv", "avi", "mov"].includes(ext)
}

function isAudio(filename) {
	if (!filename) return false
	const ext = filename.split(".").pop().toLowerCase()
	return ["mp3", "wav", "ogg", "aac", "flac"].includes(ext)
}

function getSourceBadgeClass(source) {
	if (source === "Direct" || source === "Shared") return "bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300"
	if (source === "Ticket") return "bg-sky-50 dark:bg-sky-950/40 text-sky-700 dark:text-sky-300"
	if (source === "Task") return "bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300"
	return "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300"
}

function isDeletable(file) {
	if (session.isTicketRaiser) return false
	return true
}

const filteredFiles = computed(() => {
	let list = files.value

	if (searchQuery.value) {
		const q = searchQuery.value.toLowerCase()
		list = list.filter((f) => f.file_name.toLowerCase().includes(q))
	}

	if (fileTypeFilter.value !== "All") {
		list = list.filter((f) => {
			const ext = f.file_name.split(".").pop().toLowerCase()
			if (fileTypeFilter.value === "Documents") {
				return ["pdf", "doc", "docx", "txt", "rtf", "odt"].includes(ext)
			}
			if (fileTypeFilter.value === "Images") {
				return ["png", "jpg", "jpeg", "gif", "svg", "webp"].includes(ext)
			}
			if (fileTypeFilter.value === "Audio/Video") {
				return ["mp3", "wav", "mp4", "webm", "mkv", "mov"].includes(ext)
			}
			if (fileTypeFilter.value === "Others") {
				return ![
					"pdf",
					"doc",
					"docx",
					"txt",
					"rtf",
					"odt",
					"png",
					"jpg",
					"jpeg",
					"gif",
					"svg",
					"webp",
					"mp3",
					"wav",
					"mp4",
					"webm",
					"mkv",
					"mov",
				].includes(ext)
			}
			return true
		})
	}

	if (sourceFilter.value !== "All") {
		list = list.filter((f) => f.source === sourceFilter.value)
	}

	if (accessFilter.value === "My") {
		list = list.filter((f) => f.is_owner)
	} else if (accessFilter.value === "Shared") {
		list = list.filter((f) => f.shared_with_me || f.is_shared)
	}

	return list
})
</script>

<style>
/* Global Dialog Overlay Z-index override to ensure teleported dialogs always sit on top of everything (z-[99999]) */
body > div[data-frappe-ui-dialog],
body .frappe-dialog-overlay-top,
div[role="dialog"] {
  z-index: 99999 !important;
}

body div[data-dialog-backdrop],
.dialog-backdrop {
  z-index: 99990 !important;
}
</style>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 9999px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: #334155;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #475569;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.97); }
  to { opacity: 1; transform: scale(1); }
}

.animate-fade-in {
  animation: fadeIn 0.15s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(16px);
}

:global([data-radix-popper-content-wrapper]), :global([data-reka-popper-content-wrapper]), :global(.PopoverContent) { z-index: 100005 !important; }
</style>