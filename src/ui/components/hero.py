import streamlit as st

from src.ui.theme import set_theme


def render_hero(active_theme: str) -> None:
    header_col, toggle_col = st.columns([6, 1])
    with header_col:
        st.markdown(
            """
            <div class="ll-hero-card">
                <div class="ll-hero-title">📸 Local Lens</div>
                <p class="ll-hero-subtitle">
                    Turn quick snapshots into structured council-ready reports.
                    Upload an image, let AI analyse it, and submit in under a minute.
                </p>
                <div style="margin-top:16px; display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
                    <button disabled style="
                        background: var(--brand-primary);
                        color: #ffffff;
                        border: none;
                        border-radius: 999px;
                        padding: 8px 16px;
                        font-size: 0.9rem;
                        font-weight: 600;
                        cursor: pointer;
                    ">
                        Start a new report ↓
                    </button>
                    <span class="ll-helper-text">
                        Go to <strong>Report an Issue</strong> below to begin.
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with toggle_col:
        st.markdown("<div style='text-align:right'>", unsafe_allow_html=True)
        is_dark = active_theme == "dark"
        new_is_dark = st.toggle("Dark mode", value=is_dark)
        if new_is_dark != is_dark:
            set_theme("dark" if new_is_dark else "light")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_onboarding_steps() -> None:
    step_col1, step_col2, step_col3 = st.columns(3)
    with step_col1:
        st.markdown(
            """
            <div class="ll-step-card">
                <div class="ll-step-badge">1</div>
                <div><strong>Upload an image</strong></div>
                <div class="ll-helper-text">
                    Snap a quick photo of a street, park, or public space issue.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with step_col2:
        st.markdown(
            """
            <div class="ll-step-card">
                <div class="ll-step-badge">2</div>
                <div><strong>AI analyses it</strong></div>
                <div class="ll-helper-text">
                    Our AI suggests a title, severity, category, and recommended action.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with step_col3:
        st.markdown(
            """
            <div class="ll-step-card">
                <div class="ll-step-badge">3</div>
                <div><strong>Submit to council</strong></div>
                <div class="ll-helper-text">
                    Review the auto-filled form, edit if needed, then submit your report.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

