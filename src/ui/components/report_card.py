import html

import streamlit as st

from src.ui.theme import SEVERITY_COLOURS, severity_badge

STATUS_COLORS = {
    "Open": "#ef4444",
    "In Progress": "#f59e0b",
    "Resolved": "#22c55e",
    "Won't Fix": "#6b7280",
}


def _normalise_status(raw) -> str:
    s = str(raw).strip() if raw else ""
    return s if s in STATUS_COLORS else "Open"


def render_report_card(
    report: dict,
    upload_service=None,
    user_id: str | None = None,
) -> None:
    report_id = str(report.get("id", ""))
    sev        = report.get("severity", "Medium")
    title_text = str(report.get("title") or report.get("filename") or "Untitled").strip()
    cat        = str(report.get("category") or "Unknown").strip()
    loc        = str(report.get("location") or "Unknown location").strip()
    date       = str(report.get("upload_date", "")).split("T")[0] or "—"
    status     = _normalise_status(report.get("status"))
    image_url  = report.get("cloud_storage_url") or report.get("image_path")

    details_text = str(report.get("additional_details") or report.get("details") or "").strip()
    action_text  = str(report.get("recommended_action") or "").strip()

    override_key = f"upvote_count_{report_id}"
    upvotes = st.session_state.get(override_key, int(report.get("upvotes") or 0))
    user_voted = report_id in (st.session_state.get("ll_user_votes") or set())

    border_colour = SEVERITY_COLOURS.get(sev, "#6b7280")
    status_color  = STATUS_COLORS.get(status, "#6b7280")

    with st.container(border=True):
        # ── Header row ────────────────────────────────────────────────────────
        st.markdown(
            f"<div style='border-left:4px solid {border_colour};padding-left:12px;'>"
            f"<div style='display:flex;align-items:center;gap:8px;flex-wrap:wrap;'>"
            f"<span style='font-weight:700;font-size:0.97rem;'>{html.escape(title_text)}</span>"
            f"{severity_badge(sev)}"
            f"<span style='display:inline-flex;align-items:center;gap:4px;"
            f"padding:2px 8px;border-radius:999px;font-size:0.72rem;font-weight:600;"
            f"background:{status_color}22;color:{status_color};border:1px solid {status_color}44;'>"
            f"{html.escape(status)}</span>"
            f"</div>"
            f"<div style='font-size:0.8rem;color:#94a3b8;margin-top:4px;'>"
            f"🏷️ {html.escape(cat)} &nbsp;|&nbsp; "
            f"📍 {html.escape(loc)} &nbsp;|&nbsp; "
            f"📅 {html.escape(date)}"
            f"</div></div>",
            unsafe_allow_html=True,
        )

        # ── Body ──────────────────────────────────────────────────────────────
        body_col, vote_col = st.columns([5, 1], gap="medium")

        with body_col:
            if details_text:
                preview = details_text if len(details_text) <= 160 else details_text[:157] + "…"
                st.write(preview)

            with st.expander("📋 View full report details"):
                _render_full_details(report, image_url, details_text, action_text, date, loc, cat, sev, status)

        with vote_col:
            _render_upvote_button(
                report_id=report_id,
                upvotes=upvotes,
                user_voted=user_voted,
                user_id=user_id,
                upload_service=upload_service,
            )


