from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Sequence
from unittest import mock


sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "mining-market-research"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "mining-market-research"
SCRIPT_ROOT = SKILL_ROOT / "scripts"
CHECKER_PATH = SCRIPT_ROOT / "check_plugin_update.py"
UPDATER_PATH = SCRIPT_ROOT / "update_installed_plugin.py"
SYNC_PATH = PLUGIN_ROOT / "scripts" / "sync_plugin_release.py"
CLAUDE_RELEASE_PATH = SKILL_ROOT / "references" / "plugin-release-claude.json"
CLAUDE_MANIFEST_PATH = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
CLAUDE_MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"
CLAUDE_SKILL_ROOT = SKILL_ROOT
PLUGIN_POLICY_PATH = CLAUDE_SKILL_ROOT / "references" / "plugin-policy.json"
LEGACY_CLAUDE_MANIFEST_PATH = (
    PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
)
CLAUDE_INSTALL_GUIDE = ROOT / "docs" / "anchises-analysis-claude-install.md"


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))
checker = sys.modules.get("check_plugin_update") or _load_module(
    "check_plugin_update",
    CHECKER_PATH,
)
updater = _load_module("anchises_claude_plugin_updater", UPDATER_PATH)
release_sync = _load_module("anchises_claude_release_sync", SYNC_PATH)


PLUGIN_ID = "mining-market-research@anchises-capital"
MARKETPLACE = "anchises-capital"
REPOSITORY = "https://github.com/2026Allin/Mining-Market-Research.git"
GITHUB_REPOSITORY = "2026Allin/Mining-Market-Research"
TAG_PREFIX = "mining-market-research/claude/v"
CURRENT_VERSION = "0.7.0-dev.1"
CURRENT_RELEASE = "0.7.0-dev.1+claude.20260806170037"
TARGET_VERSION = "0.7.0-dev.2"
TARGET_RELEASE = "0.7.0-dev.2+claude.20260808120000"
MAIN_COMMIT = "4" * 40
OTHER_COMMIT = "5" * 40

CLAUDE_LIST = ("claude", "plugin", "list", "--json")
CLAUDE_MARKETPLACE_LIST = (
    "claude",
    "plugin",
    "marketplace",
    "list",
    "--json",
)
CLAUDE_MARKETPLACE_UPDATE = (
    "claude",
    "plugin",
    "marketplace",
    "update",
    MARKETPLACE,
)
CLAUDE_UPDATE = ("claude", "plugin", "update", PLUGIN_ID)


class FakeRunner:
    def __init__(self, results: Sequence[Any]) -> None:
        self.results = list(results)
        self.commands: list[tuple[str, ...]] = []

    def __call__(self, command: Sequence[str]) -> Any:
        self.commands.append(tuple(command))
        if not self.results:
            raise AssertionError("an unexpected extra command was executed")
        return self.results.pop(0)


def _ok(stdout: str = "") -> Any:
    return updater.CommandResult(0, stdout, "")


def _fail(message: str = "denied") -> Any:
    return updater.CommandResult(1, "", message)


def _refs(
    *versions: str,
    main_commit: str = MAIN_COMMIT,
    head_commit: str | None = None,
    include_head: bool = True,
    tag_commit: str | None = None,
    extra: Sequence[str] = (),
) -> str:
    lines = []
    if include_head:
        lines.append(f"{head_commit or main_commit}\tHEAD")
    lines.append(f"{main_commit}\trefs/heads/main")
    for version in versions:
        lines.append(
            f"{tag_commit or main_commit}\trefs/tags/{TAG_PREFIX}{version}"
        )
    lines.extend(extra)
    return "\n".join(lines) + "\n"


def _plugin_list(version: str, *, enabled: bool = True) -> str:
    return json.dumps(
        [
            {
                "id": PLUGIN_ID,
                "version": version,
                "enabled": enabled,
            }
        ]
    )


def _marketplace_list(
    *,
    source: str = "github",
    repo: str = GITHUB_REPOSITORY,
    url: str | None = None,
    ref: str | None = "main",
    include_ref: bool = True,
) -> str:
    entry: dict[str, Any] = {
        "name": MARKETPLACE,
        "source": source,
        "installLocation": "/tmp/claude-marketplace",
    }
    if source == "github":
        entry["repo"] = repo
    if url is not None:
        entry["url"] = url
    if include_ref:
        entry["ref"] = ref
    return json.dumps([entry])


