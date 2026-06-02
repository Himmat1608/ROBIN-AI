import re
from core.project_session import ProjectSession
from core.project_detector import ProjectDetector
from core.brain import get_ai_response
from utils.logger import get_logger

logger = get_logger(__name__)

# Questions per project category
PROJECT_QUESTIONS = {
    "Website": [
        ("audience", "Who is the target audience for this website?"),
        ("style", "What kind of design style or aesthetic do you have in mind? (e.g. clean/minimalist, dark/sleek, colorful/playful)"),
        ("features", "What core features or pages do you need? (e.g. landing page, blog, auth, dashboard)")
    ],
    "Mobile App": [
        ("platform", "Which platform are we targeting? iOS, Android, or cross-platform?"),
        ("users", "Who are the primary users of the application?"),
        ("functionality", "What is the key functionality or core feature set of the app?")
    ],
    "AI Assistant": [
        ("objective", "What is the primary objective of this AI assistant?"),
        ("capabilities", "What capabilities or tools should the assistant have? (e.g. web search, file reading, API access)"),
        ("deployment target", "Where do you plan to deploy or host this assistant?")
    ],
    "Dashboard": [
        ("data_sources", "What data sources or APIs will feed this dashboard?"),
        ("key_metrics", "What key metrics or charts should be displayed?"),
        ("features", "Do you need user authentication, exports, or admin settings?")
    ],
    "Game": [
        ("genre", "What is the genre or type of game? (e.g., arcade, puzzle, platformer)"),
        ("platform", "What platform is the game targeted for? (e.g. web, mobile, desktop)"),
        ("mechanics", "What are the core gameplay mechanics or rules?")
    ],
    "Startup Idea": [
        ("problem", "What is the core problem you are trying to solve?"),
        ("target_market", "Who is the target market or ideal customer?"),
        ("monetization", "What is the planned monetization or business model?")
    ],
    "General Software Project": [
        ("objective", "What is the primary objective of this software?"),
        ("features", "What are the key features or requirements?"),
        ("tech_stack", "Do you have any preferred programming languages or technologies in mind?")
    ]
}

