from core.assistant_state_engine import state_engine, AssistantState as States

class AssistantState:
    """
    Maintains the current state of the assistant, including active workflows,
    media playback, and recently used applications.
    """
    def __init__(self):
        self.active_workflow = None
        self.is_media_playing = False
        self.last_media_platform = "spotify"
        self.last_app_opened = None
        self.current_task = None
        self.last_response = None
        
    @property
    def current_mode(self):
        return state_engine.current_state

    def update_media(self, playing: bool, platform: str = None):
        self.is_media_playing = playing
        if platform:
            self.last_media_platform = platform
        if playing:
            state_engine.transition_to(States.MEDIA)
            
    def update_app(self, app_name: str):
        self.last_app_opened = app_name
        
    def set_workflow(self, workflow_name: str):
        self.active_workflow = workflow_name
        if workflow_name == "coding":
            state_engine.transition_to(States.CODING)
        elif workflow_name == "focus":
            state_engine.transition_to(States.FOCUS)

# Singleton instance
state = AssistantState()
