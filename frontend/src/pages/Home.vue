<template>
	<div class="flex h-screen overflow-hidden bg-white font-sans text-slate-900 antialiased">
		
		<!-- Sidebar -->
		<SideBar />

		<main class="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#F8FAFC]">
			
			<!-- Header -->
			<header class="h-14 border-b border-slate-200 bg-[#F8F8F8] flex items-center justify-between px-6 flex-shrink-0 z-40 shadow-sm shadow-slate-500/5">
				
				<!-- Search -->
				<div class="relative w-72 group">
					
				</div>
				
				<!-- Right Section -->
				<div class="flex items-center gap-3">
					<button class="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-50 rounded-md transition-all">
						<IconHelpCircle class="w-4 h-4" />
					</button>

					<div class="relative" ref="notificationContainer" v-if="!session.isTicketRaiser">
						<button
							type="button"
								class="relative inline-flex h-9 w-9 items-center justify-center rounded-md text-slate-500 transition-all hover:bg-slate-50 hover:text-slate-700"
							@click="toggleNotifications"
						>
								<IconBell class="relative z-10 w-5 h-5" />
							<span
								v-if="unreadNotifications"
									class="absolute -top-0.5 -right-0.5 z-20 min-w-4 h-4 px-0.5 flex items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white ring-2 ring-white"
							>
								{{ unreadNotifications }}
							</span>
						</button>

						<div
							v-if="showNotifications"
							class="absolute right-0 top-full mt-2 w-[22rem] overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-[0_20px_50px_rgba(0,0,0,0.1)] transition-all z-50 flex flex-col"
						>
							<div class="flex items-center justify-between gap-3 border-b border-slate-100 px-4 py-3.5 bg-slate-50/50">
								<div>
									<div class="text-xs font-bold text-slate-800 uppercase tracking-wider">Notifications</div>
									<div class="text-[10px] text-slate-400 font-medium">Task and ticket assignments</div>
								</div>
								<button
									type="button"
									class="text-[11px] font-bold text-blue-600 hover:text-blue-700 transition-colors uppercase tracking-wide border-none bg-transparent cursor-pointer outline-none"
									@click="markAllNotificationsRead"
								>
									Mark all read
								</button>
							</div>

							<div class="max-h-96 overflow-y-auto divide-y divide-slate-100/60 custom-scrollbar">
								<div v-if="notifications.length === 0" class="px-4 py-10 text-center text-xs text-slate-400 font-medium italic">
									No notifications yet
								</div>
								<button
									v-for="notification in notifications"
									:key="notification.id"
									type="button"
									class="w-full px-4 py-3.5 text-left transition-all outline-none focus:outline-none flex gap-3 items-start cursor-pointer border-y border-y-slate-50/30 first:border-t-0"
									:class="[
										notification.read 
											? 'bg-white hover:bg-slate-50/60 border-l-[3.5px] border-l-transparent opacity-75' 
											: (notification.document_type === 'Pull Request' ? 'bg-purple-50/35 hover:bg-purple-50/55 border-l-[3.5px] border-l-[#8250df]' : 'bg-blue-50/35 hover:bg-blue-50/55 border-l-[3.5px] border-l-blue-500')
									]"
									@click="handleNotificationClick(notification)"
								>
									<!-- Status Indicator Dot -->
									<div class="flex flex-col items-center pt-1 shrink-0">
										<span 
											class="h-2 w-2 rounded-full transition-all" 
											:class="[
												notification.read 
													? 'bg-transparent border border-slate-300' 
													: (notification.document_type === 'Pull Request' ? 'bg-[#8250df] shadow-sm shadow-[#8250df]/50 border border-transparent' : 'bg-blue-500 shadow-sm shadow-blue-500/50 border border-transparent'),
											]"
										/>
									</div>

									<div class="min-w-0 flex-1 space-y-2">
										<!-- Main Content -->
										<div 
											class="text-xs leading-relaxed break-words" 
											:class="[
												notification.read ? 'text-slate-500 font-normal' : 'text-slate-800 font-semibold'
											]"
											v-html="notification.title"
										>
										</div>

										<!-- Metadata -->
										<div class="flex items-center gap-2 flex-wrap">
											<span 
												v-if="notification.docname" 
												class="text-[9px] font-mono px-1.5 py-0.5 rounded leading-none font-bold"
												:class="[
													notification.read 
														? 'bg-slate-100 text-slate-500' 
														: (notification.document_type === 'Pull Request' ? 'bg-purple-50 text-purple-600 ring-1 ring-purple-600/10' : 'bg-blue-50 text-blue-600')
												]"
											>
												{{ notification.docname }}
											</span>
											
											<span class="text-[10px] text-slate-400 font-medium leading-none">
												{{ notification.assigned_by ? `From ${notification.assigned_by}` : 'From Tactix' }}
											</span>

											<span v-if="notification.creation" class="text-[9px] text-slate-400 leading-none ml-auto font-medium">
												{{ formatCreationTime(notification.creation) }}
											</span>
										</div>
									</div>
								</button>
							</div>
						</div>
					</div>
					
						<div class="relative flex items-center gap-2.5 pl-3 ml-1 border-l border-slate-200" ref="profileContainer">
						<div class="text-right leading-tight hidden sm:block">
							<!-- <div class="text-xs font-bold text-slate-700">{{ session.user }}</div> -->
							<!-- <div class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Admin</div> -->
						</div>
							<button type="button" class="w-8 h-8 rounded-lg overflow-hidden shadow-md cursor-pointer ring-1 ring-transparent hover:ring-blue-200 transition-all" @click="toggleProfileMenu">
								<img v-if="session.userImage" :src="session.userImage" class="w-full h-full object-cover" />
								<div v-else class="upper w-full h-full bg-blue-600 flex items-center justify-center text-white text-[11px] font-black uppercase hover:bg-blue-700 transition-colors">
								{{ session.user?.[0] }}
								</div>
							</button>

							<div
								v-if="showProfileMenu"
								class="absolute right-0 top-full mt-2 w-56 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_20px_50px_rgba(15,23,42,0.16)] z-50"
							>
								<div class="px-4 py-3 border-b border-slate-100 bg-slate-50/70">
									<div class="text-xs font-bold uppercase tracking-wider text-slate-700">Profile</div>
									<div class="text-[10px] text-slate-500 mt-0.5 truncate">{{ session.userFullName || session.user }}</div>
								</div>

								<button
									type="button"
									class="w-full px-4 py-3 text-left text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors flex items-center gap-2"
									:disabled="uploadingProfilePicture"
									@click="openProfilePicturePicker"
								>
									<span class="h-7 w-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
										<IconUpload class="w-4 h-4" />
									</span>
									<span>{{ session.userImage ? 'Re-upload profile picture' : 'Upload profile picture' }}</span>
								</button>

								<button
									v-if="session.userImage"
									type="button"
									class="w-full px-4 py-3 text-left text-sm font-semibold text-rose-600 hover:bg-rose-50 transition-colors flex items-center gap-2 border-t border-slate-100"
									:disabled="uploadingProfilePicture"
									@click="removeProfilePicture"
								>
									<span class="h-7 w-7 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center shrink-0">
										<IconTrash2 class="w-4 h-4" />
									</span>
									<span>Remove profile picture</span>
								</button>
							</div>
							<input ref="profileFileInput" type="file" accept="image/*" class="hidden" @change="handleProfilePictureSelected" />
					</div>
				</div>
			</header>

				<div v-if="showCropModal" class="fixed inset-0 z-[70] flex items-center justify-center bg-slate-950/55 px-4 py-6 backdrop-blur-sm">
					<div class="w-full max-w-xl overflow-hidden rounded-3xl bg-white shadow-[0_30px_90px_rgba(15,23,42,0.35)]">
						<div class="flex items-center justify-between border-b border-slate-100 px-5 py-4">
							<div>
								<div class="text-sm font-bold text-slate-900">Crop profile picture</div>
								<div class="text-[11px] text-slate-500 mt-0.5">Drag to reposition, use the slider to zoom</div>
							</div>
							<button type="button" class="rounded-lg px-2 py-1 text-sm font-semibold text-slate-500 hover:bg-slate-100" @click="closeCropModal">Cancel</button>
						</div>

						<div class="px-5 py-5">
							<div
								ref="cropStage"
								class="relative mx-auto aspect-square w-full max-w-sm overflow-hidden rounded-3xl border border-slate-200 bg-slate-100 shadow-inner touch-none select-none"
								@pointerdown="startCropDrag"
								@pointermove="moveCropDrag"
								@pointerup="endCropDrag"
								@pointerleave="endCropDrag"
							>
								<img
									v-if="cropPreviewUrl"
									:src="cropPreviewUrl"
									alt="Profile preview"
									class="absolute left-1/2 top-1/2 max-w-none rounded-none shadow-none"
									:style="cropImageStyle"
									draggable="false"
								/>

								<div class="pointer-events-none absolute inset-0 ring-1 ring-inset ring-white/70"></div>
								<div class="pointer-events-none absolute inset-0">
									<div class="absolute left-1/2 top-1/2 h-[70%] w-[70%] -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white/90 shadow-[0_0_0_999px_rgba(15,23,42,0.35)]"></div>
								</div>
							</div>

							<div class="mt-5 flex items-center gap-3">
								<span class="text-xs font-semibold uppercase tracking-wider text-slate-500">Zoom</span>
								<input v-model="cropZoom" type="range" :min="cropDefaultZoom" max="3" step="0.01" class="w-full accent-blue-600" />
							</div>
						</div>

						<div class="flex items-center justify-end gap-3 border-t border-slate-100 bg-slate-50/60 px-5 py-4">
							<button type="button" class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-white hover:text-slate-900" @click="closeCropModal">Cancel</button>
							<button type="button" class="rounded-xl bg-blue-600 px-5 py-2 text-sm font-semibold text-white shadow-md shadow-blue-200 hover:bg-blue-700 disabled:opacity-60" :disabled="uploadingProfilePicture" @click="confirmCropAndUpload">
								{{ uploadingProfilePicture ? 'Saving...' : 'OK' }}
							</button>
						</div>
					</div>
				</div>

			<!-- Routed Pages -->
			<div class="flex-1 overflow-hidden p-0 lg:p-2 flex flex-col min-h-0">
				<router-view v-slot="{ Component }">
					<transition name="fade" mode="out-in">
						<component :is="Component" />
					</transition>
				</router-view>
			</div>

			<!-- Real-time Toast Notifications Container -->
			<div class="fixed bottom-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none max-w-sm w-full">
				<transition-group name="toast">
					<div 
						v-for="toast in toastAlerts" 
						:key="toast.id"
						class="pointer-events-auto flex items-start gap-3 p-4 rounded-xl border bg-white shadow-xl border-slate-200/80"
					>
						<!-- Status Icon / indicator -->
						<div class="pt-0.5 shrink-0">
							<span 
								class="flex h-5 w-5 items-center justify-center rounded-full text-white text-[10px] font-bold"
								:class="[
									toast.type === 'pr' ? 'bg-[#8250df]' : (toast.type === 'ticket' ? 'bg-red-500' : 'bg-blue-500')
								]"
							>
								{{ toast.type === 'pr' ? 'PR' : (toast.type === 'ticket' ? '!' : '✓') }}
							</span>
						</div>
						<!-- Content -->
						<div class="flex-1 min-w-0">
							<div class="text-xs font-bold text-slate-800">{{ toast.title }}</div>
							<div class="text-[11px] text-slate-500 mt-0.5 leading-relaxed break-words" v-html="toast.message"></div>
						</div>
						<!-- Close Button -->
						<button 
							type="button" 
							@click="toastAlerts = toastAlerts.filter(t => t.id !== toast.id)"
							class="text-slate-400 hover:text-slate-600 transition-colors border-none bg-transparent cursor-pointer shrink-0"
						>
							✕
						</button>
					</div>
				</transition-group>
			</div>

		</main>
	</div>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue"
