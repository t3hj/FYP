import pandas as pd
import streamlit as st


def render_insights_tab(reports: list[dict], council_password: str) -> None:
    st.subheader("Council Insights")

    if not council_password:
        st.warning(
            "Council analytics password is not configured. "
            "Set `COUNCIL_ADMIN_PASSWORD` in `.streamlit/secrets.toml` to protect this view."
        )

    if not st.session_state.get("council_authed", False) and council_password:
        st.info("This area is reserved for council staff.")
        password = st.text_input("Council admin password", type="password", key="council_password")
        if st.button("Log in", key="council_login_button"):
            if password == council_password:
                st.session_state["council_authed"] = True
                st.success("Logged in as council.")
            else:
                st.error("Incorrect password.")

    if not (st.session_state.get("council_authed", False) or not council_password):
        return

    if not reports:
        st.markdown(
            """
            <div class="ll-empty-state">
                <div class="ll-empty-emoji">📊</div>
                <div class="ll-empty-title">Analytics will appear here</div>
                <div class="ll-empty-subtitle">
                    Once residents start submitting reports, you will see breakdowns
                    by category, severity, and trends over time.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    df = pd.DataFrame(reports)
    if "upload_date" in df.columns:
        df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Reports by Category**")
        cat_counts = (
            df["category"]
            .fillna("Unknown")
            .value_counts()
            .rename_axis("Category")
            .reset_index(name="Reports")
        )
        st.bar_chart(cat_counts.set_index("Category"))

    with col2:
        st.markdown("**Reports by Severity**")
        if "severity" in df.columns:
            sev_counts = (
                df["severity"]
                .fillna("Medium")
                .value_counts()
                .rename_axis("Severity")
                .reset_index(name="Reports")
            )
            st.bar_chart(sev_counts.set_index("Severity"))

    st.markdown("---")
    st.markdown("**Reports Over Time**")
    if "upload_date" in df.columns and df["upload_date"].notna().any():
        time_series = (
            df.dropna(subset=["upload_date"])
            .groupby(df["upload_date"].dt.date)
            .size()
            .rename("Reports")
            .reset_index()
            .rename(columns={"upload_date": "Date"})
        )
        st.line_chart(time_series.set_index("Date"))
    else:
        st.caption("Report dates are not available yet for time-based analytics.")

