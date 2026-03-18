import streamlit as st

from config.settings import ENABLE_OLLAMA, REQUIRE_AI, REQUIRE_GEOLOCATION, COUNCIL_ADMIN_PASSWORD
from src.services.ai_service import VALID_CATEGORIES, VALID_SEVERITIES
from src.services.auth_service import init_auth_state, is_logged_in, get_user_display_name
from src.services.backup_service import BackupService
from src.services.upload_service import UploadService
from src.ui.theme import init_theme, apply_theme_css
from src.ui.components.hero import render_hero, render_onboarding_steps, render_overview_cards
from src.ui.components.auth import render_auth_modal, render_auth_widget
from src.ui.tabs.reports import render_reports_tab
from src.ui.tabs.map import render_map_tab
from src.ui.tabs.insights import render_insights_tab
from src.ui.tabs.backup import render_backup_tab
from src.ui.tabs.upload import render_upload_tab


def main():
    st.set_page_config(
        page_title="Local Lens",
        page_icon="📸",
        layout="wide",
        menu_items={
            "About": "**Local Lens** — AI-powered community issue reporting. "
                     "Turn quick snapshots into council-ready reports.",
        },
    )

    active_theme = init_theme()
    apply_theme_css(active_theme)

    # Initialise auth state
    init_auth_state()
    if "ll_auth_modal" not in st.session_state:
        st.session_state.ll_auth_modal = None

    # ── Navbar ────────────────────────────────────────────────────────────────
    nav_left, nav_right = st.columns([5, 2])
    with nav_left:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:10px;padding:4px 0;">'
            '<span style="font-size:1.4rem;">📸</span>'
            '<span style="font-size:1.15rem;font-weight:800;letter-spacing:-0.02em;'
            'color:var(--text-primary);">Local Lens</span>'
            '<span style="font-size:0.75rem;font-weight:600;padding:2px 8px;'
            'border-radius:999px;background:rgba(99,102,241,0.15);'
            'color:#818cf8;margin-left:4px;">Beta</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    with nav_right:
        auth_col, theme_col = st.columns([3, 1])
        with auth_col:
            render_auth_widget()
        with theme_col:
            is_dark = active_theme == "dark"
            from src.ui.theme import set_theme
            new_dark = st.toggle("🌙", value=is_dark, key="ll_theme_toggle",
                                 help="Toggle dark / light mode")
            if new_dark != is_dark:
                set_theme("dark" if new_dark else "light")
                st.rerun()

    # ── Auth modal (renders if triggered) ────────────────────────────────────
    render_auth_modal()

    # ── Hero + steps ──────────────────────────────────────────────────────────
    render_hero(active_theme)
    render_onboarding_steps()

    if REQUIRE_GEOLOCATION:
        st.info("📍 Geolocation required — reports must include valid coordinates.")

    # ── Services ──────────────────────────────────────────────────────────────
    upload_service = UploadService()
    backup_service = BackupService()
    reports = upload_service.list_uploaded_images()

    # ── Session state defaults ────────────────────────────────────────────────
    defaults = {
        "pending_upload": None,
        "analyzed_file_id": None,
        "council_authed": False,
        "show_quick_upload": None,
        "active_tab": None,
        "show_duplicate_warning": None,
        "nearby_duplicate_reports": None,
        "pending_report_data": None,
        "confirmed_despite_duplicates": None,
        "map_picked_lat": None,
        "map_picked_lon": None,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # ── Overview cards ────────────────────────────────────────────────────────
    by_cat = {}
    for r in reports:
        c = r.get("category", "Unknown")
        by_cat[c] = by_cat.get(c, 0) + 1
    top_cat = max(by_cat, key=by_cat.get) if by_cat else "-"
    latest = str(reports[0].get("upload_date", "-") if reports else "-")[:10]
    render_overview_cards(len(reports), str(top_cat), latest)

    # Quick upload expander (triggered from hero CTA)
    if st.session_state.get("show_quick_upload"):
        with st.expander("📸 Quick Upload — Report an Issue", expanded=True):
            render_upload_tab(
                upload_service,
                enable_ollama=ENABLE_OLLAMA,
                require_ai=REQUIRE_AI,
                valid_categories=VALID_CATEGORIES,
                valid_severities=VALID_SEVERITIES,
            )
        st.divider()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_upload, tab_reports, tab_map, tab_insights, tab_backup = st.tabs([
        "📤 Report an Issue",
        "📋 View Reports",
        "🗺️ Map",
        "🏛 Council Insights",
        "💾 Backup",
    ])

    with tab_upload:
        if not st.session_state.get("show_quick_upload"):
            render_upload_tab(
                upload_service,
                enable_ollama=ENABLE_OLLAMA,
                require_ai=REQUIRE_AI,
                valid_categories=VALID_CATEGORIES,
                valid_severities=VALID_SEVERITIES,
            )
        else:
            st.info("📤 Use the form above to submit your report.")

    with tab_reports:
        render_reports_tab(reports, upload_service=upload_service)

    with tab_map:
        render_map_tab(reports)

    with tab_insights:
        render_insights_tab(reports, COUNCIL_ADMIN_PASSWORD, upload_service)

    with tab_backup:
        render_backup_tab(backup_service, COUNCIL_ADMIN_PASSWORD)


if __name__ == "__main__":
    main()