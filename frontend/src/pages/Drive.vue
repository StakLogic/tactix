<template>
  <div class="space-y-4 p-1 flex flex-col h-full overflow-hidden min-h-0">
    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">

      <!-- Top Bar: Filters & Actions Card (matching Tasks.vue & Ticket.vue) -->
      <div class="bg-white dark:bg-slate-900 p-3 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col gap-3 flex-shrink-0">
        <!-- Top Row: Search & Action Buttons -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 w-full pb-2 border-b border-slate-100 dark:border-slate-800">
          <!-- Search Input -->
          <div class="relative w-full sm:w-80">
            <IconSearch class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search file name..."
              class="w-full pl-9 pr-3 py-1.5 text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-slate-900 dark:text-white"
            />
          </div>

          <!-- Action Buttons -->
          <div class="flex items-center gap-2 ml-auto sm:ml-0">
            <!-- View Mode Toggle -->
            <div class="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200/50 dark:border-slate-700">
              <button
                @click="viewMode = 'grid'"
                class="p-1.5 rounded-md transition-colors"
                :class="viewMode === 'grid' ? 'bg-white dark:bg-slate-700 text-blue-600 font-bold shadow-sm' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
                title="Grid View"
              >
                <IconLayoutGrid class="w-4 h-4" />
              </button>
              <button
                @click="viewMode = 'list'"
                class="p-1.5 rounded-md transition-colors"
                :class="viewMode === 'list' ? 'bg-white dark:bg-slate-700 text-blue-600 font-bold shadow-sm' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
                title="List View"
              >
                <IconList class="w-4 h-4" />
              </button>
            </div>

            <!-- Refresh Button -->
            <Button
              variant="outline"
              class="!text-slate-600 dark:!text-slate-300 !px-3 !h-9 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800"
              @click="refresh"
            >
              <template #prefix><IconRefreshCcw class="w-4 h-4 text-slate-500" :class="{ 'animate-spin': loading }" /></template>
            </Button>

            <!-- Back Button -->
            <Button
              v-if="currentPath !== '/'"
              variant="outline"
              class="!text-slate-600 dark:!text-slate-300 !px-3 !h-9 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800"
              @click="navigateUp"
            >
              <template #prefix><IconArrowLeft class="w-4 h-4 text-slate-500" /></template>
              Back
            </Button>

            <!-- New Folder Button -->
            <Button
              v-if="uploadAllowed"
              variant="solid"
              class="!text-xs !px-5 !h-9 !shadow-md transition-all"
              style="background-color: var(--primary-color); box-shadow: 0 4px 6px -1px var(--primary-color-shadow);"
              @click="showNewFolderModal = true"
            >
              <template #prefix><IconFolderPlus class="w-4 h-4" /></template>
              New Folder
            </Button>
          </div>
        </div>

        <!-- Bottom Row: Filters (File Type, Source, Access, Clear) -->
        <div class="flex flex-wrap items-center gap-2">
          <select
            v-model="fileTypeFilter"
            class="h-9 px-3 text-xs font-semibold rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-200 outline-none cursor-pointer hover:bg-slate-100"
          >
            <option value="All">All Types</option>
            <option value="Documents">Documents</option>
            <option value="Images">Images</option>
            <option value="Audio/Video">Audio & Video</option>
            <option value="Others">Others</option>
          </select>

          <select
            v-model="sourceFilter"
            class="h-9 px-3 text-xs font-semibold rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-200 outline-none cursor-pointer hover:bg-slate-100"
          >
            <option value="All">All Sources</option>
            <option value="Direct">Direct Upload</option>
            <option value="Ticket">Ticket Attachment</option>
            <option value="Task">Task Attachment</option>
          </select>

          <select
            v-model="accessFilter"
            class="h-9 px-3 text-xs font-semibold rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-200 outline-none cursor-pointer hover:bg-slate-100"
          >
            <option value="All">All Accessible</option>
            <option value="My">My Files</option>
            <option value="Shared">Shared With Me</option>
          </select>

          <Button
            v-if="searchQuery || fileTypeFilter !== 'All' || sourceFilter !== 'All' || accessFilter !== 'All'"
            variant="ghost"
            class="!text-red-500 hover:!bg-red-50 !px-2.5 !h-9 shrink-0"
            @click="resetFilters"
          >
            <template #prefix><IconX class="w-3.5 h-3.5" /></template>
            Clear
          </Button>
        </div>
      </div>

      <!-- Breadcrumb & Stats Bar -->
      <div class="mt-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-2 flex-shrink-0 shadow-sm">
        <div class="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 font-semibold overflow-x-auto whitespace-nowrap">
          <button
            class="flex items-center gap-1.5 hover:text-blue-600 dark:hover:text-blue-400 font-bold uppercase tracking-wider text-[10px] px-1.5 py-1 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-950/40"
            @click="fetchPath('/')"
          >
            <IconHome class="w-3.5 h-3.5" />
            Home
          </button>

          <template v-for="(part, idx) in rawPathParts" :key="idx">
            <IconChevronRight class="w-3 h-3 text-slate-300 dark:text-slate-600 shrink-0" />
            <button
              class="hover:text-blue-600 dark:hover:text-blue-400 font-semibold px-1.5 py-1 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-950/40 text-xs"
              :class="{ 'text-slate-900 dark:text-white font-bold': idx === rawPathParts.length - 1 }"
              @click="navigateToBreadcrumb(idx)"
            >
              {{ getCleanName(part) }}
            </button>
          </template>
        </div>

        <div class="flex items-center gap-2 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wide shrink-0">
          <span v-if="!loading" class="flex items-center gap-1.5">
            <IconFolder class="w-3.5 h-3.5 text-slate-400" />
            {{ folders.length }} {{ folders.length === 1 ? 'Folder' : 'Folders' }}
          </span>
          <span v-if="!loading" class="text-slate-200 dark:text-slate-700">•</span>
          <span v-if="!loading" class="flex items-center gap-1.5">
            <IconFile class="w-3.5 h-3.5 text-slate-400" />
            {{ filteredFiles.length }} {{ filteredFiles.length === 1 ? 'File' : 'Files' }}
          </span>
        </div>
      </div>

      <!-- Main Scrollable Directory Workspace -->
      <div class="flex-1 overflow-y-auto space-y-4 min-h-0 pr-1 mt-3 custom-scrollbar">

        <!-- Loading State -->
        <div v-if="loading" class="flex flex-col items-center justify-center py-24 gap-4">
          <LoadingIndicator class="w-8 h-8 text-blue-600" />
          <span class="text-xs font-semibold text-slate-400">Retrieving items…</span>
        </div>

        <div v-else class="space-y-4">
          <!-- Virtual Folders Grid -->
          <div v-if="folders.length > 0" class="space-y-2">
            <h3 class="text-[11px] font-bold text-slate-400 uppercase tracking-widest px-1">
              Folders ({{ folders.length }})
            </h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-3">
              <div
                v-for="folder in folders"
                :key="folder.path"
                class="group relative flex flex-col p-4 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700/60 hover:border-blue-400 dark:hover:border-blue-500 hover:shadow-md transition-all duration-200 cursor-pointer select-none"
                :class="{ 'ring-2 ring-blue-500 border-transparent': selectedItem?.path === folder.path }"
                @click="selectItem(folder)"
                @dblclick="fetchPath(folder.path)"
              >
                <div class="flex items-start justify-between">
                  <div class="p-2.5 rounded-lg transition-all shrink-0 shadow-sm" :class="getFolderIconGradientClass(folder.path)">
                    <IconFolder class="w-5 h-5 group-hover:scale-105 transition-transform" />
                  </div>

                  <span class="text-[9px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-full border border-slate-200 dark:border-slate-700" :class="getFolderTagClass(folder.path)">
                    {{ getFolderTypeLabel(folder.path) }}
                  </span>
                </div>

                <div class="mt-3">
                  <div class="text-sm font-bold text-slate-800 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors truncate" :title="folder.name">
                    {{ folder.name }}
                  </div>
                  <div class="text-[10px] text-slate-400 dark:text-slate-500 font-semibold mt-1 flex items-center gap-1 group-hover:text-blue-500 transition-colors">
                    <span>Open folder</span>
                    <IconArrowLeft class="w-3 h-3 rotate-180 group-hover:translate-x-0.5 transition-transform" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Files List Container -->
          <div class="space-y-3">
            <transition name="slide-up">
              <div v-if="selectedItems && selectedItems.length > 0" class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-indigo-50/90 dark:bg-indigo-950/60 border border-indigo-200/80 dark:border-indigo-800 p-3.5 rounded-2xl shadow-sm mb-4">
                <div class="flex items-center gap-2.5">
                  <div class="w-2 h-2 rounded-full bg-indigo-600 animate-pulse"></div>
                  <span class="text-xs font-bold text-indigo-950 dark:text-indigo-100">
                    {{ selectedItems ? selectedItems.length : 0 }} {{ selectedItems?.length === 1 ? 'file' : 'files' }} selected
                  </span>
                </div>
                <div class="flex items-center gap-2 w-full sm:w-auto justify-end">
                  <Button variant="solid" class="!bg-indigo-600 hover:!bg-indigo-700 !shadow-sm" size="sm" @click="openBulkShareModal">
                    <template #prefix><IconShare2 class="w-3.5 h-3.5" /></template>
                    Share Selected
                  </Button>
                  <Button variant="outline" class="!text-rose-600 !border-rose-200 hover:!bg-rose-50 dark:!border-rose-900/50" size="sm" @click="promptBulkDelete">
                    <template #prefix><IconTrash2 class="w-3.5 h-3.5" /></template>
                    Delete Selected
                  </Button>
                  <Button variant="ghost" size="sm" @click="clearSelection" class="!text-slate-500">
                    Clear
                  </Button>
                </div>
              </div>
            </transition>

            <!-- Header Title -->
            <div class="flex items-center justify-between px-1">
              <h3 class="text-[11px] font-bold text-slate-400 uppercase tracking-widest">
                Files ({{ filteredFiles.length }})
              </h3>
            </div>

            <!-- Empty File Explorer -->
            <div v-if="filteredFiles.length === 0" class="flex flex-col items-center justify-center py-16 px-4 bg-white border border-dashed border-slate-200 rounded-2xl text-center">
              <div class="p-4 bg-slate-50 rounded-2xl mb-4">
                <IconFile class="w-9 h-9 text-slate-300" />
              </div>
              <h4 class="text-sm font-bold text-slate-700">No files found</h4>
              <p class="text-xs text-slate-400 max-w-sm mt-1">
                {{ searchQuery ? 'Try adjusting your search query or filters.' : 'This directory does not contain any documents yet.' }}
              </p>
            </div>

            <!-- Files Grid/List Content -->
            <div v-else>
              <!-- Grid View -->
              <div v-if="viewMode === 'grid'" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-4">
                <div
                  v-for="file in filteredFiles"
                  :key="file.name"
                  class="flex flex-col items-center p-4 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200/70 dark:border-slate-800 hover:border-indigo-200 dark:hover:border-indigo-950 hover:shadow-[0_14px_28px_rgba(15,23,42,0.06)] dark:hover:shadow-[0_14px_28px_rgba(0,0,0,0.25)] transition-all duration-300 cursor-pointer group text-center select-none relative"
                  :class="{ 'ring-2 ring-indigo-500 border-transparent': selectedItem?.name === file.name || isSelected(file.name) }"
                  @click="selectItem(file)"
                >
                  <!-- Checkbox selector -->
                  <div class="absolute top-3 left-3 z-10" @click.stop>
                    <input
                      type="checkbox"
                      :checked="isSelected(file.name)"
                      @change="toggleSelect(file.name)"
                      class="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 border-slate-300 dark:border-slate-700 dark:bg-slate-900 cursor-pointer"
                    />
                  </div>

                  <!-- Thumbnail with color-matched theme -->
                  <div class="p-5 rounded-2xl transition-all duration-300 mb-3 shrink-0 flex items-center justify-center aspect-square w-14" :class="getFileIconBg(file.file_name)">
                    <component
                      :is="getFileIcon(file.file_name)"
                      class="w-6 h-6 shrink-0 transition-transform duration-300 group-hover:scale-110"
                      :class="getFileIconColor(file.file_name)"
                    />
                  </div>

                  <!-- File Name -->
                  <div class="text-xs font-bold text-slate-800 dark:text-slate-100 break-all line-clamp-2 px-1 w-full min-h-[2.5rem] flex items-center justify-center leading-snug">
                    {{ file.file_name }}
                  </div>

                  <!-- File Size & Source badge -->
                  <div class="flex items-center gap-1.5 mt-2 justify-center flex-wrap">
                    <span class="text-[9px] font-mono font-semibold text-slate-400 dark:text-slate-500">
                      {{ formatBytes(file.file_size) }}
                    </span>
                    <span
                      class="text-[8px] font-bold px-2 py-0.5 rounded-full leading-none shrink-0"
                      :class="getSourceBadgeClass(file.source)"
                    >
                      {{ file.source }}
                    </span>
                    <span v-if="file.is_shared" class="text-[8px] font-bold px-1.5 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-100 dark:bg-amber-950/40 dark:text-amber-400 flex items-center gap-1 shrink-0" title="Shared with team members">
                      <IconShare2 class="w-2.5 h-2.5" />
                      {{ file.shares_count }}
                    </span>
                  </div>

                  <!-- Hover Action Buttons -->
                  <div class="absolute top-3 right-3 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200" @click.stop>
                    <button
                      v-if="file.can_share"
                      class="p-1.5 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-400 dark:text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors cursor-pointer border-none shadow-sm"
                      title="Share File Access"
                      @click="openShareModal(file)"
                    >
                      <IconShare2 class="w-3.5 h-3.5" />
                    </button>
                    <a
                      :href="file.file_url"
                      target="_blank"
                      download
                      class="p-1.5 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-400 dark:text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors cursor-pointer shrink-0 shadow-sm"
                      title="Download File"
                    >
                      <IconDownload class="w-3.5 h-3.5" />
                    </a>
                    <button
                      v-if="isDeletable(file)"
                      class="p-1.5 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-400 dark:text-slate-500 hover:text-rose-600 dark:hover:text-rose-450 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors cursor-pointer border-none shadow-sm"
                      title="Delete File"
                      @click="promptDelete(file)"
                    >
                      <IconTrash2 class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>

              <!-- List View (Table) -->
              <div v-else class="bg-white dark:bg-slate-800 border border-slate-200/70 dark:border-slate-800 rounded-2xl overflow-hidden shadow-sm transition-colors duration-300">
                <table class="w-full text-left border-collapse table-fixed">
                  <thead>
                    <tr class="bg-slate-50/70 dark:bg-slate-900/50 border-b border-slate-200/80 dark:border-slate-850 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                      <th class="w-10 py-3.5 pl-5 pr-1 text-center">
                        <input
                          type="checkbox"
                          :checked="isAllSelected"
                          @change="toggleSelectAll"
                          class="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 border-slate-300 dark:border-slate-700 dark:bg-slate-900 cursor-pointer"
                        />
                      </th>
                      <th class="w-1/2 py-3.5 px-4">Name</th>
                      <th class="w-1/6 py-3.5 px-4">Size</th>
                      <th class="w-1/6 py-3.5 px-4">Date</th>
                      <th class="w-1/6 py-3.5 px-4 text-right pr-6">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100 dark:divide-slate-800 text-xs font-medium text-slate-700 dark:text-slate-300">
                    <tr
                      v-for="file in filteredFiles"
                      :key="file.name"
                      class="hover:bg-slate-50/70 dark:hover:bg-slate-900/40 transition-colors cursor-pointer group"
                      :class="{ 'bg-indigo-50/30 hover:bg-indigo-50/40 dark:bg-indigo-950/20 dark:hover:bg-indigo-950/30': selectedItem?.name === file.name || isSelected(file.name) }"
                      @click="selectItem(file)"
                    >
                      <td class="py-3.5 pl-5 pr-1 text-center" @click.stop>
                        <input
                          type="checkbox"
                          :checked="isSelected(file.name)"
                          @change="toggleSelect(file.name)"
                          class="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 border-slate-300 dark:border-slate-700 dark:bg-slate-900 cursor-pointer"
                        />
                      </td>
                      <td class="py-3.5 px-4 flex items-center gap-3 min-w-0">
                        <div class="p-2 rounded-lg shrink-0" :class="getFileIconBg(file.file_name)">
                          <component
                            :is="getFileIcon(file.file_name)"
                            class="w-4 h-4 shrink-0"
                            :class="getFileIconColor(file.file_name)"
                          />
                        </div>
                        <div class="min-w-0 flex-1">
                          <div class="font-semibold text-slate-800 dark:text-slate-200 truncate" :title="file.file_name">
                            {{ file.file_name }}
                          </div>
                          <div class="flex items-center gap-1.5 mt-0.5">
                            <span
                              class="text-[9px] font-bold px-1.5 py-0.5 rounded-full leading-none shrink-0"
                              :class="getSourceBadgeClass(file.source)"
                            >
                              {{ file.source }}
                            </span>
                            <span v-if="file.is_shared" class="text-[8px] font-bold px-1.5 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-100 dark:bg-amber-950/40 dark:text-amber-400 flex items-center gap-1 shrink-0">
                              <IconShare2 class="w-2.5 h-2.5" />
                              Shared ({{ file.shares_count }})
                            </span>
                            <span v-if="file.source === 'Task' && file.task_subject" class="text-[10px] text-slate-400 dark:text-slate-500 font-medium truncate">
                              {{ file.task_subject }}
                            </span>
                            <span v-else-if="file.source_name" class="text-[10px] text-slate-400 dark:text-slate-500 font-medium truncate">
                              {{ file.source_name }}
                            </span>
                          </div>
                        </div>
                      </td>

                      <td class="py-3.5 px-4 text-slate-500 dark:text-slate-400 font-mono text-[11px] select-none">
                        {{ formatBytes(file.file_size) }}
                      </td>

                      <td class="py-3.5 px-4 text-slate-500 dark:text-slate-400 font-medium select-none">
                        {{ formatDate(file.creation) }}
                      </td>

                      <td class="py-3.5 px-4 text-right pr-6 select-none" @click.stop>
                        <div class="flex items-center justify-end gap-1">
                          <button
                            v-if="file.can_share"
                            class="p-1.5 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-all shrink-0 cursor-pointer border-none bg-transparent"
                            title="Share File Access"
                            @click="openShareModal(file)"
                          >
                            <IconShare2 class="w-4 h-4" />
                          </button>
                          <a
                            :href="file.file_url"
                            target="_blank"
                            download
                            class="p-1.5 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-all shrink-0 cursor-pointer border border-transparent"
                            title="Download File"
                          >
                            <IconDownload class="w-4 h-4" />
                          </a>
                          <button
                            v-if="isDeletable(file)"
                            class="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-all shrink-0 cursor-pointer border-none bg-transparent"
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

          <!-- Drag/Drop Dropzone -->
          <div v-if="uploadAllowed" class="space-y-3.5 pt-5 border-t border-slate-200/70 dark:border-slate-800">
            <h3 class="text-[11px] font-bold text-slate-400 uppercase tracking-widest px-1">Upload Documents</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                class="border-2 border-dashed border-indigo-200 dark:border-indigo-950 hover:border-indigo-400 dark:hover:border-indigo-800 rounded-2xl p-8 transition-all duration-300 flex flex-col items-center justify-center cursor-pointer bg-indigo-50/20 dark:bg-indigo-950/10 hover:bg-indigo-50/40 dark:hover:bg-indigo-950/20 group select-none relative"
                :class="{ '!border-indigo-500 !bg-indigo-50/60 dark:!bg-indigo-950/35': dragActive }"
                @dragenter.prevent="dragActive = true"
                @dragover.prevent="dragActive = true"
                @dragleave.prevent="dragActive = false"
                @drop.prevent="handleDrop"
                @click="fileInput.click()"
              >
                <input ref="fileInput" type="file" class="hidden" multiple @change="handleFileSelect" />
                <div class="p-3.5 bg-white dark:bg-slate-900 group-hover:bg-indigo-100/60 rounded-2xl transition-colors duration-300 mb-3 shadow-sm">
                  <IconUploadCloud class="w-7 h-7 text-indigo-400 group-hover:text-indigo-600 transition-all duration-300 group-hover:scale-110" />
                </div>
                <div class="text-sm font-bold text-slate-700 dark:text-slate-200">
                  <span class="text-indigo-600 group-hover:underline">Click to upload</span> or drag files here
                </div>
                <div class="text-[9px] text-slate-400 font-bold uppercase tracking-widest mt-2">
                  Uploads attach to {{ currentPathName }}
                </div>
              </div>

              <!-- Uploading List Progress -->
              <div v-if="uploading" class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 flex flex-col justify-center space-y-4 shadow-sm">
                <div class="flex items-center gap-3.5">
                  <div class="p-2.5 bg-indigo-50 rounded-xl">
                    <LoadingIndicator class="w-5 h-5 text-indigo-600 animate-spin" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-sm font-bold text-slate-700 dark:text-slate-200">Uploading document…</div>
                    <div class="text-xs text-slate-400 mt-0.5 truncate font-medium">{{ uploadingFileName }}</div>
                  </div>
                  <div class="text-xs font-mono font-bold text-slate-500">{{ uploadProgress }}%</div>
                </div>
                <div class="w-full bg-slate-100 dark:bg-slate-900 h-2 rounded-full overflow-hidden">
                  <div
                    class="bg-gradient-to-r from-indigo-500 to-indigo-600 h-full rounded-full transition-all duration-300"
                    :style="{ width: `${uploadProgress}%` }"
                  ></div>
                </div>
              </div>

              <!-- Folder Instruction Box -->
              <div v-else class="relative overflow-hidden border border-slate-200/60 dark:border-slate-850 rounded-2xl p-6 bg-gradient-to-br from-slate-900 to-indigo-950 dark:from-slate-950 dark:to-indigo-950/80 text-black shadow-lg">
                <div class="absolute top-0 right-0 -translate-y-6 translate-x-6 w-36 h-36 bg-indigo-500/10 rounded-full blur-2xl"></div>
                <div class="flex items-start gap-4 relative z-10">
                  <div class="p-3 bg-white/10 backdrop-blur-md rounded-2xl shrink-0 border border-white/5">
                    <IconInfo class="w-5 h-5 text-indigo-200" />
                  </div>
                  <div class="space-y-2">
                    <h4 class="text-[10px] font-bold uppercase tracking-wider text-slate-300">Folder Storage Policy</h4>
                    <p class="text-xs text-slate-300 leading-relaxed font-medium">
                      Direct uploads are stored securely and attached to this category. Shared documents are visible company-wide, while client and department folders follow organization privacy boundaries.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Side Details Explorer Panel -->
    <div
      class="w-80 border-l border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col p-6 flex-shrink-0 relative overflow-y-auto hidden lg:flex custom-scrollbar"
    >
      <div v-if="selectedItem" class="space-y-6">
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
          <span class="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Details</span>
          <button @click="selectedItem = null" class="text-slate-400 hover:text-slate-600 p-1 border-none bg-transparent cursor-pointer rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800">
            <IconX class="w-4 h-4" />
          </button>
        </div>

        <div class="flex flex-col items-center text-center p-5 rounded-2xl bg-slate-50/70 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800">
          <div class="p-4 rounded-2xl mb-1 dark:bg-slate-900" :class="selectedItem.is_folder ? getFolderIconGradientClass(selectedItem.path) : getFileIconBg(selectedItem.file_name)">
            <component
              :is="selectedItem.is_folder ? IconFolder : getFileIcon(selectedItem.file_name)"
              class="w-8 h-8"
              :class="selectedItem.is_folder ? '' : getFileIconColor(selectedItem.file_name)"
            />
          </div>
          <h4 class="text-sm font-bold text-slate-800 dark:text-slate-100 break-all mt-3 w-full px-1">
            {{ selectedItem.is_folder ? selectedItem.name : selectedItem.file_name }}
          </h4>
          <span
            v-if="!selectedItem.is_folder"
            class="text-[9px] font-bold px-2 py-0.5 rounded-full uppercase mt-2 shrink-0"
            :class="getSourceBadgeClass(selectedItem.source)"
          >
            {{ selectedItem.source }} Upload
          </span>
          <span v-else class="text-[9px] font-bold px-2 py-0.5 rounded-full uppercase bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 mt-2 shrink-0">
            System Folder
          </span>
        </div>

        <div class="space-y-3.5 text-xs font-semibold">
          <div class="flex justify-between items-center py-2.5 border-b border-slate-100 dark:border-slate-800/80">
            <span class="text-slate-400 dark:text-slate-500">Path</span>
            <span class="text-slate-700 dark:text-slate-300 truncate max-w-[10rem]" :title="selectedItem.path || currentPath">
              {{ selectedItem.path || currentPath }}
            </span>
          </div>

          <template v-if="!selectedItem.is_folder">
            <div class="flex justify-between items-center py-2.5 border-b border-slate-100 dark:border-slate-800/80">
              <span class="text-slate-400 dark:text-slate-500">File Size</span>
              <span class="text-slate-700 dark:text-slate-300 font-mono">{{ formatBytes(selectedItem.file_size) }}</span>
            </div>

            <div class="flex justify-between items-center py-2.5 border-b border-slate-100 dark:border-slate-800/80">
              <span class="text-slate-400 dark:text-slate-500">Created At</span>
              <span class="text-slate-700 dark:text-slate-300">{{ formatDate(selectedItem.creation) }}</span>
            </div>

            <div class="flex justify-between items-center py-2.5 border-b border-slate-100 dark:border-slate-800/80">
              <span class="text-slate-400 dark:text-slate-500">Uploaded By</span>
              <div class="flex items-center gap-1.5">
                <Avatar :image="selectedItem.owner_image" :label="selectedItem.owner_full_name" size="xs" class="ring-1 ring-white dark:ring-slate-850 shrink-0" />
                <span class="text-slate-700 dark:text-slate-300 max-w-[8rem] truncate" :title="selectedItem.owner_full_name">
                  {{ selectedItem.owner_full_name }}
                </span>
              </div>
            </div>

            <!-- Action buttons -->
            <div class="pt-1 space-y-2">
              <a
                :href="selectedItem.file_url"
                target="_blank"
                download
                class="flex items-center justify-center gap-2 w-full rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold py-2.5 transition-colors shadow-sm"
              >
                <IconDownload class="w-3.5 h-3.5" />
                Download File
              </a>
              <button
                v-if="selectedItem.can_share"
                @click="openShareModal(selectedItem)"
                class="flex items-center justify-center gap-2 w-full rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-bold py-2.5 transition-colors border-none cursor-pointer shadow-sm"
              >
                <IconShare2 class="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                Share Access ({{ selectedItem.shares_count || 0 }})
              </button>
            </div>

            <!-- Linked Context Redirect -->
            <div v-if="selectedItem.source === 'Ticket' || selectedItem.source === 'Task'" class="flex flex-col gap-2 pt-1">
              <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Document Origin</span>
              <div class="flex items-center gap-2 p-3 bg-indigo-50/50 dark:bg-indigo-950/20 rounded-xl border border-indigo-100/60 dark:border-indigo-950/40">
                <component :is="selectedItem.source === 'Ticket' ? IconTicket : IconBriefcase" class="w-4.5 h-4.5 text-indigo-600 dark:text-indigo-400 shrink-0" />
                <div class="min-w-0 flex-1">
                  <div class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wide">
                    Linked {{ selectedItem.source }}
                  </div>
                  <div class="text-xs font-bold text-slate-700 dark:text-slate-200 truncate mt-0.5">
                    {{ selectedItem.source === 'Task' && selectedItem.task_subject ? selectedItem.task_subject : selectedItem.source_name }}
                  </div>
                </div>
                <button
                  class="p-1 text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 hover:bg-white dark:hover:bg-slate-800 rounded-lg transition-colors border-none bg-transparent cursor-pointer"
                  @click="redirectOrigin(selectedItem)"
                >
                  <IconArrowLeft class="w-4 h-4 rotate-180" />
                </button>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="flex justify-between items-center py-2.5 border-b border-slate-100 dark:border-slate-800/80">
              <span class="text-slate-400 dark:text-slate-500">Folder Name</span>
              <span class="text-slate-700 dark:text-slate-350">{{ selectedItem.name }}</span>
            </div>
            <div class="pt-3">
              <Button variant="solid" class="w-full justify-center !bg-indigo-600 hover:!bg-indigo-700" @click="fetchPath(selectedItem.path)">
                Open Folder
              </Button>
            </div>
          </template>
        </div>
      </div>

      <div v-else class="h-full flex flex-col items-center justify-center text-center space-y-4">
        <div class="p-4 bg-slate-50 dark:bg-slate-800 rounded-2xl">
          <IconInfo class="w-6 h-6 text-slate-300 dark:text-slate-600" />
        </div>
        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">File Information</h4>
        <p class="text-xs text-slate-400 dark:text-slate-500 max-w-[14rem] leading-relaxed">
          Select a folder or a file to inspect metadata, size, upload origin, and links to source documents.
        </p>
      </div>
    </div>
  </div>

    <!-- Confirm File / Bulk Deletion Dialog (matching Tasks & Tickets) -->
    <Dialog
      v-model="deleteConfirm.show"
      :disable-outside-click-to-close="true"
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
            Are you sure you want to permanently delete <b class="text-slate-900 dark:text-white break-all">"{{ deleteConfirm.file?.file_name }}"</b>? It will be removed from all attached workspaces and records.
          </span>
        </p>
      </template>
    </Dialog>

    <!-- New Folder Dialog (matching Tasks & Tickets) -->
    <Dialog
      v-model="showNewFolderModal"
      :disable-outside-click-to-close="true"
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

    <!-- Share File Dialog (matching Tasks & Tickets) -->
    <Dialog
      v-model="shareModal.show"
      :disable-outside-click-to-close="true"
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
        <div class="space-y-6 py-2">
          <!-- File Subtitle / Bulk summary -->
          <div v-if="!shareModal.isBulk && shareModal.file" class="p-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg flex items-center gap-2">
            <IconFile class="w-4 h-4 text-blue-600 dark:text-blue-400 shrink-0" />
            <span class="text-xs font-bold text-slate-800 dark:text-slate-100 truncate" :title="shareModal.file.file_name">
              {{ shareModal.file.file_name }}
            </span>
          </div>

          <div v-else-if="shareModal.isBulk" class="p-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
            <span class="text-xs font-bold text-slate-700 dark:text-slate-300">
              Sharing {{ selectedItems ? selectedItems.length : 0 }} selected file(s) with team member
            </span>
          </div>

          <!-- Add Access Form using FormControl -->
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

          <!-- Active Access List (Only for Single File Share) -->
          <div v-if="!shareModal.isBulk" class="space-y-3 pt-3 border-t border-slate-100 dark:border-slate-800">
            <div class="flex items-center justify-between">
              <label class="text-xs font-medium text-slate-600 dark:text-slate-400 uppercase tracking-wider">People with Access</label>
              <span class="text-xs text-slate-400 font-medium">{{ (shareModal.shares?.length || 0) + (shareModal.owner ? 1 : 0) }} members</span>
            </div>

            <!-- Loading state -->
            <div v-if="shareModal.loading" class="py-4 flex justify-center">
              <div class="w-5 h-5 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
            </div>

            <div v-else class="space-y-2 max-h-56 overflow-y-auto custom-scrollbar pr-1">
              <!-- File Owner Record -->
              <div v-if="shareModal.owner" class="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                <div class="flex items-center gap-3">
                  <Avatar :image="shareModal.owner.user_image" :label="shareModal.owner.full_name" size="sm" />
                  <div>
                    <div class="text-xs font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
                      {{ shareModal.owner.full_name }}
                      <Badge theme="gray" variant="subtle" label="Owner" />
                    </div>
                    <div class="text-[10px] text-slate-400 font-mono mt-0.5">{{ shareModal.owner.email }}</div>
                  </div>
                </div>
                <span class="text-[10px] font-bold text-slate-400 uppercase">Full Owner</span>
              </div>

              <!-- Shared Users List -->
              <div
                v-for="share in shareModal.shares"
                :key="share.share_id"
                class="flex items-center justify-between p-2.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm"
              >
                <div class="flex items-center gap-3">
                  <Avatar :image="share.user_image" :label="share.full_name" size="sm" />
                  <div>
                    <div class="text-xs font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
                      {{ share.full_name }}
                      <Badge theme="blue" variant="subtle" :label="share.primary_role" />
                    </div>
                    <div class="text-[10px] text-slate-400 font-mono mt-0.5">{{ share.email }}</div>
                  </div>
                </div>

                <div class="flex items-center gap-2">
                  <span class="text-xs font-semibold text-slate-500 dark:text-slate-400 capitalize">
                    {{ share.permission === 'write' ? 'Can Edit' : 'Can View' }}
                  </span>
                  <Button
                    size="sm"
                    variant="ghost"
                    class="!text-red-500 hover:!bg-red-50 !p-1.5"
                    @click="executeUnshare(share.user)"
                    title="Revoke access"
                  >
                    <template #prefix><IconTrash2 class="w-3.5 h-3.5" /></template>
                  </Button>
                </div>
              </div>

              <div v-if="(!shareModal.shares || shareModal.shares.length === 0) && !shareModal.loading" class="text-center py-4 text-xs text-slate-400 italic font-medium">
                No additional team members currently have access.
              </div>
            </div>
          </div>
        </div>
      </template>
    </Dialog>