import { useRouter } from "vue-router"

import dayjs from "dayjs"
import relativeTime from "dayjs/plugin/relativeTime"
import utc from "dayjs/plugin/utc"
import SideBar from "../components/SideBar.vue"
import { session } from "../data/session"
import { useSocket } from "../socket"
import {
	playNotificationSound,
	playPRNotificationSound,
	playWarningNotificationSound,
} from "../utils/audio"

dayjs.extend(relativeTime)
dayjs.extend(utc)

import IconBell from "~icons/lucide/bell"
import IconHelpCircle from "~icons/lucide/help-circle"
// Icons
import IconSearch from "~icons/lucide/search"
import IconTrash2 from "~icons/lucide/trash-2"
import IconUpload from "~icons/lucide/upload"

const socket = useSocket()
const router = useRouter()
const showNotifications = ref(false)
const showProfileMenu = ref(false)
const showCropModal = ref(false)
const notifications = ref([])
const notificationContainer = ref(null)
const profileContainer = ref(null)
const profileFileInput = ref(null)
const uploadingProfilePicture = ref(false)
const cropStage = ref(null)
const cropPreviewUrl = ref("")
const cropSourceFile = ref(null)
const cropImageWidth = ref(0)
const cropImageHeight = ref(0)
const cropZoom = ref(0.5)
const cropOffsetX = ref(0)
const cropOffsetY = ref(0)
const cropDragging = ref(false)
const cropDragStart = ref({ x: 0, y: 0, offsetX: 0, offsetY: 0 })
const cropDefaultZoom = 0.5

