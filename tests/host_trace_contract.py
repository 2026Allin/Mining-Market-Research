"""Validate normalized, per-request host traces without executing any tools.

Real host adapters/exporters supply logical tool names, arguments and returned
data. Tests of this validator prove the gate, not that an LLM passed the gate.
"""
from jsonschema import Draft202012Validator


def validate_trace(trace, contract):
    tools = {t["name"]: t for t in contract["tools"]}
    errors, seen = [], []
    articles, validated_sql, exportable = set(), set(), set()
    cursors, last_rowset = {}, None
    export_succeeded = False
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
        if name in {"screen_stocks", "run_readonly_sql"} and "cursor" in args:
            size = "page_size" if name == "screen_stocks" else "max_rows"
            if set(args) - {"cursor", size}:
                errors.append("continuation must not resend query arguments")
            if args["cursor"] != cursors.get(name):
                errors.append("continuation requires the preceding same-tool cursor")
        if event.get("purpose") == "completeness_audit":
            errors.append("no unsolicited database completeness audit")
        if name == "create_csv_export" and result.get("download_url"):
            export_succeeded = True
        if name == "search_news":
            articles.update(result.get("news_codes", []))
        if name == "validate_readonly_sql" and result.get("valid") is True:
            validated_sql.add(args["sql"])
        if name in {"screen_stocks", "run_readonly_sql"}:
            cursors[name] = result.get("page", {}).get("next_cursor")
            if "page" in result:
                last_rowset = result
            policy = result.get("export_policy", {})
            if policy.get("eligible_by_query") is True and name in policy.get("source_tools_allowed", []):
                query_id = result.get("query_id")
                if query_id:
                    exportable.add(query_id)
        seen.append(name)
    if last_rowset:
        page, analysis = last_rowset["page"], last_rowset.get("analysis", {})
        incomplete = bool(page.get("next_cursor") or page.get("truncated")
                          or analysis.get("pagination_limit_reached"))
        if trace.get("claims_complete") and incomplete:
            errors.append("cannot claim complete analysis of a partial query")
        if (trace.get("claimed_total") is not None and incomplete
                and analysis.get("matched_row_count") is None):
            errors.append("unknown total must not be replaced by displayed rows")
    if trace.get("claims_export_success") and not export_succeeded:
        errors.append("export eligibility is not export success")
    if article_calls > 5:
        errors.append("at most five article calls per user request")
    if seen.count("get_connection_status") > 1:
        errors.append("duplicate service check")
    if trace.get("task") == "news" and "search_news" not in seen and not trace.get("service_unavailable"):
        errors.append("news task requires corpus search")
    if trace.get("trading_date_selection") and "get_available_dates" not in seen and not trace.get("service_unavailable"):
        errors.append("historical task requires date discovery")
    if trace.get("task") not in {"diagnostics", "plugin_update", "upgrade"} and trace.get("release_check"):
        if trace.get("update_probe_action") != "check_required":
            errors.append("business release lookup requires a due cache probe")
    if trace.get("plugin_install") and not trace.get("explicit_upgrade_authorization"):
        errors.append("installation requires explicit upgrade authorization")
    if trace.get("claims_web_research") and not trace.get("web_evidence"):
        errors.append("prepared prompt is not web research evidence")
    return errors
