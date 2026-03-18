import streamlit as st

BRAND_COLORS = {
    "primary": "#6366f1",          # Indigo-500
    "primary_dark": "#4f46e5",     # Indigo-600
    "primary_light": "#818cf8",    # Indigo-400
    "primary_soft": "#eef2ff",     # Indigo-50
    "accent": "#a855f7",           # Purple-500
    "accent_dark": "#9333ea",      # Purple-600
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "violet": "#7c3aed",
}

SEVERITY_COLOURS = {
    "Low": "#22c55e",
    "Medium": "#f59e0b",
    "High": "#ef4444",
    "Critical": "#7c3aed",
}

SPACING_SCALE = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "2xl": "48px",
}

# ── Dark palette ──────────────────────────────────────────────────────────────
_DARK = {
    "bg":            "#0a0f1e",   # Near-black blue
    "surface":       "#111827",   # Card surface
    "surface_2":     "#1a2235",   # Elevated card
    "surface_3":     "#212d45",   # Tooltip / popover
    "border":        "#1e2d45",   # Subtle border
    "border_accent": "#3730a3",   # Indigo-tinted border
    "text_primary":  "#f1f5f9",
    "text_secondary":"#94a3b8",
    "text_muted":    "#475569",
    "hero_bg":       "linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%)",
    "hero_border":   "rgba(99,102,241,0.35)",
    "chip_bg":       "rgba(99,102,241,0.18)",
    "chip_color":    "#a5b4fc",
    "step_bg":       "rgba(30,41,59,0.7)",
    "step_border":   "rgba(99,102,241,0.2)",
    "kpi_bg":        "rgba(17,24,39,0.9)",
    "kpi_border":    "rgba(99,102,241,0.22)",
    "upload_bg":     "rgba(17,24,39,0.6)",
    "upload_border": "rgba(99,102,241,0.3)",
    "glow":          "rgba(99,102,241,0.25)",
}

# ── Light palette ─────────────────────────────────────────────────────────────
_LIGHT = {
    "bg":            "#f8fafc",
    "surface":       "#ffffff",
    "surface_2":     "#f1f5f9",
    "surface_3":     "#e2e8f0",
    "border":        "#e2e8f0",
    "border_accent": "#c7d2fe",
    "text_primary":  "#0f172a",
    "text_secondary":"#475569",
    "text_muted":    "#94a3b8",
    "hero_bg":       "linear-gradient(135deg, #eef2ff 0%, #f5f3ff 50%, #eef2ff 100%)",
    "hero_border":   "rgba(99,102,241,0.3)",
    "chip_bg":       "rgba(99,102,241,0.1)",
    "chip_color":    "#4338ca",
    "step_bg":       "#ffffff",
    "step_border":   "#e0e7ff",
    "kpi_bg":        "#ffffff",
    "kpi_border":    "#e0e7ff",
    "upload_bg":     "rgba(238,242,255,0.5)",
    "upload_border": "rgba(99,102,241,0.25)",
    "glow":          "rgba(99,102,241,0.12)",
}


def init_theme() -> str:
    try:
        params = st.query_params
        url_theme = params.get("theme", ["dark"])
        url_theme = url_theme[0] if isinstance(url_theme, list) else url_theme
    except Exception:
        params = st.experimental_get_query_params()
        url_theme = params.get("theme", ["dark"])[0] if params.get("theme") else "dark"

    if "theme" not in st.session_state:
        st.session_state.theme = url_theme if url_theme in {"light", "dark"} else "dark"

    return st.session_state.theme


def set_theme(theme: str) -> None:
    if theme not in {"light", "dark"}:
        return
    st.session_state.theme = theme
    try:
        st.query_params["theme"] = theme
    except Exception:
        st.experimental_set_query_params(theme=theme)


