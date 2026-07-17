<template>
  <div class="flex flex-col h-full overflow-hidden font-sans min-h-0">
	<div class="grid grid-cols-2 lg:grid-cols-6 gap-3 md:gap-4 p-2 flex-shrink-0">
		<Card 
			v-for="stat in kpiStats" 
			:key="stat.label" 
			:class="[
				'!shadow-sm bg-white cursor-pointer transition-all duration-200 border active:scale-[0.98]',
				'border-slate-100 hover:border-slate-200'
			]"
			@click="filterByStat(stat.label)"
		>
			<div class="flex items-center justify-between">
				<span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">{{ stat.label }}</span>
				<div :class="['p-1.5 rounded-lg', stat.bg]">
					<component :is="stat.icon" class="w-4 h-4" :class="stat.color" />
				</div>
			</div>

			<div class="text-2xl font-black mt-2 text-slate-900 flex items-center h-8">
				<template v-if="tickets.loading">
					<div class="w-4 h-4 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
				</template>
				<span v-else>{{ stat.value }}</span>
			</div>
		</Card>
	</div>

	<div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm flex flex-col gap-3 mx-2 my-4 relative z-10 overflow-visible flex-shrink-0">
	  <!-- Top Row: Search & Actions -->
	  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 w-full pb-2 border-b border-slate-100">
		<div class="relative w-full sm:w-80">
		  <IconSearch class="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
		  <input v-model="searchQuery" placeholder="Search subject or ID..." 
				 class="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-1 focus:ring-blue-500 outline-none transition-all" />
		</div>

		<div class="flex items-center gap-2 ml-auto sm:ml-0">
		  <!-- Refresh Button -->
		  <Button
			variant="outline"
			class="!text-slate-600 !px-3 !h-9 border border-slate-200 hover:bg-slate-50 transition-all"
			@click="tickets.reload()"
		  >
			<template #prefix><IconRefresh class="w-4 h-4 text-slate-500" /></template>
		  </Button>

		  <!-- Actions Dropdown / New Ticket Button -->
		  <Dropdown
			v-if="selectedTickets.size > 0"
			:options="actionsOptions"
		  >
			<Button
			  variant="solid"
			  class="!bg-slate-800 !text-white !text-xs !px-5 !h-9 !shadow-md hover:!bg-slate-900 transition-all"
			>
			  Actions
			  <template #suffix><FeatherIcon name="chevron-down" class="w-4 h-4 shrink-0" /></template>
			</Button>
		  </Dropdown>

		  <Button
			v-else
			variant="solid"
			class="!text-xs !px-5 !h-9 !shadow-md transition-all"
			style="background-color: var(--primary-color); box-shadow: 0 4px 6px -1px var(--primary-color-shadow);"
			@click="isEditMode=false; resetForm(); customerResource.reload(); departmentResource.reload(); showCreateDialog=true"
		>
			<template #prefix><IconPlus class="w-4 h-4" /></template> New Ticket
		</Button>
		</div>
	  </div>

	  <!-- Bottom Row: Filters -->
	  <div class="filter-row flex flex-nowrap overflow-x-auto pb-1.5 gap-2 w-full custom-scrollbar sm:flex-wrap sm:overflow-visible sm:pb-0 sm:items-center sm:gap-2">
		<select 
		  v-model="selectedFilters.status"
		  :class="[
			'px-3 h-9 rounded-lg border text-xs font-semibold focus:outline-none cursor-pointer min-w-[120px] shrink-0 transition-all duration-200',
			selectedFilters.status !== ''
			  ? 'border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/10 font-black shadow-sm ring-1 ring-[var(--primary-color)]/10 focus:ring-2 focus:ring-[var(--primary-color)]/20 dark:border-indigo-400 dark:text-indigo-300'
			  : 'border-slate-200 bg-slate-50 text-slate-600 dark:text-slate-300 dark:bg-slate-900 dark:border-slate-700 focus:ring-2 focus:ring-blue-500/20'
		  ]"
		>
		  <option value="">Select Status</option>
		  <option value="Open">Open</option>
		  <option value="Replied">Replied</option>
		  <option value="Resolved">Resolved</option>
		  <option value="Closed">Closed</option>
		</select>

		<select 
		  v-model="selectedFilters.customer"
		  :class="[
			'px-3 h-9 rounded-lg border text-xs font-semibold focus:outline-none cursor-pointer min-w-[120px] shrink-0 transition-all duration-200',
			selectedFilters.customer !== ''
			  ? 'border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/10 font-black shadow-sm ring-1 ring-[var(--primary-color)]/10 focus:ring-2 focus:ring-[var(--primary-color)]/20 dark:border-indigo-400 dark:text-indigo-300'
			  : 'border-slate-200 bg-slate-50 text-slate-600 dark:text-slate-300 dark:bg-slate-900 dark:border-slate-700 focus:ring-2 focus:ring-blue-500/20'
		  ]"
		>
		  <option value="">Client</option>
		  <option v-for="opt in customerFilterSelectOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
		</select>

		<select 
		  v-model="selectedFilters.department"
		  :class="[
			'px-3 h-9 rounded-lg border text-xs font-semibold focus:outline-none cursor-pointer min-w-[120px] shrink-0 transition-all duration-200',
			selectedFilters.department !== ''
			  ? 'border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/10 font-black shadow-sm ring-1 ring-[var(--primary-color)]/10 focus:ring-2 focus:ring-[var(--primary-color)]/20 dark:border-indigo-400 dark:text-indigo-300'
			  : 'border-slate-200 bg-slate-50 text-slate-600 dark:text-slate-300 dark:bg-slate-900 dark:border-slate-700 focus:ring-2 focus:ring-blue-500/20'
		  ]"
		>
		  <option value="">Department</option>
		  <option v-for="opt in departmentFilterSelectOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
		</select>

		<select 
		  v-model="selectedFilters.priority"
		  :class="[
			'px-3 h-9 rounded-lg border text-xs font-semibold focus:outline-none cursor-pointer min-w-[120px] shrink-0 transition-all duration-200',
			selectedFilters.priority !== ''
			  ? 'border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/10 font-black shadow-sm ring-1 ring-[var(--primary-color)]/10 focus:ring-2 focus:ring-[var(--primary-color)]/20 dark:border-indigo-400 dark:text-indigo-300'
			  : 'border-slate-200 bg-slate-50 text-slate-600 dark:text-slate-300 dark:bg-slate-900 dark:border-slate-700 focus:ring-2 focus:ring-blue-500/20'
		  ]"
		>
		  <option value="">Priority</option>
		  <option value="Low">Low</option>
		  <option value="Medium">Medium</option>
		  <option value="High">High</option>
		  <option value="Urgent">Urgent</option>
		</select>

		<select 
		  v-model="selectedFilters.raised_by"
		  :class="[
			'px-3 h-9 rounded-lg border text-xs font-semibold focus:outline-none cursor-pointer min-w-[120px] shrink-0 transition-all duration-200',
			selectedFilters.raised_by !== ''
			  ? 'border-[var(--primary-color)] text-[var(--primary-color)] bg-blue-50/10 font-black shadow-sm ring-1 ring-[var(--primary-color)]/10 focus:ring-2 focus:ring-[var(--primary-color)]/20 dark:border-indigo-400 dark:text-indigo-300'
			  : 'border-slate-200 bg-slate-50 text-slate-600 dark:text-slate-300 dark:bg-slate-900 dark:border-slate-700 focus:ring-2 focus:ring-blue-500/20'
		  ]"
		>
		  <option value="">Raised By</option>
		  <option v-for="opt in raisedByFilterSelectOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
		</select>

		<Button 
		  v-if="hasActiveFilters"
		  variant="ghost" 
		  class="!text-red-500 hover:!bg-red-50 !px-2.5 !h-9 shrink-0"
		  @click="resetFilters"
		>
		  <template #prefix><IconX class="w-3.5 h-3.5" /></template>
		  Clear
		</Button>
	  </div>
	</div>

	<div class="flex-1 overflow-y-auto md:overflow-hidden px-2 pb-2 flex flex-col min-h-0">
	  <div class="bg-white rounded-xl border border-slate-800 dark:border-slate-700 shadow-sm flex flex-col min-h-[420px] md:min-h-0 md:flex-1 md:overflow-hidden">
		  <ListView
		  class="h-full flex flex-col min-h-0"
		  :columns="columns"
		  :rows="tickets.data?.tickets || []" 
		  :options="{ 
			  selectable: true, 
			  showTooltip: true, 
			  resizeColumn: true, 
			  onRowClick: (row) => openEditDialog(row) 
		  }"
		  row-key="name"
		  v-model:selections="selectedTickets"
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
			  v-for="row in (tickets.data?.tickets || [])" 
			  :key="row.name" 
			  :row="row"
			  >
			<ListRowItem :item="item">
				
				<template v-if="column.key === 'name'">
				<span class="font-bold text-blue-600">#{{ row.name }}</span>
				</template>

				<template v-if="column.key === 'subject'" #prefix>
				<div class="flex items-center -space-x-2 mr-4 isolate">
					<Avatar 
					v-for="(assignment, index) in (row.assigned_to || []).slice(0, 3)" 
					:key="index"
					:image="getUserAvatarImage(assignment)"
					:label="assignment" 
					size="lg" 
					class="border-2 border-white ring-1 ring-gray-100 rounded-full"
					v-tooltip="assignment"
					/>
					<div 
					v-if="row.assigned_to?.length > 3" 
					class="flex items-center justify-center h-7 w-7 rounded-full bg-gray-100 border-2 border-white text-[10px] font-medium text-gray-600 ring-1 ring-gray-100 z-10"
					>
					+{{ row.assigned_to.length - 3 }}
					</div>
				</div>
				</template>

				<template v-if="column.key === 'status'">
				<div class="flex items-center">
					<div class="h-2 w-2 rounded-full mr-2 shrink-0" :class="getStatusColor(item)" />
					<span class="text-sm truncate">
					{{ item }}
					<span v-if="row.is_overdue" class="text-red-500 font-bold ml-1 text-xs">
						- (Overdue)
					</span>
					</span>
				</div>
				</template>

				<template v-if="column.key === 'priority'">
				<Badge :theme="getPriorityTheme(item)" variant="subtle" :label="item" />
				</template>

				<template v-if="column.key === 'description_for_list'">
				<div class="max-w-[500px] truncate text-slate-500 text-sm" v-tooltip="item">
					{{ item || '—' }}
				</div>
				</template>

				<template v-if="column.key === 'creation'">
				<div class="flex items-center gap-2 text-slate-500 whitespace-nowrap">
					<IconClock class="w-3.5 h-3.5" v-if="row.creation"/>
					<span class="text-xs font-medium">
					{{ row.creation ? formatDateTime(row.creation) : '' }}
					</span>
				</div>
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
				<span v-else class="text-xs text-slate-400 font-medium pl-2">—</span>
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
				<span v-else class="text-xs text-slate-400 font-medium pl-2">—</span>
				</template>

				<template v-if="column.key === 'exp_end_date'">
				<div class="flex items-center gap-2 text-slate-500 whitespace-nowrap">
					<IconClock class="w-3.5 h-3.5" v-if="row.exp_end_date"/>
					<span class="text-xs font-medium">
					{{ row.exp_end_date ? formatDate(row.exp_end_date) : '' }}
					</span>
				</div>
				</template>

			</ListRowItem>
			</ListRow>
		  </ListRows>
		  </div>
		  </ListView>
		<!-- Pagination controls -->
		<div class="flex items-center justify-between border-t border-slate-100 bg-white px-4 py-3 sm:px-6">
		  <div class="flex flex-1 justify-between sm:hidden">
			<Button 
			  :disabled="currentPage === 1" 
			  @click="currentPage--"
			  variant="ghost"
			>
			  Previous
			</Button>
			<Button 
			  :disabled="currentPage >= totalPages" 
			  @click="currentPage++"
			  variant="ghost"
			>
			  Next
			</Button>
		  </div>
		  <div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
			<div>
			  <p class="text-xs text-slate-500">
				Showing
				<span class="font-bold text-slate-800">{{ totalCount > 0 ? (currentPage - 1) * pageLength + 1 : 0 }}</span>
				to
				<span class="font-bold text-slate-800">{{ Math.min(currentPage * pageLength, totalCount) }}</span>
				of
				<span class="font-bold text-slate-800">{{ totalCount }}</span>
				results
			  </p>
			</div>
			<div>
			  <nav class="isolate inline-flex -space-x-px rounded-lg bg-slate-50 p-1 border border-slate-200/50" aria-label="Pagination">
				<button 
				  @click="currentPage = Math.max(1, currentPage - 1)"
				  :disabled="currentPage === 1"
				  class="relative inline-flex items-center rounded-md p-1 text-slate-400 hover:bg-white hover:text-slate-700 disabled:opacity-50 disabled:hover:bg-transparent transition-all mr-1"
				>
				  <span class="sr-only">Previous</span>
				  <IconChevronLeft class="w-3.5 h-3.5" />
				</button>
				
				<template v-for="(page, idx) in paginationPages" :key="idx">
				  <button 
					v-if="page !== '...'"
					@click="currentPage = page"
					:class="[
					  'relative inline-flex items-center justify-center rounded-md text-[11px] font-bold transition-all px-2.5 py-1 min-w-[28px]',
					  currentPage === page 
						? 'bg-blue-600 text-white shadow-sm' 
						: 'text-slate-600 hover:bg-white hover:text-slate-900'
					]"
				  >
					{{ page }}
				  </button>
				  <span 
					v-else 
					class="relative inline-flex items-center justify-center text-[11px] font-semibold text-slate-400 px-1.5 py-1"
				  >
					...
				  </span>
				</template>

				<button 
				  @click="currentPage = Math.min(totalPages, currentPage + 1)"
				  :disabled="currentPage === totalPages"
				  class="relative inline-flex items-center rounded-md p-1 text-slate-400 hover:bg-white hover:text-slate-700 disabled:opacity-50 disabled:hover:bg-transparent transition-all ml-1"
				>
				  <span class="sr-only">Next</span>
				  <IconChevronRight class="w-3.5 h-3.5" />
				</button>
			  </nav>
			</div>
		  </div>
		</div>
	  </div>
	</div>

	<Dialog v-model="showBulkDeleteDialog" 
		:options="{ 
		title: 'Delete Selected Tickets', 
		size: 'sm',
		actions: [
			{ label: 'Delete', variant: 'solid', theme: 'red', loading: saving, onClick: executeBulkDelete },
			{ label: 'Cancel', variant: 'ghost', onClick: () => (showBulkDeleteDialog = false) }
		] 
		}">
	  <template #body-content>
		<p class="text-sm text-slate-600 leading-relaxed py-2">
		  Are you sure you want to permanently delete the <span class="font-bold text-slate-900">{{ selectedTickets.size }}</span> selected ticket(s)? This action cannot be undone.
		</p>
	  </template>
	</Dialog>

	<Dialog v-model="showErrorDialog" 
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

	<Dialog v-model="showCreateDialog" :options="dialogOptions">
	  <template #body-content>
		<div class="space-y-6 py-2">
		  <p v-if="ticketFormError" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
			{{ ticketFormError }}
		  </p>
		  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<div class="space-y-4">
			  <div :class="['rounded-lg transition-all', { 'field-invalid-blink': ticketInvalidFields.subject }]">
				<FormControl label="Subject *" v-model="ticketForm.subject" />
			  </div>
			  <FormControl
				type="select"
				label="Customer"
				:options="customerFilterSelectOptions"
				v-model="ticketForm.customer"
				placeholder="Client"
			  />
			 <FormControl label="Raised By" type="select" v-model="ticketForm.raised_by" :options="raisedByFilterOptions" :disabled="isFieldDisabled"/>
			</div>
			<div class="space-y-4">
			  <div class="grid grid-cols-2 gap-4">
				<FormControl label="Type" type="select" :options="['Bug', 'Support', 'Technical']" v-model="ticketForm.ticket_type"/>
				<FormControl label="Priority" type="select" :options="['Low', 'Medium', 'High', 'Urgent']" v-model="ticketForm.priority" />
			  </div>
			  <FormControl
				type="select"
				label="Department"
				:options="departmentFilterSelectOptions"
				v-model="ticketForm.department"
				placeholder="Department"
			  />
			  <!-- <FormControl label="Agent Group" type="text" v-model="ticketForm.agent_group" /> -->
			</div>
		  </div>
		  <div class="space-y-2 border-t pt-4">
			<label class="text-xs font-medium text-slate-600 uppercase tracking-wider">Description</label>
			<div class="border rounded-lg bg-white shadow-sm overflow-hidden min-h-[200px]">
			  <TextEditor
				editor-class="prose-sm max-w-none p-6 outline-none"
				:content="ticketForm.description"
				@change="(val) => (ticketForm.description = val)"
				:fixed-menu="true"
			  />
			</div>
		  </div>
		</div>
	  </template>
	</Dialog>

	<Transition name="slide">
		<div v-if="showEditTicket" class="fixed inset-0 flex justify-end z-50">
			<div class="absolute inset-0 bg-slate-900/20 backdrop-blur-[2px]" @click="showEditTicket=false"></div>
			
			<div class="relative w-full md:max-w-4xl lg:max-w-5xl h-full bg-white flex flex-col md:flex-row shadow-2xl border-l overflow-y-auto md:overflow-hidden">
				<div v-if="!editPanelReady" class="flex-1 grid place-items-center bg-slate-50/30 min-h-0">
					<div class="flex items-center gap-3 text-slate-500">
						<div class="w-5 h-5 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
						<span class="text-sm font-medium">Loading ticket details...</span>
					</div>
				</div>

				<div v-else class="flex w-full h-full flex-col md:flex-row">
					<!-- Left Column: Activity (Full Width) -->
					<div class="h-[400px] md:h-full md:w-[60%] flex flex-col bg-white min-h-0 border-b md:border-b-0 md:border-r border-slate-100 shrink-0">
						<header class="p-4 border-b bg-white flex justify-between items-center shrink-0 shadow-sm z-10">
							<h3 class="text-sm font-bold text-slate-800">Activity</h3>
						</header>
						
						<div class="flex-grow md:flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar relative before:absolute before:inset-y-0 before:left-[40px] before:w-0.5 before:bg-slate-200/50">
							<!-- Timeline Activity Comments -->
							<div v-for="c in comments.data || []" :key="c.name" class="relative pl-12 group">
								<!-- Timeline Avatar absolute aligned on the rail line -->
								<div class="absolute left-0 top-1 z-10">
									<Avatar 
										:image="getUserAvatarImage(c.owner)"
										:label="getUserLabel(c.owner) || 'User'" 
										size="md" 
										class="ring-4 ring-white shadow-sm shrink-0" 
									/>
								</div>

								<!-- Comment Card -->
								<div class="bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm hover:shadow-md transition-all duration-200">
									<div class="flex items-center justify-between mb-2">
										<div class="flex items-center gap-1.5 text-xs">
											<span class="font-bold text-slate-800">{{ getUserLabel(c.owner) }}</span>
											<span class="text-slate-300">·</span>
											<span class="text-slate-400 font-medium">{{ dayjs(c.creation).fromNow() }}</span>
										</div>

										<!-- Comment Edit/Delete Actions -->
										<div class="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity" v-if="c.owner === session.user">
											<button 
												@click="startEditing(c)"
												class="p-1 hover:bg-slate-50 rounded text-slate-400 hover:text-blue-600 transition-colors"
												title="Edit Comment"
											>
												<IconEdit3 class="w-3.5 h-3.5" />
											</button>
											<button 
												@click="handleDeleteComment(c.name)"
												class="p-1 hover:bg-red-50 rounded text-slate-400 hover:text-red-600 transition-colors"
												title="Delete Comment"
											>
												<IconTrash2 class="w-3.5 h-3.5" />
											</button>
										</div>
									</div>

									<div class="text-sm text-slate-600 leading-relaxed">
										<div v-if="editingCommentName === c.name" class="space-y-3">
											<FormControl 
												type="textarea"
												v-model="editContent" 
												class="w-full rounded-xl border border-slate-200 p-2 text-sm focus:ring-1 focus:ring-blue-500 outline-none resize-none"
											/>
											<div class="flex justify-end gap-2">
												<Button size="sm" variant="ghost" @click="cancelEdit">Cancel</Button>
												<Button size="sm" variant="solid" @click="handleUpdateComment(c.name)" class="!bg-blue-600">Save</Button>
											</div>
										</div>
										<div v-else class="prose prose-sm max-w-none text-slate-600" v-html="c.content"></div>
									</div>
								</div>
							</div>

							<!-- Empty State Placeholder -->
							<div v-if="!(comments.data && comments.data.length > 0)" class="flex flex-col items-center justify-center py-8 text-slate-400 bg-white rounded-2xl border border-dashed border-slate-200/60 mx-2 my-2 shadow-sm">
								<IconMessageSquare class="w-8 h-8 mb-2 opacity-25 text-slate-500" />
								<p class="text-[11px] font-semibold italic text-slate-400">No comments yet. Start the conversation!</p>
							</div>
						</div>

						<div class="p-4 bg-white border-t shrink-0">
							<CommentBox
								v-model="newComment"
								:avatar="getUserAvatarImage(session.user)"
								:user="session.user"
								:userName="session.userFullName"
								placeholder="Type a message..."
								:loading="comments.loading"
								@submit="addComment"
							/>
						</div>
					</div>

					<!-- Right Column: Ticket Details Form (40% Width) -->
					<div class="w-full md:w-[40%] md:shrink-0 flex flex-col bg-white min-h-0">
						<header class="p-4 border-b flex justify-between items-center bg-white shrink-0 shadow-sm z-10">
							<div class="min-w-0 flex-1 mr-2">
								<div class="flex flex-wrap items-center gap-1.5">
									<span class="text-[10px] font-bold text-blue-600 bg-blue-50 border border-blue-100 rounded-md px-2 py-0.5 uppercase tracking-wider">{{ ticketForm.name }}</span>
									<Badge v-if="ticketForm.first_responded_on" theme="blue" variant="subtle" class="font-semibold !px-2 !py-0.5 text-[10px]" v-tooltip="'First Response: ' + formatDateTime(ticketForm.first_responded_on)">
										Responded in {{ formatDuration(ticketForm.first_response_time) }}
									</Badge>
									<Badge v-if="ticketForm.closed_on" theme="green" variant="subtle" class="font-semibold !px-2 !py-0.5 text-[10px]" v-tooltip="'Closed on: ' + formatDateTime(ticketForm.closed_on)">
										Closed in {{ formatDuration(ticketForm.closed_time) }}
									</Badge>
								</div>
								<h2 class="font-extrabold text-slate-900 text-base md:text-lg mt-2 truncate max-w-full" :title="ticketForm.subject">{{ ticketForm.subject }}</h2>
							</div>
							<div class="flex items-center gap-1.5 shrink-0">
								<Button variant="solid" size="sm" theme="blue" :loading="saving" @click="openTaskCreateDialog(ticketForm)" class="shadow-sm !px-2 sm:!px-3 text-xs">Create Task</Button>
								<Button variant="solid" size="sm" :loading="saving" @click="handleSaveTicket" class="shadow-sm !px-2 sm:!px-3 text-xs">Save</Button>
								<Button variant="ghost" size="sm" @click="showEditTicket=false" class="text-slate-400 hover:text-slate-600 !p-1">
									<IconX class="w-4 h-4"/>
								</Button>
							</div>
						</header>

						<div class="flex-grow md:flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
							<!-- Metadata Card -->
							<div class="bg-slate-50/50 rounded-2xl border border-slate-100 p-4 space-y-4 shadow-sm mb-6">
								<div class="grid grid-cols-2 gap-4">
									<FormControl label="Status" type="select" :options="['Open','Replied','Resolved','Closed']" v-model="ticketForm.status" class="!mb-0 shadow-sm" />
									<FormControl label="Priority" type="select" :options="['Low','Medium','High','Urgent']" v-model="ticketForm.priority" class="!mb-0 shadow-sm" />
								</div>

								<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 border-t pt-4">
									<FormControl label="Customer" type="select" :options="customerFilterOptions" v-model="ticketForm.customer" class="!mb-0 shadow-sm" />
									<FormControl label="Raised By" type="select" v-model="ticketForm.raised_by" :options="raisedByFilterOptions" class="!mb-0 shadow-sm" :disabled="isFieldDisabled" />
									<FormControl label="Department" type="select" v-model="ticketForm.department" :options="departmentFilterOptions" class="!mb-0 shadow-sm" />
								</div>
							</div>

							
							<!-- Description Field -->
							<div class="space-y-2 border-t pt-4">
								<label class="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest block">Description</label>
								<div class="border border-slate-200 rounded-2xl bg-white shadow-sm overflow-hidden min-h-[200px] focus-within:border-blue-300 focus-within:ring-2 focus-within:ring-blue-100/50 transition-all">
									<TextEditor
										editor-class="prose-sm max-w-none p-4 outline-none bg-white min-h-[200px]"
										:content="ticketForm.description"
										@change="(val) => (ticketForm.description = val)"
										:fixed-menu="true"
									/>
								</div>
							</div>

							<!-- Resolution Field -->
							<div class="space-y-2 border-t pt-4 pb-2" >
								<label class="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest block">Resolution</label>
								<div class="border border-slate-200 rounded-2xl bg-white shadow-sm overflow-hidden min-h-[200px] focus-within:border-blue-300 focus-within:ring-2 focus-within:ring-blue-100/50 transition-all">
									<TextEditor
										editor-class="prose-sm max-w-none p-4 outline-none bg-white min-h-[200px]"
										:content="ticketForm.resolution_details"
										@change="(val) => (ticketForm.resolution_details = val)"
										:fixed-menu="true"
									/>
								</div>
							</div>

							<!-- Attachments Field -->
							<div class="pt-4 border-t border-slate-200">
								<label class="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest block mb-3">
									Attachments
								</label>
								<div class="space-y-4">
									<FileUploader @success="handleFileUploadTicket">
										<template #default="{ openFileSelector }">
											<button 
												@click="openFileSelector" 
												class="w-full flex items-center justify-center gap-2 border-2 border-dashed border-slate-200 rounded-2xl p-4 text-slate-500 hover:border-blue-400 hover:text-blue-500 hover:bg-blue-50/30 transition-all group"
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
											class="group flex items-center justify-between bg-white border border-slate-200 rounded-xl shadow-sm hover:border-blue-300 hover:shadow-md transition-all overflow-hidden p-2"
										>
											<a 
												:href="file.file_url" 
												target="_blank" 
												class="flex flex-1 items-center gap-2.5 truncate"
											>
												<div class="h-8 w-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
													<IconBriefcase class="w-4 h-4" /> 
												</div>
												<div class="truncate text-left">
													<span class="block truncate font-semibold text-slate-700 text-xs group-hover:text-blue-600 transition-colors">
														{{ file.file_name }}
													</span>
													<span class="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Attachment</span>
												</div>
											</a>

											<button 
												@click.stop="removeAttachmentTicket(idx)" 
												class="p-2 ml-1 hover:bg-red-50 rounded-lg text-slate-400 hover:text-red-500 transition-colors"
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
		:options="{ 
		title: 'Create Task', 
		size: '4xl',
		actions: [
			{ label: 'Create Task', variant: 'solid', loading: taskSaving, onClick: handleSaveTask },
			{ label: 'Cancel', variant: 'ghost', onClick: () => (showCreateTaskDialog = false) }
		] 
		}">
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
			  <FormControl type="select" label="Project" v-model="newTask.project" :options="projectResource.data" />
			  <FormControl type="select" label="Department" v-model="newTask.department" :options="departmentResourceTask.data" />
			  <FormControl type="select" label="Status" v-model="newTask.status" :options="statusOptions.map(s => s.value)" />
			  

			</div>
			<div class="space-y-4">
			  <FormControl type="select" label="Priority" v-model="newTask.priority" :options="priorityOptions" />
			  <FormControl type="date" label="Start Date" v-model="newTask.assigned_date" />
			  <FormControl type="date" label="Deadline" v-model="newTask.exp_end_date" />
			  <FormControl type="number" label="Expected Time (In Hrs)" v-model="newTask.expected_time" />
			</div>
			<div class="space-y-4">
			  <FormControl type="select" label="Assigned By" v-model="newTask.assigned_by" :options="userResourceTask.data" :disabled="isTaskFieldDisabled" />
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
			<label class="text-xs font-medium text-slate-600 uppercase">Attachments</label>
			<div class="border rounded-lg overflow-hidden border-slate-200">
			  <table class="w-full text-left text-sm">
				<thead class="bg-slate-50 border-b border-slate-200">
				  <tr>
					<th class="px-4 py-2">File Name</th>
					<th class="px-4 py-2 text-right"></th>
				  </tr>
				</thead>
				<tbody class="divide-y divide-slate-100 bg-white">
				  <tr v-for="(file, index) in newTask.attachments" :key="index">
					<td class="px-4 py-2">
					  <a :href="file.file_url" target="_blank" class="text-blue-600 flex items-center gap-2">
						<IconBriefcase class="w-3.5 h-3.5" /> {{ file.file_name }}
					  </a>
					</td>
					<td class="px-4 py-2 text-right">
					  <Button variant="ghost" @click="removeAttachment(index)" class="!text-red-500">
						<IconPlus class="w-4 h-4 rotate-45" />
					  </Button>
					</td>
				  </tr>
				</tbody>
			  </table>
			</div>
		  </div>

		  <div class="space-y-2 border-t pt-4">
			<label class="text-xs font-medium text-slate-600 uppercase tracking-wider">Task Description</label>
			<div class="border rounded-lg bg-white shadow-sm overflow-hidden editor-container">
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

