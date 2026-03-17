import streamlit as st

from src.services.ai_service import VALID_SEVERITIES
from src.ui.components.report_card import render_report_card


def render_reports_tab(reports: list[dict]) -> None:
    st.subheader("Community Reports")
    if not reports:
        st.markdown(
            """
            <div class="ll-empty-state">
                <div class="ll-empty-emoji">🗂️</div>
                <div class="ll-empty-title">No reports yet</div>
                <div class="ll-empty-subtitle">
                    When residents start submitting reports, they will appear here with
                    AI-assessed severity, categories, and locations.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        search_term = st.text_input("🔍 Search by filename or location", "")
    with filter_col2:
        all_categories = ["All"] + sorted(
            {r.get("category", "Unknown") for r in reports if r.get("category")}
        )
        category_filter = st.selectbox("Category", all_categories)
    with filter_col3:
        all_severities = ["All"] + VALID_SEVERITIES
        severity_filter = st.selectbox("Severity", all_severities)

    filtered = reports
    if search_term.strip():
        term = search_term.lower()
        filtered = [
            r
            for r in filtered
            if term in str(r.get("filename", "")).lower()
            or term in str(r.get("location", "")).lower()
        ]
    if category_filter != "All":
        filtered = [r for r in filtered if r.get("category") == category_filter]
    if severity_filter != "All":
        filtered = [r for r in filtered if r.get("severity") == severity_filter]

    st.caption(f"Showing {len(filtered)} of {len(reports)} reports")

    for report in filtered:
        render_report_card(report)