const cropImageStyle = computed(() => {
	if (
		!cropPreviewUrl.value ||
		!cropImageWidth.value ||
		!cropImageHeight.value
	) {
		return {}
	}

	const stageSize = cropStage.value?.clientWidth || 320
	const coverScale = Math.max(
		stageSize / cropImageWidth.value,
		stageSize / cropImageHeight.value,
	)
	const renderedWidth = cropImageWidth.value * coverScale * cropZoom.value
	const renderedHeight = cropImageHeight.value * coverScale * cropZoom.value

	return {
		width: `${renderedWidth}px`,
		height: `${renderedHeight}px`,
		transform: `translate(-50%, -50%) translate(${cropOffsetX.value}px, ${cropOffsetY.value}px)`,
	}
})

function handleClickOutside(event) {
	if (
		notificationContainer.value &&
		!notificationContainer.value.contains(event.target)
	) {
		showNotifications.value = false
	}

	if (
		profileContainer.value &&
		!profileContainer.value.contains(event.target)
	) {
		showProfileMenu.value = false
	}
}

function toggleProfileMenu() {
	showProfileMenu.value = !showProfileMenu.value
	if (showProfileMenu.value) {
		showNotifications.value = false
		showCropModal.value = false
	}
}

function openProfilePicturePicker() {
	profileFileInput.value?.click()
}