</template>

<script setup>
import dayjs from "dayjs"
import { Avatar, Badge, Button, Dialog, FormControl, LoadingIndicator, createResource } from "frappe-ui"
import { computed, reactive, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { session } from "../data/session"

import IconAlertCircle from "~icons/lucide/alert-circle"
import IconArrowLeft from "~icons/lucide/arrow-left"
import IconBriefcase from "~icons/lucide/briefcase"
import IconCheck from "~icons/lucide/check"
import IconChevronRight from "~icons/lucide/chevron-right"
import IconDownload from "~icons/lucide/download"
import IconFile from "~icons/lucide/file"
import IconFileArchive from "~icons/lucide/file-archive"
import IconFileAudio from "~icons/lucide/file-audio"
import IconFileImage from "~icons/lucide/file-image"
import IconFileSpreadsheet from "~icons/lucide/file-spreadsheet"
import IconFileText from "~icons/lucide/file-text"
import IconFileVideo from "~icons/lucide/file-video"
import IconFolder from "~icons/lucide/folder"
// Icons
import IconFolderOpen from "~icons/lucide/folder-open"
import IconFolderPlus from "~icons/lucide/folder-plus"
import IconHome from "~icons/lucide/home"
import IconInfo from "~icons/lucide/info"
import IconLayoutGrid from "~icons/lucide/layout-grid"
import IconList from "~icons/lucide/list"
import IconRefreshCcw from "~icons/lucide/refresh-ccw"
import IconSearch from "~icons/lucide/search"
import IconShare2 from "~icons/lucide/share-2"
import IconTicket from "~icons/lucide/ticket"
import IconTrash2 from "~icons/lucide/trash-2"
import IconUploadCloud from "~icons/lucide/upload-cloud"
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
const fileTypeFilter = ref("All")
const sourceFilter = ref("All")
const accessFilter = ref("All")
const viewMode = ref("grid")

const shareableUsers = ref([])
const shareModal = reactive({
	show: false,
	file: null,
	loading: false,
	submitting: false,
	targetUser: "",
	permission: "read",
	owner: null,
	shares: []
})

const selectedItem = ref(null)

const toast = ref({ show: false, message: "", type: "success" })
const deleteConfirm = ref({ show: false, file: null })

const showNewFolderModal = ref(false)
const newFolderName = ref("")
const creatingFolder = ref(false)

const fileInput = ref(null)
const dragActive = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadingFileName = ref("")

// Path Parts Helper for Breadcrumbs
const rawPathParts = computed(() => {
	if (currentPath.value === "/") return []
	return currentPath.value.split("/").filter((x) => x !== "")
})

// Strips unique database suffixes
function getCleanName(name) {
	if (name && name.includes("__")) {
		return name.split("__")[0]
	}
	return name
}

// Current Folder Friendly Name Helper
const currentPathName = computed(() => {
	const parts = rawPathParts.value
	if (parts.length === 0) return "Home"
	return getCleanName(parts[parts.length - 1])
})

// Check if uploading is allowed in current directory
const uploadAllowed = computed(() => {
	const p = currentPath.value
	if (p === "/" || p === "/Clients" || p === "/Departments") {
		return false
	}
	return true
})

const dbFolder = ref("Home")

// API resources - using the dedicated drive API module
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

async function executeUnshare(targetUser) {
	if (!shareModal.file || !targetUser) return
	try {
		await unshareFileResource.submit({
			file_name: shareModal.file.name,
			target_user: targetUser,
		})
		showToast("Revoked access successfully", "success")
		const res = await getFileSharesResource.fetch({ file_name: shareModal.file.name })
		shareModal.owner = res.owner
		shareModal.shares = res.shares || []
		loadPathContents(currentPath.value)
	} catch (err) {
		showToast(err.message || "Failed to revoke access", "error")
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

// Reload folder contents when path changes (uses resource.fetch for instant updates)
function loadPathContents(path) {
	loading.value = true
	selectedItem.value = null // reset details selection
	selectedItems.value = [] // reset selection list
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

// Watch the route parameters to fetch folder contents dynamically
watch(
	() => route.params.folderPath,
	(newVal) => {
		let path = "/"
		if (newVal) {
			path = Array.isArray(newVal) ? "/" + newVal.join("/") : "/" + newVal
		}
		currentPath.value = path
		loadPathContents(path)
	},
	{ immediate: true },
)

// Folder themed classes based on folder categories
function getFolderIconGradientClass(folderPath) {
	if (folderPath?.startsWith("/Shared")) {
		return "bg-gradient-to-tr from-amber-400 to-orange-500 text-white shadow-md shadow-orange-500/10"
	}
	if (folderPath?.startsWith("/Clients")) {
		return "bg-gradient-to-tr from-indigo-500 to-blue-600 text-white shadow-md shadow-blue-500/10"
	}
	if (folderPath?.startsWith("/Departments")) {
		return "bg-gradient-to-tr from-emerald-400 to-teal-500 text-white shadow-md shadow-blue-500/10"
	}
	return "bg-gradient-to-tr from-slate-400 to-slate-500 text-white shadow-md shadow-slate-500/10"
}

function getFolderTagClass(folderPath) {
	if (folderPath.startsWith("/Shared")) {
		return "bg-amber-50 border-amber-100 text-amber-700 font-bold"
	}
	if (folderPath.startsWith("/Clients")) {
		return "bg-indigo-50 border-indigo-100 text-indigo-700 font-bold"
	}
	if (folderPath.startsWith("/Departments")) {
		return "bg-emerald-50 border-emerald-100 text-emerald-700 font-bold"
	}
	return "bg-slate-50 border-slate-150 text-slate-700 font-bold"
}

function getFolderTypeLabel(folderPath) {
	if (folderPath.startsWith("/Shared")) return "Shared"
	if (folderPath.startsWith("/Clients")) return "Client"
	if (folderPath.startsWith("/Departments")) return "Dept"
	return "Subfolder"
}

function getFileIconBg(filename) {
	if (!filename) return "bg-slate-50"
	const ext = filename.split(".").pop().toLowerCase()
	if (["pdf"].includes(ext)) return "bg-rose-50 border border-rose-100"
	if (["png", "jpg", "jpeg", "gif", "svg", "webp"].includes(ext))
		return "bg-sky-50 border border-sky-100"
	if (["xls", "xlsx", "csv", "ods"].includes(ext))
		return "bg-emerald-50 border border-emerald-100"
	if (["mp4", "webm", "mkv", "avi", "mov"].includes(ext))
		return "bg-purple-50 border border-purple-100"
	if (["mp3", "wav", "ogg", "aac", "flac"].includes(ext))
		return "bg-amber-50 border border-amber-100"
	if (["zip", "tar", "gz", "rar", "7z"].includes(ext))
		return "bg-orange-50 border border-orange-100"
	return "bg-indigo-50/50 border border-indigo-100/50"
}

// Navigation functions
function selectItem(item) {
	selectedItem.value = item
}

// Navigate back up a level
function navigateUp() {
	const path = currentPath.value
	if (path === "/") return
	const parts = path.split("/").filter((x) => x !== "")
	parts.pop()
	const parent = "/" + parts.join("/")
	fetchPath(parent)
}

// Navigate to breadcrumb trail point
function navigateToBreadcrumb(idx) {
	const parts = rawPathParts.value.slice(0, idx + 1)
	const target = "/" + parts.join("/")
	fetchPath(target)
}

// CSRF token provider
function getCsrfToken() {
	if (window.csrf_token) return window.csrf_token
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	return cookies.get("system_csrf_token") || ""
}

// Dropzone drag-and-drop
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

// File upload handler
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

	for (let i = 0; i < filesList.length; i++) {
		const fileObj = filesList[i]
		uploadingFileName.value = fileObj.name
		uploadProgress.value = 10

		const formData = new FormData()
		formData.append("file", fileObj)
		formData.append("is_private", 0)
		formData.append("doctype", doctype)
		formData.append("docname", docname)
		formData.append("folder", dbFolder.value || "Home")

		try {
			const csrfToken = getCsrfToken()
			uploadProgress.value = 40

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

			uploadProgress.value = 100
			showToast(`Successfully uploaded "${fileObj.name}"`, "success")
		} catch (err) {
			showToast(`Failed uploading "${fileObj.name}"`, "error")
		}
	}

	// Done uploads, clean up states
	uploading.value = false
	uploadingFileName.value = ""
	uploadProgress.value = 0

	// Reload current folder contents directly
	loadPathContents(currentPath.value)
}

// Delete Handlers
function promptDelete(file) {
	deleteConfirm.value = {
		show: true,
		file,
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
		showToast(`Deleted ${selectedItems.value.length} files successfully`, "success")
		clearSelection()
		loadPathContents(currentPath.value)
	} catch (err) {
		loading.value = false
		showToast(err.message || "Failed to delete selected files", "error")
	}
}

// Redirect client to ticket or task view page
function redirectOrigin(file) {
	if (file.source === "Ticket") {
		router.push(`/tickets/${file.source_name}`)
	} else if (file.source === "Task") {
		router.push(`/tasks/${file.source_name}`)
	}
}

// Toast helper
function showToast(message, type = "success") {
	toast.value = {
		show: true,
		message,
		type,
	}
	setTimeout(() => {
		toast.value.show = false
	}, 5000)
}

// Byte Formatter
function formatBytes(bytes) {
	if (!bytes) return "0 B"
	const k = 1024
	const sizes = ["Bytes", "KB", "MB", "GB"]
	const i = Math.floor(Math.log(bytes) / Math.log(k))
	return `${Number.parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

// Date Formatter
function formatDate(creation) {
	if (!creation) return ""
	return dayjs(creation).format("MMM DD, YYYY")
}

// File extension color maps
function getFileIconColor(filename) {
	if (!filename) return "text-slate-400"
	const ext = filename.split(".").pop().toLowerCase()
	if (["pdf"].includes(ext)) return "text-rose-500"
	if (["png", "jpg", "jpeg", "gif", "svg", "webp"].includes(ext))
		return "text-sky-500"
	if (["xls", "xlsx", "csv", "ods"].includes(ext)) return "text-emerald-500"
	if (["mp4", "webm", "mkv", "avi", "mov"].includes(ext))
		return "text-purple-500"
	if (["mp3", "wav", "ogg", "aac", "flac"].includes(ext))
		return "text-amber-500"
	if (["zip", "tar", "gz", "rar", "7z"].includes(ext)) return "text-orange-500"
	return "text-indigo-400"
}

// Dynamic File Icon Selector based on extension
function getFileIcon(filename) {
	if (!filename) return IconFile
	const ext = filename.split(".").pop().toLowerCase()
	if (["pdf", "doc", "docx", "txt", "rtf", "odt"].includes(ext))
		return IconFileText
	if (["png", "jpg", "jpeg", "gif", "svg", "webp"].includes(ext))
		return IconFileImage
	if (["xls", "xlsx", "csv", "ods"].includes(ext)) return IconFileSpreadsheet
	if (["mp4", "webm", "mkv", "avi", "mov"].includes(ext)) return IconFileVideo
	if (["mp3", "wav", "ogg", "aac", "flac"].includes(ext)) return IconFileAudio
	if (["zip", "tar", "gz", "rar", "7z"].includes(ext)) return IconFileArchive
	return IconFile
}

// Source Color Badges Class
function getSourceBadgeClass(source) {
	if (source === "Direct" || source === "Shared")
		return "bg-indigo-50 text-indigo-700 border border-indigo-100"
	if (source === "Ticket") return "bg-sky-50 text-sky-700 border border-sky-100"
	if (source === "Task")
		return "bg-purple-50 text-purple-700 border border-purple-100"
	return "bg-slate-100 text-slate-700"
}

// Deletable condition calculator
function isDeletable(file) {
	if (!session.isTicketRaiser) return true
	if (file.owner === session.user) return true
	if (
		file.source === "Direct" &&
		file.source_name === session.userInfo.tactix_customer
	)
		return true
	return false
}

// Computes filtered files
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

<style scoped>
/* Scoped brand color overrides for primary theme var(--primary-color) */
.text-indigo-600,
.\!text-indigo-600,
.group:hover .group-hover\:text-indigo-600,
.hover\:text-indigo-600:hover {
  color: var(--primary-color) !important;
}

.bg-indigo-600,
.\!bg-indigo-600 {
  background-color: var(--primary-color) !important;
}

.hover\:bg-indigo-700:hover,
.hover\:\!bg-indigo-700:hover {
  background-color: var(--primary-color-hover) !important;
}

.border-indigo-500,
.group:hover .group-hover\:border-indigo-300,
.group:hover .group-hover\:border-indigo-200 {
  border-color: var(--primary-color) !important;
}

.ring-indigo-500,
.focus\:ring-indigo-500:focus {
  --tw-ring-color: var(--primary-color) !important;
}

.focus\:border-indigo-500:focus {
  border-color: var(--primary-color) !important;
}

.text-indigo-700 {
  color: var(--primary-color) !important;
}

.bg-indigo-50 {
  background-color: var(--primary-color-shadow-light) !important;
}

.hover\:bg-indigo-50:hover {
  background-color: var(--primary-color-shadow) !important;
}

.border-indigo-100 {
  border-color: var(--primary-color-shadow-light) !important;
}

.from-indigo-600.to-indigo-500,
.bg-gradient-to-tr.from-indigo-500.to-blue-600 {
  background-image: linear-gradient(to top right, var(--primary-color), var(--primary-color-hover)) !important;
}

.bg-gradient-to-r.from-indigo-500.to-indigo-600 {
  background-image: linear-gradient(to right, var(--primary-color), var(--primary-color-hover)) !important;
}

.shadow-indigo-200,
.shadow-indigo-500\/20 {
  --tw-shadow-color: var(--primary-color-shadow) !important;
}

/* Dark mode overrides for file category backgrounds */
.dark .bg-rose-50 {
  background-color: rgba(244, 63, 94, 0.12) !important;
  border-color: rgba(244, 63, 94, 0.25) !important;
}
.dark .bg-sky-50 {
  background-color: rgba(14, 165, 233, 0.12) !important;
  border-color: rgba(14, 165, 233, 0.25) !important;
}
.dark .bg-emerald-50 {
  background-color: rgba(16, 185, 129, 0.12) !important;
  border-color: rgba(16, 185, 129, 0.25) !important;
}
.dark .bg-purple-50 {
  background-color: rgba(168, 85, 247, 0.12) !important;
  border-color: rgba(168, 85, 247, 0.25) !important;
}
.dark .bg-amber-50 {
  background-color: rgba(245, 158, 11, 0.12) !important;
  border-color: rgba(245, 158, 11, 0.25) !important;
}
.dark .bg-orange-50 {
  background-color: rgba(249, 115, 22, 0.12) !important;
  border-color: rgba(249, 115, 22, 0.25) !important;
}
.dark .bg-indigo-50\/50 {
  background-color: rgba(99, 102, 241, 0.12) !important;
  border-color: rgba(99, 102, 241, 0.25) !important;
}

/* Dark mode overrides for folder category tags */
.dark .bg-amber-50 {
  background-color: rgba(245, 158, 11, 0.1) !important;
  color: #fbbf24 !important;
  border-color: rgba(245, 158, 11, 0.2) !important;
}
.dark .bg-indigo-50 {
  background-color: rgba(99, 102, 241, 0.1) !important;
  color: #818cf8 !important;
  border-color: rgba(99, 102, 241, 0.2) !important;
}
.dark .bg-emerald-50 {
  background-color: rgba(16, 185, 129, 0.1) !important;
  color: #34d399 !important;
  border-color: rgba(16, 185, 129, 0.2) !important;
}
.dark .bg-slate-50 {
  background-color: rgba(148, 163, 184, 0.1) !important;
  color: #cbd5e1 !important;
  border-color: rgba(148, 163, 184, 0.2) !important;
}

/* Scrollbars */
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
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.animate-fade-in {
  animation: fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* Slide up and down transitions */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>