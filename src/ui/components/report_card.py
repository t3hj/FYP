import html

import streamlit as st

from src.ui.theme import SEVERITY_COLOURS, severity_badge


def render_report_card(report: dict, upload_service=None, user_id: str | None = None) -> None:
    sev = report.get("severity", "Medium")
    badge = severity_badge(sev)
    title_text = str(report.get("title") or report.get("filename") or "Untitled").strip()
    cat = str(report.get("category") or "Unknown").strip()
    loc = str(report.get("location") or "Unknown location").strip()
    date = str(report.get("upload_date", "")).split("T")[0] or "Unknown date"
    details_text = str(report.get("additional_details") or report.get("details") or "").strip()
    action_text = str(report.get("recommended_action") or "").strip()
    image_url = report.get("cloud_storage_url") or report.get("image_path")
    report_id = str(report.get("id", ""))
    upvotes = int(report.get("upvotes") or 0)
    status = report.get("status", "Open")

    STATUS_COLORS = {
        "Open": "#ef4444",
        "In Progress": "#f59e0b",
        "Resolved": "#22c55e",
        "Won't Fix": "#6b7280",
    }
    status_color = STATUS_COLORS.get(status, "#6b7280")

    preview = details_text
    if len(preview) > 160:
        preview = preview[:157].rstrip() + "…"

    border_colour = SEVERITY_COLOURS.get(sev, "#6b7280")

    # Has this user already upvoted?
    user_voted = report_id in (st.session_state.get("ll_user_votes") or set())

    with st.container(border=True):
        st.markdown(
            f"<div style='border-left:4px solid {border_colour};padding-left:12px;'>"
            f"<div style='display:flex;align-items:center;gap:8px;flex-wrap:wrap;'>"
            f"<span style='font-weight:700;font-size:0.97rem;'>{html.escape(title_text)}</span>"
            f"{badge}"
            f"<span style='display:inline-flex;align-items:center;gap:4px;"
            f"padding:2px 8px;border-radius:999px;font-size:0.72rem;font-weight:600;"
            f"background:{status_color}22;color:{status_color};border:1px solid {status_color}44;'>"
            f"{html.escape(status)}</span>"
            f"</div>"
            f"<div class='ll-meta-text' style='margin-top:4px;'>"
            f"🏷️ {html.escape(cat)} &nbsp;|&nbsp; "
            f"📍 {html.escape(loc)} &nbsp;|&nbsp; "
            f"📅 {html.escape(date)}"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        body_col, vote_col, img_col = st.columns([3, 1, 1], gap="medium")

        with body_col:
            if preview:
                st.write(preview)
            with st.expander("View full details"):
                if details_text:
                    st.write(details_text)
                else:
                    st.caption("No additional details provided.")
                if action_text:
                    st.markdown("**Recommended action**")
                    st.write(action_text)

        with vote_col:
            _render_upvote_button(
                report_id=report_id,
                upvotes=upvotes,
                user_voted=user_voted,
                user_id=user_id,
                upload_service=upload_service,
            )

        with img_col:
            if image_url:
                try:
                    st.image(image_url, use_container_width=True)
                except Exception:
                    st.caption("Image unavailable.")


def _render_upvote_button(
    report_id: str,
    upvotes: int,
    user_voted: bool,
    user_id: str | None,
    upload_service,
) -> None:
    from src.services.auth_service import is_logged_in

    arrow = "▲"
    voted_style = (
        "background:rgba(99,102,241,0.18);color:#818cf8;"
        "border:1px solid rgba(99,102,241,0.5);"
    )
    default_style = (
        "background:var(--surface-2);color:var(--text-secondary);"
        "border:1px solid var(--border);"
    )
    style = voted_style if user_voted else default_style

    st.markdown(
        f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px;'
        f'padding-top:6px;">'
        f'<div style="font-size:1.5rem;font-weight:800;color:var(--text-primary);">'
        f'{upvotes}</div>'
        f'<div style="font-size:0.72rem;color:var(--text-muted);">upvotes</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    btn_label = f"{arrow} Upvoted" if user_voted else f"{arrow} Upvote"
    btn_key = f"upvote_{report_id}"

    if not is_logged_in():
        if st.button(f"{arrow} Upvote", key=btn_key, use_container_width=True,
                     help="Log in to upvote"):
            st.session_state.ll_auth_modal = "login"
            st.rerun()
        st.caption("Login to vote")
        return

    if st.button(
        btn_label,
        key=btn_key,
        use_container_width=True,
        disabled=user_voted,
        help="You've already upvoted this" if user_voted else "Upvote to signal urgency",
    ):
        if upload_service and user_id:
            result = upload_service.add_vote(report_id, user_id)
            if result.get("success"):
                votes = st.session_state.get("ll_user_votes") or set()
                votes.add(report_id)
                st.session_state.ll_user_votes = votes
                st.rerun()
            else:
                st.toast(result.get("message", "Could not upvote."), icon="⚠️")