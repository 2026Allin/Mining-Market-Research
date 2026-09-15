from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = (
    ROOT / "plugins" / "mining-market-research" / "skills" / "mining-market-research"
)
OAUTH_PLAN = ROOT / "docs" / "hosted-mcp-oauth-migration-plan.md"


class ReleaseRepositoryHygieneTest(unittest.TestCase):
    def test_readme_tracks_latest_release_and_branding(self) -> None:
        plugin = ROOT / "plugins" / "mining-market-research"
        manifest = json.loads((plugin / ".codex-plugin/plugin.json").read_text())
        claude = json.loads((plugin / ".claude-plugin/plugin.json").read_text())
        version = manifest["version"].split("+", 1)[0]
        self.assertEqual(claude["version"].split("+", 1)[0], version)
        name = manifest["interface"]["displayName"]
        logo = Path(manifest["interface"]["logo"])
        self.assertTrue((plugin / logo).is_file())
        readme = (ROOT / "README.md").read_text()
        package_readme = (plugin / "README.md").read_text()
        for text, logo_path in (
            (readme, (plugin / logo).relative_to(ROOT).as_posix()),
            (package_readme, logo.as_posix()),
        ):
            self.assertEqual(text.splitlines()[0], f"# {name}")
            self.assertIn(f'src="{logo_path}"', text)
            self.assertIn(f'alt="{name} logo"', text)
        self.assertIn(f"Development preview: `{version}`", readme)
        self.assertIn(f"Product version: `{version}`", package_readme)
        self.assertEqual(
            re.findall(r"^## What changed[^\n]*", readme, re.MULTILINE),
            [f"## What changed in {version}"],
        )
        repository = manifest["repository"]
        self.assertIn(f"{repository}/releases/tag/mining-market-research/codex/v{version}", readme)
        self.assertIn(
            f"{repository}/releases/download/mining-market-research/claude/v{version}/"
            f"mining-market-research-{version}-claude.zip", readme,
        )
        notes = re.search(r"\[Latest release notes\]\(([^)]+)\)", readme)
        self.assertIsNotNone(notes)
        note_path = ROOT / notes.group(1)
        self.assertTrue(note_path.is_file())
        self.assertIn(version, note_path.read_text().splitlines()[0])

    def test_company_report_workflow_is_required_by_the_skill(self) -> None:
        workflow = SKILL_ROOT / "workflows" / "company-report.md"
        self.assertTrue(workflow.is_file())

        skill = (
            SKILL_ROOT.parent / "company-report" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("../mining-market-research/workflows/company-report.md", skill)

    def test_generated_output_directories_are_ignored(self) -> None:
        rules = {
            line.strip()
            for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        self.assertTrue({"output/", "outputs/"}.issubset(rules))

    def test_only_docs_oauth_plan_is_kept(self) -> None:
        self.assertTrue(OAUTH_PLAN.is_file())
        self.assertFalse((ROOT / "hosted-mcp-oauth-migration-plan.md").exists())

    def test_oauth_plan_is_explicitly_historical(self) -> None:
        preface = OAUTH_PLAN.read_text(encoding="utf-8")[:1600]
        for marker in (
            "历史架构记录和未来 OAuth",
            "`public_noauth`",
            "用户无需",
            "历史方案 / 未来 OAuth 规划",
            "不得复制到当前 Plugin Directory",
            "Hosted MCP 0.6.0",
            "stock-data-export-v1",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, preface)

    def test_current_release_surfaces_do_not_require_login(self) -> None:
        release_surfaces = (
            ROOT / "README.md",
            ROOT / "plugins" / "mining-market-research" / "README.md",
            ROOT
            / "plugins"
            / "mining-market-research"
            / ".codex-plugin"
            / "plugin.json",
            ROOT / "docs" / "anchises-analysis-0.4.0-beta.2-release-notes.md",
        )
        forbidden_phrases = (
            "approved-access beta",
            "reviewer oauth account",
            "pending entitlement",
            "users must log in",
            "user must log in",
            "用户必须登录",
        )

        for path in release_surfaces:
            text = path.read_text(encoding="utf-8").lower()
            for phrase in forbidden_phrases:
                with self.subTest(path=path.relative_to(ROOT), phrase=phrase):
                    self.assertNotIn(phrase, text)

    def test_tracked_files_exclude_generated_release_artifacts(self) -> None:
        if not (ROOT / ".git").exists():
            self.skipTest("Git metadata is unavailable")

        completed = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        forbidden: list[str] = []
        for relative in completed.stdout.splitlines():
            path = PurePosixPath(relative)
            if not path.parts:
                continue
            if path.parts[0] in {"output", "outputs"}:
                forbidden.append(relative)
                continue
            if "__pycache__" in path.parts:
                forbidden.append(relative)
                continue
            if path.suffix.lower() in {".csv", ".pdf", ".pyc"}:
                forbidden.append(relative)
                continue
            if path.name == ".env":
                forbidden.append(relative)

        self.assertEqual(forbidden, [])


if __name__ == "__main__":
    unittest.main()
