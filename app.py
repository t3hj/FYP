import streamlit as st

from config.settings import ENABLE_OLLAMA, REQUIRE_AI, REQUIRE_GEOLOCATION, COUNCIL_ADMIN_PASSWORD
from src.services.ai_service import VALID_CATEGORIES, VALID_SEVERITIES
from src.services.backup_service import BackupService
from src.services.upload_service import UploadService
from src.ui.theme import init_theme, apply_theme_css
from src.ui.components.hero import render_hero, render_onboarding_steps, render_overview_cards
from src.ui.tabs.reports import render_reports_tab
from src.ui.tabs.map import render_map_tab
from src.ui.tabs.insights import render_insights_tab
from src.ui.tabs.backup import render_backup_tab
from src.ui.tabs.upload import render_upload_tab


def main():
    st.set_page_config(page_title="Local Lens", page_icon="📸", layout="wide")

    active_theme = init_theme()
    apply_theme_css(active_theme)

    render_hero(active_theme)
    render_onboarding_steps()

    if REQUIRE_GEOLOCATION:
        st.info("📍 Geolocation required — reports must include valid coordinates.")

    upload_service = UploadService()
    backup_service = BackupService()
    reports = upload_service.list_uploaded_images()

    for key in ("pending_upload", "analyzed_file_id", "council_authed", "show_quick_upload", "active_tab", 
                "show_duplicate_warning", "nearby_duplicate_reports", "pending_report_data", "confirmed_despite_duplicates"):
        if key not in st.session_state:
            if key == "council_authed":
                st.session_state[key] = False
            else:
                st.session_state[key] = None

    by_category = {}
    for report in reports:
        category = report.get("category", "Unknown")
        by_category[category] = by_category.get(category, 0) + 1

    top_category = max(by_category, key=by_category.get) if by_category else "-"
    latest = reports[0].get("upload_date", "-") if reports else "-"
    if latest and latest != "-":
        latest = str(latest)[:10]
    render_overview_cards(len(reports), str(top_category), str(latest))

    # Show quick upload expander if button was clicked
    if st.session_state.get("show_quick_upload"):
        with st.expander("📸 Quick Upload Form", expanded=True):
            st.markdown("<h3 style='margin-top: 0;'>Ready to report an issue?</h3>", unsafe_allow_html=True)
            render_upload_tab(
                upload_service,
                enable_ollama=ENABLE_OLLAMA,
                require_ai=REQUIRE_AI,
                valid_categories=VALID_CATEGORIES,
                valid_severities=VALID_SEVERITIES,
            )
        st.divider()

    tab_upload, tab_reports, tab_map, tab_insights, tab_backup = st.tabs(
        ["📤 Report an Issue", "📋 View Reports", "🗺️ Map", "🏛 Council Insights", "💾 Backup"]
    )

    # ── TAB 1: Report an Issue ────────────────────────────────────────────────
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
            st.info("📤 Use the form above to submit your report, or continue to the next tabs to view your submissions.")

    # ── TAB 2: View Reports ────────────────────────────────────────────────────
    with tab_reports:
        render_reports_tab(reports)

    # ── TAB 3: Map ─────────────────────────────────────────────────────────────
    with tab_map:
        render_map_tab(reports)
    # ── TAB 4: Council Insights ────────────────────────────────────────────────
    with tab_insights:
        render_insights_tab(reports, COUNCIL_ADMIN_PASSWORD)

    # ── TAB 5: Backup ──────────────────────────────────────────────────────────
    with tab_backup:
        render_backup_tab(backup_service, COUNCIL_ADMIN_PASSWORD)


if __name__ == "__main__":
    main()
