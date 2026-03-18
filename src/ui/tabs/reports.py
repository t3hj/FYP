import streamlit as st

from src.services.ai_service import VALID_SEVERITIES
from src.ui.components.report_card import render_report_card
from src.ui.theme import SEVERITY_COLOURS


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

    # Summary statistics
    sev_counts = {sev: 0 for sev in VALID_SEVERITIES}
    for report in reports:
        sev = report.get("severity", "Low")
        if sev in sev_counts:
            sev_counts[sev] += 1

    stat1, stat2, stat3 = st.columns(3)
    with stat1:
        st.metric("Total Reports", len(reports))
    with stat2:
        high_priority = sev_counts.get("Critical", 0) + sev_counts.get("High", 0)
        st.metric("High Priority", high_priority, help="Critical + High severity")
    with stat3:
        categories = {r.get("category", "Unknown") for r in reports}
        st.metric("Categories", len(categories))

    st.divider()

    # Filters
    filter_col1, filter_col2, filter_col3, sort_col = st.columns(4)
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
    with sort_col:
        sort_by = st.selectbox(
            "Sort by",
            ["Most Recent", "Oldest", "Severity (High→Low)", "Severity (Low→High)"],
            help="How to order the reports"
        )

    # Apply filters
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

    # Apply sorting
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    
    if sort_by == "Most Recent":
        filtered = sorted(
            filtered,
            key=lambda r: r.get("upload_date", ""),
            reverse=True
        )
    elif sort_by == "Oldest":
        filtered = sorted(
            filtered,
            key=lambda r: r.get("upload_date", ""),
            reverse=False
        )
    elif sort_by == "Severity (High→Low)":
        filtered = sorted(
            filtered,
            key=lambda r: severity_order.get(r.get("severity", "Low"), 999)
        )
    elif sort_by == "Severity (Low→High)":
        filtered = sorted(
            filtered,
            key=lambda r: severity_order.get(r.get("severity", "Low"), 999),
            reverse=True
        )

    # Show filtered results
    if filtered:
        st.caption(f"Showing {len(filtered)} of {len(reports)} reports")
        
        # Show severity breakdown for filtered results
        if filtered != reports:  # Only if filtering is active
            st.markdown("<div style='margin: 0.5rem 0; font-size: 0.85rem;'>", unsafe_allow_html=True)
            filtered_sev = {sev: 0 for sev in VALID_SEVERITIES}
            for r in filtered:
                sev = r.get("severity", "Low")
                if sev in filtered_sev:
                    filtered_sev[sev] += 1
            
            severity_badges = []
            for sev in VALID_SEVERITIES:
                count = filtered_sev[sev]
                if count > 0:
                    color = SEVERITY_COLOURS.get(sev, "#6b7280")
                    severity_badges.append(
                        f'<span style="display:inline-flex; align-items:center; gap:0.3rem; margin-right:0.8rem; padding:0.3rem 0.6rem; background:{color}15; border-radius:6px; border:1px solid {color}40; font-size:0.85rem;">'
                        f'<span style="width:8px; height:8px; border-radius:50%; background:{color};"></span>{sev} ({count})'
                        f'</span>'
                    )
            
            st.markdown("".join(severity_badges), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        for report in filtered:
            render_report_card(report)
    else:
        st.info("📭 No reports match your filters. Try adjusting your search or filter criteria.")