def apply_theme_css(theme: str) -> None:
    p = _DARK if theme == "dark" else _LIGHT
    is_dark = theme == "dark"

    st.markdown(
        f"""
        <style>
        /* ── Reset & base ─────────────────────────────────────────────────── */
        *, *::before, *::after {{ box-sizing: border-box; }}

        :root {{
            --brand-primary:       {BRAND_COLORS["primary"]};
            --brand-primary-dark:  {BRAND_COLORS["primary_dark"]};
            --brand-primary-light: {BRAND_COLORS["primary_light"]};
            --brand-primary-soft:  {BRAND_COLORS["primary_soft"]};
            --brand-accent:        {BRAND_COLORS["accent"]};

            --bg:            {p["bg"]};
            --surface:       {p["surface"]};
            --surface-2:     {p["surface_2"]};
            --surface-3:     {p["surface_3"]};
            --border:        {p["border"]};
            --border-accent: {p["border_accent"]};
            --text-primary:  {p["text_primary"]};
            --text-secondary:{p["text_secondary"]};
            --text-muted:    {p["text_muted"]};
            --glow:          {p["glow"]};

            --radius-sm:  8px;
            --radius-md:  14px;
            --radius-lg:  20px;
            --radius-xl:  28px;
            --radius-full: 9999px;

            --shadow-sm:  0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08);
            --shadow-md:  0 4px 16px rgba(0,0,0,0.18), 0 2px 6px rgba(0,0,0,0.1);
            --shadow-lg:  0 12px 40px rgba(0,0,0,0.24), 0 4px 12px rgba(0,0,0,0.12);
            --shadow-glow: 0 0 30px var(--glow);
        }}

        html, body,
        [data-testid="stAppViewContainer"],
        [data-testid="stMainBlockContainer"],
        .stApp {{
            background: var(--bg) !important;
            color: var(--text-primary) !important;
            font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont,
                         "Segoe UI", sans-serif;
            -webkit-font-smoothing: antialiased;
        }}

        [data-testid="stSidebar"] {{
            background: var(--surface) !important;
            border-right: 1px solid var(--border) !important;
        }}

        /* ── Streamlit chrome ─────────────────────────────────────────────── */
        [data-baseweb="tab-list"] {{
            background: transparent !important;
            border-bottom: 1px solid var(--border) !important;
            gap: 4px !important;
        }}
        [data-baseweb="tab"] {{
            color: var(--text-secondary) !important;
            font-weight: 500 !important;
            border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
            padding: 10px 18px !important;
            transition: all 0.2s ease !important;
        }}
        [data-baseweb="tab"][aria-selected="true"] {{
            color: var(--brand-primary) !important;
            background: {"rgba(99,102,241,0.1)" if is_dark else "rgba(99,102,241,0.06)"} !important;
            border-bottom: 2px solid var(--brand-primary) !important;
        }}
        [data-baseweb="tab"] span {{ color: inherit !important; }}

        /* Inputs */
        [data-baseweb="input"] input,
        [data-baseweb="textarea"] textarea,
        [data-baseweb="select"] div {{
            background: var(--surface-2) !important;
            border-color: var(--border) !important;
            color: var(--text-primary) !important;
            border-radius: var(--radius-sm) !important;
        }}
        [data-baseweb="input"]:focus-within,
        [data-baseweb="textarea"]:focus-within {{
            border-color: var(--brand-primary) !important;
            box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
        }}

        /* Labels */
        label, .stTextInput label, .stTextArea label,
        .stSelectbox label, .stFileUploader label {{
            color: var(--text-secondary) !important;
            font-size: 0.875rem !important;
            font-weight: 500 !important;
        }}

        /* Dividers */
        hr, [data-testid="stDivider"] {{
            border-color: var(--border) !important;
            opacity: 1 !important;
        }}

        /* Caption / small text */
        .stCaption, small, .caption {{ color: var(--text-muted) !important; }}

        /* Metrics */
        [data-testid="stMetric"] {{
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            padding: 1rem 1.25rem !important;
        }}
        [data-testid="stMetricLabel"] {{ color: var(--text-secondary) !important; }}
        [data-testid="stMetricValue"] {{ color: var(--text-primary) !important; }}

        /* Alerts */
        [data-testid="stAlert"] {{
            border-radius: var(--radius-md) !important;
            border-width: 1px !important;
        }}

        /* Expanders */
        [data-testid="stExpander"] {{
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            background: var(--surface) !important;
            overflow: hidden !important;
        }}
        [data-testid="stExpander"] summary {{
            padding: 0.9rem 1.1rem !important;
            font-weight: 500 !important;
            color: var(--text-primary) !important;
        }}
        [data-testid="stExpander"]:hover {{
            border-color: var(--border-accent) !important;
        }}

        /* Buttons */
        button[kind="primary"] {{
            background: linear-gradient(135deg, {BRAND_COLORS["primary_dark"]}, {BRAND_COLORS["accent"]}) !important;
            border: none !important;
            border-radius: var(--radius-sm) !important;
            font-weight: 600 !important;
            letter-spacing: 0.01em !important;
            box-shadow: 0 4px 14px rgba(99,102,241,0.4) !important;
            transition: all 0.2s ease !important;
        }}
        button[kind="primary"]:hover {{
            opacity: 0.92 !important;
            box-shadow: 0 6px 20px rgba(99,102,241,0.5) !important;
            transform: translateY(-1px) !important;
        }}
        button[kind="secondary"] {{
            background: var(--surface-2) !important;
            border: 1px solid var(--border) !important;
            color: var(--text-primary) !important;
            border-radius: var(--radius-sm) !important;
            font-weight: 500 !important;
        }}
        button[kind="secondary"]:hover {{
            border-color: var(--brand-primary) !important;
            color: var(--brand-primary) !important;
        }}

        /* Toggle (theme switch) */
        label[for*="Dark mode"] span,
        label[data-testid="stWidgetLabel"] span {{
            color: var(--text-secondary) !important;
            font-size: 0.85rem !important;
        }}
        [data-testid="stToggle"] > div > div[data-checked="true"] {{
            background: var(--brand-primary) !important;
        }}

        /* Data editor / dataframe */
        [data-testid="stDataFrame"],
        [data-testid="stDataEditor"] {{
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            overflow: hidden !important;
        }}

        /* Containers with border */
        [data-testid="stVerticalBlockBorderWrapper"] > div {{
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
        }}

        /* ── Hero card ────────────────────────────────────────────────────── */
        .ll-hero-card {{
            position: relative;
            overflow: hidden;
            padding: 2.5rem 2.5rem 2rem;
            border-radius: var(--radius-xl);
            border: 1px solid {p["hero_border"]};
            background: {p["hero_bg"]};
            margin-bottom: 2rem;
            box-shadow: var(--shadow-lg), var(--shadow-glow);
        }}

        .ll-hero-card::before {{
            content: "";
            position: absolute;
            top: -60px; right: -60px;
            width: 320px; height: 320px;
            background: radial-gradient(circle, rgba(99,102,241,0.25) 0%, transparent 70%);
            pointer-events: none;
        }}
        .ll-hero-card::after {{
            content: "";
            position: absolute;
            bottom: -40px; left: -40px;
            width: 240px; height: 240px;
            background: radial-gradient(circle, rgba(168,85,247,0.18) 0%, transparent 70%);
            pointer-events: none;
        }}

        .ll-hero-chip {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            border-radius: var(--radius-full);
            border: 1px solid {p["border_accent"]};
            background: {p["chip_bg"]};
            color: {p["chip_color"]};
            padding: 0.3rem 0.9rem;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 1.1rem;
            position: relative; z-index: 1;
        }}

        .ll-hero-title {{
            font-size: clamp(1.7rem, 3vw, 2.4rem);
            font-weight: 800;
            letter-spacing: -0.035em;
            line-height: 1.12;
            color: {p["text_primary"]};
            margin-bottom: 0.85rem;
            position: relative; z-index: 1;
        }}

        .ll-hero-subtitle {{
            font-size: 1rem;
            color: {p["text_secondary"]};
            max-width: 600px;
            line-height: 1.7;
            margin-bottom: 1.6rem;
            position: relative; z-index: 1;
        }}

        /* ── Step cards ───────────────────────────────────────────────────── */
        .ll-step-card {{
            padding: 1.5rem;
            border-radius: var(--radius-lg);
            border: 1px solid {p["step_border"]};
            background: {p["step_bg"]};
            min-height: 155px;
            display: flex;
            flex-direction: column;
            box-shadow: var(--shadow-sm);
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
            {"backdrop-filter: blur(12px);" if is_dark else ""}
        }}
        .ll-step-card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-md), 0 0 20px var(--glow);
            border-color: var(--border-accent);
        }}

        .ll-step-badge {{
            width: 38px; height: 38px;
            border-radius: var(--radius-full);
            background: linear-gradient(135deg, {BRAND_COLORS["primary_dark"]}, {BRAND_COLORS["accent"]});
            color: #fff;
            font-size: 0.9rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 0.85rem;
            box-shadow: 0 4px 14px rgba(99,102,241,0.4);
            flex-shrink: 0;
        }}

        .ll-step-title {{
            font-size: 1rem;
            font-weight: 700;
            color: {p["text_primary"]};
            margin-bottom: 0.45rem;
        }}

        /* ── KPI cards ────────────────────────────────────────────────────── */
        .ll-kpi-card {{
            border-radius: var(--radius-lg);
            border: 1px solid {p["kpi_border"]};
            background: {p["kpi_bg"]};
            padding: 1.5rem 1.6rem;
            box-shadow: var(--shadow-sm);
            min-height: 130px;
            position: relative;
            overflow: hidden;
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
            {"backdrop-filter: blur(12px);" if is_dark else ""}
        }}
        .ll-kpi-card:hover {{
            transform: translateY(-3px);
            box-shadow: var(--shadow-md), 0 0 18px var(--glow);
            border-color: var(--border-accent);
        }}
        .ll-kpi-card::after {{
            content: "";
            position: absolute;
            top: -30px; right: -20px;
            width: 120px; height: 120px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
        }}

        .ll-kpi-label {{
            font-size: 0.75rem;
            color: {p["text_muted"]};
            text-transform: uppercase;
            letter-spacing: 0.07em;
            font-weight: 600;
            margin-bottom: 0.55rem;
            position: relative; z-index: 1;
        }}
        .ll-kpi-value {{
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            color: {p["text_primary"]};
            line-height: 1.1;
            margin-bottom: 0.3rem;
            position: relative; z-index: 1;
            overflow-wrap: break-word;
        }}
        .ll-kpi-hint {{
            font-size: 0.8rem;
            color: {p["text_muted"]};
            position: relative; z-index: 1;
        }}

        /* ── Upload zone ──────────────────────────────────────────────────── */
        .ll-upload-zone {{
            border: 2px dashed {p["upload_border"]};
            border-radius: var(--radius-lg);
            padding: 2.5rem 2rem;
            text-align: center;
            background: {p["upload_bg"]};
            transition: all 0.25s ease;
            margin-bottom: 1rem;
        }}
        .ll-upload-zone:hover {{
            border-color: var(--brand-primary);
            background: {"rgba(99,102,241,0.08)" if is_dark else "rgba(99,102,241,0.05)"};
            box-shadow: 0 0 24px var(--glow);
        }}
        .ll-upload-icon {{
            width: 72px; height: 72px;
            margin: 0 auto 1.2rem;
            border-radius: 50%;
            background: linear-gradient(135deg, {BRAND_COLORS["primary_dark"]}, {BRAND_COLORS["accent"]});
            display: flex; align-items: center; justify-content: center;
            font-size: 2.2rem;
            box-shadow: 0 8px 24px rgba(99,102,241,0.35);
        }}
        .ll-upload-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: {p["text_primary"]};
            margin-bottom: 0.4rem;
        }}
        .ll-upload-subtitle {{
            font-size: 0.9rem;
            color: {p["text_secondary"]};
            margin-bottom: 1rem;
        }}
        .ll-upload-requirements {{
            font-size: 0.8rem;
            color: {p["text_muted"]};
        }}

        /* ── Status pill / badge ──────────────────────────────────────────── */
        .ll-status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 3px 10px;
            border-radius: var(--radius-full);
            font-size: 0.73rem;
            font-weight: 700;
            letter-spacing: 0.03em;
        }}

        /* ── Empty state ──────────────────────────────────────────────────── */
        .ll-empty-state {{
            border-radius: var(--radius-lg);
            border: 1px dashed {p["border"]};
            padding: 3rem 2rem;
            text-align: center;
            background: {"rgba(17,24,39,0.5)" if is_dark else "rgba(248,250,252,0.8)"};
        }}
        .ll-empty-emoji {{ font-size: 2.5rem; margin-bottom: 0.75rem; }}
        .ll-empty-title  {{ font-weight: 700; font-size: 1.1rem; color: {p["text_primary"]}; margin-bottom: 0.5rem; }}
        .ll-empty-subtitle {{ font-size: 0.9rem; color: {p["text_secondary"]}; line-height: 1.6; }}

        /* ── Misc helpers ─────────────────────────────────────────────────── */
        .ll-meta-text  {{ font-size: 0.8rem;  color: {p["text_muted"]}; }}
        .ll-helper-text {{ font-size: 0.85rem; color: {p["text_secondary"]}; line-height: 1.5; }}
        .ll-topbar-controls {{ display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem; }}

        /* scrollbar */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{
            background: {"rgba(99,102,241,0.35)" if is_dark else "rgba(99,102,241,0.25)"};
            border-radius: 99px;
        }}
        ::-webkit-scrollbar-thumb:hover {{ background: rgba(99,102,241,0.55); }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def severity_badge(severity: str) -> str:
    colour = SEVERITY_COLOURS.get(severity, "#6b7280")
    return (
        f'<span class="ll-status-pill" '
        f'style="background:{colour}22;color:{colour};border:1px solid {colour}55;">'
        f"{severity}</span>"
    )