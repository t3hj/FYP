import streamlit as st
from src.services.backup_service import BackupService

def main():
    st.title("Backup and Restore Management")
    backup_service = BackupService()

    if st.button("Create Backup"):
        result = backup_service.run_backup()
        if result.get("success"):
            st.success(result.get("message", "Backup created successfully"))
            st.caption(result.get("backup_file", ""))
        else:
            st.error(f"Error creating backup: {result.get('message')}")

    st.subheader("Available Backups")
    backups = backup_service.list_backups()
    if backups:
        st.write(backups)
    else:
        st.info("No backups available yet.")

if __name__ == "__main__":
    main()