import os
import requests
import frappe


def get_github_settings():
	"""
	Retrieves the token and organization from the Github Settings Single DocType.
	Falls back to the environment variables / hardcoded defaults if not configured.
	"""
	token = None
	orgs = None
	
	try:
		if frappe.db.exists("DocType", "Github Settings"):
			doc = frappe.get_doc("Github Settings")
			token = doc.get_password("github_token")
			orgs = doc.organization_name
	except Exception:
		pass
		
	if not token:
		token = os.environ.get("GITHUB_TOKEN") or DEFAULT_GITHUB_TOKEN
	if not orgs:
		orgs = DEFAULT_ORG
		
	return token, orgs

@frappe.whitelist()
def sync_pull_requests_from_github(orgs=None):
	"""
	Wrapper sync function to support existing API endpoints.
	"""
	return sync_all_pull_requests()

@frappe.whitelist()
def sync_all_pull_requests():
	"""
	Comprehensive synchronizer that iterates through all repositories in the configured organization(s)
	and pages through ALL pull requests (both open and closed) to pull full contribution details.
	"""
	token, orgs = get_github_settings()
	
	org_list = [org.strip() for org in orgs.split(",") if org.strip()]
	if not org_list:
		return {"status": "error", "error": "At least one organization is required."}
		
	headers = {
		"Authorization": f"token {token}",
		"Accept": "application/vnd.github.v3+json"
	}
	
	repos_count = 0
	prs_count = 0
	processed_ids = set()
	
	try:
		for org in org_list:
			# Fetch all repositories of the organization
			repos = []
			page = 1
			while True:
				repos_url = f"https://api.github.com/orgs/{org}/repos"
				res_repos = requests.get(repos_url, headers=headers, params={"per_page": 100, "page": page}, timeout=10)
				res_repos.raise_for_status()
				items = res_repos.json()
				if not items:
					break
				repos.extend(items)
				if len(items) < 100:
					break
				page += 1
				
			repos_count += len(repos)
			
			# For each repository, fetch all pull requests
			for repo_obj in repos:
				full_name = repo_obj.get("full_name")
				pr_page = 1
				while True:
					pulls_url = f"https://api.github.com/repos/{full_name}/pulls"
					res_pulls = requests.get(pulls_url, headers=headers, params={"state": "all", "per_page": 100, "page": pr_page}, timeout=10)
					if not res_pulls.ok:
						break
					pulls = res_pulls.json()
					if not pulls:
						break
						
					for pr in pulls:
						github_id = str(pr.get("id"))
						if github_id in processed_ids:
							continue
						processed_ids.add(github_id)
						is_merged = 1 if pr.get("merged_at") else 0
						user_data = pr.get("user") or {}
						
						doc_data = {
							"doctype": "Tactix Pull Request",
							"github_id": github_id,
							"title": pr.get("title"),
							"number": pr.get("number"),
							"state": pr.get("state"),
							"is_merged": is_merged,
							"github_created_at": pr.get("created_at"),
							"html_url": pr.get("html_url"),
							"repository_url": repo_obj.get("url") or f"https://api.github.com/repos/{full_name}",
							"author_login": user_data.get("login"),
							"author_avatar_url": user_data.get("avatar_url"),
							"comments_count": pr.get("comments", 0)
						}
						
						existing_name = frappe.db.get_value("Tactix Pull Request", {"github_id": github_id}, "name")
						if existing_name:
							doc = frappe.get_doc("Tactix Pull Request", existing_name)
							doc.update(doc_data)
							doc.save(ignore_permissions=True)
						else:
							doc = frappe.get_doc(doc_data)
							doc.insert(ignore_permissions=True)
							
						prs_count += 1
						
					if len(pulls) < 100:
						break
					pr_page += 1
					
		frappe.db.commit()
		return {
			"status": "success",
			"repos_count": repos_count,
			"prs_count": prs_count
		}
	except Exception as e:
		frappe.log_error(message=str(e), title="Github Sync All Pull Requests Failure")
		return {
			"status": "error",
			"error": str(e)
		}

