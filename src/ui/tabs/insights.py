import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, timezone

from src.services.priority_service import score_reports

REPORT_STATUSES = ["Open", "In Progress", "Resolved", "Won't Fix"]

STATUS_COLORS = {
    "Open":        "#ef4444",
    "In Progress": "#f97316",
    "Resolved":    "#22c55e",
    "Won't Fix":   "#6b7280",
}

_BAND_ORDER = {
    "Critical Priority": 0,
    "High Priority":     1,
    "Medium Priority":   2,
    "Low Priority":      3,
}


def render_insights_tab(reports: list[dict], council_password: str, upload_service=None) -> None:
    st.subheader("Council Dashboard")

    if not council_password:
        st.warning(
            "No admin password configured. "
            "Set `COUNCIL_ADMIN_PASSWORD` in `.streamlit/secrets.toml`."
        )

    if not st.session_state.get("council_authed", False) and council_password:
        st.info("This area is reserved for council staff.")
        password = st.text_input("Admin password", type="password", key="council_password")
        if st.button("Log in", key="council_login_button"):
            if password == council_password:
                st.session_state["council_authed"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        return

    if not reports:
        st.markdown(
            """<div class="ll-empty-state"><div class="ll-empty-emoji">📊</div>
            <div class="ll-empty-title">No data yet</div>
            <div class="ll-empty-subtitle">Analytics appear once reports are submitted.</div>
            </div>""",
            unsafe_allow_html=True,
        )
        return

    tab_priority, tab_analytics, tab_manage = st.tabs([
        "🎯 Priority Queue",
        "📊 Analytics",
        "🛠️ Manage Reports",
    ])

    with tab_priority:
        _render_priority_queue(reports, upload_service)

    with tab_analytics:
        _render_analytics(reports)

    with tab_manage:
        _render_manage(reports, upload_service)


# ── Priority Queue ────────────────────────────────────────────────────────────

def _render_priority_queue(reports: list[dict], upload_service) -> None:
    st.markdown("#### AI Priority Scoring")
    st.caption(
        "Each report is scored 0–100 using four signals: "
        "**AI severity** (up to 40 pts) · "
        "**Time open** (up to 25 pts) · "
        "**Community upvotes** (up to 20 pts) · "
        "**Local report density** (up to 15 pts)"
    )

    # ── Controls ──────────────────────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        include_resolved = st.toggle(
            "Include resolved reports", value=False, key="pq_include_resolved"
        )
    with fc2:
        band_filter = st.selectbox(
            "Band filter",
            ["All", "Critical Priority", "High Priority", "Medium Priority", "Low Priority"],
            key="pq_band_filter",
            label_visibility="collapsed",
        )
    with fc3:
        top_n = st.selectbox(
            "Show top",
            [10, 25, 50, 100],
            key="pq_top_n",
            label_visibility="collapsed",
            format_func=lambda x: f"Top {x} reports",
        )

    # ── Score all reports ──────────────────────────────────────────────────────
    with st.spinner("Calculating priority scores…"):
        scored = score_reports(reports)

    # Filter out resolved/won't-fix unless toggled
    if not include_resolved:
        scored = [
            r for r in scored
            if str(r.get("status") or "Open").strip() not in ("Resolved", "Won't Fix")
        ]

    if band_filter != "All":
        scored = [r for r in scored if r["_priority_band"] == band_filter]

    scored = scored[:top_n]

    if not scored:
        st.info("No reports match the selected filters.")
        return

    # ── Band summary chips ────────────────────────────────────────────────────
    band_counts: dict[str, int] = {}
    for r in score_reports(reports):
        b = r["_priority_band"]
        band_counts[b] = band_counts.get(b, 0) + 1

    band_colours = {
        "Critical Priority": "#7c3aed",
        "High Priority":     "#ef4444",
        "Medium Priority":   "#f59e0b",
        "Low Priority":      "#22c55e",
    }
    chips_html = " ".join(
        f'<span style="display:inline-flex;align-items:center;gap:5px;'
        f'padding:3px 10px;border-radius:999px;font-size:0.78rem;font-weight:700;'
        f'background:{band_colours[b]}18;border:1px solid {band_colours[b]}44;'
        f'color:{band_colours[b]};margin-right:4px;">'
        f'● {b}: {band_counts.get(b, 0)}</span>'
        for b in ["Critical Priority", "High Priority", "Medium Priority", "Low Priority"]
        if band_counts.get(b, 0) > 0
    )
    st.markdown(chips_html, unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Ranked report cards ───────────────────────────────────────────────────
    for rank, report in enumerate(scored, 1):
        _render_priority_card(report, rank, upload_service)


def _render_priority_card(report: dict, rank: int, upload_service) -> None:
    score     = report["_priority_score"]
    band      = report["_priority_band"]
    colour    = report["_priority_colour"]
    breakdown = report["_priority_breakdown"]

    title    = str(report.get("title") or report.get("filename") or "Untitled")[:70]
    cat      = str(report.get("category") or "Unknown")
    loc      = str(report.get("location") or "Unknown")
    sev      = str(report.get("severity") or "Medium")
    status   = str(report.get("status") or "Open")
    date_raw = str(report.get("upload_date") or "")[:10]
    upvotes  = int(report.get("upvotes") or 0)
    report_id = str(report.get("id", ""))

    # Days open
    from src.services.priority_service import _parse_date
    dt = _parse_date(report.get("upload_date") or report.get("created_at"))
    days_open = (
        int((datetime.now(timezone.utc) - dt).days) if dt else None
    )

    status_color = STATUS_COLORS.get(status, "#6b7280")

    with st.container(border=True):
        header_col, score_col = st.columns([6, 1])

        with header_col:
            # Rank + title + badges
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:10px;flex-wrap:wrap;'>"
                f"<span style='font-size:1.1rem;font-weight:800;color:{colour};'>"
                f"#{rank}</span>"
                f"<span style='font-weight:700;font-size:0.97rem;'>{title}</span>"
                f"<span style='background:{colour}22;color:{colour};"
                f"border:1px solid {colour}55;border-radius:999px;"
                f"padding:2px 9px;font-size:0.75rem;font-weight:700;'>{band}</span>"
                f"<span style='background:{status_color}22;color:{status_color};"
                f"border:1px solid {status_color}44;border-radius:999px;"
                f"padding:2px 9px;font-size:0.72rem;font-weight:600;'>{status}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            # Meta row
            meta_parts = [f"🏷️ {cat}", f"📍 {loc}", f"🔴 {sev}"]
            if days_open is not None:
                meta_parts.append(f"⏱️ {days_open}d open")
            if upvotes:
                meta_parts.append(f"▲ {upvotes} votes")
            st.markdown(
                "<span style='font-size:0.8rem;color:#94a3b8;'>"
                + " &nbsp;|&nbsp; ".join(meta_parts)
                + "</span>",
                unsafe_allow_html=True,
            )

        with score_col:
            # Circular-ish score badge
            st.markdown(
                f"<div style='text-align:center;padding-top:4px;'>"
                f"<div style='font-size:1.8rem;font-weight:800;color:{colour};'>{score:.0f}</div>"
                f"<div style='font-size:0.68rem;color:#94a3b8;letter-spacing:0.04em;'>/ 100</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        # Score breakdown bar chart
        with st.expander("📊 Score breakdown & quick actions"):
            bar_col, action_col = st.columns([3, 2])

            with bar_col:
                st.markdown("**Score components**")
                components = [
                    ("Severity (AI)",    breakdown["severity"],  40, "#6366f1"),
                    ("Time open",        breakdown["time_open"], 25, "#f59e0b"),
                    ("Community votes",  breakdown["votes"],     20, "#22c55e"),
                    ("Local density",    breakdown["density"],   15, "#ef4444"),
                ]
                for label, pts, max_pts, bar_colour in components:
                    pct = int((pts / max_pts) * 100) if max_pts else 0
                    st.markdown(
                        f"<div style='margin-bottom:8px;'>"
                        f"<div style='display:flex;justify-content:space-between;"
                        f"font-size:0.8rem;margin-bottom:3px;'>"
                        f"<span style='color:#94a3b8;'>{label}</span>"
                        f"<span style='font-weight:700;color:#f1f5f9;'>{pts:.1f} / {max_pts}</span>"
                        f"</div>"
                        f"<div style='background:#1e2d45;border-radius:999px;height:7px;'>"
                        f"<div style='background:{bar_colour};width:{pct}%;height:7px;"
                        f"border-radius:999px;transition:width 0.4s ease;'></div>"
                        f"</div></div>",
                        unsafe_allow_html=True,
                    )

            with action_col:
                st.markdown("**Quick actions**")
                if upload_service and report_id:
                    new_status = st.selectbox(
                        "Set status",
                        REPORT_STATUSES,
                        index=REPORT_STATUSES.index(status) if status in REPORT_STATUSES else 0,
                        key=f"pq_status_{report_id}",
                        label_visibility="collapsed",
                    )
                    assignee = st.text_input(
                        "Assign to",
                        value=str(report.get("assigned_to") or ""),
                        placeholder="Officer name or email",
                        key=f"pq_assign_{report_id}",
                        label_visibility="collapsed",
                    )
                    if st.button(
                        "💾 Save", key=f"pq_save_{report_id}", use_container_width=True
                    ):
                        updates = {
                            "status": new_status,
                            "assigned_to": assignee or None,
                        }
                        if new_status == "Resolved":
                            updates["resolved_at"] = datetime.now(timezone.utc).isoformat()
                        res = upload_service.update_report(report_id, updates)
                        if res.get("success"):
                            st.toast("✅ Updated!", icon="✅")
                            st.rerun()
                        else:
                            st.error(res.get("message", "Update failed."))
                else:
                    st.caption("Upload service unavailable.")


# ── Analytics ─────────────────────────────────────────────────────────────────

def _render_analytics(reports: list[dict]) -> None:
    df = pd.DataFrame(reports)
    if "upload_date" in df.columns:
        df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")

    today = datetime.now()
    c1, c2 = st.columns(2)
    with c1:
        date_start = st.date_input("From", value=today - timedelta(days=90), key="ins_from")
    with c2:
        date_end = st.date_input("To", value=today, key="ins_to")

    if "upload_date" in df.columns:
        mask = (df["upload_date"].dt.date >= date_start) & (df["upload_date"].dt.date <= date_end)
        filtered_df = df[mask]
    else:
        filtered_df = df

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Reports", len(filtered_df))
    with m2:
        high = (
            len(filtered_df[filtered_df.get("severity", pd.Series()).isin(["Critical", "High"])])
            if "severity" in filtered_df.columns else 0
        )
        st.metric("🚨 High Priority", high)
    with m3:
        avg = len(filtered_df) / max((date_end - date_start).days + 1, 1)
        st.metric("Reports/Day", f"{avg:.1f}")
    with m4:
        cats = filtered_df["category"].nunique() if "category" in filtered_df.columns else 0
        st.metric("Categories", cats)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Reports by Category**")
        if "category" in filtered_df.columns and not filtered_df.empty:
            st.bar_chart(filtered_df["category"].fillna("Unknown").value_counts().head(8))
    with col2:
        st.markdown("**Reports by Severity**")
        if "severity" in filtered_df.columns and not filtered_df.empty:
            st.bar_chart(filtered_df["severity"].fillna("Medium").value_counts())

    st.divider()
    st.markdown("**Reports Over Time**")
    if "upload_date" in filtered_df.columns and filtered_df["upload_date"].notna().any():
        ts = (
            filtered_df.dropna(subset=["upload_date"])
            .groupby(filtered_df["upload_date"].dt.date)
            .size()
            .rename("Reports")
        )
        st.line_chart(ts)
    else:
        st.caption("No date data available.")


# ── Manage ────────────────────────────────────────────────────────────────────

def _render_manage(reports: list[dict], upload_service) -> None:

    st.markdown("#### Status Pipeline")
    pipeline_cols = st.columns(4)
    for col, status in zip(pipeline_cols, REPORT_STATUSES):
        count = sum(1 for r in reports if r.get("status", "Open") == status)
        color = STATUS_COLORS[status]
        with col:
            st.markdown(
                f'<div style="border-radius:14px;border:1px solid {color}40;'
                f'background:{color}10;padding:1.2rem 1rem;text-align:center;">'
                f'<div style="font-size:2.2rem;font-weight:780;color:{color};">{count}</div>'
                f'<div style="font-size:0.9rem;font-weight:600;color:{color};margin-top:4px;">{status}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown("#### Bulk Edit")
    st.caption("Edit Status or Assigned To inline, then click Save.")

    sf1, sf2, sf3 = st.columns(3)
    with sf1:
        search = st.text_input("Search", "", key="manage_search")
    with sf2:
        sev_f = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"], key="manage_sev")
    with sf3:
        status_f = st.selectbox("Status", ["All"] + REPORT_STATUSES, key="manage_status_f")

    filtered = reports
    if search.strip():
        t = search.lower()
        filtered = [r for r in filtered if t in str(r.get("title", "")).lower()
                    or t in str(r.get("location", "")).lower()]
    if sev_f != "All":
        filtered = [r for r in filtered if r.get("severity") == sev_f]
    if status_f != "All":
        filtered = [r for r in filtered if r.get("status", "Open") == status_f]

    st.caption(f"Showing {len(filtered)} of {len(reports)} reports")

    if not filtered:
        st.info("No reports match filters.")
    else:
        rows = [
            {
                "ID":          str(r.get("id", "")),
                "Title":       (r.get("title") or r.get("filename") or "Untitled")[:50],
                "Category":    r.get("category", "Unknown"),
                "Severity":    r.get("severity", "Medium"),
                "Status":      r.get("status") or "Open",
                "Assigned To": r.get("assigned_to") or "",
                "Location":    str(r.get("location") or "")[:40],
                "Date":        str(r.get("upload_date", ""))[:10],
            }
            for r in filtered
        ]

        df_orig = pd.DataFrame(rows)
        edited = st.data_editor(
            df_orig,
            column_config={
                "ID":          st.column_config.TextColumn("ID", disabled=True, width="small"),
                "Title":       st.column_config.TextColumn("Title", disabled=True, width="large"),
                "Category":    st.column_config.TextColumn("Category", disabled=True),
                "Severity":    st.column_config.SelectboxColumn(
                    "Severity", options=["Low", "Medium", "High", "Critical"], disabled=True
                ),
                "Status":      st.column_config.SelectboxColumn(
                    "Status", options=REPORT_STATUSES, required=True
                ),
                "Assigned To": st.column_config.TextColumn("Assigned To"),
                "Location":    st.column_config.TextColumn("Location", disabled=True),
                "Date":        st.column_config.TextColumn("Date", disabled=True, width="small"),
            },
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            key="bulk_edit_table",
        )

        changed = edited[
            (edited["Status"] != df_orig["Status"]) |
            (edited["Assigned To"] != df_orig["Assigned To"])
        ]

        if not changed.empty:
            st.warning(f"⚠️ {len(changed)} unsaved change(s).")
            if st.button("💾 Save All Changes", type="primary", key="save_bulk"):
                if upload_service:
                    saved = 0
                    for _, row in changed.iterrows():
                        res = upload_service.update_report(
                            row["ID"],
                            {
                                "status":      row["Status"],
                                "assigned_to": row["Assigned To"] or None,
                            },
                        )
                        if res.get("success"):
                            saved += 1
                    st.success(f"✅ Saved {saved}/{len(changed)} changes.")
                    st.rerun()
                else:
                    st.error("Upload service unavailable.")

    st.divider()
    st.markdown("#### Edit Individual Report")

    options = {
        f"#{r.get('id','?')} — {(r.get('title') or r.get('filename','Untitled'))[:50]}"
        f"  [{r.get('status','Open')}]": r
        for r in reports
    }

    selected_label = st.selectbox(
        "Select a report", list(options.keys()), key="individual_report_select"
    )
    if not selected_label:
        return

    report = options[selected_label]
    image_url = report.get("cloud_storage_url") or report.get("image_path")

    with st.container(border=True):
        ic1, ic2 = st.columns([1, 2], gap="large")

        with ic1:
            if image_url:
                try:
                    st.image(image_url, use_container_width=True)
                except Exception:
                    st.caption("Image unavailable.")
            st.caption(f"📍 {report.get('location','Unknown')}")
            st.caption(f"🏷️ {report.get('category','Unknown')} · {report.get('severity','Medium')}")
            st.caption(f"📅 {str(report.get('upload_date',''))[:10]}")

        with ic2:
            with st.form("individual_report_form"):
                fc1, fc2 = st.columns(2)
                with fc1:
                    current_status = report.get("status", "Open")
                    new_status = st.selectbox(
                        "Status",
                        REPORT_STATUSES,
                        index=REPORT_STATUSES.index(current_status)
                        if current_status in REPORT_STATUSES else 0,
                    )
                with fc2:
                    new_assigned = st.text_input(
                        "Assigned To",
                        value=report.get("assigned_to") or "",
                        placeholder="Officer name or email",
                    )

                new_notes = st.text_area(
                    "Council Notes (internal only)",
                    value=report.get("council_notes") or "",
                    height=110,
                    placeholder="Internal notes visible only to council staff…",
                )

                saved = st.form_submit_button(
                    "💾 Save Changes", type="primary", use_container_width=True
                )

            if saved and upload_service:
                updates = {
                    "status":        new_status,
                    "assigned_to":   new_assigned or None,
                    "council_notes": new_notes or None,
                }
                if new_status == "Resolved" and current_status != "Resolved":
                    updates["resolved_at"] = datetime.now(timezone.utc).isoformat()

                result = upload_service.update_report(report.get("id"), updates)
                if result.get("success"):
                    st.success("✅ Report updated.")
                    st.rerun()
                else:
                    st.error(f"Failed: {result.get('message')}")