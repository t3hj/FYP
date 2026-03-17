import streamlit as st


def render_backup_tab(backup_service, council_password: str) -> None:
    st.subheader("Backup Management")

    if council_password and not st.session_state.get("council_authed", False):
        st.info(
            "Backups are restricted to council staff. "
            "Log in on the Council Insights tab to access this area."
        )
        return

    if st.button("▶️ Run Backup"):
        backup_result = backup_service.run_backup()
        if backup_result["success"]:
            st.success(backup_result.get("message", "Backup completed."))
            st.caption(backup_result.get("backup_file", ""))
        else:
            st.error(f"Backup failed: {backup_result['message']}")

    backups = backup_service.list_backups()
    if backups:
        st.write("Recent backup files:")
        st.write(backups)
    else:
        st.info("No backups yet.")