@frappe.whitelist()
def get_contributions(orgs=None):
	"""
	Highly optimized fetcher for repositories and pull requests across user's organizations.
	Uses cached records from the Tactix Pull Request DocType. Performs an initial sync if empty.
	"""
	if not orgs:
		_, orgs = get_github_settings()
		
	org_list = [org.strip() for org in orgs.split(",") if org.strip()]
	if not org_list:
		frappe.throw("At least one organization is required.")
		
	try:
		# If no records exist, perform initial sync from GitHub in the background to prevent loading issues
		if not frappe.db.count("Tactix Pull Request"):
			frappe.enqueue("tactix.api.github.sync_all_pull_requests", queue="long")
			
		# Query all cached PRs from the database
		db_prs = frappe.get_all(
			"Tactix Pull Request",
			fields=[
				"github_id", "title", "number", "state", "is_merged", 
				"github_created_at", "html_url", "repository_url", 
				"author_login", "author_avatar_url", "comments_count"
			],
			order_by="github_created_at desc"
		)
		
		pr_items = []
		repos_set = set()
		for db_pr in db_prs:
			repo_url = db_pr.repository_url or ""
			repo_name = ""
			if repo_url and "/repos/" in repo_url:
				repo_name = repo_url.split("/repos/")[1]
			if repo_name:
				repos_set.add(repo_name)
				
			pr_items.append({
				"id": int(db_pr.github_id) if db_pr.github_id.isdigit() else db_pr.github_id,
				"title": db_pr.title,
				"number": db_pr.number,
				"state": db_pr.state,
				"is_merged": bool(db_pr.is_merged),
				"created_at": db_pr.github_created_at,
				"html_url": db_pr.html_url,
				"repository_url": db_pr.repository_url,
				"user": {
					"login": db_pr.author_login,
					"avatar_url": db_pr.author_avatar_url or ""
				},
				"comments": db_pr.comments_count or 0
			})
			
		repos_list = [
			{
				"name": r.split("/")[1] if "/" in r else r,
				"full_name": r
			}
			for r in repos_set
		]

		# Sort final pull requests list chronologically (latest first)
		pr_items.sort(key=lambda x: x.get("created_at") or "", reverse=True)
		
		return {
			"repos": repos_list,
			"prs": pr_items
		}
		
	except Exception as e:
		frappe.log_error(message=str(e), title="Contributions Backend Exception")
		return {
			"repos": [],
			"prs": [],
			"error": f"Server error resolving contributions: {str(e)}"
		}


@frappe.whitelist()
def publish_pr_raised_notification(pr_title, repo_name, author_name, html_url, pr_number):
	"""
	Publish a real-time notification to all users who have the "Code Reviewer" or "System Manager" role.
	Always includes the current session user for easy testing.
	"""
	# 1. Fetch reviewers and managers
	reviewers = frappe.get_all("Has Role", filters={"role": "Code Reviewer", "parenttype": "User"}, fields=["parent"])
	managers = frappe.get_all("Has Role", filters={"role": "System Manager", "parenttype": "User"}, fields=["parent"])
	reviewer_users = list(set([r.parent for r in reviewers] + [m.parent for m in managers]))
	
	# 2. Append current user for test preview convenience
	if frappe.session.user and frappe.session.user not in reviewer_users:
		reviewer_users.append(frappe.session.user)
		
	# 3. Publish realtime notification and create Notification Log
	from tactix.api.generic import create_notification_log
	for user in reviewer_users:
		frappe.publish_realtime(
			event="github_pr_notification",
			message={
				"title": "New Pull Request Raised",
				"repo": repo_name,
				"author": author_name,
				"number": pr_number,
				"title_text": pr_title,
				"url": html_url
			},
			user=user
		)
		create_notification_log(
			for_user=user,
			subject=f"New PR #{pr_number} raised in {repo_name} by {author_name}",
			document_type="Pull Request",
			document_name=f"PR-{pr_number}",
			from_user="Administrator"
		)
	return {"status": "success", "notified_count": len(reviewer_users)}

