import unittest
from core.project_detector import ProjectDetector
from core.project_session import ProjectSession
from core.project_manager import ProjectManager, project_manager
from core.intent_engine import IntentEngine
from core.command_router import determine_route
from core.assistant import RobinAssistant

class TestProjectMode(unittest.TestCase):
    def setUp(self):
        # Reset project manager singleton before each test
        project_manager.active_session = None
        project_manager.last_asked_requirement = None

    def test_build_intent_detection(self):
        detector = ProjectDetector()
        
        # Real software builds should be detected
        res_web = detector.detect_project_intent("let's build a website")
        self.assertTrue(res_web["intent_detected"])
        self.assertEqual(res_web["project_type"], "Website")
        
        res_app = detector.detect_project_intent("let's create an app")
        self.assertTrue(res_app["intent_detected"])
        self.assertEqual(res_app["project_type"], "Mobile App")

        res_game = detector.detect_project_intent("make a pygame game")
        self.assertTrue(res_game["intent_detected"])
        self.assertEqual(res_game["project_type"], "Game")
        
        # Speculative sci-fi builds should NOT trigger project mode
        res_time = detector.detect_project_intent("let's build a time machine")
        self.assertFalse(res_time["intent_detected"])

        res_wormhole = detector.detect_project_intent("how about we create a wormhole in the basement")
        self.assertFalse(res_wormhole["intent_detected"])

    def test_routing(self):
        # Ensure build requests route to project_mode and time machine routes to ai_reasoning
        route_web = determine_route("let's build a website")
        self.assertEqual(route_web["route"], "project_mode")
        
        route_time = determine_route("let's build a time machine")
        self.assertEqual(route_time["route"], "ai_reasoning")

    def test_project_lifecycle_specified_type(self):
        assistant = RobinAssistant()
        
        # 1. Start website project (ambiguous -> triggers discovery stage)
        resp = assistant.process_input("let's build a website")
        self.assertIn("What are we building?", resp)
        self.assertEqual(assistant.active_stage, "DISCOVERY")
        
        # 2. Select SaaS
        resp = assistant.process_input("SaaS")
        self.assertIn("What is the primary purpose", resp)
        self.assertEqual(assistant.active_stage, "REQUIREMENTS")
        self.assertTrue(assistant.active_project.startswith("Project_") or assistant.active_project == "New Project")
        
        # 3. Provide purpose
        resp = assistant.process_input("business tool")
        self.assertIn("Who is the target audience", resp)
        self.assertEqual(assistant.active_stage, "REQUIREMENTS")
        
        # 4. Provide audience
        resp = assistant.process_input("designers and developers")
        self.assertIn("What design style or aesthetic", resp)
        
        # 5. Provide style
        resp = assistant.process_input("minimalist dark theme")
        self.assertIn("What are the key features", resp)
        
        # 6. Provide features
        resp = assistant.process_input("landing page, project gallery, contact form")
        self.assertIn("Should this be designed mobile-first", resp)
        
        # 7. Provide mobile-first
        resp = assistant.process_input("yes, mobile-first")
        self.assertIn("Do we need user authentication", resp)
        
        # 8. Provide authentication
        resp = assistant.process_input("no logins needed")
        self.assertIn("Are there any admin panel", resp)
        
        # 9. Provide admin panel -> Should transition to COMPLETED -> SUMMARY_READY -> HANDOFF_READY
        resp = assistant.process_input("no admin panel")
        self.assertIn("Project Goal", resp)
        self.assertIn("Suggested Architecture", resp)
        self.assertIn("Build Notes", resp)
        
        self.assertEqual(assistant.active_stage, "COMPLETED")
        
        # Check that we stored the draft prompt
        active_proj = assistant.project_mode_manager.get_active_project()
        self.assertIsNotNone(active_proj.get("future_prompt_package"))
        self.assertIn("landing page, project gallery, contact form", active_proj["future_prompt_package"]["requirements"]["features"])

    def test_project_lifecycle_discovery_flow(self):
        assistant = RobinAssistant()
        
        # 1. Start ambiguous project
        resp = assistant.process_input("let's build something")
        self.assertIn("What are we building?", resp)
        self.assertEqual(assistant.active_stage, "DISCOVERY")
        
        # 2. Select Website (Website maps to Custom internally for requirements list)
        resp = assistant.process_input("website")
        self.assertIn("What is the primary purpose", resp)
        self.assertEqual(assistant.active_stage, "REQUIREMENTS")
        active_proj = assistant.project_mode_manager.get_active_project()
        self.assertEqual(active_proj["project_type"], "Custom")

    def test_status_commands(self):
        assistant = RobinAssistant()
        
        # Set up a session manually to test status commands
        assistant.process_input("let's build a website")
        assistant.process_input("SaaS")
        
        # Phase check
        resp = assistant.process_input("current phase")
        self.assertIn("Current Phase: REQUIREMENTS", resp)

        # Status check
        resp = assistant.process_input("project status")
        self.assertIn("Project:", resp)
        self.assertIn("Stage: REQUIREMENTS", resp)

        # What's next check
        resp = assistant.process_input("what's next")
        self.assertIn("Next requirement: purpose", resp)

    def test_exit_conditions(self):
        assistant = RobinAssistant()
        
        # Start a project
        assistant.process_input("let's build a website")
        active_proj = assistant.project_mode_manager.get_active_project()
        self.assertIsNotNone(active_proj)
        
        # Exit project mode
        resp = assistant.process_input("exit project mode")
        self.assertIn("Exiting project mode", resp)
        active_proj = assistant.project_mode_manager.get_active_project()
        self.assertIsNone(active_proj)
        
        # Ensure we are back to normal routes
        route_normal = determine_route("hello")
        self.assertEqual(route_normal["route"], "greeting")

if __name__ == "__main__":
    unittest.main()
