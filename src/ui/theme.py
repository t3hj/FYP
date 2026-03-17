import streamlit as st

BRAND_COLORS = {
    "primary": "#2563eb",
    "primary_soft": "#dbeafe",
    "accent": "#f97316",
    "accent_soft": "#fff7ed",
    "neutral_100": "#f9fafb",
    "neutral_200": "#e5e7eb",
    "neutral_300": "#d1d5db",
    "neutral_600": "#4b5563",
    "neutral_700": "#374151",
    "neutral_900": "#111827",
}

SEVERITY_COLOURS = {
    "Low": "#22c55e",
    "Medium": "#f97316",
    "High": "#ef4444",
    "Critical": "#7c3aed",
}

SPACING_SCALE = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
}


def init_theme() -> str:
    """Initialise light/dark theme from session state or URL and return active theme."""
    try:
        params = st.query_params  # streamlit >= 1.36
        url_theme = params.get("theme", ["light"])
        url_theme = url_theme[0] if isinstance(url_theme, list) else url_theme
    except Exception:
        params = st.experimental_get_query_params()
        url_theme = params.get("theme", ["light"])[0] if params.get("theme") else "light"

    if "theme" not in st.session_state:
        st.session_state.theme = url_theme if url_theme in {"light", "dark"} else "light"

    return st.session_state.theme


def set_theme(theme: str) -> None:
    if theme not in {"light", "dark"}:
        return
    st.session_state.theme = theme
    try:
        st.query_params["theme"] = theme  # type: ignore[index]
    except Exception:
        st.experimental_set_query_params(theme=theme)


def apply_theme_css(theme: str) -> None:
    is_dark = theme == "dark"

    if is_dark:
        bg = "#020617"
        surface = "#020617"
        border = BRAND_COLORS["neutral_700"]
        text_primary = "#e5e7eb"
        text_secondary = "#9ca3af"
        hero_overlay = "rgba(15, 23, 42, 0.85)"
        step_bg = "rgba(15, 23, 42, 0.65)"
    else:
        bg = "#f3f4f6"
        surface = "#ffffff"
        border = BRAND_COLORS["neutral_200"]
        text_primary = BRAND_COLORS["neutral_900"]
        text_secondary = BRAND_COLORS["neutral_600"]
        hero_overlay = "rgba(249, 250, 251, 0.9)"
        step_bg = "#f9fafb"

    st.markdown(
        f"""
        <style>
        :root {{
            --brand-primary: {BRAND_COLORS["primary"]};
            --brand-primary-soft: {BRAND_COLORS["primary_soft"]};
            --brand-accent: {BRAND_COLORS["accent"]};
            --brand-accent-soft: {BRAND_COLORS["accent_soft"]};
            --brand-border: {border};
            --brand-bg: {bg};
            --brand-surface: {surface};
            --brand-hero-overlay: {hero_overlay};
            --brand-step-surface: {step_bg};
            --brand-text-primary: {text_primary};
            --brand-text-secondary: {text_secondary};
            --space-xs: {SPACING_SCALE["xs"]};
            --space-sm: {SPACING_SCALE["sm"]};
            --space-md: {SPACING_SCALE["md"]};
            --space-lg: {SPACING_SCALE["lg"]};
            --space-xl: {SPACING_SCALE["xl"]};
        }}

        html, body, [data-testid="stAppViewContainer"], .stApp {{
            background: var(--brand-bg) !important;
            color: var(--brand-text-primary) !important;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text",
                         "Inter", "Segoe UI", sans-serif;
        }}

        [data-testid="stSidebar"] {{
            background-color: var(--brand-surface) !important;
            color: var(--brand-text-primary) !important;
        }}

        label[for*="Dark mode"], div[role="switch"] span {{
            color: var(--brand-text-primary) !important;
            font-size: 0.85rem;
            font-weight: 500;
        }}

        [data-baseweb="tab-list"] button, [data-baseweb="tab"] {{
            color: var(--brand-text-primary) !important;
            font-weight: 500;
        }}

        [data-baseweb="tab"] span {{
            color: inherit !important;
        }}

        .ll-hero-title {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Display",
                         "Inter", "Segoe UI", sans-serif;
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            margin-bottom: var(--space-xs);
        }}

        .ll-hero-subtitle {{
            font-size: 0.95rem;
            color: var(--brand-text-secondary);
            max-width: 520px;
        }}

        .ll-meta-text {{
            font-size: 0.8rem;
            color: var(--brand-text-secondary);
        }}

        .ll-helper-text {{
            font-size: 0.8rem;
            color: var(--brand-text-secondary);
        }}

        .ll-status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 2px 10px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            background: rgba(15, 118, 110, 0.08);
            color: var(--brand-text-secondary);
        }}

        .ll-hero-card {{
            padding: var(--space-lg);
            border-radius: 18px;
            border: 1px solid var(--brand-border);
            background:
                radial-gradient(circle at top left,
                    rgba(37, 99, 235, 0.20),
                    transparent 55%),
                linear-gradient(135deg,
                    var(--brand-hero-overlay),
                    var(--brand-surface));
            margin-bottom: var(--space-lg);
        }}

        .ll-step-card {{
            padding: var(--space-md);
            border-radius: 14px;
            border: 1px dashed var(--brand-border);
            background: var(--brand-step-surface);
        }}

        .ll-step-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 26px;
            height: 26px;
            border-radius: 999px;
            background: var(--brand-primary-soft);
            color: var(--brand-primary);
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: var(--space-sm);
        }}

        .ll-report-card {{
            border-radius: 14px;
            border: 1px solid var(--brand-border);
            padding: var(--space-md);
            background: var(--brand-surface);
        }}

        .ll-empty-state {{
            border-radius: 18px;
            border: 1px dashed var(--brand-border);
            padding: var(--space-lg);
            text-align: center;
            background: rgba(15, 23, 42, 0.02);
        }}

        .ll-empty-emoji {{
            font-size: 2rem;
            margin-bottom: var(--space-sm);
        }}

        .ll-empty-title {{
            font-weight: 600;
            margin-bottom: var(--space-xs);
        }}

        .ll-empty-subtitle {{
            font-size: 0.9rem;
            color: var(--brand-text-secondary);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def severity_badge(severity: str) -> str:
    colour = SEVERITY_COLOURS.get(severity, "#6b7280")
    return (
        f'<span class="ll-status-pill" '
        f'style="background:{colour}1a;color:#111827;">'
        f"{severity}</span>"
    )

