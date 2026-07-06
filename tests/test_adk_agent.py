from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ADK_AGENT = ROOT / "app" / "adk_agent.py"


class AdkAgentDefinitionTests(unittest.TestCase):
    def test_adk_agent_defines_root_agent_with_existing_tools(self):
        source = ADK_AGENT.read_text(encoding="utf-8")

        self.assertIn("from google.adk.agents import Agent", source)
        self.assertIn("from google.adk.tools import FunctionTool", source)
        self.assertIn("root_agent = Agent(", source)

        for tool_name in [
            "adk_get_application",
            "adk_check_allocation",
            "adk_check_budget_risk",
            "adk_check_receipt_status",
            "adk_summarize_financial_status",
        ]:
            self.assertIn(f"FunctionTool({tool_name})", source)

    def test_adk_agent_instruction_preserves_read_only_guardrails(self):
        source = ADK_AGENT.read_text(encoding="utf-8")

        self.assertIn("Never approve applications", source)
        self.assertIn("Never update ERP data", source)
        self.assertIn("Never create vouchers", source)
        self.assertIn("risk level, findings, evidence", source)

    def test_adk_tool_wrappers_do_not_return_none_values(self):
        import app.adk_agent as adk_agent

        samples = [
            adk_agent.adk_get_application("EG-2099-9999"),
            adk_agent.adk_check_allocation("EG-2026-0001"),
            adk_agent.adk_check_budget_risk("EG-2026-0001"),
            adk_agent.adk_check_receipt_status("EG-2026-0001"),
            adk_agent.adk_summarize_financial_status("EG-2026-0001"),
        ]

        for sample in samples:
            self.assertIsInstance(sample, dict)
            self.assertFalse(self._contains_none(sample), sample)

    def _contains_none(self, value):
        if value is None:
            return True
        if isinstance(value, dict):
            return any(self._contains_none(item) for item in value.values())
        if isinstance(value, list):
            return any(self._contains_none(item) for item in value)
        return False


if __name__ == "__main__":
    unittest.main()
