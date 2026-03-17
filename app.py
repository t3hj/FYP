import streamlit as st

from config.settings import ENABLE_OLLAMA, REQUIRE_AI, REQUIRE_GEOLOCATION, COUNCIL_ADMIN_PASSWORD
from src.services.ai_service import VALID_CATEGORIES, VALID_SEVERITIES
from src.services.backup_service import BackupService
from src.services.upload_service import UploadService
from src.ui.theme import init_theme, set_theme, apply_theme_css, SEVERITY_COLOURS, severity_badge
from src.ui.components.hero import render_hero, render_onboarding_steps
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

    if REQUIRE_AI:
        if ENABLE_OLLAMA:
            st.success("✅ AI mode active — every report is automatically analysed by Ollama.")
        else:
            st.error(
                "⚠️ AI-required mode is ON but Ollama is disabled. "
                "Set ENABLE_OLLAMA = true in your secrets."
            )
    if REQUIRE_GEOLOCATION:
        st.info("📍 Geolocation required — reports must include valid coordinates.")

    upload_service = UploadService()
    backup_service = BackupService()
    reports = upload_service.list_uploaded_images()

    for key in ("pending_upload", "analyzed_file_id", "council_authed"):
        if key not in st.session_state:
            st.session_state[key] = None if key != "council_authed" else False

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Total Reports", len(reports))
    with col_b:
        by_category = {}
        for r in reports:
            cat = r.get("category", "Unknown")
            by_category[cat] = by_category.get(cat, 0) + 1
        top_category = max(by_category, key=by_category.get) if by_category else "-"
        st.metric("Top Category", top_category)
    with col_c:
        latest = reports[0].get("upload_date", "-") if reports else "-"
        if latest and latest != "-":
            latest = str(latest)[:10]
        st.metric("Latest Report", latest)

    st.divider()

    tab_upload, tab_reports, tab_map, tab_insights, tab_backup = st.tabs(
        ["📤 Report an Issue", "📋 View Reports", "🗺️ Map", "🏛 Council Insights", "💾 Backup"]
    )

    # ── TAB 1: Report an Issue ────────────────────────────────────────────────
    with tab_upload:
        render_upload_tab(
            upload_service,
            enable_ollama=ENABLE_OLLAMA,
            require_ai=REQUIRE_AI,
            valid_categories=VALID_CATEGORIES,
            valid_severities=VALID_SEVERITIES,
        )

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