@frappe.whitelist(allow_guest=True)
def handle_webhook():
	"""
	Webhook handler for GitHub events.
	Listens for 'pull_request' actions, updates the local database, and triggers realtime notifications for 'opened'.
	"""
	event = frappe.get_request_header("X-GitHub-Event")
	
	if event == "pull_request":
		try:
			data = None
			
			# Support both application/x-www-form-urlencoded and application/json
			if frappe.form_dict.get("payload"):
				data = frappe.parse_json(frappe.form_dict.get("payload"))
			elif frappe.request.data:
				raw_data = frappe.request.data
				if isinstance(raw_data, bytes):
					raw_data = raw_data.decode("utf-8")
				data = frappe.parse_json(raw_data)
				
			if not isinstance(data, dict):
				data = dict(frappe.form_dict)
				
			action = data.get("action")
			pr = data.get("pull_request", {})
			repo_dict = data.get("repository") or {}
			
			if pr:
				github_id = str(pr.get("id"))
				is_merged = 1 if pr.get("merged") else 0
				user_data = pr.get("user") or {}
				
				doc_data = {
					"doctype": "Tactix Pull Request",
					"github_id": github_id,
					"title": pr.get("title"),
					"number": pr.get("number"),
					"state": pr.get("state"),
					"is_merged": is_merged,
					"github_created_at": pr.get("created_at"),
					"html_url": pr.get("html_url"),
					"repository_url": pr.get("repository_url") or repo_dict.get("url") or pr.get("base", {}).get("repo", {}).get("url") or "",
					"author_login": user_data.get("login"),
					"author_avatar_url": user_data.get("avatar_url"),
					"comments_count": pr.get("comments", 0)
				}
				
				existing_name = frappe.db.get_value("Tactix Pull Request", {"github_id": github_id}, "name")
				if existing_name:
					doc = frappe.get_doc("Tactix Pull Request", existing_name)
					doc.update(doc_data)
					doc.save(ignore_permissions=True)
				else:
					doc = frappe.get_doc(doc_data)
					doc.insert(ignore_permissions=True)
				
				frappe.db.commit()
			
			# Trigger notifications when a new PR is opened (raised)
			if action in ["opened", "reopened"]:
				pr_title = pr.get("title", "")
				pr_number = pr.get("number", 0)
				html_url = pr.get("html_url", "")
				author = pr.get("user", {}).get("login", "Unknown")
				repo = data.get("repository", {}).get("full_name", "Unknown")
				
				publish_pr_raised_notification(
					pr_title=pr_title,
					repo_name=repo,
					author_name=author,
					html_url=html_url,
					pr_number=pr_number
				)
				return {"status": "processed", "action": action}
		except Exception as e:
			frappe.log_error(message=str(e), title="GitHub Webhook Parsing Error")
			
	return {"status": "ignored"}

@frappe.whitelist()
def simulate_pr_raised():
	"""
	Triggers a mock PR raised notification to all reviewers and the current session user.
	"""
	return publish_pr_raised_notification(
		pr_title="feat: support oauth2 authentication mechanisms for integrations",
		repo_name="Teciza-Solutions/tactix",
		author_name="octocat",
		html_url="https://github.com/Teciza-Solutions/tactix/pull/415",
		pr_number=415
	)

@frappe.whitelist()
def get_github_config():
	"""Get masked token and organization name for UI."""
	roles = frappe.get_roles(frappe.session.user)
	if "System Manager" not in roles:
		frappe.throw(_("Not authorized to load GitHub settings."))
		
	doc = frappe.get_doc("Github Settings")
	token = doc.get_password("github_token")
	
	return {
		"has_token": bool(token),
		"organization_name": doc.organization_name or "Teciza-Solutions"
	}

@frappe.whitelist()
def save_github_config(token=None, organization_name=None):
	"""Save token and organization name from UI."""
	roles = frappe.get_roles(frappe.session.user)
	if "System Manager" not in roles:
		frappe.throw(_("Not authorized to configure GitHub settings."))
		
	doc = frappe.get_doc("Github Settings")
	if token and token != "******":
		doc.github_token = token
	if organization_name:
		doc.organization_name = organization_name
	doc.save()
	frappe.db.commit()
	return {"status": "success"}