function closeCropModal() {
	showCropModal.value = false
	cropDragging.value = false
	cropZoom.value = cropDefaultZoom
	cropOffsetX.value = 0
	cropOffsetY.value = 0
	if (cropPreviewUrl.value) {
		URL.revokeObjectURL(cropPreviewUrl.value)
	}
	cropPreviewUrl.value = ""
	cropSourceFile.value = null
	cropImageWidth.value = 0
	cropImageHeight.value = 0
}

function resetCropToCenter() {
	cropZoom.value = cropDefaultZoom
	cropOffsetX.value = 0
	cropOffsetY.value = 0
}

function openCropModalFromFile(file) {
	closeCropModal()
	cropSourceFile.value = file
	const preview = URL.createObjectURL(file)
	cropPreviewUrl.value = preview
	showCropModal.value = true

	const image = new Image()
	image.onload = () => {
		cropImageWidth.value = image.naturalWidth
		cropImageHeight.value = image.naturalHeight
		resetCropToCenter()
	}
	image.src = preview
}

function startCropDrag(event) {
	if (!cropPreviewUrl.value) return
	cropDragging.value = true
	cropDragStart.value = {
		x: event.clientX,
		y: event.clientY,
		offsetX: cropOffsetX.value,
		offsetY: cropOffsetY.value,
	}
	event.currentTarget.setPointerCapture?.(event.pointerId)
}

