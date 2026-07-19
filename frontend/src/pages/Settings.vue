<template>
  <div class="h-full overflow-y-auto p-6 space-y-6 custom-scrollbar bg-slate-50/50">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-4 gap-4">
      <div class="min-w-0">
        <h1 class="text-xl font-black text-slate-900 leading-tight">Settings</h1>
        <p class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mt-1">Manage your personal preferences and system configurations</p>
      </div>
      <Button 
        variant="ghost" 
        class="!text-slate-600 hover:!bg-slate-100/50 self-start sm:self-auto shrink-0"
        @click="$router.back()"
      >
        <template #prefix><IconArrowLeft class="w-4 h-4" /></template>
        Back
      </Button>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex gap-1.5 border-b border-slate-200 pb-3 overflow-x-auto whitespace-nowrap">
      <Button 
        v-for="tab in tabs" 
        :key="tab.id"
        :variant="activeTab === tab.id ? 'subtle' : 'ghost'"
        class="!text-xs font-bold uppercase tracking-wider !px-3"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </Button>
    </div>

    <!-- Tab Contents -->
    <div class="space-y-6 animate-fade-in">
      
      <!-- Tab 1: Personal Settings -->
      <div v-if="activeTab === 'personal'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card class="!shadow-sm bg-white border border-slate-200/60 p-6 space-y-6 lg:col-span-2 flex flex-col justify-between hover:shadow-md transition-all duration-300">
          <div class="space-y-6">
            <div class="flex items-center gap-3">
              <div class="p-2.5 rounded-xl bg-blue-50 text-blue-600 border border-blue-100">
                <IconVolume2 class="w-6 h-6" />
              </div>
              <div>
                <h3 class="text-sm font-black text-slate-800 uppercase tracking-wider">Audio & Notifications</h3>
                <p class="text-xs text-slate-400 font-medium">Customize how you receive real-time alerts</p>
              </div>
            </div>

            <div class="border-t border-slate-100 pt-6 space-y-4">
              <!-- Sound Toggle -->
              <div class="flex items-center justify-between p-4 bg-slate-50/50 rounded-xl border border-slate-100">
                <div class="space-y-1 pr-4">
                  <label class="text-xs font-bold text-slate-700 block">Real-Time Sound Alerts</label>
                  <span class="text-[10px] text-slate-400 font-semibold block leading-normal max-w-md">
                    Play a notification chime when new tickets are raised or tasks are assigned to you.
                  </span>
                </div>
                <!-- Custom Toggle Switch -->
                <button
                  type="button"
                  :class="[
                    personalSettings.enableSound ? 'bg-blue-600' : 'bg-slate-200',
                    'relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none'
                  ]"
                  @click="personalSettings.enableSound = !personalSettings.enableSound; savePersonalSettings()"
                >
                  <span
                    :class="[
                      personalSettings.enableSound ? 'translate-x-4' : 'translate-x-0',
                      'pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
                    ]"
                  />
                </button>
              </div>

              <!-- Test Sound Button -->
              <div class="flex items-center justify-between p-4 bg-slate-50/50 rounded-xl border border-slate-100">
                <div class="space-y-1">
                  <label class="text-xs font-bold text-slate-700 block">Test Chime Alert</label>
                  <span class="text-[10px] text-slate-400 font-semibold block leading-normal">
                    Verify that your browser allows audio playback on this website.
                  </span>
                </div>
                <Button 
                  variant="outline"
                  class="!text-xs font-bold uppercase tracking-wider"
                  @click="triggerTestSound"
                >
                  <template #prefix><IconPlay class="w-3.5 h-3.5" /></template>
                  Play Test Sound
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </div>

      <!-- Tab 2: System Settings -->
      <div v-if="activeTab === 'system'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card class="!shadow-sm bg-white border border-slate-200/60 p-6 space-y-6 lg:col-span-2 flex flex-col justify-between hover:shadow-md transition-all duration-300">
          <div class="space-y-6">
            <div class="flex items-center gap-3">
              <div class="p-2.5 rounded-xl bg-purple-50 text-purple-600 border border-purple-100">
                <IconSettings class="w-6 h-6" />
              </div>
              <div>
                <h3 class="text-sm font-black text-slate-800 uppercase tracking-wider">System Workspace Settings</h3>
                <p class="text-xs text-slate-400 font-medium">Configure global helpdesk options and rules</p>
              </div>
            </div>

            <!-- Permission warning for non-admins -->
            <div v-if="!isAdmin" class="p-4 bg-amber-50 text-amber-800 rounded-xl border border-amber-200/60 flex items-start gap-3">
              <IconLock class="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div class="space-y-1">
                <span class="text-xs font-bold block">Administrator Mode Required</span>
                <span class="text-[10px] text-amber-700 font-semibold block leading-normal">
                  Only System Managers are authorized to modify workspace configurations. These values are displayed as read-only.
                </span>
              </div>
            </div>

            <div class="border-t border-slate-100 pt-6 space-y-5">
              <!-- Workspace branding -->
              <!-- <div class="space-y-1">
                <label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Workspace/Company Name</label>
                <input 
                  type="text" 
                  v-model="systemSettings.company_name" 
                  :disabled="!isAdmin"
                  placeholder="e.g. Tactix"
                  class="w-full px-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/25 focus:border-blue-500 hover:bg-slate-100/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                />
              </div> -->

              <!-- Default priority -->
              <div class="space-y-1">
                <label class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Default Ticket Priority</label>
                <select 
                  v-model="systemSettings.default_ticket_priority" 
                  :disabled="!isAdmin"
                  class="w-full px-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/25 focus:border-blue-500 hover:bg-slate-100/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all cursor-pointer"
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Urgent">Urgent</option>
                </select>
              </div>

              <!-- Global notification sound switch -->
              <div class="flex items-center justify-between p-4 bg-slate-50/50 rounded-xl border border-slate-100">
                <div class="space-y-1 pr-4">
                  <label class="text-xs font-bold text-slate-700 block">System-Wide Notification Chimes</label>
                  <span class="text-[10px] text-slate-400 font-semibold block leading-normal max-w-md">
                    Allow audio alerts for all system events. Disabling this turns off chimes system-wide.
                  </span>
                </div>
                <!-- Custom Toggle Switch -->
                <button
                  type="button"
                  :disabled="!isAdmin"
                  :class="[
                    systemSettings.enable_real_time_notification_sound ? 'bg-blue-600' : 'bg-slate-200',
                    !isAdmin ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
                    'relative inline-flex h-5 w-9 shrink-0 rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none'
                  ]"
                  @click="isAdmin && (systemSettings.enable_real_time_notification_sound = !systemSettings.enable_real_time_notification_sound)"
                >
                  <span
                    :class="[
                      systemSettings.enable_real_time_notification_sound ? 'translate-x-4' : 'translate-x-0',
                      'pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
                    ]"
                  />
                </button>
              </div>

              <!-- Ticket closure permission -->
              <div class="flex items-center justify-between p-4 bg-slate-50/50 rounded-xl border border-slate-100">
                <div class="space-y-1 pr-4">
                  <label class="text-xs font-bold text-slate-700 block">Allow Ticket Raisers to Close Tickets</label>
                  <span class="text-[10px] text-slate-400 font-semibold block leading-normal max-w-md">
                    Allow customers/raisers to mark their tickets as closed directly. If disabled, only support employees and managers can close tickets.
                  </span>
                </div>
                <!-- Custom Toggle Switch -->
                <button
                  type="button"
                  :disabled="!isAdmin"
                  :class="[
                    systemSettings.allow_ticket_raiser_to_close_tickets ? 'bg-blue-600' : 'bg-slate-200',
                    !isAdmin ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
                    'relative inline-flex h-5 w-9 shrink-0 rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none'
                  ]"
                  @click="isAdmin && (systemSettings.allow_ticket_raiser_to_close_tickets = !systemSettings.allow_ticket_raiser_to_close_tickets)"
                >
                  <span
                    :class="[
                      systemSettings.allow_ticket_raiser_to_close_tickets ? 'translate-x-4' : 'translate-x-0',
                      'pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
                    ]"
                  />
                </button>
              </div>
            </div>
          </div>

          <!-- Save Button (Visible only to Admins) -->
          <div v-if="isAdmin" class="border-t border-slate-100 pt-6 mt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
            <!-- Feedback -->
            <div v-if="feedback" :class="[
              'text-xs font-bold flex items-center gap-1.5 py-1.5 px-3 rounded-lg',
              feedback.type === 'success' ? 'bg-green-50 text-green-700 border border-green-100' : 'bg-red-50 text-red-700 border border-red-100'
            ]">
              <span class="w-1.5 h-1.5 rounded-full" :class="feedback.type === 'success' ? 'bg-green-500 animate-ping' : 'bg-red-500'"></span>
              {{ feedback.message }}
            </div>
            <div v-else></div>

            <Button 
              variant="solid" 
              class="w-full sm:w-auto !h-8 !px-3 font-semibold text-xs justify-center !bg-slate-800 hover:!bg-slate-900 !text-white transition-all" 
              :loading="saving"
              @click="saveSystemSettings"
            >
              Save Configuration
            </Button>
          </div>
        </Card>
      </div>

    </div>
  </div>
