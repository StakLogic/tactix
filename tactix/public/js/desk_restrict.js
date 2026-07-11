function restrictDesk() {
	try {
		if (typeof frappe !== "undefined") {
			// Check if bootstrap data or user roles are fully loaded
			const bootRoles = frappe.boot && frappe.boot.user && Array.isArray(frappe.boot.user.roles) ? frappe.boot.user.roles : null;
			const hasUserRoleFunc = frappe.user && typeof frappe.user.has_role === "function";
			
			const isSystemManager = (bootRoles && bootRoles.includes("System Manager")) ||
									(hasUserRoleFunc && frappe.user.has_role("System Manager")) ||
									(Array.isArray(frappe.user_roles) && frappe.user_roles.includes("System Manager"));

			// Only restrict if the user roles are loaded, and the user is NOT a System Manager
			const isLoaded = bootRoles || (frappe.user && frappe.user.name) || Array.isArray(frappe.user_roles);
			if (isLoaded && !isSystemManager) {
				if (window.location.pathname.startsWith("/app")) {
					window.location.href = "/tactix/?restricted=1";
				}
			}
		}
	} catch (e) {
		// Silent catch to prevent console spam before boot finishes
	}
}

document.addEventListener("DOMContentLoaded", restrictDesk)
restrictDesk();
setInterval(restrictDesk, 50);