// Friendly labels for Autocomplete dropdowns
function getClientLabel(val) {
	if (!val) return "Client"
	const match = customerFilterOptions.value.find((c) => c.value === val)
	return match ? match.label : val
}

function getDepartmentLabel(val) {
	if (!val) return "Department"
	const match = departmentFilterOptions.value.find((d) => d.value === val)
	return match ? match.label : val
}

function getUserLabel(val, defaultLabel = "User") {
	if (!val) return defaultLabel
	const match = raisedByFilterOptions.value.find((u) => u.value === val)
	return match ? match.label : val
}

import IconAlertCircle from "~icons/lucide/alert-circle"
import IconBriefcase from "~icons/lucide/briefcase"
import IconCheckCircle from "~icons/lucide/check-circle"
import IconChevronLeft from "~icons/lucide/chevron-left"
import IconChevronRight from "~icons/lucide/chevron-right"
import IconClock from "~icons/lucide/clock"
import IconEdit3 from "~icons/lucide/edit-3"
import IconHash from "~icons/lucide/hash"
import IconList from "~icons/lucide/list"
import IconMessageSquare from "~icons/lucide/message-square"
// Icons
import IconPlus from "~icons/lucide/plus"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconSearch from "~icons/lucide/search"
import IconTrash2 from "~icons/lucide/trash-2"
import IconUser from "~icons/lucide/user"
import IconX from "~icons/lucide/x"
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
const tactixDepartment = session.tactixDepartment
const isTactixDeptHead = session.isTactixDeptHead

