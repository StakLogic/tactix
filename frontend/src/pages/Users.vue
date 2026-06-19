<template>
  <div class="h-full overflow-y-auto flex items-center justify-center p-6 custom-scrollbar">
    <div class="max-w-md w-full text-center space-y-6">
      <div class="flex justify-center">
        <div class="p-4 bg-blue-50 rounded-2xl">
          <IconLayoutGrid class="w-12 h-12 text-blue-600 animate-pulse" />
        </div>
      </div>

      <div class="space-y-2">
        <h1 class="text-3xl font-bold text-slate-900 tracking-tight">
          Module Under Construction
        </h1>
        <p class="text-slate-500 leading-relaxed">
          We're currently building out this feature to help you manage your workflow more effectively. Stay tuned for advanced analytics and reporting tools.
        </p>
      </div>

      <div class="space-y-3 pt-4">
        <div class="flex justify-between text-xs font-bold text-slate-400 uppercase tracking-widest">
          <span>Development Progress</span>
          <span>65%</span>
        </div>
        <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
          <div class="bg-blue-600 h-full w-[65%] rounded-full transition-all duration-1000"></div>
        </div>
      </div>

      <div class="pt-6">
        <Button 
          variant="ghost" 
          class="!text-slate-600 hover:!bg-slate-100"
          @click="$router.back()"
        >
          <template #prefix><IconArrowLeft class="w-4 h-4" /></template>
          Go Back
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button } from "frappe-ui"
import IconArrowLeft from "~icons/lucide/arrow-left"
import IconLayoutGrid from "~icons/lucide/layout-grid"
</script>

<style scoped>
/* Optional: Add a subtle fade-in animation */
div {
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>