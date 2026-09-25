<template>
  <div class="min-h-screen w-full flex flex-col justify-between bg-slate-950 p-4 sm:p-6 lg:p-8 relative overflow-hidden font-sans selection:bg-blue-500 selection:text-white">
    
    <!-- Ambient Background Lighting & Orbs -->
    <div class="absolute -top-40 -left-40 w-[35rem] h-[35rem] bg-blue-600/15 rounded-full blur-[140px] pointer-events-none"></div>
    <div class="absolute -bottom-40 -right-40 w-[35rem] h-[35rem] bg-indigo-600/15 rounded-full blur-[140px] pointer-events-none"></div>

    <!-- Subtle Grid Overlay Background -->
    <div class="absolute inset-0 bg-[linear-gradient(to_right,#1e293b20_1px,transparent_1px),linear-gradient(to_bottom,#1e293b20_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_75%_75%_at_50%_50%,#000_80%,transparent_100%)] pointer-events-none"></div>

    <!-- TOP BACKGROUND CALLOUT HEADER -->
    <header class="w-full flex items-center justify-between text-[11px] font-bold text-slate-500 uppercase tracking-[0.3em] relative z-10 px-2 sm:px-6 pt-2 pointer-events-none">
      <div class="flex items-center gap-2">
        <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
        Tactix Enterprise Platform
      </div>
      <div class="hidden sm:block text-slate-600">
        Real-Time Operations & Management
      </div>
    </header>

    <!-- MAIN CENTRAL FLOATING CARD CONTAINER -->
    <main class="w-full max-w-5xl mx-auto bg-slate-900/90 rounded-3xl sm:rounded-[2.5rem] shadow-[0_32px_80px_-20px_rgba(0,0,0,0.8)] border border-slate-800/90 flex flex-col md:flex-row overflow-hidden relative z-20 backdrop-blur-2xl my-auto">
      
      <!-- LEFT SIDE: Tactix Branding & OS Vector Graphics Panel -->
      <div class="md:w-1/2 bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 p-6 sm:p-10 lg:p-12 flex flex-col justify-between items-center text-center relative overflow-hidden border-b md:border-b-0 md:border-r border-slate-800/90">
        
        <!-- Glowing Orbs inside Left Card -->
        <div class="absolute -top-20 -left-20 w-64 h-64 bg-blue-500/15 rounded-full blur-3xl pointer-events-none"></div>
        <div class="absolute -bottom-20 -right-20 w-64 h-64 bg-indigo-500/15 rounded-full blur-3xl pointer-events-none"></div>

        <!-- Prominent Left Section Logo Display -->
        <div class="relative z-10 w-full flex items-center justify-between mb-6">
          <div class="flex items-center gap-3">
            <img 
              :src="'/assets/tactix/frontend/tactix_logo_highlighted.png'" 
              alt="Tactix Logo" 
              class="h-8 sm:h-10 w-auto object-contain"
            />
            <span class="text-[10px] sm:text-xs font-extrabold px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">v15</span>
          </div>
          <div class="flex items-center gap-2 text-xs font-semibold text-slate-300 bg-slate-800/90 px-3.5 py-1.5 rounded-full border border-slate-700/80">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            System Operational
          </div>
        </div>

        <!-- Tactix OS Central Vector Illustration -->
        <div class="w-full flex justify-center py-4 sm:py-6 relative z-10">
          <svg class="w-full max-w-[280px] sm:max-w-[320px] h-auto drop-shadow-2xl" viewBox="0 0 400 320" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- Background Aura Circle -->
            <circle cx="200" cy="160" r="120" fill="#1e293b" />
            
            <!-- Floating Live Status Bubble 1 -->
            <g transform="translate(30, 48)">
              <rect x="0" y="0" width="125" height="38" rx="12" fill="#0f172a" stroke="#334155" stroke-width="2" />
              <circle cx="18" cy="19" r="6" fill="#10b981" />
              <path d="M15 19 L17 21 L21 17" stroke="#ffffff" stroke-width="2" stroke-linecap="round" />
              <text x="32" y="23" fill="#f8fafc" font-size="11" font-weight="700" font-family="sans-serif">24 Tasks Done</text>
            </g>

            <!-- Floating Live Status Bubble 2 -->
            <g transform="translate(245, 58)">
              <rect x="0" y="0" width="125" height="38" rx="12" fill="#0f172a" stroke="#334155" stroke-width="2" />
              <circle cx="18" cy="19" r="6" fill="#3b82f6" />
              <text x="32" y="23" fill="#f8fafc" font-size="11" font-weight="700" font-family="sans-serif">Tactix Drive</text>
            </g>

            <!-- Main Workspace Dashboard Panel Card -->
            <rect x="110" y="100" width="180" height="150" rx="14" fill="#0f172a" stroke="#334155" stroke-width="3" />
            
            <!-- Panel Header Bar -->
            <rect x="110" y="100" width="180" height="30" rx="12" fill="#1e293b" />
            <circle cx="126" cy="115" r="4" fill="#ef4444" />
            <circle cx="138" cy="115" r="4" fill="#eab308" />
            <circle cx="150" cy="115" r="4" fill="#22c55e" />
            <text x="175" y="119" fill="#94a3b8" font-size="10" font-weight="800" font-family="sans-serif">TACTIX WORKSPACE</text>

            <!-- Mini Metrics Charts inside Panel -->
            <rect x="125" y="145" width="70" height="40" rx="8" fill="#1e293b" />
            <rect x="133" y="167" width="8" height="10" rx="2" fill="#3b82f6" />
            <rect x="145" y="159" width="8" height="18" rx="2" fill="#60a5fa" />
            <rect x="157" y="153" width="8" height="24" rx="2" fill="#38bdf8" />
            <rect x="169" y="162" width="8" height="15" rx="2" fill="#818cf8" />

            <rect x="205" y="145" width="70" height="40" rx="8" fill="#1e293b" />
            <circle cx="240" cy="165" r="12" fill="none" stroke="#334155" stroke-width="4" />
            <circle cx="240" cy="165" r="12" fill="none" stroke="#3b82f6" stroke-width="4" stroke-dasharray="50 75" />

            <!-- Progress Task Rows -->
            <rect x="125" y="195" width="150" height="8" rx="4" fill="#334155" />
            <rect x="125" y="195" width="110" height="8" rx="4" fill="#3b82f6" />

            <rect x="125" y="210" width="150" height="8" rx="4" fill="#334155" />
            <rect x="125" y="210" width="75" height="8" rx="4" fill="#10b981" />

            <rect x="125" y="225" width="150" height="8" rx="4" fill="#334155" />
            <rect x="125" y="225" width="135" height="8" rx="4" fill="#6366f1" />
          </svg>
        </div>

        <!-- Headline & Subtitle -->
        <div class="mt-4 mb-4 relative z-10">
          <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[11px] font-bold uppercase tracking-wider mb-3">
            <IconSparkles class="w-3.5 h-3.5" />
            Operations & Management Platform
          </div>
          <h2 class="text-xl sm:text-2xl md:text-3xl font-extrabold text-white tracking-tight mb-2">
            Manage operations with precision.
          </h2>
          <p class="text-xs sm:text-sm font-normal text-slate-400 max-w-sm mx-auto leading-relaxed">
            Centralize task tracking, drive storage, performance metrics, and support ticketing in one unified workspace.
          </p>
        </div>

      </div>

      <!-- RIGHT SIDE: Clean Professional Login Form Panel -->
      <div class="md:w-1/2 bg-white dark:bg-slate-900 p-6 sm:p-10 md:p-12 lg:p-14 flex flex-col justify-center relative z-10">
        
        <div class="w-full max-w-sm mx-auto">
          
          <!-- Form Header -->
          <div class="mb-6 sm:mb-8 text-left">
            <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-1">
              Sign in to Workspace
            </h1>
            <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 font-medium">
              Welcome back! Please enter your credentials below.
            </p>
          </div>

          <!-- Login Form -->
          <form class="space-y-4" @submit.prevent="handleSubmit">
            
            <!-- Email Input -->
            <div class="space-y-1.5">
              <label class="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">Email Address</label>
              <div class="relative group">
                <Input
                  name="email"
                  type="text"
                  placeholder="name@company.com"
                  v-model="email"
                  class="!bg-slate-50 dark:!bg-slate-800 !border-slate-200 dark:!border-slate-700 !h-11 !text-slate-900 dark:!text-white placeholder:!text-slate-400 focus:!bg-white focus:!border-blue-600 transition-all duration-200 rounded-xl"
                  required
                >
                  <template #prefix>
                    <div class="pl-3.5">
                      <IconMail class="w-4 h-4 text-slate-400 group-focus-within:text-blue-600 transition-colors" />
                    </div>
                  </template>
                </Input>
              </div>
            </div>

            <!-- Password Input -->
            <div class="space-y-1.5">
              <div class="flex justify-between items-center">
                <label class="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">Password</label>
                <a href="#" class="text-xs font-bold text-blue-600 hover:text-blue-700 transition-colors hover:underline">Forgot?</a>
              </div>
              <div class="relative group">
                <Input
                  name="password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="••••••••"
                  v-model="password"
                  class="!bg-slate-50 dark:!bg-slate-800 !border-slate-200 dark:!border-slate-700 !h-11 !text-slate-900 dark:!text-white placeholder:!text-slate-400 focus:!bg-white focus:!border-blue-600 transition-all duration-200 rounded-xl"
                  required
                >
                  <template #prefix>
                    <div class="pl-3.5">
                      <IconLock class="w-4 h-4 text-slate-400 group-focus-within:text-blue-600 transition-colors" />
                    </div>
                  </template>
                </Input>
                <button 
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors z-20"
                >
                  <IconEye v-if="!showPassword" class="w-4 h-4" />
                  <IconEyeOff v-else class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- Options Row: Remember Me -->
            <div class="flex items-center justify-between pt-1 text-xs">
              <label class="flex items-center gap-2 text-slate-600 dark:text-slate-400 font-medium cursor-pointer select-none">
                <input 
                  type="checkbox" 
                  v-model="rememberMe"
                  class="w-4 h-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900 accent-slate-900"
                />
                Remember Me
              </label>
            </div>

            <!-- Error Notification -->
            <Transition name="slide-up">
              <div 
                v-if="errorMessage" 
                class="p-3.5 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/60 rounded-xl flex items-start gap-2.5 text-xs text-red-700 dark:text-red-300 font-medium leading-relaxed"
                role="alert"
              >
                <IconAlertCircle class="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                <span class="flex-1">{{ errorMessage }}</span>
                <button 
                  type="button" 
                  @click="clearError" 
                  class="text-red-400 hover:text-red-600 dark:text-red-400 dark:hover:text-red-200 shrink-0 transition-colors p-0.5"
                  aria-label="Dismiss error"
                >
                  <IconX class="w-3.5 h-3.5" />
                </button>
              </div>
            </Transition>

            <!-- Login Button -->
            <Button 
              :loading="session.login.loading" 
              variant="solid" 
              type="submit"
              class="w-full !h-12 !bg-slate-900 hover:!bg-blue-600 !text-white !rounded-xl !text-sm font-bold transition-all duration-300 shadow-md shadow-slate-900/10 hover:shadow-blue-600/25 hover:-translate-y-0.5 cursor-pointer mt-3"
            >
              <div class="flex items-center justify-center gap-2">
                Sign into Workspace
                <IconChevronRight class="w-4 h-4" />
              </div>
            </Button>

          </form>

          <!-- Footer Info -->
          <p class="text-center mt-6 sm:mt-8 text-xs text-slate-400 font-medium">
            &copy; 2026 Tactix Inc. &bull; Operations & Management Platform
          </p>

        </div>

      </div>

    </main>

    <!-- BOTTOM BACKGROUND FOOTER -->
    <footer class="w-full flex items-center justify-between text-[11px] font-bold text-slate-600 uppercase tracking-[0.2em] relative z-10 px-2 sm:px-6 pb-2 pointer-events-none">
      <div>Tactix OS v15.0</div>
    </footer>

  </div>