class ProjectManager:
    def __init__(self):
        self.active_session = None
        self.detector = ProjectDetector()
        # Track the key of the question we just asked the user
        self.last_asked_requirement = None

    def start_session(self, project_type=None, project_name=None) -> str:
        """Starts a new project session and sets initial state."""
        self.active_session = ProjectSession(project_name=project_name, project_type=project_type)
        logger.info("[ProjectMode] Activated")
        
        if project_type is None:
            self.active_session.set_stage("DISCOVERY")
            logger.info("[ProjectMode] Discovery")
            return (
                "Alright, boss. Let's structure this properly. "
                "What are we building?\n\n"
                "• Website\n"
                "• Mobile App\n"
                "• Desktop App\n"
                "• AI Assistant\n"
                "• Dashboard\n"
                "• Game\n"
                "• Startup Idea\n"
                "• General Software Project"
            )
        else:
            self.active_session.set_stage("REQUIREMENTS")
            logger.info("[ProjectMode] Requirements Stage started")
            return self._ask_next_question()

    def handle_exit(self, command: str) -> str:
        """Clears the active session and exits project mode."""
        self.active_session = None
        self.last_asked_requirement = None
        logger.info("[ProjectMode] Exited project mode")
        return "Alright, boss. Exiting project mode. Back to normal assistant mode."

    def get_status_info(self, command: str) -> str:
        """Handles project status commands."""
        if not self.active_session:
            return "No active project session."

        cmd = command.lower().strip()
        if "summary" in cmd:
            if self.active_session.project_summary:
                return (
                    f"**Project Summary: {self.active_session.project_name}**\n\n"
                    f"{self.active_session.project_summary}\n\n"
                    f"**Suggested Architecture:**\n{self.active_session.architecture_summary}"
                )
            else:
                return "Project planning is not completed yet. We are still gathering requirements."

        elif "status" in cmd:
            return (
                f"**Project Status**\n"
                f"Project: {self.active_session.project_name}\n"
                f"Type: {self.active_session.project_type}\n"
                f"Stage: {self.active_session.current_stage}\n"
                f"State: {self.active_session.project_state}\n"
                f"Completion: {self.active_session.completion_percentage}%"
            )

        elif "next" in cmd:
            if self.active_session.current_stage == "REQUIREMENTS":
                next_q = self._get_next_question_details()
                if next_q:
                    return f"Next requirement: {next_q[0]}. Question: {next_q[1]}"
                return "All requirements collected. Ready to plan."
            elif self.active_session.current_stage == "HANDOFF_READY":
                return "The project is fully planned. The Antigravity prompt draft is prepared. Let me know when you're ready to proceed."
            else:
                return f"Current stage is {self.active_session.current_stage}."

        elif "roadmap" in cmd:
            if self.active_session.roadmap:
                return f"**Build Roadmap:**\n\n{self.active_session.roadmap}"
            return "Roadmap not generated yet. Finish collecting requirements first."

        elif "phase" in cmd:
            return f"Current Phase: {self.active_session.current_stage} ({self.active_session.project_state})"

        return "Unknown project status command."

    def process_message(self, user_input: str) -> str:
        """Core message loop for Project Mode."""
        if not self.active_session:
            # Detect build intent first if not already in project mode
            detection = self.detector.detect_project_intent(user_input)
            if detection["intent_detected"]:
                return self.start_session(
                    project_type=detection["project_type"],
                    project_name=detection["project_name"]
                )
            return "No active project session."

        cleaned = user_input.lower().strip()

        # Handle Exit Commands
        exit_phrases = ["cancel project", "exit project mode", "start over", "new project"]
        if any(p in cleaned for p in exit_phrases):
            return self.handle_exit(cleaned)

        # Handle Status/Utility Commands
        status_phrases = ["show summary", "project status", "whats next", "what's next", "show roadmap", "current phase"]
        if any(p in cleaned for p in status_phrases):
            return self.get_status_info(cleaned)

        # 1. DISCOVERY STAGE
        if self.active_session.current_stage == "DISCOVERY":
            # Map input to a valid category
            mapped_type = self._map_to_category(user_input)
            self.active_session.project_type = mapped_type
            self.active_session.set_stage("REQUIREMENTS")
            logger.info("[ProjectMode] Discovery completed")
            return f"Got it, boss. Let's structure this as a {mapped_type}.\n\n" + self._ask_next_question()

        # 2. REQUIREMENTS STAGE
        elif self.active_session.current_stage == "REQUIREMENTS":
            # Store the answer to the last asked requirement
            if self.last_asked_requirement:
                self.active_session.update_requirement(self.last_asked_requirement, user_input)
                logger.info("[ProjectMode] Requirement collected")
                self.last_asked_requirement = None

            # Calculate completeness
            questions_list = PROJECT_QUESTIONS.get(self.active_session.project_type, PROJECT_QUESTIONS["General Software Project"])
            total_q = len(questions_list)
            collected_q = len(self.active_session.requirements)
            self.active_session.completion_percentage = round((collected_q / total_q) * 100.0, 1)

            # Check if we have more questions to ask
            next_question_info = self._get_next_question_details()
            if next_question_info:
                return f"Got it, boss. " + self._ask_next_question()
            else:
                # All requirements gathered! Transition automatically into PLANNING
                return self._run_planning_phase()

        return "Alright, boss. Let me know if you want to show summary or exit project mode."

    def _map_to_category(self, user_input: str) -> str:
        cleaned = user_input.lower().strip()
        
        # Exact category match
        for key in PROJECT_QUESTIONS.keys():
            if key.lower() in cleaned:
                return key
        
        # Keyword mapping using project detector logic
        detection = self.detector.detect_project_intent(user_input)
        if detection["project_type"]:
            return detection["project_type"]
            
        return "General Software Project"

    def _get_next_question_details(self):
        questions_list = PROJECT_QUESTIONS.get(self.active_session.project_type, PROJECT_QUESTIONS["General Software Project"])
        for key, question in questions_list:
            if key not in self.active_session.requirements:
                return key, question
        return None

    def _ask_next_question(self) -> str:
        next_q = self._get_next_question_details()
        if next_q:
            self.last_asked_requirement = next_q[0]
            return next_q[1]
        return "All requirements collected."

    def _run_planning_phase(self) -> str:
        """Transitions into planning stage, generates roadmap and draft prompt."""
        self.active_session.set_stage("PLANNING")
        logger.info("[ProjectMode] Planning started")

        project_name = self.active_session.project_name
        project_type = self.active_session.project_type
        requirements = self.active_session.requirements

        import sys
        is_testing = 'unittest' in sys.modules or any('test' in arg for arg in sys.argv)

        # 1. Programmatic Fallback Plan Generation
        plan = self._generate_programmatic_plan(project_name, project_type, requirements)
        
        # 2. Try to enrich using LLM if Ollama is running and not in test mode
        if not is_testing:
            try:
                llm_plan = self._generate_llm_plan(project_name, project_type, requirements)
                if llm_plan:
                    plan = llm_plan
            except Exception as e:
                logger.warning(f"Failed to use LLM for planning, using programmatic template: {e}")

        # Update session summaries
        self.active_session.project_summary = plan.get("summary")
        self.active_session.architecture_summary = plan.get("architecture")
        self.active_session.roadmap = plan.get("roadmap")
        self.active_session.set_stage("SUMMARY_READY")
        logger.info("[ProjectMode] Summary generated")

        # 3. Generate Handoff Prompt Draft
        prompt_draft = self._generate_handoff_prompt(project_name, project_type, plan)
        self.active_session.antigravity_prompt_draft = prompt_draft
        self.active_session.set_stage("HANDOFF_READY")
        logger.info("[ProjectMode] Handoff ready")

        # Format output response
        response = (
            f"Alright, boss. Let's structure this properly.\n\n"
            f"**Project Summary:**\n{self.active_session.project_summary}\n\n"
            f"**Suggested Architecture & Tech Stack:**\n{self.active_session.architecture_summary}\n\n"
            f"**Build Roadmap:**\n{self.active_session.roadmap}\n\n"
            f"**Antigravity Prompt Draft Prepared.** It is saved in the project session. "
            f"Let me know if you want to exit or inspect anything."
        )
        return response

    def _generate_programmatic_plan(self, name: str, p_type: str, reqs: dict) -> dict:
        """Generates a structured plan based on requirements dictionary."""
        # Clean up keys for presentation
        req_summary = "\n".join([f"- **{k.capitalize()}**: {v}" for k, v in reqs.items()])
        
        summary = (
            f"The project '{name}' is structured as a {p_type}. "
            f"It is aimed at addressing the following specifications:\n{req_summary}"
        )
        
        # Specific defaults per project type
        if p_type == "Website":
            arch = (
                "- **Architecture**: Single Page Application (SPA) with server-side rendering (SSR) for SEO optimization.\n"
                "- **Tech Stack**: React/Next.js, TailwindCSS, Node.js backend.\n"
                "- **Database**: PostgreSQL or Prisma ORM."
            )
            goals = "1. Deliver a responsive interface.\n2. Optimize loading speeds.\n3. Ensure semantic HTML structure."
            roadmap = (
                "Milestone 1 — Setup: Initialize Next.js app, configure styling templates.\n"
                "Milestone 2 — Features: Build landing page, navigation elements, core pages.\n"
                "Milestone 3 — Finishing: Add metadata, conduct responsive styling checks."
            )
            features = reqs.get("features", "Landing page, navigation, responsive container.")
        elif p_type == "Mobile App":
            arch = (
                "- **Architecture**: Cross-platform client architecture with local offline-first SQLite database and cloud syncing.\n"
                "- **Tech Stack**: Flutter / React Native, Firebase authentication.\n"
                "- **Database**: SQLite / Room database."
            )
            goals = "1. Cross-platform support.\n2. High performance and smooth UI transitions."
            roadmap = (
                "Milestone 1: Project setup, state management config.\n"
                "Milestone 2: Implementing layout, navigation, and primary screens.\n"
                "Milestone 3: Data synchronization and local database operations."
            )
            features = reqs.get("functionality", "User login, content dashboard, navigation flow.")
        elif p_type == "AI Assistant":
            arch = (
                "- **Architecture**: Modular agent loop using prompt routers, cognitive memory buffers, and custom tool bindings.\n"
                "- **Tech Stack**: Python, LangChain, Ollama/Gemini API wrapper.\n"
                "- **Database**: ChromaDB (Vector DB) / JSON logs."
            )
            goals = "1. Clean separation of agent capabilities.\n2. Graceful error handling for API timeouts."
            roadmap = (
                "Milestone 1: Set up basic routing pipeline and agent loops.\n"
                "Milestone 2: Add tools, APIs, and document parser interfaces.\n"
                "Milestone 3: Fine-tune prompts and verify accuracy."
            )
            features = reqs.get("capabilities", "Agent loop, custom API tool call execution.")
        else:
            arch = (
                "- **Architecture**: Modular application architecture prioritizing separation of concerns.\n"
                "- **Tech Stack**: Python / JavaScript with modern helper libraries."
            )
            goals = "1. Clear and maintainable codebase.\n2. Scalable feature modules."
            roadmap = (
                "Milestone 1: Project setup, environment configuration.\n"
                "Milestone 2: Core feature implementation.\n"
                "Milestone 3: Validation, testing, and deployment prep."
            )
            features = reqs.get("features", "Core application business logic.")

        return {
            "summary": summary,
            "goals": goals,
            "features": features,
            "architecture": arch,
            "roadmap": roadmap,
            "risks": "- Scope creep due to wide requirement boundaries.\n- External API dependency delays.",
            "expansion_ideas": "- Add comprehensive telemetry/logging dashboards.\n- Implement user role-based access controls."
        }

    def _generate_llm_plan(self, name: str, p_type: str, reqs: dict) -> dict:
        """Tries to query LLM for project plan if running."""
        # Initialize with programmatic plan so we preserve features, goals, risks, etc.
        plan = self._generate_programmatic_plan(name, p_type, reqs)
        
        req_details = ", ".join([f"{k}: {v}" for k, v in reqs.items()])
        prompt = (
            f"Generate a structured project plan for a {p_type} named '{name}'.\n"
            f"User Requirements: {req_details}\n\n"
            f"Please structure your reply exactly as a plan. "
            f"Provide a brief project summary, suggested tech stack, and milestone roadmap. "
            f"Keep it very brief, assistant-like."
        )
        
        # System instructions
        context = (
            "You are ROBIN, the project planner. "
            "Help the boss structure their new project. "
            "Keep the responses highly technical and clean."
        )
        
        response = get_ai_response(prompt, context)
        if "Can't reach Ollama" in response or "Something went wrong" in response:
            return plan
            
        if "summary" in response.lower():
            sections = re.split(r'#+\s*', response)
            for sec in sections:
                if sec.lower().startswith("summary"):
                    plan["summary"] = sec.split("\n", 1)[-1].strip()
                elif "architecture" in sec.lower() or "tech stack" in sec.lower():
                    plan["architecture"] = sec.split("\n", 1)[-1].strip()
                elif "roadmap" in sec.lower() or "milestone" in sec.lower():
                    plan["roadmap"] = sec.split("\n", 1)[-1].strip()
        else:
            plan["summary"] = response
            
        return plan

    def _generate_handoff_prompt(self, name: str, p_type: str, plan: dict) -> str:
        """Prepares a clean Antigravity prompt draft."""
        return (
            f"=== ANTIGRAVITY BUILD PROMPT ===\n"
            f"Project Name: {name}\n"
            f"Project Type: {p_type}\n\n"
            f"Context & Summary:\n{plan.get('summary')}\n\n"
            f"Target Architecture:\n{plan.get('architecture')}\n\n"
            f"Features to Build:\n{plan.get('features')}\n\n"
            f"Roadmap:\n{plan.get('roadmap')}\n\n"
            f"Expectations:\n"
            f"Implement a high-quality codebase that fits this specification. "
            f"Prioritize clean directory organization and error boundaries."
        )

project_manager = ProjectManager()
