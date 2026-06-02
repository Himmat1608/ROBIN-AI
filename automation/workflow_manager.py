from core.assistant_state import state
from system.automation import AutomationManager

class WorkflowManager:
    """
    Manages complex multi-step assistant workflows (Coding mode, Study mode, etc.)
    """
    
    WORKFLOWS = {
        "coding": {
            "trigger_phrases": ["start coding mode", "let's code", "prepare coding workspace", "coding mode"],
            "action": AutomationManager.run_coding_mode,
            "args": {"editor": "code"}
        },
        "study": {
            "trigger_phrases": ["study mode", "i'm gonna study", "start study session"],
            "action": AutomationManager.run_study_mode,
            "args": {}
        },
        "focus": {
            "trigger_phrases": ["enable focus mode", "start focus mode", "focus mode"],
            "action": lambda: "Focus mode enabled. I'll keep interruptions to a minimum.",
            "args": {}
        }
    }

    def check_for_workflow(self, user_input: str) -> dict:
        """Checks if user input triggers a known workflow."""
        cleaned = user_input.lower().strip()
        
        for name, data in self.WORKFLOWS.items():
            if any(phrase in cleaned for phrase in data["trigger_phrases"]):
                return {
                    "type": "WORKFLOW",
                    "name": name,
                    "action": data["action"],
                    "args": data["args"]
                }
        return None

    def execute_workflow(self, workflow_data: dict) -> str:
        """Executes the workflow and updates state."""
        name = workflow_data["name"]
        action = workflow_data["action"]
        args = workflow_data["args"]
        
        state.set_workflow(name)
        return action(**args)

# Singleton instance
workflow_mgr = WorkflowManager()