function moveCropDrag(event) {
	if (!cropDragging.value) return
	const stageSize = cropStage.value?.clientWidth || 320
	const coverScale = Math.max(
		stageSize / cropImageWidth.value,
		stageSize / cropImageHeight.value,
	)
	const renderedWidth = cropImageWidth.value * coverScale * cropZoom.value
	const renderedHeight = cropImageHeight.value * coverScale * cropZoom.value
	const maxOffsetX = Math.max(0, (renderedWidth - stageSize) / 2)
	const maxOffsetY = Math.max(0, (renderedHeight - stageSize) / 2)
	const deltaX = event.clientX - cropDragStart.value.x
	const deltaY = event.clientY - cropDragStart.value.y
	cropOffsetX.value = Math.min(
		maxOffsetX,
		Math.max(-maxOffsetX, cropDragStart.value.offsetX + deltaX),
	)
	cropOffsetY.value = Math.min(
		maxOffsetY,
		Math.max(-maxOffsetY, cropDragStart.value.offsetY + deltaY),
	)
}

function endCropDrag() {
	cropDragging.value = false
}

function getCropCanvas() {
	return new Promise((resolve, reject) => {
		if (!cropSourceFile.value) {
			reject(new Error("No image selected"))
			return
		}

		const image = new Image()
		const previewUrl = cropPreviewUrl.value
		const stageSize = cropStage.value?.clientWidth || 320
		const outputSize = 512

		image.onload = () => {
			const canvas = document.createElement("canvas")
			canvas.width = outputSize
			canvas.height = outputSize
			const context = canvas.getContext("2d")

			if (!context) {
				reject(new Error("Canvas unavailable"))
				return
			}

			// Match preview: coverScale fills the stage, then zoom scales UP from there
			// cropZoom 0.5 = default fit; so divide by cropZoom to invert
			const coverScale = Math.max(
				stageSize / image.naturalWidth,
				stageSize / image.naturalHeight,
			)
			const totalScale = coverScale / cropZoom.value // <-- invert zoom
			const drawWidth = image.naturalWidth * totalScale
			const drawHeight = image.naturalHeight * totalScale
			const scaleFactor = outputSize / stageSize

			context.fillStyle = "#ffffff"
			context.fillRect(0, 0, outputSize, outputSize)
			context.drawImage(
				image,
				(outputSize - drawWidth) / 2 + cropOffsetX.value * scaleFactor,
				(outputSize - drawHeight) / 2 + cropOffsetY.value * scaleFactor,
				drawWidth,
				drawHeight,
			)

			canvas.toBlob(
				(blob) => {
					if (!blob) {
						reject(new Error("Failed to create cropped image"))
						return
					}
					resolve(blob)
				},
				cropSourceFile.value.type || "image/png",
				0.95,
			)
		}

		image.onerror = () => reject(new Error("Failed to load image"))
		image.src = previewUrl
	})
}

async function confirmCropAndUpload() {
	if (!cropSourceFile.value) return
	uploadingProfilePicture.value = true
	try {
		const blob = await getCropCanvas()
		const croppedFile = new File(
			[blob],
			cropSourceFile.value.name || "profile-picture.png",
			{
				type: blob.type || "image/png",
			},
		)
		await uploadProfilePicture(croppedFile)
		closeCropModal()
		showProfileMenu.value = false
	} catch (error) {
		console.error("Failed to crop and upload profile picture", error)
	} finally {
		uploadingProfilePicture.value = false
	}
}

async function removeProfilePicture() {
	if (!session.user) return
	uploadingProfilePicture.value = true
	try {
		await createResource({
			url: "frappe.client.set_value",
			params: {
				doctype: "User",
				name: session.user,
				fieldname: {
					user_image: "",
				},
			},
		}).submit()
		session.userInfo.reload()
		showProfileMenu.value = false
	} catch (error) {
		console.error("Failed to remove profile picture", error)
	} finally {
		uploadingProfilePicture.value = false
	}
}

async function uploadProfilePicture(file) {
	const formData = new FormData()
	formData.append("file", file)
	formData.append("doctype", "User")
	formData.append("docname", session.user)
	formData.append("is_private", "0")

	const response = await fetch("/api/method/upload_file", {
		method: "POST",
		body: formData,
		credentials: "include",
	})

	if (!response.ok) {
		throw new Error("Upload failed")
	}

	const result = await response.json()
	const fileUrl = result?.message?.file_url

	if (!fileUrl) {
		throw new Error("Upload did not return a file URL")
	}

	await createResource({
		url: "frappe.client.set_value",
		params: {
			doctype: "User",
			name: session.user,
			fieldname: {
				user_image: fileUrl,
			},
		},
	}).submit()

	session.userInfo.reload()
	window.location.reload()
}

