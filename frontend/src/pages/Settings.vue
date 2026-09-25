<template>
  <div class="h-full overflow-y-auto p-6 space-y-6 custom-scrollbar bg-slate-50/50 dark:bg-slate-950 transition-colors duration-300">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4 gap-4">
      <div class="min-w-0">
        <h1 class="text-xl font-black text-slate-900 dark:text-white leading-tight">Settings</h1>
        <p class="text-[10px] text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider mt-1">Manage user preferences, GitHub integration, and system configurations</p>
      </div>
      <Button 
        variant="ghost" 
        class="!text-slate-700 dark:!text-slate-300 hover:!bg-slate-200/60 dark:hover:!bg-slate-800/60 self-start sm:self-auto shrink-0"
        @click="$router.back()"
      >
        <template #prefix><IconArrowLeft class="w-4 h-4" /></template>
        Back
      </Button>
    </div>

    <!-- Settings Dialog / Panel Layout Container -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-xs transition-colors duration-300">
      <!-- Left Sidebar Navigation -->
      <div class="md:col-span-1 border-b md:border-b-0 md:border-r border-slate-200 dark:border-slate-800 pb-4 md:pb-0 md:pr-4 space-y-6">
        <div v-for="group in groups" :key="group.label" class="space-y-2">
          <div class="text-[10px] font-black text-slate-500 dark:text-slate-400 uppercase tracking-wider px-2">{{ group.label }}</div>
          <div class="space-y-1">
            <button
              v-for="tab in group.tabs"
              :key="tab.value"
              @click="activeTab = tab.value"
              :class="[
                'w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all text-left cursor-pointer',
                activeTab === tab.value
                  ? 'bg-blue-600 text-white shadow-md ring-2 ring-blue-500/30'
                  : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/70 hover:text-slate-900 dark:hover:text-white'
              ]"
            >
              <div class="flex items-center gap-2.5">
                <component :is="tab.iconComponent" class="w-4 h-4 shrink-0" />
                <span>{{ tab.label }}</span>
              </div>
              <div v-if="activeTab === tab.value" class="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></div>
            </button>
          </div>
        </div>
      </div>

      <!-- Right Content Panels -->
      <div class="md:col-span-3 pl-0 md:pl-2 space-y-6">
        
        <!-- Panel 1: Personal Preferences & Audio -->
        <div v-if="activeTab === 'personal'" class="space-y-6 animate-fade-in">
          <div class="flex items-center gap-3 pb-4 border-b border-slate-200 dark:border-slate-800">
            <div class="p-2.5 rounded-xl bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 border border-blue-100 dark:border-blue-900/50">
              <IconSliders class="w-5 h-5" />
            </div>
            <div>
              <h3 class="text-sm font-black text-slate-900 dark:text-slate-100 uppercase tracking-wider">Personal Preferences & Audio</h3>
              <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">Manage your personal workspace preferences and sound alerts</p>
            </div>
          </div>

          <div class="space-y-4">
            <div class="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200/80 dark:border-slate-800">
              <div class="space-y-1 pr-4">
                <label class="text-xs font-bold text-slate-900 dark:text-slate-100 block">Real-Time Sound Alerts</label>
                <p class="text-[11px] text-slate-600 dark:text-slate-400 font-medium leading-normal max-w-md">
                  Play a notification chime when new tickets are raised or tasks are assigned to you.
                </p>
              </div>
              <Switch
                v-model="personalSettings.enableSound"
                size="md"
                @change="savePersonalSettings"
              />
            </div>

            <div class="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200/80 dark:border-slate-800">
              <div class="space-y-1">
                <label class="text-xs font-bold text-slate-900 dark:text-slate-100 block">Test Chime Alert</label>
                <p class="text-[11px] text-slate-600 dark:text-slate-400 font-medium leading-normal">
                  Verify that your browser allows audio playback on this website.
                </p>
              </div>
              <Button 
                variant="outline"
                class="!text-xs font-bold uppercase tracking-wider !text-slate-700 dark:!text-slate-200 border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800"
                @click="triggerTestSound"
              >
                <template #prefix><IconPlay class="w-3.5 h-3.5" /></template>
                Play Test Sound
              </Button>
            </div>
          </div>
        </div>

        <!-- Panel 2: GitHub Integration -->
        <div v-if="activeTab === 'github'" class="space-y-6 animate-fade-in">
          <div class="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800">
            <div class="flex items-center gap-3">
              <div class="p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700">
                <IconGitBranch class="w-5 h-5" />
              </div>
              <div>
                <h3 class="text-sm font-black text-slate-900 dark:text-slate-100 uppercase tracking-wider">GitHub Integration Settings</h3>
                <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">Sync pull requests and reviewer contributions</p>
              </div>
            </div>
            <Badge 
              :theme="configResource.data?.has_token ? 'green' : 'gray'" 
              variant="subtle" 
              class="font-black text-[9px] uppercase tracking-wide px-2.5 py-0.5"
            >
              {{ configResource.data?.has_token ? 'Connected' : 'Disconnected' }}
            </Badge>
          </div>

          <div v-if="isAdmin" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-1">
                <label class="text-[10px] font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider block">Personal Access Token</label>
                <input 
                  type="password"
                  v-model="githubForm.token"
                  placeholder="••••••••••••••••••••"
                  class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/25 focus:border-blue-500 hover:bg-slate-100/50 dark:hover:bg-slate-750 transition-all"
                />
              </div>
              <div class="space-y-1">
                <label class="text-[10px] font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider block">Organization Names</label>
                <input 
                  type="text"
                  v-model="githubForm.organization_name"
                  placeholder="e.g. your-organization"
                  class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/25 focus:border-blue-500 hover:bg-slate-100/50 dark:hover:bg-slate-750 transition-all"
                />
              </div>
            </div>

            <div class="flex flex-wrap items-center gap-2 pt-2">
              <Button 
                variant="solid" 
                class="!h-8 !px-3 font-semibold text-xs flex-1 sm:flex-none justify-center !bg-slate-800 hover:!bg-slate-900 dark:!bg-blue-600 dark:hover:!bg-blue-700 !text-white transition-all"
                :loading="savingGithub"
                @click="saveGithubConfig"
              >
                Save Config
              </Button>
              <Button 
                variant="outline" 
                class="!text-slate-700 dark:!text-slate-200 !h-8 !px-3 border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 font-semibold text-xs flex-1 sm:flex-none justify-center"
                :loading="syncingGithub"
                @click="syncPRs"
              >
                <template #prefix><IconRefresh class="w-3.5 h-3.5" /></template>
                Sync PRs Now
              </Button>
            </div>

            <div v-if="githubFeedback" class="mt-1">
              <ErrorMessage v-if="githubFeedback.type === 'error'" :message="githubFeedback.message" />
              <Badge v-else-if="githubFeedback.type === 'success'" theme="green" variant="subtle" size="md">{{ githubFeedback.message }}</Badge>
            </div>
          </div>
          <div v-else class="pt-2 text-xs text-slate-500 dark:text-slate-400 italic">
            GitHub settings are configured by system administrators. Only connected state is displayed.
          </div>

          <!-- Webhook Details -->
          <div class="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800 space-y-2 text-xs">
            <div class="flex items-center gap-1.5 font-bold text-slate-800 dark:text-slate-200">
              <IconSettings class="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
              <span>Webhook Integration Details</span>
            </div>
            <p class="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
              To enable real-time pull request notifications, register this Webhook URL in your GitHub repository/organization settings under the <b class="text-slate-800 dark:text-slate-200">pull_request</b> events scope:
            </p>
            <div class="bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/60 p-2.5 rounded-xl font-mono text-[10px] text-slate-800 dark:text-slate-200 break-all select-all flex items-center justify-between gap-2">
              <span>{{ webhookUrl }}</span>
              <IconExternalLink class="w-3.5 h-3.5 text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 cursor-pointer" @click="copyWebhook" />
            </div>
          </div>
        </div>

        <!-- Panel 3: Workspace System Settings -->
        <div v-if="activeTab === 'system'" class="space-y-6 animate-fade-in">
          <div class="flex items-center gap-3 pb-4 border-b border-slate-200 dark:border-slate-800">
            <div class="p-2.5 rounded-xl bg-purple-50 dark:bg-purple-950/50 text-purple-600 dark:text-purple-400 border border-purple-100 dark:border-purple-900/50">
              <IconSettings class="w-5 h-5" />
            </div>
            <div>
              <h3 class="text-sm font-black text-slate-900 dark:text-slate-100 uppercase tracking-wider">System Workspace Settings</h3>
              <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">Configure global helpdesk options and rules</p>
            </div>
          </div>

          <div v-if="!isAdmin" class="p-4 bg-amber-50 dark:bg-amber-950/40 text-amber-900 dark:text-amber-200 rounded-xl border border-amber-200 dark:border-amber-800/60 flex items-start gap-3">
            <IconLock class="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
            <div class="space-y-1">
              <span class="text-xs font-bold block">Administrator Mode Required</span>
              <span class="text-[10px] text-amber-800 dark:text-amber-300 font-semibold block leading-normal">
                Only System Managers are authorized to modify workspace configurations. These values are displayed as read-only.
              </span>
            </div>
          </div>

          <div class="space-y-5">
            <div class="space-y-1">
              <label class="text-[10px] font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider block">Default Ticket Priority</label>
              <select 
                v-model="systemSettings.default_ticket_priority"
                :disabled="!isAdmin"
                class="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500/25 focus:border-blue-500 transition-all cursor-pointer disabled:opacity-50"
              >
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Urgent">Urgent</option>
              </select>
            </div>

            <div class="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200/80 dark:border-slate-800">
              <div class="space-y-1 pr-4">
                <label class="text-xs font-bold text-slate-900 dark:text-slate-100 block">System-Wide Notification Chimes</label>
                <p class="text-[11px] text-slate-600 dark:text-slate-400 font-medium leading-normal max-w-md">
                  Allow audio alerts for all system events. Disabling this turns off chimes system-wide.
                </p>
              </div>
              <Switch
                v-model="systemSettings.enable_real_time_notification_sound"
                :disabled="!isAdmin"
                size="md"
              />
            </div>

            <div class="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200/80 dark:border-slate-800">
              <div class="space-y-1 pr-4">
                <label class="text-xs font-bold text-slate-900 dark:text-slate-100 block">Allow Ticket Raisers to Close Tickets</label>
                <p class="text-[11px] text-slate-600 dark:text-slate-400 font-medium leading-normal max-w-md">
                  Allow customers/raisers to mark their tickets as closed directly. If disabled, only support employees and managers can close tickets.
                </p>
              </div>
              <Switch
                v-model="systemSettings.allow_ticket_raiser_to_close_tickets"
                :disabled="!isAdmin"
                size="md"
              />
            </div>
          </div>

          <div v-if="isAdmin" class="border-t border-slate-200 dark:border-slate-800 pt-6 mt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div v-if="feedback">
              <ErrorMessage v-if="feedback.type === 'error'" :message="feedback.message" />
              <Badge v-else-if="feedback.type === 'success'" theme="green" variant="subtle" size="md">{{ feedback.message }}</Badge>
            </div>
            <div v-else></div>

            <Button 
              variant="solid" 
              class="w-full sm:w-auto !h-8 !px-3 font-semibold text-xs justify-center !bg-slate-800 hover:!bg-slate-900 dark:!bg-blue-600 dark:hover:!bg-blue-700 !text-white transition-all" 
              :loading="saving"
              @click="saveSystemSettings"
            >
              Save Configuration
            </Button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { session } from "@/data/session"