const selectedFilters = reactive({
	status: "",
	priority: "",
	customer: "",
	raised_by: "",
	department: "",
})

/* RESOURCES */
const ticketFilters = computed(() => {
	const f = {}
	if (searchQuery.value) f.subject = ["like", `%${searchQuery.value}%`]
	if (selectedFilters.status) f.status = selectedFilters.status
	if (selectedFilters.priority) f.priority = selectedFilters.priority
	if (selectedFilters.customer) f.customer = selectedFilters.customer
	if (selectedFilters.raised_by) f.raised_by_user = selectedFilters.raised_by
	if (selectedFilters.department) f.department = selectedFilters.department
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
		currentPage.value = 1
		fetchTickets()
		fetchTicketSummary()
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
	filters: { enabled: 1, name: ["not in", ["Administrator", "Guest"]] },
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

const departmentResource = createListResource({
	doctype: "Tactix Department",
	fields: ["name"],
	auto: true,
	transform: (departments) => {
		const departmentRows = Array.isArray(departments)
			? departments
			: Array.isArray(departments?.message)
				? departments.message
				: Array.isArray(departments?.message?.message)
					? departments.message.message
					: Array.isArray(departments?.data)
						? departments.data
						: Array.isArray(departments?.data?.message)
							? departments.data.message
							: []

		if (!departmentRows.length) return []

		return departmentRows
			.map((d) => {
				if (d == null) return null
				if (
					Object.prototype.hasOwnProperty.call(d, "label") &&
					Object.prototype.hasOwnProperty.call(d, "value")
				) {
					return { label: d.label, value: String(d.value) }
				}
				const name =
					d.name ?? d.department_name ?? d.department ?? d.label ?? d.value
				if (name == null) return null
				return { label: String(name), value: String(name) }
			})
			.filter((opt) => opt && opt.value !== "" && opt.value != null)
	},
	pageLength: 10000,
})

const departmentResourceTask = createListResource({
	doctype: "Department",
	fields: ["name"],
	auto: true,
	transform: (departments) =>
		departments.map((d) => ({ label: d.name, value: d.name })),
	pageLength: 10000,
})

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

const customerFilterOptions = computed(() =>
	normalizeOptions(customerResource.data, [
		"name",
		"customer_name",
		"customer",
	]),
)
const departmentFilterOptions = computed(() =>
	normalizeOptions(departmentResource.data, [
		"name",
		"department_name",
		"department",
	]),
)
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
const customerFilterSelectOptions = computed(() => [
	{ label: "Client", value: "" },
	...customerFilterOptions.value,
])
const departmentFilterSelectOptions = computed(() => [
	{ label: "Department", value: "" },
	...departmentFilterOptions.value,
])
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

const comments = createResource({
	url: "tactix.api.ticket.get_comments",
	initialData: [],
	auto: false,
})

/* DIALOG CONFIG */
const dialogOptions = computed(() => ({
	title: isEditMode.value ? "Edit Ticket" : "Create New Ticket",
	size: "4xl",
	actions: [
		{
			label: isEditMode.value ? "Save Changes" : "Create Ticket",
			variant: "solid",
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
const emptyTicket = () => ({
	name: "",
	subject: "",
	raised_by: session.user,
	raised_by_user: "",
	status: "Open",
	priority: "Medium",
	ticket_type: "Support",
	department: isTicketRaiser && tactixDepartment ? tactixDepartment : "",
	agent_group: "",
	description: "",
	customer: isTicketRaiser && ticketCustomerId ? ticketCustomerId : "",
	resolution_details: "",
	attachments: [],
})

const ticketForm = reactive(emptyTicket())
const resetForm = () => {
	Object.assign(ticketForm, emptyTicket())
	ticketFormError.value = ""
	ticketInvalidFields.subject = false
}

const initialForm = {
	name: "",
	subject: "",
	project: "",
	priority: "Medium",
	status: "Open",
	ticket: "",
	exp_end_date: "",
	assigned_to: [],
	assigned_date: new Date().toISOString().split("T")[0],
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
		if (route.params.name !== ticket.name) {
			router.push({ path: `/tickets/${ticket.name}` })
		}
	})
}

async function handleSaveTicket() {
	ticketFormError.value = ""
	ticketInvalidFields.subject = false

	if (!ticketForm.subject?.trim()) {
		ticketInvalidFields.subject = true
		ticketFormError.value = "Please fill all mandatory fields: Subject."
		setTimeout(() => {
			ticketInvalidFields.subject = false
		}, 700)
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
		await createResource({ url, params }).submit()
		tickets.reload()
		showCreateDialog.value = false
		showEditTicket.value = false
		resetForm()
	} finally {
		saving.value = false
	}
}

function openTaskCreateDialog(ticket) {
	Object.assign(newTask, {
		...initialForm,
		attachments: [],
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
	} finally {
		taskSaving.value = false
	}
}

/* LISTVIEW CONFIG */
const columns = [
	{ label: "Ticket ID", key: "name", width: "140px", icon: IconHash },
	{ label: "Subject", key: "subject", width: "3.5fr", icon: IconList },
	{ label: "Client", key: "customer", width: "160px", icon: IconBriefcase },
	{
		label: "Department",
		key: "department",
		width: "400px",
		icon: IconBriefcase,
	},
	{ label: "Status", key: "status", width: "130px", icon: IconAlertCircle },
	{ label: "Priority", key: "priority", width: "130px", icon: IconBriefcase },
	{ label: "Raised By", key: "raised_by", width: "300px", icon: IconUser },
	{ label: "Raised On", key: "creation", width: "200px", icon: IconClock },
	{
		label: "First Response Time",
		key: "first_response_time",
		width: "180px",
		icon: IconClock,
	},
	{ label: "Closed Time", key: "closed_time", width: "180px", icon: IconClock },
]

const hasActiveFilters = computed(() => {
	if (searchQuery.value) return true
	return Object.values(selectedFilters).some((value) => value !== "")
})

const resetFilters = () => {
	searchQuery.value = ""
	selectedFilters.status = ""
	selectedFilters.priority = ""
	selectedFilters.raised_by = ""
	selectedFilters.customer = ""
	selectedFilters.department = ""
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
	return {
		Open: "bg-blue-400",
		Replied: "bg-orange-400",
		Resolved: "bg-green-500",
		Closed: "bg-green-500",
	}[status]
}

function getPriorityTheme(p) {
	return (
		{ High: "red", Medium: "orange", Low: "gray", Urgent: "red" }[p] || "gray"
	)
}

async function addComment() {
	if (!newComment.value) return
	await createResource({
		url: "tactix.api.ticket.add_comment",
		params: { ticket: ticketForm.name, content: newComment.value },
	}).submit()
	newComment.value = ""
	comments.submit({ ticket: ticketForm.name })
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
	}
}

async function handleDeleteComment(name) {
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
		ticketInvalidFields.subject = false
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
	if (socket) {
		socket.on("tactix_ticket_raised", onTicketRaised)
	}
})

onUnmounted(() => {
	window.removeEventListener("keydown", handleGlobalKeydown)
	if (socket) {
		socket.off("tactix_ticket_raised", onTicketRaised)
	}
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
.slide-enter-active, .slide-leave-active { transition: transform .3s cubic-bezier(0.4, 0, 0.2, 1); }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }

/* Ensure frappe-ui dialogs are always above page-level filters and sticky elements. */
:global(.dialog-overlay) { z-index: 1200; }
:global(.dialog-content) { position: relative; z-index: 1201; }
/* Keep autocomplete/select popovers above dialogs so dropdowns are usable inside modals. */
:global([data-radix-popper-content-wrapper]), :global([data-reka-popper-content-wrapper]), :global(.PopoverContent), :global(.ticket-modal-autocomplete) { z-index: 100005 !important; }
/* Ensure list-view filter dropdowns render above cards/list containers as well. */
:global(.ticket-filter-autocomplete) { z-index: 100005 !important; }

.field-invalid-blink {
	border: 1px solid #ef4444;
	box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
	animation: fieldBlink 0.7s ease-out 1;
}

@keyframes fieldBlink {
	0% { opacity: 1; transform: translateY(0); }
	30% { opacity: 0.85; transform: translateY(-1px); }
	100% { opacity: 1; transform: translateY(0); }
}
</style>