async function handleProfilePictureSelected(event) {
	const file = event.target.files?.[0]
	event.target.value = ""

	if (!file) {
		return
	}

	openCropModalFromFile(file)
}

const notificationLogResource = createResource({
	url: "frappe.client.get_list",
	params: {
		doctype: "Notification Log",
		fields: [
			"name",
			"subject",
			"from_user",
			"read",
			"document_type",
			"document_name",
			"creation",
		],
		filters: {
			for_user: session.user,
		},
		limit: 20,
		order_by: "creation desc",
	},
	initialData: [],
	auto: true,
	transform: (res) => {
		const entries = res || []
		return entries.map((entry) => {
			let formattedTitle = entry.subject || "Task update"
			if (entry.document_type === "Pull Request") {
				formattedTitle = formattedTitle
					.replace(/New PR (#\d+) raised in (.+?) by (.+)/i, "<strong>New PR Raised:</strong> $1 in <strong>$2</strong> by <strong>$3</strong>")
			} else if (entry.document_type === "Tactix Ticket" || entry.document_type === "Ticket") {
				formattedTitle = formattedTitle
					.replace(/New Ticket Raised: (.+)/i, "<strong>New Ticket Raised:</strong> '$1'")
			}
			return {
				id: entry.name,
				docname: entry.document_name || "",
				document_type: entry.document_type || "Task",
				document_name: entry.document_name || "",
				action: entry.subject?.toLowerCase().includes("removed")
					? "removed"
					: "assigned",
				title: formattedTitle,
				subject: entry.subject || "",
				assigned_by: entry.from_user || "",
				read: entry.read === 1 || entry.read === true || entry.read === "1",
				creation: entry.creation,
			}
		})
	},
})

const tactixSettingsResource = createResource({
	url: "tactix.api.generic.get_tactix_settings",
	auto: true,
	onSuccess(data) {
		if (data) {
			localStorage.setItem("tactix_global_enable_sound", data.enable_real_time_notification_sound ? "true" : "false")
			localStorage.setItem("tactix_allow_ticket_raiser_to_close_tickets", data.allow_ticket_raiser_to_close_tickets ? "1" : "0")
			localStorage.setItem("tactix_default_ticket_priority", data.default_ticket_priority || "Medium")
			localStorage.setItem("tactix_company_name", data.company_name || "Tactix")
			document.title = data.company_name || "Tactix"
		}
	}
})

const markAsReadResource = createResource({
	url: "frappe.desk.doctype.notification_log.notification_log.mark_as_read",
	auto: false,
})

const markAllAsReadResource = createResource({
	url: "frappe.desk.doctype.notification_log.notification_log.mark_all_as_read",
	auto: false,
})

function formatCreationTime(creation) {
	if (!creation) return ""
	return dayjs(creation).fromNow()
}

const unreadNotifications = computed(
	() => notifications.value.filter((notification) => !notification.read).length,
)

const toastAlerts = ref([])

function showToastAlert(title, message, type = "info") {
	const id = Date.now() + Math.random().toString(16).slice(2, 8)
	toastAlerts.value.push({ id, title, message, type })
	setTimeout(() => {
		toastAlerts.value = toastAlerts.value.filter((t) => t.id !== id)
	}, 6000)
}

function onTaskAssignment(payload) {
	notificationLogResource.reload()
	if (payload && payload.assigned_by !== session.user) {
		playNotificationSound()
		showToastAlert(
			payload.title || "Task Assigned",
			payload.subject || "A new task has been assigned to you.",
			"info"
		)
	}
}

function onPRNotification(payload) {
	if (!payload) return
	notificationLogResource.reload()
	playPRNotificationSound()
	showToastAlert(
		"New Pull Request Raised",
		`'${payload.title_text}' in <strong>${payload.repo}</strong> by <strong>${payload.author}</strong>`,
		"pr"
	)
}

function escapeHTML(str) {
	if (!str) return ""
	return str
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#039;")
}

function onTicketRaised(payload) {
	if (!payload) return
	if (session.isTicketRaiser) return
	notificationLogResource.reload()
	playWarningNotificationSound()
	showToastAlert(
		"New Ticket Raised",
		`'${escapeHTML(payload.subject)}' raised by <strong>${payload.raised_by || 'System'}</strong>`,
		"ticket"
	)
}

function hydrateNotifications() {
	const storedNotifications = notificationLogResource.data || []
	notifications.value = storedNotifications.map((entry) => ({
		id: entry.id,
		docname: entry.docname,
		document_type: entry.document_type,
		document_name: entry.document_name,
		action: entry.action,
		title: entry.title,
		subject: entry.subject,
		assigned_by: entry.assigned_by,
		read: entry.read,
		creation: entry.creation,
	}))
}

watch(
	() => notificationLogResource.data,
	() => {
		hydrateNotifications()
	},
	{ deep: true },
)

async function markNotificationRead(notification) {
	if (notification.read) return
	notification.read = true
	if (
		notification.id &&
		typeof notification.id === "string" &&
		!notification.id.startsWith("task-")
	) {
		try {
			await markAsReadResource.submit({ docname: notification.id })
			notificationLogResource.reload()
		} catch (e) {
			console.error("Failed to mark notification read", e)
		}
	}
}

async function handleNotificationClick(notification) {
	await markNotificationRead(notification)
	showNotifications.value = false

	const docType = notification.document_type || "Task"
	const docName = notification.document_name || notification.docname

	if (docType === "Pull Request") {
		if (notification.is_pr_url) {
			window.open(notification.is_pr_url, "_blank")
		}
	} else if (docName) {
		if (docType === "Task") {
			router.push({ path: `/tasks/${docName}` })
		} else if (docType === "Ticket" || docType === "Tactix Ticket") {
			router.push({ path: `/tickets/${docName}` })
		}
	}
}

async function markAllNotificationsRead() {
	notifications.value = notifications.value.map((notification) => ({
		...notification,
		read: true,
	}))

	try {
		await markAllAsReadResource.submit()
		notificationLogResource.reload()
	} catch (e) {
		console.error("Failed to mark all notifications read", e)
	}
}

function toggleNotifications() {
	showNotifications.value = !showNotifications.value
}

onMounted(() => {
	document.addEventListener("click", handleClickOutside)
	hydrateNotifications()
	if (notificationLogResource.fetch) {
		notificationLogResource.fetch()
	}

	if (!socket) {
		return
	}

	socket.on("tactix_task_assignment", onTaskAssignment)
	socket.on("github_pr_notification", onPRNotification)
	socket.on("tactix_ticket_raised", onTicketRaised)
	socket.on("notification", () => {
		notificationLogResource.reload()
		playNotificationSound()
	})
})

if (notificationLogResource.data) {
	hydrateNotifications()
}

onBeforeUnmount(() => {
	document.removeEventListener("click", handleClickOutside)
	if (cropPreviewUrl.value) {
		URL.revokeObjectURL(cropPreviewUrl.value)
	}
	if (!socket) {
		return
	}

	socket.off("tactix_task_assignment", onTaskAssignment)
	socket.off("github_pr_notification", onPRNotification)
	socket.off("tactix_ticket_raised", onTicketRaised)
	socket.off("notification")
})
</script>

<style scoped>
/* Smooth View Transitions */
.fade-enter-active,
.fade-leave-active {
	transition: all 0.15s ease-out;
}

.fade-enter-from {
	opacity: 0;
	transform: translateY(4px);
}

.fade-leave-to {
	opacity: 0;
	transform: translateY(-4px);
}

/* Toast Transition */
.toast-enter-active,
.toast-leave-active {
	transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-enter-from {
	opacity: 0;
	transform: translateY(24px) scale(0.95);
}

.toast-leave-to {
	opacity: 0;
	transform: translateX(100px) scale(0.95);
}

/* Custom Scrollbar */
main ::-webkit-scrollbar {
	width: 6px;
}
main ::-webkit-scrollbar-track {
	background: transparent;
}
main ::-webkit-scrollbar-thumb {
	background: #e2e8f0;
	border-radius: 10px;
}
main ::-webkit-scrollbar-thumb:hover {
	background: #cbd5e1;
}
</style>