import { playNotificationSound } from "@/utils/audio"
import { Badge, Button, ErrorMessage, Switch, createResource } from "frappe-ui"
import { computed, onMounted, reactive, ref, watch } from "vue"

// Icons
import IconArrowLeft from "~icons/lucide/arrow-left"
import IconExternalLink from "~icons/lucide/external-link"
import IconGitBranch from "~icons/lucide/git-branch"
import IconLock from "~icons/lucide/lock"
import IconPlay from "~icons/lucide/play"
import IconRefresh from "~icons/lucide/refresh-cw"
import IconSettings from "~icons/lucide/settings"
import IconSliders from "~icons/lucide/sliders"

// Grouped Tabs Definition
const groups = [
	{
		label: "User settings",
		tabs: [
			{
				label: "Personal Preferences",
				value: "personal",
				iconComponent: IconSliders,
			},
		],
	},
	{
		label: "Integrations & System",
		tabs: [
			{
				label: "GitHub Sync",
				value: "github",
				iconComponent: IconGitBranch,
			},
			{
				label: "Workspace System Settings",
				value: "system",
				iconComponent: IconSettings,
			},
		],
	},
]

const activeTab = ref("personal")
const isAdmin = computed(() => session.isAdmin)

// Personal preferences model (local storage)
const personalSettings = reactive({
	enableSound: true,
})

