import os
import json
import datetime
import re
from utils.logger import get_logger

logger = get_logger(__name__)

STATE_FILE = os.path.join(os.path.dirname(__file__), "memory", "project_state.json")

PROJECT_REQUIREMENTS_MAP = {
    "SaaS": ["purpose", "audience", "style", "features", "mobile-first", "authentication", "admin_panel"],
    "E-commerce": ["purpose", "audience", "style", "features", "mobile-first", "authentication", "admin_panel"],
    "Portfolio": ["purpose", "audience", "style", "features", "mobile-first", "authentication", "admin_panel"],
    "Custom": ["purpose", "audience", "style", "features", "mobile-first", "authentication", "admin_panel"],
    "Website": ["purpose", "audience", "style", "features", "mobile-first", "authentication", "admin_panel"],
    "App": ["platform", "users", "core_features", "integrations"],
    "Mobile App": ["platform", "users", "core_features", "integrations"],
    "Dashboard": ["data_source", "user_roles", "analytics_needs"],
    "AI Product": ["platform", "user type", "integrations", "primary workflows"],
}

REQUIREMENT_QUESTIONS = {
    "purpose": "What is the primary purpose of this website?",
    "audience": "Who is the target audience for this?",
    "style": "What design style or aesthetic do you prefer? (e.g. minimalist, dark/sleek, colorful)",
    "features": "What are the key features or core pages needed?",
    "mobile-first": "Should this be designed mobile-first or desktop-focused?",
    "authentication": "Do we need user authentication or logins?",
    "admin_panel": "Are there any admin panel or management requirements?",
    "platform": "What platform are we targeting? (e.g. iOS, Android, cross-platform, or Web?)",
    "users": "Who are the primary users of the application?",
    "core_features": "What is the key functionality or core feature set of the app?",
    "integrations": "What external APIs or integrations are required?",
    "data_source": "What data sources or APIs will feed this dashboard?",
    "user_roles": "Who will be using this dashboard and what are their roles?",
    "analytics_needs": "What key metrics or reporting needs do you have?",
    # Legacy fallbacks
    "design style": "What design style or aesthetic do you prefer? (e.g. minimalist, dark/sleek, colorful)",
    "key features": "What are the key features or core pages needed?",
    "admin needs": "Are there any admin panel or management requirements?",
    "mobile-first requirements": "Should this be designed mobile-first or desktop-focused?",
    "data sources": "What data sources or APIs will feed this dashboard?",
    "reporting needs": "What are the key metrics or reporting needs?",
    "permissions": "Do you need role-based access control or specific permissions?",
    "user type": "Who is the target user for this AI product?",
    "primary workflows": "What are the primary workflows or user actions?"
}

FOCUS_LABELS = {
    "purpose": "Purpose",
    "audience": "Audience",
    "style": "Style",
    "features": "Features",
    "mobile-first": "Mobile-first",
    "authentication": "Authentication",
    "admin_panel": "Admin panel",
    "platform": "Platform",
    "users": "Users",
    "core_features": "Core features",
    "integrations": "Integrations",
    "data_source": "Data source",
    "user_roles": "Users",
    "analytics_needs": "Analytics needs",
    # Legacy fallbacks
    "design style": "Design style",
    "key features": "Key features",
    "admin needs": "Admin needs",
    "mobile-first requirements": "Mobile-first requirements",
    "data sources": "Data sources",
    "reporting needs": "Reporting needs",
    "permissions": "Permissions",
    "user type": "User type",
    "primary workflows": "Primary workflows"
}