class ClaudeManifestTest(unittest.TestCase):
    def test_claude_loads_the_same_maintainer_policy_as_codex(self) -> None:
        self.assertTrue(PLUGIN_POLICY_PATH.is_file())
        policy = json.loads(PLUGIN_POLICY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            policy,
            {
                "schema_version": 1,
                "market_data": {"restrictions": "disabled"},
            },
        )
        matches = [
            path.resolve()
            for path in ROOT.rglob("plugin-policy.json")
            if ".git" not in path.parts
        ]
        self.assertEqual(matches, [PLUGIN_POLICY_PATH.resolve()])

    def test_both_hosts_load_the_same_self_contained_package(self) -> None:
        marketplace = json.loads(CLAUDE_MARKETPLACE_PATH.read_text())
        entry = marketplace["plugins"][0]
        self.assertEqual((ROOT / entry["source"]).resolve(), PLUGIN_ROOT.resolve())
        claude = json.loads(CLAUDE_MANIFEST_PATH.read_text())
        codex = json.loads((PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text())
        for key in ("name", "description", "author", "skills", "mcpServers"):
            self.assertEqual(claude[key], codex[key])
        self.assertEqual(claude["version"].split("+")[0], codex["version"].split("+")[0])
        self.assertEqual(claude["displayName"], codex["interface"]["displayName"])
        self.assertFalse((ROOT / ".claude-plugin/plugin.json").exists())
        self.assertEqual(len(list((PLUGIN_ROOT / claude["skills"]).glob("*/SKILL.md"))), 7)
        self.assertTrue((PLUGIN_ROOT / claude["mcpServers"]).is_file())

    def test_runtime_markdown_links_remain_inside_the_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "plugin"
            shutil.copytree(PLUGIN_ROOT, package)
            for folder in ("skills", "shared"):
                for source in (package / folder).rglob("*.md"):
                    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", source.read_text()):
                        target = target.split("#", 1)[0]
                        if not target or "://" in target:
                            continue
                        resolved = (source.parent / target).resolve()
                        self.assertTrue(resolved.is_relative_to(package.resolve()), str(source))
                        self.assertTrue(resolved.is_file(), f"{source}: {target}")

    def test_shared_mcp_contract_has_eighteen_tools_and_codex_declarations(self) -> None:
        mcp = json.loads((PLUGIN_ROOT / ".mcp.json").read_text(encoding="utf-8"))
        manifest = json.loads((PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(
            mcp,
            {
                "mcpServers": {
                    "mining_market_research": {
                        "type": "http",
                        "url": "https://mcp.miningmarketresearch.com/mcp",
                        "http_headers": {
                            "X-MMR-Plugin-Version": manifest["version"].split("+", 1)[0],
                            "X-MMR-Plugin-Build": manifest["version"].split("+", 1)[1],
                            "X-MMR-Platform": "codex",
                            "X-MMR-Channel": "dev",
                            "X-MMR-Update-Owner": "client",
                        },
                    }
                }
            },
        )
        contract = json.loads(
            (PLUGIN_ROOT / "contracts" / "hosted-mcp-v1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(len(contract["tools"]), 18)

        release = json.loads(CLAUDE_RELEASE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            set(release),
            {
                "schema_version",
                "name",
                "platform",
                "version",
                "release_id",
                "plugin_id",
                "marketplace",
                "repository",
                "git_ref",
                "tag_prefix",
            },
        )
        self.assertEqual(release["platform"], "claude")
        self.assertEqual(release["plugin_id"], PLUGIN_ID)
        self.assertEqual(release["marketplace"], MARKETPLACE)

    def test_install_guide_covers_github_cli_and_all_claude_surfaces(self) -> None:
        guide = CLAUDE_INSTALL_GUIDE.read_text(encoding="utf-8")
        normalized = " ".join(guide.split())
        for expected in (
            "2026Allin/Mining-Market-Research@main",
            "claude plugin install mining-market-research@anchises-capital",
            "claude --plugin-dir .",
            "Claude Chat",
            "Claude Desktop",
            "Cowork",
            "Claude Code",
            "not certified",
            "mining-market-research/claude/v<semver>",
            "all seven Skills",
            "17 required tools",
        ):
            self.assertIn(expected, normalized)


class ClaudeTagCheckTest(unittest.TestCase):
    def test_claude_namespace_is_separate_and_uses_the_fixed_repository(self) -> None:
        codex_tag = (
            f"{MAIN_COMMIT}\trefs/tags/mining-market-research/codex/v99.0.0"
        )
        result = checker.check_remote_refs(
            _refs(TARGET_VERSION, extra=(codex_tag,)),
            metadata_path=CLAUDE_RELEASE_PATH,
            use_cache=False,
        )
        self.assertEqual(result["status"], "update_available")
        self.assertEqual(result["target_version"], TARGET_VERSION)
        self.assertEqual(result["target_tag"], f"{TAG_PREFIX}{TARGET_VERSION}")
        self.assertEqual(
            checker.release_check_command(CLAUDE_RELEASE_PATH),
            ("git", "ls-remote", "--", REPOSITORY),
        )

    def test_claude_cache_prefers_plugin_data_and_falls_back_safely(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_DATA": tmp}):
                self.assertEqual(
                    checker._default_cache_path("claude"),
                    Path(tmp) / "release-check-cache.json",
                )
            with mock.patch.dict(
                os.environ,
                {"CLAUDE_PLUGIN_DATA": "relative/not-allowed"},
            ):
                fallback = checker._default_cache_path("claude")
                self.assertTrue(fallback.is_absolute())
                self.assertIn("mining-market-research-claude-tags-", fallback.name)
            with mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_DATA": "/"}):
                self.assertNotEqual(
                    checker._default_cache_path("claude"),
                    Path("/release-check-cache.json"),
                )

    def test_claude_success_and_failure_cache_ttls_match_shared_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            success_cache = Path(tmp) / "success.json"
            checker.check_remote_refs(
                _refs(TARGET_VERSION),
                metadata_path=CLAUDE_RELEASE_PATH,
                cache_path=success_cache,
                now=1000,
            )
            self.assertEqual(
                checker.check_cached_result(
                    metadata_path=CLAUDE_RELEASE_PATH,
                    cache_path=success_cache,
                    now=1000 + checker.SUCCESS_CACHE_SECONDS - 1,
                )["status"],
                "update_available",
            )
            self.assertEqual(
                checker.check_cached_result(
                    metadata_path=CLAUDE_RELEASE_PATH,
                    cache_path=success_cache,
                    now=1000 + checker.SUCCESS_CACHE_SECONDS,
                )["status"],
                checker.CHECK_REQUIRED,
            )

            failure_cache = Path(tmp) / "failure.json"
            checker.check_remote_refs(
                "",
                metadata_path=CLAUDE_RELEASE_PATH,
                cache_path=failure_cache,
                now=2000,
            )
            self.assertEqual(
                checker.check_cached_result(
                    metadata_path=CLAUDE_RELEASE_PATH,
                    cache_path=failure_cache,
                    now=2000 + checker.FAILURE_CACHE_SECONDS - 1,
                )["status"],
                "unknown",
            )
            self.assertEqual(
                checker.check_cached_result(
                    metadata_path=CLAUDE_RELEASE_PATH,
                    cache_path=failure_cache,
                    now=2000 + checker.FAILURE_CACHE_SECONDS,
                )["status"],
                checker.CHECK_REQUIRED,
            )

    def test_cli_selects_claude_metadata_without_network(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(CHECKER_PATH),
                "--platform",
                "claude",
                "--remote-refs-stdin",
                "--no-cache",
            ],
            check=False,
            capture_output=True,
            input=_refs(TARGET_VERSION),
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "update_available")
        self.assertEqual(result["installed_version"], CURRENT_VERSION)

    def test_malformed_platform_metadata_fails_closed(self) -> None:
        metadata = json.loads(CLAUDE_RELEASE_PATH.read_text(encoding="utf-8"))
        metadata["platform"] = []
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "release.json"
            path.write_text(json.dumps(metadata), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsupported platform"):
                checker._load_metadata(path)


class ClaudeUpdateTest(unittest.TestCase):
    def _run(self, runner: FakeRunner, *, refs: str | None = None) -> dict[str, Any]:
        return updater.run_update(
            remote_refs=refs or _refs(TARGET_VERSION),
            runner=runner,
            metadata_path=CLAUDE_RELEASE_PATH,
        )

    def test_success_executes_only_the_five_fixed_claude_commands(self) -> None:
        runner = FakeRunner(
            [
                _ok(_plugin_list(CURRENT_RELEASE)),
                _ok(_marketplace_list()),
                _ok(),
                _ok(),
                _ok(_plugin_list(TARGET_RELEASE)),
            ]
        )
        result = self._run(runner)
        self.assertEqual(result["status"], "updated")
        self.assertEqual(result["installed_release"], TARGET_RELEASE)
        self.assertEqual(
            runner.commands,
            [
                CLAUDE_LIST,
                CLAUDE_MARKETPLACE_LIST,
                CLAUDE_MARKETPLACE_UPDATE,
                CLAUDE_UPDATE,
                CLAUDE_LIST,
            ],
        )

    def test_exact_git_url_and_unpinned_matching_head_are_supported(self) -> None:
        for marketplace in (
            _marketplace_list(source="git", url=REPOSITORY),
            _marketplace_list(source="url", url=REPOSITORY),
            _marketplace_list(include_ref=False),
        ):
            with self.subTest(marketplace=marketplace):
                runner = FakeRunner(
                    [
                        _ok(_plugin_list(CURRENT_RELEASE)),
                        _ok(marketplace),
                        _ok(),
                        _ok(),
                        _ok(_plugin_list(TARGET_RELEASE)),
                    ]
                )
                self.assertEqual(self._run(runner)["status"], "updated")

    def test_wrong_source_or_non_main_ref_fails_closed(self) -> None:
        for marketplace in (
            _marketplace_list(repo="other/repository"),
            _marketplace_list(repo="2026Allin/anchises-stock-qa"),
            _marketplace_list(ref="qa-v2-auth"),
            _marketplace_list(source="local"),
        ):
            with self.subTest(marketplace=marketplace):
                runner = FakeRunner(
                    [_ok(_plugin_list(CURRENT_RELEASE)), _ok(marketplace)]
                )
                result = self._run(runner)
                self.assertEqual(result["status"], "unsupported_source")
                self.assertEqual(
                    runner.commands,
                    [CLAUDE_LIST, CLAUDE_MARKETPLACE_LIST],
                )

    def test_failure_stops_without_retry_or_fallback(self) -> None:
        runner = FakeRunner(
            [
                _ok(_plugin_list(CURRENT_RELEASE)),
                _ok(_marketplace_list()),
                _fail(),
            ]
        )
        result = self._run(runner)
        self.assertEqual(result["status"], "upgrade_failed")
        self.assertEqual(result["step"], "marketplace_upgrade")
        self.assertEqual(
            runner.commands,
            [CLAUDE_LIST, CLAUDE_MARKETPLACE_LIST, CLAUDE_MARKETPLACE_UPDATE],
        )

    def test_claude_release_metadata_matches_manifest_and_syncs(self) -> None:
        manifest = json.loads(CLAUDE_MANIFEST_PATH.read_text(encoding="utf-8"))
        release = json.loads(CLAUDE_RELEASE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["version"],
            f"{release['version']}+{release['release_id']}",
        )
        self.assertEqual(release["tag_prefix"], TAG_PREFIX)
        self.assertFalse(
            release_sync.sync_release(check=True, platform="claude")
        )

        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "plugin.json"
            release_path = Path(tmp) / "plugin-release-claude.json"
            manifest_path.write_text(
                json.dumps({"version": TARGET_RELEASE}),
                encoding="utf-8",
            )
            stale = dict(release)
            stale["version"] = "0.6.0-dev.1"
            release_path.write_text(json.dumps(stale), encoding="utf-8")
            self.assertTrue(
                release_sync.sync_release(
                    check=False,
                    manifest_path=manifest_path,
                    release_path=release_path,
                    platform="claude",
                )
            )
            synced = json.loads(release_path.read_text(encoding="utf-8"))
            self.assertEqual(synced["version"], TARGET_VERSION)
            self.assertEqual(synced["release_id"], "claude.20260808120000")


class SharedBundleRegressionTest(unittest.TestCase):
    def test_business_workflows_are_present_in_the_self_contained_core(self) -> None:
        expected_fingerprints = {
            "company-brief.md": "exactly three or four prose sentences",
            "company-comparison.md": "Never silently compare only the first five",
            "company-report.md": "only plugin Skill allowed to call",
            "market-analysis.md": "Complete analysis authorizes necessary cursor",
        }
        workflow_root = CLAUDE_SKILL_ROOT / "workflows"
        for filename, expected in expected_fingerprints.items():
            with self.subTest(filename=filename):
                workflow = (workflow_root / filename).read_text(encoding="utf-8")
                if filename == "company-brief.md":
                    workflow += (CLAUDE_SKILL_ROOT / "references" / "company-introductions.md").read_text(encoding="utf-8")
                self.assertIn(expected, " ".join(workflow.split()))


if __name__ == "__main__":
    unittest.main()
