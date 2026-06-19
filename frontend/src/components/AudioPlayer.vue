<script setup>
import { NodeViewWrapper, nodeViewProps } from "@tiptap/vue-3"
import { computed, onMounted, onUnmounted, ref, watch } from "vue"

const props = defineProps(nodeViewProps)

const audioRef = ref(null)
const waveformRef = ref(null)

const isPlaying = ref(false)
const isSeeking = ref(false)
const currentTime = ref(0)
const duration = ref(0)

const audioSrc = computed(() => props.node?.attrs?.src || "")

// Static realistic waveform heights for visual symmetry
const waveHeights = [
	4, 8, 12, 6, 10, 16, 8, 14, 20, 10, 16, 24, 12, 18, 14, 8, 12, 10, 6, 12, 16,
	8, 12, 6, 4,
]

const progressPercent = computed(() => {
	if (!duration.value) return 0
	return (currentTime.value / duration.value) * 100
})

function formatTime(time) {
	if (isNaN(time) || time === Number.POSITIVE_INFINITY) return "0:00"
	const mins = Math.floor(time / 60)
	const secs = Math.floor(time % 60)
	return `${mins}:${secs.toString().padStart(2, "0")}`
}

function togglePlay() {
	if (!audioRef.value) return
	if (isPlaying.value) {
		audioRef.value.pause()
	} else {
		audioRef.value.play()
	}
}

function onPlay() {
	isPlaying.value = true
}

function onPause() {
	isPlaying.value = false
}

function onTimeUpdate() {
	if (audioRef.value) {
		currentTime.value = audioRef.value.currentTime
	}
}

function onDurationChange() {
	if (
		audioRef.value &&
		audioRef.value.duration !== Number.POSITIVE_INFINITY &&
		!isNaN(audioRef.value.duration)
	) {
		duration.value = audioRef.value.duration
	}
}

function onLoadedMetadata() {
	if (!audioRef.value) return

	if (
		audioRef.value.duration === Number.POSITIVE_INFINITY ||
		isNaN(audioRef.value.duration)
	) {
		// WebM Chrome duration bug workaround: seek to the end to trigger duration calculation
		audioRef.value.currentTime = 1e101

		const onTimeUpdate = () => {
			if (
				audioRef.value.duration !== Number.POSITIVE_INFINITY &&
				!isNaN(audioRef.value.duration)
			) {
				duration.value = audioRef.value.duration
				audioRef.value.currentTime = 0
				audioRef.value.removeEventListener("timeupdate", onTimeUpdate)
			}
		}
		audioRef.value.addEventListener("timeupdate", onTimeUpdate)
	} else {
		duration.value = audioRef.value.duration
	}
}

function onEnded() {
	isPlaying.value = false
	currentTime.value = 0
}

function handleSeekEvent(e) {
	if (
		!waveformRef.value ||
		!audioRef.value ||
		!duration.value ||
		duration.value === Number.POSITIVE_INFINITY
	)
		return
	const rect = waveformRef.value.getBoundingClientRect()
	const clickX = e.clientX - rect.left
	const ratio = Math.max(0, Math.min(1, clickX / rect.width))
	audioRef.value.currentTime = ratio * duration.value
}

function startSeeking(e) {
	isSeeking.value = true
	handleSeekEvent(e)
	window.addEventListener("mousemove", handleSeeking)
	window.addEventListener("mouseup", stopSeeking)
}

function handleSeeking(e) {
	if (isSeeking.value) {
		handleSeekEvent(e)
	}
}

function stopSeeking() {
	isSeeking.value = false
	window.removeEventListener("mousemove", handleSeeking)
	window.removeEventListener("mouseup", stopSeeking)
}

function isBarActive(index) {
	const barRatio = index / waveHeights.length
	const progressRatio = duration.value ? currentTime.value / duration.value : 0
	return progressRatio >= barRatio
}

watch(audioSrc, () => {
	currentTime.value = 0
	duration.value = 0
	isPlaying.value = false
})

onMounted(() => {
	if (audioRef.value) {
		if (
			audioRef.value.duration &&
			audioRef.value.duration !== Number.POSITIVE_INFINITY
		) {
			duration.value = audioRef.value.duration
		} else {
			onLoadedMetadata()
		}
	}
})

onUnmounted(() => {
	window.removeEventListener("mousemove", handleSeeking)
	window.removeEventListener("mouseup", stopSeeking)
})
</script>

<template>
	<NodeViewWrapper as="div" class="my-3 block not-prose select-none">
		<div class="voice-note-card flex items-center gap-3 p-2.5 bg-slate-50 border border-slate-200/80 rounded-2xl max-w-[300px] hover:border-slate-300 transition-colors shadow-sm">
			<!-- Hidden Audio Element -->
			<audio
				ref="audioRef"
				:src="audioSrc"
				@play="onPlay"
				@pause="onPause"
				@timeupdate="onTimeUpdate"
				@loadedmetadata="onLoadedMetadata"
				@durationchange="onDurationChange"
				@ended="onEnded"
				preload="metadata"
			></audio>

			<!-- Play/Pause Button -->
			<button
				@click="togglePlay"
				type="button"
				class="w-9 h-9 flex items-center justify-center text-white rounded-full transition-transform active:scale-95 shadow cursor-pointer shrink-0"
				:style="{ backgroundColor: isPlaying ? '#061d43' : '#061d43', hover: '#061d43' }"
			>
				<!-- Play SVG Icon -->
				<svg v-if="!isPlaying" class="w-4 h-4 fill-current ml-0.5" viewBox="0 0 24 24">
					<path d="M8 5v14l11-7z"/>
				</svg>
				<!-- Pause SVG Icon -->
				<svg v-else class="w-4 h-4 fill-current" viewBox="0 0 24 24">
					<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
				</svg>
			</button>

			<!-- Waveform and Details -->
			<div class="flex-1 flex flex-col justify-center min-w-0">
				<!-- Waveform Seekbar -->
				<div
					ref="waveformRef"
					@mousedown="startSeeking"
					class="flex items-end gap-[3px] h-6 mb-1 cursor-pointer"
				>
					<div
						v-for="(h, idx) in waveHeights"
						:key="idx"
						:style="{ height: `${h}px` }"
						:class="[
							'w-[3px] rounded-full transition-colors pointer-events-none',
							isBarActive(idx) ? 'bg-[#061d43]' : 'bg-slate-300/80'
						]"
					></div>
				</div>

				<!-- Text Info -->
				<div class="flex items-center justify-between text-[10px] text-slate-500 font-semibold leading-none">
					<span>{{ formatTime(currentTime) }}</span>
					<span v-if="duration > 0 && duration !== Infinity">{{ formatTime(duration) }}</span>
				</div>
			</div>

			<!-- Microphone Avatar / Icon indicator -->
			<div class="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 shrink-0 border border-slate-200/50">
				<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
					<path d="M19 10v1a7 7 0 0 1-14 0v-1M12 19v4M8 23h8"/>
				</svg>
			</div>
		</div>
	</NodeViewWrapper>
</template>
