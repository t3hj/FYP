import pandas as pd
import streamlit as st
from datetime import datetime, timedelta


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

    # Date range filter
    col_filter1, col_filter2 = st.columns(2)
    today = datetime.now()
    with col_filter1:
        date_start = st.date_input(
            "From date",
            value=today - timedelta(days=90),
            key="insights_date_start"
        )
    with col_filter2:
        date_end = st.date_input(
            "To date",
            value=today,
            key="insights_date_end"
        )

    # Filter by date range
    mask = (df["upload_date"].dt.date >= date_start) & (df["upload_date"].dt.date <= date_end)
    filtered_df = df[mask] if "upload_date" in df.columns else df

    # Key metrics
    st.divider()
    metric1, metric2, metric3, metric4 = st.columns(4)
    with metric1:
        st.metric("📋 Total Reports", len(filtered_df))
    with metric2:
        critical_high = 0
        if "severity" in filtered_df.columns:
            critical_high = len(filtered_df[filtered_df["severity"].isin(["Critical", "High"])])
        st.metric("🚨 High Priority", critical_high, help="Critical + High severity")
    with metric3:
        avg_per_day = len(filtered_df) / max((date_end - date_start).days + 1, 1)
        st.metric("📈 Reports/Day", f"{avg_per_day:.1f}")
    with metric4:
        categories = filtered_df["category"].nunique() if "category" in filtered_df.columns else 0
        st.metric("🏷️ Categories", categories)

    st.divider()

    # Reports over time (create early for trend analysis)
    time_series = None
    if "upload_date" in filtered_df.columns and filtered_df["upload_date"].notna().any():
        time_series = (
            filtered_df.dropna(subset=["upload_date"])
            .groupby(filtered_df["upload_date"].dt.date)
            .size()
            .rename("Reports")
            .reset_index()
            .rename(columns={"upload_date": "Date"})
        )

    # Top issues
    top_col, sev_col = st.columns(2)
    with top_col:
        st.markdown("**🔥 Top 5 Issue Categories**")
        if not filtered_df.empty and "category" in filtered_df.columns:
            cat_counts = (
                filtered_df["category"]
                .fillna("Unknown")
                .value_counts()
                .head(5)
            )
            if not cat_counts.empty:
                st.bar_chart(cat_counts)
            else:
                st.caption("No category data available")
        else:
            st.caption("No data for this period")

    with sev_col:
        st.markdown("**⚠️ Severity Breakdown**")
        if not filtered_df.empty and "severity" in filtered_df.columns:
            sev_counts = filtered_df["severity"].value_counts()
            if not sev_counts.empty:
                st.bar_chart(sev_counts)
            else:
                st.caption("No severity data available")
        else:
            st.caption("No severity data available")

    st.divider()

    # Reports over time (display)
    st.markdown("**📅 Reports Over Time**")
    if time_series is not None:
        st.line_chart(time_series.set_index("Date"))
    else:
        st.caption("No time-based data for this period")

    st.divider()

    # Insights box
    st.markdown("**💡 Key Insights**")
    insights = []
    
    if not filtered_df.empty:
        # Most reported category
        if "category" in filtered_df.columns:
            top_cat = filtered_df["category"].value_counts().index[0] if not filtered_df["category"].value_counts().empty else "Unknown"
            top_cat_count = filtered_df["category"].value_counts().values[0]
            insights.append(f"🏆 **{top_cat}** is the top reported issue ({top_cat_count} reports)")
        
        # Critical/high severity
        if "severity" in filtered_df.columns:
            critical_count = len(filtered_df[filtered_df["severity"] == "Critical"])
            if critical_count > 0:
                insights.append(f"🔴 **{critical_count} critical** issues require immediate attention")
        
        # Trend
        if time_series is not None and len(time_series) > 1:
            recent_avg = time_series.iloc[-7:]["Reports"].mean()
            previous_avg = time_series.iloc[-14:-7]["Reports"].mean() if len(time_series) > 7 else recent_avg
            trend = "📈 increasing" if recent_avg > previous_avg else "📉 decreasing"
            insights.append(f"Trend is {trend}")
        
        for insight in insights:
            st.markdown(f"- {insight}")
    else:
        st.info("No reports in selected date range")