onMounted(() => {
	const storedSound = localStorage.getItem("tactix_personal_enable_sound")
	personalSettings.enableSound = storedSound !== "false"
})

function savePersonalSettings() {
	localStorage.setItem(
		"tactix_personal_enable_sound",
		personalSettings.enableSound ? "true" : "false",
	)
}

function triggerTestSound() {
	const savedPersonal = localStorage.getItem("tactix_personal_enable_sound")
	const savedGlobal = localStorage.getItem("tactix_global_enable_sound")

	localStorage.setItem("tactix_personal_enable_sound", "true")
	localStorage.setItem("tactix_global_enable_sound", "true")

	playNotificationSound()

	setTimeout(() => {
		if (savedPersonal !== null)
			localStorage.setItem("tactix_personal_enable_sound", savedPersonal)
		else localStorage.removeItem("tactix_personal_enable_sound")

		if (savedGlobal !== null)
			localStorage.setItem("tactix_global_enable_sound", savedGlobal)
		else localStorage.removeItem("tactix_global_enable_sound")
	}, 100)
}

// GitHub Settings (Moved from DataSource)
const configResource = createResource({
	url: "tactix.api.github.get_github_config",
	initialData: { has_token: false, organization_name: "" },
	auto: true,
})

const githubForm = reactive({
	token: "",
	organization_name: "",
})

