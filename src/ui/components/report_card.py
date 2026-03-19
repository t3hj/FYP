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

    details_text   = str(report.get("additional_details") or report.get("details") or "").strip()
    action_text    = str(report.get("recommended_action") or "").strip()
    description    = details_text  # same field

    # Live upvote count: prefer session-state override (post-vote) over DB value
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
            f"<div class='ll-meta-text' style='margin-top:4px;'>"
            f"🏷️ {html.escape(cat)} &nbsp;|&nbsp; "
            f"📍 {html.escape(loc)} &nbsp;|&nbsp; "
            f"📅 {html.escape(date)}"
            f"</div></div>",
            unsafe_allow_html=True,
        )

        # ── Body ──────────────────────────────────────────────────────────────
        body_col, vote_col = st.columns([5, 1], gap="medium")

        with body_col:
            # Show a short preview of description if present
            if description:
                preview = description if len(description) <= 160 else description[:157] + "…"
                st.write(preview)

            # Full details expander — shows ALL fields
            with st.expander("📋 View full report details"):
                _render_full_details(report, image_url, description, action_text, date, loc, cat, sev, status)

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
    """Renders a rich full-details view inside the expander."""

    title_text  = str(report.get("title") or report.get("filename") or "Untitled").strip()
    reporter    = str(report.get("reporter_id") or "Anonymous").strip()
    assigned    = str(report.get("assigned_to") or "").strip()
    notes       = str(report.get("council_notes") or "").strip()
    lat         = report.get("latitude")
    lon         = report.get("longitude")
    upvotes     = int(report.get("upvotes") or 0)
    filename    = str(report.get("filename") or "").strip()
    updated     = str(report.get("updated_at") or "").split("T")[0] or None
    resolved    = str(report.get("resolved_at") or "").split("T")[0] or None

    border_colour = SEVERITY_COLOURS.get(sev, "#6b7280")
    status_color  = STATUS_COLORS.get(status, "#6b7280")

    left_col, right_col = st.columns([3, 2], gap="large")

    with left_col:
        # Core info table
        st.markdown(
            f"""
            <div style="border-radius:12px;border:1px solid var(--border);
                background:var(--surface-2);padding:1.1rem 1.2rem;margin-bottom:1rem;">
                <div style="display:grid;grid-template-columns:auto 1fr;gap:6px 14px;
                    font-size:0.875rem;">

                    <span style="color:var(--text-muted);font-weight:500;">Category</span>
                    <span style="color:var(--text-primary);font-weight:600;">{html.escape(cat)}</span>

                    <span style="color:var(--text-muted);font-weight:500;">Severity</span>
                    <span>
                        <span style="background:{border_colour}22;color:{border_colour};
                            border:1px solid {border_colour}55;border-radius:999px;
                            padding:2px 9px;font-size:0.75rem;font-weight:700;">
                            {html.escape(sev)}
                        </span>
                    </span>

                    <span style="color:var(--text-muted);font-weight:500;">Status</span>
                    <span>
                        <span style="background:{status_color}22;color:{status_color};
                            border:1px solid {status_color}44;border-radius:999px;
                            padding:2px 9px;font-size:0.75rem;font-weight:700;">
                            {html.escape(status)}
                        </span>
                    </span>

                    <span style="color:var(--text-muted);font-weight:500;">Location</span>
                    <span style="color:var(--text-primary);">📍 {html.escape(loc)}</span>

                    <span style="color:var(--text-muted);font-weight:500;">Reported</span>
                    <span style="color:var(--text-primary);">📅 {html.escape(date)}</span>

                    {"<span style='color:var(--text-muted);font-weight:500;'>Updated</span><span style='color:var(--text-primary);'>" + html.escape(updated) + "</span>" if updated else ""}

                    {"<span style='color:var(--text-muted);font-weight:500;'>Resolved</span><span style='color:var(--text-primary);'>✅ " + html.escape(resolved) + "</span>" if resolved else ""}

                    <span style="color:var(--text-muted);font-weight:500;">Upvotes</span>
                    <span style="color:var(--text-primary);">▲ {upvotes}</span>

                    {"<span style='color:var(--text-muted);font-weight:500;'>Reporter</span><span style='color:var(--text-primary);'>" + html.escape(reporter) + "</span>" if reporter != "Anonymous" else ""}

                    {"<span style='color:var(--text-muted);font-weight:500;'>Assigned to</span><span style='color:var(--text-primary);'>👤 " + html.escape(assigned) + "</span>" if assigned else ""}

                    {"<span style='color:var(--text-muted);font-weight:500;'>Coordinates</span><span style='color:var(--text-primary);font-size:0.82rem;'>" + str(lat) + ", " + str(lon) + "</span>" if lat is not None and lon is not None else ""}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Description
        if description:
            st.markdown(
                '<div style="font-size:0.8rem;font-weight:600;color:var(--text-muted);'
                'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;">'
                'Description</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="border-radius:10px;border:1px solid var(--border);'
                f'background:var(--surface-2);padding:0.9rem 1rem;'
                f'font-size:0.9rem;color:var(--text-primary);line-height:1.65;">'
                f'{html.escape(description)}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.caption("No description provided.")

        # Recommended action
        if action_text:
            st.markdown(
                '<div style="font-size:0.8rem;font-weight:600;color:var(--text-muted);'
                'text-transform:uppercase;letter-spacing:0.06em;margin:12px 0 6px;">'
                'Recommended Action</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="border-radius:10px;border:1px solid rgba(99,102,241,0.25);'
                f'background:rgba(99,102,241,0.06);padding:0.9rem 1rem;'
                f'font-size:0.9rem;color:var(--text-primary);line-height:1.65;">'
                f'💡 {html.escape(action_text)}</div>',
                unsafe_allow_html=True,
            )

        # Council notes (only show if present)
        if notes:
            st.markdown(
                '<div style="font-size:0.8rem;font-weight:600;color:var(--text-muted);'
                'text-transform:uppercase;letter-spacing:0.06em;margin:12px 0 6px;">'
                'Council Notes</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="border-radius:10px;border:1px solid rgba(245,158,11,0.25);'
                f'background:rgba(245,158,11,0.06);padding:0.9rem 1rem;'
                f'font-size:0.9rem;color:var(--text-primary);line-height:1.65;">'
                f'🏛 {html.escape(notes)}</div>',
                unsafe_allow_html=True,
            )

    with right_col:
        # Photo
        if image_url:
            st.markdown(
                '<div style="font-size:0.8rem;font-weight:600;color:var(--text-muted);'
                'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;">'
                'Photo</div>',
                unsafe_allow_html=True,
            )
            try:
                st.image(image_url, use_container_width=True,
                         caption=filename if filename else None)
            except Exception:
                st.caption("Image preview unavailable.")
        else:
            st.markdown(
                '<div style="border-radius:12px;border:1px dashed var(--border);'
                'padding:2rem;text-align:center;color:var(--text-muted);font-size:0.9rem;">'
                '📷 No photo attached</div>',
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

    color = "#6366f1" if user_voted else "var(--text-muted)"

    st.markdown(
        f'<div style="display:flex;flex-direction:column;align-items:center;'
        f'gap:2px;padding-top:4px;text-align:center;">'
        f'<div style="font-size:1.6rem;font-weight:800;color:{color};">{upvotes}</div>'
        f'<div style="font-size:0.7rem;color:var(--text-muted);letter-spacing:0.04em;">VOTES</div>'
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
                # Update vote set
                votes = st.session_state.get("ll_user_votes") or set()
                votes.add(report_id)
                st.session_state.ll_user_votes = votes
                # ── Instantly update local count so UI reflects change ──────
                st.session_state[f"upvote_count_{report_id}"] = upvotes + 1
                st.rerun()
            else:
                st.toast(result.get("message", "Could not upvote."), icon="⚠️")