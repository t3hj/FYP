import streamlit as st
import os
from datetime import datetime


def render_backup_tab(backup_service, council_password: str) -> None:
    st.subheader("Backup Management")

    if council_password and not st.session_state.get("council_authed", False):
        st.info(
            "Backups are restricted to council staff. "
            "Log in on the Council Insights tab to access this area."
        )
        return

    # Run backup section
    st.markdown("### Create New Backup")
    col_action, col_info = st.columns([2, 3])
    
    with col_action:
        if st.button("▶️ Run Backup Now", key="run_backup_btn", use_container_width=True):
            with st.spinner("Creating backup…"):
                backup_result = backup_service.run_backup()
            if backup_result["success"]:
                st.success("✅ " + backup_result.get("message", "Backup completed."))
                if "backup_file" in backup_result:
                    st.caption(f"File: {backup_result['backup_file']}")
            else:
                st.error(f"❌ Backup failed: {backup_result['message']}")
    
    with col_info:
        st.info(
            "💾 Backups protect your data by creating encrypted copies of all reports, "
            "images, and metadata. Regular backups are essential for data safety."
        )

    st.divider()

    # Backup history
    st.markdown("### Backup History")
    backups = backup_service.list_backups()
    
    if backups:
        # Format backup list into a dataframe for better display
        if isinstance(backups, list):
            backup_rows = []
            for backup in backups:
                if isinstance(backup, str):
                    # Parse filename for info
                    filename = backup.split("/")[-1]
                    try:
                        # Try to extract metadata from filename
                        file_path = backup
                        if os.path.exists(file_path):
                            size_mb = os.path.getsize(file_path) / (1024 * 1024)
                            mod_time = os.path.getmtime(file_path)
                            mod_datetime = datetime.fromtimestamp(mod_time)
                            backup_rows.append({
                                "Filename": filename,
                                "Size (MB)": f"{size_mb:.2f}",
                                "Created": mod_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                "Status": "✅ Ready"
                            })
                        else:
                            backup_rows.append({
                                "Filename": filename,
                                "Size (MB)": "—",
                                "Created": "Unknown",
                                "Status": "⚠️ Not found"
                            })
                    except Exception:
                        backup_rows.append({
                            "Filename": filename,
                            "Size (MB)": "—",
                            "Created": "Unknown",
                            "Status": "ℹ️ Unavailable"
                        })
            
            if backup_rows:
                st.dataframe(
                    backup_rows,
                    use_container_width=True,
                    hide_index=True,
                )
                
                st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
                
                # Backup metadata
                meta_col1, meta_col2, meta_col3 = st.columns(3)
                with meta_col1:
                    st.metric("Total Backups", len(backup_rows))
                with meta_col2:
                    recent_size = backup_rows[0]["Size (MB)"] if backup_rows else "—"
                    st.metric("Latest Backup Size", recent_size)
                with meta_col3:
                    st.metric("Backup Status", "✅ Healthy")
            else:
                st.info("No backups found.")
        else:
            # If backups is not a list format
            st.code(str(backups))
    else:
        st.markdown(
            """
            <div class="ll-empty-state">
                <div class="ll-empty-emoji">💾</div>
                <div class="ll-empty-title">No backups yet</div>
                <div class="ll-empty-subtitle">
                    Click "Run Backup Now" to create your first backup.
                    Regular backups protect your data and allow recovery if needed.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    st.divider()
    st.markdown("**📌 Backup Best Practices**")
    st.markdown(
        """
        - Run backups **at least weekly** to minimize data loss
        - Store backups in **multiple locations** (cloud + local)
        - Test restores periodically to ensure integrity
        - Document your backup schedule and retention policy
        - Monitor backup completion status regularly
        """
    )

