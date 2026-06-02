import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

VALID_STAGES = ["DISCOVERY", "REQUIREMENTS", "PLANNING", "SUMMARY_READY", "HANDOFF_READY"]
VALID_STATES = ["PLANNING", "DESIGNING", "BUILDING", "TESTING", "REFINING", "DEPLOYING", "MAINTAINING", "ARCHIVED"]

class ProjectSession:
    def __init__(self, project_name=None, project_type=None):
        self.project_name = project_name or "New Project"
        self.project_type = project_type  # e.g., Website, Mobile App, AI Assistant
        self.project_state = "PLANNING"   # Default state
        self.current_stage = "DISCOVERY"  # Default stage
        
        # Dictionary storing collected requirement key-values
        # e.g., {"audience": "...", "style": "...", "features": "..."}
        self.requirements = {}
        
        # Track requirements status
        self.completion_percentage = 0.0
        
        # Structured project planning outputs
        self.project_summary = None
        self.architecture_summary = None
        self.roadmap = None
        
        # Bridge to Phase 7.2 / Antigravity handoff
        self.antigravity_prompt_draft = None
        
        # Metadata
        self.created_date = datetime.datetime.now().isoformat()
        self.last_active_date = datetime.datetime.now().isoformat()

    def set_stage(self, stage: str):
        if stage in VALID_STAGES:
            self.current_stage = stage
            self.last_active_date = datetime.datetime.now().isoformat()
            logger.info(f"[ProjectMode] Stage changed to {stage}")
        else:
            raise ValueError(f"Invalid project stage: {stage}")

    def set_state(self, state: str):
        if state in VALID_STATES:
            self.project_state = state
            self.last_active_date = datetime.datetime.now().isoformat()
            logger.info(f"[ProjectMode] State changed to {state}")
        else:
            raise ValueError(f"Invalid project state: {state}")

    def update_requirement(self, key: str, value: str):
        self.requirements[key] = value
        self.last_active_date = datetime.datetime.now().isoformat()
        logger.info(f"[ProjectMode] Requirement collected: {key} = {value}")

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "project_type": self.project_type,
            "project_state": self.project_state,
            "current_stage": self.current_stage,
            "requirements": self.requirements,
            "completion_percentage": self.completion_percentage,
            "project_summary": self.project_summary,
            "architecture_summary": self.architecture_summary,
            "roadmap": self.roadmap,
            "antigravity_prompt_draft": self.antigravity_prompt_draft,
            "created_date": self.created_date,
            "last_active_date": self.last_active_date
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ProjectSession':
        session = cls(
            project_name=data.get("project_name"),
            project_type=data.get("project_type")
        )
        session.project_state = data.get("project_state", "PLANNING")
        session.current_stage = data.get("current_stage", "DISCOVERY")
        session.requirements = data.get("requirements", {})
        session.completion_percentage = data.get("completion_percentage", 0.0)
        session.project_summary = data.get("project_summary")
        session.architecture_summary = data.get("architecture_summary")
        session.roadmap = data.get("roadmap")
        session.antigravity_prompt_draft = data.get("antigravity_prompt_draft")
        session.created_date = data.get("created_date", session.created_date)
        session.last_active_date = data.get("last_active_date", session.last_active_date)
        return session
