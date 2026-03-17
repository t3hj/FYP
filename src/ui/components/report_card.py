import html

import streamlit as st

from src.ui.theme import SEVERITY_COLOURS, severity_badge


def render_report_card(report: dict) -> None:
    sev = report.get("severity", "Medium")
    badge = severity_badge(sev)
    title_text = str(report.get("title") or report.get("filename") or "Untitled").strip()
    cat = str(report.get("category") or "Unknown").strip()
    loc = str(report.get("location") or "Unknown location").strip()
    date = str(report.get("upload_date", "")).split("T")[0] or "Unknown date"
    details_text = str(report.get("additional_details") or report.get("details") or "").strip()
    action_text = str(report.get("recommended_action") or "").strip()
    image_url = report.get("cloud_storage_url") or report.get("image_path")

    preview = details_text
    if len(preview) > 160:
        preview = preview[:157].rstrip() + "…"

    border_colour = SEVERITY_COLOURS.get(sev, "#6b7280")

    with st.container(border=True):
        st.markdown(
            f"<div style='border-left:4px solid {border_colour}; padding-left:12px;'>"
            f"<div style='display:flex; align-items:center; gap:8px;'>"
            f"<span style='font-weight:650;'>{html.escape(title_text)}</span>"
            f"{badge}"
            f"</div>"
            f"<div class='ll-meta-text'>🏷️ {html.escape(cat)} &nbsp;|&nbsp; 📍 {html.escape(loc)} &nbsp;|&nbsp; 📅 {html.escape(date)}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        body_col, img_col = st.columns([3, 1], gap="large")
        with body_col:
            if preview:
                st.write(preview)
            with st.expander("View full details"):
                if details_text:
                    st.write(details_text)
                else:
                    st.caption("No additional details were provided for this report.")
                if action_text:
                    st.markdown("**Recommended action**")
                    st.write(action_text)
        with img_col:
            if image_url:
                try:
                    st.image(image_url, use_container_width=True)
                except Exception:
                    st.caption("Image preview unavailable.")

