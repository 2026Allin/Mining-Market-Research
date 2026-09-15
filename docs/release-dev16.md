# Mining Market Research 0.6.0-dev.16 (preview)

- Keep one Claude package for Web Chat, App Chat and App Code. Select maintenance
  and installation paths by observed capabilities, not the product label.
- Generate the five business Skill entry checklists from one shared template to
  reduce cross-file omissions. Skill loading is still host-dependent.
- Add shared routing and capability diagnostics for SessionStart, PreToolUse,
  PostToolUse, UserPromptSubmit, PreCompact and Stop. Registered definitions do
  not prove that a host executed or consumed them.
- Default notification delivery to attempt-only without matching current-turn
  native Hook evidence. Do not equate a reminder attempt with confirmed delivery.
- Disable assistant full-response review on all hosts before reading input.
  Native confirmation uses bounded host evidence; no conversation upload,
  automatic installation or server-side update takeover is enabled.
- Resolve upgrade capability when upgrading. Do not install a CLI to enable the
  updater, assume an Update button exists, or claim installation from a check.
- Keep maintenance permission failures non-blocking for business requests.

Validation: 326 automated tests, 316 passed and 10 skipped; generated entries,
Hook configuration, release metadata and plugin structure validated. New Hook
and delivery behavior has synthetic coverage, not cross-host certification.

After upgrading, start a new session and review changed Hook definitions where
the host supports them. Chat/MCP-only hosts may bypass Skills; the package does
not guarantee automatic checks in those hosts. Explicit installation consent and
host network permissions remain required. This is a development prerelease.
