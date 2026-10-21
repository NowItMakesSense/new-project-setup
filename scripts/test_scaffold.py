#!/usr/bin/env python3
"""Regression suite for scaffold.py and verify_setup.py.

Usage: python scripts/test_scaffold.py           (or: python -m unittest scripts.test_scaffold)
No third-party dependencies - stdlib unittest only, consistent with scaffold.py/verify_setup.py.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = ROOT / "scripts" / "scaffold.py"
VERIFY = ROOT / "scripts" / "verify_setup.py"
PY = sys.executable


def base_answers(**overrides) -> dict:
    answers = {
        "PROJECT_NAME": "demo", "PROJECT_DESCRIPTION": "demo project", "DOC_LANGUAGE": "en",
        "DOMAIN": "demo", "PROJECT_TYPE": "api", "STACK": "python", "TEST_CMD": "pytest",
        "LINT_CMD": "ruff", "BUILD_CMD": "none", "DB_ENGINE": "postgresql",
        "TEST_DB_STRATEGY": "in-memory fakes", "CI_PROVIDER": "none", "VCS_BRANCHING": "trunk-based",
        "ENGINEERING_PRINCIPLES": "defaults", "COMPLIANCE": "none", "TEAM": "solo",
        "PYTHON_CMD": "python", "NPX_CMD": "none", "HAS_UI": "no",
        "MODEL_PRIORITY": "balanced", "COVERAGE_THRESHOLD": "80", "EXTRA_DENY": [],
    }
    answers.update(overrides)
    return answers


def run_scaffold(target: Path, answers: dict, *extra_args: str) -> subprocess.CompletedProcess:
    answers_path = target.parent / (target.name + "-answers.json")
    answers_path.write_text(json.dumps(answers), encoding="utf-8")
    return subprocess.run(
        [PY, str(SCAFFOLD), "--target", str(target), "--answers", str(answers_path), *extra_args],
        capture_output=True, text=True,
    )


def run_verify(target: Path, answers_path: Path | None = None) -> subprocess.CompletedProcess:
    args = [PY, str(VERIFY), "--target", str(target)]
    if answers_path is not None:
        args += ["--answers", str(answers_path)]
    return subprocess.run(args, capture_output=True, text=True)


class ScaffoldTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.target = Path(self._tmp.name) / "proj"

    def tearDown(self):
        self._tmp.cleanup()

    def test_missing_required_key_fails(self):
        answers = base_answers()
        del answers["TEST_CMD"]
        r = run_scaffold(self.target, answers)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("TEST_CMD", r.stdout + r.stderr)

    def test_default_scaffold_passes_verify(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        v = run_verify(self.target)
        self.assertEqual(v.returncode, 0, v.stdout)
        self.assertIn("0 failure(s)", v.stdout)

    def test_model_tiers_and_new_artifacts(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        agents_dir = self.target / ".claude" / "agents"
        for name, tier in [("architect", "opus"), ("security", "opus"), ("reviewer", "opus"),
                            ("debug", "opus"), ("devops-docs", "haiku"), ("implementer", "sonnet"),
                            ("knowledge-graph", "sonnet")]:
            body = (agents_dir / f"{name}.md").read_text(encoding="utf-8")
            model_line = next(line for line in body.splitlines() if line.startswith("model:"))
            self.assertEqual(model_line.strip(), f"model: {tier}", name)
        self.assertTrue((self.target / ".claude" / "skills" / "amend-constitution" / "SKILL.md").is_file())
        self.assertTrue((self.target / "docs" / "specs" / "_templates" / "findings-ledger.md").is_file())
        self.assertTrue((self.target / "docs" / "specs" / "_templates" / "retro.md").is_file())
        self.assertTrue((self.target / "docs" / "specs" / "_templates" / "feature-status.md").is_file())

    def test_model_priority_cost_has_no_opus(self):
        r = run_scaffold(self.target, base_answers(MODEL_PRIORITY="cost"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        agents_dir = self.target / ".claude" / "agents"
        for p in agents_dir.glob("*.md"):
            body = p.read_text(encoding="utf-8")
            model_line = next(line for line in body.splitlines() if line.startswith("model:"))
            self.assertNotEqual(model_line.strip(), "model: opus", p.name)

    def test_model_priority_quality_upgrades_domain_and_knowledge_graph(self):
        r = run_scaffold(self.target, base_answers(MODEL_PRIORITY="quality"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for name in ("domain", "knowledge-graph"):
            body = (self.target / ".claude" / "agents" / f"{name}.md").read_text(encoding="utf-8")
            model_line = next(line for line in body.splitlines() if line.startswith("model:"))
            self.assertEqual(model_line.strip(), "model: opus", name)

    def test_invalid_model_priority_fails(self):
        r = run_scaffold(self.target, base_answers(MODEL_PRIORITY="fastest"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("MODEL_PRIORITY", r.stdout + r.stderr)

    def test_coverage_threshold_wired_into_claude_md_and_ci(self):
        r = run_scaffold(self.target, base_answers(COVERAGE_THRESHOLD="90", CI_PROVIDER="github-actions"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        claude_md = (self.target / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("90", claude_md)
        ci = (self.target / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("90", ci)

    def test_has_ui_yes_generates_designer(self):
        r = run_scaffold(self.target, base_answers(HAS_UI="yes"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.target / ".claude" / "agents" / "designer.md").is_file())

    def test_has_ui_no_omits_designer(self):
        r = run_scaffold(self.target, base_answers(HAS_UI="no"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.target / ".claude" / "agents" / "designer.md").exists())

    def test_npx_cmd_set_adds_mcp_server(self):
        r = run_scaffold(self.target, base_answers(NPX_CMD="npx"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        settings = json.loads((self.target / ".claude" / "settings.json").read_text())
        kg = settings["mcpServers"]["knowledge-graph"]
        self.assertEqual(kg["command"], "npx")
        self.assertEqual(kg["args"], ["-y", "@modelcontextprotocol/server-memory"])
        agent = (self.target / ".claude" / "agents" / "knowledge-graph.md").read_text()
        self.assertIn("mcp__knowledge-graph__read_graph", agent)

    def test_npx_cmd_none_omits_mcp_server(self):
        r = run_scaffold(self.target, base_answers(NPX_CMD="none"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        settings = json.loads((self.target / ".claude" / "settings.json").read_text())
        self.assertNotIn("mcpServers", settings)
        agent = (self.target / ".claude" / "agents" / "knowledge-graph.md").read_text()
        tools_line = next(line for line in agent.splitlines() if line.startswith("tools:"))
        self.assertNotIn("mcp__knowledge-graph__", tools_line)

    def test_ci_provider_github_actions_generates_workflow(self):
        r = run_scaffold(self.target, base_answers(CI_PROVIDER="github-actions"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.target / ".github" / "workflows" / "ci.yml").is_file())
        ci = (self.target / ".github" / "workflows" / "ci.yml").read_text()
        self.assertIn("verify-guard.py", ci)

    def test_ci_provider_none_omits_workflow(self):
        r = run_scaffold(self.target, base_answers(CI_PROVIDER="none"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.target / ".github").exists())

    def test_extra_deny_is_appended(self):
        r = run_scaffold(self.target, base_answers(EXTRA_DENY=["Bash(terraform apply:*)"]))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        settings = json.loads((self.target / ".claude" / "settings.json").read_text())
        self.assertIn("Bash(terraform apply:*)", settings["permissions"]["deny"])

    def test_existing_file_skipped_without_overwrite(self):
        run_scaffold(self.target, base_answers())
        claude_md = self.target / "CLAUDE.md"
        claude_md.write_text("CUSTOMIZED BY USER", encoding="utf-8")
        r = run_scaffold(self.target, base_answers(PROJECT_NAME="changed"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(claude_md.read_text(encoding="utf-8"), "CUSTOMIZED BY USER")

    def test_overwrite_replaces_existing_file(self):
        run_scaffold(self.target, base_answers())
        claude_md = self.target / "CLAUDE.md"
        claude_md.write_text("CUSTOMIZED BY USER", encoding="utf-8")
        r = run_scaffold(self.target, base_answers(PROJECT_NAME="changed"), "--overwrite")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("changed", claude_md.read_text(encoding="utf-8"))

    def test_merge_settings_unions_deny_rules_without_clobbering_custom_keys(self):
        run_scaffold(self.target, base_answers(NPX_CMD="none"))
        settings_path = self.target / ".claude" / "settings.json"
        settings = json.loads(settings_path.read_text())
        settings["permissions"]["deny"].append("Bash(my-custom-tool:*)")
        settings["someCustomKey"] = "keep-me"
        settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")

        r = run_scaffold(self.target, base_answers(NPX_CMD="npx"), "--merge-settings")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        merged = json.loads(settings_path.read_text())
        self.assertIn("Bash(my-custom-tool:*)", merged["permissions"]["deny"])
        self.assertIn("Bash(psql:*)", merged["permissions"]["deny"])
        self.assertEqual(merged["someCustomKey"], "keep-me")
        self.assertIn("knowledge-graph", merged["mcpServers"])

    def test_verify_fails_when_deny_rule_removed(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        settings_path = self.target / ".claude" / "settings.json"
        settings = json.loads(settings_path.read_text())
        settings["permissions"]["deny"] = [d for d in settings["permissions"]["deny"] if "psql" not in d]
        settings_path.write_text(json.dumps(settings), encoding="utf-8")

        v = run_verify(self.target)
        self.assertNotEqual(v.returncode, 0)
        self.assertIn("FAIL", v.stdout)

    def test_hook_blocks_cloud_secret_manager_cli(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        hook = self.target / ".claude" / "hooks" / "block-db-access.py"
        cases = [
            "aws secretsmanager get-secret-value --secret-id prod/db",
            "vault read secret/prod/db",
            "gcloud secrets versions access latest --secret=prod-db",
            "az keyvault secret show --name db-pass",
            "doppler secrets get DB_PASSWORD",
        ]
        for cmd in cases:
            p = subprocess.run([PY, str(hook)], input=json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}}),
                                capture_output=True, text=True)
            self.assertEqual(p.returncode, 2, f"should block: {cmd}\n{p.stderr}")

    def test_dry_run_creates_nothing(self):
        r = run_scaffold(self.target, base_answers(), "--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