</template>

<script setup>
import {
  Button,
  Card,
  createResource,
} from "frappe-ui"
import { computed, reactive, ref, onMounted } from "vue"
import { session } from "@/data/session"
import { playNotificationSound } from "@/utils/audio"

// Icons
import IconArrowLeft from "~icons/lucide/arrow-left"
import IconVolume2 from "~icons/lucide/volume-2"
import IconPlay from "~icons/lucide/play"
import IconSettings from "~icons/lucide/settings"
import IconLock from "~icons/lucide/lock"

// Tabs definition
const tabs = [
  { id: "personal", label: "Personal Preferences" },
  { id: "system", label: "Workspace System Settings" }
]
const activeTab = ref("personal")

const isAdmin = computed(() => session.isAdmin)

// Personal preferences model (local storage)
const personalSettings = reactive({
  enableSound: true
})

// Load personal preferences from local storage
onMounted(() => {
  const storedSound = localStorage.getItem("tactix_personal_enable_sound")
  personalSettings.enableSound = storedSound !== "false"
})

// Save personal settings to local storage
function savePersonalSettings() {
  localStorage.setItem("tactix_personal_enable_sound", personalSettings.enableSound ? "true" : "false")
}

// Trigger a mock audio sound to test chimes
function triggerTestSound() {
  // temporarily override global and personal settings checks just to let user preview audio
  const savedPersonal = localStorage.getItem("tactix_personal_enable_sound")
  const savedGlobal = localStorage.getItem("tactix_global_enable_sound")

  localStorage.setItem("tactix_personal_enable_sound", "true")
  localStorage.setItem("tactix_global_enable_sound", "true")
  
  playNotificationSound()

  // restore state asynchronously
  setTimeout(() => {
    if (savedPersonal !== null) localStorage.setItem("tactix_personal_enable_sound", savedPersonal)
    else localStorage.removeItem("tactix_personal_enable_sound")

    if (savedGlobal !== null) localStorage.setItem("tactix_global_enable_sound", savedGlobal)
    else localStorage.removeItem("tactix_global_enable_sound")
  }, 100)
}

