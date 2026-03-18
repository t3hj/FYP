import streamlit as st

from src.ui.theme import set_theme


def render_hero(active_theme: str) -> None:
     with st.container():
        st.markdown(
            """
            <div class="ll-hero-card">
                <div class="ll-hero-chip">✦ AI-Powered Reporting</div>
                <div class="ll-hero-title">Turn snapshots into council-ready reports</div>
                <p class="ll-hero-subtitle">
                    Upload an image, let AI analyse it, and submit the issue in under a minute.
                    Every report is structured with category, severity, and suggested action.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        if st.button(
            "🚀 Start a new report",
            key="hero_start_report_btn",
            use_container_width=True,
            help="Upload and analyze an image right now"
        ):
            st.session_state.show_quick_upload = True
            st.session_state.active_tab = "upload"
            st.rerun()
        
        st.markdown(
            '<p class="ll-helper-text">or scroll down to use the tabs below</p>',
            unsafe_allow_html=True,
        )

    


def render_onboarding_steps() -> None:
    steps = [
        ("1", "Upload an image", "Drop a quick photo of a street, park, or public space issue."),
        ("2", "AI analyses it", "Our AI organises a title, severity, category, and recommended action."),
        ("3", "Submit to council", "Review the auto-filled form, edit if needed, then submit your report."),
    ]
    columns = st.columns(3, gap="large")
    for col, (number, title, description) in zip(columns, steps):
        with col:
            st.markdown(
                f"""
                <div class="ll-step-card">
                    <div class="ll-step-badge">{number}</div>
                    <div class="ll-step-title">{title}</div>
                    <div class="ll-helper-text">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_overview_cards(total_reports: int, top_category: str, latest_report: str) -> None:
    from html import escape
    cards = [
        ("Total Reports", str(total_reports), "+12%" if total_reports else "-"),
        ("Top Category", top_category or "-", "Most common" if top_category and top_category != "-" else "-"),
        ("Latest Report", latest_report or "-", "Today" if latest_report and latest_report != "-" else "-"),
    ]
    columns = st.columns(3, gap="large")
    for col, (label, value, hint) in zip(columns, cards):
        with col:
            safe_label = escape(label)
            safe_value = escape(value)
            safe_hint = escape(hint)
            st.markdown(
                f"""
                <div class="ll-kpi-card">
                    <div class="ll-kpi-label">{safe_label}</div>
                    <div class="ll-kpi-value">{safe_value}</div>
                    <div class="ll-kpi-hint">{safe_hint}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

