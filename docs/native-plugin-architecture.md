# Mining Market Research: native multi-host architecture

Status: development implementation; real dual-host behavioral acceptance is
required before advertising a certified release. No generated host skill trees.

## One package, two native entries

Both repository marketplaces select `plugins/mining-market-research`. Its Codex and
Claude Code manifests load the same `skills/` and `.mcp.json`. Seven entries share
canonical workflows and policies. Existing shared research documents remain in
`skills/mining-market-research/references` and `workflows`; moving them merely to
rename directories would add migration risk without improving consistency.
Host-only behavior lives in `skills/mining-market-research/references/hosts`, loaded through the global contract.
Everything needed at runtime stays inside the package; no cross-package links.

Brand: Mining Market Research. Technical slug and marketplace IDs remain stable.
Both hosts use product version `0.6.0-dev.11`; platform cache identifiers are
packaging metadata, not different product versions. Existing platform Tag
namespaces remain for upgrade compatibility. Certified releases require both
hosts to pass acceptance against the same commit. The maintainer explicitly
authorized dev.11 as an uncertified development preview on 2026-09-11, accepting
the automatic-trigger and outstanding real-host limitations in its release notes.

## Contract ownership

### Agent-driven updates

Claude Chat has an explicit degraded mode: first plugin use in each new
conversation checks releases; subsequent checks use a six-hour successful-check
TTL in that conversation only. A UUID4 token retained by the agent scopes a
temporary database. Missing/lost session storage may cause a fresh check.
No cross-conversation persistence is claimed. Chat compares the bundled loaded
version, never native installed inventory, and offers manual upload/update plus
a new-session requirement. Codex and Claude Code retain the native flow below.
Chat compatibility is not Claude Code or Cowork certification.

Both hosts natively load `skills/upgrade/SKILL.md` and the same shared upgrade
workflow. Business workflows use `references/update-notifications.md` and
`scripts/update_state.py`; no hooks, daemon, scheduler or MCP proxy is introduced.
The helper reads native installed inventory and stores profile/platform/channel/
scope-isolated state in a private SQLite database outside the versioned cache.
On first use, or first use at least six hours after the last successful check,
the agent performs one fixed Git tag lookup. No update yields no user-facing text.
Failures stay silent, preserve last success, and back off for 30 minutes.
Short transactional leases deduplicate concurrent checks and notice reservations.
No permanent opt-out, skipped release, or seven-day snooze exists: declining or
ignoring a notice preserves the clock, and the next cycle can remind again.

The dedicated Upgrade workflow distinguishes check-only from explicit upgrade
authorization. It rechecks tags, validates the installed source, refreshes the
native marketplace, installs, verifies the installed enabled version, and
requires restarting the session. Discovery can identify a tag after `main`
advances, but installation still fails closed if the native source does not
match the tagged release. No remote-provided commands are executed.

Loaded-session, installed-disk and latest-published versions are distinct.
There is no host delivery callback, so notice acknowledgement is best-effort,
not exactly-once delivery. Sessions predating these instructions require one
restart before they can participate. Real Claude Code execution remains an
acceptance requirement; deterministic tests are not a host certification.

`contracts/hosted-mcp-v1.json` remains the canonical raw descriptor snapshot
inside the existing validated envelope. Do not add a duplicate snapshot just
to rename it. Synchronize from the service; never rewrite its descriptions for
branding. `capabilities.yaml` is JSON-compatible YAML containing tool ownership,
valid example arguments, shared limits and workflow invariants. It is test-time
metadata, not a runtime proxy.

`sync_hosted_contract.py --check` permits additive tools and optional arguments
with review notices. Missing required tools, changed input constraints, output
contracts, security or annotations block automatic acceptance. This is a
conservative compatibility gate, not a full JSON Schema compatibility proof.
New tools are not automatically authorized for use by a workflow.

The current snapshot was obtained without authentication. OAuth scopes for new
tools cannot be inferred from noauth discovery. Authenticated support requires
separate live discovery and acceptance; mock OAuth tests are not certification.

## Development checks

```sh
.venv/bin/python -m unittest discover -s tests -v
python3 plugins/mining-market-research/scripts/sync_plugin_release.py --platform all --check
python3 plugins/mining-market-research/contracts/sync_hosted_contract.py --check
```

The last command performs read-only live discovery. The unit suite's eight
legacy live tests plus the new native-capability smoke test are opt-in.
Loopback mock-server tests need local port access.
Native Skill validators and plugin manifest validation should also run locally.

## Host acceptance matrix (not yet certified)

Run each case in fresh Codex and Claude Code sessions with the same source
commit, product version and deterministic MCP fixture responses. Repeat critical
cases and record host/model versions, input, actual calls and final evidence.

| Case | Required evidence |
|---|---|
| Install and reload | Seven Skills discovered; correct MCP URL and tool schemas |
| Company brief | Identity resolved; brief format; no report-preparation call |
| Company report | Identity, preparation, actual live web sources, dated claims |
| Comparison | All requested entities; no silent report substitution |
| Historical market | Dynamic markets and dates; separate screen/SQL schemas |
| News | Corpus before web; returned article IDs only; at most five article calls |
| CSV | Explicit request; current eligible query; source tool permitted |
| Missing tool / outage | Affected capability disclosed; no fabricated success |
| Web unavailable | Prepared prompt never represented as completed research |
| Ordinary business | Probe each request; remote lookup only when six-hour success cache is due; silent unless actionable |
| Upgrade | Same product version, successful reload, preserved connection |

Normalize exported tool traces for `tests/host_trace_contract.py`: each request
has `task`, `calls` (logical tool, arguments, normalized response evidence),
and flags for requested export/history, release checking and actual web evidence.
The trace validator checks workflow invariants; tests using hand-authored traces
only validate the validator. They do not demonstrate agent behavior. Preserve
the raw run evidence alongside normalized traces; never store credentials or
bearer URLs in committed fixtures.

Release requires local checks plus actual acceptance evidence for both hosts.
Claude Chat/Cowork are outside this certified matrix until independently tested.
Do not upload, publish, or tag automatically during local implementation.

## Migration and rollback

Claude's marketplace source moved from repository root to the shared package.
Refresh its marketplace before upgrading and start a fresh session. For local
testing use `claude --plugin-dir ./plugins/mining-market-research`. Existing cached
root-layout installs will not change until refreshed. Keep prior release refs
available for rollback through the host's supported install workflow; do not
delete user settings or credentials. Codex retains its existing package source.

Architecture references: [Superpowers](https://github.com/obra/superpowers),
[Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin),
[Context Mode](https://github.com/mksglu/context-mode), and
[Trail of Bits Skills](https://github.com/trailofbits/skills).