def _render_full_details(
    report: dict,
    image_url: str | None,
    description: str,
    action_text: str,
    date: str,
    loc: str,
    cat: str,
    sev: str,
    status: str,
) -> None:
    """Renders a rich full-details view using native Streamlit components."""

    assigned  = str(report.get("assigned_to") or "").strip()
    notes     = str(report.get("council_notes") or "").strip()
    lat       = report.get("latitude")
    lon       = report.get("longitude")
    upvotes   = int(report.get("upvotes") or 0)
    filename  = str(report.get("filename") or "").strip()
    updated   = str(report.get("updated_at") or "").split("T")[0] or None
    resolved  = str(report.get("resolved_at") or "").split("T")[0] or None
    reporter  = str(report.get("reporter_id") or "").strip()

    border_colour = SEVERITY_COLOURS.get(sev, "#6b7280")
    status_color  = STATUS_COLORS.get(status, "#6b7280")

    left_col, right_col = st.columns([3, 2], gap="large")

    with left_col:
        # ── Key facts using st.columns pairs ─────────────────────────────────
        st.markdown("##### Report Info")

        def _row(label: str, value: str, icon: str = ""):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(
                    f"<span style='font-size:0.82rem;color:#94a3b8;font-weight:500;'>{label}</span>",
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f"<span style='font-size:0.88rem;font-weight:600;'>{icon} {html.escape(value)}</span>",
                    unsafe_allow_html=True,
                )

        # Severity badge
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(
                "<span style='font-size:0.82rem;color:#94a3b8;font-weight:500;'>Severity</span>",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"<span style='background:{border_colour}22;color:{border_colour};"
                f"border:1px solid {border_colour}55;border-radius:999px;"
                f"padding:2px 9px;font-size:0.78rem;font-weight:700;'>{html.escape(sev)}</span>",
                unsafe_allow_html=True,
            )

        # Status badge
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(
                "<span style='font-size:0.82rem;color:#94a3b8;font-weight:500;'>Status</span>",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"<span style='background:{status_color}22;color:{status_color};"
                f"border:1px solid {status_color}44;border-radius:999px;"
                f"padding:2px 9px;font-size:0.78rem;font-weight:700;'>{html.escape(status)}</span>",
                unsafe_allow_html=True,
            )

        _row("Category", cat, "🏷️")
        _row("Location", loc, "📍")
        _row("Reported", date, "📅")

        if updated:
            _row("Updated", updated, "🔄")
        if resolved:
            _row("Resolved", resolved, "✅")

        _row("Upvotes", str(upvotes), "▲")

        if reporter:
            _row("Reporter", reporter, "👤")
        if assigned:
            _row("Assigned to", assigned, "👤")
        if lat is not None and lon is not None:
            _row("Coordinates", f"{lat}, {lon}", "🌐")

        st.divider()

        # ── Description ───────────────────────────────────────────────────────
        if description:
            st.markdown("**Description**")
            st.info(description)
        else:
            st.caption("No description provided.")

        # ── Recommended action ────────────────────────────────────────────────
        if action_text:
            st.markdown("**Recommended Action**")
            st.success(f"💡 {action_text}")

        # ── Council notes ─────────────────────────────────────────────────────
        if notes:
            st.markdown("**Council Notes**")
            st.warning(f"🏛 {notes}")

    with right_col:
        st.markdown("**Photo**")
        if image_url:
            try:
                st.image(image_url, use_container_width=True,
                         caption=filename if filename else None)
            except Exception:
                st.caption("Image preview unavailable.")
        else:
            st.markdown(
                "<div style='border-radius:12px;border:2px dashed #334155;"
                "padding:2rem;text-align:center;color:#64748b;font-size:0.9rem;'>"
                "📷 No photo attached</div>",
                unsafe_allow_html=True,
            )


def _render_upvote_button(
    report_id: str,
    upvotes: int,
    user_voted: bool,
    user_id: str | None,
    upload_service,
) -> None:
    from src.services.auth_service import is_logged_in

    color = "#6366f1" if user_voted else "#94a3b8"

    st.markdown(
        f'<div style="display:flex;flex-direction:column;align-items:center;'
        f'gap:2px;padding-top:4px;text-align:center;">'
        f'<div style="font-size:1.6rem;font-weight:800;color:{color};">{upvotes}</div>'
        f'<div style="font-size:0.7rem;color:#94a3b8;letter-spacing:0.04em;">VOTES</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    btn_label = "▲ Upvoted" if user_voted else "▲ Upvote"
    btn_key   = f"upvote_{report_id}"

    if not is_logged_in():
        if st.button("▲ Vote", key=btn_key, use_container_width=True,
                     help="Log in to upvote"):
            st.session_state.ll_auth_modal = "login"
            st.session_state.ll_scroll_to_modal = True
            st.rerun()
        st.caption("Login\nto vote")
        return

    if st.button(
        btn_label,
        key=btn_key,
        use_container_width=True,
        disabled=user_voted,
        help="Already upvoted" if user_voted else "Upvote to signal urgency",
    ):
        if upload_service and user_id:
            result = upload_service.add_vote(report_id, user_id)
            if result.get("success"):
                votes = st.session_state.get("ll_user_votes") or set()
                votes.add(report_id)
                st.session_state.ll_user_votes = votes
                st.session_state[f"upvote_count_{report_id}"] = upvotes + 1
                st.rerun()
            else:
                st.toast(result.get("message", "Could not upvote."), icon="⚠️")