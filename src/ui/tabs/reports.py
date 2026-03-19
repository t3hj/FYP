import streamlit as st

from src.services.ai_service import VALID_SEVERITIES
from src.services.auth_service import get_user_id
from src.ui.components.report_card import render_report_card
from src.ui.theme import SEVERITY_COLOURS

STATUS_COLORS = {
    "Open":        "#ef4444",
    "In Progress": "#f59e0b",
    "Resolved":    "#22c55e",
    "Won't Fix":   "#6b7280",
}

SEV_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}

PAGE_SIZE = 10


def _normalise_status(raw) -> str:
    s = str(raw).strip() if raw else ""
    return s if s in STATUS_COLORS else "Open"


def render_reports_tab(reports: list[dict], upload_service=None) -> None:

    if not reports:
        st.markdown(
            """<div class="ll-empty-state">
            <div class="ll-empty-emoji">🗂️</div>
            <div class="ll-empty-title">No reports yet on Local Lens</div>
            <div class="ll-empty-subtitle">
                Be the first to report a community issue.<br>
                Head to the <strong>Report an Issue</strong> tab to get started.
            </div></div>""",
            unsafe_allow_html=True,
        )
        return

    # Load which reports the current user has voted on (once per session)
    user_id = get_user_id()
    if user_id and upload_service and st.session_state.get("ll_user_votes") is None:
        voted = upload_service.get_user_votes(user_id)
        st.session_state.ll_user_votes = set(voted)

    # ── Summary strip ─────────────────────────────────────────────────────────
    total     = len(reports)
    high      = sum(1 for r in reports if r.get("severity") in ("Critical", "High"))
    open_c    = sum(1 for r in reports if _normalise_status(r.get("status")) == "Open")
    resolved  = sum(1 for r in reports if _normalise_status(r.get("status")) == "Resolved")
    top_votes = max((int(r.get("upvotes") or 0) for r in reports), default=0)

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("Total", total)
    with m2: st.metric("🚨 High Priority", high)
    with m3: st.metric("🔄 Open", open_c)
    with m4: st.metric("✅ Resolved", resolved)
    with m5: st.metric("▲ Top Votes", top_votes)

    st.divider()

    # ── Filters ───────────────────────────────────────────────────────────────
    f1, f2, f3, f4, f5 = st.columns([2, 2, 2, 2, 2])
    with f1:
        search = st.text_input("🔍 Search", "", placeholder="Title, location…",
                               label_visibility="collapsed")
    with f2:
        all_cats = ["All categories"] + sorted(
            {r.get("category", "Unknown") for r in reports if r.get("category")}
        )
        cat_filter = st.selectbox("Category", all_cats, label_visibility="collapsed")
    with f3:
        sev_filter = st.selectbox(
            "Severity", ["All severities"] + VALID_SEVERITIES,
            label_visibility="collapsed",
        )
    with f4:
        present_statuses = sorted({_normalise_status(r.get("status")) for r in reports})
        status_filter = st.selectbox(
            "Status", ["All statuses"] + present_statuses,
            label_visibility="collapsed",
        )
    with f5:
        sort_by = st.selectbox(
            "Sort",
            ["Most Upvoted", "Most Recent", "Oldest", "Severity ↓", "Severity ↑"],
            label_visibility="collapsed",
        )

    # ── Apply filters ─────────────────────────────────────────────────────────
    filtered = reports
    if search.strip():
        t = search.lower()
        filtered = [
            r for r in filtered
            if t in str(r.get("title", "")).lower()
            or t in str(r.get("location", "")).lower()
            or t in str(r.get("category", "")).lower()
        ]
    if cat_filter != "All categories":
        filtered = [r for r in filtered if r.get("category") == cat_filter]
    if sev_filter != "All severities":
        filtered = [r for r in filtered if r.get("severity") == sev_filter]
    if status_filter != "All statuses":
        filtered = [r for r in filtered
                    if _normalise_status(r.get("status")) == status_filter]

    # ── Sort ──────────────────────────────────────────────────────────────────
    if sort_by == "Most Upvoted":
        filtered = sorted(filtered, key=lambda r: int(r.get("upvotes") or 0), reverse=True)
    elif sort_by == "Most Recent":
        filtered = sorted(filtered, key=lambda r: r.get("upload_date", ""), reverse=True)
    elif sort_by == "Oldest":
        filtered = sorted(filtered, key=lambda r: r.get("upload_date", ""))
    elif sort_by == "Severity ↓":
        filtered = sorted(filtered, key=lambda r: SEV_ORDER.get(r.get("severity", "Low"), 9))
    elif sort_by == "Severity ↑":
        filtered = sorted(filtered,
                          key=lambda r: SEV_ORDER.get(r.get("severity", "Low"), 9),
                          reverse=True)

    if not filtered:
        st.info("📭 No reports match your filters. Try adjusting the search or dropdowns above.")
        return

    # ── Pagination — reset to page 0 whenever filters/sort change ─────────────
    filter_sig = f"{search}|{cat_filter}|{sev_filter}|{status_filter}|{sort_by}"
    if st.session_state.get("reports_filter_sig") != filter_sig:
        st.session_state.reports_filter_sig = filter_sig
        st.session_state.reports_page = 0

    total_filtered = len(filtered)
    total_pages    = max((total_filtered + PAGE_SIZE - 1) // PAGE_SIZE, 1)
    page           = int(st.session_state.get("reports_page", 0))
    page           = max(0, min(page, total_pages - 1))   # clamp after filter changes

    page_start = page * PAGE_SIZE
    page_end   = min(page_start + PAGE_SIZE, total_filtered)
    page_items = filtered[page_start:page_end]

    # ── Results header ────────────────────────────────────────────────────────
    res_col, chip_col = st.columns([2, 3])
    with res_col:
        st.caption(
            f"Showing {page_start + 1}–{page_end} of {total_filtered} report"
            f"{'s' if total_filtered != 1 else ''}"
            + (f" (page {page + 1} of {total_pages})" if total_pages > 1 else "")
        )
    with chip_col:
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
                    f'<span style="display:inline-flex;align-items:center;gap:4px;'
                    f'margin-right:6px;padding:2px 9px;border-radius:8px;'
                    f'background:{c}15;border:1px solid {c}40;font-size:0.78rem;'
                    f'font-weight:600;">'
                    f'<span style="width:6px;height:6px;border-radius:50%;background:{c};"></span>'
                    f'{sev} {fs[sev]}</span>'
                )
        if chips:
            st.markdown("".join(chips), unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Report cards ──────────────────────────────────────────────────────────
    for report in page_items:
        render_report_card(report, upload_service=upload_service, user_id=user_id)

    # ── Pagination controls ───────────────────────────────────────────────────
    if total_pages > 1:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.divider()

        prev_col, info_col, next_col = st.columns([1, 2, 1])

        with prev_col:
            if st.button(
                "← Previous",
                key="reports_prev",
                use_container_width=True,
                disabled=(page == 0),
            ):
                st.session_state.reports_page = page - 1
                st.rerun()

        with info_col:
            st.markdown(
                f"<div style='text-align:center;padding:6px 0;"
                f"font-size:0.85rem;color:#94a3b8;'>"
                f"Page <strong style='color:#f1f5f9;'>{page + 1}</strong>"
                f" of {total_pages}"
                f"</div>",
                unsafe_allow_html=True,
            )

        with next_col:
            if st.button(
                "Next →",
                key="reports_next",
                use_container_width=True,
                disabled=(page >= total_pages - 1),
            ):
                st.session_state.reports_page = page + 1
                st.rerun()