// System Configurations Model (saved to db)
const systemSettings = reactive({
  company_name: "",
  default_ticket_priority: "Medium",
  enable_real_time_notification_sound: true,
  allow_ticket_raiser_to_close_tickets: true
})

// Fetch backend configurations
const settingsResource = createResource({
  url: "tactix.api.generic.get_tactix_settings",
  auto: true,
  onSuccess(data) {
    if (data) {
      systemSettings.company_name = data.company_name || ""
      systemSettings.default_ticket_priority = data.default_ticket_priority || "Medium"
      systemSettings.enable_real_time_notification_sound = !!data.enable_real_time_notification_sound
      systemSettings.allow_ticket_raiser_to_close_tickets = !!data.allow_ticket_raiser_to_close_tickets
      
      // Update local storage configurations synchronously
      localStorage.setItem("tactix_global_enable_sound", systemSettings.enable_real_time_notification_sound ? "true" : "false")
      localStorage.setItem("tactix_allow_ticket_raiser_to_close_tickets", systemSettings.allow_ticket_raiser_to_close_tickets ? "1" : "0")
      localStorage.setItem("tactix_default_ticket_priority", systemSettings.default_ticket_priority)
      localStorage.setItem("tactix_company_name", systemSettings.company_name)
      
      document.title = systemSettings.company_name || "Tactix"
    }
  }
})

const saving = ref(false)
const feedback = ref(null)

// Save configurations to backend
async function saveSystemSettings() {
  saving.value = true
  feedback.value = null
  try {
    const res = await fetch(
      "/api/method/tactix.api.generic.save_tactix_settings",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_name: systemSettings.company_name,
          default_ticket_priority: systemSettings.default_ticket_priority,
          enable_real_time_notification_sound: systemSettings.enable_real_time_notification_sound ? 1 : 0,
          allow_ticket_raiser_to_close_tickets: systemSettings.allow_ticket_raiser_to_close_tickets ? 1 : 0
        })
      }
    )
    const data = await res.json()
    if (data.message?.status === "success") {
      feedback.value = {
        type: "success",
        message: "Settings saved successfully!"
      }
      settingsResource.reload()
    } else {
      feedback.value = {
        type: "error",
        message: data.message?.error || "An error occurred while saving."
      }
    }
  } catch (err) {
    feedback.value = {
      type: "error",
      message: "Network error occurred."
    }
  } finally {
    saving.value = false
    setTimeout(() => {
      feedback.value = null
    }, 5000)
  }
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.2s ease-out forwards;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
