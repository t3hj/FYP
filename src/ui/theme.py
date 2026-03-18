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
        bg = "#f8fafc"
        surface = "#ffffff"
        border = "#cbd5e1"
        text_primary = "#0f172a"
        text_secondary = "#475569"
        hero_overlay = "rgba(226, 232, 240, 0.95)"
        step_bg = "#f1f5f9"

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

        html, body, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"], .stApp {{
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
            font-size: 0.85rem;
            color: var(--brand-text-secondary);
            line-height: 1.5;
        }}

        .ll-topbar-controls {{
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
            align-items: flex-end;
            text-align: right;
        }}

        .ll-hero-chip {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            border-radius: 999px;
            border: 1px solid rgba(99, 102, 241, 0.4);
            background: rgba(99, 102, 241, 0.12);
            color: #4f46e5;
            padding: 0.35rem 0.8rem;
            font-size: 0.82rem;
            font-weight: 700;
            margin-bottom: 1rem;
            letter-spacing: 0.02em;
        }}

        .ll-hero-card {{
            position: relative;
            overflow: hidden;
            padding: 2.5rem 2rem;
            border-radius: 20px;
            border: 1px solid rgba(99, 102, 241, 0.35);
            background: linear-gradient(135deg, rgba(219, 234, 254, 0.6), rgba(238, 242, 255, 0.8));
            margin-bottom: 2.5rem;
            box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
            color: #0f172a;
        }}

        .ll-hero-card::after {{
            content: \"\";
            position: absolute;
            top: -20%;
            right: -10%;
            width: 280px;
            height: 280px;
            background: rgba(99, 102, 241, 0.15);
            border-radius: 999px;
            filter: blur(60px);
            pointer-events: none;
        }}

        .ll-hero-title {{
            font-size: 2.2rem;
            font-weight: 780;
            letter-spacing: -0.03em;
            line-height: 1.15;
            max-width: 700px;
            margin-bottom: 0.9rem;
            position: relative;
            z-index: 1;
            color: #0f172a;
        }}

        .ll-hero-subtitle {{
            font-size: 1.05rem;
            color: #334155;
            max-width: 720px;
            line-height: 1.7;
            margin-bottom: 1.5rem;
            position: relative;
            z-index: 1;
        }}

        .ll-hero-actions {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
            position: relative;
            z-index: 1;
        }}

        .ll-hero-cta {{
            border: none;
            border-radius: 999px;
            padding: 0.7rem 1.4rem;
            background: linear-gradient(120deg, #4f46e5, #9333ea);
            color: #ffffff;
            font-size: 1rem;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            cursor: pointer;
            box-shadow: 0 12px 32px rgba(99, 102, 241, 0.4);
            transition: all 0.3s ease;
        }}

        .ll-hero-cta:hover {{
            background: linear-gradient(120deg, #5d5aec, #a78bfa);
            box-shadow: 0 16px 40px rgba(99, 102, 241, 0.5);
            transform: translateY(-2px);
        }}

        .ll-hero-cta:active {{
            transform: translateY(0);
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.35);
        }}

        .ll-step-card {{
            padding: 1.6rem;
            border-radius: 16px;
            border: 1px solid #cbd5e1;
            background: #ffffff;
            min-height: 160px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}

        .ll-step-card:hover {{
            border-color: #93c5fd;
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.12);
        }}

        .ll-step-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            border-radius: 999px;
            background: linear-gradient(135deg, #3b82f6, #6366f1);
            color: #ffffff;
            font-size: 0.95rem;
            font-weight: 700;
            margin-bottom: 0.9rem;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
            flex-shrink: 0;
        }}

        .ll-step-title {{
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            line-height: 1.3;
        }}

        .ll-kpi-card {{
            border-radius: 16px;
            border: 1px solid #cbd5e1;
            background: #ffffff;
            padding: 1.6rem;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
            min-height: 140px;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }}

        .ll-kpi-card:hover {{
            border-color: #93c5fd;
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(99, 102, 241, 0.12);
        }}

        .ll-kpi-card::after {{
            content: \"\";
            position: absolute;
            top: -25px;
            right: -20px;
            width: 100px;
            height: 100px;
            border-radius: 999px;
            background: rgba(99, 102, 241, 0.1);
            filter: blur(25px);
        }}

        .ll-kpi-label {{
            font-size: 0.9rem;
            color: rgba(148, 163, 184, 0.9);
            margin-bottom: 0.6rem;
            position: relative;
            z-index: 1;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}

        .ll-kpi-value {{
            font-size: 2.3rem;
            font-weight: 780;
            line-height: 1.15;
            margin-bottom: 0.3rem;
            letter-spacing: -0.03em;
            position: relative;
            z-index: 1;
            overflow-wrap: break-word;
        }}

        .ll-kpi-hint {{
            font-size: 0.85rem;
            color: rgba(148, 163, 184, 0.85);
            position: relative;
            z-index: 1;
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

        .ll-report-card {{
            border-radius: 16px;
            border: 1px solid rgba(99, 102, 241, 0.25);
            padding: 1.5rem;
            background: rgba(30, 41, 59, 0.6);
            box-shadow: 0 8px 16px rgba(15, 23, 42, 0.2);
        }}

        .ll-empty-state {{
            border-radius: 18px;
            border: 1px dashed rgba(99, 102, 241, 0.3);
            padding: 2rem;
            text-align: center;
            background: rgba(30, 41, 59, 0.5);
        }}

        .ll-empty-emoji {{
            font-size: 2.5rem;
            margin-bottom: 0.8rem;
        }}

        .ll-empty-title {{
            font-weight: 700;
            font-size: 1.1rem;
            margin-bottom: 0.6rem;
        }}

        .ll-empty-subtitle {{
            font-size: 0.95rem;
            color: var(--brand-text-secondary);
            line-height: 1.6;
        }}

        /* Streamlit button styling for primary actions */
        button[kind="primary"] {{
            background: linear-gradient(120deg, #4f46e5, #9333ea) !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
        }}

        button[kind="primary"]:hover {{
            background: linear-gradient(120deg, #5d5aec, #a78bfa) !important;
            box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4) !important;
        }}

        /* Expander styling for quick upload */
        div[data-testid="stExpander"] {{
            border: 1px solid rgba(99, 102, 241, 0.35) !important;
            border-radius: 16px !important;
            background: rgba(30, 41, 59, 0.7) !important;
            overflow: hidden;
        }}

        div[data-testid="stExpander"] button {{
            padding: 1.25rem !important;
            font-weight: 600 !important;
            color: var(--brand-text-primary) !important;
        }}

        div[data-testid="stExpander"] button:hover {{
            background: rgba(99, 102, 241, 0.1) !important;
        }}

        /* Custom upload zone styling */
        .ll-upload-zone {{
            position: relative;
            border: 2px dashed #cbd5e1;
            border-radius: 20px;
            padding: 3rem 2rem;
            text-align: center;
            background: linear-gradient(135deg, rgba(219, 234, 254, 0.3), rgba(238, 242, 255, 0.5));
            transition: all 0.3s ease;
            cursor: pointer;
        }}

        .ll-upload-zone:hover {{
            border-color: #93c5fd;
            background: linear-gradient(135deg, rgba(219, 234, 254, 0.5), rgba(238, 242, 255, 0.7));
            box-shadow: 0 8px 32px rgba(99, 102, 241, 0.12);
        }}

        .ll-upload-icon {{
            width: 80px;
            height: 80px;
            margin: 0 auto 1.5rem;
            border-radius: 50%;
            background: linear-gradient(135deg, #3b82f6, #6366f1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            box-shadow: 0 4px 16px rgba(99, 102, 241, 0.25);
        }}

        .ll-upload-title {{
            font-size: 1.3rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.5rem;
        }}

        .ll-upload-subtitle {{
            font-size: 0.95rem;
            color: #475569;
            margin-bottom: 1.5rem;
        }}

        .ll-upload-requirements {{
            font-size: 0.85rem;
            color: #64748b;
            margin-bottom: 1.5rem;
        }}

        .ll-file-uploader-container {{
            max-width: 100%;
        }}

        .ll-file-uploader-container input[type="file"] {{
            display: none;
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

