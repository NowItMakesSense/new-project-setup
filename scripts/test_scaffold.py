#!/usr/bin/env python3
"""Regression suite for scaffold.py and verify_setup.py.

Usage: python scripts/test_scaffold.py           (or: python -m unittest scripts.test_scaffold)
No third-party dependencies - stdlib unittest only, consistent with scaffold.py/verify_setup.py.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = ROOT / "scripts" / "scaffold.py"
VERIFY = ROOT / "scripts" / "verify_setup.py"
RETUNE = ROOT / "scripts" / "retune.py"
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


def run_retune(target: Path, *extra_args: str) -> subprocess.CompletedProcess:
    return subprocess.run([PY, str(RETUNE), "--target", str(target), *extra_args],
                           capture_output=True, text=True)


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

    def test_status_archive_scaffolded(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.target / "docs" / "specs" / "STATUS-archive.md").is_file())
        status = (self.target / "docs" / "specs" / "STATUS.md").read_text(encoding="utf-8")
        self.assertIn("STATUS-archive.md", status)

    def test_orchestrate_skill_mentions_change_size_and_archiving(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        body = (self.target / ".claude" / "skills" / "orchestrate" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Change size", body)
        self.assertIn("## Archiving", body)
        self.assertNotIn("{{", body)

    def test_orchestrate_skill_reference_files_scaffolded(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        refs_dir = self.target / ".claude" / "skills" / "orchestrate" / "references"
        for ref in ["parallel-implementation.md", "context-hygiene.md", "archiving.md", "revert-checklist.md"]:
            self.assertTrue((refs_dir / ref).is_file(), ref)

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

    UI_AGENTS = ("designer", "frontend", "ui-reviewer")
    UI_REFS = ("art-direction.md", "app-screens.md", "materials-type.md", "motion.md", "worst-case.md", "review.md")

    def test_has_ui_yes_generates_frontend_team_and_craft_skill(self):
        r = run_scaffold(self.target, base_answers(HAS_UI="yes"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for name in self.UI_AGENTS:
            body = (self.target / ".claude" / "agents" / f"{name}.md").read_text(encoding="utf-8")
            frontmatter = body.split("---")[1]
            self.assertIn("skills:\n  - frontend-craft", frontmatter, name)
            self.assertIn("Skill", next(line for line in frontmatter.splitlines() if line.startswith("tools:")), name)
        skill = self.target / ".claude" / "skills" / "frontend-craft"
        self.assertIn("name: frontend-craft", (skill / "SKILL.md").read_text(encoding="utf-8"))
        for ref in self.UI_REFS:
            self.assertTrue((skill / "references" / ref).is_file(), ref)

    def test_has_ui_no_omits_frontend_team_and_craft_skill(self):
        r = run_scaffold(self.target, base_answers(HAS_UI="no"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for name in self.UI_AGENTS:
            self.assertFalse((self.target / ".claude" / "agents" / f"{name}.md").exists(), name)
        self.assertFalse((self.target / ".claude" / "skills" / "frontend-craft").exists())

    def test_has_ui_yes_passes_verify_with_answers(self):
        answers_path = self.target.parent / (self.target.name + "-answers.json")
        r = run_scaffold(self.target, base_answers(HAS_UI="yes"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        v = run_verify(self.target, answers_path)
        self.assertEqual(v.returncode, 0, v.stdout)
        self.assertIn("agent preloads the frontend-craft skill: frontend", v.stdout)
        self.assertIn("exists: frontend-craft/references/motion.md", v.stdout)

    def test_verify_fails_when_ui_agent_missing_with_has_ui_yes(self):
        answers_path = self.target.parent / (self.target.name + "-answers.json")
        r = run_scaffold(self.target, base_answers(HAS_UI="yes"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        (self.target / ".claude" / "agents" / "ui-reviewer.md").unlink()
        v = run_verify(self.target, answers_path)
        self.assertNotEqual(v.returncode, 0)
        self.assertIn("FAIL agent exists: ui-reviewer (HAS_UI=yes)", v.stdout)

    def test_ui_agent_tiers_follow_model_priority(self):
        expected = {"cost": ("sonnet", "sonnet"), "balanced": ("sonnet", "opus"), "quality": ("opus", "opus")}
        for priority, (frontend, ui_reviewer) in expected.items():
            with self.subTest(priority=priority):
                target = Path(self._tmp.name) / f"proj-{priority}"
                r = run_scaffold(target, base_answers(HAS_UI="yes", MODEL_PRIORITY=priority))
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                for name, model in (("frontend", frontend), ("ui-reviewer", ui_reviewer)):
                    body = (target / ".claude" / "agents" / f"{name}.md").read_text(encoding="utf-8")
                    self.assertIn(f"\nmodel: {model}\n", body, name)

    def test_tasks_template_and_orchestrator_route_ui_tasks(self):
        r = run_scaffold(self.target, base_answers(HAS_UI="yes"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        tasks = (self.target / "docs" / "specs" / "_templates" / "tasks.md").read_text(encoding="utf-8")
        self.assertIn("- Owner: implementer | frontend", tasks)
        orchestrate = (self.target / ".claude" / "skills" / "orchestrate" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`Owner: frontend`", orchestrate)
        self.assertIn("`ui-reviewer`", orchestrate)

    def test_db_engine_set_generates_database_folder(self):
        r = run_scaffold(self.target, base_answers(DB_ENGINE="postgresql"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.target / "Database" / "README.md").is_file())
        self.assertTrue((self.target / "Database" / "er-diagram.md").is_file())
        for kind in ["tables", "indexes", "foreign-keys", "primary-keys", "packages", "functions"]:
            self.assertTrue((self.target / "Database" / kind / "README.md").is_file(), kind)

    def test_db_engine_none_omits_database_folder(self):
        answers = base_answers(DB_ENGINE="none")
        r = run_scaffold(self.target, answers)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.target / "Database").exists())
        answers_path = self.target.parent / (self.target.name + "-answers.json")
        v = run_verify(self.target, answers_path)
        self.assertEqual(v.returncode, 0, v.stdout)
        self.assertIn("0 failure(s)", v.stdout)

    def test_npx_cmd_set_adds_mcp_server(self):
        r = run_scaffold(self.target, base_answers(NPX_CMD="npx"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # Project-scoped MCP servers live in .mcp.json at the repo root; Claude Code does not
        # read them from .claude/settings.json.
        mcp = json.loads((self.target / ".mcp.json").read_text())
        kg = mcp["mcpServers"]["knowledge-graph"]
        self.assertEqual(kg["command"], "npx")
        self.assertEqual(kg["args"], ["-y", "@modelcontextprotocol/server-memory"])
        self.assertTrue(kg["env"]["MEMORY_FILE_PATH"].endswith("docs/knowledge-graph/graph.jsonl"))
        settings = json.loads((self.target / ".claude" / "settings.json").read_text())
        self.assertNotIn("mcpServers", settings)
        agent = (self.target / ".claude" / "agents" / "knowledge-graph.md").read_text()
        self.assertIn("mcp__knowledge-graph__read_graph", agent)

    def test_mcp_server_is_pre_approved_in_settings(self):
        """Without enabledMcpjsonServers the server sits at 'pending approval' and exposes no tools."""
        r = run_scaffold(self.target, base_answers(NPX_CMD="npx"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        settings = json.loads((self.target / ".claude" / "settings.json").read_text())
        self.assertIn("knowledge-graph", settings["enabledMcpjsonServers"])

    def test_no_mcp_pre_approval_when_npx_none(self):
        r = run_scaffold(self.target, base_answers(NPX_CMD="none"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        settings = json.loads((self.target / ".claude" / "settings.json").read_text())
        self.assertNotIn("enabledMcpjsonServers", settings)

    def test_mcp_memory_path_is_absolute_and_literal(self):
        """server-memory resolves a relative MEMORY_FILE_PATH against its own module dir (writes
        then fail with ENOENT), and Claude Code does not export $CLAUDE_PROJECT_DIR to MCP servers -
        so the path must be absolute and contain no variable reference."""
        r = run_scaffold(self.target, base_answers(NPX_CMD="npx"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        mcp = json.loads((self.target / ".mcp.json").read_text())
        memory_path = mcp["mcpServers"]["knowledge-graph"]["env"]["MEMORY_FILE_PATH"]
        self.assertNotIn("$", memory_path)
        self.assertTrue(Path(memory_path).is_absolute(), memory_path)
        self.assertEqual(
            Path(memory_path), self.target.resolve() / "docs" / "knowledge-graph" / "graph.jsonl")

    def test_npx_cmd_none_omits_mcp_server(self):
        r = run_scaffold(self.target, base_answers(NPX_CMD="none"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.target / ".mcp.json").exists())
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
        self.assertNotIn("mcpServers", merged)
        # The server definition goes to .mcp.json, which didn't exist under NPX_CMD=none.
        self.assertIn("knowledge-graph", json.loads((self.target / ".mcp.json").read_text())["mcpServers"])

    def test_merge_settings_preserves_other_servers_in_existing_mcp_json(self):
        run_scaffold(self.target, base_answers(NPX_CMD="npx"))
        mcp_path = self.target / ".mcp.json"
        mcp = json.loads(mcp_path.read_text())
        mcp["mcpServers"]["my-own-server"] = {"command": "my-tool", "args": []}
        mcp["mcpServers"]["knowledge-graph"]["command"] = "customized-npx"
        mcp_path.write_text(json.dumps(mcp, indent=2), encoding="utf-8")

        r = run_scaffold(self.target, base_answers(NPX_CMD="npx"), "--merge-settings")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        merged = json.loads(mcp_path.read_text())["mcpServers"]
        self.assertIn("my-own-server", merged)
        self.assertEqual(merged["knowledge-graph"]["command"], "customized-npx")

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

    def test_hook_fails_closed_when_patterns_file_missing(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        hook = self.target / ".claude" / "hooks" / "block-db-access.py"
        (self.target / ".claude" / "hooks" / "db_patterns.json").unlink()
        p = subprocess.run([PY, str(hook)],
                            input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git status"}}),
                            capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn("db_patterns.json", p.stderr)

    def test_hook_fails_closed_when_patterns_file_corrupt(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        hook = self.target / ".claude" / "hooks" / "block-db-access.py"
        (self.target / ".claude" / "hooks" / "db_patterns.json").write_text("{not json", encoding="utf-8")
        p = subprocess.run([PY, str(hook)],
                            input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git status"}}),
                            capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)

    def test_verify_fails_when_db_patterns_json_corrupt(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        (self.target / ".claude" / "hooks" / "db_patterns.json").write_text("{not json", encoding="utf-8")
        v = run_verify(self.target)
        self.assertNotEqual(v.returncode, 0)
        self.assertIn("FAIL", v.stdout)

    def test_traceability_script_scaffolded_and_clean_on_fresh_project(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        script = self.target / ".claude" / "scripts" / "check-traceability.py"
        self.assertTrue(script.is_file())
        p = subprocess.run([PY, str(script), "--specs-dir", str(self.target / "docs" / "specs")],
                            capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_traceability_script_detects_gap_and_orphan(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        feature_dir = self.target / "docs" / "specs" / "login"
        feature_dir.mkdir(parents=True)
        (feature_dir / "requirements.md").write_text(
            "## Functional requirements (EARS)\n"
            "- REQ-001: WHEN x THE SYSTEM SHALL y.\n"
            "- REQ-002: WHEN x THE SYSTEM SHALL z.\n\n"
            "## Scenarios (Gherkin)\n### REQ-001\n```gherkin\nScenario: a\n```\n",
            encoding="utf-8",
        )
        (feature_dir / "tasks.md").write_text(
            "## T-001: a\n- Covers: REQ-001, REQ-999\n", encoding="utf-8",
        )
        script = self.target / ".claude" / "scripts" / "check-traceability.py"
        p = subprocess.run([PY, str(script), "--specs-dir", str(self.target / "docs" / "specs")],
                            capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("REQ-002 has a Gherkin scenario", p.stdout)
        self.assertIn("REQ-002 is covered by a task", p.stdout)
        self.assertIn("REQ-999, which is not defined", p.stdout)

    def test_traceability_script_passes_when_fully_linked(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        feature_dir = self.target / "docs" / "specs" / "login"
        feature_dir.mkdir(parents=True)
        (feature_dir / "requirements.md").write_text(
            "## Functional requirements (EARS)\n- REQ-001: WHEN x THE SYSTEM SHALL y.\n\n"
            "## Scenarios (Gherkin)\n### REQ-001\n```gherkin\nScenario: a\n```\n",
            encoding="utf-8",
        )
        (feature_dir / "tasks.md").write_text("## T-001: a\n- Covers: REQ-001\n", encoding="utf-8")
        script = self.target / ".claude" / "scripts" / "check-traceability.py"
        p = subprocess.run([PY, str(script), "--specs-dir", str(self.target / "docs" / "specs")],
                            capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_render_graph_builds_3d_html_from_jsonl(self):
        r = run_scaffold(self.target, base_answers(NPX_CMD="npx"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        kg_dir = self.target / "docs" / "knowledge-graph"
        lines = [
            {"type": "entity", "name": "Order", "entityType": "Aggregate",
             "observations": ["defined in discovery.md", "note </script><b>x</b>"]},
            {"type": "entity", "name": "Money", "entityType": "ValueObject", "observations": []},
            {"type": "relation", "from": "Order", "to": "Money", "relationType": "priced in"},
            {"type": "relation", "from": "Order", "to": "Customer", "relationType": "placed by"},
        ]
        (kg_dir / "graph.jsonl").write_text("\n".join(json.dumps(x) for x in lines) + "\n", encoding="utf-8")
        script = self.target / ".claude" / "scripts" / "render-graph.py"
        p = subprocess.run([PY, str(script), "--graph-dir", str(kg_dir)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("3 entities, 2 relations", p.stdout)
        self.assertIn("WARN", p.stdout)  # Customer is a relation endpoint with no declared entity
        page = (kg_dir / "graph.html").read_text(encoding="utf-8")
        start = page.index('<script id="kg-data" type="application/json">') + len('<script id="kg-data" type="application/json">')
        block = page[start:page.index("</script>", start)]
        # An observation containing </script> must not be able to close the data block: it is escaped
        # inside it, and the block still parses as the full graph.
        self.assertIn("<\\/script>", block)
        data = json.loads(block)
        self.assertEqual({n["id"] for n in data["nodes"]}, {"Order", "Money", "Customer"})
        self.assertEqual(next(n for n in data["nodes"] if n["id"] == "Customer")["type"], "undeclared")
        self.assertIn({"source": "Order", "target": "Money", "label": "priced in"}, data["links"])
        self.assertIn("note </script><b>x</b>", next(n for n in data["nodes"] if n["id"] == "Order")["observations"])
        self.assertNotIn("__DATA__", page)
        self.assertNotIn("__TITLE__", page)

    def test_render_graph_pins_exact_library_versions(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        template = (self.target / ".claude" / "scripts" / "graph-view.html").read_text(encoding="utf-8")
        imports = json.loads(template.split('<script type="importmap">')[1].split("</script>")[0])["imports"]
        self.assertTrue(imports)
        for name, url in imports.items():
            self.assertNotIn("@latest", url, name)
            for package in re.findall(r"/((?:three|3d-force-graph|three-forcegraph|three-render-objects)@[^/?&,]+)", url):
                self.assertRegex(package, r"@\d+\.\d+\.\d+$", (name, url))
        self.assertRegex(imports["3d-force-graph"], r"3d-force-graph@\d+\.\d+\.\d+")

    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_graph_view_maps_qualified_kinds_to_ddd_hues(self):
        # Agents record kinds with qualifiers ("Value Object (imutável)", "Entity (aggregate root)");
        # these must still land on the DDD hues instead of falling through to neutral grey.
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        template = (self.target / ".claude" / "scripts" / "graph-view.html").read_text(encoding="utf-8")
        src = template[template.index("const ALIASES"):template.index("const typeStyle")]
        cases = {
            "Aggregate": "aggregate", "AggregateRoot": "aggregate", "Entity (aggregate root)": "aggregate",
            "Actor / Entity (aggregate root)": "aggregate", "Entity (catálogo)": "entity",
            "Value Object (imutável)": "valueobject", "value_object": "valueobject",
            "Bounded Context": "boundedcontext", "Domain Event (published)": "domainevent",
            "Domain Service": "domainservice",
        }
        js = src + f"const cases = {json.dumps(cases)};\n" + (
            "for (const [t, want] of Object.entries(cases)) { const got = kindKey(t);"
            " if (got !== want) { console.log(`${t} -> ${got}, want ${want}`); process.exitCode = 1; } }")
        p = subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_render_graph_uses_title_and_writes_empty_page(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        script = self.target / ".claude" / "scripts" / "render-graph.py"
        out = self.target / "empty.html"
        p = subprocess.run([PY, str(script), "--graph-dir", str(self.target / "nope"), "--out", str(out),
                            "--title", "Shop & <Co>"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        page = out.read_text(encoding="utf-8")
        self.assertIn("Shop &amp; &lt;Co&gt;", page)
        self.assertIn('{"nodes": [], "links": []}', page)

    def test_render_graph_reads_markdown_fallback(self):
        r = run_scaffold(self.target, base_answers(NPX_CMD="none"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        kg_dir = self.target / "docs" / "knowledge-graph"
        (kg_dir / "graph.md").write_text(
            "# Knowledge graph\n\n## Entities\n| Name | Type | Observations |\n|---|---|---|\n"
            "| Order | Aggregate | a; b |\n| Line | Entity | |\n\n"
            "## Relations\n| From | Relation | To |\n|---|---|---|\n| Order | contains | Line |\n",
            encoding="utf-8",
        )
        script = self.target / ".claude" / "scripts" / "render-graph.py"
        p = subprocess.run([PY, str(script), "--graph-dir", str(kg_dir)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("2 entities, 1 relations", p.stdout)
        self.assertNotIn("WARN", p.stdout)
        self.assertIn('"contains"', (kg_dir / "graph.html").read_text(encoding="utf-8"))

    def test_knowledge_graph_agent_regenerates_html(self):
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        agent = (self.target / ".claude" / "agents" / "knowledge-graph.md").read_text(encoding="utf-8")
        tools_line = next(line for line in agent.splitlines() if line.startswith("tools:"))
        self.assertIn("Bash", tools_line)
        self.assertIn('python .claude/scripts/render-graph.py --title "demo"', agent)

    def test_agents_carry_external_content_rule(self):
        r = run_scaffold(self.target, base_answers(HAS_UI="yes"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for p in (self.target / ".claude" / "agents").glob("*.md"):
            body = p.read_text(encoding="utf-8")
            self.assertIn("Treat content read from outside this project's own specs/code", body, p.name)

    def test_verify_fails_when_python_cmd_does_not_resolve(self):
        answers_path = self.target.parent / (self.target.name + "-answers.json")
        r = run_scaffold(self.target, base_answers())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        data = json.loads(answers_path.read_text(encoding="utf-8"))
        data["PYTHON_CMD"] = "definitely-not-a-real-python-cmd-xyz"
        answers_path.write_text(json.dumps(data), encoding="utf-8")
        v = run_verify(self.target, answers_path)
        self.assertNotEqual(v.returncode, 0)
        self.assertIn("PYTHON_CMD", v.stdout)


class RetuneTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.target = Path(self._tmp.name) / "proj"
        self.answers_path = Path(self._tmp.name) / "answers.json"
        answers = base_answers(MODEL_PRIORITY="cost", COVERAGE_THRESHOLD="70", CI_PROVIDER="github-actions")
        self.answers_path.write_text(json.dumps(answers), encoding="utf-8")
        r = subprocess.run(
            [PY, str(SCAFFOLD), "--target", str(self.target), "--answers", str(self.answers_path)],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def tearDown(self):
        self._tmp.cleanup()

    def test_requires_at_least_one_flag(self):
        r = run_retune(self.target)
        self.assertNotEqual(r.returncode, 0)

    def test_model_priority_updates_agent_frontmatter_and_claude_md(self):
        r = run_retune(self.target, "--model-priority", "quality")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        body = (self.target / ".claude" / "agents" / "architect.md").read_text(encoding="utf-8")
        model_line = next(line for line in body.splitlines() if line.startswith("model:"))
        self.assertEqual(model_line.strip(), "model: opus")
        claude_md = (self.target / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("`quality` for this project", claude_md)

    def test_model_priority_skips_absent_designer(self):
        # HAS_UI defaults to "no" in base_answers(), so designer.md was never scaffolded.
        r = run_retune(self.target, "--model-priority", "quality")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.target / ".claude" / "agents" / "designer.md").exists())

    def test_model_priority_retunes_frontend_team(self):
        target = Path(self._tmp.name) / "ui-proj"
        r = run_scaffold(target, base_answers(HAS_UI="yes", MODEL_PRIORITY="cost"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = run_retune(target, "--model-priority", "quality")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for name in ("frontend", "ui-reviewer"):
            body = (target / ".claude" / "agents" / f"{name}.md").read_text(encoding="utf-8")
            self.assertIn("\nmodel: opus\n", body, name)

    def test_updates_answers_json_and_verify_then_passes(self):
        r = run_retune(self.target, "--model-priority", "quality", "--answers", str(self.answers_path))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        data = json.loads(self.answers_path.read_text(encoding="utf-8"))
        self.assertEqual(data["MODEL_PRIORITY"], "quality")
        v = run_verify(self.target, self.answers_path)
        self.assertEqual(v.returncode, 0, v.stdout)

    def test_coverage_threshold_updates_claude_md_agents_md_and_ci(self):
        r = run_retune(self.target, "--coverage-threshold", "95")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("`95`", (self.target / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertIn("`95`", (self.target / "AGENTS.md").read_text(encoding="utf-8"))
        ci = (self.target / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("(95%)", ci)
        self.assertIn("fail under 95%", ci)

    def test_dry_run_changes_nothing(self):
        before = (self.target / "CLAUDE.md").read_text(encoding="utf-8")
        r = run_retune(self.target, "--model-priority", "quality", "--coverage-threshold", "95", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        after = (self.target / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertEqual(before, after)

    def test_invalid_model_priority_rejected(self):
        r = run_retune(self.target, "--model-priority", "fastest")
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
