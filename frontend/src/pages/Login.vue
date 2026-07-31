<template>
  <div class="min-h-screen flex items-center justify-center bg-[#f8fafc] relative overflow-hidden p-6">
	<div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-100/50 rounded-full blur-[120px]"></div>
	<div class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-100/50 rounded-full blur-[120px]"></div>

	<div class="w-full max-w-[440px] relative z-10">
	  <div class="flex flex-col items-center mb-10 text-center">
		<div class="group relative mb-6">
		  <div class="absolute inset-0 bg-blue-600 blur-2xl opacity-20 group-hover:opacity-40 transition-opacity duration-500"></div>
		  <div class="relative bg-white p-4 rounded-[1.5rem] shadow-2xl shadow-blue-100 border border-white transition-transform duration-500 hover:scale-105">
			<img 
			  :src="'/assets/tactix/frontend/tactix_icon.png'"
			  alt="Tactix Logo" 
			  class="h-12 w-12 object-contain"
			/>
		  </div>
		</div>
		
		<h1 class="text-4xl font-black text-slate-900 tracking-tight mb-2">Tactix</h1>
		<div class="flex items-center gap-3">
			<div class="h-px w-6 bg-slate-200"></div>
			<p class="text-blue-600 font-bold text-[10px] uppercase tracking-[0.4em]">Operations and Management</p>
			<div class="h-px w-6 bg-slate-200"></div>
		</div>
	  </div>

	  <div class="bg-white/80 backdrop-blur-xl rounded-[2.5rem] shadow-[0_32px_64px_-16px_rgba(0,0,0,0.1)] border border-white p-2">
		<div class="bg-white rounded-[2.2rem] p-8 md:p-10">
		  <form class="space-y-6" @submit.prevent="handleSubmit">
			
			<div class="space-y-2">
			  <label class="text-[11px] font-bold text-slate-400 uppercase tracking-widest ml-1">Email</label>
			  <div class="relative group">
				<Input
				  name="email"
				  type="text"
				  placeholder="name@company.com"
				  v-model="email"
				  class="!bg-slate-50/50 !border-slate-100 !h-12 focus:!bg-white focus:!border-blue-500 transition-all duration-300"
				  required
				>
				  <template #prefix>
					<div class="pl-4">
					  <IconMail class="w-4 h-4 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
					</div>
				  </template>
				</Input>
			  </div>
			</div>

			<div class="space-y-2">
			  <div class="flex justify-between items-center px-1">
				<label class="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Password</label>
				<a href="#" class="text-[11px] font-bold text-blue-600 hover:underline decoration-2 underline-offset-4">Forgot?</a>
			  </div>
			  <div class="relative group">
				<Input
				  name="password"
				  :type="showPassword ? 'text' : 'password'"
				  placeholder="••••••••"
				  v-model="password"
				  class="!bg-slate-50/50 !border-slate-100 !h-12 focus:!bg-white focus:!border-blue-500 transition-all duration-300"
				  required
				>
				  <template #prefix>
					<div class="pl-4">
					  <IconLock class="w-4 h-4 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
					</div>
				  </template>
				</Input>
				<button 
				  type="button"
				  @click="showPassword = !showPassword"
				  class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-300 hover:text-slate-600 transition-colors z-20"
				>
				  <IconEye v-if="!showPassword" class="w-4 h-4" />
				  <IconEyeOff v-else class="w-4 h-4" />
				</button>
			  </div>
			</div>

			<Transition name="slide-up">
			  <ErrorMessage 
			    v-if="session.login.error" 
			    :message="session.login.error.message || 'Access denied. Please check credentials.'" 
			    class="p-4 bg-red-50 text-red-600 text-xs rounded-2xl border border-red-100 font-medium" 
			  />
			</Transition>

			<Button 
			  :loading="session.login.loading" 
			  variant="solid" 
			  type="submit"
			  class="w-full !h-14 !bg-slate-900 hover:!bg-blue-600 !text-white !rounded-2xl !text-[15px] font-bold transition-all duration-500 shadow-xl shadow-slate-200 hover:shadow-blue-200 hover:-translate-y-0.5"
			>
			  <div class="flex items-center justify-center gap-2">
				Sign into Workspace
				<IconChevronRight class="w-4 h-4" />
			  </div>
			</Button>
		  </form>
		</div>
	  </div>

	  <p class="text-center mt-8 text-slate-400 text-xs font-medium tracking-wide">
		&copy; 2026 Tactix Inc. &bull; Operations & Management
	  </p>
	</div>
  </div>
</template>

<script setup>
import { Button, ErrorMessage } from "frappe-ui"
import { ref, watch } from "vue" // Added watch
import { useRouter } from "vue-router" // Added router
import { session } from "../data/session"

import IconAlertCircle from "~icons/lucide/alert-circle"
import IconChevronRight from "~icons/lucide/chevron-right"
import IconEye from "~icons/lucide/eye"
import IconEyeOff from "~icons/lucide/eye-off"
import IconLock from "~icons/lucide/lock"
// Lucide Imports via unplugin-icons
import IconMail from "~icons/lucide/mail"

const router = useRouter()
const email = ref("")
const password = ref("")
const showPassword = ref(false)

// WATCH: This triggers as soon as the session.login resource succeeds
watch(
	() => session.isLoggedIn,
	(isLoggedIn) => {
		if (isLoggedIn) {
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
	session.login.submit({
		email: email.value,
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