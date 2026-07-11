function initMobileMenu() {
	if (document.querySelector(".mobile-menu-toggle")) return

	function findSidebar() {
		return (
			document.querySelector(".h-screen.flex.bg-slate-50") ||
			document.querySelector('[class*="bg-slate-50"][class*="border-r"]')
		)
	}

	var sidebar = findSidebar()
	if (!sidebar) {
		setTimeout(initMobileMenu, 500)
		return
	}

	var btn = document.createElement("button")
	btn.className = "mobile-menu-toggle"
	btn.setAttribute("aria-label", "Menu")
	btn.innerHTML =
		'<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="4" y1="6" x2="20" y2="6"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg>'
	document.body.appendChild(btn)

	var backdrop = document.createElement("div")
	backdrop.className = "mobile-backdrop"
	document.body.appendChild(backdrop)

	var menuLabels = {
		"/dashboard": "Dashboard",
		"/tasks": "Tasks",
		"/tickets": "Tickets",
		"/timesheets": "Timesheets",
		"/performance": "Performance",
		"/data-sources": "Data Sources",
		"/users": "Users",
		"/settings": "Settings",
	}

	function fixSidebarLabels() {
		sidebar = findSidebar()
		if (!sidebar) return

		var innerElements = sidebar.querySelectorAll(
			'aside, nav, [class*="sidebar"], > div',
		)
		innerElements.forEach((el) => {
			el.style.setProperty("width", "260px", "important")
			el.style.setProperty("min-width", "260px", "important")
			el.style.setProperty("max-width", "260px", "important")
		})

		var currentPath = location.pathname
			.replace(/\/tactix/g, "")
			.replace(/^\/+/, "/")

		var links = sidebar.querySelectorAll("a[href]")
		links.forEach((link) => {
			var href = link.getAttribute("href")
			var cleanHref = href.replace("/tactix", "").split("?")[0]
			if (menuLabels[cleanHref]) {
				var span = link.querySelector("span.mobile-injected-label")
				if (!span) {
					span = document.createElement("span")
					span.className = "mobile-injected-label"
					span.textContent = menuLabels[cleanHref]
					span.style.marginLeft = "12px"
					span.style.fontSize = "14px"
					span.style.fontWeight = "500"
					span.style.display = "inline"
					link.appendChild(span)
				} else {
					span.style.display = "inline"
				}
				link.style.justifyContent = "flex-start"
				link.style.paddingLeft = "16px"
				link.style.paddingRight = "16px"

				var isActive =
					currentPath === cleanHref ||
					(currentPath.indexOf(cleanHref) === 0 && cleanHref !== "/")
				if (isActive) {
					link.style.setProperty("background-color", "#0f172a", "important")
					link.style.setProperty("color", "white", "important")
					link.style.setProperty("font-weight", "700", "important")
					link.style.setProperty(
						"box-shadow",
						"0 4px 6px -1px rgb(0 0 0 / 0.1)",
						"important",
					)
					link.style.setProperty("border-radius", "12px", "important")
					if (span) span.style.setProperty("color", "white", "important")
					var svg = link.querySelector("svg")
					if (svg) svg.style.setProperty("color", "white", "important")
				} else {
					link.style.removeProperty("background-color")
					link.style.removeProperty("box-shadow")
					link.style.setProperty("color", "", "")
					link.style.setProperty("font-weight", "500", "")
					if (span) span.style.setProperty("color", "", "")
					var svg = link.querySelector("svg")
					if (svg) svg.style.removeProperty("color")
				}
			}
		})

		var headerBtn = sidebar.querySelector(
			"header button, .sidebar-header button",
		)
		if (headerBtn) {
			headerBtn.style.setProperty("width", "100%", "important")
			headerBtn.style.setProperty("display", "flex", "important")
			headerBtn.style.setProperty(
				"justify-content",
				"space-between",
				"important",
			)
		}

		var collapseBtn = sidebar.querySelector(
			'[class*="collapse"], [class*="Collapse"]',
		)
		if (
			collapseBtn &&
			(collapseBtn.tagName === "BUTTON" ||
				collapseBtn.getAttribute("role") === "button")
		) {
			collapseBtn.style.setProperty("display", "none", "important")
		}
	}

	function openMenu() {
		sidebar = findSidebar()
		if (!sidebar) return
		sidebar.classList.add("mobile-sidebar-open")
		backdrop.classList.add("mobile-backdrop-open")
		document.body.style.overflow = "hidden"
		setTimeout(fixSidebarLabels, 50)
		setTimeout(fixSidebarLabels, 200)
	}

	function closeMenu() {
		sidebar = findSidebar()
		if (!sidebar) return
		sidebar.classList.remove("mobile-sidebar-open")
		backdrop.classList.remove("mobile-backdrop-open")
		document.body.style.overflow = ""
	}

	btn.addEventListener("click", (e) => {
		e.preventDefault()
		e.stopPropagation()
		sidebar = findSidebar()
		if (!sidebar) return
		if (sidebar.classList.contains("mobile-sidebar-open")) {
			closeMenu()
		} else {
			openMenu()
		}
	})

	backdrop.addEventListener("click", closeMenu)
	backdrop.addEventListener("touchend", (e) => {
		e.preventDefault()
		closeMenu()
	})

	function updatePageTitle() {
		if (window.innerWidth > 767) return
		var header = document.querySelector("header.h-14 .relative.w-72")
		if (!header) return
		var path = location.pathname.replace(/\/tactix/g, "").replace(/^\/+/, "/")
		var title = menuLabels[path] || ""
		if (!title) {
			for (var key in menuLabels) {
				if (path.indexOf(key) === 0) {
					title = menuLabels[key]
					break
				}
			}
		}
		if (!title) title = "Tactix"
		var span = header.querySelector(".mobile-page-title")
		if (!span) {
			span = document.createElement("span")
			span.className = "mobile-page-title"
			span.style.fontSize = "15px"
			span.style.fontWeight = "700"
			span.style.color = "#1e293b"
			span.style.letterSpacing = "-0.01em"
			header.appendChild(span)
		}
		span.textContent = title
	}

	document.addEventListener(
		"click",
		(e) => {
			sidebar = findSidebar()
			if (!sidebar) return
			if (!sidebar.classList.contains("mobile-sidebar-open")) return

			var target = e.target
			if (target.closest("header") || target.closest(".sidebar-header")) {
				return
			}

			var link =
				target.closest("a") ||
				target.closest(".frappe-sidebar-item") ||
				target.closest("li > div")

			if (link && sidebar.contains(link)) {
				setTimeout(closeMenu, 150)
			}
		},
		true,
	)

	var lastUrl = location.href
	setInterval(() => {
		if (location.href !== lastUrl) {
			lastUrl = location.href
			closeMenu()
			updatePageTitle()
		}
	}, 200)

	updatePageTitle()

	function handleResize() {
		if (window.innerWidth > 767) {
			btn.style.display = "none"
			backdrop.style.display = "none"
			sidebar = findSidebar()
			if (sidebar) {
				sidebar.classList.remove("mobile-sidebar-open")
				var injected = sidebar.querySelectorAll(".mobile-injected-label")
				injected.forEach((el) => {
					el.style.display = "none"
				})
			}
			document.body.style.overflow = ""
			var pageTitle = document.querySelector(".mobile-page-title")
			if (pageTitle) pageTitle.style.display = "none"
		} else {
			btn.style.display = ""
			backdrop.style.display = ""
			var injected = document.querySelectorAll(".mobile-injected-label")
			injected.forEach((el) => {
				el.style.display = "inline"
			})
			var pageTitle = document.querySelector(".mobile-page-title")
			if (pageTitle) pageTitle.style.display = "inline"
		}
	}

	window.addEventListener("resize", handleResize)
	handleResize()
}

if (document.readyState === "loading") {
	document.addEventListener("DOMContentLoaded", () => {
		setTimeout(initMobileMenu, 800)
	})
} else {
	setTimeout(initMobileMenu, 800)
}