watch(
	() => configResource.data,
	(data) => {
		if (data) {
			githubForm.token = data.has_token ? "******" : ""
			githubForm.organization_name = data.organization_name || ""
		}
	},
	{ immediate: true },
)

const savingGithub = ref(false)
const syncingGithub = ref(false)
const githubFeedback = ref(null)

const webhookUrl = computed(() => {
	return `${window.location.origin}/api/method/tactix.api.github.handle_webhook`
})

function copyWebhook() {
	navigator.clipboard.writeText(webhookUrl.value)
	alert("Webhook URL copied to clipboard!")
}

async function saveGithubConfig() {
	savingGithub.value = true
	githubFeedback.value = null
	try {
		const res = await fetch(
			"/api/method/tactix.api.github.save_github_config",
			{
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(githubForm),
			},
		)
		const data = await res.json()
		if (data.message?.status === "success") {
			githubFeedback.value = {
				type: "success",
				message: "Configuration saved successfully!",
			}
			configResource.reload()
		} else {
			githubFeedback.value = {
				type: "error",
				message: "Failed to save configuration.",
			}
		}
	} catch (err) {
		githubFeedback.value = {
			type: "error",
			message: "An error occurred while saving.",
		}
	} finally {
		savingGithub.value = false
	}
}

async function syncPRs() {
	syncingGithub.value = true
	githubFeedback.value = null
	try {
		const res = await fetch(
			"/api/method/tactix.api.github.sync_all_pull_requests",
			{
				method: "POST",
			},
		)
		const data = await res.json()
		if (data.message?.status === "success") {
			githubFeedback.value = {
				type: "success",
				message: "Synchronized pull requests successfully!",
			}
		} else if (data.message?.error) {
			githubFeedback.value = {
				type: "error",
				message: `Sync error: ${data.message.error}`,
			}
		} else {
			githubFeedback.value = {
				type: "success",
				message: "Sync job dispatched successfully in background!",
			}
		}
	} catch (err) {
		githubFeedback.value = {
			type: "error",
			message: "An error occurred while synchronizing.",
		}
	} finally {
		syncingGithub.value = false
	}
}

// System Configurations Model (saved to db)
const systemSettings = reactive({
	company_name: "",
	default_ticket_priority: "Medium",
	enable_real_time_notification_sound: true,
	allow_ticket_raiser_to_close_tickets: true,
})

const settingsResource = createResource({
	url: "tactix.api.generic.get_tactix_settings",
	auto: true,
	onSuccess(data) {
		if (data) {
			systemSettings.company_name = data.company_name || ""
			systemSettings.default_ticket_priority =
				data.default_ticket_priority || "Medium"
			systemSettings.enable_real_time_notification_sound =
				!!data.enable_real_time_notification_sound
			systemSettings.allow_ticket_raiser_to_close_tickets =
				!!data.allow_ticket_raiser_to_close_tickets

			localStorage.setItem(
				"tactix_global_enable_sound",
				systemSettings.enable_real_time_notification_sound ? "true" : "false",
			)
			localStorage.setItem(
				"tactix_allow_ticket_raiser_to_close_tickets",
				systemSettings.allow_ticket_raiser_to_close_tickets ? "1" : "0",
			)
			localStorage.setItem(
				"tactix_default_ticket_priority",
				systemSettings.default_ticket_priority,
			)
			localStorage.setItem("tactix_company_name", systemSettings.company_name)

			document.title = systemSettings.company_name || "Tactix"
		}
	},
})

const saving = ref(false)
const feedback = ref(null)

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
					enable_real_time_notification_sound:
						systemSettings.enable_real_time_notification_sound ? 1 : 0,
					allow_ticket_raiser_to_close_tickets:
						systemSettings.allow_ticket_raiser_to_close_tickets ? 1 : 0,
				}),
			},
		)
		const data = await res.json()
		if (data.message?.status === "success") {
			feedback.value = {
				type: "success",
				message: "Settings saved successfully!",
			}
			settingsResource.reload()
		} else {
			feedback.value = {
				type: "error",
				message: data.message?.error || "An error occurred while saving.",
			}
		}
	} catch (err) {
		feedback.value = {
			type: "error",
			message: "Network error occurred.",
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
