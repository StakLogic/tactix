function restrictDesk() {

	if (typeof frappe !== "undefined" && !frappe.user.has_role("System Manager")) {

		if (window.location.pathname.startsWith("/app")) {
			window.location.href = "/tactix"
		}

	}

}

document.addEventListener("DOMContentLoaded", restrictDesk)
setInterval(restrictDesk, 100)
