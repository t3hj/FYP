import streamlit as st

from src.services.ai_service import VALID_SEVERITIES
from src.services.auth_service import get_user_id
from src.ui.components.report_card import render_report_card
from src.ui.theme import SEVERITY_COLOURS


def render_reports_tab(reports: list[dict], upload_service=None) -> None:
    st.subheader("Community Reports")

    if not reports:
        st.markdown(
            """<div class="ll-empty-state">
            <div class="ll-empty-emoji">🗂️</div>
            <div class="ll-empty-title">No reports yet</div>
            <div class="ll-empty-subtitle">
                Be the first to report an issue in your area on Local Lens.
            </div></div>""",
            unsafe_allow_html=True,
        )
        return

    # Load which reports the current user has voted on (once per session)
    user_id = get_user_id()
    if user_id and upload_service and st.session_state.get("ll_user_votes") is None:
        voted = upload_service.get_user_votes(user_id)
        st.session_state.ll_user_votes = set(voted)

    # ── Summary ───────────────────────────────────────────────────────────────
    sev_counts = {sev: 0 for sev in VALID_SEVERITIES}
    for r in reports:
        sev = r.get("severity", "Low")
        if sev in sev_counts:
            sev_counts[sev] += 1

    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric("Total Reports", len(reports))
    with s2:
        high = sev_counts.get("Critical", 0) + sev_counts.get("High", 0)
        st.metric("🚨 High Priority", high)
    with s3:
        cats = len({r.get("category", "Unknown") for r in reports})
        st.metric("🏷️ Categories", cats)

    st.divider()

    # ── Filters ───────────────────────────────────────────────────────────────
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        search_term = st.text_input("🔍 Search", "", placeholder="Title or location…")
    with f2:
        all_cats = ["All"] + sorted(
            {r.get("category", "Unknown") for r in reports if r.get("category")}
        )
        cat_filter = st.selectbox("Category", all_cats)
    with f3:
        sev_filter = st.selectbox("Severity", ["All"] + VALID_SEVERITIES)
    with f4:
        sort_by = st.selectbox(
            "Sort by",
            ["Most Upvoted", "Most Recent", "Oldest", "Severity (High→Low)"],
        )

    filtered = reports
    if search_term.strip():
        t = search_term.lower()
        filtered = [
            r for r in filtered
            if t in str(r.get("title", "")).lower()
            or t in str(r.get("location", "")).lower()
        ]
    if cat_filter != "All":
        filtered = [r for r in filtered if r.get("category") == cat_filter]
    if sev_filter != "All":
        filtered = [r for r in filtered if r.get("severity") == sev_filter]

    sev_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    if sort_by == "Most Upvoted":
        filtered = sorted(filtered, key=lambda r: int(r.get("upvotes") or 0), reverse=True)
    elif sort_by == "Most Recent":
        filtered = sorted(filtered, key=lambda r: r.get("upload_date", ""), reverse=True)
    elif sort_by == "Oldest":
        filtered = sorted(filtered, key=lambda r: r.get("upload_date", ""))
    elif sort_by == "Severity (High→Low)":
        filtered = sorted(filtered, key=lambda r: sev_order.get(r.get("severity", "Low"), 999))

    if not filtered:
        st.info("📭 No reports match your filters.")
        return

    st.caption(f"Showing {len(filtered)} of {len(reports)} Local Lens reports")

    # Severity breakdown chips when filtering
    if len(filtered) != len(reports):
        chips = []
        fs = {s: 0 for s in VALID_SEVERITIES}
        for r in filtered:
            s = r.get("severity", "Low")
            if s in fs:
                fs[s] += 1
        for sev in VALID_SEVERITIES:
            if fs[sev]:
                c = SEVERITY_COLOURS[sev]
                chips.append(
                    f'<span style="display:inline-flex;align-items:center;gap:5px;'
                    f'margin-right:8px;padding:3px 10px;border-radius:8px;'
                    f'background:{c}15;border:1px solid {c}40;font-size:0.82rem;">'
                    f'<span style="width:7px;height:7px;border-radius:50%;background:{c};"></span>'
                    f'{sev} ({fs[sev]})</span>'
                )
        if chips:
            st.markdown("".join(chips), unsafe_allow_html=True)

    for report in filtered:
        render_report_card(report, upload_service=upload_service, user_id=user_id)