class ProjectModeManager:
    def __init__(self):
        self.state = self._load_state()

    def _load_state(self):
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading project state: {e}")
        return {"projects": {}, "active_project_name": None}

    def _save_state(self):
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving project state: {e}")

    def get_active_project(self):
        name = self.state.get("active_project_name")
        if name and name in self.state["projects"]:
            proj = self.state["projects"][name]
            if proj.get("project_active"):
                return proj
        return None

    def start_project(self, project_type=None, project_name=None):
        # 1. Pause currently active project
        active = self.get_active_project()
        if active:
            active["project_active"] = False
            active["project_status"] = "paused"
            logger.info(f"[ProjectMode] Paused project: {active['project_name']}")

        # 2. Setup name
        if not project_name:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            project_name = f"Project_{timestamp}"

        # 3. Create new project entry
        new_proj = {
            "project_active": True,
            "project_name": project_name,
            "project_type": project_type,
            "requirements_collected": {},
            "project_summary": None,
            "last_project_timestamp": datetime.datetime.now().isoformat(),
            "project_status": "active",
            "stage": "DISCOVERY" if not project_type else "REQUIREMENTS",
            "next_requirement_index": 0,
            "future_prompt_package": None
        }

        self.state["projects"][project_name] = new_proj
        self.state["active_project_name"] = project_name
        self._save_state()

        logger.info("[ProjectMode] Started")

        if not project_type:
            return (
                "Alright, boss.\n\n"
                "Opening Project Mode.\n\n"
                "Let's structure it properly.\n\n"
                "What are we building?\n\n"
                "* SaaS\n"
                "* E-commerce\n"
                "* Portfolio\n"
                "* Dashboard\n"
                "* AI Product\n"
                "* Custom"
            )
        else:
            req_list = PROJECT_REQUIREMENTS_MAP.get(project_type, [])
            first_req = req_list[0]
            question = REQUIREMENT_QUESTIONS.get(first_req, f"What is the {first_req}?")
            return (
                "Alright, boss.\n\n"
                "Opening Project Mode.\n\n"
                "Let's structure it properly.\n\n"
                f"{question}"
            )

    def restore_project(self, phrase):
        target_name = None
        cleaned = phrase.lower()

        # Try to find by type mentioned in the phrase
        matched_type = None
        if "dashboard" in cleaned:
            matched_type = "Dashboard"
        elif "saas" in cleaned:
            matched_type = "SaaS"
        elif "e-commerce" in cleaned or "ecommerce" in cleaned:
            matched_type = "E-commerce"
        elif "portfolio" in cleaned:
            matched_type = "Portfolio"
        elif "website" in cleaned:
            matched_type = "Website"
        elif "ai" in cleaned or "assistant" in cleaned or "agent" in cleaned:
            matched_type = "AI Product"
        elif "app" in cleaned:
            matched_type = "App"

        # Search projects
        projects = self.state["projects"]
        if matched_type:
            # Try to find project of matched type
            for name, proj in projects.items():
                p_type = proj.get("project_type", "")
                if p_type == matched_type or (matched_type == "App" and p_type in ["App", "Mobile App"]):
                    target_name = name
                    break

        if not target_name and projects:
            # Fallback to the last active / updated project
            sorted_projects = sorted(
                projects.items(),
                key=lambda x: x[1].get("last_project_timestamp", ""),
                reverse=True
            )
            target_name = sorted_projects[0][0]

        if not target_name:
            return "No projects found to restore, boss."

        # Pause current
        active = self.get_active_project()
        if active and active["project_name"] != target_name:
            active["project_active"] = False
            active["project_status"] = "paused"

        # Activate target
        proj = projects[target_name]
        proj["project_active"] = True
        proj["project_status"] = "active"
        proj["last_project_timestamp"] = datetime.datetime.now().isoformat()
        self.state["active_project_name"] = target_name
        self._save_state()

        logger.info("[ProjectMode] Project restored")

        # Create concise restoration message
        p_type = proj.get("project_type") or "Custom"
        req_list = PROJECT_REQUIREMENTS_MAP.get(p_type, [])
        collected = proj.get("requirements_collected", {})
        remaining = [r for r in req_list if r not in collected]

        focus_bullets = ""
        for r in remaining:
            label = FOCUS_LABELS.get(r, r.capitalize())
            focus_bullets += f"\n* {label}"

        if not focus_bullets:
            focus_bullets = "\n* Project completed/planned."

        return (
            "Project restored, boss.\n"
            f"{p_type} project active.\n"
            f"Current focus:{focus_bullets}"
        )

    def exit_project_mode(self):
        active = self.get_active_project()
        if active:
            active["project_active"] = False
            active["project_status"] = "paused"
            active["last_project_timestamp"] = datetime.datetime.now().isoformat()
            self._save_state()
            logger.info("[ProjectMode] Exited")
            return "Alright, boss. Exiting project mode."
        return "Not in project mode, boss."

    def process_message(self, user_input):
        active = self.get_active_project()
        if not active:
            return "No active project session."

        cleaned = user_input.lower().strip()

        # Handle explicit exit commands
        exit_phrases = ["exit project mode", "cancel project", "stop building", "nevermind"]
        if any(p in cleaned for p in exit_phrases):
            return self.exit_project_mode()

        # Handle explicit status/summary commands
        if cleaned == "show summary" or cleaned == "project summary":
            if self._check_minimum_threshold(active):
                summary_text = self._generate_summary(active)
                active["project_summary"] = summary_text
                active["future_prompt_package"] = self._prepare_antigravity_package(active)
                self._save_state()
                return summary_text
            else:
                return "Not enough requirements gathered yet to generate a project summary, boss."

        if cleaned == "project status":
            p_name = active.get("project_name", "New Project")
            p_type = active.get("project_type") or "Discovery"
            status = active.get("project_status", "active")
            stage = active.get("stage", "DISCOVERY")
            return f"Project: {p_name}\nType: {p_type}\nStatus: {status}\nStage: {stage}"

        if "phase" in cleaned:
            return f"Current Phase: {active['stage']}"

        if cleaned == "whats next" or cleaned == "what's next":
            p_type = active["project_type"]
            if active["stage"] == "DISCOVERY":
                return "Select what we are building: SaaS, E-commerce, Portfolio, Dashboard, AI Product, Custom."
            req_list = PROJECT_REQUIREMENTS_MAP.get(p_type, [])
            idx = active.get("next_requirement_index", 0)
            if idx < len(req_list):
                return f"Next requirement: {req_list[idx]}"
            return "All requirements collected."

        # Stage: DISCOVERY
        if active["stage"] == "DISCOVERY":
            selected_type = None
            valid_types = ["SaaS", "E-commerce", "Portfolio", "Dashboard", "AI Product", "Custom", "Website", "App"]
            for vt in valid_types:
                if vt.lower() in cleaned:
                    selected_type = vt
                    break
            
            if not selected_type:
                return "Please select from the options: SaaS, E-commerce, Portfolio, Dashboard, AI Product, or Custom."

            # Normalize Website/App for internal mapping if selected in discovery
            if selected_type == "Website":
                selected_type = "Custom"
            elif selected_type == "App":
                selected_type = "Mobile App"

            active["project_type"] = selected_type
            active["stage"] = "REQUIREMENTS"
            active["next_requirement_index"] = 0
            active["last_project_timestamp"] = datetime.datetime.now().isoformat()
            self._save_state()

            req_list = PROJECT_REQUIREMENTS_MAP.get(selected_type, [])
            first_req = req_list[0]
            question = REQUIREMENT_QUESTIONS.get(first_req, f"What is the {first_req}?")
            return f"Got it, boss. Let's structure this as a {selected_type}.\n\n{question}"

        # Stage: REQUIREMENTS
        elif active["stage"] == "REQUIREMENTS":
            p_type = active["project_type"]
            req_list = PROJECT_REQUIREMENTS_MAP.get(p_type, [])
            idx = active.get("next_requirement_index", 0)

            if idx < len(req_list):
                current_req_key = req_list[idx]
                active["requirements_collected"][current_req_key] = user_input.strip()
                logger.info("[ProjectMode] Requirement captured")
                idx += 1
                active["next_requirement_index"] = idx
                active["last_project_timestamp"] = datetime.datetime.now().isoformat()
                self._save_state()

            if idx < len(req_list):
                next_req_key = req_list[idx]
                question = REQUIREMENT_QUESTIONS.get(next_req_key, f"What is the {next_req_key}?")
                return question
            else:
                active["stage"] = "COMPLETED"
                active["project_status"] = "completed"
                summary_text = self._generate_summary(active)
                active["project_summary"] = summary_text
                active["future_prompt_package"] = self._prepare_antigravity_package(active)
                self._save_state()
                
                logger.info("[ProjectMode] Summary generated")
                return summary_text

        return "Alright, boss. Let me know if you want to show summary or exit project mode."

    def _check_minimum_threshold(self, proj) -> bool:
        p_type = proj.get("project_type")
        collected = proj.get("requirements_collected", {})
        if p_type in ["SaaS", "E-commerce", "Portfolio", "Custom", "Website"]:
            has_purpose = "purpose" in collected
            has_audience = "audience" in collected
            has_features = "features" in collected or "key features" in collected or "key_features" in collected
            return has_purpose and has_audience and has_features
        elif p_type == "Dashboard":
            has_datasource = "data_source" in collected or "data sources" in collected
            has_users = "user_roles" in collected or "users" in collected
            has_metrics = "analytics_needs" in collected or "reporting needs" in collected
            return has_datasource and has_users and has_metrics
        elif p_type in ["AI Product", "AI Assistant"]:
            has_platform = "platform" in collected
            has_users = "user type" in collected or "users" in collected
            has_workflows = "primary workflows" in collected or "core_features" in collected or "features" in collected
            return has_platform and has_users and has_workflows
        elif p_type in ["App", "Mobile App"]:
            has_platform = "platform" in collected
            has_users = "users" in collected
            has_features = "core_features" in collected or "features" in collected
            return has_platform and has_users and has_features
        return False

    def _generate_summary(self, proj) -> str:
        p_name = proj.get("project_name", "New Project")
        p_type = proj.get("project_type", "Custom")
        collected = proj.get("requirements_collected", {})

        goal = collected.get("purpose") or collected.get("data_source") or collected.get("data sources") or collected.get("platform") or "Not specified"
        users = collected.get("audience") or collected.get("users") or collected.get("user_roles") or collected.get("user type") or "Not specified"
        features = (collected.get("features") or collected.get("key_features") or collected.get("key features") or 
                    collected.get("core_features") or collected.get("analytics_needs") or collected.get("reporting needs") or 
                    collected.get("primary workflows") or "Not specified")

        if p_type in ["SaaS", "E-commerce", "Portfolio", "Custom", "Website"]:
            arch = "SPA with Next.js/React frontend and a lightweight API backend."
            build_notes = "Use TailwindCSS for styling and HSL-tailored colors. Ensure clean directory organization and mobile-first responsive layout."
        elif p_type == "Dashboard":
            arch = "Modular component-based dashboard using React/Vite, tracking real-time status and charts."
            build_notes = "Utilize recharts or Chart.js for data visualization. Implement role-based permission routing in state."
        else:
            arch = "Modular component/agent architecture tailored to target platform."
            build_notes = "Establish clean separation of features. Implement robust error boundaries and clean logging."

        summary = (
            f"=== PROJECT SUMMARY: {p_name} ===\n\n"
            f"* **Project Goal**: {goal}\n"
            f"* **Users**: {users}\n"
            f"* **Features**: {features}\n"
            f"* **Suggested Architecture**: {arch}\n"
            f"* **Build Notes**: {build_notes}\n"
        )
        return summary

    def _prepare_antigravity_package(self, proj) -> dict:
        p_type = proj.get("project_type", "Custom")
        collected = proj.get("requirements_collected", {})
        
        if p_type in ["SaaS", "E-commerce", "Portfolio", "Custom", "Website"]:
            arch = "SPA Next.js/React frontend, lightweight API backend."
            build_instructions = "Initialize Next.js app, configure styling templates, and build core layout components."
        elif p_type == "Dashboard":
            arch = "React/Vite dashboard client."
            build_instructions = "Set up Vite dashboard structure, configure data polling/fetching utilities, and build visualization cards."
        else:
            arch = "Modular architecture matching project requirements."
            build_instructions = "Set up codebase structure, implement core logic loop, and add unit tests."

        package = {
            "requirements": collected,
            "architecture": arch,
            "build_instructions": build_instructions,
            "implementation_notes": proj.get("project_summary", "Phase 7.1 established project awareness.")
        }
        return package
