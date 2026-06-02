import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add workspace directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.intent_engine import IntentEngine
from core.command_router import determine_route
from core.assistant import RobinAssistant
from project_mode import ProjectModeManager, STATE_FILE

class TestProjectModeRefinement(unittest.TestCase):
    def setUp(self):
        # Reset JSON state file before each test
        if os.path.exists(STATE_FILE):
            try:
                os.remove(STATE_FILE)
            except Exception:
                pass
        
        # Reset singleton/mock state
        from core.project_manager import project_manager
        project_manager.active_session = None

    def tearDown(self):
        if os.path.exists(STATE_FILE):
            try:
                os.remove(STATE_FILE)
            except Exception:
                pass

    def test_intent_detection_confidence_rules(self):
        engine = IntentEngine()

        # 1. High confidence triggers
        triggers = [
            "let's build a website",
            "let's build an app",
            "let's create a dashboard",
            "start a project",
            "make a SaaS",
            "build a game",
            "create a platform",
            "build a portfolio"
        ]
        for t in triggers:
            res = engine.analyze_intent(t)
            self.assertEqual(res["intent"], "PROJECT_MODE_INTENT")
            self.assertEqual(res["action"], "PROJECT_MODE_START")
            self.assertGreaterEqual(res["confidence"], 0.70)

        # 2. Informational/question queries (must not trigger project mode)
        non_triggers = [
            "explain websites",
            "how do dashboards work",
            "what is SaaS",
            "tell me about portfolios"
        ]
        for nt in non_triggers:
            res = engine.analyze_intent(nt)
            if res["intent"] == "PROJECT_MODE_INTENT":
                # If matched, confidence must be 0.0 or it shouldn't trigger
                self.assertLess(res["confidence"], 0.70)

    def test_progressive_intake_and_discovery(self):
        # Mock handle_response to return clean text
        with patch('core.assistant.handle_response', lambda x: x):
            assistant = RobinAssistant()
            
            # Start a website project (ambiguous -> triggers discovery list)
            resp = assistant.process_input("let's build a website")
            self.assertIn("What are we building?", resp)
            self.assertIn("SaaS", resp)
            self.assertIn("E-commerce", resp)
            
            # Choose SaaS
            resp = assistant.process_input("SaaS")
            self.assertIn("What is the primary purpose of this website?", resp)
            
            # Provide purpose
            resp = assistant.process_input("A tool for developers to monitor servers.")
            self.assertIn("Who is the target audience", resp)
            
            # Provide audience
            resp = assistant.process_input("Developers and system administrators.")
            self.assertIn("What design style or aesthetic", resp)
            
            # Provide design style
            resp = assistant.process_input("Clean, dark mode layout.")
            self.assertIn("What are the key features", resp)

    def test_minimum_threshold_and_summary(self):
        with patch('core.assistant.handle_response', lambda x: x):
            assistant = RobinAssistant()
            
            # Start dashboard project directly
            resp = assistant.process_input("let's create a dashboard")
            self.assertIn("What data sources or APIs will feed this dashboard?", resp)
            
            # Show summary before threshold (should fail)
            resp = assistant.process_input("show summary")
            self.assertIn("Not enough requirements gathered yet", resp)
            
            # Answer 1: Data sources
            assistant.process_input("Prometheus and Grafana APIs.")
            
            # Answer 2: Users
            assistant.process_input("Operations engineers and developers.")
            
            # Answer 3: Reporting needs
            resp = assistant.process_input("Real-time latency charts and error rates.")
            
            # Since Dashboard requirements has 4 items (data sources, users, reporting needs, permissions),
            # answering the 3rd requirement meets the minimum threshold (goal, users, features known).
            # Let's request the summary
            resp = assistant.process_input("show summary")
            self.assertIn("=== PROJECT SUMMARY", resp)
            self.assertIn("Prometheus and Grafana APIs", resp)
            self.assertIn("Operations engineers", resp)

    def test_project_continuity_restoration(self):
        with patch('core.assistant.handle_response', lambda x: x):
            assistant = RobinAssistant()
            
            # 1. Start a dashboard project and collect one requirement
            assistant.process_input("let's create a dashboard")
            assistant.process_input("REST API backend.")
            
            # 2. Exit project mode
            resp = assistant.process_input("exit project mode")
            self.assertIn("Exiting project mode", resp)
            
            # 3. Request restoration using continuity phrases
            resp = assistant.process_input("continue the dashboard")
            self.assertIn("Project restored, boss.", resp)
            self.assertIn("Dashboard project active.", resp)
            self.assertIn("Current focus:", resp)
            self.assertIn("Users", resp)

    def test_project_switching_multiple_projects(self):
        with patch('core.assistant.handle_response', lambda x: x):
            assistant = RobinAssistant()
            
            # 1. Start SaaS project
            assistant.process_input("let's build a website")
            assistant.process_input("SaaS")
            
            # 2. Start a second project (SaaS gets paused, Dashboard becomes active)
            assistant.process_input("let's create a dashboard")
            
            # Check state
            manager = assistant.project_mode_manager
            projects = manager.state["projects"]
            self.assertEqual(len(projects), 2)
            
            # Verify Dashboard is active and SaaS is paused
            active_proj = manager.get_active_project()
            self.assertEqual(active_proj["project_type"], "Dashboard")
            self.assertEqual(active_proj["project_status"], "active")

if __name__ == "__main__":
    unittest.main()
