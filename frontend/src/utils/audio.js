let lastPlayTime = 0
const COOLDOWN_MS = 1000

export function playNotificationSound() {
	if (localStorage.getItem("tactix_personal_enable_sound") === "false") {
		return
	}
	if (localStorage.getItem("tactix_global_enable_sound") === "false") {
		return
	}
	const nowTime = Date.now()
	if (nowTime - lastPlayTime < COOLDOWN_MS) {
		return // Suppress double-chime triggers in rapid succession
	}
	lastPlayTime = nowTime

	try {
		const AudioContext = window.AudioContext || window.webkitAudioContext
		if (!AudioContext) return

		const ctx = new AudioContext()

		// Resume context if suspended (common browser autoplay security mitigation)
		if (ctx.state === "suspended") {
			ctx.resume()
		}

		const now = ctx.currentTime

		// First chime oscillator & gain
		const osc1 = ctx.createOscillator()
		const gain1 = ctx.createGain()
		osc1.type = "sine"
		osc1.frequency.setValueAtTime(587.33, now) // D5
		osc1.frequency.exponentialRampToValueAtTime(880, now + 0.15) // A5

		gain1.gain.setValueAtTime(0, now)
		gain1.gain.linearRampToValueAtTime(0.15, now + 0.03)
		gain1.gain.exponentialRampToValueAtTime(0.0001, now + 0.45)

		osc1.connect(gain1)
		gain1.connect(ctx.destination)

		// Second chime oscillator & gain
		const osc2 = ctx.createOscillator()
		const gain2 = ctx.createGain()
		osc2.type = "sine"
		osc2.frequency.setValueAtTime(880, now + 0.1) // A5
		osc2.frequency.exponentialRampToValueAtTime(1174.66, now + 0.25) // D6

		gain2.gain.setValueAtTime(0, now + 0.1)
		gain2.gain.linearRampToValueAtTime(0.12, now + 0.13)
		gain2.gain.exponentialRampToValueAtTime(0.0001, now + 0.6)

		osc2.connect(gain2)
		gain2.connect(ctx.destination)

		osc1.start(now)
		osc1.stop(now + 0.5)

		osc2.start(now + 0.1)
		osc2.stop(now + 0.6)
	} catch (e) {
		console.warn("Failed to play notification sound", e)
	}
}

export function playPRNotificationSound() {
	if (localStorage.getItem("tactix_personal_enable_sound") === "false") {
		return
	}
	if (localStorage.getItem("tactix_global_enable_sound") === "false") {
		return
	}
	const nowTime = Date.now()
	if (nowTime - lastPlayTime < COOLDOWN_MS) {
		return // Suppress double-chime triggers in rapid succession
	}
	lastPlayTime = nowTime

	try {
		const AudioContext = window.AudioContext || window.webkitAudioContext
		if (!AudioContext) return

		const ctx = new AudioContext()

		// Resume context if suspended (common browser autoplay security mitigation)
		if (ctx.state === "suspended") {
			ctx.resume()
		}

		const now = ctx.currentTime

		// Ascending triple tone chime: C5 -> G5 -> C6
		// First chime oscillator & gain
		const osc1 = ctx.createOscillator()
		const gain1 = ctx.createGain()
		osc1.type = "sine"
		osc1.frequency.setValueAtTime(523.25, now) // C5
		gain1.gain.setValueAtTime(0, now)
		gain1.gain.linearRampToValueAtTime(0.12, now + 0.02)
		gain1.gain.exponentialRampToValueAtTime(0.0001, now + 0.35)

		osc1.connect(gain1)
		gain1.connect(ctx.destination)

		// Second chime oscillator & gain
		const osc2 = ctx.createOscillator()
		const gain2 = ctx.createGain()
		osc2.type = "sine"
		osc2.frequency.setValueAtTime(783.99, now + 0.08) // G5
		gain2.gain.setValueAtTime(0, now + 0.08)
		gain2.gain.linearRampToValueAtTime(0.12, now + 0.1)
		gain2.gain.exponentialRampToValueAtTime(0.0001, now + 0.45)

		osc2.connect(gain2)
		gain2.connect(ctx.destination)

		// Third chime oscillator & gain
		const osc3 = ctx.createOscillator()
		const gain3 = ctx.createGain()
		osc3.type = "sine"
		osc3.frequency.setValueAtTime(1046.5, now + 0.16) // C6
		gain3.gain.setValueAtTime(0, now + 0.16)
		gain3.gain.linearRampToValueAtTime(0.12, now + 0.18)
		gain3.gain.exponentialRampToValueAtTime(0.0001, now + 0.6)

		osc3.connect(gain3)
		gain3.connect(ctx.destination)

		osc1.start(now)
		osc1.stop(now + 0.4)

		osc2.start(now + 0.08)
		osc2.stop(now + 0.5)

		osc3.start(now + 0.16)
		osc3.stop(now + 0.7)
	} catch (e) {
		console.warn("Failed to play PR notification sound", e)
	}
}

export function playSynthesizerArpeggio() {
	if (localStorage.getItem("tactix_personal_enable_sound") === "false") {
		return
	}
	if (localStorage.getItem("tactix_global_enable_sound") === "false") {
		return
	}
	const nowTime = Date.now()
	if (nowTime - lastPlayTime < COOLDOWN_MS) {
		return
	}
	lastPlayTime = nowTime

	try {
		const AudioContext = window.AudioContext || window.webkitAudioContext
		if (!AudioContext) return

		const ctx = new AudioContext()
		if (ctx.state === "suspended") ctx.resume()

		const now = ctx.currentTime

		// C Major 7 arpeggio (C5 -> E5 -> G5 -> B5) using triangle wave for a warm retro synthesizer feel
		const notes = [523.25, 659.25, 783.99, 987.77]

		notes.forEach((freq, idx) => {
			const osc = ctx.createOscillator()
			const gain = ctx.createGain()
			const startTime = now + idx * 0.05

			osc.type = "triangle"
			osc.frequency.setValueAtTime(freq, startTime)

			gain.gain.setValueAtTime(0, startTime)
			gain.gain.linearRampToValueAtTime(0.08, startTime + 0.01)
			gain.gain.exponentialRampToValueAtTime(0.0001, startTime + 0.25)

			osc.connect(gain)
			gain.connect(ctx.destination)

			osc.start(startTime)
			osc.stop(startTime + 0.3)
		})
	} catch (e) {
		console.warn("Failed to play synthesizer arpeggio", e)
	}
}

export function playWarningNotificationSound() {
	// You can easily change this to playBellSound(), playTingSound(), etc.
	playSynthesizerArpeggio()
}
