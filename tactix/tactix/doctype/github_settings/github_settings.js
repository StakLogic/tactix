// Copyright (c) 2026, CodeVenturers and contributors
// For license information, please see license.txt

frappe.ui.form.on("Github Settings", {
	sync_prs: function(frm) {
		frappe.call({
			method: "tactix.api.github.sync_all_pull_requests",
			freeze: true,
			freeze_message: __("Synchronizing pull requests from GitHub..."),
			callback: function(r) {
				if (r.message && r.message.status === "success") {
					frappe.show_alert({
						message: __("Pull requests synchronized successfully: {0} active repos, {1} total PRs.", [r.message.repos_count, r.message.prs_count]),
						indicator: "green"
					});
				} else {
					frappe.msgprint({
						title: __("Sync Error"),
						message: r.message ? r.message.error : __("An unexpected error occurred during sync."),
						indicator: "red"
					});
				}
			}
		});
	}
});
