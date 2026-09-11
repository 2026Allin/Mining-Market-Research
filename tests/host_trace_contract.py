"""Validate normalized, per-request host traces without executing any tools.

Real host adapters/exporters supply logical tool names, arguments and returned
data. Tests of this validator prove the gate, not that an LLM passed the gate.
"""
from jsonschema import Draft202012Validator


def validate_trace(trace, contract):
    tools = {t["name"]: t for t in contract["tools"]}
    errors, seen = [], []
    articles, validated_sql, exportable = set(), set(), set()
    article_calls = 0
    for event in trace["calls"]:
        name, args = event["tool"], event.get("arguments", {})
        if name not in tools:
            errors.append(f"unknown tool: {name}")
            continue
        errors.extend(f"{name}: {e.message}" for e in
                      Draft202012Validator(tools[name]["inputSchema"]).iter_errors(args))
        if name == "get_news_article":
            article_calls += 1
            if args.get("news_code") not in articles:
                errors.append("article must come from preceding cards")
        if name == "prepare_news_web_research" and "search_news" not in seen:
            errors.append("news corpus must precede web preparation")
        if name == "run_readonly_sql" and "sql" in args and args["sql"] not in validated_sql:
            errors.append("SQL must pass validation before execution")
        if name == "create_csv_export" and (
            not trace.get("export_requested") or args.get("query_id") not in exportable
        ):
            errors.append("export requires user request and eligible current query")
        # Normalized evidence is extracted from the actual host tool responses.
        result = event.get("evidence", {})
        if name == "search_news":
            articles.update(result.get("news_codes", []))
        if name == "validate_readonly_sql" and result.get("valid") is True:
            validated_sql.add(args["sql"])
        if name in {"screen_stocks", "run_readonly_sql"}:
            policy = result.get("export_policy", {})
            if policy.get("eligible_by_query") is True and name in policy.get("source_tools_allowed", []):
                query_id = result.get("query_id")
                if query_id:
                    exportable.add(query_id)
        seen.append(name)
    if article_calls > 5:
        errors.append("at most five article calls per user request")
    if seen.count("get_connection_status") > 1:
        errors.append("duplicate service check")
    if trace.get("task") == "news" and "search_news" not in seen and not trace.get("service_unavailable"):
        errors.append("news task requires corpus search")
    if trace.get("historical") and "get_available_dates" not in seen and not trace.get("service_unavailable"):
        errors.append("historical task requires date discovery")
    if trace.get("task") not in {"diagnostics", "plugin_update", "upgrade"} and trace.get("release_check"):
        if trace.get("update_probe_action") != "check_required":
            errors.append("business release lookup requires a due cache probe")
    if trace.get("plugin_install") and not trace.get("explicit_upgrade_authorization"):
        errors.append("installation requires explicit upgrade authorization")
    if trace.get("claims_web_research") and not trace.get("web_evidence"):
        errors.append("prepared prompt is not web research evidence")
    return errors
