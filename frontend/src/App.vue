<template>
  <div>
    <!-- Restricted Access Alert Banner -->
    <div v-if="showRestrictedAlert" class="fixed top-4 right-4 z-[9999] max-w-md w-full bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-4 flex gap-3 items-start animate-slide-in">
      <div class="p-1.5 bg-red-500/10 border border-red-500/20 rounded-lg text-red-500 flex-shrink-0">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
          <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
        </svg>
      </div>
      <div class="flex-grow">
        <h4 class="text-sm font-bold text-white mb-0.5">Access Restricted</h4>
        <p class="text-xs text-slate-400 leading-relaxed">Your account does not have permission to view the administrative desk.</p>
      </div>
      <button @click="showRestrictedAlert = false" class="text-slate-500 hover:text-slate-300 transition-colors p-0.5 rounded">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
    
    <router-view />
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue"

const showRestrictedAlert = ref(false)

onMounted(() => {
	const urlParams = new URLSearchParams(window.location.search)
	if (urlParams.has("restricted")) {
		showRestrictedAlert.value = true

		// Clean up url parameters so restricted=1 is hidden
		const newUrl = window.location.pathname
		window.history.replaceState({}, document.title, newUrl)

		// Auto hide after 6 seconds
		setTimeout(() => {
			showRestrictedAlert.value = false
		}, 6000)
	}
})
</script>

<style>
@keyframes slideIn {
  from {
    transform: translateY(-1rem);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
.animate-slide-in {
  animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>