</template>

<script setup>
import { Button } from "frappe-ui"
import { computed, ref, watch } from "vue"
import { useRouter } from "vue-router"
import { session } from "../data/session"

import IconAlertCircle from "~icons/lucide/alert-circle"
import IconChevronRight from "~icons/lucide/chevron-right"
import IconEye from "~icons/lucide/eye"
import IconEyeOff from "~icons/lucide/eye-off"
import IconLock from "~icons/lucide/lock"
import IconMail from "~icons/lucide/mail"
import IconSparkles from "~icons/lucide/sparkles"
import IconX from "~icons/lucide/x"

const router = useRouter()
const email = ref("")
const password = ref("")
const showPassword = ref(false)
const rememberMe = ref(false)

// Clear error state when user modifies input
watch([email, password], () => {
	if (session.login.error) {
		session.login.error = null
	}
})

// User-friendly error message resolution
const errorMessage = computed(() => {
	const err = session.login.error
	if (!err) return ""

	// 1. Check if messages array exists and has meaningful text from backend
	if (Array.isArray(err.messages) && err.messages.length > 0) {
		const validMsgs = err.messages
			.map((m) =>
				typeof m === "string" ? m.replace(/<[^>]*>/g, "").trim() : "",
			)
			.filter((m) => {
				if (!m) return false
				const lower = m.toLowerCase()
				return (
					!lower.includes("/api/method/login") &&
					!lower.includes("authenticationerror") &&
					lower !== "internal server error"
				)
			})

		if (validMsgs.length > 0) {
			const msg = validMsgs.join(" ")
			const lower = msg.toLowerCase()
			if (
				lower.includes("invalid login credentials") ||
				lower.includes("incorrect password")
			) {
				return "Invalid email address or password. Please check your credentials and try again."
			}
			return msg
		}
	}

	// 2. Check exc_type
	const excType = err.exc_type || ""
	if (excType === "AuthenticationError" || excType === "PasswordError") {
		return "Invalid email address or password. Please check your credentials and try again."
	}
	if (excType === "ValidationError") {
		return "Please enter a valid email address and password."
	}
	if (excType === "TooManyRequestsError" || excType === "RateLimitExceeded") {
		return "Too many failed login attempts. Please wait a few minutes before trying again."
	}
	if (excType === "SecurityException" || excType === "PermissionError") {
		return "Access denied. You do not have permission to access this workspace."
	}
	if (excType === "UserDisabledError") {
		return "This user account is currently disabled. Please contact your system administrator."
	}
	if (excType === "CSRFTokenError" || excType === "InvalidCSRFToken") {
		return "Your session has expired. Please refresh the page and try again."
	}

	// 3. Check HTTP Status Code
	const status = err.status || err.response?.status
	if (status === 401) {
		return "Invalid email address or password. Please check your credentials and try again."
	}
	if (status === 403) {
		return "Access denied. Your account does not have permission to sign in."
	}
	if (status === 429) {
		return "Too many failed login attempts. Please wait a few minutes before trying again."
	}
	if (status === 502 || status === 503 || status === 504) {
		return "Server is temporarily unavailable. Please check your connection and try again."
	}

	// 4. Check raw error string / message
	const rawMsg = typeof err === "string" ? err : err.message || ""
	if (rawMsg) {
		const lower = rawMsg.toLowerCase()
		if (
			lower.includes("authenticationerror") ||
			lower.includes("invalid login credentials") ||
			lower.includes("/api/method/login")
		) {
			return "Invalid email address or password. Please check your credentials and try again."
		}
		if (
			lower.includes("failed to fetch") ||
			lower.includes("networkerror") ||
			lower.includes("network request failed")
		) {
			return "Unable to connect to the server. Please check your internet connection."
		}
		if (lower.includes("disabled") || lower.includes("inactive")) {
			return "This user account is disabled. Please contact your system administrator."
		}
		if (lower.includes("locked") || lower.includes("too many")) {
			return "Too many failed attempts. Please wait a few minutes before trying again."
		}
	}

	return "Invalid email address or password. Please check your credentials and try again."
})

function clearError() {
	if (session.login.error) {
		session.login.error = null
	}
}

// WATCH: This triggers as soon as the session.login resource succeeds
watch(
	() => session.isLoggedIn,
	async (isLoggedIn) => {
		if (isLoggedIn) {
			if (!session.userInfo.data?.roles?.length) {
				try {
					await session.userInfo.fetch()
				} catch (e) {
					console.error("Failed to fetch user info on login", e)
				}
			}
			// Logic for conditional redirect
			if (session.isTicketRaiser) {
				router.push("/tickets")
			} else {
				router.push("/dashboard")
			}
		}
	},
)

function handleSubmit() {
	const trimmedEmail = email.value.trim()
	if (!trimmedEmail || !password.value) return

	session.login.submit({
		email: trimmedEmail,
		password: password.value,
	})
}
</script>

<style scoped>
/* Smooth slide-up animation for errors */
.slide-up-enter-active, .slide-up-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-enter-from { opacity: 0; transform: translateY(10px); }
.slide-up-leave-to { opacity: 0; transform: translateY(-10px); }
</style>